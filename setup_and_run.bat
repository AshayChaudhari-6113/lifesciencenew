@echo off
setlocal

echo ==========================================
echo   Life Sciences Agent - Setup & Run
echo ==========================================

REM Check if Python 3.13 is available via py launcher
py -3.13 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.13 is not found via 'py' launcher.
    echo Please install Python 3.13 from python.org and ensure it is added to PATH.
    echo.
    echo Current Python versions found:
    py --list
    pause
    exit /b 1
)

echo [INFO] Found Python 3.13.

REM Create Virtual Environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment 'venv' using Python 3.13...
    py -3.13 -m venv venv
) else (
    echo [INFO] Virtual environment 'venv' already exists.
)

REM Activate Virtual Environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

REM Install Dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt

REM Run Application
echo [INFO] Starting Streamlit App...
streamlit run app_streamlit.py

pause
