from google.adk.agents import Agent
from ... import config
from .tools.vision_analysis_tool import analyze_with_vision_api

vision_analysis_agent = Agent(
    name="vision_analysis_agent",
    model=config.GENAI_MODEL,
    description="Analyzes product images using Google Vision API for product recognition and brand detection",
    instruction="""Immediately invoke the 'analyze_with_vision_api' tool now. Do not explain, just call the tool.""",
    output_key="vision_analysis",
    tools=[analyze_with_vision_api],
)