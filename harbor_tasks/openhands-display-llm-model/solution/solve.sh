#!/bin/bash
set -e
cd /workspace/OpenHands

# Apply all changes using Python
python3 /solution/apply_patch.py
