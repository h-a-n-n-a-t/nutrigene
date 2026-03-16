@echo off
echo 🧬 NutriGene - Starting Application
echo ====================================

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start backend
echo Starting backend server...
start python backend\app.py

echo ✓ Backend started
echo.
echo 📝 Open frontend in your browser:
echo    File: %cd%\frontend\index.html
echo.
echo API running at: http://localhost:5000
echo.
pause