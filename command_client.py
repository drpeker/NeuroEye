import socket
import sys
import json

SOCKET = "/tmp/neuroeye-command.sock"

command = " ".join(sys.argv[1:]).strip()

if not command:
    print("Usage: python command_client.py SEARCH person")
    sys.exit(1)

try:
    with socket.socket(
        socket.AF_UNIX, socket.SOCK_STREAM
    ) as client:
        client.settimeout(20)
        client.connect(SOCKET)
        client.sendall(command.encode())

        response = b""

        while b"\n" not in response:
            chunk = client.recv(4096)
            if not chunk:
                break
            response += chunk

        if response:
            result = json.loads(response.decode())
            print(json.dumps(
                result,
                ensure_ascii=False,
                indent=2
            ))
        else:
            print("ERROR: No response")

except (OSError, ValueError) as exc:
    print("ERROR:", exc)
    sys.exit(1)
