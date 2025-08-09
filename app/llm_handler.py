import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
from app.models import Receipt
from app.notion_client import NotionReceiptManager
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

with open('app/prompt.yaml', 'r') as file:
    system_prompt = yaml.safe_load(file)['SYSTEM_PROMPT']

def get_openai_client():
    """Initializes and returns the OpenAI client, ensuring the API key is set."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # This will be caught by the global exception handler in main.py
        raise ValueError("OPENAI_API_KEY environment variable not found.")
    return OpenAI(api_key=api_key)

database_id = os.getenv("NOTION_TRANSACTIONS_DATABASE_ID")

def process_receipt(image_bytes: bytes):
    # Convert image bytes to base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    client = get_openai_client()
    response = client.responses.parse(
        model="gpt-5",
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text", 
                        "text": "Analyze this receipt image and extract the information according to the specified format."
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}"
                    }
                ]
            }
        ],
        text_format=Receipt,
        reasoning={
        "effort": "minimal"
    }
    )
    logger.info(f"OpenAIResponse: {response}")
    return response

def push_to_notion(receipt_data: Receipt) -> dict:
    """
    Push receipt data to Notion database.
    
    Args:
        receipt_data: Receipt object containing parsed receipt information
    
    Returns:
        Dictionary containing the response from Notion
    """
    try:
        notion_manager = NotionReceiptManager()
        # Convert enum to string value before sending to Notion
        receipt_dict = receipt_data.model_dump()
        receipt_dict['reciept_category'] = receipt_dict['reciept_category'].value
        # If there are any null values, set them to "Unknown"
        for key, value in receipt_dict.items():
            if value is None:
                receipt_dict[key] = "Unknown"
        logger.info(f"Receipt dictionary: {receipt_dict}")
        page = notion_manager.create_new_entry(receipt_dict)
        if page:
            return {
                "status": "success",
                "database_id": database_id,
                "page_id": page["id"],
                "page_url": page.get("url", ""),
                "message": "Receipt successfully added to Notion database"
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to push to Notion: {str(e)}"
        }

if __name__ == "__main__":
    import requests
    image_path = '/Users/admin/Desktop/test_receipt2.png'
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
    # Don't encode to base64 here since process_receipt() will do it
    response = process_receipt(image_bytes)    
    # Test pushing to Notion
    notion_response = push_to_notion(response.output_parsed)
    print("Notion response:", notion_response)
