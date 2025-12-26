# utils/fallbacks.py
import random
import datetime

class FallbackResponseGenerator:
    def __init__(self):
        self.fallback_responses = [
            "I'm not sure I understand. Could you rephrase that?",
            "Let me think about how to help with that.",
            "I want to make sure I get this right. Could you provide more details?",
            "That's an interesting request. Let me see how I can assist.",
            "I'm still learning. Could you try asking in a different way?"
        ]
        
    def get_contextual_fallback(self, user_input: str) -> str:
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ['help', 'emergency', 'urgent']):
            return "This sounds important. Please describe what kind of help you need."
        elif any(word in input_lower for word in ['service', 'book', 'need']):
            return "Which service are you looking for? Plumbing, electrical, cleaning, or something else?"
        elif any(word in input_lower for word in ['time']):
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
        else:
            return random.choice(self.fallback_responses)
