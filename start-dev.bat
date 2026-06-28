@echo off
setlocal
cd /d "%~dp0"

echo Lexicon Shaper v2 - Development Mode
echo   Backend:  http://127.0.0.1:8000  (API + docs at /docs)
echo   Frontend: http://127.0.0.1:5173  (Vite hot-reload)
echo Press Ctrl+C in each window to stop.
echo.

if exist "venv\Scripts\uvicorn.exe" (
  set "UV=venv\Scripts\uvicorn.exe"
) else (
  set "UV=uvicorn"
)

start "Lexicon API" cmd /k "cd /d "%~dp0" && "%UV%" main:app --host 127.0.0.1 --port 8000 --reload"
start "Lexicon Frontend" cmd /k "cd /d "%~dp0\frontend" && npm run dev"
