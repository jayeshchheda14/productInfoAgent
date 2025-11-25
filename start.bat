@echo off
echo Starting ClamAV MCP Server...
echo.

cd clamav-mcp
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start ClamAV container
    exit /b 1
)
cd ..

echo Waiting for ClamAV to initialize...
timeout /t 5 /nobreak >nul

docker ps | findstr clamav-mcp-server >nul
if %errorlevel% neq 0 (
    echo ERROR: ClamAV container not running
    exit /b 1
)

echo.
echo ========================================
echo ClamAV MCP Server: RUNNING
echo ========================================
echo.
echo Now run: adk run .\ProductInfoADKAgent\
echo.
