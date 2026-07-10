@echo off
cd /d "%~dp0"

if exist "C:\Python312\pythonw.exe" (
    start "" "C:\Python312\pythonw.exe" "%~dp0src\main.py"
    exit /b 0
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%~dp0src\main.py"
    exit /b 0
)

start "" python "%~dp0src\main.py"
exit /b 0
