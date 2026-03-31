#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="/workspace/slime"
cd "$REPO_DIR"

total=0.0
earned=0.0

add() { earned=$(python3 -c "print(round($earned + $1, 4))"); }

# ── GATE (0.00): Syntax check ──────────────────────────────────────────────
# [pr_diff] (0.00): File must be valid Python
if ! python3 -c "import ast; ast.parse(open('slime/rollout/on_policy_distillation.py').read())"; then
    echo "GATE FAILED: syntax error in on_policy_distillation.py"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ── Behavioral fail-to-pass (0.35): Payload includes image_data for multimodal samples ──
# [pr_diff] (0.35): reward_func must include encoded images in payload when sample has multimodal_inputs
BEHAVIORAL_1=$(python3 -c "
import asyncio
import json
import io
import base64
from unittest.mock import AsyncMock, patch, MagicMock
from PIL import Image

from slime.utils.types import Sample
from slime.rollout.on_policy_distillation import reward_func

# Create a small test image
img = Image.new('RGB', (4, 4), color='red')

# Create sample with multimodal inputs
sample = Sample(
    tokens=[1, 2, 3, 4, 5],
    multimodal_inputs={'images': [img]},
)

# Mock args
args = MagicMock()
args.rm_url = 'http://localhost:9999/v1/reward'

# Capture the payload sent to the server
captured_payload = {}

async def run_test():
    mock_resp = AsyncMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = AsyncMock(return_value={'reward': 0.0})

    mock_session = AsyncMock()
    mock_post_ctx = AsyncMock()
    mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_post_ctx.__aexit__ = AsyncMock(return_value=False)

    def capture_post(url, json=None):
        captured_payload.update(json or {})
        return mock_post_ctx

    mock_session.post = capture_post

    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch('aiohttp.ClientSession', return_value=mock_session_ctx):
        await reward_func(args, sample)

asyncio.run(run_test())

# Check that image_data was included in the payload
assert 'image_data' in captured_payload, 'image_data missing from payload'
assert isinstance(captured_payload['image_data'], list), 'image_data should be a list'
assert len(captured_payload['image_data']) == 1, 'image_data should have 1 entry'
# Verify it's a base64 data URI
assert captured_payload['image_data'][0].startswith('data:image/png;base64,'), 'image should be base64 PNG data URI'
print('PASS')
" 2>&1) || true

if [ "$BEHAVIORAL_1" = "PASS" ]; then
    add 0.35
    echo "PASS (0.35): Payload includes image_data for multimodal samples"
else
    echo "FAIL (0.35): Payload includes image_data for multimodal samples"
    echo "  Output: $BEHAVIORAL_1"
fi

# ── Behavioral fail-to-pass (0.30): Multiple images are each encoded ──
# [pr_diff] (0.30): Each image in multimodal_inputs is individually encoded
BEHAVIORAL_2=$(python3 -c "
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from PIL import Image

from slime.utils.types import Sample
from slime.rollout.on_policy_distillation import reward_func

# Create multiple test images of different colors
imgs = [Image.new('RGB', (4, 4), color=c) for c in ['red', 'green', 'blue']]

sample = Sample(
    tokens=[1, 2, 3],
    multimodal_inputs={'images': imgs},
)

args = MagicMock()
args.rm_url = 'http://localhost:9999/v1/reward'

captured_payload = {}

async def run_test():
    mock_resp = AsyncMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = AsyncMock(return_value={'reward': 0.0})

    mock_session = AsyncMock()
    mock_post_ctx = AsyncMock()
    mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_post_ctx.__aexit__ = AsyncMock(return_value=False)

    def capture_post(url, json=None):
        captured_payload.update(json or {})
        return mock_post_ctx

    mock_session.post = capture_post

    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch('aiohttp.ClientSession', return_value=mock_session_ctx):
        await reward_func(args, sample)

asyncio.run(run_test())

assert 'image_data' in captured_payload, 'image_data missing'
assert len(captured_payload['image_data']) == 3, f'Expected 3 images, got {len(captured_payload[\"image_data\"])}'

# Verify each is a unique base64 string (different images produce different encodings)
unique_encodings = set(captured_payload['image_data'])
assert len(unique_encodings) == 3, 'Each image should produce a unique encoding'
print('PASS')
" 2>&1) || true

if [ "$BEHAVIORAL_2" = "PASS" ]; then
    add 0.30
    echo "PASS (0.30): Multiple images are each encoded"
else
    echo "FAIL (0.30): Multiple images are each encoded"
    echo "  Output: $BEHAVIORAL_2"
fi

# ── Pass-to-pass (0.15): reward_func still works without multimodal inputs ──
# [pr_diff] (0.15): Text-only samples must not include image_data in payload
PASS_TO_PASS=$(python3 -c "
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from slime.utils.types import Sample
from slime.rollout.on_policy_distillation import reward_func

# Sample without multimodal inputs
sample = Sample(tokens=[1, 2, 3, 4, 5])

args = MagicMock()
args.rm_url = 'http://localhost:9999/v1/reward'

captured_payload = {}

async def run_test():
    mock_resp = AsyncMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = AsyncMock(return_value={'reward': 0.0})

    mock_session = AsyncMock()
    mock_post_ctx = AsyncMock()
    mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_post_ctx.__aexit__ = AsyncMock(return_value=False)

    def capture_post(url, json=None):
        captured_payload.update(json or {})
        return mock_post_ctx

    mock_session.post = capture_post

    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch('aiohttp.ClientSession', return_value=mock_session_ctx):
        await reward_func(args, sample)

asyncio.run(run_test())

assert 'image_data' not in captured_payload, 'image_data should NOT be in text-only payload'
assert 'input_ids' in captured_payload, 'input_ids should be in payload'
print('PASS')
" 2>&1) || true

if [ "$PASS_TO_PASS" = "PASS" ]; then
    add 0.15
    echo "PASS (0.15): Text-only samples work without image_data"
else
    echo "FAIL (0.15): Text-only samples work without image_data"
    echo "  Output: $PASS_TO_PASS"
fi

# ── Structural (0.10): encode_image_for_rollout_engine is imported ──
# [pr_diff] (0.10): The image encoding utility must be imported for use
STRUCTURAL_1=$(python3 -c "
import ast

with open('slime/rollout/on_policy_distillation.py') as f:
    tree = ast.parse(f.read())

# Check for import of encode_image_for_rollout_engine
found_import = False
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name == 'encode_image_for_rollout_engine':
                found_import = True
                break

# Justify AST: we need to verify the import exists separately from the runtime test,
# because a missing import would cause a different error (ImportError) vs missing logic
assert found_import, 'encode_image_for_rollout_engine not imported'
print('PASS')
" 2>&1) || true

if [ "$STRUCTURAL_1" = "PASS" ]; then
    add 0.10
    echo "PASS (0.10): encode_image_for_rollout_engine is imported"
else
    echo "FAIL (0.10): encode_image_for_rollout_engine is imported"
    echo "  Output: $STRUCTURAL_1"
fi

# ── Config-derived (0.10): reward_func remains async ──
# [agent_config] (0.10): "Doing blocking network calls without async handling" — .claude/skills/add-reward-function/SKILL.md:83
CONFIG_1=$(python3 -c "
import ast

with open('slime/rollout/on_policy_distillation.py') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'reward_func':
        print('PASS')
        break
else:
    print('FAIL')
" 2>&1) || true

if [ "$CONFIG_1" = "PASS" ]; then
    add 0.10
    echo "PASS (0.10): reward_func is async (agent config: no blocking network calls)"
else
    echo "FAIL (0.10): reward_func is async (agent config: no blocking network calls)"
    echo "  Output: $CONFIG_1"
fi

# ── Final score ─────────────────────────────────────────────────────────────
echo ""
echo "Total reward: $earned"
echo "$earned" > /logs/verifier/reward.txt

# Compute component scores for reward.json
behavioral=$(python3 -c "
b1 = 0.35 if '$BEHAVIORAL_1' == 'PASS' else 0.0
b2 = 0.30 if '$BEHAVIORAL_2' == 'PASS' else 0.0
print(round(b1 + b2, 4))
")
regression=$(python3 -c "print(0.15 if '$PASS_TO_PASS' == 'PASS' else 0.0)")
config=$(python3 -c "print(0.10 if '$CONFIG_1' == 'PASS' else 0.0)")
structural=$(python3 -c "print(0.10 if '$STRUCTURAL_1' == 'PASS' else 0.0)")

python3 -c "
import json
print(json.dumps({
    'reward': $earned,
    'behavioral': $behavioral,
    'regression': $regression,
    'config': $config,
    'structural': $structural,
}))
" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
