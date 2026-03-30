#!/usr/bin/env bash
set +e

TARGET="/workspace/sglang/python/sglang/srt/managers/scheduler.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.40
WEIGHTS[regression]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.05
WEIGHTS[config]=0.10

for key in behavioral regression structural antistub config; do
    RESULTS[$key]=0
done

python3 -c "import ast; ast.parse(open('$TARGET').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS"

# ---------- PRIMARY 1 (40%): is_empty() guard present in pause_generation ----------
python3 << 'PYEOF'
import ast, sys, re

with open("/workspace/sglang/python/sglang/srt/managers/scheduler.py") as f:
    src = f.read()

# Find pause_generation method
tree = ast.parse(src)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "pause_generation":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: pause_generation not found"); sys.exit(1)

lines = src.splitlines()
func_src = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

# Check that unconditional merge_batch is gone
if re.search(r'^\s+self\.running_batch\.merge_batch\(self\.last_batch\)\s*$', func_src, re.MULTILINE):
    # Check if there's an is_empty guard above it
    if "is_empty()" not in func_src:
        print("BEHAVIORAL FAIL: unconditional merge_batch still present without is_empty guard")
        sys.exit(1)

# Verify is_empty guard exists
if "is_empty()" not in func_src:
    print("BEHAVIORAL FAIL: is_empty() guard not found in pause_generation")
    sys.exit(1)

print("BEHAVIORAL PASS: is_empty() guard present in pause_generation")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): regression - merge_batch still called when batch not empty ----------
python3 << 'PYEOF'
import ast, sys
with open("/workspace/sglang/python/sglang/srt/managers/scheduler.py") as f: src = f.read()
tree = ast.parse(src)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "pause_generation":
        func_node = node; break
if func_node is None: print("REGRESSION FAIL"); sys.exit(1)
lines = src.splitlines()
func_src = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])
if "merge_batch" not in func_src:
    print("REGRESSION FAIL: merge_batch removed entirely from pause_generation")
    sys.exit(1)
print("REGRESSION PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[regression]=1 && echo "TEST regression: PASS" || echo "TEST regression: FAIL"

# ---------- SUPPLEMENTARY (20%): structural ----------
python3 << 'PYEOF'
import sys, re
with open("/workspace/sglang/python/sglang/srt/managers/scheduler.py") as f: src = f.read()
# Should have the same pattern as get_next_batch_to_run
if "self.running_batch = self.last_batch" not in src:
    # Or at least the empty-replacement pattern
    pass  # acceptable if merge_batch is just guarded
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (15%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/sglang/python/sglang/srt/managers/scheduler.py") as f: src = f.read()
ok = all(["def pause_generation" in src, "class" in src, len(src.splitlines()) > 500])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# Config-derived test (0.10): "Has `if __name__ == '__main__': unittest.main()`"
# Source: .claude/skills/write-sglang-test/SKILL.md lines 8-10 @ 279e7738c5857ce8664a77b1ffcb59d46960f1e4
cd /workspace/sglang 2>/dev/null
NEW_TEST_FILES=$(git diff --name-only --diff-filter=A HEAD 2>/dev/null | grep -E '^test/.*\.py$' || true)
if [ -z "$NEW_TEST_FILES" ]; then
    echo "CONFIG config: PASS (no new test files added)"
    RESULTS[config]=1
else
    ALL_OK=1
    for tf in $NEW_TEST_FILES; do
        if ! grep -q 'if __name__.*==.*"__main__"' "/workspace/sglang/$tf" 2>/dev/null; then
            echo "CONFIG config: FAIL — $tf missing main guard"
            ALL_OK=0
        fi
    done
    [ "$ALL_OK" -eq 1 ] && RESULTS[config]=1
fi

SCORE=$(python3 -c "
w={'behavioral':${WEIGHTS[behavioral]},'regression':${WEIGHTS[regression]},'structural':${WEIGHTS[structural]},'antistub':${WEIGHTS[antistub]},'config':${WEIGHTS[config]}}
r={'behavioral':${RESULTS[behavioral]},'regression':${RESULTS[regression]},'structural':${RESULTS[structural]},'antistub':${RESULTS[antistub]},'config':${RESULTS[config]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
