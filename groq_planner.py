import json
import urllib.request
import urllib.error
from pathlib import Path

from task_protocol import validate_task, execute_simulation

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "qwen/qwen3.8-27b"

SYSTEM_PROMPT = """
You are a task planner for a mobile robot.

Convert Turkish or English user instructions into JSON.

Allowed actions:
SEARCH, FOLLOW, APPROACH, DESCRIBE, LOCATE, STOP

Return exactly one JSON object using this schema:

{
  "action": "SEARCH",
  "target": {
    "class": "person",
    "color": null
  },
  "parameters": {
    "direction": "right"
  },
  "on_success": "STOP"
}

Rules:
- Return valid JSON only.
- Use English object names.
- Directions: left, right, any.
- Use null for unspecified values.
- For "find", use SEARCH.
- For "follow", use FOLLOW.
- For "approach", use APPROACH.
- For "describe", use DESCRIBE.
- For "where is", use LOCATE.
- For "stop", use STOP.
- For multiple steps, return the first action and
  optionally the next action in on_success.
- Never generate GPIO commands or motor speeds.
"""


def load_api_key():
    for line in Path(".env").read_text().splitlines():
        if line.startswith("GROQ_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("GROQ_API_KEY not found")


def ask_groq(command):
    payload = {
        "model": MODEL,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": command}
        ]
    }

    headers = {
        "Authorization": "Bearer " + load_api_key(),
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "curl/8.0.0"
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)

    content = result["choices"][0]["message"]["content"]
    return json.loads(content)


def main():
    print("NeuroSupervisor AI Planner v0.1")
    print("Motor control: DISABLED")
    print("Type 'exit' to quit")

    while True:
        try:
            command = input("\nKomut > ").strip()

            if not command:
                continue

            if command.lower() in ("exit", "quit", "cikis"):
                break

            plan = ask_groq(command)

            print("\nAI PLAN:")
            print(json.dumps(plan, indent=2, ensure_ascii=False))

            task = validate_task(plan)
            execute_simulation(task)

        except KeyboardInterrupt:
            break

        except urllib.error.HTTPError as exc:
            print("Groq HTTP error:", exc.code)
            print(exc.read().decode(errors="replace")[:500])

        except Exception as exc:
            print("ERROR:", type(exc).__name__, str(exc))


if __name__ == "__main__":
    main()
