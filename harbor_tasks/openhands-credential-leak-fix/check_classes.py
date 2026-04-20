import sys
sys.path.insert(0, '/workspace/OpenHands')
import os
os.environ['OPENHANDS_SUPPRESS_BANNER'] = '1'

# Get all imports from the file
with open('/workspace/OpenHands/openhands/app_server/event_callback/event_callback_models.py') as f:
    content = f.read()

# Find all class definitions
import re
classes = re.findall(r'^class (\w+).*$', content, re.MULTILINE)
print('Classes in event_callback_models.py:')
for c in classes:
    print(f'  - {c}')