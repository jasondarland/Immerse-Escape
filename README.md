# IMMERSE Designer – Escape Room Edition (MVP)

Professional desktop authoring software for designing, engineering, and programming escape rooms and immersive attractions for the IMMERSE Runtime ecosystem.

## Runtime-oriented MVP delivered
- Dark professional multi-page desktop UI (left nav + center workspace + right inspector + bottom log)
- Image-first layout workflow with unlimited rooms and overlay placement
- Device registry page for runtime-addressable hardware definitions
- Node-based puzzle/logic editing foundations with zoom + clipboard tools
- Project save/load/autosave/version snapshots
- **Direct Runtime package export:** `IMMERSEPACK.ZIP`
- Pre-export **validation pass** with issue reporting and build manifest

## IMMERSEPACK.ZIP output structure
The exporter now produces Runtime-ready files:

- `immersepack.json`
- `project/project.json`
- `layout/rooms.json`
- `layout/backgrounds/...`
- `devices/devices.json`
- `devices/patch.json`
- `logic/logic_graph.json`
- `logic/states.json`
- `timeline/timeline.json`
- `media/media_index.json`
- `media/audio/...`
- `media/video/...`
- `media/images/...`
- `operator/operator_controls.json`
- `config/runtime_config.json`
- `reports/build_manifest.json`

## Validation checks (MVP)
- missing device IDs
- duplicate addresses
- broken logic links
- missing media files
- invalid node assignments
- empty operator actions
- timeline cues with missing targets
- invalid room references
- unsupported protocols

## Run
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Export
Use **File → Export IMMERSEPACK.ZIP**. Export is blocked when validation contains errors.
