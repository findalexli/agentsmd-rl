#!/bin/bash
set -e

cd /workspace/civitai

# Apply the gold patch by modifying the blocklist JSON directly
# The patch adds "civit", "c1vit", "civ1t", "c1v1t" to the partial blocklist

# Use python to modify the JSON file
python3 <<'PYTHON_SCRIPT'
import json
import os

blocklist_path = "/workspace/civitai/src/utils/blocklist-username.json"

with open(blocklist_path, "r") as f:
    blocklist = json.load(f)

# Add civit variants to partial blocklist
new_partial_items = ["civit", "c1vit", "civ1t", "c1v1t"]
for item in new_partial_items:
    if item not in blocklist["partial"]:
        blocklist["partial"].append(item)

with open(blocklist_path, "w") as f:
    json.dump(blocklist, f, indent=2)

print(f"Updated blocklist: {blocklist['partial'][:10]}")
PYTHON_SCRIPT

# Verify the patch was applied
grep -q "civit" src/utils/blocklist-username.json && echo "Patch applied successfully"