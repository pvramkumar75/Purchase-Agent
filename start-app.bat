@echo off
title OmniMind — Starting...
echo.
echo  ======================================
echo     OmniMind — Universal AI Assistant
echo  ======================================
echo.
echo  Starting Docker containers...
echo.

cd /d "%~dp0"
docker-compose up --build -d

echo.
echo  ✅ OmniMind is starting up!
echo.
echo  Frontend:  http://localhost:3000
echo  Backend:   http://localhost:8000
echo.
echo  Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo  ─────────────────────────────────────
echo  To stop OmniMind, run: stop-app.bat
echo  Or press Ctrl+C here and run:
echo    docker-compose down
echo  ─────────────────────────────────────
echo.
echo  Showing live logs (Ctrl+C to exit logs only):
docker-compose logs -f
