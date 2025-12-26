# final_usb_test.py
import speech_recognition as sr
import time

print("=== FINAL USB MICROPHONE TEST ===")
print("")

# First, test what index is correct
print("Finding correct USB microphone index...")
mics = sr.Microphone.list_microphone_names()
print("\nAll available microphones:")
for i, name in enumerate(mics):
    print(f"  [{i}] {name}")

print("\nTesting index 1 (from usb_mic_config.py)...")
try:
    with sr.Microphone(device_index=1) as source:
        print("✅ Index 1 works!")
        
        r = sr.Recognizer()
        r.energy_threshold = 500  # From config
        
        print("Calibrating for 3 seconds...")
        r.adjust_for_ambient_noise(source, duration=3)
        print(f"Energy threshold after calibration: {r.energy_threshold}")
        
        # Cap if too high
        if r.energy_threshold > 1000:
            r.energy_threshold = 500
            print(f"Capped threshold to 500")
        
        print("\n🎤 Speak now! Say 'testing one two three'")
        print("Listening for 5 seconds...")
        
        try:
            audio = r.listen(source, timeout=7, phrase_time_limit=5)
            print("✅ Audio captured!")
            
            text = r.recognize_google(audio)
            print(f"✅ SUCCESS! Recognized: \"{text}\"")
            
        except sr.WaitTimeoutError:
            print("❌ No speech detected")
            print("Try speaking louder or checking mic connection")
        except sr.UnknownValueError:
            print("❌ Speech detected but not understood")
        except Exception as e:
            print(f"❌ Error during recognition: {e}")
            
except Exception as e:
    print(f"❌ Failed with index 1: {e}")
    
    # Try index 2
    print("\nTrying index 2...")
    try:
        with sr.Microphone(device_index=2) as source:
            print("✅ Index 2 works!")
    except:
        print("❌ Index 2 also failed")
