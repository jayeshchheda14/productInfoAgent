from google.adk.agents import Agent
from ... import config
from .tools.scoring_tool import score_product_image

scoring_agent = Agent(
    name="scoring_agent",
    model=config.GENAI_MODEL,
    description="Scores product images against policy rules and validates ecommerce eligibility",
    instruction="""Immediately invoke the 'score_product_image' tool now. Do not explain, just call the tool.""",
    output_key="scoring",
    tools=[score_product_image],
)