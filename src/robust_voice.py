"""
robust_voice.py - Advanced voice recognition with fallbacks
"""
import speech_recognition as sr
import pyaudio
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustVoiceRecognizer:
    """Enhanced voice recognition with multiple fallbacks"""
    
    def __init__(self, energy_threshold=300, pause_threshold=0.8):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.dynamic_energy_threshold = True
        
        self.mic = None
        self.working_device = None
        self.setup_microphone()
    
    def setup_microphone(self):
        """Find and use working microphone with fallback"""
        logger.info("🔍 Scanning for working microphones...")
        
        # Try to use default first
        try:
            self.mic = sr.Microphone()
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("✅ Using default microphone")
            self.working_device = None
            return
        except Exception as e:
            logger.warning(f"⚠️ Default mic failed: {e}")
        
        # Scan all devices
        p = pyaudio.PyAudio()
        device_found = False
        
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                logger.info(f"  Testing device {i}: {dev['name'][:50]}...")
                try:
                    test_mic = sr.Microphone(device_index=i)
                    with test_mic as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.mic = test_mic
                    self.working_device = i
                    device_found = True
                    logger.info(f"✅ Selected device {i}: {dev['name'][:30]}")
                    break
                except Exception as e:
                    logger.debug(f"    Device {i} failed: {e}")
        
        p.terminate()
        
        if not device_found:
            logger.error("❌ No working microphone found!")
            raise Exception("No audio input devices available")
    
    def listen_with_retry(self, timeout=5, retries=3, phrase_time_limit=10):
        """Robust listening with multiple retry strategies"""
        
        if not self.mic:
            self.setup_microphone()
        
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"🎤 Listening (attempt {attempt}/{retries})...")
                
                with self.mic as source:
                    # Adjust for ambient noise each attempt
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Listen with timeouts
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit
                    )
                    
                    logger.info("✓ Audio captured, processing...")
                    
                    # TRY MULTIPLE RECOGNITION ENGINES (with fallback)
                    
                    # 1. Try Google (best accuracy)
                    try:
                        text = self.recognizer.recognize_google(audio)
                        logger.info(f"✅ Google understood: {text}")
                        return text.lower()
                    except sr.UnknownValueError:
                        logger.warning("Google couldn't understand audio")
                    except sr.RequestError as e:
                        logger.warning(f"Google API error: {e}")
                    
                    # 2. Try Whisper if available (offline)
                    try:
                        text = self.recognizer.recognize_whisper(audio, language="en")
                        logger.info(f"✅ Whisper understood: {text}")
                        return text.lower()
                    except:
                        pass  # Whisper not installed or failed
                    
                    # 3. Try Vosk (offline, if installed)
                    try:
                        import vosk  # Import inside try block
                        text = self.recognizer.recognize_vosk(audio)
                        logger.info(f"✅ Vosk understood: {text}")
                        return text.lower()
                    except:
                        pass
                    
                    # 4. Try Sphinx (offline, least accurate)
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                        logger.info(f"✅ Sphinx understood: {text}")
                        return text.lower()
                    except:
                        pass
                    
                    logger.warning("All recognition engines failed")
                    
            except sr.WaitTimeoutError:
                logger.warning(f"⏰ Timeout on attempt {attempt}")
                time.sleep(0.5)  # Brief pause before retry
                
            except Exception as e:
                logger.error(f"❌ Error on attempt {attempt}: {e}")
                time.sleep(1)
        
        logger.error("All retries exhausted")
        return None
    
    def quick_listen(self, prompt_text="Yes or No?", yes_no_mode=True):
        """Optimized for yes/no confirmation"""
        original_threshold = self.recognizer.energy_threshold
        self.recognizer.energy_threshold = 400  # Higher for yes/no
        
        try:
            text = self.listen_with_retry(timeout=3, retries=2, phrase_time_limit=3)
            
            if text and yes_no_mode:
                # Simple yes/no detection
                if any(word in text for word in ['yes', 'yeah', 'yep', 'correct', 'right', 'हाँ', 'हां']):
                    return 'yes'
                elif any(word in text for word in ['no', 'nope', 'wrong', 'incorrect', 'नहीं']):
                    return 'no'
            
            return text
        finally:
            self.recognizer.energy_threshold = original_threshold
    
    def get_audio_info(self):
        """Get info about current audio setup"""
        info = {
            'device_index': self.working_device,
            'energy_threshold': self.recognizer.energy_threshold,
            'pause_threshold': self.recognizer.pause_threshold
        }
        
        if self.working_device is not None:
            p = pyaudio.PyAudio()
            try:
                dev = p.get_device_info_by_index(self.working_device)
                info['device_name'] = dev['name']
                info['channels'] = dev['maxInputChannels']
            finally:
                p.terminate()
        
        return info

# Test function
if __name__ == "__main__":
    print("🔊 Testing RobustVoiceRecognizer...")
    rvr = RobustVoiceRecognizer()
    print(f"Audio Info: {rvr.get_audio_info()}")
    
    print("\nSpeak something (will try 3 times)...")
    text = rvr.listen_with_retry()
    
    if text:
        print(f"\n✅ FINAL RESULT: {text}")
    else:
        print("\n❌ Could not understand anything")
