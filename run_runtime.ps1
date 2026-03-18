$ErrorActionPreference = 'Stop'

if (Test-Path '.venv\Scripts\python.exe') {
    & '.venv\Scripts\python.exe' -m immerse_runtime.main
    exit $LASTEXITCODE
}

python -m immerse_runtime.main
exit $LASTEXITCODE
