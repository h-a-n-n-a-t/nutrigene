@echo off
echo NutriGene - Starting Application on Port 5050
echo ============================================

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 goto :error

REM Start backend on port 5050
echo Starting backend server on http://localhost:5050 ...
set PORT=5050
python backend\backend_app.py
goto :end

:error
echo.
echo Failed to start application. Make sure setup_5050.bat completed successfully.

:end
pause
