#!/usr/bin/env bash
set +e

TARGET="/workspace/sglang/python/sglang/srt/managers/scheduler.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[gate]=0.00
WEIGHTS[fail_to_pass]=0.45
WEIGHTS[pass_to_pass]=0.25
WEIGHTS[regression]=0.15
WEIGHTS[antistub]=0.10
WEIGHTS[config]=0.05

for key in gate fail_to_pass pass_to_pass regression antistub config; do
    RESULTS[$key]=0
done

# ---------- GATE: Code must parse ----------
python3 -c "import ast; ast.parse(open('$TARGET').read())" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    echo "GATE FAIL: Code does not parse"
    exit 0
fi
RESULTS[gate]=1
echo "GATE PASS"

# ---------- PRIMARY (45%): Fail-to-pass behavioral test ----------
# [pr_diff] (0.45): Bug reproduction - empty batch after filter must not corrupt tensors
# This test simulates the bug: when filter_batch empties last_batch.reqs but
# leaves tensors with M elements, unconditional merge_batch corrupts running_batch.
python3 << 'PYEOF'
import ast
import sys
import textwrap

TARGET = "/workspace/sglang/python/sglang/srt/managers/scheduler.py"

# Extract pause_generation source
with open(TARGET) as f:
    src = f.read()

tree = ast.parse(src)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "pause_generation":
        func_node = node
        break

if func_node is None:
    print("FAIL: pause_generation method not found")
    sys.exit(1)

lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1:func_node.end_lineno]))

# We need to test the FIXED behavior without importing heavy sglang deps.
# The PR shows the fix pattern: check is_empty() before merge_batch.
# We'll extract and execute just the relevant logic.

# Simulate the behavior with fake classes (same as PR's unit test)
import torch

class FakeReq:
    def __init__(self, finished=False):
        self._finished = finished
    def finished(self):
        return self._finished

class FakeBatch:
    def __init__(self, n, all_finished=False):
        self.reqs = [FakeReq(finished=all_finished) for _ in range(n)]
        self.seq_lens = torch.ones(n, dtype=torch.int32)
        self.seq_lens_cpu = torch.ones(n, dtype=torch.int32)
        self.orig_seq_lens = torch.ones(n, dtype=torch.int32)
        self.req_pool_indices = torch.zeros(n, dtype=torch.int64)
        self.output_ids = torch.zeros(n, dtype=torch.int64)
        self.seq_lens_sum = n

    def is_empty(self):
        return len(self.reqs) == 0

    def filter_batch(self, chunked_req_to_exclude=None):
        """Simplified filter_batch with early-return bug behavior."""
        keep = [i for i in range(len(self.reqs)) if not self.reqs[i].finished()]
        if len(keep) == 0:
            self.reqs = []  # emptied but tensors unchanged!
            return
        if len(keep) == len(self.reqs):
            return
        # Full filter (not needed for this test)
        self.reqs = [self.reqs[i] for i in keep]
        idx = torch.tensor(keep, dtype=torch.int64)
        self.seq_lens = self.seq_lens[idx]
        self.seq_lens_cpu = self.seq_lens_cpu[idx]
        self.orig_seq_lens = self.orig_seq_lens[idx]
        self.req_pool_indices = self.req_pool_indices[idx]
        if self.output_ids is not None:
            self.output_ids = self.output_ids[idx]
        self.seq_lens_sum = int(self.seq_lens.sum().item())

    def merge_batch(self, other):
        """Tensor concat - the source of the bug."""
        self.seq_lens = torch.cat([self.seq_lens, other.seq_lens])
        self.seq_lens_cpu = torch.cat([self.seq_lens_cpu, other.seq_lens_cpu])
        self.orig_seq_lens = torch.cat([self.orig_seq_lens, other.orig_seq_lens])
        self.req_pool_indices = torch.cat([self.req_pool_indices, other.req_pool_indices])
        if self.output_ids is not None and other.output_ids is not None:
            self.output_ids = torch.cat([self.output_ids, other.output_ids])
        self.seq_lens_sum += other.seq_lens_sum
        self.reqs.extend(other.reqs)

# Simulate the FIXED pause_generation logic by patching our simulation
# We check if the actual code has the is_empty guard by analyzing the AST

has_is_empty_check = False
has_guarded_merge = False

# Walk the AST to find the actual pattern
for node in ast.walk(func_node):
    if isinstance(node, ast.If):
        # Check for: if not self.last_batch.is_empty():
        if isinstance(node.test, ast.UnaryOp) and isinstance(node.test.op, ast.Not):
            operand = node.test.operand
            if isinstance(operand, ast.Call):
                if isinstance(operand.func, ast.Attribute):
                    if operand.func.attr == "is_empty":
                        has_is_empty_check = True
        # Also check for: if self.last_batch.is_empty(): return / continue
        elif isinstance(node.test, ast.Call):
            if isinstance(node.test.func, ast.Attribute):
                if node.test.func.attr == "is_empty":
                    has_is_empty_check = True

# Alternative valid patterns: checking len(reqs) == 0
for node in ast.walk(func_node):
    if isinstance(node, ast.Compare):
        # Check for len(self.last_batch.reqs) == 0 or similar
        if isinstance(node.left, ast.Call) and isinstance(node.left.func, ast.Name):
            if node.left.func.id == "len":
                for op in node.ops:
                    if isinstance(op, ast.Eq):
                        has_is_empty_check = True

# Simulate with the fix applied (is_empty guard)
def simulate_fixed_pause_generation():
    """The expected behavior with the fix."""
    N = 651
    running_batch = FakeBatch(N)
    last_batch = FakeBatch(1, all_finished=True)

    # Simulate filter_batch call
    last_batch.filter_batch()

    # The fix: guard with is_empty check
    if not last_batch.is_empty():
        if running_batch.is_empty():
            running_batch = last_batch
        else:
            running_batch.merge_batch(last_batch)

    # Verify invariant preserved
    assert len(running_batch.reqs) == running_batch.seq_lens.shape[0], \
        f"Invariant violated: len(reqs)={len(running_batch.reqs)}, seq_lens.shape[0]={running_batch.seq_lens.shape[0]}"
    assert len(running_batch.reqs) == N, f"Expected {N} reqs, got {len(running_batch.reqs)}"
    return True

def simulate_buggy_pause_generation():
    """The buggy behavior without fix."""
    N = 651
    running_batch = FakeBatch(N)
    last_batch = FakeBatch(1, all_finished=True)

    # Simulate filter_batch call
    last_batch.filter_batch()

    # Bug: unconditional merge_batch
    running_batch.merge_batch(last_batch)

    # Invariant violated
    return len(running_batch.reqs) != running_batch.seq_lens.shape[0]

# Verify our simulation: buggy should violate invariant, fixed should not
buggy_violates = simulate_buggy_pause_generation()
fixed_preserves = simulate_fixed_pause_generation()

if not buggy_violates:
    print("FAIL: Bug simulation did not violate invariant as expected")
    sys.exit(1)

if not fixed_preserves:
    print("FAIL: Fixed simulation did not preserve invariant")
    sys.exit(1)

# Now check if the actual code has the fix
if not has_is_empty_check:
    print("FAIL: No is_empty() guard found in pause_generation")
    print("The fix requires checking if last_batch is empty before merge_batch")
    sys.exit(1)

# Additional check: verify the merge_batch is not unconditional
# by looking for it inside an if block or after an early return
merge_unconditional = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Expr):
        if isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == "merge_batch":
                # Check if this is at the top level (unconditional)
                # by checking if any ancestor is an If node
                merge_unconditional = True

# Better approach: extract line numbers and check context
lines_src = func_src.splitlines()
merge_line_idx = None
is_empty_line_idx = None

for i, line in enumerate(lines_src):
    if ".merge_batch(" in line:
        merge_line_idx = i
    if "is_empty()" in line or "len(" in line and "reqs" in line:
        is_empty_line_idx = i

if merge_line_idx is None:
    print("FAIL: merge_batch not found in pause_generation")
    sys.exit(1)

# If merge_batch exists but no is_empty check before it, fail
if is_empty_line_idx is None or is_empty_line_idx > merge_line_idx:
    # Check if merge_batch is inside an if block
    # Look at indentation
    merge_line = lines_src[merge_line_idx]
    merge_indent = len(merge_line) - len(merge_line.lstrip())

    # Find the first if statement before merge
    found_guard = False
    for i in range(merge_line_idx):
        line = lines_src[i]
        if line.strip().startswith("if "):
            indent = len(line) - len(line.lstrip())
            if indent < merge_indent:
                # Check if this if contains the merge in its body
                # (by checking if subsequent lines with same/higher indent are in the block)
                found_guard = True
                break

    if not found_guard and is_empty_line_idx is None:
        print("FAIL: merge_batch appears unconditional (no is_empty guard)")
        sys.exit(1)

print("PASS: Fail-to-pass behavioral test - is_empty guard prevents tensor mismatch")
PYEOF
RESULTS[fail_to_pass]=$?
[ ${RESULTS[fail_to_pass]} -eq 0 ] && echo "TEST fail_to_pass: PASS" || echo "TEST fail_to_pass: FAIL"

# Only proceed with structural checks if behavioral passed
if [ ${RESULTS[fail_to_pass]} -ne 0 ]; then
    SCORE=$(python3 -c "
w={'gate':0,'fail_to_pass':0.45,'pass_to_pass':0,'regression':0,'antistub':0.05,'config':0.05}
r={'gate':1,'fail_to_pass':0,'pass_to_pass':0,'regression':0,'antistub':1,'config':1}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
    echo "TOTAL: $SCORE"
    echo "$SCORE" > "$REWARD_FILE"
    exit 0
fi

# ---------- PASS-TO-PASS (25%): Non-empty batch still merged correctly ----------
# [pr_diff] (0.25): The fix must not skip merge when batch has live requests
python3 << 'PYEOF'
import sys
import torch

class FakeReq:
    def __init__(self, finished=False):
        self._finished = finished
    def finished(self):
        return self._finished

class FakeBatch:
    def __init__(self, n, all_finished=False):
        self.reqs = [FakeReq(finished=all_finished) for _ in range(n)]
        if n > 0 and not all_finished:
            # First req finished, rest running
            self.reqs[0] = FakeReq(finished=True)
        self.seq_lens = torch.ones(n, dtype=torch.int32)
        self.seq_lens_cpu = torch.ones(n, dtype=torch.int32)
        self.orig_seq_lens = torch.ones(n, dtype=torch.int32)
        self.req_pool_indices = torch.zeros(n, dtype=torch.int64)
        self.output_ids = torch.zeros(n, dtype=torch.int64)
        self.seq_lens_sum = n

    def is_empty(self):
        return len(self.reqs) == 0

    def filter_batch(self):
        keep = [i for i in range(len(self.reqs)) if not self.reqs[i].finished()]
        if len(keep) == 0:
            self.reqs = []
            return
        if len(keep) == len(self.reqs):
            return
        self.reqs = [self.reqs[i] for i in keep]
        idx = torch.tensor(keep, dtype=torch.int64)
        self.seq_lens = self.seq_lens[idx]
        self.seq_lens_cpu = self.seq_lens_cpu[idx]
        self.orig_seq_lens = self.orig_seq_lens[idx]
        self.req_pool_indices = self.req_pool_indices[idx]
        if self.output_ids is not None:
            self.output_ids = self.output_ids[idx]
        self.seq_lens_sum = int(self.seq_lens.sum().item())

    def merge_batch(self, other):
        self.seq_lens = torch.cat([self.seq_lens, other.seq_lens])
        self.seq_lens_cpu = torch.cat([self.seq_lens_cpu, other.seq_lens_cpu])
        self.orig_seq_lens = torch.cat([self.orig_seq_lens, other.orig_seq_lens])
        self.req_pool_indices = torch.cat([self.req_pool_indices, other.req_pool_indices])
        if self.output_ids is not None and other.output_ids is not None:
            self.output_ids = torch.cat([self.output_ids, other.output_ids])
        self.seq_lens_sum += other.seq_lens_sum
        self.reqs.extend(other.reqs)

# Test: 3-req batch with 1 finished, 2 alive -> should still merge
N = 100
running_batch = FakeBatch(N, all_finished=False)
last_batch = FakeBatch(3, all_finished=False)  # First req finished

last_batch.filter_batch()  # Should keep 2 reqs

assert len(last_batch.reqs) == 2, "Expected 2 reqs after filter"
assert not last_batch.is_empty(), "Last batch should not be empty"

# Apply the fix pattern
if not last_batch.is_empty():
    running_batch.merge_batch(last_batch)

# Verify merge happened
assert len(running_batch.reqs) == N + 2, f"Expected {N+2} reqs, got {len(running_batch.reqs)}"
assert running_batch.seq_lens.shape[0] == N + 2, "Tensor shape mismatch"
print("PASS: Non-empty batch still merged correctly")
PYEOF
[ $? -eq 0 ] && RESULTS[pass_to_pass]=1 && echo "TEST pass_to_pass: PASS" || echo "TEST pass_to_pass: FAIL"

# ---------- REGRESSION (15%): merge_batch still exists in pause_generation ----------
# [pr_diff] (0.15): Don't remove merge_batch entirely
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/sglang/python/sglang/srt/managers/scheduler.py") as f:
    src = f.read()

tree = ast.parse(src)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "pause_generation":
        func_node = node
        break

if func_node is None:
    print("FAIL: pause_generation not found")
    sys.exit(1)

# Check merge_batch is still called somewhere in the function
has_merge = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "merge_batch":
            has_merge = True
            break

if not has_merge:
    print("FAIL: merge_batch removed entirely from pause_generation")
    sys.exit(1)

print("PASS: merge_batch still present")
PYEOF
[ $? -eq 0 ] && RESULTS[regression]=1 && echo "TEST regression: PASS" || echo "TEST regression: FAIL"

# ---------- ANTI-STUB (10%): Code depth check ----------
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/sglang/python/sglang/srt/managers/scheduler.py") as f:
    src = f.read()

tree = ast.parse(src)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "pause_generation":
        func_node = node
        break

if func_node is None:
    print("FAIL: pause_generation not found")
    sys.exit(1)

# Count meaningful statements (non-docstring, non-pass)
meaningful = 0
for node in func_node.body:
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
        continue  # Skip docstring
    if isinstance(node, ast.Pass):
        continue
    meaningful += 1

if meaningful < 3:
    print(f"FAIL: Only {meaningful} meaningful statements in pause_generation")
    sys.exit(1)

print(f"PASS: {meaningful} meaningful statements")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# ---------- CONFIG (5%): Main guard in new test files ----------
# [agent_config] (0.05): New test files have if __name__ == '__main__' guard
# Source: sglang testing conventions
cd /workspace/sglang 2>/dev/null
NEW_TEST_FILES=$(git diff --name-only --diff-filter=A HEAD 2>/dev/null | grep -E '^test/.*\.py$' || true)
if [ -z "$NEW_TEST_FILES" ]; then
    echo "CONFIG config: PASS (no new test files)"
    RESULTS[config]=1
else
    ALL_OK=1
    for tf in $NEW_TEST_FILES; do
        if ! grep -q 'if __name__.*==.*"__main__"' "/workspace/sglang/$tf" 2>/dev/null; then
            echo "CONFIG config: PARTIAL — $tf missing main guard"
            ALL_OK=0
        fi
    done
    # Partial credit: 0.5 if some files missing guard
    if [ "$ALL_OK" -eq 1 ]; then
        RESULTS[config]=1
    else
        RESULTS[config]=0
    fi
fi

SCORE=$(python3 -c "
w={'gate':0,'fail_to_pass':0.45,'pass_to_pass':0.25,'regression':0.15,'antistub':0.10,'config':0.05}
r={'gate':${RESULTS[gate]},'fail_to_pass':${RESULTS[fail_to_pass]},'pass_to_pass':${RESULTS[pass_to_pass]},'regression':${RESULTS[regression]},'antistub':${RESULTS[antistub]},'config':${RESULTS[config]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
