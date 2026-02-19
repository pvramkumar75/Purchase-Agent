@echo off
title OmniMind — Stopping...
echo.
echo  Stopping OmniMind containers...
echo.

cd /d "%~dp0"
docker-compose down

echo.
echo  ✅ OmniMind stopped successfully!
echo  Your data is safely saved in the /memory folder.
echo.
pause
