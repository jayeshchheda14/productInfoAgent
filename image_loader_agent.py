from google.adk.agents import Agent
from . import config
from .tools.load_image_tool import load_image_from_folder

image_loader_agent = Agent(
    name="image_loader_agent",
    model=config.GENAI_MODEL,
    description="Loads product images from disk folder",
    instruction="""When user provides an image path or folder, immediately invoke 'load_image_from_folder' tool with the path parameter. Examples:
- User: "analyze C:\\Image\\product.jpg" -> call load_image_from_folder(path="C:\\Image\\product.jpg")
- User: "scan image from C:\\Image" -> call load_image_from_folder(path="C:\\Image")
- User: "analyze image" -> call load_image_from_folder(path="C:\\Image")""",
    output_key="image_loader",
    tools=[load_image_from_folder],
)
