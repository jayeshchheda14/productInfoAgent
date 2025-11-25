@echo off
echo Stopping ClamAV MCP Server...
cd clamav-mcp
docker-compose down
cd ..
echo Done.
