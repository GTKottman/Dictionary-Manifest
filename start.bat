@echo off
setlocal
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
  set "PY=venv\Scripts\python.exe"
  set "PIP=venv\Scripts\pip.exe"
  set "UV=venv\Scripts\uvicorn.exe"
) else (
  where py >nul 2>&1 && set "PY=py" && set "UV=uvicorn" && goto :check_frontend
  where python >nul 2>&1 && set "PY=python" && set "UV=uvicorn" && goto :check_frontend
  echo No Python found. Create a venv:  py -3 -m venv venv
  echo Then: venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)

:check_frontend
if not exist "frontend\dist\index.html" (
  echo Building frontend for the first time...
  where node >nul 2>&1 || (
    echo Node.js is required to build the frontend. Install from https://nodejs.org
    pause
    exit /b 1
  )
  cd frontend
  call npm install --silent
  call npm run build
  cd ..
  echo Frontend built.
  echo.
)

:run
echo Lexicon Shaper v2  -  http://127.0.0.1:8000
echo Press Ctrl+C to stop.
echo.
"%UV%" main:app --host 127.0.0.1 --port 8000
if errorlevel 1 pause
