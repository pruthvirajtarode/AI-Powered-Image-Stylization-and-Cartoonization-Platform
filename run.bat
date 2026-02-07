@echo off
REM Quick start script - Run this after setup is complete

echo Starting Toonify SaaS Backend (Flask)...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Update dependencies if needed
pip install -r requirements.txt

REM Run Flask app
echo Launching server at http://localhost:5000
python backend.py

pause
