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
pip install -r backend\backend_requirements.txt

REM Create database
echo Initializing database...
python -c "from backend.backend_database import DatabaseManager; db = DatabaseManager(); db.load_gene_data('backend/backend_gene_data_Version2.json'); print('✓ Database initialized successfully')"

echo.
echo ✓ Setup complete!
echo.
echo To run the application:
echo   1. Start backend: venv\Scripts\activate && python backend\backend_app.py
echo   2. Open frontend: Open frontend\frontend_index_Version2.html in a web browser
echo.
pause