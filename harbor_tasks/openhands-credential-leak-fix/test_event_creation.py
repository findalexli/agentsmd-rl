import sys
sys.path.insert(0, '/workspace/OpenHands')
from openhands.sdk import MessageEvent, Message
from uuid import uuid4
from datetime import datetime

# Suppress banner
import os
os.environ['OPENHANDS_SUPPRESS_BANNER'] = '1'

secret_key = "gsk_abc123def456ghi789jkl012mno"

try:
    # Create with content containing secret
    msg = Message(role='user', content=f'Secret API key: {secret_key}')
    event = MessageEvent(
        id=str(uuid4()),
        timestamp=datetime.now().isoformat(),
        source='user',
        llm_message=msg,
        llm_response_id='resp-123',
    )
    print('Created event:', event)
    print('str(event):', str(event))
    print('Secret in str(event)?', secret_key in str(event))
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')