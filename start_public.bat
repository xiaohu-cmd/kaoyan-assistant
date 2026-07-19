@echo off
echo Starting KaoYan Assistant...
echo.
echo 1. Starting local server...
start "考研助手-服务器" cmd /c "cd /d %~dp0 && venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

echo 2. Starting Cloudflare tunnel (external access)...
start "考研助手-外网隧道" cmd /c "cd /d %~dp0 && ..\cloudflared.exe tunnel --url http://localhost:8000"

timeout /t 8 /nobreak >nul
echo.
echo ============================================
echo  Server running at: http://localhost:8000
echo  External tunnel started
echo  Check tunnel window for public URL
echo ============================================
echo.
echo DO NOT close the tunnel window!
pause
