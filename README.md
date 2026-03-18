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
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
immerse-runtime
```

## Demo package
The bundled `demo_package/` folder contains a complete sample runtime package for immediate use.


## Logs and crash reporting
- Runtime logs are written to `logs/immerse_runtime.log`.
- Unhandled exceptions and fatal interpreter traces are written to `logs/immerse_runtime_crash.log`.
- If the app fails at launch, start it from a terminal to see the console message and then send the contents of those log files.

- The app now searches multiple locations for the bundled demo package in packaged builds and can reconstruct it from internal bundled resources if the external `demo_package/` folder is missing.
