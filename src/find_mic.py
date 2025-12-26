import speech_recognition as sr

print("🔍 Finding your USB microphone...")
mics = sr.Microphone.list_microphone_names()
print("\nAvailable microphones:")
for i, name in enumerate(mics):
    print(f"  {i}: {name}")
    
# Look for USB in the names
print("\n🔧 Probable USB microphone indices:")
for i, name in enumerate(mics):
    if 'usb' in name.lower() or 'card 1' in name.lower() or 'pnp' in name.lower():
        print(f"  → USE THIS: device_index={i} - {name}")

print("\n🎯 Based on 'arecord -l', your USB mic should be device_index=1 or 2")
