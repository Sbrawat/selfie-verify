# api/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import uuid

# Import your existing modular logic
from core.vision_engine import engine
from db.mongo_client import (
    create_user_profile, 
    get_user_embedding, 
    save_session_token,
    log_security_event,
    get_recent_logs
)
from schemas import StandardResponse, VerifyResponse

app = FastAPI(title="FaceAuth API", version="2.0.0")

# Allow your future Streamlit frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def process_uploaded_image(file: UploadFile):
    """Helper function to convert an HTTP file upload into an OpenCV RGB image."""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file format.")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


@app.post("/api/v1/register", response_model=StandardResponse)
async def register_user(username: str = Form(...), file: UploadFile = File(...)):
    
    rgb_frame = await process_uploaded_image(file)
    encoding = engine.extract_embedding(rgb_frame)
    
    if encoding is None:
        log_security_event(username, "REGISTER", False)
        raise HTTPException(status_code=400, detail="No face detected in the image.")
        
    # Save to MongoDB
    create_user_profile(username, encoding)
    log_security_event(username, "REGISTER", True)
    
    return StandardResponse(status="success", message=f"User {username} registered.")


@app.post("/api/v1/verify", response_model=VerifyResponse)
async def verify_identity(username: str = Form(...), file: UploadFile = File(...)):
    
    saved_encoding = get_user_embedding(username)
    if saved_encoding is None:
        log_security_event(username, "VERIFY", False)
        raise HTTPException(status_code=404, detail="User not found.")

    rgb_frame = await process_uploaded_image(file)
    live_encoding = engine.extract_embedding(rgb_frame)

    if live_encoding is None:
        log_security_event(username, "VERIFY", False)
        raise HTTPException(status_code=400, detail="No face detected in the live image.")

    # In a production app, you can calculate exact distance for the confidence score. 
    # For now, we use a boolean match.
    is_match = engine.verify_match(live_encoding, saved_encoding)
    
    if is_match:
        token = uuid.uuid4().hex
        save_session_token(username, token)
        log_security_event(username, "VERIFY", True, confidence_score=95.0) # Mock score
        
        return VerifyResponse(
            status="success", 
            message="Identity verified.", 
            match=True, 
            session_token=token,
            confidence_score=95.0
        )
    else:
        log_security_event(username, "VERIFY", False, confidence_score=15.0)
        return VerifyResponse(
            status="failed", 
            message="Face does not match.", 
            match=False
        )

@app.get("/")
async def health_check():
    """Simple health check to verify the API is running."""
    return {
        "status": "online", 
        "service": "FaceAuth API", 
        "version": "2.0.0"
    }

@app.get("/api/v1/logs")
async def get_security_logs():
    """Endpoint for the Admin Dashboard to fetch SOC data."""
    logs = get_recent_logs()
    return {"status": "success", "logs": logs}