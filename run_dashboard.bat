@echo off
rem Double-click launcher for the CMO dashboard generator (needs Python installed).
rem You can also drag a .db3 file onto this .bat to build that specific database.
rem No Python? Download the prebuilt build_dashboard.exe from the project's Releases page instead.
setlocal
cd /d "%~dp0"
echo Building your Command: Modern Operations dashboard...
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py build_dashboard.py %*
    goto done
)
where python >nul 2>nul
if %errorlevel%==0 (
    python build_dashboard.py %*
    goto done
)

echo Python was not found on this PC.
echo.
echo Easiest fix: download the prebuilt build_dashboard.exe from the project's
echo GitHub Releases page - it needs no Python at all.
echo.
echo Or install Python from https://www.python.org/downloads/
echo (on the first screen, tick "Add python.exe to PATH"), then run this again.

:done
echo.
pause
