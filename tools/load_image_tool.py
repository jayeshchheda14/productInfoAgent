import base64
from pathlib import Path
from google.adk.tools import ToolContext
try:
    from productInfoAgent.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def load_image_from_folder(tool_context: ToolContext, path: str = "C:\\Image") -> str:
    """Load image from file path or folder path"""
    try:
        logger.info(f"[LOAD_IMAGE] Starting - path: {path}")
    except:
        pass
    try:
        target_path = Path(path)
        try:
            logger.debug(f"[LOAD_IMAGE] Resolved path: {target_path}")
        except:
            pass
        
        # If it's a file, load it directly
        if target_path.is_file():
            image_file = target_path
        # If it's a folder, load first image
        elif target_path.is_dir():
            image_files = list(target_path.glob("*.jpg")) + list(target_path.glob("*.png"))
            if not image_files:
                return f"❌ No images found in {path}"
            image_file = image_files[0]
        else:
            return f"❌ Path not found: {path}"
        
        with open(image_file, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        # Store in session state
        tool_context.state["image_data"] = image_data
        tool_context.state["filename"] = image_file.name
        
        logger.info(f"[LOAD_IMAGE] Success - file: {image_file.name}, size: {len(image_data)} bytes")
        return f"✅ Loaded image: {image_file.name} from {path}"
        
    except Exception as e:
        logger.error(f"[LOAD_IMAGE] Error: {str(e)}", exc_info=True)
        return f"❌ Error loading image: {str(e)}"
