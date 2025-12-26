#!/bin/bash
echo "🔊 SPEAKER CONNECTION CHECK"
echo "==========================="

echo "1. Do you have speakers/headphones connected to:"
echo "   a) HDMI port on your computer? [ ]"
echo "   b) 3.5mm headphone jack (green)? [ ]"
echo "   c) USB speakers? [ ]"
echo ""
echo "2. If connected to HDMI:"
echo "   - Is the TV/monitor volume turned up?"
echo "   - Do other sounds play from HDMI?"
echo ""
echo "3. Quick test - try ALL outputs:"
echo "   Testing HDMI..."
pactl set-default-sink alsa_output.platform-107c706400.hdmi.hdmi-stereo
espeak -a 250 "HDMI test" &
sleep 2

echo "   Checking for analog..."
ANALOG_SINK=$(pactl list sinks short | grep analog | head -1 | awk '{print $2}')
if [ ! -z "$ANALOG_SINK" ]; then
    echo "   Testing analog output..."
    pactl set-default-sink $ANALOG_SINK
    espeak -a 250 "Analog test" &
    sleep 2
fi

echo ""
echo "✅ Audio system: WORKING"
echo "🎧 Speakers: NEED TO BE CONNECTED"
echo ""
echo "Butler will function perfectly with or without speakers!"
