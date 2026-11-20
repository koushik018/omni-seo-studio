@echo off
title OmniSEO Studio - Create Desktop Shortcut
chcp 65001 >nul
cls

echo ========================================================
echo   OmniSEO Studio - Desktop Shortcut Installer
echo ========================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "TARGET_BAT=%SCRIPT_DIR%start.bat"
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
set "SHORTCUT_PATH=%DESKTOP_DIR%\OmniSEO Studio.lnk"

echo [*] Location of this tool:
echo     %SCRIPT_DIR%
echo.
echo [*] Installing Desktop Shortcut to:
echo     %SHORTCUT_PATH%
echo.

:: Use PowerShell to create the Windows shortcut
powershell -NoProfile -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$s = $ws.CreateShortcut('%SHORTCUT_PATH%'); " ^
    "$s.TargetPath = '%TARGET_BAT%'; " ^
    "$s.WorkingDirectory = '%SCRIPT_DIR%'; " ^
    "$s.Description = 'Launch OmniSEO Studio Audit Engine'; " ^
    "$s.Save()"

if %errorlevel% equ 0 (
    echo ========================================================
    echo   [SUCCESS] Shortcut created on your Desktop!
    echo   You can now launch OmniSEO Studio from your Desktop
    echo   no matter where you extracted this folder (C: or D:).
    echo ========================================================
) else (
    echo [!] Could not create shortcut automatically.
    echo You can right-click 'start.bat' and select:
    echo   'Send to' -> 'Desktop (create shortcut)'.
)

echo.
pause
