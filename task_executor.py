from neurosupervisor import read_detections, analyze

def execute_live(task):
    print("\n===== LIVE TASK =====")
    print("Action:", task.action)
    print("Target:", task.target_class)

    if task.action == "STOP":
        print("Status: STOPPED")
        return

    detections = analyze(read_detections())

    matches = [
        obj for obj in detections
        if obj["class"] == task.target_class
    ]

    if not matches:
        print("Status: TARGET NOT FOUND")
        return

    target = max(matches, key=lambda obj: obj["confidence"])

    print("Status: TARGET DETECTED")
    print("Direction:", target["direction"])
    print("X:", target["x"])
    print("Area:", target["area"])

    if task.target_color:
        print("Color verification: NOT AVAILABLE")

    print("Motor control: DISABLED")
