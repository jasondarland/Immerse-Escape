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
  package_loader.py
  pack_builder.py
  validation.py
  models.py
  sample_data.py
  styles.py
  services.py
  ui_main.py

tools/
  build_immersepack.py

examples/
  manifest.json
```

## Notes
This MVP uses simulated runtime data and mock command dispatch while keeping architecture ready for integration with live show-control backends.

## Crash Diagnostics
If the application fails very early during startup, diagnostic information is written to:

`~/.immerse_occ_startup.log`

On Windows, this resolves to:

`C:\Users\<your-user>\.immerse_occ_startup.log`

## Official Package Format: `.immersepack`

`*.immersepack` is now the primary package format (ZIP container).

Accepted package sources in OCC:
- `.immersepack` (primary)
- `.zip` (legacy/backward compatible)
- folder path (dev mode)

Use:
- **Load Package (.immersepack/.zip)** for file packages
- **Load Package Folder** for unpacked dev packages

The OCC validates package structure before loading and displays:
- project name
- version
- room count
- device count

### Required official structure
```
manifest.json
payload/
  immersepack.json
  project/project.json
  devices/devices.json
  devices/patch.json
  logic/logic_graph.json
  logic/states.json
  timeline/timeline.json
  media/media_index.json
  operator/operator_controls.json
  config/runtime_config.json
```

Optional directories:
- `checksums/`
- `assets/`

### Loader behavior
1. If `manifest.json` exists, use `manifest["payload_root"]` or default `payload`.
2. Else if `payload/` exists, use `payload/`.
3. Else, treat package root as payload.

### Security and validation
- Safe extraction blocks path traversal (`../`) entries.
- Archives extract to temporary folder:
  - `%TEMP%/immerse_runtime/<uuid>/` on Windows
  - equivalent temp directory on macOS/Linux
- Required files are validated for official `.immersepack` packages.

Errors:
- `PackageValidationError("Invalid IMMERSEPACK: missing required files ...")`
- `PackageValidationError("Invalid manifest: ...")`

### Logging
Package loader logs include:
- `INFO Loading IMMERSEPACK`
- `INFO Detected payload root`
- `INFO Validation passed`
- `ERROR Missing required files`
- `ERROR Invalid manifest`

## Legacy compatibility
- `.zip` without `manifest.json` remains supported.
- Unpacked folder packages remain supported.
- Legacy room/device/show element JSON layouts remain supported as fallback.

## Designer Export / Builder Utility

Example manifest is included at:
- `examples/manifest.json`

Build an official `.immersepack` from a prepared payload source folder:

```bash
PYTHONPATH=src python tools/build_immersepack.py /path/to/payload_source ./MyShow_v1.immersepack --version 1.0.0
```

Programmatic export helper:
- `src/immerse_occ/pack_builder.py::export_immersepack(...)`
