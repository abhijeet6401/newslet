@echo off

echo 🚀 Setting up Financial News Extraction System...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📥 Installing requirements...
pip install -r requirements.txt

REM Create data directory
echo 📁 Creating data directory...
if not exist data mkdir data

REM Create static directory
if not exist static mkdir static

echo ✅ Setup complete!
echo.
echo To run the application:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run the app: python app.py
echo   3. Open browser to: http://localhost:5000
echo.
echo 🎉 Happy newsletter generation!
pause