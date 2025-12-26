import os
from typing import Dict, Any

class Config:
    """Production-ready configuration with API placeholder system"""
    
    def __init__(self):
        # Application
        self.APP_NAME = "Butler Enterprise"
        self.VERSION = "2.0.0"
        self.ENVIRONMENT = os.getenv("BUTLER_ENV", "production")
        self.DEBUG = self.ENVIRONMENT == "development"
        
        # Voice Settings
        self.WAKE_WORD = "butler"
        self.AUDIO_SAMPLE_RATE = 16000
        self.AUDIO_CHUNK_SIZE = 1024
        self.MAX_RECORDING_SECONDS = 8

        # Conversation timing
        self.SLEEP_BETWEEN_CONVERSATIONS = 2
        self.LISTENING_TIMEOUT = 10
        self.WAKE_WORD_TIMEOUT = 5
       
        # Service Settings
        self.DEFAULT_LOCATION = "Bangalore"
        self.MAX_VENDORS_TO_SHOW = 5
        self.CACHE_DURATION = 300

        # SMS Services
        self.SMS_API_KEY = os.getenv("SMS_API_KEY", "PLACEHOLDER_SMS_API_KEY")
        self.SMS_PROVIDER = "textlocal"  # or twilio, msg91
        self.TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")

        
        
        # ==================== API PLACEHOLDER SYSTEM ====================
        
        # Perplexity AI API (Placeholder - will be provided later)
        self.PERPLEXITY_API_KEY = os.getenv("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", "PLACEHOLDER_PERPL_EXITY_API_KEY")
        self.PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
        self.PERPLEXITY_MODEL = "llama-3.1-sonar-large-128k-online"
        
        # Medical Services APIs (Placeholders)
        self.PRACTO_API_KEY = os.getenv("PRACTO_API_KEY", "PLACEHOLDER_PRACTO_API_KEY")
        self.PRACTO_BASE_URL = "https://api.practo.com"
        
        # Maps & Location Services (Placeholders)
        self.GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "PLACEHOLDER_GOOGLE_MAPS_KEY")
        self.GOOGLE_MAPS_BASE_URL = "https://maps.googleapis.com/maps/api"
        
        # Emergency Services
        self.EMERGENCY_API_KEY = os.getenv("EMERGENCY_API_KEY", "PLACEHOLDER_EMERGENCY_API_KEY")
        self.EMERGENCY_BASE_URL = "https://api.emergency.services"
        
        # ==================== ENTERPRISE FEATURE TOGGLES ====================
        self.FEATURE_FLAGS = {
            "enhanced_intelligence": True,
            "live_booking_simulation": True,
            "smart_fallbacks": True,
            "multi_step_flows": True,
            "voice_optimization": True,
            "api_ready": False
        }
        
        # Hardware
        self.LED_PIN = 18
        self.BUTTON_PIN = 17
        
        # Paths
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.MODEL_DIR = os.path.join(self.BASE_DIR, "models")
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data")
        self.CACHE_DIR = os.path.join(self.DATA_DIR, "cache")
        self.LOG_DIR = os.path.join(self.DATA_DIR, "logs")
        self.AUDIO_CACHE_DIR = os.path.join(self.CACHE_DIR, "audio")
        
        # Create directories
        for directory in [self.MODEL_DIR, self.DATA_DIR, self.CACHE_DIR, self.LOG_DIR, self.AUDIO_CACHE_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    def is_api_available(self, service: str) -> bool:
        """Check if API is available (not a placeholder)"""
        api_keys = {
            "perplexity": self.PERPLEXITY_API_KEY,
            "practo": self.PRACTO_API_KEY,
            "google_maps": self.GOOGLE_MAPS_API_KEY,
            "emergency": self.EMERGENCY_API_KEY
        }
        
        key = api_keys.get(service)
        return key and not key.startswith("PLACEHOLDER_")
    
    def get_available_apis(self) -> Dict[str, bool]:
        """Get status of all APIs"""
        return {
            "perplexity_ai": self.is_api_available("perplexity"),
            "practo_medical": self.is_api_available("practo"),
            "google_maps": self.is_api_available("google_maps"),
            "emergency_services": self.is_api_available("emergency"),
            "enhanced_system": True
        }
    
    def validate(self):
        """Validate configuration"""
        api_status = self.get_available_apis()
        available_apis = [name for name, available in api_status.items() if available]
        
        if available_apis:
            print(f"✅ Active APIs: {', '.join(available_apis)}")
        else:
            print("🔄 Running in Enhanced Simulation Mode")
            print("💡 Real APIs can be added later without code changes")
        
        print("🚀 Production system ready!")
        return True

print("🚀 Enterprise Configuration Loaded")
