"""
Telephony Agent placeholder
"""

import logging

logger = logging.getLogger(__name__)

class TelephonyAgent:
    def __init__(self):
        pass
    
    async def handle_inbound_call(self, call_sid: str, from_number: str):
        """Handle inbound calls"""
        return "<Response><Say>Hello from the bootcamp chatbot!</Say></Response>"
    
    async def make_outbound_call(self, to_number: str, appointment_data: dict):
        """Make outbound call"""
        return None