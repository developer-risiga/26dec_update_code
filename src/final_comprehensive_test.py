import pyttsx3
from voice_manager import voice

print("="*60)
print("FINAL COMPREHENSIVE TEST")
print("="*60)

# Test 1: Check pyttsx3
print("\n1. Testing pyttsx3...")
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print(f"   ✅ pyttsx3: {len(voices)} voices found")
    
    # Check specific Indian voices
    test_voices = ['hindi', 'tamil', 'bengali']
    for v_test in test_voices:
        found = any(v_test in v.id.lower() for v in voices)
        print(f"   {'✅' if found else '❌'} {v_test}: {'Found' if found else 'Not found'}")
        
except Exception as e:
    print(f"   ❌ pyttsx3 error: {e}")

# Test 2: Check flite (voice_manager)
print("\n2. Testing flite (voice_manager)...")
try:
    print(f"   ✅ voice_manager imported successfully")
    print(f"   Voice settings: {voice.voice}, Speed: {voice.speed}")
    
    # Test speaking
    print("   Testing English speech...")
    voice.speak("Test message")
    
except Exception as e:
    print(f"   ❌ voice_manager error: {e}")

# Test 3: Test actual Hindi speech
print("\n3. Testing Hindi speech...")
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    for v in voices:
        if 'hindi' in v.id.lower():
            engine.setProperty('voice', v.id)
            print(f"   🔊 Speaking Hindi...")
            engine.say("हाँ, मैं सुन रहा हूँ")
            engine.runAndWait()
            print(f"   ✅ Hindi test successful!")
            break
except Exception as e:
    print(f"   ❌ Hindi speech error: {e}")

print("\n" + "="*60)
print("TEST COMPLETED")
print("="*60)
