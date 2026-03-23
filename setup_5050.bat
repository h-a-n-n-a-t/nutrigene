@echo off
echo NutriGene Setup Script (Port 5050)
echo ==================================

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 goto :error

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 goto :error

REM Install dependencies
echo Installing dependencies...
pip install -r backend\backend_requirements.txt
if errorlevel 1 goto :error

echo.
echo Setup complete.
echo.
echo To run the application on port 5050:
echo   1. Run: run_5050.bat
echo   2. Open: http://localhost:5050
echo.
pause
exit /b 0

:error
echo.
echo Setup failed. Check the error messages above.
pause
exit /b 1
