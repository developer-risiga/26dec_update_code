# Update your voice_manager.py to support Indian languages
import os
import time
import pyttsx3
import threading

class VoiceManager:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.current_lang = "english"
        self.is_speaking = False
        print("🔊 Butler Voice: pyttsx3 with Indian language support")
        
        # Set default voice
        self.set_voice("english")
    
    def set_voice(self, language):
        """Set voice for specific language"""
        self.current_lang = language
        
        # Map language names to voice IDs from your check_voices.py
        voice_map = {
            "hindi": "hindi",
            "tamil": "tamil", 
            "telugu": "telugu-test",
            "kannada": "kannada",
            "malayalam": "malayalam", 
            "bengali": "bengali",
            "gujarati": "gujarati-test",
            "punjabi": "punjabi",
            "english": "english"
        }
        
        if language in voice_map:
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if voice_map[language] in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    print(f"   🔊 Voice set to: {language} ({voice.id})")
                    return True
        
        return False
    
    def speak(self, text, wait=False):
        """Make Butler speak"""
        print(f"🔊 Butler: {text}")
        
        # Run in background thread
        thread = threading.Thread(target=self._speak_thread, args=(text, wait))
        thread.daemon = True
        thread.start()
        
        if wait:
            thread.join(timeout=10)
    
    def _speak_thread(self, text, wait):
        """Background thread for speech"""
        self.is_speaking = True
        try:
            self.engine.say(text)
            if wait:
                self.engine.runAndWait()
            else:
                self.engine.startLoop(False)
                self.engine.iterate()
                self.engine.endLoop()
        except Exception as e:
            print(f"⚠️ Speech error: {e}")
        finally:
            self.is_speaking = False
    
    def speak_immediate(self, text):
        """Stop current speech and speak immediately"""
        self.stop()
        time.sleep(0.2)
        self.speak(text, wait=True)
    
    def stop(self):
        """Stop any speaking"""
        try:
            self.engine.stop()
        except:
            pass
        self.is_speaking = False
    
    def wait_until_done(self, timeout=10):
        """Wait for speech to finish"""
        start_time = time.time()
        while self.is_speaking and (time.time() - start_time) < timeout:
            time.sleep(0.1)

# KEEP ALL YOUR EXISTING RESPONSE FUNCTIONS (same as before)
def welcome():
    return "Hello, I am Butler. How can I help you today?"

def listening():
    return "I am listening."

def processing():
    return "Let me check that for you."

def command_received(command):
    return "I understand. Let me find that for you."

def service_confirmed(service):
    return f"I found a {service}. Starting the booking process."

def searching(service):
    return f"Searching for available {service} professionals."

def booking_confirmed(service):
    return f"Excellent. Your {service} is booked and will arrive within two hours."

def help_prompt():
    return "You can ask for a plumber, electrician, cleaner, or carpenter."

def goodbye():
    return "Goodbye. Thank you for using Butler."

# Create global instance
voice = VoiceManager()
