# IMMERSE Designer – Escape Room Edition (MVP)

A professional desktop authoring platform for escape rooms and immersive attractions targeting IMMERSE Runtime.

## Fully built working pages
- Dashboard (status widgets, recent projects/exports, warnings, activity, room overview)
- Projects (browse/create/duplicate/rename/delete/open, metadata editing, search)
- Layout (multi-room image-based editor + massive drag/drop escape-room object library)
- Devices (runtime device registry editor)
- Puzzle Flow + Logic (node editing with zoom + clipboard)
- Timeline (track/cue editor with trigger modes and cue data)
- Operator (live action controls + timer + status lists)
- Simulator (event injection controls + logic/state log)
- Reports (report type generator + preview + filtering controls)
- Settings (project/runtime/simulation/timeline defaults)

## IMMERSEPACK export
Export creates `IMMERSEPACK.ZIP` with runtime-oriented structure:
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
- `operator/operator_controls.json`
- `config/runtime_config.json`
- `reports/build_manifest.json`

## Validation before export
Checks include:
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
