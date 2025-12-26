# usb_mic_config.py - PRODUCTION CONFIGURATION

# Your USB microphone is on Card 1 (device index 1 in speech_recognition)
# But in sounddevice it's device 0 (USB PnP Sound Device)

USB_MIC_INDEX = 1  # For speech_recognition.Microphone(device_index=1)
USB_MIC_ENERGY_THRESHOLD = 300  # Very sensitive

# Optional settings
USB_MIC_SAMPLE_RATE = 44100
USB_MIC_CHANNELS = 1  # MONO
USB_MIC_ALSA_DEVICE = "hw:1,0"  # ALSA device string

# Production print (FIXED - use correct variable names)
print("\n🔧 PRODUCTION USB CONFIGURATION")
print(f"   Microphone Index: {USB_MIC_INDEX}")
print(f"   Forced Threshold: {USB_MIC_ENERGY_THRESHOLD}")
print(f"   Sample Rate: {USB_MIC_SAMPLE_RATE}Hz")
print(f"   Channels: {USB_MIC_CHANNELS}")
print(f"   Timeout: 10s")
print(f"   Phrase Limit: 8s")
