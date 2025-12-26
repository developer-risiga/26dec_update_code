#!/usr/bin/env python3
import speech_recognition as sr
import time

print("=== BRUTAL SIMPLE TEST ===")
print("Testing if microphone works at ALL...")

r = sr.Recognizer()
# Set LOW threshold for testing
r.energy_threshold = 500

try:
    with sr.Microphone(device_index=0, sample_rate=44100) as source:
        print("Calibrating...")
        r.adjust_for_ambient_noise(source, duration=2)
        print(f"Threshold: {r.energy_threshold}")
        
        print("\n🎤 SAY SOMETHING LOUD RIGHT NOW!")
        print("You have 5 seconds...")
        
        try:
            audio = r.listen(source, timeout=5)
            print("✅ VOICE DETECTED!")
            
            # Try to recognize
            try:
                text = r.recognize_google(audio)
                print(f"   You said: {text}")
            except:
                print("   Voice detected but not understood")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            
except Exception as e:
    print(f"❌ SETUP ERROR: {e}")
