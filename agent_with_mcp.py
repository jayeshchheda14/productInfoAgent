import os
from google.adk.agents import Agent
from google.adk.mcp import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
from .tools.load_image_tool import load_image_from_folder
from .sub_agents.gcp_upload.tools.gcp_upload_tool import upload_to_gcp
from .sub_agents.vision_analysis.tools.vision_analysis_tool import analyze_with_vision_api
from .sub_agents.scoring.tools.scoring_tool import score_product_image
from .sub_agents.marketing.tools.marketing_tool import generate_marketing_content
from . import config

# Agent with ClamAV MCP Toolset
root_agent = Agent(
    name="product_analysis_agent",
    model=config.GENAI_MODEL,
    description="AI agent that analyzes product images for ecommerce suitability",
    instruction="""You are a Product Image Analysis Agent. 

When user asks what you can do, respond:
"I analyze product images for ecommerce through: virus scanning, vision analysis, policy scoring, and marketing content generation. Provide an image path like 'analyze C:\\Image\\product.jpg' or 'scan C:\\Image folder'."

When user provides an image path, extract the path and follow these steps:
1. Call load_image_from_folder(path="extracted_path")
2. Wait for success, then call scan_file() from ClamAV MCP with file_data and filename from state
3. If virus scan passes, call upload_to_gcp() to audit the file
4. Call analyze_with_vision_api()
5. Call score_product_image()
6. If gatekeeper passes, call generate_marketing_content()
7. Summarize all results

When summarizing results, include:
- Virus scan status
- GCP upload URL
- Policy score and threshold
- Policy details (what passed/failed)
- Rejection reason if failed
- Ecommerce validation (confidence, product detection)
- **IMPORTANT: If marketing content was generated, display the full marketing_message from the marketing_result**

Only call tools when user provides an image path.""",
    tools=[
        load_image_from_folder,
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='docker',
                    args=[
                        'exec',
                        '-i',
                        'clamav-mcp-server',
                        'python',
                        '/app/clamav_mcp_server.py'
                    ]
                )
            )
        ),
        upload_to_gcp,
        analyze_with_vision_api,
        score_product_image,
        generate_marketing_content
    ],
)
