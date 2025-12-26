# pi_mic_fix.py - FOR USB MICROPHONE (Card 1)
import speech_recognition as sr

def get_pi_microphone():
    """For USB microphone on card 1"""
    print("🔧 Configuring USB microphone (card 1)...")
    
    # USB microphone should be device index 1 or 2
    # Try different indices
    for index in [1, 2, 0, 3]:
        try:
            print(f"\nTrying device index {index}...")
            
            with sr.Microphone(device_index=index) as source:
                r = sr.Recognizer()
                r.energy_threshold = 3000  # Lower for USB mic
                r.dynamic_energy_threshold = False
                
                print("  Adjusting for noise...")
                r.adjust_for_ambient_noise(source, duration=1)
                
                print(f"✅ USB microphone works at index {index}")
                return index
                
        except Exception as e:
            print(f"  ❌ Index {index} failed: {str(e)[:50]}")
            continue
    
    print("⚠️ Using default index 0")
    return 0

if __name__ == "__main__":
    idx = get_pi_microphone()
    print(f"\n🎤 Use: device_index={idx}")
