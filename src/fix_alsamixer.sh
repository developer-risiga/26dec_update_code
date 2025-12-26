#!/bin/bash
echo "Fixing alsamixer and USB audio..."

# Kill any existing alsamixer
pkill alsamixer 2>/dev/null

# Open alsamixer with playback view for USB
echo "Opening alsamixer for USB playback..."
alsamixer -c 1 -V playback &

# Wait a moment
sleep 2

# Now fix audio levels from command line
echo "Setting USB audio levels..."
amixer -c 1 set Master 100% unmute
amixer -c 1 set PCM 100% unmute
amixer -c 1 set Speaker 100% unmute
amixer -c 1 set 'Auto Gain Control' off

echo "✅ Audio fixed. In alsamixer window:"
echo "   - You should see Master, PCM, Speaker"
echo "   - Use UP/DOWN arrows to adjust"
echo "   - Press 'M' if you see 'MM' (muted)"
