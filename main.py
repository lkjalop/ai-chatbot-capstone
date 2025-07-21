"""
Enhanced FastAPI application for AI-powered bootcamp chatbot
Supporting web, voice, and telephony interfaces with multi-agent architecture
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional
import json
import uuid
import os
import logging

# Import our custom modules
from database import DatabaseManager
from vector_store import VectorStore
from llm_orchestrator import LLMOrchestrator, LLMProvider
from agents.rag_agent import RAGAgent
from agents.scheduler_agent import SchedulerAgent
from agents.telephony_agent import TelephonyAgent
from agents.voice_agent import VoiceAgent
from agents.feedback_agent import FeedbackAgent
from agents.intent_agent import IntentAgent
from identity_manager import IdentityManager
from monitoring import MonitoringService
from models import ChatMessage, ChatResponse, FeedbackRequest, AppointmentRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state for WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources"""
    try:
        # Initialize database
        app.state.db = DatabaseManager()
        await app.state.db.initialize()
        logger.info("Database initialized successfully")
        
        # Initialize vector store
        app.state.vector_store = VectorStore()
        await app.state.vector_store.initialize()
        logger.info("Vector store initialized successfully")
        
        # Initialize LLM orchestrator
        app.state.llm_orchestrator = LLMOrchestrator()
        logger.info("LLM orchestrator initialized")
        
        # Initialize all agents
        app.state.rag_agent = RAGAgent(app.state.vector_store, app.state.db)
        app.state.scheduler_agent = SchedulerAgent(app.state.db)
        app.state.telephony_agent = TelephonyAgent()
        app.state.voice_agent = VoiceAgent()
        app.state.feedback_agent = FeedbackAgent(app.state.db)
        app.state.intent_agent = IntentAgent(app.state.llm_orchestrator)
        logger.info("All agents initialized successfully")
        
        # Initialize security and monitoring
        app.state.identity_manager = IdentityManager()
        app.state.monitoring = MonitoringService()
        logger.info("Security and monitoring initialized")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    finally:
        # Cleanup resources
        if hasattr(app.state, 'db') and app.state.db.pool:
            await app.state.db.pool.close()
            logger.info("Database connections closed")

# Create FastAPI application
app = FastAPI(
    title="Bootcamp Chatbot API",
    description="Multi-agent AI chatbot for Employability Advantage & AusBiz Consulting",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    """Root endpoint with basic system info"""
    return {
        "message": "Bootcamp Chatbot is live",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "healthy",
            "vector_store": "healthy",
            "llm_orchestrator": "healthy"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )