import base64
from google.cloud import vision
from google.adk.tools import ToolContext
try:
    from productInfoAgent.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def analyze_with_vision_api(tool_context: ToolContext) -> str:
    """Analyze product image using Google Vision API"""
    logger.info("[VISION_API] Starting analysis")
    # Get image data from state
    image_data = tool_context.state.get("image_data")
    
    if not image_data:
        return "❌ No image data provided for vision analysis"
    try:
        client = vision.ImageAnnotatorClient()
        image_bytes = base64.b64decode(image_data)
        image = vision.Image(content=image_bytes)
        
        # Perform multiple types of detection
        response = client.annotate_image({
            'image': image,
            'features': [
                {'type_': vision.Feature.Type.LABEL_DETECTION, 'max_results': 10},
                {'type_': vision.Feature.Type.TEXT_DETECTION, 'max_results': 10},
                {'type_': vision.Feature.Type.LOGO_DETECTION, 'max_results': 10},
                {'type_': vision.Feature.Type.OBJECT_LOCALIZATION, 'max_results': 10},
            ],
        })
        
        # Extract results
        labels = [{'description': label.description, 'score': label.score} 
                 for label in response.label_annotations]
        
        detected_text = response.full_text_annotation.text if response.full_text_annotation else ""
        
        logos = [{'description': logo.description, 'score': logo.score} 
                for logo in response.logo_annotations]
        
        objects = [{'name': obj.name, 'score': obj.score} 
                  for obj in response.localized_object_annotations]
        
        vision_result = {
            'labels': labels,
            'detected_text': detected_text,
            'logos': logos,
            'objects': objects,
            'analysis_complete': True
        }
        
        tool_context.state["vision_analysis_result"] = vision_result
        
        logger.info(f"[VISION_API] Success - labels: {len(labels)}, logos: {len(logos)}, text: {len(detected_text)} chars, objects: {len(objects)}")
        
        # Log all labels with scores
        logger.debug("[VISION_API] Labels detected:")
        for label in labels:
            logger.debug(f"  - {label['description']}: {label['score']:.2f}")
        
        # Log all logos
        if logos:
            logger.debug("[VISION_API] Logos detected:")
            for logo in logos:
                logger.debug(f"  - {logo['description']}: {logo['score']:.2f}")
        
        # Log detected text
        if detected_text:
            logger.debug(f"[VISION_API] Detected text:\n{detected_text[:500]}..." if len(detected_text) > 500 else f"[VISION_API] Detected text:\n{detected_text}")
        
        # Log objects
        if objects:
            logger.debug("[VISION_API] Objects detected:")
            for obj in objects:
                logger.debug(f"  - {obj['name']}: {obj['score']:.2f}")
        
        # Create summary
        label_names = [label['description'] for label in labels[:5]]
        logo_names = [logo['description'] for logo in logos]
        
        summary = f"✅ Vision Analysis Complete:\n"
        summary += f"- Labels detected: {', '.join(label_names)}\n"
        if logo_names:
            summary += f"- Logos found: {', '.join(logo_names)}\n"
        if detected_text:
            summary += f"- Text detected: {len(detected_text)} characters\n"
        summary += f"- Objects found: {len(objects)}"
        
        return summary
        
    except Exception as e:
        logger.error(f"[VISION_API] Error: {str(e)}", exc_info=True)
        error_result = {'error': str(e), 'analysis_complete': False}
        tool_context.state["vision_analysis_result"] = error_result
        return f"❌ Vision Analysis Error: {str(e)}"