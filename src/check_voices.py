import pyttsx3

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Get all available voices
voices = engine.getProperty('voices')

print("Available voices on your system:")
print("=" * 50)

for i, voice in enumerate(voices):
    print(f"\nVoice #{i}:")
    print(f"  Name: {voice.name}")
    print(f"  ID: {voice.id}")
    print(f"  Languages: {voice.languages}")
    print(f"  Gender: {voice.gender}")
    print(f"  Age: {voice.age}")
