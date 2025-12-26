# voice/reliable_voice.py
import speech_recognition as sr
import numpy as np
import asyncio
from typing import Tuple

class ReliableVoiceRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Enhanced configuration
        self.recognizer.pause_threshold = 0.8
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        
        self._calibrate_microphone()
    
    def _calibrate_microphone(self):
        print("🎤 Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=3)
        print("✅ Microphone calibrated!")
    
    async def reliable_listen(self, timeout: int = 8, phrase_time_limit: int = 6) -> Tuple[str, bool]:
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                print(f"🎯 Listening attempt {attempt + 1}...")
                
                with self.microphone as source:
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit
                    )
                
                if await self._validate_audio_quality(audio):
                    text = await self._transcribe_with_fallbacks(audio)
                    
                    if text and len(text.strip()) > 2:
                        print(f"✅ Recognized: {text}")
                        return text, True
                    else:
                        print("❌ Empty transcription")
                else:
                    print("❌ Poor audio quality")
                    
            except sr.WaitTimeoutError:
                print("⏰ Listening timeout")
                if attempt == max_attempts - 1:
                    return "I'm listening... please speak now.", False
                    
            except sr.UnknownValueError:
                print("🤔 Could not understand audio")
                if attempt == max_attempts - 1:
                    return "I didn't catch that. Could you please repeat?", False
                    
            except Exception as e:
                print(f"🎯 Listening error: {e}")
                if attempt == max_attempts - 1:
                    return "There seems to be a microphone issue. Please check your connection.", False
            
            attempt += 1
            await asyncio.sleep(0.5)
        
        return "I'm having trouble hearing you. Please try again.", False

    async def _validate_audio_quality(self, audio) -> bool:
        try:
            audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
            rms = np.sqrt(np.mean(audio_data**2))
            return rms > 1000  # Not too quiet
        except:
            return True

    async def _transcribe_with_fallbacks(self, audio) -> str:
        try:
            return self.recognizer.recognize_google(audio)
        except:
            try:
                # Optional: Add Wit.ai fallback here
                # return self.recognizer.recognize_wit(audio, key="YOUR_KEY")
                return ""
            except:
                return ""
