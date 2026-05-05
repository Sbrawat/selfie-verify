# api/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StandardResponse(BaseModel):
    status: str
    message: str

class VerifyResponse(BaseModel):
    status: str
    message: str
    match: bool
    session_token: Optional[str] = None
    confidence_score: Optional[float] = None

class SecurityLog(BaseModel):
    timestamp: datetime
    username: str
    action: str
    success: bool
    confidence_score: Optional[float] = None