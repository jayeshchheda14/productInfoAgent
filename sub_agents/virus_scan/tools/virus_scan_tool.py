from google.adk.tools import ToolContext
try:
    from productInfoAgent.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def scan_for_virus(tool_context: ToolContext) -> str:
    """Mock virus scanner for development (use MCP for real scanning)"""
    logger.info("[VIRUS_SCAN] Starting mock scan")
    filename = tool_context.state.get("filename", "unknown.jpg")
    logger.debug(f"[VIRUS_SCAN] Mock scanning file: {filename}")
    
    scan_result = {
        "clean": True,
        "virus_found": False,
        "scan_time": "0.001s",
        "engine_version": "Mock Scanner v1.0",
        "method": "mock",
        "note": "Enable USE_MCP_CLAMAV=true for real ClamAV scanning"
    }
    
    tool_context.state["virus_scan_result"] = scan_result
    logger.info(f"[VIRUS_SCAN] Mock result - clean: True")
    
    return f"✅ Virus scan PASSED: mock method (Enable USE_MCP_CLAMAV=true for real scanning)"
