@echo off
setlocal

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m immerse_runtime.main
    exit /b %ERRORLEVEL%
)

python -m immerse_runtime.main
exit /b %ERRORLEVEL%
