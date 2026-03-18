@echo off
setlocal

for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
  taskkill /PID %%p /F >nul 2>nul
)

for /f "tokens=5" %%p in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
  taskkill /PID %%p /F >nul 2>nul
)

echo Puertos 8000 y 3000 liberados.
endlocal
