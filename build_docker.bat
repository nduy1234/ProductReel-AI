@echo off
REM Build script for GAIA Green Agent Docker image (Windows)

echo Building GAIA Green Agent Docker image...

docker build -t gaia-green-agent:latest .

if %ERRORLEVEL% EQU 0 (
    echo Build complete!
    echo.
    echo To run the Green Agent:
    echo   docker run -v %CD%\results:/app/results gaia-green-agent:latest
    echo.
    echo To run the Purple Agent server:
    echo   docker run -p 8000:8000 gaia-green-agent:latest python -m purple_agent.server
    echo.
    echo Or use docker-compose:
    echo   docker-compose up
) else (
    echo Build failed!
    exit /b 1
)
