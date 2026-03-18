@echo off
setlocal

call "%~dp0start-backend.cmd"
call "%~dp0start-frontend.cmd"

echo.
echo Servicios locales:
echo   - Backend:  http://localhost:8000
echo   - Frontend: http://localhost:3000
echo.
echo Si ves datos vacios, configura DATABASE_URL en backend\.env.

endlocal
