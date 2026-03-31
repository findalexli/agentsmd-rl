#!/usr/bin/env bash
set -euo pipefail

TOTAL=0.0
REWARD=0.0

add() {
    REWARD=$(python3 -c "print(round($REWARD + $1, 4))")
    TOTAL=$(python3 -c "print(round($TOTAL + $2, 4))")
}

cd /repo

# Build ty if not already built
if ! command -v ty &>/dev/null && [ ! -f target/debug/ty ]; then
    cargo build --bin ty 2>&1 | tail -3
fi
TY="${TY:-$(command -v ty || echo target/debug/ty)}"

# ========== GATE: Syntax check ==========
# [pr_diff] (0.00): Rust code must compile
if cargo check --bin ty 2>&1 | tail -5; then
    echo "GATE PASS: compilation succeeds"
else
    echo "GATE FAIL: compilation failed"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ========== Behavioral: Fail-to-pass tests (0.65 total) ==========

# Test 1: Function-based transformer with **kwargs respects frozen=True
# [pr_diff] (0.25): frozen param via **kwargs in function transformer
cat > /tmp/test_func_kwargs.py <<'EOF'
from typing import dataclass_transform, Callable

@dataclass_transform()
def create_model[T: type](**kwargs) -> Callable[[T], T]:
    raise NotImplementedError

@create_model(frozen=True)
class Frozen:
    name: str

f = Frozen("Alice")
f.name = "Bob"
EOF

FUNC_OUT=$("$TY" check /tmp/test_func_kwargs.py 2>&1 || true)
if echo "$FUNC_OUT" | grep -q "invalid-assignment"; then
    echo "PASS: function-based **kwargs frozen detection"
    add 0.25 0.25
else
    echo "FAIL: function-based **kwargs frozen detection"
    echo "Output: $FUNC_OUT"
    add 0.0 0.25
fi

# Test 2: Metaclass-based transformer with **kwargs respects frozen=True
# [pr_diff] (0.20): frozen param via **kwargs in metaclass transformer
cat > /tmp/test_meta_kwargs.py <<'EOF'
from typing import dataclass_transform

@dataclass_transform()
class ModelMeta(type):
    def __new__(cls, name, bases, namespace, **kwargs): ...

class ModelBase(metaclass=ModelMeta): ...

class Frozen(ModelBase, frozen=True):
    name: str

f = Frozen(name="test")
f.name = "new"
EOF

META_OUT=$("$TY" check /tmp/test_meta_kwargs.py 2>&1 || true)
if echo "$META_OUT" | grep -q "invalid-assignment"; then
    echo "PASS: metaclass-based **kwargs frozen detection"
    add 0.20 0.20
else
    echo "FAIL: metaclass-based **kwargs frozen detection"
    echo "Output: $META_OUT"
    add 0.0 0.20
fi

# Test 3: Base-class-based transformer with **kwargs respects frozen=True
# [pr_diff] (0.20): frozen param via **kwargs in base-class transformer
cat > /tmp/test_base_kwargs.py <<'EOF'
from typing import dataclass_transform

@dataclass_transform()
class ModelBase:
    def __init_subclass__(cls, **kwargs): ...

class Frozen(ModelBase, frozen=True):
    name: str

f = Frozen(name="test")
f.name = "new"
EOF

BASE_OUT=$("$TY" check /tmp/test_base_kwargs.py 2>&1 || true)
if echo "$BASE_OUT" | grep -q "invalid-assignment"; then
    echo "PASS: base-class-based **kwargs frozen detection"
    add 0.20 0.20
else
    echo "FAIL: base-class-based **kwargs frozen detection"
    echo "Output: $BASE_OUT"
    add 0.0 0.20
fi

# ========== Pass-to-pass: Existing explicit-param transformers still work (0.15) ==========

# Test 4: Explicit params still recognized (existing behavior must not regress)
# [pr_diff] (0.15): explicit frozen param still works
cat > /tmp/test_explicit.py <<'EOF'
from typing import dataclass_transform

@dataclass_transform()
def create_model(*, frozen: bool = False): ...

@create_model(frozen=True)
class ExplicitFrozen:
    name: str

f = ExplicitFrozen(name="test")
f.name = "new"
EOF

EXPLICIT_OUT=$("$TY" check /tmp/test_explicit.py 2>&1 || true)
if echo "$EXPLICIT_OUT" | grep -q "invalid-assignment"; then
    echo "PASS: explicit params still work"
    add 0.15 0.15
else
    echo "FAIL: explicit params regression"
    echo "Output: $EXPLICIT_OUT"
    add 0.0 0.15
fi

# ========== Structural: Anti-stub check (0.05) ==========
# [pr_diff] (0.05): bind.rs DATACLASS_FLAGS loop is not stubbed out
if grep -q 'DATACLASS_FLAGS' crates/ty_python_semantic/src/types/call/bind.rs; then
    echo "PASS: DATACLASS_FLAGS loop preserved"
    add 0.05 0.05
else
    echo "FAIL: DATACLASS_FLAGS loop missing (stubbed out)"
    add 0.0 0.05
fi

# ========== Config-derived checks (0.15) ==========

# [agent_config] (0.05): "All changes must be tested" — AGENTS.md:72
# Check that the mdtest file for dataclass_transform was updated
if grep -qi 'kwargs' crates/ty_python_semantic/resources/mdtest/dataclasses/dataclass_transform.md 2>/dev/null; then
    echo "PASS: mdtest updated with kwargs tests"
    add 0.05 0.05
else
    echo "FAIL: no mdtest update for kwargs"
    add 0.0 0.05
fi

# [agent_config] (0.05): "Try hard to avoid patterns that require panic!, unreachable!, or .unwrap()" — AGENTS.md:79
# Verify the changed code in bind.rs doesn't introduce unwrap/panic in the dataclass section
BIND_SECTION=$(sed -n '/DATACLASS_FLAGS/,/dataclass_params = DataclassParams::new/p' crates/ty_python_semantic/src/types/call/bind.rs)
if echo "$BIND_SECTION" | grep -qE '\.unwrap\(\)|panic!\(|unreachable!\(' 2>/dev/null; then
    echo "FAIL: unwrap/panic in dataclass flag resolution"
    add 0.0 0.05
else
    echo "PASS: no unwrap/panic in dataclass flag resolution"
    add 0.05 0.05
fi

# [agent_config] (0.05): "Rust imports should always go at the top of the file, never locally in functions" — AGENTS.md:76
# Check bind.rs doesn't have local use statements inside functions
if python3 -c "
import re
with open('crates/ty_python_semantic/src/types/call/bind.rs') as f:
    content = f.read()
# Find 'use' statements that appear inside function bodies (indented)
local_uses = re.findall(r'^\s{8,}use\s+', content, re.MULTILINE)
# Filter out ones in macro invocations
exit(1 if local_uses else 0)
" 2>/dev/null; then
    echo "FAIL: local use statements found in bind.rs"
    add 0.0 0.05
else
    echo "PASS: no local use statements in bind.rs"
    add 0.05 0.05
fi

# ========== Summary ==========
echo ""
echo "Total reward: $REWARD / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt

# Compute component scores for reward.json
python3 -c "
import json
reward = $REWARD
# behavioral = tests 1-3 (0.65 max)
# regression = test 4 (0.15 max)
# config = tests 6-8 (0.15 max)
# structural = test 5 (0.05 max)
print(json.dumps({
    'reward': reward,
    'behavioral': min(reward, 0.65),
    'regression': 0.0,
    'config': 0.0,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json 2>/dev/null || echo "{\"reward\": $REWARD}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
