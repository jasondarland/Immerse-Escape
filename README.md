# IMMERSE Remote OCC – Escape Room Operator

Professional desktop/tablet-style Operator Control Console MVP for live escape room operations.

## Features
- Two fully working pages:
  - **Operator Controls**
  - **Show Elements / Effects Trigger**
- Touchscreen-friendly dark UI
- Live simulated status engine
- Command dispatch service ready for future transport adapters (TCP/WebSocket/MQTT/REST)
- Timestamped event log
- Room and category filtering
- Example production-style data (Lab A / Lab B)

## Run (macOS / Linux)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m immerse_occ
```

## Run (Windows PowerShell)
> Run these commands from the **repository root** (the folder containing `README.md`, `pyproject.toml`, and `src/`).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m immerse_occ
```

If your PowerShell version does not support `&&`, run one command per line (or use `;`).

**Important:** do not paste commands with a leading `&&` at the start of the line.
For example, this is invalid in Windows PowerShell 5.x and will throw the parser error you saw:

```powershell
&& python -m compileall src
```

## Quick Validation Check
From repository root:

```powershell
python -m compileall src
```

If you run this from `src\immerse_occ`, it will fail with `Can't list 'src'` because there is no nested `src` folder there.

## Project Structure
```
src/immerse_occ/
  __init__.py
  __main__.py
  app.py
  models.py
  sample_data.py
  styles.py
  services.py
  ui_main.py
```

## Notes
This MVP uses simulated runtime data and mock command dispatch while keeping architecture ready for integration with live show-control backends.

## Crash Diagnostics
If the application fails very early during startup, diagnostic information is written to:

`~/.immerse_occ_startup.log`

On Windows, this resolves to:

`C:\Users\<your-user>\.immerse_occ_startup.log`

## Importing `immersepack.zip`
Use the **Load ImmersePack ZIP** button in the top bar of the Operator Controls page.

Supported pack layouts:

1. `immersepack.json` (or `manifest.json` / `pack.json`) at any path in the zip:

```json
{
  "rooms": [
    {
      "id": "lab_a",
      "name": "Lab A",
      "puzzles": [{"id": "a1", "name": "Calibrate Reactor"}],
      "reset_checklist": ["Re-lock main door"]
    }
  ],
  "devices": [
    {"id": "door_a", "name": "Lab A Main Door", "room_id": "lab_a", "kind": "door", "status": "locked"}
  ],
  "show_elements": [
    {"id": "cue_alarm", "name": "Alarm", "room_id": "lab_a", "category": "Audio", "status": "ready"}
  ]
}
```

2. Separate files: `rooms.json` (required), plus optional `devices.json`, `show_elements.json`.
3. Fallback folder scan: `/rooms/<room-name>/...` (creates room list even if no device/cue JSON exists).

When loaded, the app automatically rebuilds room selectors and filters so room count and content come from your pack.
