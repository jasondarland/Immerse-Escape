# IMMERSE Runtime – Escape Room Edition

A professional desktop runtime MVP for escape rooms and immersive attractions.

## Features
- Runtime dashboard with live operational status
- Session control with timer, puzzle actions, and operator notes
- Device monitor with simulated nodes and device actions
- Logic/state monitor with progression, conditions, and variables
- Event log with search/filter/export
- Outputs/cue monitor
- Alerts and faults center
- Settings and connection configuration
- Demo package with 2 rooms and realistic mock progression

## Quick start

### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m immerse_runtime.main
```

### Windows Command Prompt
```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -e .
python -m immerse_runtime.main
```

### macOS / Linux
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m immerse_runtime.main
```

## Alternative launch options
- If the editable install script is not on your PATH, run `python -m immerse_runtime.main` instead.
- On Windows, you can also use the included launcher scripts:
  - PowerShell: `./run_runtime.ps1`
  - Command Prompt: `run_runtime.bat`
- If PowerShell blocks script execution, run:
  `powershell -ExecutionPolicy Bypass -File .\run_runtime.ps1`

## Demo package
The bundled `demo_package/` folder contains a complete sample runtime package for immediate use.

## Logs and crash reporting
- Runtime logs are written to `logs/immerse_runtime.log`.
- Unhandled exceptions and fatal interpreter traces are written to `logs/immerse_runtime_crash.log`.
- If the app fails at launch, start it from a terminal to see the console message and then send the contents of those log files.
- The app now searches multiple locations for the bundled demo package in packaged builds and can reconstruct it from internal bundled resources if the external `demo_package/` folder is missing.
