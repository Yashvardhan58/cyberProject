@echo off
setlocal enabledelayedexpansion
title AI-Powered Adaptive UEBA Launcher

echo ==================================================================
echo  Starting AI-Powered Adaptive UEBA Local Dev Environment (Windows)
echo ==================================================================

:: Set paths cleanly
set "SCRIPTS_DIR=%~dp0"
cd /d "%SCRIPTS_DIR%.."
set "BACKEND_DIR=%CD%"
cd /d "%BACKEND_DIR%\..\frontend"
set "FRONTEND_DIR=%CD%"

echo [*] Backend Directory:  %BACKEND_DIR%
echo [*] Frontend Directory: %FRONTEND_DIR%
echo ------------------------------------------------------------------

:: 1. Backend Python & Venv Check
cd /d "%BACKEND_DIR%"
if not exist "venv\Scripts\activate.bat" (
    echo [*] Creating virtual environment (venv)...
    python -m venv venv
)

call "%BACKEND_DIR%\venv\Scripts\activate.bat"

python -c "import django" 2>nul
if %errorlevel% neq 0 (
    echo [*] Installing backend dependencies (one-time setup)...
    pip install -r requirements.txt
    pip install numpy pandas scikit-learn xgboost imbalanced-learn shap joblib
    python manage.py makemigrations
    python manage.py migrate
    python ml/data/seed_sqlite_db.py
)

:: 2. Frontend Node Check
cd /d "%FRONTEND_DIR%"
if not exist "node_modules" (
    echo [*] Installing frontend dependencies (one-time setup)...
    call npm.cmd install
)

:: 3. Launch Servers in Separate Windows
echo.
echo [+] Starting Backend Django API on http://localhost:8000 ...
cd /d "%BACKEND_DIR%"
start "UEBA Django API" cmd /k "call venv\Scripts\activate.bat && python manage.py runserver 8000"

echo [+] Starting Frontend React Dashboard on http://localhost:3000 / 5173 ...
cd /d "%FRONTEND_DIR%"
start "UEBA React UI" cmd /k "call npm.cmd run dev"

echo.
echo ==================================================================
echo  Both servers launched successfully!
echo  - Django API: http://localhost:8000/api/v1/
echo  - React UI:   http://localhost:5173/ or http://localhost:3000/
echo ==================================================================
echo  You can leave this window or press any key to close this launcher.
pause
