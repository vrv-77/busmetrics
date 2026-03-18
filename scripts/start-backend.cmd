@echo off
setlocal

cd /d "%~dp0..\backend"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] No existe backend\.venv\Scripts\python.exe
  echo Crea el entorno primero:
  echo   cd backend
  echo   python -m venv .venv
  echo   .venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)

set AUTO_INIT_DB=false
set FAIL_ON_STARTUP_DB_ERROR=false

start "BusMetric Backend" cmd /k ".venv\Scripts\python.exe run.py"

echo Backend iniciado en http://localhost:8000
endlocal
