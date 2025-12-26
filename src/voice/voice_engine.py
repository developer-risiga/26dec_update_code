"""
SIMPLE PRODUCTION Voice Engine - Working Version
"""

import asyncio
import speech_recognition as sr
import subprocess
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("voice")

class SimpleVoiceEngine:
    """Simple working voice engine"""
    
    def __init__(self):
        self.initialized = False
        
        # Load USB config
        try:
            from usb_mic_config import USB_MIC_INDEX, USB_MIC_ENERGY_THRESHOLD
            self.mic_index = USB_MIC_INDEX
            self.energy_threshold = USB_MIC_ENERGY_THRESHOLD
            logger.info(f"✅ USB Mic: index={USB_MIC_INDEX}, threshold={USB_MIC_ENERGY_THRESHOLD}")
        except ImportError:
            self.mic_index = 0
            self.energy_threshold = 350
            logger.warning("⚠️ Using defaults")
        
        # Speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = self.energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        
        self.wake_word = "butler"
    
    async def initialize(self, config=None):
        """Simple initialization"""
        logger.info("🚀 Initializing Simple Voice Engine...")
        
        try:
            # Set HDMI audio
            subprocess.run(['pactl', 'set-default-sink', 
                          'alsa_output.platform-107c706400.hdmi.hdmi-stereo'], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Set max volume
            subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '100%'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Test espeak
            result = subprocess.run(['which', 'espeak'], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.espeak_available = result.returncode == 0
            
            if not self.espeak_available:
                logger.info("Installing espeak...")
                subprocess.run(['sudo', 'apt', 'install', '-y', 'espeak'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.espeak_available = True
            
            self.initialized = True
            logger.info("✅ Simple Voice Engine ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def speak(self, text: str):
        """Simple speech"""
        if not text:
            return
            
        logger.info(f"🔊 Speaking: {text}")
        
        # Play start beep
        self._play_beep(783.99, 0.1)
        
        # Use espeak
        if self.espeak_available:
            subprocess.run(['espeak', '-s', '150', text],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._play_beep(659.25, 0.2)  # Success beep
        else:
            logger.info(f"📢 [Voice]: {text}")
            self._play_beep(554.37, 0.25)  # Notification beep
    
    def _play_beep(self, freq, duration):
        """Play a simple beep"""
        try:
            # Generate beep with sox
            subprocess.run([
                'sox', '-n', '-r', '44100', '-b', '16',
                '/tmp/beep.wav', 'synth', str(duration),
                'sine', str(freq), 'vol', '0.3'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Play it
            subprocess.run([
                'paplay', '--device=alsa_output.platform-107c706400.hdmi.hdmi-stereo',
                '/tmp/beep.wav'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Cleanup
            os.remove('/tmp/beep.wav')
            
        except Exception as e:
            logger.debug(f"⚠️ Beep failed: {e}")
    
    async def wait_for_wake_word(self):
        """Wait for wake word"""
        logger.info(f"👂 Listening for '{self.wake_word}'...")
        return True
    
    async def listen_command(self):
        """Listen for command"""
        try:
            logger.info("🎤 Listening...")
            
            with sr.Microphone(device_index=self.mic_index) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=4)
            
            text = self.recognizer.recognize_google(audio)
            if text:
                logger.info(f"✅ Command: {text}")
                return text
            
            return ""
            
        except Exception as e:
            logger.error(f"❌ Listen error: {e}")
            return ""

# Export
VoiceEngine = SimpleVoiceEngine

async def test():
    print("🔊 Testing Simple Voice Engine...")
    
    engine = SimpleVoiceEngine()
    if await engine.initialize():
        print("✅ Engine ready")
        
        # Test beeps
        print("\n🎵 Testing beeps...")
        for freq, name in [(523, "Start"), (659, "Success"), (440, "Notify")]:
            print(f"  {name} beep...")
            engine._play_beep(freq, 0.2)
            await asyncio.sleep(0.3)
        
        # Test speech
        print("\n🗣️  Testing speech...")
        await engine.speak("Simple voice engine working")
        await asyncio.sleep(1)
        
        await engine.speak("Ready for Butler")
        
        print("\n✅ Test complete!")
    else:
        print("❌ Engine failed")

if __name__ == "__main__":
    asyncio.run(test())
