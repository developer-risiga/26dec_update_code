import pyttsx3
print("Testing basic text-to-speech...")
engine = pyttsx3.init()

# Try different drivers if 'sapi5' or 'nsss' don't work.
# Common ones: 'espeak', 'dummy'
# engine = pyttsx3.init('espeak')  # Try this if the default fails

print(f"Driver: {engine.getProperty('voice')}")
engine.say("Hello from Butler Assistant. Testing one two three.")
engine.runAndWait()
print("Test complete.")
