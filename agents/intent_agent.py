"""
Intent Agent placeholder
"""

import logging

logger = logging.getLogger(__name__)

class IntentAgent:
    def __init__(self, llm_orchestrator):
        self.llm_orchestrator = llm_orchestrator
    
    async def detect_intent(self, message: str) -> str:
        """Detect user intent"""
        # Simple keyword-based intent detection
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["book", "schedule", "appointment"]):
            return "scheduling"
        elif any(word in message_lower for word in ["course", "program", "curriculum"]):
            return "course_info"
        elif any(word in message_lower for word in ["enroll", "signup", "register"]):
            return "enrollment"
        else:
            return "general"