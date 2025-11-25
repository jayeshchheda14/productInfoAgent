import json
import base64
from PIL import Image
import io
from google.adk.tools import ToolContext
try:
    from productInfoAgent.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def score_product_image(tool_context: ToolContext) -> str:
    """Score product image against policy rules and ecommerce eligibility"""
    logger.info("[SCORING] Starting policy scoring")
    # Get image data from state
    image_data = tool_context.state.get("image_data")
    
    if not image_data:
        return "❌ No image data provided for scoring"
    try:
        # Load policy from file
        import os
        from pathlib import Path
        # Get policy.json from project root
        policy_path = Path(__file__).parent.parent.parent.parent / 'policy.json'
        with open(policy_path, 'r') as f:
            policy = json.load(f)
        
        # Get vision analysis results
        vision_result = tool_context.state.get("vision_analysis_result", {})
        
        # Log vision data being used for scoring
        labels = vision_result.get('labels', [])
        logos = vision_result.get('logos', [])
        text = vision_result.get('detected_text', '')
        logger.debug(f"[SCORING] Using vision data - labels: {len(labels)}, logos: {len(logos)}, text length: {len(text)}")
        if labels:
            logger.debug(f"[SCORING] Top 3 labels: {[l['description'] for l in labels[:3]]}")
        if logos:
            logger.debug(f"[SCORING] Logos: {[l['description'] for l in logos]}")
        
        # Basic image scoring
        policy_score = _score_image_policy(image_data, policy)
        
        # Ecommerce validation
        ecommerce_validation = _validate_ecommerce_eligibility(vision_result, policy)
        
        # Gatekeeper decision logic
        gatekeeper_checks = {
            'policy_score_passed': policy_score.get('passed', False),
            'ecommerce_eligible': ecommerce_validation.get('is_sellable', False),
            'min_confidence_met': ecommerce_validation.get('confidence', 0) >= policy['ecommerce_policy']['validation_rules']['min_product_confidence']
        }
        
        gatekeeper_passed = all(gatekeeper_checks.values())
        
        # Determine rejection reason
        rejection_reason = None
        if not gatekeeper_passed:
            if not gatekeeper_checks['policy_score_passed']:
                rejection_reason = f"Policy score too low: {policy_score.get('score', 0)}/{policy['image_policy']['scoring']['threshold']}"
            elif not gatekeeper_checks['ecommerce_eligible']:
                rejection_reason = f"Not suitable for ecommerce: {ecommerce_validation.get('reason', 'Unknown')}"
            elif not gatekeeper_checks['min_confidence_met']:
                rejection_reason = f"Confidence too low: {ecommerce_validation.get('confidence', 0):.2f}"
        
        scoring_result = {
            'score': policy_score.get('score', 0),
            'policy_details': policy_score.get('details', []),
            'ecommerce_validation': ecommerce_validation,
            'gatekeeper_checks': gatekeeper_checks,
            'gatekeeper_passed': gatekeeper_passed,
            'rejection_reason': rejection_reason,
            'can_proceed_to_marketing': gatekeeper_passed
        }
        
        tool_context.state["scoring_result"] = scoring_result
        
        logger.info(f"[SCORING] Result - score: {scoring_result['score']}/50, gatekeeper: {gatekeeper_passed}")
        logger.debug(f"[SCORING] Checks: {gatekeeper_checks}")
        logger.debug(f"[SCORING] Ecommerce: {ecommerce_validation}")
        
        if gatekeeper_passed:
            return f"✅ Gatekeeper APPROVED - Score: {scoring_result['score']}/50, Ecommerce eligible"
        else:
            details_str = "\n".join([f"  - {detail}" for detail in policy_score.get('details', [])])
            return f"""🚫 Gatekeeper REJECTED - {rejection_reason}

Policy Score Breakdown:
{details_str}

Ecommerce Validation:
  - Product detected: {ecommerce_validation.get('is_sellable', False)}
  - Confidence: {ecommerce_validation.get('confidence', 0):.2f}
  - Reason: {ecommerce_validation.get('reason', 'Unknown')}
  - Has brand logos: {ecommerce_validation.get('has_brand_logos', False)}
  - Has product text: {ecommerce_validation.get('has_product_text', False)}

Required threshold: {policy_score.get('threshold', 45)}/50"""
        
    except Exception as e:
        error_result = {
            'score': 0,
            'gatekeeper_passed': False,
            'rejection_reason': f"Scoring error: {str(e)}",
            'error': str(e)
        }
        tool_context.state["scoring_result"] = error_result
        return f"❌ Scoring Error: {str(e)}"

def _score_image_policy(image_data: str, policy: dict) -> dict:
    """Score image against policy rules"""
    try:
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        width, height = image.size
        mode = image.mode
        
        # Log image properties
        logger.info(f"[SCORING] Image properties - Width: {width}px, Height: {height}px, Mode: {mode}")
        
        score = 0
        details = []
        
        # Score calculation with logging
        min_width = policy['image_policy']['technical_requirements']['min_width']
        min_height = policy['image_policy']['technical_requirements']['min_height']
        
        logger.debug(f"[SCORING] Policy requirements - min_width: {min_width}px, min_height: {min_height}px")
        
        if width >= min_width:
            score += 10
            details.append(f"Width requirement met: {width}px >= {min_width}px")
            logger.debug(f"[SCORING] +10 points: Width {width}px >= {min_width}px (Total: {score})")
        else:
            details.append(f"Width requirement NOT met: {width}px < {min_width}px")
            logger.debug(f"[SCORING] +0 points: Width {width}px < {min_width}px (Total: {score})")
        
        if height >= min_height:
            score += 10
            details.append(f"Height requirement met: {height}px >= {min_height}px")
            logger.debug(f"[SCORING] +10 points: Height {height}px >= {min_height}px (Total: {score})")
        else:
            details.append(f"Height requirement NOT met: {height}px < {min_height}px")
            logger.debug(f"[SCORING] +0 points: Height {height}px < {min_height}px (Total: {score})")
        
        if width > 500 and height > 500:
            score += 15
            details.append(f"High resolution image detected: {width}x{height}")
            logger.debug(f"[SCORING] +15 points: High resolution {width}x{height} > 500x500 (Total: {score})")
        else:
            logger.debug(f"[SCORING] +0 points: Not high resolution {width}x{height} (Total: {score})")
        
        if mode in ['RGB', 'RGBA']:
            score += 10
            details.append(f"Good color format: {mode}")
            logger.debug(f"[SCORING] +10 points: Good color mode {mode} (Total: {score})")
        else:
            details.append(f"Color format: {mode}")
            logger.debug(f"[SCORING] +0 points: Color mode {mode} not RGB/RGBA (Total: {score})")
        
        if width >= 800 or height >= 600:
            score += 5
            details.append(f"Professional image dimensions: {width}x{height}")
            logger.debug(f"[SCORING] +5 points: Professional dimensions {width}x{height} (Total: {score})")
        else:
            logger.debug(f"[SCORING] +0 points: Not professional dimensions {width}x{height} (Total: {score})")
        
        logger.info(f"[SCORING] Final score calculation: {score}/50 (capped at 50)")
        
        final_score = min(score, 50)
        threshold = policy['image_policy']['scoring']['threshold']
        passed = final_score >= threshold
        
        logger.info(f"[SCORING] Policy result - Score: {final_score}/{threshold}, Passed: {passed}")
        
        return {
            "score": final_score,
            "threshold": threshold,
            "passed": passed,
            "details": details
        }
    except Exception as e:
        return {"score": 0, "passed": False, "error": str(e)}

def _validate_ecommerce_eligibility(vision_result: dict, policy: dict) -> dict:
    """Validate if image is suitable for ecommerce"""
    labels = vision_result.get('labels', [])
    text = vision_result.get('detected_text', '')
    logos = vision_result.get('logos', [])
    
    # Simple classification based on labels
    product_keywords = ['product', 'bottle', 'can', 'package', 'box', 'container', 'food', 'drink', 'beverage']
    
    confidence = 0.0
    is_sellable = False
    reason = "No product detected"
    
    for label in labels:
        if any(keyword in label['description'].lower() for keyword in product_keywords):
            confidence = max(confidence, label['score'])
            is_sellable = True
            reason = f"Product detected: {label['description']}"
            break
    
    validation_rules = policy['ecommerce_policy']['validation_rules']
    meets_requirements = confidence >= validation_rules['min_product_confidence']
    
    return {
        'is_sellable': is_sellable and meets_requirements,
        'confidence': confidence,
        'reason': reason,
        'has_brand_logos': len(logos) > 0,
        'has_product_text': bool(text),
        'meets_policy_requirements': meets_requirements
    }