#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TARGET="/repo/src/transformers/tokenization_utils_tokenizers.py"
TESTS_DIR="/logs/verifier"

########################################################################
# GATE: Syntax check — abort on failure
########################################################################
# [pr_diff] (0.00): File must be valid Python
echo "=== GATE: Syntax check ==="
if ! python3 -c "import ast; ast.parse(open('$TARGET').read())"; then
    echo "GATE FAILED: syntax error in $TARGET"
    echo "0.0" > "$TESTS_DIR/reward.txt"
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > "$TESTS_DIR/reward.json"
    exit 0
fi
echo "GATE PASSED"

########################################################################
# BEHAVIORAL FAIL-TO-PASS: BPE tokenizer avoids from_file (0.35)
########################################################################
# [pr_diff] (0.35): BPE tokenizer path must not call TokenizerFast.from_file
echo "=== TEST 1: BPE path avoids redundant from_file ==="
T1=$(python3 << 'PYEOF'
import json, os, sys, tempfile, unittest.mock as mock

# Create a minimal BPE tokenizer.json
bpe_tokenizer = {
    "version": "1.0",
    "model": {
        "type": "BPE",
        "vocab": {"a": 0, "b": 1, "c": 2, "ab": 3},
        "merges": ["a b"],
        "dropout": None,
        "unk_token": None,
        "continuing_subword_prefix": None,
        "end_of_word_suffix": None,
        "fuse_unk": False
    },
    "added_tokens": [],
    "normalizer": None,
    "pre_tokenizer": None,
    "post_processor": None,
    "decoder": None
}

tmpdir = tempfile.mkdtemp()
tok_path = os.path.join(tmpdir, "tokenizer.json")
with open(tok_path, "w") as f:
    json.dump(bpe_tokenizer, f)

from tokenizers import Tokenizer as TokenizerFast
from tokenizers.models import BPE
from transformers.tokenization_utils_tokenizers import TokenizersBackend

# Create a subclass with custom __init__ to trigger elif branch
class CustomBPETokenizer(TokenizersBackend):
    model = BPE
    def __init__(self, *args, **kwargs):
        pass

# Track calls to from_file
from_file_calls = []
original_from_file = TokenizerFast.from_file

def tracking_from_file(path, *args, **kwargs):
    from_file_calls.append(path)
    return original_from_file(path, *args, **kwargs)

with mock.patch.object(TokenizerFast, 'from_file', side_effect=tracking_from_file):
    try:
        result = CustomBPETokenizer.convert_to_native_format(
            trust_remote_code=False,
            tokenizer_file=tok_path
        )
    except Exception as e:
        print(f"0|convert_to_native_format raised: {e}", file=sys.stderr)
        print("0")
        sys.exit(0)

if len(from_file_calls) == 0:
    print("1")
else:
    print(f"0|from_file called {len(from_file_calls)} time(s) for BPE", file=sys.stderr)
    print("0")
PYEOF
)
T1_PASS=$(echo "$T1" | tail -1)
echo "  Result: $T1_PASS (from_file avoidance for BPE)"

########################################################################
# BEHAVIORAL FAIL-TO-PASS: Correct output from optimized path (0.30)
########################################################################
# [pr_diff] (0.30): Optimized path must return correct vocab and merges
echo "=== TEST 2: Optimized path returns correct vocab/merges ==="
T2=$(python3 << 'PYEOF'
import json, os, sys, tempfile, unittest.mock as mock

# Create a BPE tokenizer.json with known vocab/merges
bpe_tokenizer = {
    "version": "1.0",
    "model": {
        "type": "BPE",
        "vocab": {"a": 0, "b": 1, "c": 2, "ab": 3},
        "merges": ["a b"],
        "dropout": None,
        "unk_token": None,
        "continuing_subword_prefix": None,
        "end_of_word_suffix": None,
        "fuse_unk": False
    },
    "added_tokens": [],
    "normalizer": None,
    "pre_tokenizer": None,
    "post_processor": None,
    "decoder": None
}

tmpdir = tempfile.mkdtemp()
tok_path = os.path.join(tmpdir, "tokenizer.json")
with open(tok_path, "w") as f:
    json.dump(bpe_tokenizer, f)

from tokenizers import Tokenizer as TokenizerFast
from tokenizers.models import BPE
from transformers.tokenization_utils_tokenizers import TokenizersBackend

class CustomBPETokenizer(TokenizersBackend):
    model = BPE
    def __init__(self, *args, **kwargs):
        pass

# Block from_file to ensure the optimized path is used
def blocked_from_file(path, *args, **kwargs):
    raise RuntimeError("from_file should not be called for BPE optimization")

with mock.patch.object(TokenizerFast, 'from_file', side_effect=blocked_from_file):
    try:
        result = CustomBPETokenizer.convert_to_native_format(
            trust_remote_code=False,
            tokenizer_file=tok_path
        )
    except RuntimeError as e:
        if "from_file should not be called" in str(e):
            print(f"0|from_file was called — optimization not present", file=sys.stderr)
            print("0")
            sys.exit(0)
        raise
    except Exception as e:
        print(f"0|convert_to_native_format raised: {e}", file=sys.stderr)
        print("0")
        sys.exit(0)

# Verify returned values
errors = []
vocab = result.get("vocab")
if vocab is None:
    errors.append("vocab is None")
elif not isinstance(vocab, dict):
    errors.append(f"vocab type is {type(vocab).__name__}, expected dict")
elif set(vocab.keys()) != {"a", "b", "c", "ab"}:
    errors.append(f"vocab keys wrong: {set(vocab.keys())}")

merges = result.get("merges")
if merges is None:
    errors.append("merges is None")
elif len(merges) != 1:
    errors.append(f"merges length is {len(merges)}, expected 1")

if errors:
    print(f"0|{'; '.join(errors)}", file=sys.stderr)
    print("0")
else:
    print("1")
PYEOF
)
T2_PASS=$(echo "$T2" | tail -1)
echo "  Result: $T2_PASS (correct vocab/merges from optimized path)"

########################################################################
# PASS-TO-PASS: Unigram/unknown types still use from_file fallback (0.10)
########################################################################
# [pr_diff] (0.10): Unigram tokenizers must still work via from_file fallback
echo "=== TEST 3: Unigram fallback still works ==="
T3=$(python3 << 'PYEOF'
import json, os, sys, tempfile

# Create a Unigram tokenizer.json
unigram_tokenizer = {
    "version": "1.0",
    "model": {
        "type": "Unigram",
        "vocab": [["<unk>", 0.0], ["a", -1.0], ["b", -2.0], ["ab", -1.5]],
        "unk_id": 0,
        "byte_fallback": False
    },
    "added_tokens": [],
    "normalizer": None,
    "pre_tokenizer": None,
    "post_processor": None,
    "decoder": None
}

tmpdir = tempfile.mkdtemp()
tok_path = os.path.join(tmpdir, "tokenizer.json")
with open(tok_path, "w") as f:
    json.dump(unigram_tokenizer, f)

from tokenizers.models import Unigram
from transformers.tokenization_utils_tokenizers import TokenizersBackend

class CustomUnigramTokenizer(TokenizersBackend):
    model = Unigram
    def __init__(self, *args, **kwargs):
        pass

try:
    result = CustomUnigramTokenizer.convert_to_native_format(
        trust_remote_code=False,
        tokenizer_file=tok_path
    )
except Exception as e:
    print(f"0|Unigram path raised: {e}", file=sys.stderr)
    print("0")
    sys.exit(0)

# Verify vocab extracted correctly
vocab = result.get("vocab")
if vocab is None:
    print("0|vocab is None", file=sys.stderr)
    print("0")
elif not isinstance(vocab, list):
    print(f"0|vocab type is {type(vocab).__name__}, expected list", file=sys.stderr)
    print("0")
elif len(vocab) != 4:
    print(f"0|vocab length is {len(vocab)}, expected 4", file=sys.stderr)
    print("0")
else:
    print("1")
PYEOF
)
T3_PASS=$(echo "$T3" | tail -1)
echo "  Result: $T3_PASS (Unigram fallback)"

########################################################################
# PASS-TO-PASS: First branch (no custom __init__) unchanged (0.10)
########################################################################
# [pr_diff] (0.10): Base class path (no custom __init__) must still work
echo "=== TEST 4: Base class path unchanged ==="
T4=$(python3 << 'PYEOF'
import json, os, sys, tempfile

bpe_tokenizer = {
    "version": "1.0",
    "model": {
        "type": "BPE",
        "vocab": {"x": 0, "y": 1, "xy": 2},
        "merges": ["x y"],
        "dropout": None,
        "unk_token": None,
        "continuing_subword_prefix": None,
        "end_of_word_suffix": None,
        "fuse_unk": False
    },
    "added_tokens": [],
    "normalizer": None,
    "pre_tokenizer": None,
    "post_processor": None,
    "decoder": None
}

tmpdir = tempfile.mkdtemp()
tok_path = os.path.join(tmpdir, "tokenizer.json")
with open(tok_path, "w") as f:
    json.dump(bpe_tokenizer, f)

from transformers.tokenization_utils_tokenizers import TokenizersBackend

# Base class has no custom __init__, should hit the first branch
try:
    result = TokenizersBackend.convert_to_native_format(
        trust_remote_code=False,
        tokenizer_file=tok_path
    )
except Exception as e:
    print(f"0|base class path raised: {e}", file=sys.stderr)
    print("0")
    sys.exit(0)

if "tokenizer_object" in result:
    print("1")
else:
    print(f"0|tokenizer_object not in result", file=sys.stderr)
    print("0")
PYEOF
)
T4_PASS=$(echo "$T4" | tail -1)
echo "  Result: $T4_PASS (base class path)"

########################################################################
# CONFIG-DERIVED: ruff format check (0.10)
########################################################################
# [agent_config] (0.10): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2
echo "=== TEST 5: ruff format check ==="
T5="0"
if command -v ruff &>/dev/null || pip install --quiet ruff 2>/dev/null; then
    if ruff check "$TARGET" --select E9,F63,F7,F82 --quiet 2>/dev/null; then
        if ruff format --check "$TARGET" 2>/dev/null; then
            T5="1"
            echo "  ruff: PASSED"
        else
            echo "  ruff format: FAILED"
        fi
    else
        echo "  ruff check: FAILED (fatal errors)"
    fi
else
    echo "  ruff: not available, skipping (neutral)"
    T5="1"
fi

########################################################################
# ANTI-STUB: Changed file must not be a trivial stub (0.05)
########################################################################
# [pr_diff] (0.05): Fix must not be a no-op or comment-only change
echo "=== TEST 6: Anti-stub check ==="
T6=$(python3 << 'PYEOF'
import subprocess, sys

# Check that there are actual code changes (not just comments/whitespace)
diff = subprocess.run(
    ["git", "diff", "HEAD", "--", "src/transformers/tokenization_utils_tokenizers.py"],
    cwd="/repo", capture_output=True, text=True
).stdout

if not diff:
    diff = subprocess.run(
        ["git", "diff", "--cached", "--", "src/transformers/tokenization_utils_tokenizers.py"],
        cwd="/repo", capture_output=True, text=True
    ).stdout

if not diff:
    # Check committed changes
    diff = subprocess.run(
        ["git", "log", "-1", "-p", "--", "src/transformers/tokenization_utils_tokenizers.py"],
        cwd="/repo", capture_output=True, text=True
    ).stdout

if not diff:
    print("0|no changes detected", file=sys.stderr)
    print("0")
    sys.exit(0)

# Count actual code line changes (not comments or blank)
added = 0
for line in diff.splitlines():
    if line.startswith("+") and not line.startswith("+++"):
        stripped = line[1:].strip()
        if stripped and not stripped.startswith("#"):
            added += 1

if added >= 2:
    print("1")
else:
    print(f"0|only {added} non-comment lines added", file=sys.stderr)
    print("0")
PYEOF
)
T6_PASS=$(echo "$T6" | tail -1)
echo "  Result: $T6_PASS (anti-stub)"

########################################################################
# Compute final score
########################################################################
# Weights: T1=0.35, T2=0.30, T3=0.10, T4=0.10, T5=0.10, T6=0.05
SCORE=$(python3 -c "
t1=$T1_PASS; t2=$T2_PASS; t3=$T3_PASS; t4=$T4_PASS; t5=$T5; t6=$T6_PASS
behavioral = 0.35*t1 + 0.30*t2
regression = 0.10*t3 + 0.10*t4
config = 0.10*t5
structural = 0.05*t6
total = behavioral + regression + config + structural
print(f'{total:.2f}')
")

BEHAVIORAL=$(python3 -c "print(f'{0.35*$T1_PASS + 0.30*$T2_PASS:.2f}')")
REGRESSION=$(python3 -c "print(f'{0.10*$T3_PASS + 0.10*$T4_PASS:.2f}')")
CONFIG=$(python3 -c "print(f'{0.10*$T5:.2f}')")
STRUCTURAL=$(python3 -c "print(f'{0.05*$T6_PASS:.2f}')")

echo ""
echo "=== FINAL SCORE: $SCORE ==="
echo "  behavioral=$BEHAVIORAL regression=$REGRESSION config=$CONFIG structural=$STRUCTURAL"

echo "$SCORE" > "$TESTS_DIR/reward.txt"
cat > "$TESTS_DIR/reward.json" << ENDJSON
{"reward": $SCORE, "behavioral": $BEHAVIORAL, "regression": $REGRESSION, "config": $CONFIG, "style_rubric": 0.0}
ENDJSON

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
