#!/usr/bin/env bash
# Verifier for transformers-fast-image-processor-import
# Bug: importing fast image processor modules via full path fails with ModuleNotFoundError

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

echo "=== transformers-fast-image-processor-import verifier ==="

# ── GATE: Python syntax validity ─────────────────────────────────────────
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
for path in [
    "/workspace/transformers/src/transformers/__init__.py",
    "/workspace/transformers/utils/check_repo.py",
]:
    try:
        with open(path) as f:
            ast.parse(f.read())
        print(f"  OK: {path} parses successfully")
    except SyntaxError as e:
        print(f"  FAIL: SyntaxError in {path}: {e}")
        sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights - target >=60% behavioral
W_FAILTOPASS_IMPORT=0.35      # PRIMARY: actual import works
W_FAILTOPASS_CLASS=0.25       # PRIMARY: Fast->non-Fast class redirect works
W_BEHAV_CLASS_REDIRECT=0.10   # behavioral: class name handling verified
W_BEHAV_CHECK_REPO=0.10       # behavioral: check_repo ignores _fast modules
W_PASSTOPASS=0.10             # regression: existing imports still work
W_ANTISTUB=0.10               # anti-stub: files not gutted

SCORE="0.0"
IMPORT_WORKS=false

# ── TEST 1 (PRIMARY - GATE): Fail-to-pass - import from alias module works ──
# [pr_diff] (0.35): ModuleNotFoundError is fixed - can import from image_processing_*_fast paths
echo ""
echo "TEST 1 (PRIMARY): fail-to-pass - import from alias module works (weight=$W_FAILTOPASS_IMPORT)"
T1=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers/src')

# Try to import from a fast image processor module path
# This is the actual bug: ModuleNotFoundError on these paths
try:
    # Find an available model with image_processing
    from pathlib import Path
    models_dir = Path('/workspace/transformers/src/transformers/models')
    candidate = None
    for proc_file in models_dir.rglob('image_processing_*.py'):
        if proc_file.stem.endswith('_fast'):
            continue
        model_name = proc_file.parent.name
        class_name = ''.join([p.title() for p in model_name.replace('_', '-').split('-')]) + 'ImageProcessorFast'
        module_name = proc_file.stem
        candidate = (model_name, module_name, class_name)
        break

    if candidate is None:
        print("SKIP: no image_processing files found")
        sys.exit(1)

    model_name, module_name, class_name = candidate
    fast_module = f"transformers.models.{model_name}.{module_name}_fast"

    # This is the actual failing import from the bug
    exec(f"from {fast_module} import {class_name}")
    print(f"PASS: successfully imported {class_name} from {fast_module}")
    sys.exit(0)
except ModuleNotFoundError as e:
    print(f"FAIL: ModuleNotFoundError - {e}")
    sys.exit(1)
except ImportError as e:
    # ImportError for missing deps is different from ModuleNotFoundError for missing module
    if "ModuleNotFoundError" in str(e):
        print(f"FAIL: ModuleNotFoundError wrapped in ImportError - {e}")
        sys.exit(1)
    # Other ImportErrors (missing optional deps) may be acceptable
    print(f"PASS: ImportError (not ModuleNotFoundError) - module exists but has dep issues: {e}")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: unexpected error - {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_FAILTOPASS_IMPORT)")
    IMPORT_WORKS=true
fi

# ── TEST 2 (PRIMARY - GATE): Fail-to-pass - class redirect works ──
# [pr_diff] (0.25): XImageProcessorFast imported from alias resolves to XImageProcessor
echo ""
echo "TEST 2 (PRIMARY): fail-to-pass - class redirect Fast->non-Fast works (weight=$W_FAILTOPASS_CLASS)"
T2=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers/src')

# After import, the Fast class should resolve to non-Fast class
try:
    from pathlib import Path
    models_dir = Path('/workspace/transformers/src/transformers/models')

    for proc_file in models_dir.rglob('image_processing_*.py'):
        if proc_file.stem.endswith('_fast'):
            continue

        model_name = proc_file.parent.name
        module_name = proc_file.stem
        # Convert model_name to CamelCase
        words = model_name.replace('_', '-').split('-')
        camel_name = ''.join([w.title() for w in words])
        fast_class = camel_name + 'ImageProcessorFast'
        normal_class = camel_name + 'ImageProcessor'

        fast_module = f"transformers.models.{model_name}.{module_name}_fast"

        try:
            # Import the Fast class from the alias module
            namespace = {}
            exec(f"from {fast_module} import {fast_class} as ImportedFast", namespace)
            ImportedFast = namespace['ImportedFast']

            # Import the normal class from the actual module
            normal_module = f"transformers.models.{model_name}.{module_name}"
            namespace2 = {}
            exec(f"from {normal_module} import {normal_class} as ImportedNormal", namespace2)
            ImportedNormal = namespace2['ImportedNormal']

            # They should be the same class (redirect worked)
            if ImportedFast is ImportedNormal:
                print(f"PASS: {fast_class} from alias module is same as {normal_class}")
                sys.exit(0)
            else:
                print(f"FAIL: {fast_class} is not the same as {normal_class}")
                sys.exit(1)

        except ModuleNotFoundError:
            continue  # Try next model
        except ImportError:
            continue  # Try next model

    print("FAIL: could not find any model to test class redirect")
    sys.exit(1)

except Exception as e:
    print(f"FAIL: unexpected error - {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_FAILTOPASS_CLASS)")
fi

# ── TEST 3: behavioral - __getattr__ mechanism present ──
# [pr_diff] (0.10): __getattr__ handles Fast->non-Fast redirect
echo ""
echo "TEST 3: behavioral - __getattr__ redirect mechanism (weight=$W_BEHAV_CLASS_REDIRECT)"
T3=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers/src')

# Verify the mechanism exists by checking that imported module has __getattr__
try:
    from pathlib import Path
    models_dir = Path('/workspace/transformers/src/transformers/models')

    for proc_file in models_dir.rglob('image_processing_*.py'):
        if proc_file.stem.endswith('_fast'):
            continue

        model_name = proc_file.parent.name
        module_name = proc_file.stem
        fast_module_name = f"transformers.models.{model_name}.{module_name}_fast"

        try:
            # Import the alias module
            import importlib
            fast_mod = importlib.import_module(fast_module_name)

            # Check it has __getattr__
            if hasattr(fast_mod, '__getattr__'):
                print(f"PASS: {fast_module_name} has __getattr__ for redirect")
                sys.exit(0)
            else:
                print(f"FAIL: {fast_module_name} missing __getattr__")
                sys.exit(1)

        except ModuleNotFoundError:
            continue
        except ImportError:
            continue

    print("FAIL: could not verify __getattr__ on any alias module")
    sys.exit(1)

except Exception as e:
    print(f"FAIL: unexpected error - {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_CLASS_REDIRECT)")
fi

# ── TEST 4: behavioral - check_repo.py ignores _fast aliases ──
# [pr_diff] (0.10): check_repo.py excludes image_processing_*_fast from docs
echo ""
echo "TEST 4: behavioral - check_repo.py ignores _fast aliases (weight=$W_BEHAV_CHECK_REPO)"
T4=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers')

# Import the actual function and test it
try:
    from utils.check_repo import ignore_undocumented

    # Test that image_processing_*_fast names are ignored
    test_names = [
        "image_processing_llama4_fast",
        "image_processing_clip_fast",
        "image_processing_vit_fast",
    ]

    for name in test_names:
        if not ignore_undocumented(name):
            print(f"FAIL: ignore_undocumented('{name}') returned False, expected True")
            sys.exit(1)

    print("PASS: ignore_undocumented correctly excludes image_processing_*_fast")
    sys.exit(0)

except ImportError as e:
    print(f"FAIL: could not import ignore_undocumented - {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected error - {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_CHECK_REPO)")
fi

# ── TEST 5: pass-to-pass - existing imports still work ──
# [repo_tests] (0.10): Existing module aliases not broken
echo ""
echo "TEST 5: pass-to-pass - existing imports preserved (weight=$W_PASSTOPASS)"
T5=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers/src')

try:
    # These should still work after the fix
    from transformers import AutoTokenizer  # Basic sanity
    from transformers import image_processing_utils_fast  # Existing alias

    print("PASS: existing imports work")
    sys.exit(0)
except ImportError as e:
    print(f"FAIL: existing import broken - {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected error - {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_PASSTOPASS)")
fi

# ── TEST 6: anti-stub ──
echo ""
echo "TEST 6: anti-stub - files retain content (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/transformers/src/transformers/__init__.py") as f:
    lines = len(f.read().splitlines())
if lines < 500:
    print(f"FAIL: __init__.py too short: {lines} lines")
    sys.exit(1)

with open("/workspace/transformers/utils/check_repo.py") as f:
    source = f.read()
if "ignore_undocumented" not in source:
    print("FAIL: check_repo.py missing ignore_undocumented")
    sys.exit(1)
if len(source.splitlines()) < 500:
    print("FAIL: check_repo.py too short")
    sys.exit(1)

print("PASS: files retain original content")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# ── Final score ──────────────────────────────────────────────────────────
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
