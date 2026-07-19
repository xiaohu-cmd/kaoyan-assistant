@echo off
chcp 65001 >nul
title 考研助手

cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ first.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Create venv if not exists
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv.
        pause
        exit /b 1
    )
)

:: Activate venv
call venv\Scripts\activate.bat

:: Install dependencies
echo [INFO] Checking dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: Create data directory
if not exist "data\" mkdir data
if not exist "uploads\" mkdir uploads

echo.
echo ============================================
echo   考研助手 - 启动中...
echo   浏览器打开: http://localhost:8000
echo   按 Ctrl+C 停止服务器
echo ============================================
echo.

:: Open browser after short delay
start "" http://localhost:8000

:: Start server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
