# src/config/production_config.py
import logging

logger = logging.getLogger(__name__)

class ProductionConfig:
    """Production configuration for your Butler"""
    
    # Voice settings
    VOICE_TIMEOUT = 10
    VOICE_RETRIES = 3
    VOICE_ENERGY_THRESHOLD = 400
    
    # Service settings  
    API_TIMEOUT = 30
    MAX_BOOKING_ATTEMPTS = 3
    
    # Monitoring
    HEALTH_CHECK_INTERVAL = 300  # 5 minutes
    LOG_RETENTION_DAYS = 7
    
    # Hardware
    DISPLAY_TIMEOUT = 300  # 5 minutes
    
    @classmethod
    def validate(cls):
        """Validate production configuration"""
        required_settings = [
            cls.VOICE_TIMEOUT > 0,
            cls.VOICE_RETRIES > 0,
            cls.API_TIMEOUT > 0
        ]
        
        if all(required_settings):
            logger.info("✅ Production configuration validated")
            return True
        else:
            logger.error("❌ Invalid production configuration")
            return False

# Global config instance
production_config = ProductionConfig()