@echo off
echo ============================================
echo   Fake News Detector - Setup Script
echo ============================================
echo.

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo.

echo [2/4] Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 16 or higher.
    pause
    exit /b 1
)
echo.

echo [3/4] Setting up Backend...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate
echo Installing Python dependencies...
pip install -r requirements.txt
echo.

echo [4/4] Setting up Frontend...
cd ..\frontend
if not exist node_modules (
    echo Installing Node dependencies...
    call npm install
)
echo.

echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo To start the application:
echo   1. Backend: cd backend ^& venv\Scripts\activate ^& python app.py
echo   2. Frontend: cd frontend ^& npm run dev
echo.
echo Or use start.bat to run both
echo.
pause
