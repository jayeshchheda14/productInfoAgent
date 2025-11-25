import json
import google.generativeai as genai
import os
import asyncio
from google.adk.tools import ToolContext
from .... import config
try:
    from productInfoAgent.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def generate_marketing_content(tool_context: ToolContext) -> str:
    """Generate marketing content based on vision analysis using Gemini"""
    logger.info("[MARKETING] Starting content generation")
    try:
        # Check gatekeeper status first
        scoring_result = tool_context.state.get("scoring_result", {})
        if not scoring_result.get('gatekeeper_passed', False):
            rejection_reason = scoring_result.get('rejection_reason', 'Unknown')
            logger.warning(f"[MARKETING] Blocked - Gatekeeper rejected: {rejection_reason}")
            return f"🚫 Marketing content generation blocked - Image rejected by gatekeeper: {rejection_reason}"
        
        # Get vision analysis results
        vision_result = tool_context.state.get("vision_analysis_result", {})
        logger.debug(f"[MARKETING] Input - labels: {len(vision_result.get('labels', []))}, logos: {len(vision_result.get('logos', []))}")

        labels = vision_result.get('labels', [])
        detected_text = vision_result.get('detected_text', '')
        logos = vision_result.get('logos', [])

        # Extract label descriptions
        label_names = [label['description'] for label in labels[:5]]
        logo_names = [logo['description'] for logo in logos]

        # Create prompt for Gemini
        prompt = f"""Analyze this product package and create an ecommerce marketing message:

Detected Labels: {', '.join(label_names)}
Brand Logos: {', '.join(logo_names)}

Package Text:
{detected_text[:800]}

Create a compelling 2-3 sentence marketing message that:
1. Extracts the actual product name and key benefits from the package text
2. Uses natural, conversational ecommerce language
3. Highlights what customers care about (ingredients, quality, convenience, etc.)
4. Stays under 800 characters
5. Follows this example format: "[Brand] [Product] are made with [key ingredients from package] for [benefit]. [Additional selling point from package]. [Convenience factor]."

Example: "Tyson Lightly Breaded Chicken Breast Strips are made with 100% all-natural ingredients and real chicken breast with rib meat for a simple, flavorful meal. Enhanced with chicken broth for juiciness, offering convenient protein for families."

Provide output in JSON format:
{{
  "marketing_message": "your marketing message here",
  "brand": "extracted brand name",
  "product_description": "extracted product name",
  "category": "product category"
}}"""

        # Add delay to respect rate limits
        import time
        time.sleep(config.API_DELAY_SECONDS)
        
        # Configure Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Generate content
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Extract JSON from response
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()

        # Parse JSON response
        marketing_content = json.loads(response_text)
        marketing_content['confidence'] = scoring_result.get('score', 0) / 50.0
        marketing_content['generated_by'] = "Gemini AI Marketing Agent"

        tool_context.state["marketing_result"] = marketing_content
        
        logger.info(f"[MARKETING] Success - brand: {marketing_content.get('brand', 'N/A')}, product: {marketing_content.get('product_description', 'N/A')}")
        logger.debug(f"[MARKETING] Message: {marketing_content.get('marketing_message', '')[:100]}...")

        return f"✅ Marketing content generated for {marketing_content.get('brand', 'Product')} {marketing_content.get('product_description', '')}\n\nMarketing Message: {marketing_content.get('marketing_message', '')}"

    except Exception as e:
        # Fallback to template-based generation if API fails
        label_names = [label['description'] for label in vision_result.get('labels', [])[:5]]
        logo_names = [logo['description'] for logo in vision_result.get('logos', [])]
        detected_text = vision_result.get('detected_text', '')

        brand = logo_names[0] if logo_names else (detected_text.split()[0] if detected_text else "Premium")
        product = label_names[0] if label_names else "Product"

        marketing_content = {
            'marketing_message': f"{brand} {product} delivers exceptional quality with carefully selected ingredients for superior taste and convenience. Perfect for discerning customers seeking reliable, premium products.",
            'brand': brand,
            'product_description': f"{brand} {product}",
            'category': product,
            'confidence': scoring_result.get('score', 0) / 50.0,
            'generated_by': 'Template Marketing Agent (API Fallback)',
            'note': f'API Error: {str(e)}'
        }
        tool_context.state["marketing_result"] = marketing_content
        return f"⚠️ Marketing content generated using fallback template for {brand} {product}\n\nMarketing Message: {marketing_content['marketing_message']}"