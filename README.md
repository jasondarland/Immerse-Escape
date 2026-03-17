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

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m immerse_occ
```

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
