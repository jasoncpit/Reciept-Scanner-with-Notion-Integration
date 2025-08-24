from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Request
from app.llm_handler import process_receipt, push_to_notion
from app.security import setup_security_middleware, validate_file_upload, validate_auth_token, log_security_event
from datetime import datetime
import os

app = FastAPI(title="Receipt Scanner API", version="1.0.0")
limiter = setup_security_middleware(app)

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "100"))

@app.post("/scan")
@limiter.limit(f"{os.getenv('RATE_LIMIT_PER_MINUTE', '10')}/minute")
async def scan_receipt(
    request: Request,
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    # Authentication
    validate_auth_token(authorization, AUTH_TOKEN)
    
    # File validation
    validate_file_upload(file, MAX_FILE_SIZE)
    
    try:
        # Read the uploaded file
        image_bytes = await file.read()
        
        # Additional file size check after reading
        if len(image_bytes) > MAX_FILE_SIZE * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE}MB")
        
        # Log successful request
        log_security_event("receipt_scan_requested", request, {
            "file_size": len(image_bytes),
            "content_type": file.content_type
        })
        
        # Process the receipt image
        receipt_response = process_receipt(image_bytes)       

        #  
        # Push to Notion
        notion_response = push_to_notion(receipt_response.output_parsed)
        
        return {
            "status": "success",
            "receipt_data": receipt_response.output_parsed.model_dump(),
            "notion_response": notion_response
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error
        log_security_event("receipt_scan_error", request, {"error": str(e)})
        raise HTTPException(status_code=500, detail="Error processing receipt")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Receipt Scanner API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "scan": "/scan (POST)"
        }
    }

if __name__ == "__main__":
    import requests
    image_path = '/Users/admin/Desktop/test_receipt.png'
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
    # Don't encode to base64 here since process_receipt() will do it
    response = process_receipt(image_bytes)    
    # Test pushing to Notion
    notion_response = push_to_notion(response.output_parsed)
    print("Notion response:", notion_response)
