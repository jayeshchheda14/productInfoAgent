[README.md](https://github.com/user-attachments/files/23752637/README.md)
# Product Info Agent

This agent functions as an automated product image analysis system designed to validate, scan, and generate marketing content for product images. Its primary role is to ensure that product images meet quality, security, and ecommerce eligibility standards through a comprehensive validation pipeline.

## Overview

This agent analyzes product images for ecommerce suitability by performing virus scanning, vision analysis, policy scoring, and marketing content generation. Its primary purpose is to serve as an automated product validation system that maintains high standards of quality, security, and compliance.

* Scans images for viruses and malware using ClamAV
* Uploads clean images to GCP Storage for audit trails
* Analyzes images using Google Vision API for product recognition and brand detection
* Scores images against configurable policy rules with gatekeeper validation
* Generates dynamic marketing content using Gemini AI
* Provides comprehensive logging for debugging and audit trails

This agent enables users to validate product images and automatically generate marketing content while ensuring compliance with ecommerce policies.

## Agent Details

The key features of the Product Info ADK Agent include:

| Feature | Description |
| --- | --- |
| **Interaction Type** | Conversational + Workflow |
| **Complexity** | Medium |
| **Agent Type** | Multi-Tool Agent |
| **Components** | Tools: ClamAV, Google Vision API, Gemini AI |
| **Vertical** | Ecommerce |

## Setup and Installation

1. **Prerequisites**

   * Python 3.10+
   * A project on Google Cloud Platform
   * Google Cloud CLI
   * Google API Key (for Gemini)
   * GCP Service Account with Storage and Vision API permissions
   * ClamAV (optional, for real virus scanning)

2. **Installation**

   ```bash
   # Clone this repository
   cd MultiAgentPython/productInfoAgent
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configuration**

   * Create a `.env` file with the following:

     ```env
     GOOGLE_API_KEY=your_gemini_api_key_here
     GCP_BUCKET_NAME=your-bucket-name
     GOOGLE_APPLICATION_CREDENTIALS=C:/path/to/service-account.json
     API_DELAY_SECONDS=5
     ```

   * Set up Google Cloud credentials:

     ```bash
     gcloud auth application-default login
     gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
     ```

   * Enable required APIs in GCP Console:
     - Cloud Storage API
     - Cloud Vision API

4. **Setup Test Images**

   ```bash
   # Create image directory
   mkdir C:\Image
   # Add product images (.jpg, .png) to C:\Image
   ```

## Running the Agent

**Using `adk run`**

ADK provides convenient ways to interact with the agent locally. Example requests:

* `what can you do for me`
* `scan C:\Image folder`
* `analyze C:\Image\product.jpg`

Run the agent using CLI:

```bash
adk run .\productInfoAgent\
```

**Using Python Scripts**

For programmatic access:

```bash
# Interactive mode - shows menu and waits for input
python interactive_runner.py


```

## Agent Workflow

The Product Info ADK Agent implements the following sequential workflow:

1. **Image Loading** - Loads image from file path or folder
   * Supports specific file paths or folder scanning
   * Reads and base64 encodes image data
   * Stores in session state for downstream tools

2. **Virus Scanning** - Scans for malware using ClamAV (or mock scanner)
   * Uses ClamAV if installed, otherwise mock scanner
   * Logs scan method and results
   * Blocks processing if virus detected

3. **GCP Upload** - Uploads clean images to Google Cloud Storage for audit
   * Uploads to `gs://bucket-name/audit/filename.jpg`
   * Creates audit trail for compliance
   * Logs upload status and GCS URL

4. **Vision Analysis** - Analyzes with Google Vision API
   * Detects labels (product type, attributes)
   * Identifies brand logos
   * Extracts text from packaging
   * Localizes objects
   * Logs all detected labels, logos, and text

5. **Policy Scoring** - Validates against policy rules
   * Checks image dimensions (min 200x200px) - 10 points
   * Validates resolution (>500x500px) - 15 points
   * Verifies color format (RGB/RGBA) - 10 points
   * Scores professional dimensions (≥800x600px) - 5 points
   * Validates ecommerce eligibility
   * Logs detailed score calculation breakdown

6. **Gatekeeper Decision** - Determines if image passes
   * Policy score ≥ 45/50
   * Product detected with confidence ≥ 0.7
   * Ecommerce eligible
   * Provides detailed rejection reasons if failed

7. **Marketing Generation** (if approved) - Creates content using Gemini
   * Extracts brand and product name from vision data
   * Generates compelling marketing message
   * Provides product description and category
   * Rate-limited to respect API quotas

## Policy Configuration

Edit `policy.json` to customize scoring rules:

```json
{
  "image_policy": {
    "scoring": {
      "threshold": 45,
      "max_score": 50
    },
    "technical_requirements": {
      "min_width": 200,
      "min_height": 200
    }
  },
  "ecommerce_policy": {
    "validation_rules": {
      "min_product_confidence": 0.7
    }
  }
}
```

## Output Example

```json
{
  "status": "approved",
  "policy_score": {
    "score": 50,
    "threshold": 45,
    "passed": true,
    "details": [
      "Width requirement met: 1200px >= 200px",
      "Height requirement met: 800px >= 200px",
      "High resolution image detected: 1200x800",
      "Good color format: RGB",
      "Professional image dimensions: 1200x800"
    ]
  },
  "virus_scan": {
    "clean": true,
    "method": "mock",
    "note": "Install ClamAV for real scanning"
  },
  "gcp_upload": {
    "success": true,
    "gcp_url": "gs://product-audit-bucket/audit/product.jpg",
    "message": "Image uploaded to GCP for audit"
  },
  "vision_analysis": {
    "labels": [
      {"description": "Bottle", "score": 0.98},
      {"description": "Plastic bottle", "score": 0.95},
      {"description": "Drink", "score": 0.92}
    ],
    "logos": [{"description": "Gatorade", "score": 0.96}],
    "detected_text": "Gatorade Rain Berry...",
    "objects": [{"name": "Bottle", "score": 0.94}],
    "analysis_complete": true
  },
  "marketing": {
    "brand": "Gatorade",
    "product_description": "Rain Berry Electrolyte Beverage",
    "marketing_message": "Gatorade Rain Berry delivers superior hydration...",
    "category": "Sports Drink",
    "confidence": 1.0
  }
}
```

## Debugging and Logs

The agent includes comprehensive logging for debugging:

* Logs saved to `productInfoAgent/logs/agent_YYYYMMDD_HHMMSS.log`
* `logs/latest.log` points to most recent log
* Logs include:
  - **Image Loading**: File path, size, success/failure
  - **Virus Scan**: Filename, scan method, result
  - **GCP Upload**: Upload status, GCS URL, errors
  - **Vision Analysis**: All labels with scores, logos, detected text (full), objects
  - **Policy Scoring**: Image dimensions (width, height, mode), score calculation breakdown with points per rule, final score
  - **Marketing**: Brand, product, message preview, API calls

**Example Log Output:**
```
[LOAD_IMAGE] Starting - path: C:\Image\product.jpg
[LOAD_IMAGE] Success - file: product.jpg, size: 245678 bytes
[VIRUS_SCAN] Starting
[VIRUS_SCAN] Result - clean: True, method: mock
[GCP_UPLOAD] Starting upload to GCP for audit
[GCP_UPLOAD] Success - uploaded to gs://bucket/audit/product.jpg
[VISION_API] Success - labels: 10, logos: 1, text: 119 chars, objects: 2
[VISION_API] Labels detected:
  - Bottle: 0.98
  - Plastic bottle: 0.95
[VISION_API] Logos detected:
  - Gatorade: 0.96
[SCORING] Image properties - Width: 1200px, Height: 800px, Mode: RGB
[SCORING] +10 points: Width 1200px >= 200px (Total: 10)
[SCORING] +10 points: Height 800px >= 200px (Total: 20)
[SCORING] +15 points: High resolution 1200x800 > 500x500 (Total: 35)
[SCORING] +10 points: Good color mode RGB (Total: 45)
[SCORING] +5 points: Professional dimensions 1200x800 (Total: 50)
[SCORING] Final score calculation: 50/50 (capped at 50)
[SCORING] Policy result - Score: 50/45, Passed: True
[MARKETING] Success - brand: Gatorade, product: Rain Berry
```

View logs:
```bash
# Latest log
type productInfoAgent\logs\latest.log

# Tail logs in real-time
tail -f productInfoAgent\logs\latest.log
```

## Customization

The Product Info ADK Agent can be customized:

1. **Policy Rules** - Modify `policy.json` to adjust scoring criteria and thresholds
2. **Vision Analysis** - Add custom detection logic in `vision_analysis_tool.py`
3. **Marketing Prompts** - Customize Gemini prompts in `marketing_tool.py`
4. **Rate Limiting** - Adjust `API_DELAY_SECONDS` in `.env` to control API call frequency
5. **Virus Scanning** - Install ClamAV for real virus scanning instead of mock

## Troubleshooting

**Common Issues:**

* **429 RESOURCE_EXHAUSTED** - Hit Gemini API quota (15 requests/min for gemini-2.0-flash)
  - Solution: Wait 60 seconds or increase `API_DELAY_SECONDS` in `.env`

* **GCP Authentication Error** - Service account file not found
  - Solution: Verify `GOOGLE_APPLICATION_CREDENTIALS` path in `.env`

* **GCP Upload Error** - Bucket not found or permission denied
  - Solution: Verify `GCP_BUCKET_NAME` exists and service account has Storage Admin role

* **Vision API Error** - API not enabled or permissions missing
  - Solution: Enable Vision API in GCP Console and verify service account roles

* **Policy File Not Found** - `policy.json` missing
  - Solution: Ensure `policy.json` exists in project root

* **ClamAV Not Found** - Agent uses mock scanning
  - Solution: Install ClamAV or continue with mock scanning for development

## Architecture

The agent uses a single conversational Agent with multiple tools:

```
product_analysis_agent
├── load_image_from_folder (tool) - Loads image from disk
├── scan_for_virus (tool) - ClamAV virus scanning
├── upload_to_gcp (tool) - Uploads to GCS for audit
├── analyze_with_vision_api (tool) - Google Vision API analysis
├── score_product_image (tool) - Policy scoring & gatekeeper
└── generate_marketing_content (tool) - Gemini AI marketing generation
```

Each tool is called sequentially based on user input, with results stored in session state for downstream tools to access.

**Tool Dependencies:**
- `scan_for_virus` requires `image_data` from `load_image_from_folder`
- `upload_to_gcp` requires successful virus scan
- `analyze_with_vision_api` requires `image_data`
- `score_product_image` requires `vision_analysis_result`
- `generate_marketing_content` requires `vision_analysis_result` and gatekeeper approval

## License

MIT License - see LICENSE file for details.
