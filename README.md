# IMMERSE Escape Simulator

A Windows-first PySide6 desktop MVP that simulates the IMMERSE Escape stack locally on one machine.

## Run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
immerse-escape-simulator
```

## Features

- Modular local runtime engine, state manager, node simulator, media simulator, and OCC controller.
- Ten simulator pages: dashboard, room view, player inputs, runtime state, node simulator, operator controls, event log, cue monitor, package loader, and settings.
- Bundled two-room demo package with keypad, RFID, and sequence puzzle flow.
- Dark IMMERSE-inspired operator UI theme.
