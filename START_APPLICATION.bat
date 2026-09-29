@echo off
setlocal
title AI-Powered Adaptive UEBA Launcher

set "PROJECT_DIR=%~dp0"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"

echo ==================================================================
echo   AI-Powered Adaptive UEBA - Starting Application
echo ==================================================================
echo.
echo [*] Location: %PROJECT_DIR%
echo.

:: 1. Launch Django Backend Server in a new window
echo [1/2] Launching Django Backend Server (Port 8000)...
start "UEBA Backend (Django)" /D "%BACKEND_DIR%" cmd /k "venv\Scripts\activate.bat && python manage.py runserver 8000"

:: 2. Launch Vite React Frontend Server in a new window
echo [2/2] Launching React Frontend Server (Port 3000)...
start "UEBA Frontend (React)" /D "%FRONTEND_DIR%" cmd /k "npm.cmd run dev"

echo.
echo ==================================================================
echo   Servers are starting up!
echo   - Backend API: http://localhost:8000/api/v1/
echo   - Frontend UI: http://localhost:3000/
echo ==================================================================
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start http://localhost:3000/

