#!/bin/bash
set -e

echo "Starting ClamAV MCP Server..."
echo ""

cd clamav-mcp
docker-compose up -d
cd ..

echo "Waiting for ClamAV to initialize..."
sleep 5

if ! docker ps | grep -q clamav-mcp-server; then
    echo "ERROR: ClamAV container not running"
    exit 1
fi

echo ""
echo "========================================"
echo "ClamAV MCP Server: RUNNING"
echo "========================================"
echo ""
echo "Now run: adk run ./ProductInfoADKAgent/"
echo ""
