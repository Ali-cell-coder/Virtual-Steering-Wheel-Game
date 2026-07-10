@echo off
cd /d "%~dp0"

start cmd /k "call .venv\Scripts\activate.bat && py src\main.py"

timeout /t 2 >nul

start cmd /k "call .venv\Scripts\activate.bat && py game\main.py"

exit