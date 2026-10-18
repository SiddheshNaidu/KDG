
@echo off
setlocal enabledelayedexpansion

:: Switch to the repository root directory regardless of how the script is invoked
set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"
cd /d "%ROOT_DIR%"
title KDG v2 Launcher

echo ====================================================================
echo               KDG v2 - Omni-Stack Local Orchestrator
echo ====================================================================

:: 1. Locate Python environment
set "PY_BIN="
if exist "%ROOT_DIR%\.venv\Scripts\python.exe" (
    set "PY_BIN=%ROOT_DIR%\.venv\Scripts\python.exe"
    set "ACTIVATE_BAT=%ROOT_DIR%\.venv\Scripts\activate.bat"
) else (
    where python >nul 2>nul
    if !ERRORLEVEL! equ 0 (
        set "PY_BIN=python"
    ) else (
        echo [ERROR] Python environment not found!
        echo Please ensure Python or .venv is installed.
        pause
        exit /b 1
    )
)

:: 2. Verify Node / npm
where npm >nul 2>nul
if !ERRORLEVEL! neq 0 (
    echo [ERROR] npm is not installed or not in PATH!
    pause
    exit /b 1
)

:: 3. Check frontend dependencies
if not exist "%ROOT_DIR%\frontend\node_modules\" (
    echo [INFO] frontend/node_modules not found. Running npm install...
    cd /d "%ROOT_DIR%\frontend" && call npm install && cd /d "%ROOT_DIR%"
)

echo [1/2] Starting Backend service on http://127.0.0.1:8000 ...
if defined ACTIVATE_BAT (
    start "KDG Backend (Port 8000)" cmd /k "cd /d "%ROOT_DIR%" && call "%ACTIVATE_BAT%" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
) else (
    start "KDG Backend (Port 8000)" cmd /k "cd /d "%ROOT_DIR%" && "%PY_BIN%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
)

echo [2/2] Starting Frontend Vite dev server on http://localhost:5173 ...
start "KDG Frontend (Vite)" cmd /k "cd /d "%ROOT_DIR%\frontend" && npm run dev"

echo.
echo ====================================================================
echo   All services have been initiated in dedicated consoles:
echo     - Backend API:  http://127.0.0.1:8000 (Docs: http://127.0.0.1:8000/docs)
echo     - Frontend App: http://localhost:5173
echo ====================================================================
echo.
echo Press ANY KEY in this window to stop both services and exit...
pause >nul

echo [INFO] Stopping KDG services...
taskkill /FI "WINDOWTITLE eq KDG Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq KDG Frontend*" /T /F >nul 2>&1
echo [INFO] Services stopped.
timeout /t 2 >nul
exit /b 0
