# NeuroEye — Behavior Architecture v1.0

**Status:** Approved architecture baseline  
**Default autonomy mode:** `AWARE`  
**Development branch:** `feature/neurosupervisor`

## 1. Mission

NeuroEye is an autonomous, socially interactive robot that continuously perceives its environment, communicates with its user, and performs controlled actions based on commands or significant environmental events.

The system must be modular, predictable, interruptible, and safety-oriented.

## 2. Core principles

1. Continuous perception independent of AI response latency.
2. Balanced autonomy with explicit permission boundaries.
3. Local reflexes and safety decisions must not depend on cloud AI.
4. Groq AI proposes goals and interprets instructions; it does not control motors directly.
5. All actions must have defined entry, completion, cancellation, and failure conditions.
6. Existing working modules must remain independently testable.

## 3. Modules

| Module | Responsibility |
|---|---|
| NeuroEye | Camera, object detection, HTTP endpoints |
| Event Detector | Detect meaningful environmental changes |
| NeuroSupervisor | Coordinate behavior, state, and priorities |
| Groq Planner | Conversation, interpretation, task proposals |
| Behavior Manager | Select and transition between behaviors |
| Autonomy Policy | Authorize autonomous actions |
| Safety Controller | Enforce safety limits and emergency stops |
| Task Executor | Execute approved tasks |

## 4. Autonomy modes

- `PASSIVE`: Observation and explicit user commands only.
- `AWARE`: Continuous observation, attention, and limited autonomous interaction. No autonomous physical displacement.
- `AUTONOMOUS`: Limited independent movement when hardware, permissions, and safety conditions allow it.

**Default: AWARE.**

Mode changes must be explicit and logged. A mode cannot override safety rules.

## 5. Behavior states

`BOOT`, `IDLE`, `CONVERSATION`, `OBSERVING`, `SEARCHING`, `FOLLOWING`, `EXPLORING`, `REFLEX`, `SAFE_STOP`.

Conversation and perception may continue alongside compatible activities. Motion-related tasks are centrally coordinated.

## 6. Priority policy

1. P0 — Emergency safety intervention
2. P1 — User STOP command
3. P2 — Explicit user tasks
4. P3 — Local reflexes and attention events
5. P4 — Autonomous curiosity and exploration
6. P5 — Routine interaction

Safety intervention always takes precedence over motion. Lower-priority actions must not interrupt higher-priority tasks.

## 7. Event model

Initial events:

- `OBJECT_APPEARED`
- `OBJECT_DISAPPEARED`
- `TARGET_MOVED`
- `SUDDEN_CHANGE`
- `TARGET_ACQUIRED`
- `TARGET_LOST`

Events must include timestamps, source, and supporting detection information where available.

Object appearance and disappearance require temporal confirmation to reduce false positives.

Camera-only sudden changes must not automatically trigger backward movement. Physical avoidance requires appropriate safety verification.

## 8. Startup contract

The user starts the system manually with:

`neuro-eye`

Startup order:

1. Start NeuroEye camera and HTTP server if not running.
2. Wait for the detection endpoint.
3. Start NeuroSupervisor if not running.
4. Open the interactive Groq Planner.

No automatic boot startup is required.

The initial behavior mode is `AWARE`.

## 9. Task lifecycle

`CREATED → VALIDATED → ACCEPTED → RUNNING → COMPLETED`

Alternative terminal states:

`CANCELLED`, `FAILED`, `TIMED_OUT`.

`STOP` must interrupt motion-related tasks. The Safety Controller may reject or interrupt any unsafe movement.

## 10. Current implementation status

Working:

- Continuous camera and SSD MobileNet V2 detection
- HTTP detection endpoint
- NeuroSupervisor live detection analysis
- Groq natural-language task planning
- Task validation
- Single-frame live task matching
- Unified manual startup command

Not yet implemented:

- Persistent behavior state machine
- Event Detector
- Autonomous behavior execution
- Full conversational audio pipeline
- Physical motor control
- Verified collision avoidance

## 11. Development sequence

1. Event Detector — detection changes and temporal confirmation
2. Behavior Manager — states and priorities
3. Autonomy Policy — AWARE-mode permissions
4. Safety Controller — movement authorization
5. Integrated task lifecycle
6. Conversation and speech integration
7. Motor integration and physical safety testing

Each module must be tested independently before integration.

## 12. Architecture invariant

**NeuroEye perceives. Groq reasons. NeuroSupervisor coordinates. Safety Controller protects. Task Executor acts.**

No module may bypass the Safety Controller to command physical movement.
