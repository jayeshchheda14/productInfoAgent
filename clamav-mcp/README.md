# ClamAV MCP Server

Docker-based ClamAV virus scanner exposed via Model Context Protocol (MCP).

## Quick Start

### 1. Start ClamAV Server
**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### 2. Run Agent with ADK
```bash
adk run .\ProductInfoADKAgent\
```

### 3. Stop ClamAV Server
**Windows:**
```bash
stop.bat
```

**Linux/Mac:**
```bash
chmod +x stop.sh
./stop.sh
```

## Manual Setup

### 1. Build and Start Container
```bash
cd clamav-mcp
docker-compose up -d --build
```

### 2. Verify Container
```bash
docker ps | grep clamav-mcp
docker logs clamav-mcp-server
```

### 3. Test ClamAV
```bash
docker exec clamav-mcp-server clamscan --version
```

### 4. Start Agent
```bash
cd ..
python interactive_runner.py
```

## Usage

### Update Virus Definitions
```bash
docker exec clamav-mcp-server freshclam
```

### Stop/Start Container
```bash
docker-compose stop
docker-compose start
```

### Remove Container
```bash
docker-compose down
```

## Integration with Virus Scan Tool

Update `virus_scan_tool.py` to use MCP client:

```python
from clamav_mcp.mcp_client import scan_file_via_mcp

async def scan_for_virus(tool_context: ToolContext) -> str:
    image_data = tool_context.state.get("image_data")
    filename = tool_context.state.get("filename", "unknown.jpg")
    
    # Use MCP server
    scan_result = await scan_file_via_mcp(image_data, filename)
    tool_context.state["virus_scan_result"] = scan_result
    
    if scan_result.get("clean"):
        return f"✅ Virus scan PASSED via MCP"
    else:
        return f"🚫 Virus scan FAILED: {scan_result.get('error', 'Virus detected')}"
```

## Troubleshooting

**Container won't start:**
```bash
docker logs clamav-mcp-server
```

**Virus definitions outdated:**
```bash
docker exec clamav-mcp-server freshclam
docker-compose restart
```

**Port conflict:**
Edit `docker-compose.yml` and change port mapping.
