#!/bin/bash
echo "Adding voice to Butler at key points..."

# Backup
cp main.py main.py.backup.$(date +%s)

# Add voice at 7 key points using simple pattern matching
echo "1. Adding welcome voice..."
sed -i '/🔊 BUTLER VOICE ASSISTANT - PRODUCTION READY/a\    voice.speak("Hello, I am Butler. How can I help you today?")' main.py

echo "2. Adding wake word response..."
sed -i '/✅ WAKE WORD DETECTED!/a\    voice.speak("Yes, I am listening. What do you need?")' main.py

echo "3. Adding command acknowledgement..."
sed -i '/Heard: .*/{n;s/.*/    voice.speak("I understand. Processing your request.")/}' main.py

echo "4. Adding service confirmation..."
sed -i '/✅ Service detected:/a\    voice.speak("Service confirmed. Starting booking process.")' main.py

echo "5. Adding booking confirmation..."
sed -i '/✅ Booking confirmed!/{n;s/.*/    voice.speak("Booking confirmed. Your professional will arrive within two hours.")/}' main.py

echo "6. Adding notifications..."
sed -i '/📊 Notifications Sent:/a\    voice.speak("Notifications have been sent to your phone and email.")' main.py

echo "7. Adding goodbye..."
sed -i '/👋 Goodbye!/i\    voice.speak("Goodbye. Thank you for using Butler.")' main.py

echo ""
echo "✅ Voice added at 7 points!"
echo "Check: grep -c 'voice.speak' main.py"
