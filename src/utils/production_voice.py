# src/utils/production_voice.py
import speech_recognition as sr
import logging
import time
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class ProductionVoiceRecognizer:
    """Production-ready voice recognizer for Butler Assistant"""
    
    def __init__(self, microphone_index: int = 1):
        """
        Initialize with specific microphone index
        Based on your test, index 1 is your USB microphone
        """
        self.recognizer = sr.Recognizer()
        self.microphone_index = microphone_index
        self._configure_production_settings()
        self.last_calibration_time = 0
        self.calibration_valid_minutes = 30  # Recalibrate every 30 minutes
        
        logger.info(f"🎤 Production Voice Recognizer initialized (Mic index: {microphone_index})")
    
    def _configure_production_settings(self):
        """Configure production-optimized settings"""
        # These settings WORKED in your test
        self.recognizer.energy_threshold = 5000
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 2.0
        self.recognizer.non_speaking_duration = 0.5
        self.recognizer.phrase_threshold = 0.3
        
        logger.info("⚙️ Production settings configured")
    
    def ensure_calibration(self, source):
        """Ensure microphone is properly calibrated"""
        current_time = time.time()
        needs_calibration = (
            self.last_calibration_time == 0 or
            (current_time - self.last_calibration_time) > (self.calibration_valid_minutes * 60)
        )
        
        if needs_calibration:
            logger.info("🔧 Calibrating microphone for current environment...")
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.last_calibration_time = current_time
                logger.info("✅ Microphone calibration complete")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Calibration warning: {e}")
                return False
        return True
    
    def listen_for_command(self, timeout: int = 10) -> Optional[str]:
        """
        Listen for voice command with production reliability
        Returns: Recognized text or None
        """
        logger.info("🎤 Listening for voice command...")
        
        try:
            # Use the specific microphone that worked (index 1 = USB mic)
            with sr.Microphone(device_index=self.microphone_index) as source:
                # Ensure calibration
                self.ensure_calibration(source)
                
                logger.info("🎤 Speak now...")
                
                # Listen with production settings
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=7  # Reasonable limit for commands
                )
                
                logger.info("✅ Audio captured, processing recognition...")
                
                # Recognize with Google Speech Recognition
                try:
                    text = self.recognizer.recognize_google(audio)
                    text_lower = text.lower()
                    logger.info(f"🎯 Recognized: '{text_lower}'")
                    return text_lower
                    
                except sr.UnknownValueError:
                    logger.warning("❌ Could not understand audio")
                    return None
                    
                except sr.RequestError as e:
                    logger.error(f"🌐 API Error: {e}")
                    return None
                    
        except sr.WaitTimeoutError:
            logger.warning("⏰ No speech detected within timeout")
            return None
            
        except Exception as e:
            logger.error(f"❌ Voice recognition error: {e}")
            return None
    
    def detect_service_keyword(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detect service keywords from recognized text
        Returns: (success, service_type)
        """
        if not text:
            return False, None
        
        # Service keywords mapping
        service_keywords = {
            'electrician': ['electrician', 'electrical', 'electric', 'wiring', 'light', 'power'],
            'plumber': ['plumber', 'plumbing', 'pipe', 'water', 'leak', 'drain'],
            'carpenter': ['carpenter', 'carpentry', 'wood', 'furniture', 'cabinet'],
            'cleaner': ['cleaner', 'cleaning', 'clean', 'housekeeping', 'maid']
        }
        
        # Check each service
        for service, keywords in service_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    logger.info(f"✅ Detected service: {service} (from keyword: '{keyword}')")
                    return True, service
        
        logger.warning(f"⚠️ No service keyword found in: '{text}'")
        return False, None
    
    def test_voice_system(self):
        """Test the complete voice system"""
        print("\n" + "="*60)
        print("🔊 PRODUCTION VOICE SYSTEM TEST")
        print("="*60)
        
        print(f"Using microphone index: {self.microphone_index}")
        print("This should be your USB microphone")
        
        # Test 1: Listen for any command
        print("\n🎤 TEST 1: Say any phrase...")
        result1 = self.listen_for_command(timeout=8)
        
        if result1:
            print(f"✅ SUCCESS: Heard '{result1}'")
            
            # Test 2: Detect service
            print("\n🔍 TEST 2: Detecting service keyword...")
            success, service = self.detect_service_keyword(result1)
            
            if success:
                print(f"✅ SERVICE DETECTED: {service}")
                print(f"🎉 VOICE SYSTEM IS PRODUCTION READY!")
                return True, service
            else:
                print(f"⚠️ No service detected in: '{result1}'")
                print("   Try saying 'electrician' or 'plumber'")
                return True, None
        else:
            print("❌ No speech detected")
            return False, None

# Create default instance
production_voice = ProductionVoiceRecognizer(microphone_index=1)

if __name__ == "__main__":
    # Test the production voice system
    print("Testing Production Voice System...")
    
    success, service = production_voice.test_voice_system()
    
    if success:
        print("\n✅ Production voice system is WORKING!")
        if service:
            print(f"   Detected service: {service}")
    else:
        print("\n❌ Voice system needs attention")