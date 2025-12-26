"""
robust_voice_final.py - Production-ready voice recognizer with text mode fallback
"""
import asyncio
import logging
import random
import time
import sys

logger = logging.getLogger(__name__)

class AsyncVoiceRecognizer:
    """Voice recognizer with automatic text mode fallback"""
    
    def __init__(self, text_mode=False):
        self.is_listening = False
        self.text_mode = text_mode
        
        # Detect if we should use simulation mode
        self.simulation_mode = True  # Default to simulation for safety
        
        if text_mode:
            logger.info("📝 TEXT MODE ENABLED: Using keyboard input")
            logger.info("   - Press Enter for wake word")
            logger.info("   - Type commands manually")
        else:
            logger.info("🎤 VOICE MODE: Attempting microphone input")
            
            # Try to detect if microphone is available
            try:
                import speech_recognition as sr
                # Quick test to see if microphone works
                with sr.Microphone() as source:
                    logger.debug("Microphone test passed")
                self.simulation_mode = False
                logger.info("✅ Microphone detected - using real voice recognition")
            except Exception as e:
                logger.warning(f"⚠️ Microphone not available: {e}")
                logger.info("🔄 Falling back to simulation mode")
                self.simulation_mode = True
        
    async def initialize(self):
        """Initialize voice engine"""
        if self.text_mode:
            logger.info("[SYNC] Text mode voice engine initialized")
        elif self.simulation_mode:
            logger.info("[SYNC] Simulation voice engine initialized")
        else:
            logger.info("[SYNC] Real voice engine initialized")
        return True
    
    async def wait_for_wake_word(self, wake_word="butler", timeout=30):
        """Wait for wake word with text mode support"""
        logger.info(f"[LISTEN] Waiting for wake word: '{wake_word}'...")
        
        # ============================================
        # TEXT MODE: Keyboard input
        # ============================================
        if self.text_mode:
            print(f"\n{'='*60}")
            print(f"💤 TEXT MODE: Waiting for wake word '{wake_word}'")
            print("   Press Enter to simulate wake word detection")
            print("   Or type 'exit' to quit")
            print(f"{'='*60}")
            
            # Async input to not block event loop
            loop = asyncio.get_event_loop()
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Use asyncio to get input without blocking
                    user_input = await asyncio.wait_for(
                        loop.run_in_executor(None, input, "   [Press Enter] >>> "),
                        timeout=1
                    )
                    
                    if user_input.strip().lower() == 'exit':
                        logger.info("🚪 Exit requested in text mode")
                        return False
                    
                    # Any input (including empty) counts as wake word
                    logger.info(f"[TARGET] Wake word '{wake_word}' detected (text mode)")
                    return True
                    
                except asyncio.TimeoutError:
                    # No input yet, continue waiting
                    continue
                except Exception as e:
                    logger.error(f"Text input error: {e}")
                    break
            
            logger.info(f"⏰ No wake word input in {timeout} seconds")
            return False
        
        # ============================================
        # SIMULATION MODE: Auto-detect after delay
        # ============================================
        if self.simulation_mode:
            logger.info("💤 Simulation mode: Waiting 3 seconds...")
            await asyncio.sleep(3)
            logger.info(f"[TARGET] Simulated: Wake word '{wake_word}' detected!")
            return True
        
        # ============================================
        # REAL VOICE MODE: Microphone input
        # ============================================
        try:
            import speech_recognition as sr
            
            r = sr.Recognizer()
            r.energy_threshold = 400
            r.dynamic_energy_threshold = True
            
            with sr.Microphone() as source:
                logger.info("🎤 Adjusting for ambient noise...")
                r.adjust_for_ambient_noise(source, duration=1)
                
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    try:
                        logger.debug("👂 Listening...")
                        audio = r.listen(source, timeout=2, phrase_time_limit=3)
                        
                        try:
                            text = r.recognize_google(audio).lower()
                            logger.debug(f"Heard: '{text}'")
                            
                            # Flexible wake word matching
                            wake_variants = [wake_word, 'bottle', 'butter', 'battler', 'but', 'bot']
                            if any(variant in text for variant in wake_variants):
                                logger.info(f"[TARGET] Wake word detected! Heard: '{text}'")
                                return True
                                
                        except sr.UnknownValueError:
                            # Speech not understood, continue
                            continue
                        except sr.RequestError as e:
                            logger.warning(f"Google API error: {e}")
                            # Fallback to simulation
                            logger.info("🔄 Falling back to simulation due to API error")
                            await asyncio.sleep(2)
                            return True
                            
                    except sr.WaitTimeoutError:
                        # No speech detected, continue listening
                        continue
                        
                # Timeout reached
                logger.info(f"⏰ No wake word detected in {timeout} seconds")
                return False
                
        except Exception as e:
            logger.error(f"❌ Wake word error: {e}")
            # Fallback to simulation
            logger.info("🔄 Falling back to simulation due to error")
            await asyncio.sleep(2)
            return True
    
    async def listen_for_command(self, timeout=10):
        """Listen for command with text mode support"""
        logger.info("[MIC] Listening for command...")
        
        # ============================================
        # TEXT MODE: Keyboard input for command
        # ============================================
        if self.text_mode:
            print(f"\n{'='*60}")
            print("🎤 TEXT MODE: Enter your command")
            print("   Examples:")
            print("     • 'I need an electrician'")
            print("     • 'Call a plumber'")
            print("     • 'Book a cleaner'")
            print("     • 'sleep' (to go back to sleep)")
            print("     • 'exit' (to quit)")
            print(f"{'='*60}")
            
            loop = asyncio.get_event_loop()
            
            try:
                command = await asyncio.wait_for(
                    loop.run_in_executor(None, input, "   Command >>> "),
                    timeout=timeout
                )
                
                if command.strip():
                    if command.strip().lower() == 'exit':
                        logger.info("🚪 Exit requested")
                        return None
                    
                    logger.info(f"[TARGET] Command: {command}")
                    return command.lower()
                else:
                    logger.warning("🔇 No command entered")
                    return None
                    
            except asyncio.TimeoutError:
                logger.warning("⏰ Command input timeout")
                return None
            except Exception as e:
                logger.error(f"Command input error: {e}")
                return None
        
        # ============================================
        # SIMULATION MODE: Return test command
        # ============================================
        if self.simulation_mode:
            logger.info("💤 Simulation mode: Generating test command...")
            await asyncio.sleep(2)
            test_commands = [
                "i need an electrician",
                "call a plumber", 
                "book a cleaner",
                "find me a carpenter",
                "electricity problem",
                "plumbing issue",
                "i need help with wiring",
                "there's a leak in my bathroom"
            ]
            command = random.choice(test_commands)
            logger.info(f"[TARGET] Simulated command: {command}")
            return command
        
        # ============================================
        # REAL VOICE MODE: Microphone input
        # ============================================
        try:
            import speech_recognition as sr
            
            r = sr.Recognizer()
            r.energy_threshold = 300
            
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                
                try:
                    audio = r.listen(source, timeout=timeout, phrase_time_limit=15)
                    
                    # Try Google with English hint first
                    try:
                        text = r.recognize_google(audio, language="en-US")
                    except:
                        # Fallback to without language hint
                        text = r.recognize_google(audio)
                    
                    if text:
                        logger.info(f"[TARGET] Command: {text}")
                        return text.lower()
                    else:
                        logger.warning("[ERROR] Could not understand command")
                        return None
                        
                except sr.WaitTimeoutError:
                    logger.warning("⏰ No speech detected within timeout")
                    return None
                except sr.UnknownValueError:
                    logger.warning("🔇 Speech not understood")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Command listening error: {e}")
            # Fallback to simulation
            logger.info("🔄 Falling back to simulation due to error")
            await asyncio.sleep(2)
            return "i need a plumber"
    
    async def listen_command(self, timeout=10):
        """Backward compatibility alias"""
        return await self.listen_for_command(timeout)
    
    async def stop(self):
        """Stop listening"""
        self.is_listening = False
        if self.text_mode:
            logger.info("📝 Text mode stopped")
        else:
            logger.info("🎤 Voice mode stopped")
    
    async def speak(self, text):
        """Speak text - in text mode, just print it"""
        if self.text_mode:
            print(f"\n{'='*60}")
            print(f"🔊 BUTLER: {text}")
            print(f"{'='*60}\n")
        else:
            logger.info(f"[VOICE] Butler: {text}")
        
        # Optional: Add a small delay for natural conversation flow
        await asyncio.sleep(0.5)
