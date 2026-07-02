# Nomad OS Architecture Guide

> High-level overview of the project layout and the responsibility of each directory.

```
nomad-os/
│
├── config/
├── src/
│   └── nomad/
│       ├── ai/
│       ├── api/
│       ├── core/
│       ├── hardware/
│       ├── sensors/
│       ├── ui/
│       ├── voice/
│       └── main.py
│
├── tests/
│
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

# config/

Configuration that changes between machines without changing code.

### Contains

- `settings.yaml`
  - Main application configuration
  - AI model
  - feature flags
  - runtime options

- `devices.yaml`
  - Hardware definitions
  - GPIO pins
  - displays
  - microphones
  - sensors

- `secrets.env`
  - API keys
  - passwords
  - tokens

**Rule**

> Code should *read* from config, never hardcode values.

---

# src/

Everything that becomes the Nomad application.

Think of this as:

> "Everything the robot knows how to do."

---

# src/nomad/core/

The operating system.

Everything eventually passes through Core.

Responsibilities:

- startup
- shutdown
- runtime
- state management
- configuration
- event routing
- conversation lifecycle
- logging

Files:

```
config.py
conversation.py
event_bus.py
logger.py
runtime.py
state.py
```

If Nomad had a heart...

**core** would be it.

---

# src/nomad/ai/

The intelligence.

Responsibilities:

- reasoning
- prompt construction
- memory
- LLM interaction

Files:

```
brain.py
memory.py
prompts.py
```

Think of this as:

```
Human Brain
```

It decides **what** to do.

It should **not** know HOW hardware works.

---

# src/nomad/voice/

Everything involving speech.

Responsibilities

- wake word
- speech recognition
- command parsing
- text-to-speech

Files

```
wakeword.py
speech_to_text.py
text_to_speech.py
commands.py
```

Pipeline:

```
Microphone
      ↓
Wake Word
      ↓
Speech To Text
      ↓
Command Parser
      ↓
AI Brain
      ↓
Text To Speech
      ↓
Speaker
```

---

# src/nomad/hardware/

Physical devices.

Responsibilities

- microphone
- speakers
- camera
- GPIO

Files

```
camera.py
gpio.py
mic.py
speakers.py
```

These modules should expose simple APIs like:

```
camera.capture()

speaker.play()

mic.listen()
```

The AI shouldn't know *how* they work.

---

# src/nomad/sensors/

Passive information.

Unlike hardware, sensors generally **report** information rather than perform actions.

Examples:

```
battery.py

gps.py

imu.py
```

Examples of information:

- battery level
- location
- movement
- orientation

---

# src/nomad/ui/

Everything visual.

Responsibilities

- animations
- display drawing
- face rendering

Files

```
animations.py
display.py
face.py
```

Eventually this becomes:

```
+------------------+

  (^_^)

"Good morning."

+------------------+
```

---

# src/nomad/api/

Interfaces for external software.

Current:

```
server.py
```

Eventually this becomes:

- REST API
- WebSocket
- Mobile App connection
- Remote control

---

# main.py

The application's entry point.

Ideally its job is only:

```
load config

↓

initialize runtime

↓

start services

↓

run forever
```

If `main.py` becomes hundreds of lines long, it's usually a sign that logic belongs elsewhere.

---

# tests/

Unit tests.

Each major subsystem should have matching tests.

Current:

```
test_brain.py
test_conversation.py
test_event_bus.py
test_runtime.py
test_voice_cli.py
```

A good rule:

```
Every important module
        ↓
Should have
        ↓
A matching test module
```

---

# Dependency Flow

One thing I recommend keeping as the project grows:

```
                main.py
                    │
                    ▼
                 runtime
                    │
        ┌───────────┼────────────┐
        ▼           ▼            ▼
      Voice       API         Sensors
        │           │            │
        └──────┬────┘            │
               ▼                 │
             AI Brain            │
               │                 │
               ▼                 │
           Conversation          │
               │                 │
               ▼                 │
             Hardware ◄──────────┘
               │
               ▼
               UI
```

Notice that **Core** sits in the middle, while AI, Voice, Hardware, UI, and Sensors remain independent. This keeps the project modular and makes it easier to swap implementations (for example, replacing one speech engine or hardware platform without affecting the rest of the system).

---

# Mental Model

Instead of thinking in folders, think in responsibilities:

```
main.py
    │
    ▼
Core
    │
    ├── AI        → Think
    ├── Voice     → Listen & Speak
    ├── Hardware  → Control devices
    ├── Sensors   → Observe the world
    ├── UI        → Show information
    └── API       → Talk to other software
```