#!/usr/bin/env bash
set -euo pipefail

REWARD=0

add_score() {
    REWARD=$(python3 -c "print($REWARD + $1)")
}

###############################################################################
# GATE: Syntax check — all 4 files must be valid Python
###############################################################################
# [pr_diff] (0.00): All modified files must be valid Python
GATE_PASS=true
for f in \
    python/sglang/jit_kernel/benchmark/bench_cast.py \
    python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py \
    python/sglang/jit_kernel/tests/test_cast.py \
    python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py; do
    if ! python3 -c "import ast; ast.parse(open('/workspace/$f').read())" 2>/dev/null; then
        echo "GATE FAIL: syntax error in $f"
        GATE_PASS=false
    fi
done

if [ "$GATE_PASS" = "false" ]; then
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASS: all files have valid syntax"

###############################################################################
# BEHAVIORAL FAIL-TO-PASS (0.65 total)
# These tests FAIL on buggy code, PASS on fixed code.
# We use the actual ci_register AST parser to verify registration works.
###############################################################################

# [pr_diff] (0.20): bench_cast.py is discoverable by ci_register AST parser
cat > /tmp/test_bench_cast_reg.py << 'PYEOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ci_register", "/workspace/python/sglang/test/ci/ci_register.py")
ci_register = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci_register)
ut_parse_one_file = ci_register.ut_parse_one_file

regs = ut_parse_one_file("/workspace/python/sglang/jit_kernel/benchmark/bench_cast.py")
if not regs:
    print("FAIL: no registrations found in bench_cast.py")
    sys.exit(1)

suites = [r.suite for r in regs]
if "stage-b-kernel-benchmark-1-gpu-large" not in suites:
    print(f"FAIL: expected benchmark suite, got {suites}")
    sys.exit(1)

print("PASS: bench_cast.py registered for benchmark suite")
PYEOF

if python3 /tmp/test_bench_cast_reg.py 2>&1; then
    add_score 0.20
    echo "PASS (0.20): bench_cast.py CI registration"
else
    echo "FAIL (0.20): bench_cast.py CI registration"
fi

# [pr_diff] (0.20): bench_fused_qknorm_rope.py is discoverable by ci_register AST parser
cat > /tmp/test_bench_fused_reg.py << 'PYEOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ci_register", "/workspace/python/sglang/test/ci/ci_register.py")
ci_register = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci_register)
ut_parse_one_file = ci_register.ut_parse_one_file

regs = ut_parse_one_file("/workspace/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py")
if not regs:
    print("FAIL: no registrations found in bench_fused_qknorm_rope.py")
    sys.exit(1)

suites = [r.suite for r in regs]
if "stage-b-kernel-benchmark-1-gpu-large" not in suites:
    print(f"FAIL: expected benchmark suite, got {suites}")
    sys.exit(1)

print("PASS: bench_fused_qknorm_rope.py registered for benchmark suite")
PYEOF

if python3 /tmp/test_bench_fused_reg.py 2>&1; then
    add_score 0.20
    echo "PASS (0.20): bench_fused_qknorm_rope.py CI registration"
else
    echo "FAIL (0.20): bench_fused_qknorm_rope.py CI registration"
fi

# [pr_diff] (0.15): test_cast.py is discoverable and registered for kernel unit suite
cat > /tmp/test_cast_reg.py << 'PYEOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ci_register", "/workspace/python/sglang/test/ci/ci_register.py")
ci_register = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci_register)
ut_parse_one_file = ci_register.ut_parse_one_file

regs = ut_parse_one_file("/workspace/python/sglang/jit_kernel/tests/test_cast.py")
if not regs:
    print("FAIL: no registrations found in test_cast.py")
    sys.exit(1)

suites = [r.suite for r in regs]
if "stage-b-kernel-unit-1-gpu-large" not in suites:
    print(f"FAIL: expected kernel unit suite, got {suites}")
    sys.exit(1)

print("PASS: test_cast.py registered for kernel unit suite")
PYEOF

if python3 /tmp/test_cast_reg.py 2>&1; then
    add_score 0.15
    echo "PASS (0.15): test_cast.py CI registration"
else
    echo "FAIL (0.15): test_cast.py CI registration"
fi

# [pr_diff] (0.10): test_fused_qknorm_rope.py is discoverable and registered for kernel unit suite
cat > /tmp/test_fused_reg.py << 'PYEOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ci_register", "/workspace/python/sglang/test/ci/ci_register.py")
ci_register = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci_register)
ut_parse_one_file = ci_register.ut_parse_one_file

regs = ut_parse_one_file("/workspace/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py")
if not regs:
    print("FAIL: no registrations found in test_fused_qknorm_rope.py")
    sys.exit(1)

suites = [r.suite for r in regs]
if "stage-b-kernel-unit-1-gpu-large" not in suites:
    print(f"FAIL: expected kernel unit suite, got {suites}")
    sys.exit(1)

print("PASS: test_fused_qknorm_rope.py registered for kernel unit suite")
PYEOF

if python3 /tmp/test_fused_reg.py 2>&1; then
    add_score 0.10
    echo "PASS (0.10): test_fused_qknorm_rope.py CI registration"
else
    echo "FAIL (0.10): test_fused_qknorm_rope.py CI registration"
fi

###############################################################################
# PASS-TO-PASS (0.15 total)
# Regression: collect_tests on all 4 files must not raise ValueError
###############################################################################

# [pr_diff] (0.10): collect_tests() succeeds without ValueError on all 4 files
cat > /tmp/test_collect_all.py << 'PYEOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ci_register", "/workspace/python/sglang/test/ci/ci_register.py")
ci_register = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci_register)
collect_tests = ci_register.collect_tests

files = [
    "/workspace/python/sglang/jit_kernel/benchmark/bench_cast.py",
    "/workspace/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py",
    "/workspace/python/sglang/jit_kernel/tests/test_cast.py",
    "/workspace/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py",
]

try:
    regs = collect_tests(files, sanity_check=True)
except ValueError as e:
    print(f"FAIL: collect_tests raised ValueError: {e}")
    sys.exit(1)

if len(regs) < 4:
    print(f"FAIL: expected at least 4 registrations, got {len(regs)}")
    sys.exit(1)

print(f"PASS: collect_tests found {len(regs)} registrations across 4 files")
PYEOF

if python3 /tmp/test_collect_all.py 2>&1; then
    add_score 0.10
    echo "PASS (0.10): collect_tests succeeds on all 4 files"
else
    echo "FAIL (0.10): collect_tests succeeds on all 4 files"
fi

# [pr_diff] (0.05): est_time values are positive numbers for all registrations
cat > /tmp/test_est_times.py << 'PYEOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ci_register", "/workspace/python/sglang/test/ci/ci_register.py")
ci_register = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci_register)
collect_tests = ci_register.collect_tests

files = [
    "/workspace/python/sglang/jit_kernel/benchmark/bench_cast.py",
    "/workspace/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py",
    "/workspace/python/sglang/jit_kernel/tests/test_cast.py",
    "/workspace/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py",
]

try:
    regs = collect_tests(files, sanity_check=False)
except Exception:
    regs = []

for r in regs:
    if r.est_time <= 0:
        print(f"FAIL: {r.filename} has non-positive est_time: {r.est_time}")
        sys.exit(1)

if not regs:
    print("FAIL: no registrations to check")
    sys.exit(1)

print(f"PASS: all {len(regs)} registrations have positive est_time")
PYEOF

if python3 /tmp/test_est_times.py 2>&1; then
    add_score 0.05
    echo "PASS (0.05): est_time values are positive"
else
    echo "FAIL (0.05): est_time values are positive"
fi

###############################################################################
# STRUCTURAL / CONFIG-DERIVED (0.20 total)
###############################################################################

# [agent_config] (0.10): Registration uses literal values (AST-parseable)
# WHY AST: ci_register uses AST parsing — computed/variable args would break discovery.
# ".claude/skills/add-jit-kernel/SKILL.md:433" @ 6047d2c
# "Keep est_time and suite as literal values. run_suite.py collects them from the file AST"
cat > /tmp/test_literal_values.py << 'PYEOF'
import ast
import sys

FILES = [
    "/workspace/python/sglang/jit_kernel/benchmark/bench_cast.py",
    "/workspace/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py",
    "/workspace/python/sglang/jit_kernel/tests/test_cast.py",
    "/workspace/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py",
]

for filepath in FILES:
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)

    found_register = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id.startswith("register_") and node.func.id.endswith("_ci"):
                found_register = True
                # Check all keyword args are literals
                for kw in node.keywords:
                    if not isinstance(kw.value, ast.Constant):
                        print(f"FAIL: {filepath}: keyword '{kw.arg}' is not a literal")
                        sys.exit(1)
                # Check positional args are literals
                for arg in node.args:
                    if not isinstance(arg, ast.Constant):
                        print(f"FAIL: {filepath}: positional arg is not a literal")
                        sys.exit(1)

    if not found_register:
        print(f"FAIL: {filepath}: no register_*_ci() call found")
        sys.exit(1)

print("PASS: all registration calls use literal values")
PYEOF

if python3 /tmp/test_literal_values.py 2>&1; then
    add_score 0.10
    echo "PASS (0.10): registration uses literal values"
else
    echo "FAIL (0.10): registration uses literal values"
fi

# [pr_diff] (0.05): Anti-stub — each file has register_cuda_ci (not a generic no-op)
cat > /tmp/test_antistub.py << 'PYEOF'
import sys

FILES = [
    "/workspace/python/sglang/jit_kernel/benchmark/bench_cast.py",
    "/workspace/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py",
    "/workspace/python/sglang/jit_kernel/tests/test_cast.py",
    "/workspace/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py",
]

for filepath in FILES:
    with open(filepath) as f:
        content = f.read()
    if "register_cuda_ci" not in content:
        print(f"FAIL: {filepath} missing register_cuda_ci")
        sys.exit(1)
    if "from sglang.test.ci.ci_register import" not in content:
        print(f"FAIL: {filepath} missing import from ci_register")
        sys.exit(1)

print("PASS: all files import and call register_cuda_ci")
PYEOF

if python3 /tmp/test_antistub.py 2>&1; then
    add_score 0.05
    echo "PASS (0.05): anti-stub check"
else
    echo "FAIL (0.05): anti-stub check"
fi

# [agent_config] (0.05): Benchmark files use benchmark suite, test files use unit suite
# ".claude/skills/write-sglang-test/SKILL.md" @ 6047d2c
# "JIT kernel correctness → stage-b-kernel-unit-1-gpu-large"
# "JIT kernel benchmarks → stage-b-kernel-benchmark-1-gpu-large"
cat > /tmp/test_correct_suites.py << 'PYEOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ci_register", "/workspace/python/sglang/test/ci/ci_register.py")
ci_register = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci_register)
ut_parse_one_file = ci_register.ut_parse_one_file

# Benchmark files should use benchmark suite
for bench_file in [
    "/workspace/python/sglang/jit_kernel/benchmark/bench_cast.py",
    "/workspace/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py",
]:
    regs = ut_parse_one_file(bench_file)
    suites = [r.suite for r in regs]
    for s in suites:
        if "kernel-unit" in s:
            print(f"FAIL: {bench_file} registered for unit suite '{s}' instead of benchmark suite")
            sys.exit(1)

# Test files should use unit suite (at minimum)
for test_file in [
    "/workspace/python/sglang/jit_kernel/tests/test_cast.py",
    "/workspace/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py",
]:
    regs = ut_parse_one_file(test_file)
    suites = [r.suite for r in regs]
    has_unit = any("kernel-unit" in s or "kernel" in s for s in suites if "benchmark" not in s)
    if not has_unit:
        print(f"FAIL: {test_file} not registered for any kernel unit/test suite, got {suites}")
        sys.exit(1)

print("PASS: benchmark files use benchmark suite, test files use unit suite")
PYEOF

if python3 /tmp/test_correct_suites.py 2>&1; then
    add_score 0.05
    echo "PASS (0.05): correct suite assignment"
else
    echo "FAIL (0.05): correct suite assignment"
fi

###############################################################################
# Write reward
###############################################################################

echo ""
echo "=== SCORE: $REWARD / 1.0 ==="
echo "$REWARD" > /logs/verifier/reward.txt
python3 -c "
import json
json.dump({
    'reward': $REWARD,
    'behavioral': 0.65,
    'regression': 0.15,
    'structural': 0.20,
    'config': 0.10,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
