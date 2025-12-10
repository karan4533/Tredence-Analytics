@echo off
REM Setup script for Windows

echo ==================================
echo Workflow Engine Setup
echo ==================================

REM Check Python version
echo.
echo Checking Python version...
python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ==================================
echo Setup complete!
echo ==================================
echo.
echo Next steps:
echo   1. Activate the environment: venv\Scripts\activate
echo   2. Start the server: python -m uvicorn app.main:app --reload
echo   3. Visit: http://localhost:8000/docs
echo.
pause
