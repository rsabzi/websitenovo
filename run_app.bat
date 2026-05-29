@echo off
title AI File Organizer Launcher
echo Starting AI File Organizer...

:: Set project root directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

:: Set Python path to virtual environment
set PYTHON=%PROJECT_ROOT%.venv\Scripts\python.exe

:: Check if virtual environment exists
if not exist "%PYTHON%" (
    echo Error: Virtual environment not found at %PYTHON%
    echo Please make sure you have created the .venv folder.
    pause
    exit /b
)

:: Run frontend (which starts backend automatically)
echo Launching Frontend and Backend...
cd frontend
npm run dev

pause
