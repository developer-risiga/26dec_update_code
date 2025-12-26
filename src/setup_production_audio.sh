																																																																																																																																																																																																																																																																																																																																																																																																							#!/bin/bash
# Production Audio Setup for Ubuntu on Pi

echo "🔧 PRODUCTION AUDIO SETUP"
echo "=========================="

# 1. Stop interfering audio services
echo "1. Stopping audio servers..."
systemctl --user stop pipewire pipewire-pulse wireplumber 2>/dev/null || true
pkill -9 pipewire 2>/dev/null
pkill -9 pulseaudio 2>/dev/null

# 2. Start fresh PulseAudio
echo "2. Starting clean PulseAudio..."
pulseaudio --kill 2>/dev/null || true
sleep 2
pulseaudio --start --log-level=0
sleep 2

# 3. Set HDMI as default
echo "3. Setting HDMI as default audio..."
pactl set-default-sink alsa_output.platform-107c706400.hdmi.hdmi-stereo

# 4. Set volume to max
echo "4. Setting maximum volume..."
pactl set-sink-volume @DEFAULT_SINK@ 100%

# 5. Install required packages
echo "5. Installing required packages..."
sudo apt update
sudo apt install -y espeak espeak-ng sox alsa-utils pulseaudio-utils

# 6. Test audio
echo "6. Testing audio..."
speaker-test -t sine -f 1000 -l 1 > /dev/null 2>&1 && echo "✅ Audio test passed" || echo "⚠️ Audio test had issues"

echo "✅ PRODUCTION AUDIO SETUP COMPLETE"
