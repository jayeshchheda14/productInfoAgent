"""MCP Client for ClamAV virus scanning"""
import asyncio
import base64
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def scan_file_via_mcp(file_data: str, filename: str) -> dict:
    """Scan file using ClamAV MCP server"""
    server_params = StdioServerParameters(
        command="docker",
        args=["exec", "-i", "clamav-mcp-server", "python", "/app/clamav_mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "scan_file",
                arguments={
                    "file_data": file_data,
                    "filename": filename
                }
            )
            
            return eval(result.content[0].text)

# Example usage
async def main():
    with open("test.jpg", "rb") as f:
        file_data = base64.b64encode(f.read()).decode()
    
    result = await scan_file_via_mcp(file_data, "test.jpg")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
