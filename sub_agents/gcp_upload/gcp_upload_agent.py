from google.adk.agents import Agent
from ... import config
from .tools.gcp_upload_tool import upload_to_gcp

gcp_upload_agent = Agent(
    name="gcp_upload_agent",
    model=config.GENAI_MODEL,
    description="Uploads product images to Google Cloud Storage for audit trails",
    instruction="You are responsible for uploading images to GCP storage for audit purposes. Use the upload_to_gcp tool to store the image securely.",
    output_key="gcp_upload",
    tools=[upload_to_gcp],
)