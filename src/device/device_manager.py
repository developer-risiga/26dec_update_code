# device/device_manager.py
import logging
import subprocess
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DeviceManager:
    def __init__(self):
        self.is_raspberry_pi = self._detect_raspberry_pi()
        self.display_available = False
        self.audio_available = False
        self._initialize_hardware()
    
    def _detect_raspberry_pi(self) -> bool:
        """Detect if running on Raspberry Pi"""
        try:
            with open('/proc/device-tree/model', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
    
    def _initialize_hardware(self):
        """Initialize all hardware components"""
        logger.info("Initializing hardware components")
        self.display_available = self._check_display()
        self.audio_available = self._check_audio()
        
        if self.is_raspberry_pi:
            self._optimize_raspberry_pi()
    
    def _check_display(self) -> bool:
        """Check if display is available"""
        try:
            return subprocess.run(['which', 'xset'], capture_output=True).returncode == 0
        except:
            return False
    
    def _check_audio(self) -> bool:
        """Check if audio hardware is available"""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            device_count = p.get_device_count()
            p.terminate()
            return device_count > 0
        except:
            return False
    
    def _optimize_raspberry_pi(self):
        """Optimize Raspberry Pi for voice processing"""
        try:
            # Set CPU governor to performance
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor', 'w') as f:
                f.write('performance')
            logger.info("Raspberry Pi optimized for voice processing")
        except Exception as e:
            logger.warning(f"Could not optimize Raspberry Pi: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            'platform': 'raspberry_pi' if self.is_raspberry_pi else 'unknown',
            'display_available': self.display_available,
            'audio_available': self.audio_available
        }

# Global instance
device_manager = DeviceManager()