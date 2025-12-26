# audio_fix.py - Fix ALSA audio output issues
import os
import pyaudio

def fix_audio_output():
    print("=== AUDIO OUTPUT FIX ===")
    
    # Check current ALSA configuration
    print("1. Checking ALSA configuration...")
    os.system("cat /proc/asound/cards")
    
    # Set default output device
    print("\n2. Setting default output to HDMI (card 0)...")
    
    # Create .asoundrc configuration
    asound_config = """
defaults.pcm.card 0
defaults.ctl.card 0
pcm.!default {
    type plug
    slave.pcm "hw:0,0"
}
ctl.!default {
    type hw
    card 0
}
"""
    
    with open(os.path.expanduser("~/.asoundrc"), "w") as f:
        f.write(asound_config)
    
    print("✅ Created ~/.asoundrc configuration")
    
    # Test PyAudio
    print("\n3. Testing PyAudio output devices...")
    p = pyaudio.PyAudio()
    
    print("Available output devices:")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxOutputChannels'] > 0:
            print(f"  [{i}] {dev['name']} - Outputs: {dev['maxOutputChannels']}")
    
    p.terminate()
    print("\n✅ Audio configuration updated. Please restart your Butler.")
    
    # Test simple playback
    print("\n4. Testing audio playback...")
    test_cmd = "speaker-test -t sine -f 440 -c 2 -l 1"
    os.system(test_cmd)

if __name__ == "__main__":
    fix_audio_output()