import os
import json
import time
import socket
import queue
import threading
from datetime import datetime

from event_detector import (
    EventDetector,
    INTERVAL,
    TARGET,
    MIN_CONFIDENCE,
    read_detections,
    analyze,
)

SOCKET_PATH = "/tmp/neuroeye-command.sock"
SEARCH_TIMEOUT = 15.0


class BehaviorManager:
    def __init__(self):
        self.mode = "AWARE"
        self.state = "BOOT"
        self.detector = EventDetector()
        self.events = queue.Queue()
        self.running = threading.Event()
        self.running.set()

        self.active_target = None
        self.deadline = None
        self.waiter = None

        self.visible = False
        self.data_ready = False

    def log(self, message):
        stamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{stamp}] {message}", flush=True)

    def transition(self, new_state, reason):
        if self.state == new_state:
            return

        old = self.state
        self.state = new_state
        self.log(f"{old} -> {new_state} | {reason}")

    def reply(self, connection, result):
        try:
            connection.sendall(
                (json.dumps(result) + "\n").encode()
            )
        except OSError:
            pass
        finally:
            try:
                connection.close()
            except OSError:
                pass

    def finish_search(self, status):
        target = self.active_target
        connection = self.waiter

        self.active_target = None
        self.deadline = None
        self.waiter = None

        if status == "FOUND":
            self.transition("OBSERVING", "Person found")
        elif status == "NOT_FOUND":
            self.transition("IDLE", "Search timeout")

        self.log(f"TASK RESULT: {status} ({target})")

        if connection is not None:
            self.reply(connection, {
                "status": status,
                "target": target
            })

    def camera_loop(self):
        while self.running.is_set():
            try:
                raw = read_detections()

                if raw is None:
                    raise RuntimeError(
                        "Detection data unavailable"
                    )

                detections = analyze(raw)
                self.events.put(("detections", detections))

            except Exception as exc:
                self.events.put(("error", str(exc)))

            time.sleep(INTERVAL)

    def socket_loop(self):
        with socket.socket(
            socket.AF_UNIX, socket.SOCK_STREAM
        ) as server:
            server.bind(SOCKET_PATH)
            server.listen(5)
            server.settimeout(0.2)

            self.log("Command socket ready")

            while self.running.is_set():
                try:
                    connection, _ = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break

                connection.settimeout(2)

                try:
                    data = connection.recv(1024)
                    command = data.decode().strip()
                    self.events.put((
                        "command",
                        (command, connection)
                    ))
                except (OSError, UnicodeError):
                    connection.close()

    def handle_command(self, command, connection):
        parts = command.lower().split()

        if not parts:
            self.reply(connection, {
                "status": "ERROR",
                "reason": "Empty command"
            })
            return

        action = parts[0]
        self.log(f"COMMAND: {command}")

        if action == "status":
            self.reply(connection, {
                "status": "OK",
                "mode": self.mode,
                "state": self.state,
                "target": self.active_target,
                "visible": self.visible
            })
            return

        if action == "stop":
            if self.waiter is not None:
                self.finish_search("CANCELLED")

            self.transition("SAFE_STOP", "User STOP")
            self.reply(connection, {
                "status": "STOPPED"
            })
            return

        if action == "resume":
            if self.state == "SAFE_STOP":
                self.transition("IDLE", "User RESUME")

            self.reply(connection, {
                "status": "RESUMED",
                "state": self.state
            })
            return

        if action == "search":
            if len(parts) != 2 or parts[1] != TARGET:
                self.reply(connection, {
                    "status": "ERROR",
                    "reason": "Use SEARCH person"
                })
                return

            if self.state == "SAFE_STOP":
                self.reply(connection, {
                    "status": "ERROR",
                    "reason": "SAFE_STOP active"
                })
                return

            if self.active_target is not None:
                self.reply(connection, {
                    "status": "BUSY"
                })
                return

            self.active_target = TARGET
            self.deadline = time.monotonic() + SEARCH_TIMEOUT
            self.waiter = connection

            self.transition(
                "SEARCHING",
                "Searching for person"
            )

            if (
                self.data_ready
                and self.detector.present
                and self.visible
            ):
                self.finish_search("FOUND")

            return

        self.reply(connection, {
            "status": "ERROR",
            "reason": "Unknown command"
        })

    def handle_detections(self, detections):
        self.data_ready = True

        self.visible = any(
            obj["class"] == TARGET
            and obj["confidence"] >= MIN_CONFIDENCE
            for obj in detections
        )

        event = self.detector.update(detections)

        if event:
            kind = event["type"]
            target = event["target"]

            self.log(f"EVENT: {kind} ({target})")

            if self.state == "IDLE":
                if kind == "OBJECT_APPEARED":
                    self.transition(
                        "OBSERVING",
                        "Person appeared"
                    )

            elif self.state == "OBSERVING":
                if kind == "OBJECT_DISAPPEARED":
                    self.transition(
                        "IDLE",
                        "Person disappeared"
                    )

        if (
            self.state == "SEARCHING"
            and self.active_target == TARGET
            and self.detector.present
            and self.visible
        ):
            self.finish_search("FOUND")

    def run(self):
        print("NeuroEye Behavior Manager v0.6")
        print("Mode:", self.mode)
        print("Search timeout:", SEARCH_TIMEOUT, "seconds")

        # Only remove an inactive socket.
        if os.path.exists(SOCKET_PATH):
            probe = socket.socket(
                socket.AF_UNIX, socket.SOCK_STREAM
            )
            try:
                probe.connect(SOCKET_PATH)
            except OSError:
                os.unlink(SOCKET_PATH)
            else:
                probe.close()
                raise RuntimeError(
                    "Command socket already in use"
                )
            finally:
                probe.close()

        self.transition("IDLE", "System ready")

        camera = threading.Thread(
            target=self.camera_loop,
            daemon=True
        )
        server = threading.Thread(
            target=self.socket_loop,
            daemon=True
        )

        camera.start()
        server.start()

        try:
            while self.running.is_set():
                try:
                    kind, data = self.events.get(timeout=0.1)

                    if kind == "detections":
                        self.handle_detections(data)

                    elif kind == "command":
                        command, connection = data
                        self.handle_command(
                            command, connection
                        )

                    elif kind == "error":
                        self.data_ready = False
                        self.visible = False
                        self.log(f"Detection error: {data}")

                except queue.Empty:
                    pass

                if (
                    self.state == "SEARCHING"
                    and self.deadline is not None
                    and time.monotonic() >= self.deadline
                ):
                    self.finish_search("NOT_FOUND")

        except KeyboardInterrupt:
            self.log("Stopping")

        finally:
            self.running.clear()

            if self.waiter is not None:
                self.finish_search("CANCELLED")

            camera.join(timeout=2)
            server.join(timeout=2)

            if os.path.exists(SOCKET_PATH):
                os.unlink(SOCKET_PATH)

            self.log("Behavior Manager stopped")


if __name__ == "__main__":
    BehaviorManager().run()
