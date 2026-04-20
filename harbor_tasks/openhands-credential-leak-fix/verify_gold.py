import sys
import os
sys.path.insert(0, '/workspace/OpenHands')
os.environ['OPENHANDS_SUPPRESS_BANNER'] = '1'

import asyncio
import logging
import io
from uuid import uuid4
from unittest.mock import Mock

from openhands.app_server.event_callback.event_callback_models import LoggingCallbackProcessor

log_stream = io.StringIO()
handler = logging.StreamHandler(log_stream)
handler.setLevel(logging.INFO)
logger = logging.getLogger('openhands.app_server.event_callback.event_callback_models')
logger.addHandler(handler)
original_level = logger.level
logger.setLevel(logging.INFO)

try:
    secret_key = 'gsk_abc123def456ghi789jkl012mno'
    mock_event = Mock()
    mock_event.id = str(uuid4())
    mock_event.__str__ = lambda self: f"MessageEvent(content='secret: {secret_key}')"

    mock_callback = Mock()
    mock_callback.id = str(uuid4())

    processor = LoggingCallbackProcessor()
    conversation_id = uuid4()

    try:
        asyncio.run(processor(conversation_id, mock_callback, mock_event))
    except Exception as e:
        print(f'Exception: {type(e).__name__}')

    log_output = log_stream.getvalue()
    print(f'Log output: {repr(log_output)}')
    print(f'Secret in log: {secret_key in log_output}')
    print(f'<redacted> in log: {"<redacted>" in log_output}')
finally:
    logger.removeHandler(handler)