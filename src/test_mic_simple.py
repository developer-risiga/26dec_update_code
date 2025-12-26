# test_mic_simple.py
import speech_recognition as sr
import time

def test_microphone():
    print("🔊 TESTING MICROPHONE - SPEAK LOUDLY")
    print("="*50)
    
    r = sr.Recognizer()
    
    # Try with no device index (let it choose)
    try:
        print("\n1. Testing with DEFAULT microphone...")
        with sr.Microphone() as source:  # NO device_index
            print("   Adjusting for noise (stay silent)...")
            r.adjust_for_ambient_noise(source, duration=2)
            print(f"   Energy threshold: {r.energy_threshold}")
            
            print("\n   ⚠️ SPEAK NOW! Say 'Hello'")
            audio = r.listen(source, timeout=5, phrase_time_limit=3)
            print("   ✓ Got audio!")
            
            text = r.recognize_google(audio)
            print(f"   ✅ Recognized: '{text}'")
            return True
            
    except sr.WaitTimeoutError:
        print("   ✗ No speech detected")
    except sr.UnknownValueError:
        print("   ✗ Speech not understood (but microphone works!)")
        return True  # Mic works even if speech not understood
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    return False

if __name__ == "__main__":
    if test_microphone():
        print("\n🎉 MICROPHONE IS WORKING!")
    else:
        print("\n❌ MICROPHONE NOT DETECTING SPEECH")
        print("\nTroubleshooting steps:")
        print("1. Check if microphone is plugged in")
        print("2. Run: 'alsamixer' to check volume levels")
        print("3. Press F4 to switch to capture devices")
        print("4. Increase microphone volume (MM means muted)")
