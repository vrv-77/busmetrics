@echo off
setlocal

cd /d "%~dp0..\frontend"

if not exist "node_modules" (
  echo [INFO] Instalando dependencias de frontend...
  call npm install
  if errorlevel 1 (
    echo [ERROR] Fallo npm install
    pause
    exit /b 1
  )
)

start "BusMetric Frontend" cmd /k "npm run dev"

echo Frontend iniciado en http://localhost:3000
endlocal
