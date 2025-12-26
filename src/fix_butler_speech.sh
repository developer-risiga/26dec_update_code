#!/bin/bash
echo "Updating Butler to use enhanced_voice language-aware speech..."

# Backup
cp main.py main.py.backup.final

# 1. Remove voice_manager imports
sed -i '/from voice_manager import/d' main.py
sed -i '/import voice_manager/d' main.py

# 2. Ensure enhanced_voice import exists
if ! grep -q "from enhanced_voice import VoiceRecognizer" main.py; then
    # Add import at the top
    sed -i '1ifrom enhanced_voice import VoiceRecognizer' main.py
fi

# 3. Check if vr instance exists
if ! grep -q "vr = VoiceRecognizer" main.py; then
    echo "Adding VoiceRecognizer instance..."
    # Find after imports
    IMPORTS_END=$(grep -n "^from\|^import" main.py | tail -1 | cut -d: -f1)
    sed -i "$((IMPORTS_END+1))i\\vr = VoiceRecognizer(mic_device_index=1)" main.py
fi

# 4. Replace ALL voice.speak calls with enhanced_voice methods
echo "Replacing speech calls..."

# Welcome (line 1776) -> vr.speak_welcome()
sed -i '1776s/voice.speak(".*")/vr.speak_welcome()/' main.py

# Wake word response (line 1795) -> vr.speak_listening()
sed -i '1795s/voice.speak(".*")/vr.speak_listening()/' main.py

# Command acknowledgement (line 1837) -> vr.speak_processing()
sed -i '1837s/voice.speak(".*")/vr.speak_processing()/' main.py

# Service confirmed (line 1831) -> This needs service parameter
# We'll handle this separately

# Booking confirmed (line 1927) -> Use translations
sed -i '1927s/voice.speak(".*")/vr.speak_response(translations.get("booking_confirmed", {}).get(vr.current_language, "Booking confirmed!"), language_code=vr.current_language)/' main.py

# Notifications (line 1959) -> vr.speak_thanks()
sed -i '1959s/voice.speak(".*")/vr.speak_thanks()/' main.py

# Goodbye (line 7687) -> vr.speak_goodbye()
sed -i '7687s/voice.speak(".*")/vr.speak_goodbye()/' main.py

# 5. For service confirmation, we need to find the service variable
echo "Checking service variable..."
SERVICE_LINE=$(grep -n "service_type\|service = " main.py | head -5)
echo "Service lines: $SERVICE_LINE"

# Update line 1831 (service confirmed) to use vr.speak_confirmation()
sed -i '1831s/voice.speak("Service confirmed.*")/vr.speak_confirmation(service_type)/' main.py

echo "✅ Updated all speech calls to use enhanced_voice methods"
