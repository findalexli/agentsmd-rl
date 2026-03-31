#!/usr/bin/env bash
set +e

SCORE=0
FAIL_DETAILS=""

add() {
    local w=$1 name=$2 ok=$3
    SCORE=$(python3 -c "print($SCORE + $w)")
    if [ "$ok" = "1" ]; then
        echo "PASS ($w): $name"
    else
        SCORE=$(python3 -c "print($SCORE - $w)")
        echo "FAIL ($w): $name"
        FAIL_DETAILS="$FAIL_DETAILS\nFAIL: $name"
    fi
}

TARGET="/repo/src/transformers/video_processing_utils.py"

# =============================================================================
# GATE: Syntax check — abort on failure
# =============================================================================
# [pr_diff] (0.00): File must be valid Python
echo "--- GATE: Syntax check ---"
if ! python3 -c "import py_compile; py_compile.compile('$TARGET', doraise=True)" 2>/dev/null; then
    echo "GATE FAIL: syntax error in video_processing_utils.py"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASS: syntax OK"

# =============================================================================
# Ensure PIL is NOT available for fail-to-pass tests
# =============================================================================
python3 -m pip uninstall -y Pillow pillow 2>/dev/null >/dev/null || true

# =============================================================================
# BEHAVIORAL: Fail-to-pass tests (0.60 total)
# =============================================================================
echo ""
echo "--- BEHAVIORAL: Fail-to-pass (no PIL) ---"

# [pr_diff] (0.30): Import module without PIL + verify class is real (not stub)
# Core bug: PILImageResampling unconditionally imported crashes without PIL.
# Combined with attribute check to prevent trivial stubs from scoring.
F2P1=0
if python3 -c "
import sys
# Confirm PIL is absent
try:
    import PIL
    print('ERROR: PIL unexpectedly available')
    sys.exit(1)
except ImportError:
    pass

from transformers.video_processing_utils import BaseVideoProcessor

# Anti-stub: verify real class attributes preserved
assert BaseVideoProcessor.rescale_factor == 1/255, f'wrong rescale_factor'
assert BaseVideoProcessor.model_input_names == ['pixel_values_videos'], 'wrong model_input_names'
assert BaseVideoProcessor.default_to_square is True, 'wrong default_to_square'
assert BaseVideoProcessor.return_metadata is False, 'wrong return_metadata'
print('Import + class attrs OK')
" 2>&1; then
    F2P1=1
fi
add 0.30 "Import without PIL + class attributes correct" $F2P1

# [pr_diff] (0.15): Module-level docstring constant preserved
# Catches stubs that define the class but delete module-level content.
F2P2=0
if python3 -c "
from transformers.video_processing_utils import BASE_VIDEO_PROCESSOR_DOCSTRING
assert isinstance(BASE_VIDEO_PROCESSOR_DOCSTRING, str), 'not a string'
assert 'do_resize' in BASE_VIDEO_PROCESSOR_DOCSTRING, 'missing do_resize'
assert 'do_normalize' in BASE_VIDEO_PROCESSOR_DOCSTRING, 'missing do_normalize'
assert 'resample' in BASE_VIDEO_PROCESSOR_DOCSTRING, 'missing resample'
assert len(BASE_VIDEO_PROCESSOR_DOCSTRING) > 500, f'too short: {len(BASE_VIDEO_PROCESSOR_DOCSTRING)}'
print(f'Module docstring OK ({len(BASE_VIDEO_PROCESSOR_DOCSTRING)} chars)')
" 2>&1; then
    F2P2=1
fi
add 0.15 "Module-level BASE_VIDEO_PROCESSOR_DOCSTRING preserved" $F2P2

# [pr_diff] (0.15): processing_auto.PROCESSOR_MAPPING_NAMES accessible without PIL
# Real-world failure path: CI update_metadata.py crashes via this import chain.
F2P3=0
if python3 -c "
from transformers.models.auto.processing_auto import PROCESSOR_MAPPING_NAMES
assert len(PROCESSOR_MAPPING_NAMES) > 0, 'empty mapping'
print(f'PROCESSOR_MAPPING_NAMES OK: {len(PROCESSOR_MAPPING_NAMES)} entries')
" 2>&1; then
    F2P3=1
fi
add 0.15 "processing_auto.PROCESSOR_MAPPING_NAMES without PIL" $F2P3

# =============================================================================
# BEHAVIORAL: Anti-stub method verification (0.05)
# =============================================================================
echo ""
echo "--- BEHAVIORAL: Method verification ---"

# [pr_diff] (0.05): Key methods exist and __call__ delegates to preprocess
METHODS=0
if python3 -c "
import inspect
from transformers.video_processing_utils import BaseVideoProcessor

required = ['preprocess', '_preprocess', 'sample_frames', 'to_dict', 'from_dict',
            'from_pretrained', 'save_pretrained', 'to_json_string']
for m in required:
    assert hasattr(BaseVideoProcessor, m), f'Missing method: {m}'

# Verify __call__ delegates to preprocess (not a trivial stub)
src = inspect.getsource(BaseVideoProcessor.__call__)
assert 'preprocess' in src, '__call__ does not delegate to preprocess'
print(f'All {len(required)} methods present, __call__ delegates correctly')
" 2>&1; then
    METHODS=1
fi
add 0.05 "Key methods present on BaseVideoProcessor" $METHODS

# =============================================================================
# PASS-TO-PASS: Regression with PIL installed (0.20 total)
# =============================================================================
echo ""
echo "--- PASS-TO-PASS: Regression (with PIL) ---"

# Reinstall Pillow for regression tests
python3 -m pip install -q Pillow 2>/dev/null >/dev/null

# [pr_diff] (0.15): PILImageResampling available in module when PIL IS installed
# The fix must make PILImageResampling available at runtime (not just TYPE_CHECKING)
# because it's passed as a parameter to resize() at runtime.
# Valid approaches: try/except, if is_vision_available(), lazy import — all pass.
P2P1=0
if python3 -c "
import transformers.video_processing_utils as vpu
# PILImageResampling should be in the module namespace when PIL is present
assert hasattr(vpu, 'PILImageResampling'), 'PILImageResampling not in module namespace with PIL'
# Verify it's the real enum, not a stub
from transformers.image_utils import PILImageResampling
assert vpu.PILImageResampling is PILImageResampling, 'PILImageResampling mismatch'
print(f'PILImageResampling in module: {vpu.PILImageResampling}')
" 2>&1; then
    P2P1=1
fi
add 0.15 "PILImageResampling in module namespace with PIL" $P2P1

# [pr_diff] (0.05): Other image_utils imports still work
P2P2=0
if python3 -c "
from transformers.video_processing_utils import BaseVideoProcessor
from transformers.image_utils import ChannelDimension, SizeDict
assert ChannelDimension is not None
assert SizeDict is not None
print(f'ChannelDimension: {ChannelDimension}, SizeDict: {SizeDict}')
" 2>&1; then
    P2P2=1
fi
add 0.05 "Other image_utils imports unaffected" $P2P2

# =============================================================================
# STRUCTURAL: File integrity (0.10)
# =============================================================================
echo ""
echo "--- STRUCTURAL: File integrity ---"

# [pr_diff] (0.10): File not emptied/stubbed — must retain substantial content
FILE_OK=0
if python3 -c "
with open('$TARGET') as f:
    content = f.read()
assert len(content) > 8000, f'File too short ({len(content)} chars), likely stubbed'
assert 'class BaseVideoProcessor' in content, 'BaseVideoProcessor class missing'
assert 'def preprocess' in content, 'preprocess method missing'
assert 'def _preprocess' in content, '_preprocess method missing'
assert 'def sample_frames' in content, 'sample_frames method missing'
assert 'def to_dict' in content, 'to_dict method missing'
assert 'BASE_VIDEO_PROCESSOR_DOCSTRING' in content, 'docstring constant missing'
print(f'File integrity OK: {len(content)} chars, all expected definitions present')
" 2>&1; then
    FILE_OK=1
fi
add 0.10 "File integrity (not stubbed/emptied)" $FILE_OK

# =============================================================================
# CONFIG-DERIVED: Agent config checks (0.05)
# =============================================================================
echo ""
echo "--- CONFIG: Agent config checks ---"

# [agent_config] (0.05): "Do not edit a Copied from block" — CLAUDE.md:66 @ ed003b4
COPIED=0
if python3 -c "
import re
with open('$TARGET') as f:
    content = f.read()
for line in content.splitlines():
    if '# Copied from' in line:
        assert re.search(r'# Copied from transformers\.', line), f'Broken annotation: {line}'
print('Copied-from annotations OK')
" 2>&1; then
    COPIED=1
fi
add 0.05 "Copied-from annotations intact" $COPIED

# =============================================================================
# FINAL SCORE
# =============================================================================
echo ""
echo "==============================="
echo "Score: $SCORE / 1.0"
echo "==============================="

if [ -n "$FAIL_DETAILS" ]; then
    echo -e "\nFailed checks:$FAIL_DETAILS"
fi

# Write reward
echo "$SCORE" > /logs/verifier/reward.txt

# Compute components
BEHAVIORAL=$(python3 -c "print(${F2P1}*0.30 + ${F2P2}*0.15 + ${F2P3}*0.15 + ${METHODS}*0.05)")
REGRESSION=$(python3 -c "print(${P2P1}*0.15 + ${P2P2}*0.05)")
STRUCTURAL=$(python3 -c "print(${FILE_OK}*0.10)")
CONFIG=$(python3 -c "print(${COPIED}*0.05)")

python3 -c "
import json
data = {
    'reward': $SCORE,
    'behavioral': $BEHAVIORAL,
    'regression': $REGRESSION,
    'structural': $STRUCTURAL,
    'config': $CONFIG,
    'style_rubric': 0.0
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
print(json.dumps(data, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
