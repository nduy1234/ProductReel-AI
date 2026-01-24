@echo off
REM Build script for GAIA Green Agent Docker image (Windows)

echo Building GAIA Green Agent Docker image...

docker build -t gaia-green-agents:latest .

if %ERRORLEVEL% EQU 0 (
    echo Build complete!
    echo.
    echo To run the Green Agent:
    echo   docker run -v %CD%\results:/app/results gaia-green-agents:latest
    echo.
    echo To run the Purple Agent server:
    echo   docker build -f Dockerfile.purple -t gaia-purple-agent:latest .
    echo   docker run -p 8000:8000 gaia-purple-agent:latest
    echo.
    echo Or use docker-compose:
    echo   docker-compose up
) else (
    echo Build failed!
    exit /b 1
)
