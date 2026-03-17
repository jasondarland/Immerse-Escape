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
