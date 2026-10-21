from dataclasses import dataclass, field
from typing import Optional

ACTIONS = {
    "SEARCH",
    "FOLLOW",
    "APPROACH",
    "DESCRIBE",
    "LOCATE",
    "STOP",
}

MOTION_ACTIONS = {"SEARCH", "FOLLOW", "APPROACH"}


@dataclass
class Task:
    action: str
    target_class: Optional[str] = None
    target_color: Optional[str] = None
    direction: Optional[str] = None
    on_success: Optional[str] = None
    parameters: dict = field(default_factory=dict)


def validate_task(data: dict) -> Task:
    if not isinstance(data, dict):
        raise ValueError("Task must be a JSON object")

    action = data.get("action")

    if not isinstance(action, str) or action not in ACTIONS:
        raise ValueError(f"Unsupported action: {action}")

    target = data.get("target") or {}
    params = data.get("parameters") or {}

    if not isinstance(target, dict):
        raise ValueError("target must be an object")

    if not isinstance(params, dict):
        raise ValueError("parameters must be an object")

    target_class = target.get("class")
    target_color = target.get("color")
    direction = params.get("direction")
    on_success = data.get("on_success")

    for name, value in (
        ("target.class", target_class),
        ("target.color", target_color),
    ):
        if value is not None and (
            not isinstance(value, str) or not value.strip()
        ):
            raise ValueError(f"Invalid {name}")

    if direction is not None and direction not in (
        "left", "right", "any"
    ):
        raise ValueError("Invalid direction")

    if on_success is not None and on_success not in ACTIONS:
        raise ValueError("Invalid on_success")

    if action in {"SEARCH", "FOLLOW", "APPROACH", "LOCATE"}:
        if not target_class:
            raise ValueError("Target class is required")

    return Task(
        action=action,
        target_class=target_class,
        target_color=target_color,
        direction=direction,
        on_success=on_success,
        parameters=params,
    )


def execute_simulation(task: Task):
    print("\n===== NEUROSUPERVISOR TASK =====")
    print("Action:", task.action)
    print("Target:", task.target_class)
    print("Color:", task.target_color)
    print("Direction:", task.direction)
    print("On success:", task.on_success)

    if task.action in MOTION_ACTIONS:
        print("Status: MOTION DISABLED (simulation only)")
    elif task.action == "STOP":
        print("Status: STOP requested")
    else:
        print("Status: Task accepted for future execution")
