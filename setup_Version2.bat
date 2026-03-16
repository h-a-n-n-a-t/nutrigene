@echo off
echo 🧬 NutriGene Setup Script
echo ========================

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r backend\requirements.txt

REM Create database
echo Initializing database...
python -c "from backend.database import DatabaseManager; db = DatabaseManager(); db.load_gene_data('backend\gene_data.json'); print('✓ Database initialized successfully')"

echo.
echo ✓ Setup complete!
echo.
echo To run the application:
echo   1. Start backend: venv\Scripts\activate && python backend\app.py
echo   2. Open frontend: Open frontend\index.html in a web browser
echo.
pause