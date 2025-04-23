@echo off
REM ======= Secure IMS Frontend Startup Script =======

REM Load sensitive data from .env if available
IF EXIST .env (
    FOR /F "usebackq tokens=1,* delims==" %%A IN (".env") DO (
        SET "%%A=%%B"
    )
) ELSE (
    echo ❌ .env file not found!
    pause
    exit /b 1
)

REM Get HOST IP from ipconfig (fallback if not set in .env)
IF NOT DEFINED BACKEND_URL (
    for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4 Address"') do set HOST_IP=%%i
    set HOST_IP=%HOST_IP:~1%
    set BACKEND_URL=http://%HOST_IP%:8000
)

REM Inform the user
echo ✅ BACKEND_URL set to: %BACKEND_URL%

REM Optional: You may prompt user securely for password if needed

REM Run Docker container
echo 🚀 Starting frontend container...
docker run -it --rm ^
  --network host ^
  -v %cd%:/app ^
  -v /tmp/.X11-unix:/tmp/.X11-unix ^
  -e DISPLAY=host.docker.internal:0 ^
  -e BACKEND_URL=%BACKEND_URL% ^
    891377266155.dkr.ecr.ap-south-1.amazonaws.com/tg/inventory:latest \
    python app/entry_inventory.py
