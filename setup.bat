@echo off
REM Toonify SaaS - Automated Setup Script for Windows
REM This script automates the entire setup process for the Flask-based platform

echo ========================================
echo    Toonify SaaS Setup Script
echo    AI-Powered Image Cartoonization
echo ========================================
echo.

REM Check Python installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)
python --version
echo.

REM Create virtual environment
echo [2/6] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

REM Install dependencies
echo [4/6] Installing dependencies...
echo This may take 2-5 minutes...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

REM Initialize database
echo [5/6] Initializing database...
python scripts\init_db.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
echo.

REM Run tests
echo [6/6] Running tests...
echo Testing authentication module...
python tests\test_auth.py
echo.
echo Testing image processing module...
python tests\test_processing.py
echo.
echo Testing payment module...
python tests\test_payment.py
echo.

echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo To start the application:
echo   1. Activate virtual environment: venv\Scripts\activate
2. Run the app: python backend.py
echo.
echo The application will be available at: http://localhost:5000
echo.
echo For more information, see MODERN_FULLSTACK_README.md
echo.
pause
