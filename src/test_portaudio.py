# test_portaudio.py - Test PortAudio configuration
import sounddevice as sd
import numpy as np
import time

print("🔊 PORT AUDIO CONFIGURATION TEST")
print("="*50)

# 1. List all devices
print("\n1. Available audio devices:")
devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"  {i}: {device['name']}")
    print(f"     Input channels: {device['max_input_channels']}")
    print(f"     Output channels: {device['max_output_channels']}")
    print(f"     Default sample rate: {device['default_samplerate']}")

# 2. Set default device
print("\n2. Setting default device to USB microphone...")
try:
    # Your USB mic is device 1 according to arecord -l
    sd.default.device = 1
    print(f"   Default device set to: {sd.default.device}")
except Exception as e:
    print(f"   Error: {e}")

# 3. Test recording
print("\n3. Testing recording (3 seconds)...")
try:
    duration = 3  # seconds
    samplerate = 44100
    
    print(f"   Recording {duration} seconds at {samplerate}Hz...")
    recording = sd.rec(int(duration * samplerate), 
                      samplerate=samplerate, 
                      channels=1,
                      dtype='float32')
    
    print("   ⏺️ Recording... Speak now!")
    sd.wait()  # Wait until recording is finished
    print("   ✅ Recording complete!")
    
    # Check if we got audio
    max_amplitude = np.max(np.abs(recording))
    print(f"   Max amplitude: {max_amplitude:.4f}")
    
    if max_amplitude > 0.01:  # If we got sound
        print("   🔊 Sound detected!")
    else:
        print("   🔇 No sound detected (might be silent)")
        
except Exception as e:
    print(f"   ❌ Recording error: {e}")

# 4. Test callback functionality
print("\n4. Testing callback functionality...")
def callback(indata, frames, time, status):
    if status:
        print(f"   Status: {status}")
    if np.any(indata):
        amplitude = np.max(np.abs(indata))
        if amplitude > 0.01:
            print(f"   🔊 Real-time audio: {amplitude:.4f}")

try:
    with sd.InputStream(callback=callback, channels=1, samplerate=44100):
        print("   ⏺️ Listening for 2 seconds...")
        time.sleep(2)
    print("   ✅ Callback test successful!")
except Exception as e:
    print(f"   ❌ Callback error: {e}")

print("\n" + "="*50)
print("PortAudio configuration complete!")
