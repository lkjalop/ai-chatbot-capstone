"""
Pydantic models for the chatbot
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

class IntentType(str, Enum):
    GENERAL = "general"
    COURSE_INFO = "course_info"
    ENROLLMENT = "enrollment"
    SCHEDULING = "scheduling"

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=1, max_length=255)
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatResponse(BaseModel):
    message: str
    session_id: str
    intent: Optional[IntentType] = None
    confidence: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sources: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class FeedbackRequest(BaseModel):
    conversation_id: str
    rating: int = Field(..., ge=-1, le=1)
    comment: Optional[str] = None

class AppointmentRequest(BaseModel):
    user_id: str
    preferred_time: str
    phone_number: str
    appointment_type: Optional[str] = "consultation"
    notes: Optional[str] = None