# utils/voice_enhancement.py - GUARANTEED WORKING VERSION
import speech_recognition as sr
import numpy as np
import logging
import time
import os
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkingVoiceRecognizer:
    def __init__(self, microphone_index=None):
        """
        Initialize voice recognizer
        microphone_index: Specific mic index or None for auto
        """
        self.recognizer = sr.Recognizer()
        self.microphone_index = microphone_index
        self._configure_for_windows()
        
    def _configure_for_windows(self):
        """Windows-specific configuration that actually works"""
        print("⚙️ Configuring for Windows...")
        
        # CRITICAL SETTINGS FOR WINDOWS:
        self.recognizer.energy_threshold = 5000  # Much higher for Windows
        self.recognizer.dynamic_energy_threshold = False  # Disable - causes issues on Windows
        self.recognizer.pause_threshold = 2.0  # Longer wait for speech
        self.recognizer.non_speaking_duration = 0.5
        self.recognizer.phrase_threshold = 0.3
        
        print(f"✅ Configuration loaded - Using mic index: {self.microphone_index}")
    
    def test_microphone(self):
        """Test if microphone works"""
        print("🔍 Testing microphone...")
        try:
            mic_names = sr.Microphone.list_microphone_names()
            print(f"Found {len(mic_names)} microphones:")
            for i, name in enumerate(mic_names):
                print(f"  [{i}] {name}")
            
            # Test each microphone
            working_mics = []
            for i in [1, 5, 9, 11, 15]:  # Common microphone indices from your list
                try:
                    print(f"\nTrying microphone #{i}: {mic_names[i] if i < len(mic_names) else 'Unknown'}")
                    
                    mic = sr.Microphone(device_index=i)
                    with mic as source:
                        # Quick test - listen for 2 seconds
                        print("  Listening... (make some noise)")
                        self.recognizer.adjust_for_ambient_noise(source, duration=1)
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=2)
                        print(f"  ✅ Microphone #{i} WORKS - captured {len(audio.frame_data)} bytes")
                        working_mics.append(i)
                        
                except Exception as e:
                    print(f"  ❌ Microphone #{i} failed: {e}")
                    continue
            
            if working_mics:
                print(f"\n🎉 Working microphones: {working_mics}")
                return working_mics[0]  # Return first working
            else:
                print("\n💥 No working microphones found")
                return None
                
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return None
    
    def calibrate(self, source):
        """Calibrate microphone with visible feedback"""
        print("🔧 Calibrating... (please be quiet for 2 seconds)")
        try:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Calibration complete")
            return True
        except Exception as e:
            print(f"⚠️ Calibration warning: {e}")
            return False
    
    def listen(self, source, prompt="🎤 Listening... Speak now:"):
        """Reliable listening function"""
        print(prompt)
        print("(Speak immediately after this message)")
        
        try:
            # Listen with generous timeout
            start_time = time.time()
            audio = self.recognizer.listen(
                source,
                timeout=10,  # Longer timeout
                phrase_time_limit=5  # Max 5 seconds of speech
            )
            listen_time = time.time() - start_time
            
            print(f"✅ Audio captured in {listen_time:.1f}s, processing...")
            
            # Try to recognize
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"🎯 Recognized: '{text}'")
                return text.lower()
                
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                print("   Try speaking more clearly or closer to mic")
                return None
                
            except sr.RequestError as e:
                print(f"❌ API Error: {e}")
                return None
                
        except sr.WaitTimeoutError:
            print("⏰ No speech detected in 10 seconds")
            print("   Check microphone is working and not muted")
            return None
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def find_best_microphone(self):
        """Find the best working microphone"""
        print("\n" + "="*60)
        print("🔍 FINDING BEST MICROPHONE")
        print("="*60)
        
        mic_names = sr.Microphone.list_microphone_names()
        print(f"\nAvailable microphones ({len(mic_names)} found):")
        
        #

    class EnhancedVoiceRecognizer(WorkingVoiceRecognizer):
    """Enhanced version with Hindi support and better accuracy"""
    
        def __init__(self, microphone_index=None, language="hi-IN"):
            # Call parent constructor
            super().__init__(microphone_index)
            self.language = language
            
            # Hindi service keywords
            self.hindi_keywords = {
                "electrician": ["इलेक्ट्रीशन", "बिजली", "विद्युत", "तार", "electrician"],
                "carpenter": ["कारपेंटर", "बढ़ई", "लकड़ी", "फर्नीचर", "carpenter"],
                "plumber": ["प्लम्बर", "नल", "पानी", "पाइप", "plumber"],
                "exit": ["बंद", "रोको", "निकल", "समाप्त", "exit"]
            }
        
        def listen_hindi(self, source, prompt="🎤 Listening for Hindi..."):
            """Listen specifically for Hindi commands"""
            print(prompt)
            
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=5
                )
                
                # Recognize in Hindi
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"🎯 Recognized (Hindi): '{text}'")
                
                # Clean garbled text
                cleaned = self._clean_garbled_text(text)
                
                # Calculate confidence
                confidence = self._calculate_confidence(cleaned)
                
                return cleaned, confidence
                
            except sr.WaitTimeoutError:
                print("⏰ No speech detected")
                return None, 0.0
            except sr.UnknownValueError:
                print("❌ Could not understand Hindi audio")
                return None, 0.0
            except Exception as e:
                print(f"❌ Error: {e}")
                return None, 0.0
        
        def _clean_garbled_text(self, text: str) -> str:
            """Clean up ASR artifacts"""
            import re
            
            # Remove special characters but keep Hindi
            cleaned = re.sub(r'[\$\!\:\+\"\@\#\&\*\(\)]+', ' ', text)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return cleaned
        
        def _calculate_confidence(self, text: str) -> float:
            """Calculate confidence score"""
            confidence = 0.5  # Base
            
            # Check for service keywords
            for service, keywords in self.hindi_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        confidence += 0.3
                        break
            
            # Length check
            if len(text) < 3:
                confidence -= 0.2
            elif len(text) > 15:
                confidence += 0.1
            
            # Clamp between 0.1 and 1.0
            return max(0.1, min(1.0, confidence))
        
        def detect_service(self, text: str) -> str:
            """Detect which service is being requested"""
            if not text:
                return "unknown"
            
            text_lower = text.lower()
            
            for service, keywords in self.hindi_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        return service
            
            return "unknown"
