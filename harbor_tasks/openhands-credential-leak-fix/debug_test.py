import sys
import os
sys.path.insert(0, '/workspace/OpenHands')
os.environ['OPENHANDS_SUPPRESS_BANNER'] = '1'

import asyncio
import logging
import io
from uuid import uuid4
from unittest.mock import Mock

# Import after env set
from openhands.app_server.event_callback.set_title_callback_processor import SetTitleCallbackProcessor
from openhands.sdk import MessageEvent, Message

# Capture log output
log_stream = io.StringIO()
handler = logging.StreamHandler(log_stream)
handler.setLevel(logging.INFO)
logger = logging.getLogger('openhands.app_server.event_callback.set_title_callback_processor')
logger.addHandler(handler)
original_level = logger.level
logger.setLevel(logging.INFO)

try:
    secret_key = 'sk-or-v1-abc123def456ghi789jkl012mno'
    msg = Message(role='user', content=f'API key: {secret_key}')
    event = MessageEvent(
        id=str(uuid4()),
        timestamp='2024-01-01T00:00:00',
        source='user',
        llm_message=msg,
        llm_response_id='resp-123',
    )

    mock_callback = Mock()
    mock_callback.id = 'test-title-callback-456'

    processor = SetTitleCallbackProcessor()
    conversation_id = uuid4()

    try:
        asyncio.run(processor(conversation_id, mock_callback, event))
    except Exception as e:
        print(f'Exception during processor: {type(e).__name__}: {e}')

    log_output = log_stream.getvalue()
    print(f'Log output length: {len(log_output)}')
    print(f'Log output: {repr(log_output)}')
    print(f'Secret in log: {secret_key in log_output}')
    print(f'<redacted> in log: {"<redacted>" in log_output}')
finally:
    logger.removeHandler(handler)
    handler.close()
    logger.setLevel(original_level)