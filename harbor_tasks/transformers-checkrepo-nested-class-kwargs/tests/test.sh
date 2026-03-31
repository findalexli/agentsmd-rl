#!/usr/bin/env bash
set +e

CHECK_REPO="/workspace/transformers/utils/check_repo.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS

# Weight budget: behavioral=0.60, p2p=0.20, config=0.10, structural=0.10
WEIGHTS[behav_mixed_class]=0.25
WEIGHTS[behav_mixed_func]=0.20
WEIGHTS[behav_cache_identity]=0.10
WEIGHTS[behav_cache_api]=0.05
WEIGHTS[p2p_toplevel_missing]=0.10
WEIGHTS[p2p_toplevel_ok]=0.05
WEIGHTS[p2p_nested_only_ok]=0.05
WEIGHTS[config_ruff]=0.10
WEIGHTS[struct_antistub]=0.05
WEIGHTS[struct_modified]=0.05

for key in behav_mixed_class behav_mixed_func behav_cache_identity behav_cache_api p2p_toplevel_missing p2p_toplevel_ok p2p_nested_only_ok config_ruff struct_antistub struct_modified; do
    RESULTS[$key]=0
done

# ---------- GATE: Syntax check ----------
python3 -c "import ast; ast.parse(open('$CHECK_REPO').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "GATE FAIL: check_repo.py syntax error"; echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS: check_repo.py parses"

# ---------- BEHAVIORAL 1 (0.25): Mixed file — top-level flagged, class-nested ignored ----------
# [pr_diff] (0.25): Nested classes inside container classes are ignored; top-level violations still caught
python3 << 'PYEOF'
import os, sys, tempfile

sys.path.insert(0, "/workspace/transformers/utils")
import check_repo

tmpdir = tempfile.mkdtemp()
model_dir = os.path.join(tmpdir, "models", "mixedmodel")
os.makedirs(model_dir)

# File has: top-level class WITHOUT **kwargs + nested class WITHOUT **kwargs
# Only the top-level should be flagged
with open(os.path.join(model_dir, "modeling_mixedmodel.py"), "w") as f:
    f.write("""
class PreTrainedModel:
    pass

class TopLevelBadModel(PreTrainedModel):
    def forward(self, hidden_states):
        return hidden_states

class ContainerHelper:
    class NestedBadModel(PreTrainedModel):
        def forward(self, hidden_states):
            return hidden_states
""".lstrip())

old_path = check_repo.PATH_TO_TRANSFORMERS
check_repo.PATH_TO_TRANSFORMERS = os.path.join(tmpdir, "models")

try:
    check_repo.check_models_have_kwargs()
    print("FAIL: Expected exception for TopLevelBadModel (no-op detected)")
    sys.exit(1)
except Exception as e:
    err = str(e)
    if "TopLevelBadModel" not in err:
        print(f"FAIL: Exception did not mention TopLevelBadModel: {err}")
        sys.exit(1)
    if "NestedBadModel" in err:
        print(f"FAIL: Exception incorrectly mentions NestedBadModel: {err}")
        sys.exit(1)
    print("PASS: TopLevelBadModel flagged, NestedBadModel correctly ignored")
    sys.exit(0)
finally:
    check_repo.PATH_TO_TRANSFORMERS = old_path
PYEOF
if [ $? -eq 0 ]; then RESULTS[behav_mixed_class]=1; echo "behav_mixed_class: PASS"; else echo "behav_mixed_class: FAIL"; fi

# ---------- BEHAVIORAL 2 (0.20): Mixed file — top-level flagged, function-nested ignored ----------
# [pr_diff] (0.20): Nested classes inside functions are ignored; top-level violations still caught
python3 << 'PYEOF'
import os, sys, tempfile

sys.path.insert(0, "/workspace/transformers/utils")
import check_repo

tmpdir = tempfile.mkdtemp()
model_dir = os.path.join(tmpdir, "models", "funcmodel")
os.makedirs(model_dir)

# File has: top-level class WITHOUT **kwargs + function-nested class WITHOUT **kwargs
with open(os.path.join(model_dir, "modeling_funcmodel.py"), "w") as f:
    f.write("""
class PreTrainedModel:
    pass

class TopLevelNoKwargs(PreTrainedModel):
    def forward(self, hidden_states):
        return hidden_states

def make_helper():
    class FuncNestedModel(PreTrainedModel):
        def forward(self, hidden_states):
            return hidden_states
    return FuncNestedModel
""".lstrip())

old_path = check_repo.PATH_TO_TRANSFORMERS
check_repo.PATH_TO_TRANSFORMERS = os.path.join(tmpdir, "models")

try:
    check_repo.check_models_have_kwargs()
    print("FAIL: Expected exception for TopLevelNoKwargs (no-op detected)")
    sys.exit(1)
except Exception as e:
    err = str(e)
    if "TopLevelNoKwargs" not in err:
        print(f"FAIL: Exception did not mention TopLevelNoKwargs: {err}")
        sys.exit(1)
    if "FuncNestedModel" in err:
        print(f"FAIL: Exception incorrectly mentions FuncNestedModel: {err}")
        sys.exit(1)
    print("PASS: TopLevelNoKwargs flagged, FuncNestedModel correctly ignored")
    sys.exit(0)
finally:
    check_repo.PATH_TO_TRANSFORMERS = old_path
PYEOF
if [ $? -eq 0 ]; then RESULTS[behav_mixed_func]=1; echo "behav_mixed_func: PASS"; else echo "behav_mixed_func: FAIL"; fi

# ---------- BEHAVIORAL 3 (0.10): get_model_modules caching — same object returned ----------
# [pr_diff] (0.10): get_model_modules returns cached result on repeated calls
python3 << 'PYEOF'
import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, "/workspace/transformers/utils")
import check_repo

# Clear cache if present
if hasattr(check_repo.get_model_modules, 'cache_clear'):
    check_repo.get_model_modules.cache_clear()

class RecordingNamespace:
    def __init__(self, mapping):
        self._mapping = mapping
    def __dir__(self):
        return list(self._mapping.keys())
    def __getattr__(self, name):
        try:
            return self._mapping[name]
        except KeyError as e:
            raise AttributeError(name) from e

alpha_modeling = object()
alpha_module = RecordingNamespace({"modeling_alpha": alpha_modeling})
fake_models = RecordingNamespace({"alpha": alpha_module})
fake_transformers = SimpleNamespace(models=fake_models)

with patch.object(check_repo, "transformers", fake_transformers):
    first = check_repo.get_model_modules()
    second = check_repo.get_model_modules()

if first is second:
    print("PASS: get_model_modules returned same cached object")
    sys.exit(0)
else:
    print("FAIL: get_model_modules returned different objects (not cached)")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behav_cache_identity]=1; echo "behav_cache_identity: PASS"; else echo "behav_cache_identity: FAIL"; fi

# ---------- BEHAVIORAL 4 (0.05): get_model_modules has cache_clear (lru_cache API) ----------
# [pr_diff] (0.05): get_model_modules is wrapped with lru_cache (exposes cache_clear)
python3 << 'PYEOF'
import sys
sys.path.insert(0, "/workspace/transformers/utils")
import check_repo

if hasattr(check_repo.get_model_modules, 'cache_clear'):
    print("PASS: get_model_modules has cache_clear attribute (lru_cache)")
    sys.exit(0)
else:
    print("FAIL: get_model_modules lacks cache_clear attribute (no lru_cache)")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behav_cache_api]=1; echo "behav_cache_api: PASS"; else echo "behav_cache_api: FAIL"; fi

# ---------- PASS-TO-PASS 1 (0.10): Top-level class missing **kwargs still raises ----------
# [pr_diff] (0.10): Top-level PreTrainedModel subclass without **kwargs in forward is still caught
python3 << 'PYEOF'
import os, sys, tempfile

sys.path.insert(0, "/workspace/transformers/utils")
import check_repo

tmpdir = tempfile.mkdtemp()
model_dir = os.path.join(tmpdir, "models", "badmodel")
os.makedirs(model_dir)

with open(os.path.join(model_dir, "modeling_badmodel.py"), "w") as f:
    f.write("""
class PreTrainedModel:
    pass

class BadModel(PreTrainedModel):
    def forward(self, hidden_states):
        return hidden_states
""".lstrip())

old_path = check_repo.PATH_TO_TRANSFORMERS
check_repo.PATH_TO_TRANSFORMERS = os.path.join(tmpdir, "models")

try:
    check_repo.check_models_have_kwargs()
    print("FAIL: Expected exception for top-level class missing **kwargs")
    sys.exit(1)
except Exception as e:
    if "BadModel" in str(e):
        print("PASS: Top-level class missing **kwargs was correctly caught")
        sys.exit(0)
    else:
        print(f"FAIL: Wrong exception: {e}")
        sys.exit(1)
finally:
    check_repo.PATH_TO_TRANSFORMERS = old_path
PYEOF
if [ $? -eq 0 ]; then RESULTS[p2p_toplevel_missing]=1; echo "p2p_toplevel_missing: PASS"; else echo "p2p_toplevel_missing: FAIL"; fi

# ---------- PASS-TO-PASS 2 (0.05): Top-level class with **kwargs passes ----------
# [pr_diff] (0.05): Top-level PreTrainedModel subclass with **kwargs passes check
python3 << 'PYEOF'
import os, sys, tempfile

sys.path.insert(0, "/workspace/transformers/utils")
import check_repo

tmpdir = tempfile.mkdtemp()
model_dir = os.path.join(tmpdir, "models", "goodmodel")
os.makedirs(model_dir)

with open(os.path.join(model_dir, "modeling_goodmodel.py"), "w") as f:
    f.write("""
class PreTrainedModel:
    pass

class GoodModel(PreTrainedModel):
    def forward(self, hidden_states, **kwargs):
        return hidden_states
""".lstrip())

old_path = check_repo.PATH_TO_TRANSFORMERS
check_repo.PATH_TO_TRANSFORMERS = os.path.join(tmpdir, "models")

try:
    check_repo.check_models_have_kwargs()
    print("PASS: Top-level class with **kwargs passes check")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: Unexpected exception: {e}")
    sys.exit(1)
finally:
    check_repo.PATH_TO_TRANSFORMERS = old_path
PYEOF
if [ $? -eq 0 ]; then RESULTS[p2p_toplevel_ok]=1; echo "p2p_toplevel_ok: PASS"; else echo "p2p_toplevel_ok: FAIL"; fi

# ---------- PASS-TO-PASS 3 (0.05): Nested-only file produces no error ----------
# [pr_diff] (0.05): File with only nested classes and no top-level models passes
python3 << 'PYEOF'
import os, sys, tempfile

sys.path.insert(0, "/workspace/transformers/utils")
import check_repo

tmpdir = tempfile.mkdtemp()
model_dir = os.path.join(tmpdir, "models", "nestedonly")
os.makedirs(model_dir)

with open(os.path.join(model_dir, "modeling_nestedonly.py"), "w") as f:
    f.write("""
class PreTrainedModel:
    pass

class Wrapper:
    class InnerModel(PreTrainedModel):
        def forward(self, hidden_states):
            return hidden_states
""".lstrip())

old_path = check_repo.PATH_TO_TRANSFORMERS
check_repo.PATH_TO_TRANSFORMERS = os.path.join(tmpdir, "models")

try:
    check_repo.check_models_have_kwargs()
    print("PASS: Nested-only file produced no error")
    sys.exit(0)
except Exception as e:
    if "InnerModel" in str(e):
        print(f"FAIL: Nested-only class was incorrectly flagged: {e}")
        sys.exit(1)
    else:
        print(f"FAIL: Unexpected error: {e}")
        sys.exit(1)
finally:
    check_repo.PATH_TO_TRANSFORMERS = old_path
PYEOF
if [ $? -eq 0 ]; then RESULTS[p2p_nested_only_ok]=1; echo "p2p_nested_only_ok: PASS"; else echo "p2p_nested_only_ok: FAIL"; fi

# ---------- CONFIG-DERIVED (0.10): ruff check on modified file ----------
# [agent_config] (0.10): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ 9a9997f
ruff check "$CHECK_REPO" --select E,W,F --quiet 2>/dev/null
if [ $? -eq 0 ]; then RESULTS[config_ruff]=1; echo "config_ruff: PASS"; else echo "config_ruff: FAIL"; fi

# ---------- STRUCTURAL (0.05): Anti-stub check ----------
# [pr_diff] (0.05): check_repo.py is not stubbed out
python3 << 'PYEOF'
import sys

with open("/workspace/transformers/utils/check_repo.py") as f:
    lines = len(f.readlines())

if lines < 1000:
    print(f"FAIL: check_repo.py only has {lines} lines (expected >= 1000)")
    sys.exit(1)

print(f"PASS: check_repo.py has {lines} lines")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[struct_antistub]=1; echo "struct_antistub: PASS"; else echo "struct_antistub: FAIL"; fi

# ---------- STRUCTURAL (0.05): File was actually modified ----------
# [pr_diff] (0.05): utils/check_repo.py has changes
python3 << 'PYEOF'
import subprocess, sys

for cmd in [["git", "diff", "HEAD", "--", "utils/check_repo.py"],
            ["git", "diff", "HEAD~1", "--", "utils/check_repo.py"]]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/workspace/transformers")
    if result.stdout.strip():
        print("PASS: utils/check_repo.py was modified")
        sys.exit(0)

print("FAIL: utils/check_repo.py has no changes")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[struct_modified]=1; echo "struct_modified: PASS"; else echo "struct_modified: FAIL"; fi

# ---------- COMPUTE SCORE ----------
SCORE="0.0"
for key in "${!WEIGHTS[@]}"; do
    if [ "${RESULTS[$key]}" -eq 1 ]; then
        SCORE=$(python3 -c "print(round($SCORE + ${WEIGHTS[$key]}, 4))")
    fi
done

echo ""
echo "=== FINAL SCORE ==="
for key in behav_mixed_class behav_mixed_func behav_cache_identity behav_cache_api p2p_toplevel_missing p2p_toplevel_ok p2p_nested_only_ok config_ruff struct_antistub struct_modified; do
    STATUS="FAIL"
    if [ "${RESULTS[$key]}" -eq 1 ]; then STATUS="PASS"; fi
    echo "  $key (${WEIGHTS[$key]}): $STATUS"
done
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
