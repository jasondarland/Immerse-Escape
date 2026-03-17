# IMMERSE Designer – Escape Room Edition (MVP)

Professional desktop authoring software for designing, engineering, and programming escape rooms and immersive attractions for the IMMERSE ecosystem.

## MVP features implemented
- Project-based workflow with save/load/autosave/version snapshots
- Dark professional multi-page desktop UI (left nav + center workspace + right inspector + bottom logs)
- Image-based layout system with unlimited room tabs
  - import room backgrounds
  - place doors/props/devices as overlay objects
  - assign object image assets
  - zoom controls (toolbar + Ctrl+wheel + shortcuts)
- Device registry page with runtime-oriented device metadata
  - runtime IDs
  - room assignment
  - addressing + node assignment
- Puzzle flow and logic graph editors with copy/paste/delete + zoom
- **IMMERSEPACK.ZIP export pipeline** that generates runtime-oriented package structure:
  - `immersepack.json`
  - `layout/layouts.json`
  - `devices/devices.json`
  - `logic/logic.json`
  - `timeline/timeline.json`
  - `media/{audio,video,images}/...`
  - `config/system.json`

## Run
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Exporting IMMERSEPACK
Use **File → Export IMMERSEPACK.ZIP**. The app writes a deployable zip named `IMMERSEPACK.ZIP`.

## Notes
This is an MVP foundation designed for future direct compatibility work with IMMERSE Runtime adapters and hardware protocol plugins.
