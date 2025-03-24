@echo off
setlocal

REM Set the path to the virtual environment
set VENV_PATH=C:\Users\mandriamitantsoa\Downloads\mvola\venv

REM Set the path to the script
set SCRIPT_PATH=C:\Users\mandriamitantsoa\Downloads\mvola\script.py

REM Activate the virtual environment
call "%VENV_PATH%\Scripts\activate.bat"

REM Run the Python script
python "%SCRIPT_PATH%"

REM Deactivate the virtual environment
deactivate

endlocal
