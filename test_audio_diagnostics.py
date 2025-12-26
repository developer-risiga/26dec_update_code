# test_audio_diagnostics.py
import speech_recognition as sr
import pyaudio

print("🔍 AUDIO DIAGNOSTICS TOOL")
print("=" * 50)

# Test PyAudio
print("\n1. Testing PyAudio...")
try:
    p = pyaudio.PyAudio()
    print(f"✅ PyAudio version: {pyaudio.__version__}")
    print(f"✅ Audio devices found: {p.get_device_count()}")
    
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        print(f"  Device {i}: {dev_info['name']}")
        print(f"    Max Input Channels: {dev_info['maxInputChannels']}")
        print(f"    Default Sample Rate: {dev_info['defaultSampleRate']}")
    
    p.terminate()
except Exception as e:
    print(f"❌ PyAudio error: {e}")

# Test SpeechRecognition
print("\n2. Testing SpeechRecognition...")
try:
    print(f"✅ SpeechRecognition version: {sr.__version__}")
    
    # List microphones
    print("\nMicrophones detected by SpeechRecognition:")
    try:
        mics = sr.Microphone.list_microphone_names()
        for i, mic in enumerate(mics):
            print(f"  {i}: {mic}")
    except:
        print("  Could not list microphones")
    
except Exception as e:
    print(f"❌ SpeechRecognition error: {e}")

# Test actual microphone
print("\n3. Testing actual microphone input...")
try:
    with sr.Microphone() as source:
        r = sr.Recognizer()
        print("✅ Microphone opened successfully")
        
        # Test recording
        print("Recording 1 second test...")
        audio = r.listen(source, timeout=2, phrase_time_limit=1)
        
        # Check audio data
        audio_data = audio.get_wav_data()
        print(f"✅ Audio recorded: {len(audio_data)} bytes")
        
except Exception as e:
    print(f"❌ Microphone test failed: {e}")

print("\n" + "=" * 50)
print("DIAGNOSTICS COMPLETE")
print("=" * 50)