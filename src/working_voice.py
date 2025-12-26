import pyttsx3
import threading
import queue
import time
import logging

logger = logging.getLogger(__name__)

class HDMIVoiceSystem:
    """Voice system optimized for HDMI audio on Raspberry Pi"""
    
    def __init__(self):
        print("🔊 Initializing HDMI Voice System...")
        
        # Set ALSA environment variables
        import os
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
        os.environ['SDL_AUDIODRIVER'] = "alsa"
        os.environ['AUDIODEV'] = "hw:0,0"
        
        self.engine = None
        self.queue = queue.Queue()
        self.is_speaking = False
        self.initialized = False
        
        # Try to initialize engine
        self._initialize_engine()
        
        if self.initialized:
            # Start processing thread
            self.process_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.process_thread.start()
            print("✅ HDMI Voice System Ready")
        else:
            print("⚠️ Voice system initialization failed")
    
    def _initialize_engine(self):
        """Initialize TTS engine with HDMI support"""
        try:
            # Try different initialization methods
            self.engine = pyttsx3.init(driverName='espeak')
            self.initialized = True
            
            # Configure
            self.engine.setProperty('rate', 160)
            self.engine.setProperty('volume', 0.9)
            
            # Try to find English voice
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'english' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    print(f"🎤 Selected: {voice.name}")
                    return
            
            # Use first available
            if voices:
                self.engine.setProperty('voice', voices[0].id)
                print(f"🎤 Using: {voices[0].name}")
                
        except Exception as e:
            print(f"⚠️ Engine init failed: {e}")
            try:
                # Fallback to default init
                self.engine = pyttsx3.init()
                self.initialized = True
                print("✅ Fallback initialization successful")
            except Exception as e2:
                print(f"❌ All initialization failed: {e2}")
                self.initialized = False
    
    def _process_queue(self):
        """Process speech queue"""
        while True:
            try:
                text = self.queue.get(timeout=1)
                if text and self.initialized:
                    self._speak_text(text)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Queue error: {e}")
    
    def _speak_text(self, text: str):
        """Speak text"""
        try:
            self.is_speaking = True
            print(f"🗣️ Speaking: '{text[:50]}...'")
            self.engine.say(text)
            self.engine.runAndWait()
            time.sleep(0.1)
            self.is_speaking = False
        except Exception as e:
            logger.error(f"Speech error: {e}")
            self.is_speaking = False
    
    def speak(self, text: str):
        """Queue text for speech"""
        if not text or not self.initialized:
            return
        
        self.queue.put(text)
    
    def speak_immediate(self, text: str):
        """Speak immediately (clears queue)"""
        if not text or not self.initialized:
            return
        
        # Clear queue
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except:
                break
        
        # Stop current speech
        try:
            self.engine.stop()
        except:
            pass
        
        # Speak immediately
        self._speak_text(text)
    
    def wait_until_finished(self, timeout: float = 10.0):
        """Wait for speech to finish"""
        start = time.time()
        while self.is_speaking and (time.time() - start) < timeout:
            time.sleep(0.1)
    
    def test(self):
        """Test the voice system"""
        if not self.initialized:
            print("❌ Cannot test - voice system not initialized")
            return
        
        print("\n🔊 Testing voice system...")
        
        tests = [
            "Hello, I am Butler.",
            "Audio system is working.",
            "Voice output through HDMI.",
            "Test complete."
        ]
        
        for text in tests:
            print(f"  Speaking: {text}")
            self.speak_immediate(text)
            self.wait_until_finished()
            time.sleep(1)
        
        print("✅ Voice test complete!")

# Create global instance
voice = HDMIVoiceSystem()

if __name__ == "__main__":
    voice.test()