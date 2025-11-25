import os
import base64
from google.cloud import storage
from google.adk.tools import ToolContext
from .... import config
try:
    from productInfoAgent.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def upload_to_gcp(tool_context: ToolContext) -> str:
    """Upload image to GCP bucket for audit"""
    logger.info("[GCP_UPLOAD] Starting upload to GCP for audit")
    # Get image data from state
    image_data = tool_context.state.get("image_data")
    filename = tool_context.state.get("filename", "unknown.jpg")
    logger.debug(f"[GCP_UPLOAD] Uploading file: {filename}")
    
    if not image_data:
        return "❌ No image data provided for GCP upload"
    try:
        bucket_name = config.GCP_BUCKET_NAME
        credentials_path = config.GOOGLE_APPLICATION_CREDENTIALS
        
        if not bucket_name:
            logger.error("[GCP_UPLOAD] GCP_BUCKET_NAME not configured")
            error_result = {"success": False, "error": "GCP_BUCKET_NAME not configured"}
            tool_context.state["gcp_upload_result"] = error_result
            return "❌ ERROR: GCP_BUCKET_NAME not configured in .env file"
        
        if not credentials_path or not os.path.exists(credentials_path):
            logger.error(f"[GCP_UPLOAD] Credentials not found: {credentials_path}")
            error_result = {"success": False, "error": "GCP credentials not configured"}
            tool_context.state["gcp_upload_result"] = error_result
            return f"❌ ERROR: GOOGLE_APPLICATION_CREDENTIALS not found: {credentials_path}"
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"audit/{filename}")
        
        image_bytes = base64.b64decode(image_data)
        blob.upload_from_string(image_bytes, content_type='image/jpeg')
        
        upload_result = {
            "success": True,
            "gcp_url": f"gs://{bucket_name}/audit/{filename}",
            "message": "Image uploaded to GCP for audit"
        }
        
        tool_context.state["gcp_upload_result"] = upload_result
        logger.info(f"[GCP_UPLOAD] Success - uploaded to gs://{bucket_name}/audit/{filename}")
        return f"✅ Successfully uploaded to GCP: gs://{bucket_name}/audit/{filename}"
        
    except Exception as e:
        logger.error(f"[GCP_UPLOAD] Error: {str(e)}", exc_info=True)
        error_result = {"success": False, "error": str(e)}
        tool_context.state["gcp_upload_result"] = error_result
        return f"❌ GCP Upload Error: {str(e)}"