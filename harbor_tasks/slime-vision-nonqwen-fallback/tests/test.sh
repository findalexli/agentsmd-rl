#!/usr/bin/env bash
set +e

REPO_DIR="/workspace/slime"
cd "$REPO_DIR"

REWARD=0
add() { REWARD=$(python3 -c "print(round($REWARD + $1, 4))"); }

# ── GATE (0.00): Syntax check ──────────────────────────────────────────────
# [pr_diff] (0.00): All changed files must be valid Python
for f in slime/utils/processing_utils.py slime/backends/megatron_utils/actor.py slime/rollout/sglang_rollout.py slime_plugins/megatron_bridge/glm4v_moe.py; do
    if [ -f "$f" ] && ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "GATE FAILED: syntax error in $f"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"structural":0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done
echo "GATE PASS: all files parse"

# ── Behavioral fail-to-pass (0.30): process_vision_info with base64 image ──
# [pr_diff] (0.30): process_vision_info must not crash when qwen_vl_utils is unavailable;
#   must handle base64-encoded images and return them as PIL Images
BEHAVIORAL_1=$(python3 -c "
import base64, io, sys
from PIL import Image
from unittest.mock import MagicMock

# Create a small test image and encode as base64
img = Image.new('RGB', (8, 8), color='red')
buf = io.BytesIO()
img.save(buf, format='PNG')
img_b64 = base64.b64encode(buf.getvalue()).decode()

messages = [
    {'role': 'user', 'content': [
        {'type': 'image', 'image': img_b64},
        {'type': 'text', 'text': 'Describe this image.'},
    ]}
]

processor = MagicMock()
processor.image_processor.patch_size = 14

from slime.utils.processing_utils import process_vision_info
result = process_vision_info(messages, processor)

assert isinstance(result, dict), f'Expected dict, got {type(result)}'
assert 'images' in result, 'Missing images key'
assert 'videos' in result, 'Missing videos key'
imgs = result['images']
assert imgs is not None, 'images should not be None'
assert isinstance(imgs, (list, tuple)), f'images should be list/tuple, got {type(imgs)}'
assert len(imgs) >= 1, f'Expected >=1 image, got {len(imgs)}'
assert isinstance(imgs[0], Image.Image), f'Expected PIL Image, got {type(imgs[0])}'
assert imgs[0].size == (8, 8), f'Wrong image size: {imgs[0].size}'
print('PASS')
" 2>&1) || true

if [ "$BEHAVIORAL_1" = "PASS" ]; then
    add 0.30
    echo "PASS (0.30): process_vision_info handles base64 image without qwen_vl_utils"
else
    echo "FAIL (0.30): process_vision_info handles base64 image without qwen_vl_utils"
    echo "  Output: $BEHAVIORAL_1"
fi

# ── Behavioral fail-to-pass (0.15): process_vision_info with data: URI ─────
# [pr_diff] (0.15): process_vision_info must handle data:image/...;base64,... URIs
BEHAVIORAL_2=$(python3 -c "
import base64, io, sys
from PIL import Image
from unittest.mock import MagicMock

img = Image.new('RGB', (4, 4), color='blue')
buf = io.BytesIO()
img.save(buf, format='PNG')
data_uri = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

messages = [
    {'role': 'user', 'content': [
        {'type': 'image', 'image': data_uri},
    ]}
]

processor = MagicMock()
processor.image_processor.patch_size = 14

from slime.utils.processing_utils import process_vision_info
result = process_vision_info(messages, processor)

imgs = result.get('images')
assert imgs is not None, 'images should not be None for data: URI'
assert len(imgs) >= 1, f'Expected >=1 image, got {len(imgs)}'
assert isinstance(imgs[0], Image.Image), f'Expected PIL Image, got {type(imgs[0])}'
assert imgs[0].size == (4, 4), f'Wrong size: {imgs[0].size}'
print('PASS')
" 2>&1) || true

if [ "$BEHAVIORAL_2" = "PASS" ]; then
    add 0.15
    echo "PASS (0.15): process_vision_info handles data: URI images"
else
    echo "FAIL (0.15): process_vision_info handles data: URI images"
    echo "  Output: $BEHAVIORAL_2"
fi

# ── Behavioral fail-to-pass (0.15): process_vision_info with PIL Image ─────
# [pr_diff] (0.15): process_vision_info must pass through PIL Image objects
BEHAVIORAL_3=$(python3 -c "
from PIL import Image
from unittest.mock import MagicMock

img = Image.new('RGB', (6, 6), color='green')
messages = [
    {'role': 'user', 'content': [
        {'type': 'image', 'image': img},
    ]},
    {'role': 'user', 'content': 'text only — should be skipped'},
    {'role': 'user', 'content': [
        {'type': 'text', 'text': 'no images here'},
    ]},
]

processor = MagicMock()
processor.image_processor.patch_size = 14

from slime.utils.processing_utils import process_vision_info
result = process_vision_info(messages, processor)

imgs = result.get('images')
assert imgs is not None, 'images should not be None'
assert len(imgs) == 1, f'Expected 1 image, got {len(imgs)}'
assert isinstance(imgs[0], Image.Image), f'Expected PIL Image, got {type(imgs[0])}'
assert imgs[0].size == (6, 6), f'Wrong size: {imgs[0].size}'
print('PASS')
" 2>&1) || true

if [ "$BEHAVIORAL_3" = "PASS" ]; then
    add 0.15
    echo "PASS (0.15): process_vision_info handles PIL Image objects"
else
    echo "FAIL (0.15): process_vision_info handles PIL Image objects"
    echo "  Output: $BEHAVIORAL_3"
fi

# ── Behavioral fail-to-pass (0.10): process_vision_info multiple images ────
# [pr_diff] (0.10): process_vision_info must extract multiple images across messages
BEHAVIORAL_4=$(python3 -c "
import base64, io
from PIL import Image
from unittest.mock import MagicMock

def make_b64(color, size):
    img = Image.new('RGB', size, color=color)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()

messages = [
    {'role': 'user', 'content': [
        {'type': 'image', 'image': make_b64('red', (4, 4))},
        {'type': 'text', 'text': 'First image.'},
    ]},
    {'role': 'user', 'content': [
        {'type': 'image', 'image': make_b64('blue', (8, 8))},
        {'type': 'image', 'image': Image.new('RGB', (2, 2), color='yellow')},
    ]},
]

processor = MagicMock()
processor.image_processor.patch_size = 14

from slime.utils.processing_utils import process_vision_info
result = process_vision_info(messages, processor)

imgs = result.get('images')
assert imgs is not None, 'images should not be None'
assert len(imgs) == 3, f'Expected 3 images, got {len(imgs)}'
for i, im in enumerate(imgs):
    assert isinstance(im, Image.Image), f'Image {i} is not PIL Image: {type(im)}'
print('PASS')
" 2>&1) || true

if [ "$BEHAVIORAL_4" = "PASS" ]; then
    add 0.10
    echo "PASS (0.10): process_vision_info extracts multiple images across messages"
else
    echo "FAIL (0.10): process_vision_info extracts multiple images across messages"
    echo "  Output: $BEHAVIORAL_4"
fi

# ── Pass-to-pass (0.10): build_processor_kwargs still works ────────────────
# [pr_diff] (0.10): Existing utility must not break
P2P_1=$(python3 -c "
from slime.utils.processing_utils import build_processor_kwargs

# No multimodal inputs
result = build_processor_kwargs(None)
assert isinstance(result, dict), f'Expected dict, got {type(result)}'

# With multimodal inputs
result2 = build_processor_kwargs({'images': ['fake']})
assert 'images' in result2
assert result2['images_kwargs']['return_tensors'] == 'pt'
print('PASS')
" 2>&1) || true

if [ "$P2P_1" = "PASS" ]; then
    add 0.10
    echo "PASS (0.10): build_processor_kwargs still works"
else
    echo "FAIL (0.10): build_processor_kwargs still works"
    echo "  Output: $P2P_1"
fi

# ── Pass-to-pass (0.05): encode_image_for_rollout_engine still works ───────
# [pr_diff] (0.05): Image encoding utility must remain functional
P2P_2=$(python3 -c "
from PIL import Image
from slime.utils.processing_utils import encode_image_for_rollout_engine

img = Image.new('RGB', (4, 4), color='red')
result = encode_image_for_rollout_engine(img)
assert result.startswith('data:image/png;base64,'), f'Bad prefix: {result[:40]}'
assert len(result) > 30, 'Encoded string too short'
print('PASS')
" 2>&1) || true

if [ "$P2P_2" = "PASS" ]; then
    add 0.05
    echo "PASS (0.05): encode_image_for_rollout_engine still works"
else
    echo "FAIL (0.05): encode_image_for_rollout_engine still works"
    echo "  Output: $P2P_2"
fi

# ── Structural (0.10): actor.py handles numpy arrays ──────────────────────
# [pr_diff] (0.10): multimodal_train_inputs must handle np.ndarray values
# WHY AST: actor.py requires ray, torch.distributed, megatron — cannot import
STRUCTURAL_1=$(python3 -c "
import ast

with open('slime/backends/megatron_utils/actor.py') as f:
    source = f.read()
    tree = ast.parse(source)

# Check for numpy array handling: isinstance(..., np.ndarray) OR torch.from_numpy OR np.asarray
# Any of these patterns indicates proper numpy handling
found_isinstance = False
found_from_numpy = False
found_numpy_import = False

for node in ast.walk(tree):
    # Check for numpy import (import numpy or from numpy)
    if isinstance(node, ast.Import):
        for alias in node.names:
            if 'numpy' in alias.name:
                found_numpy_import = True
    if isinstance(node, ast.ImportFrom) and node.module and 'numpy' in node.module:
        found_numpy_import = True

    # Check for isinstance(..., np.ndarray) or isinstance(..., numpy.ndarray)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'isinstance':
        if len(node.args) >= 2:
            arg2 = node.args[1]
            if isinstance(arg2, ast.Attribute) and arg2.attr == 'ndarray':
                found_isinstance = True
            # Also accept tuple form isinstance(v, (np.ndarray, ...))
            if isinstance(arg2, ast.Tuple):
                for elt in arg2.elts:
                    if isinstance(elt, ast.Attribute) and elt.attr == 'ndarray':
                        found_isinstance = True

    # Check for torch.from_numpy(...) or similar conversion calls
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'from_numpy':
            found_from_numpy = True
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'as_tensor':
            found_from_numpy = True  # torch.as_tensor handles numpy too

assert found_numpy_import, 'No numpy import found in actor.py'
assert found_isinstance or found_from_numpy, 'No numpy array handling found (isinstance or from_numpy/as_tensor)'
print('PASS')
" 2>&1) || true

if [ "$STRUCTURAL_1" = "PASS" ]; then
    add 0.10
    echo "PASS (0.10): actor.py handles numpy arrays"
else
    echo "FAIL (0.10): actor.py handles numpy arrays"
    echo "  Output: $STRUCTURAL_1"
fi

# ── Structural (0.05): sglang_rollout.py safe multimodal access ────────────
# [pr_diff] (0.05): Safe access pattern for multimodal_inputs dict
# WHY AST: sglang_rollout.py requires sglang async server internals — cannot import
STRUCTURAL_2=$(python3 -c "
import ast

with open('slime/rollout/sglang_rollout.py') as f:
    source = f.read()
    tree = ast.parse(source)

# Accept any safe access pattern for images key:
#   .get('images')  OR  'images' in ...  OR  try/except KeyError
found_safe = False
for node in ast.walk(tree):
    # Pattern 1: .get('images')
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'get':
            for arg in node.args:
                if isinstance(arg, ast.Constant) and arg.value == 'images':
                    found_safe = True
    # Pattern 2: 'images' in ...
    if isinstance(node, ast.Compare):
        if isinstance(node.left, ast.Constant) and node.left.value == 'images':
            for op in node.ops:
                if isinstance(op, ast.In):
                    found_safe = True

assert found_safe, 'No safe access pattern for images key found in sglang_rollout.py'
print('PASS')
" 2>&1) || true

if [ "$STRUCTURAL_2" = "PASS" ]; then
    add 0.05
    echo "PASS (0.05): sglang_rollout.py uses safe multimodal access"
else
    echo "FAIL (0.05): sglang_rollout.py uses safe multimodal access"
    echo "  Output: $STRUCTURAL_2"
fi

# ── Final score ────────────────────────────────────────────────────────────
echo ""
echo "Total reward: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

behavioral=$(python3 -c "
b1 = 0.30 if '$BEHAVIORAL_1' == 'PASS' else 0.0
b2 = 0.15 if '$BEHAVIORAL_2' == 'PASS' else 0.0
b3 = 0.15 if '$BEHAVIORAL_3' == 'PASS' else 0.0
b4 = 0.10 if '$BEHAVIORAL_4' == 'PASS' else 0.0
print(round(b1 + b2 + b3 + b4, 4))
")
regression=$(python3 -c "
p1 = 0.10 if '$P2P_1' == 'PASS' else 0.0
p2 = 0.05 if '$P2P_2' == 'PASS' else 0.0
print(round(p1 + p2, 4))
")
structural=$(python3 -c "
s1 = 0.10 if '$STRUCTURAL_1' == 'PASS' else 0.0
s2 = 0.05 if '$STRUCTURAL_2' == 'PASS' else 0.0
print(round(s1 + s2, 4))
")

python3 -c "
import json
print(json.dumps({
    'reward': $REWARD,
    'behavioral': $behavioral,
    'regression': $regression,
    'structural': $structural,
}))
" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
