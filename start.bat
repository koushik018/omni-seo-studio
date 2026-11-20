@echo off
title OmniSEO Studio - Launcher
chcp 65001 >nul
cls

echo ========================================================
echo   OmniSEO Studio - Portable Web Audit ^& Ranking Engine
echo ========================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found on your system!
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo Make sure to CHECK "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Display Python Version
echo [OK] Python detected:
python --version
echo.

:: 3. Install / Verify Requirements
echo [*] Checking dependencies...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [WARNING] Encountered an issue installing requirements. Retrying...
    python -m pip install -r requirements.txt
)

echo [OK] All dependencies are ready.
echo.
echo ========================================================
echo   Launching server on http://localhost:8000
echo   Press Ctrl+C in this terminal to stop the server.
echo ========================================================
echo.

:: 4. Auto-open browser after 2 seconds
start "" cmd /c "timeout /t 2 >nul & start http://localhost:8000"

:: 5. Run Server
python run.py

pause
