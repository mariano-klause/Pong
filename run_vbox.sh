#!/bin/bash
# Run Pong in VirtualBox with software rendering

# Force software rendering (no GPU needed)
export LIBGL_ALWAYS_SOFTWARE=1
export SDL_VIDEODRIVER=x11

# Ensure display is set
export DISPLAY=:0

# Run from venv
./venv/bin/python pong.py "$@"
