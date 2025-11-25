from google.adk.agents import Agent
from ... import config
from .tools.marketing_tool import generate_marketing_content

marketing_agent = Agent(
    name="marketing_agent",
    model=config.GENAI_MODEL,
    description="Generates marketing content and product descriptions based on image analysis",
    instruction="""Immediately invoke the 'generate_marketing_content' tool now. Do not explain, just call the tool.""",
    output_key="marketing",
    tools=[generate_marketing_content],
)