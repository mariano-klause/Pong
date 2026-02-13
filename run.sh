#!/bin/bash
# Run Pong with appropriate environment setup

# Set display if not already set (for WSL/SSH)
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
fi

# Uncomment for headless/VNC environments:
# export SDL_VIDEODRIVER=x11

# Run game
python pong.py "$@"
