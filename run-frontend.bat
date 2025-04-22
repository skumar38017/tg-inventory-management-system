@echo off
REM Set host IP for BACKEND_URL
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4 Address"') do set HOST_IP=%%i
set HOST_IP=%HOST_IP:~1%

REM Optional: You may also hardcode this if needed:
REM set HOST_IP=192.168.1.100

REM Build Docker image
docker build -t ims-frontend -f frontend/Dockerfile .

REM Run Docker container
docker run -it --rm ^
  --network host ^
  -v %cd%:/app ^
  -v /tmp/.X11-unix:/tmp/.X11-unix ^
  -e DISPLAY=host.docker.internal:0 ^
  -e BACKEND_URL=http://%HOST_IP%:8000 ^
  ims-frontend python app/entry_inventory.py
