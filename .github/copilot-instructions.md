# Nomad OS Copilot Instructions

## Project overview
- This project is a Python-based Raspberry Pi robot assistant.
- The package source lives in src/nomad.
- Tests are in tests/ and should be kept passing.

## Development workflow
- Use the existing project environment for local development.
- Prefer editable installs for local development when needed:
  - `python -m pip install -e .`
  - `python -m nomad.main chat`
  - `python -m nomad.main voice`
  - `python -m unittest discover -q`
- Keep the project working without requiring hardware for core chat and voice CLI flows.

## Python version
- Target Python 3.11+.
- Avoid introducing dependencies that break compatibility with the current environment.

## Code conventions
- Keep changes small and focused.
- Preserve existing test coverage when changing behavior.
- Prefer adding targeted tests for new features or regressions.
- Keep CLI and voice flows graceful when optional hardware dependencies are unavailable.

## Notes for voice features
- The voice CLI should fall back to keyboard input when microphone support is unavailable.
- Avoid hard failures when optional speech libraries or audio backends are missing.
