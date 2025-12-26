# src/confirmation.py
import speech_recognition as sr

def ask_confirmation(service: str) -> bool:
    """
    Ask user to confirm before booking
    Returns: True if confirmed, False if cancelled
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000
    
    print(f"\n{'='*60}")
    print(f"🔔 CONFIRMATION REQUIRED")
    print(f"Detected service: {service}")
    print(f"{'='*60}")
    
    print("🔊 System: 'क्या आप वाकई इस सेवा को बुक करना चाहते हैं?'")
    print("🎤 Please say 'हाँ' or 'नहीं'")
    
    # Try voice confirmation
    try:
        with sr.Microphone() as source:
            print("Listening for response...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            response = recognizer.recognize_google(audio, language="hi-IN")
            
            print(f"You said: '{response}'")
            
            # Check for confirmation
            response_lower = response.lower()
            confirm_words = ["हाँ", "हां", "yes", "हा", "ठीक", "सही"]
            deny_words = ["नहीं", "नाही", "no", "गलत", "रद्द"]
            
            if any(word in response_lower for word in confirm_words):
                print("✅ Confirmed! Proceeding with booking...")
                return True
            elif any(word in response_lower for word in deny_words):
                print("❌ Cancelled by user")
                return False
            else:
                print("⚠️ Didn't understand. Switching to text input...")
                # Fall through to text
                
    except Exception as e:
        print(f"⚠️ Voice error: {e}")
        # Fallback to text input
    
    # Text input fallback
    while True:
        response = input("\n📝 TEXT INPUT - Confirm booking? (y/n/haan/naheen): ").lower().strip()
        
        if response in ['y', 'yes', 'हाँ', 'हां', 'haan', '1']:
            print("✅ Text: Confirmed!")
            return True
        elif response in ['n', 'no', 'नहीं', 'naheen', 'न', '0']:
            print("❌ Text: Cancelled")
            return False
        else:
            print(f"⚠️ Invalid: '{response}'. Please enter y/n/haan/naheen")

# Test the function
if __name__ == "__main__":
    print("✅ confirmation.py loaded successfully!")
    result = ask_confirmation("test_service")
    print(f"Result: {result}")
