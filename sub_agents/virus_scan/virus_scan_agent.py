"""Virus Scan Agent - Provides ClamAV scanning via MCP or local tool"""
import os
import subprocess
from google.adk.agents import Agent
from ...config import GENAI_MODEL

def check_clamav_server_running():
    """Check if ClamAV Docker container is running"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=clamav-mcp-server', '--format', '{{.Names}}'],
            capture_output=True, text=True, timeout=5
        )
        return 'clamav-mcp-server' in result.stdout
    except:
        return False

USE_MCP = os.getenv('USE_MCP_CLAMAV', 'false').lower() == 'true'

if USE_MCP and check_clamav_server_running():
    from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters
    
    tools = [
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='docker',
                    args=['exec', '-i', 'clamav-mcp-server', 'python', '/app/clamav_mcp_server.py']
                ),
                timeout=30
            )
        )
    ]
else:
    from .tools.virus_scan_tool import scan_for_virus
    tools = [scan_for_virus]
    
    if USE_MCP:
        print("⚠️  WARNING: USE_MCP_CLAMAV=true but ClamAV server not running. Using local tool.")
        print("    Start ClamAV with: docker run -d --name clamav-mcp-server ...")

virus_scan_agent = Agent(
    name="virus_scan_agent",
    model=GENAI_MODEL,
    description="Scans files for viruses using ClamAV",
    instruction="Scan the file using the available virus scanning tool. Use image_data and filename from session state.",
    tools=tools
)
