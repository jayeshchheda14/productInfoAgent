#!/usr/bin/env python3
"""ClamAV MCP Server - Provides virus scanning via Model Context Protocol"""
import subprocess
import tempfile
import os
import base64
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("clamav-scanner")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="scan_file",
            description="Scan a file for viruses using ClamAV",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_data": {
                        "type": "string",
                        "description": "Base64 encoded file data"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Original filename"
                    }
                },
                "required": ["file_data", "filename"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "scan_file":
        raise ValueError(f"Unknown tool: {name}")
    
    file_data = arguments.get("file_data")
    filename = arguments.get("filename", "unknown")
    
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(suffix=f"_{filename}", delete=False) as tmp:
            temp_file = tmp.name
            tmp.write(base64.b64decode(file_data))
        
        result = subprocess.run(
            ['clamscan', '--no-summary', temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        clean = result.returncode == 0
        virus_found = 'FOUND' in result.stdout
        
        scan_result = {
            "clean": clean and not virus_found,
            "virus_found": virus_found,
            "scan_output": result.stdout.strip(),
            "engine": "ClamAV",
            "method": "mcp_server"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(scan_result)
        )]
        
    except subprocess.TimeoutExpired:
        return [TextContent(
            type="text",
            text=json.dumps({"clean": False, "error": "Scan timeout"})
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"clean": False, "error": str(e)})
        )]
    finally:
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
