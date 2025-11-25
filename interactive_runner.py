#!/usr/bin/env python3
"""
Interactive ADK runner - waits for user input
"""
import asyncio
import base64
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

from google.adk.agents import InvocationContext, RunConfig
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from agent import root_agent as product_agent

async def main():
    """Interactive main function"""
    print("=" * 60)
    print("🤖 Product Image Analysis Agent")
    print("=" * 60)
    print("\nI analyze product images for ecommerce suitability.")
    print("Pipeline: Virus Scan → GCP Upload → Vision Analysis → Scoring → Marketing")
    print("\nAvailable images in C:\\Image\\:")
    
    image_dir = Path("C:/Image")
    if not image_dir.exists():
        print("❌ Image directory C:/Image not found")
        return
    
    image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
    if not image_files:
        print("❌ No image files found in C:/Image")
        return
    
    for idx, img in enumerate(image_files, 1):
        print(f"  {idx}. {img.name}")
    
    print("\n" + "=" * 60)
    
    # Create session
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="product_info_agent",
        user_id="test_user"
    )
    
    while True:
        print("\n💬 Enter command:")
        print("  - Type image number (e.g., '1') to analyze")
        print("  - Type 'quit' to exit")
        
        user_input = input("\n> ").strip().lower()
        
        if user_input == 'quit':
            print("👋 Goodbye!")
            break
        
        try:
            img_idx = int(user_input) - 1
            if 0 <= img_idx < len(image_files):
                image_file = image_files[img_idx]
                print(f"\n🖼️  Analyzing: {image_file.name}")
                print("=" * 60)
                
                with open(image_file, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode()
                
                # Inject image data
                session.state["image_data"] = image_data
                session.state["filename"] = image_file.name
                
                # Create user content
                user_content = Content(
                    role="user",
                    parts=[Part(text=f"Analyze {image_file.name}")]
                )
                
                # Create context
                invocation_context = InvocationContext(
                    session_service=session_service,
                    session=session,
                    invocation_id=f"inv_{img_idx}",
                    agent=product_agent,
                    user_content=user_content,
                    run_config=RunConfig()
                )
                
                # Run agent
                async for chunk in product_agent.run_async(invocation_context):
                    print(chunk, end="", flush=True)
                
                print("\n" + "=" * 60)
                print("✅ Analysis complete!")
                
                # Show results
                print(f"\n📊 Results:")
                print(f"  Virus Scan: {session.state.get('virus_scan_result', {}).get('clean', False)}")
                gcp_result = session.state.get('gcp_upload_result', {})
                print(f"  GCP Upload: {gcp_result.get('success', False)}")
                if gcp_result.get('success'):
                    print(f"    URL: {gcp_result.get('gcp_url', 'N/A')}")
                print(f"  Vision Analysis: {session.state.get('vision_analysis_result', {}).get('analysis_complete', False)}")
                print(f"  Gatekeeper: {session.state.get('scoring_result', {}).get('gatekeeper_passed', False)}")
                print(f"  Score: {session.state.get('scoring_result', {}).get('score', 0)}/50")
                
                # Show marketing message if generated
                marketing_result = session.state.get('marketing_result', {})
                if marketing_result:
                    print(f"\n📢 Marketing Content:")
                    print(f"  Brand: {marketing_result.get('brand', 'N/A')}")
                    print(f"  Product: {marketing_result.get('product_description', 'N/A')}")
                    print(f"  Message: {marketing_result.get('marketing_message', 'N/A')}")
                
            else:
                print("❌ Invalid image number")
        except ValueError:
            print("❌ Please enter a valid number or 'quit'")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
