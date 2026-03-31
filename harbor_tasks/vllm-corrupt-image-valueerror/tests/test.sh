#!/usr/bin/env bash
set +e

SCORE=0
LOGS=""

log() { LOGS+="$1"$'\n'; echo "$1"; }
add() { SCORE=$(python3 -c "print(round($SCORE + $1, 4))"); }

SOURCE="/testbed/vllm/multimodal/media/image.py"

# === GATE: Syntax check ===
# [pr_diff] (0.00): Source file must be valid Python
if python3 -c "compile(open('$SOURCE').read(), '$SOURCE', 'exec')" 2>/dev/null; then
    log "GATE syntax: PASS"
else
    log "GATE syntax: FAIL — aborting"
    mkdir -p /logs/verifier
    echo "0" > /logs/verifier/reward.txt
    echo '{"reward":0,"behavioral":0,"regression":0,"config":0,"style_rubric":0}' > /logs/verifier/reward.json
    exit 0
fi

# === Behavioral tests ===
# We exec the source with mocked heavy deps (torch, numpy, vllm internals)
# but keep PIL imports alive. Each error-path check is COMBINED with a
# valid-image prerequisite so always-raise stubs cannot score.

BEHAV_SCRIPT=$(cat <<'PYEOF'
import sys, os, tempfile, struct
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock
from PIL import Image

# --- Mock only heavy / vllm deps ---
heavy_mods = [
    'torch', 'torch.sparse', 'torch.nn', 'torch.nn.functional',
    'numpy', 'numpy.core',
    'vllm', 'vllm.utils', 'vllm.utils.serial_utils',
    'vllm.multimodal', 'vllm.multimodal.media',
]
for mod in heavy_mods:
    sys.modules.setdefault(mod, MagicMock())

# Provide real pybase64
import pybase64
sys.modules['pybase64'] = pybase64

# --- Provide vllm base classes with real behavior ---
class _MediaIO:
    def __init__(self): pass

class _MediaWithBytes:
    def __init__(self, media, data):
        self.media = media
        self.data = data

def _convert_image_mode_fn(image, mode):
    return image.convert(mode)

def _rgba_to_rgb(image, bg):
    bg_img = Image.new("RGB", image.size, bg)
    bg_img.paste(image, mask=image.split()[3])
    return bg_img

# --- Exec the source, stripping only heavy-dep imports ---
source = open('/testbed/vllm/multimodal/media/image.py').read()
lines = source.split('\n')
filtered = []
skip_prefixes = (
    'import torch', 'from torch',
    'import numpy', 'from numpy',
    'import vllm', 'from vllm',
    'import pybase64', 'from pybase64',
)
for line in lines:
    stripped = line.strip()
    if any(stripped.startswith(p) for p in skip_prefixes):
        continue
    filtered.append(line)

# Provide PIL names in namespace so both direct and import-based usage works
try:
    from PIL import UnidentifiedImageError
except ImportError:
    UnidentifiedImageError = Exception

ns = {
    '__builtins__': __builtins__,
    'BytesIO': BytesIO,
    'Path': Path,
    'Image': Image,
    'UnidentifiedImageError': UnidentifiedImageError,
    'pybase64': pybase64,
    'np': MagicMock(),
    'torch': MagicMock(),
    'convert_image_mode': _convert_image_mode_fn,
    'rgba_to_rgb': _rgba_to_rgb,
    'MediaIO': _MediaIO,
    'MediaWithBytes': _MediaWithBytes,
    'tensor2base64': lambda x: '',
    'MAGIC_NUMPY_PREFIX': b"\x93NUMPY",
}
exec('\n'.join(filtered), ns)
ImageMediaIO = ns['ImageMediaIO']
io = ImageMediaIO()

results = {}

# --- Create test data ---
# Valid PNG
valid_img = Image.new("RGB", (8, 8), (100, 150, 200))
buf = BytesIO()
valid_img.save(buf, format="PNG")
valid_png_bytes = buf.getvalue()

# Valid JPEG
buf2 = BytesIO()
valid_img.save(buf2, format="JPEG")
valid_jpeg_bytes = buf2.getvalue()

# Corrupt variants
truncated_png = valid_png_bytes[:len(valid_png_bytes) // 2]
truncated_jpeg = valid_jpeg_bytes[:len(valid_jpeg_bytes) // 2]
garbage_bytes = b"not an image at all \x00\xff\xfe"
empty_bytes = b""
# Valid PNG header but corrupt data
png_header_only = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20

tmpdir = tempfile.mkdtemp()

# --- Helper: check load_bytes behavior ---
def check_lb_raises_valueerror(data, label):
    """Returns PASS only if load_bytes raises ValueError for bad data."""
    try:
        io.load_bytes(data)
        return 'NO_RAISE'
    except ValueError:
        return 'PASS'
    except Exception as e:
        return f'WRONG_EXC:{type(e).__name__}'

def check_lb_valid(data, expected_size):
    """Returns PASS only if load_bytes returns valid image."""
    try:
        result = io.load_bytes(data)
        if hasattr(result, 'media') and result.media.size == expected_size:
            return 'PASS'
        return 'BAD_RESULT'
    except Exception as e:
        return f'EXC:{type(e).__name__}'

def check_lf_raises_valueerror(filepath, label):
    """Returns PASS only if load_file raises ValueError for bad file."""
    try:
        io.load_file(filepath)
        return 'NO_RAISE'
    except ValueError:
        return 'PASS'
    except Exception as e:
        return f'WRONG_EXC:{type(e).__name__}'

def check_lf_valid(filepath, expected_size):
    """Returns PASS only if load_file returns valid image."""
    try:
        result = io.load_file(filepath)
        if hasattr(result, 'media') and result.media.size == expected_size:
            return 'PASS'
        return 'BAD_RESULT'
    except Exception as e:
        return f'EXC:{type(e).__name__}'

# --- Run all individual checks ---
# Valid images
results['lb_valid_png'] = check_lb_valid(valid_png_bytes, (8, 8))
results['lb_valid_jpeg'] = check_lb_valid(valid_jpeg_bytes, (8, 8))

good_file = Path(tmpdir) / "good.png"
good_file.write_bytes(valid_png_bytes)
results['lf_valid'] = check_lf_valid(good_file, (8, 8))

# Error paths
results['lb_garbage'] = check_lb_raises_valueerror(garbage_bytes, 'garbage')
results['lb_truncated_png'] = check_lb_raises_valueerror(truncated_png, 'truncated_png')
results['lb_truncated_jpeg'] = check_lb_raises_valueerror(truncated_jpeg, 'truncated_jpeg')
results['lb_empty'] = check_lb_raises_valueerror(empty_bytes, 'empty')

bad_file = Path(tmpdir) / "bad.png"
bad_file.write_bytes(garbage_bytes)
results['lf_garbage'] = check_lf_raises_valueerror(bad_file, 'garbage')

trunc_file = Path(tmpdir) / "trunc.png"
trunc_file.write_bytes(truncated_png)
results['lf_truncated'] = check_lf_raises_valueerror(trunc_file, 'truncated')

# Output results
for k, v in results.items():
    print(f"{k}={v}")
PYEOF
)

BEHAV_OUTPUT=$(python3 -c "$BEHAV_SCRIPT" 2>&1) || true
echo "$BEHAV_OUTPUT"

get_result() { echo "$BEHAV_OUTPUT" | grep "^$1=" | cut -d= -f2; }

# --- P2P prerequisite: valid images must load ---
LB_VALID_PNG="$(get_result lb_valid_png)"
LB_VALID_JPEG="$(get_result lb_valid_jpeg)"
LF_VALID="$(get_result lf_valid)"

LB_VALID_OK="no"
if [ "$LB_VALID_PNG" = "PASS" ] && [ "$LB_VALID_JPEG" = "PASS" ]; then
    LB_VALID_OK="yes"
fi
LF_VALID_OK="no"
if [ "$LF_VALID" = "PASS" ]; then
    LF_VALID_OK="yes"
fi

# === Combined checks: error path scores are gated by valid-path success ===
# This prevents always-raise stubs from scoring on error checks.

# [pr_diff] (0.15): Valid PNG loads via load_bytes
if [ "$LB_VALID_PNG" = "PASS" ]; then
    log "CHECK lb_valid_png: PASS"
    add 0.15
else
    log "CHECK lb_valid_png: FAIL ($LB_VALID_PNG)"
fi

# [pr_diff] (0.10): Valid JPEG loads via load_bytes
if [ "$LB_VALID_JPEG" = "PASS" ]; then
    log "CHECK lb_valid_jpeg: PASS"
    add 0.10
else
    log "CHECK lb_valid_jpeg: FAIL ($LB_VALID_JPEG)"
fi

# [pr_diff] (0.10): Valid PNG loads via load_file
if [ "$LF_VALID" = "PASS" ]; then
    log "CHECK lf_valid: PASS"
    add 0.10
else
    log "CHECK lf_valid: FAIL ($LF_VALID)"
fi

# --- F2P error-path checks (gated by valid-path prerequisite) ---

# [pr_diff] (0.15): load_bytes raises ValueError for garbage bytes (gated)
if [ "$LB_VALID_OK" = "yes" ] && [ "$(get_result lb_garbage)" = "PASS" ]; then
    log "CHECK lb_garbage: PASS"
    add 0.15
else
    log "CHECK lb_garbage: FAIL (valid=$LB_VALID_OK, error=$(get_result lb_garbage))"
fi

# [pr_diff] (0.15): load_bytes raises ValueError for truncated PNG (gated)
if [ "$LB_VALID_OK" = "yes" ] && [ "$(get_result lb_truncated_png)" = "PASS" ]; then
    log "CHECK lb_truncated_png: PASS"
    add 0.15
else
    log "CHECK lb_truncated_png: FAIL (valid=$LB_VALID_OK, error=$(get_result lb_truncated_png))"
fi

# [pr_diff] (0.10): load_bytes raises ValueError for truncated JPEG (gated)
if [ "$LB_VALID_OK" = "yes" ] && [ "$(get_result lb_truncated_jpeg)" = "PASS" ]; then
    log "CHECK lb_truncated_jpeg: PASS"
    add 0.10
else
    log "CHECK lb_truncated_jpeg: FAIL (valid=$LB_VALID_OK, error=$(get_result lb_truncated_jpeg))"
fi

# [pr_diff] (0.05): load_bytes raises ValueError for empty bytes (gated)
if [ "$LB_VALID_OK" = "yes" ] && [ "$(get_result lb_empty)" = "PASS" ]; then
    log "CHECK lb_empty: PASS"
    add 0.05
else
    log "CHECK lb_empty: FAIL (valid=$LB_VALID_OK, error=$(get_result lb_empty))"
fi

# [pr_diff] (0.10): load_file raises ValueError for garbage content (gated)
if [ "$LF_VALID_OK" = "yes" ] && [ "$(get_result lf_garbage)" = "PASS" ]; then
    log "CHECK lf_garbage: PASS"
    add 0.10
else
    log "CHECK lf_garbage: FAIL (valid=$LF_VALID_OK, error=$(get_result lf_garbage))"
fi

# [pr_diff] (0.10): load_file raises ValueError for truncated data (gated)
if [ "$LF_VALID_OK" = "yes" ] && [ "$(get_result lf_truncated)" = "PASS" ]; then
    log "CHECK lf_truncated: PASS"
    add 0.10
else
    log "CHECK lf_truncated: FAIL (valid=$LF_VALID_OK, error=$(get_result lf_truncated))"
fi

# === Totals ===
# Weights: P2P=0.35, F2P(gated)=0.65 → total=1.00
# All checks are behavioral (call the function, check output/exception)

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Compute sub-scores
BEHAVIORAL_F2P=$(python3 -c "
s = 0
if '$LB_VALID_OK' == 'yes':
    if '$(get_result lb_garbage)' == 'PASS': s += 0.15
    if '$(get_result lb_truncated_png)' == 'PASS': s += 0.15
    if '$(get_result lb_truncated_jpeg)' == 'PASS': s += 0.10
    if '$(get_result lb_empty)' == 'PASS': s += 0.05
if '$LF_VALID_OK' == 'yes':
    if '$(get_result lf_garbage)' == 'PASS': s += 0.10
    if '$(get_result lf_truncated)' == 'PASS': s += 0.10
print(f'{s:.2f}')
")
REGRESSION=$(python3 -c "
s = 0
if '$LB_VALID_PNG' == 'PASS': s += 0.15
if '$LB_VALID_JPEG' == 'PASS': s += 0.10
if '$LF_VALID' == 'PASS': s += 0.10
print(f'{s:.2f}')
")

echo "{\"reward\":$SCORE,\"behavioral\":$BEHAVIORAL_F2P,\"regression\":$REGRESSION,\"config\":0,\"style_rubric\":0}" > /logs/verifier/reward.json

log ""
log "=== SUMMARY ==="
log "Behavioral F2P: $BEHAVIORAL_F2P / 0.65"
log "Regression P2P: $REGRESSION / 0.35"
log "TOTAL: $SCORE / 1.00"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
