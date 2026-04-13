#!/bin/bash
# Sample solution - install requests properly
set -e

cd /workspace/requests

# Ensure requests is installed
pip install -e . -q

echo "Solution applied"
