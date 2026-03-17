# Escape Room Designer (MVP)

A desktop MVP for designing and programming escape room experiences.

## Features in this MVP
- Project-based workflow with save/load/export and demo project
- Professional dark themed multi-page desktop UI
- Sidebar navigation and dock panels (inspector + system log)
- Visual layout editor with unlimited rooms, per-room backgrounds, and image-based props/devices
- Puzzle flow node editor (graph-style puzzle relationships) with copy/paste shortcuts
- Logic editor framework (input/logic/output nodes) with copy/paste shortcuts
- Keyboard editing shortcuts (Ctrl+C/Ctrl+V/Ctrl+X/Delete/Ctrl+D) across editors
- Scalable architecture for future hardware integrations

## Run
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

## Project layout
- `main.py` application entry point
- `src/escape_room_designer/` source package
- `src/escape_room_designer/demo_data/` sample project JSON

## Notes
This version is an MVP scaffold intended for rapid expansion into show-control and hardware protocols (OSC/MQTT/DMX/etc.).
