#!/usr/bin/env bash
set +e

TOTAL=0
EARNED=0
DETAILS=""

add_check() {
    local name="$1" weight="$2" pass="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        EARNED=$(python3 -c "print($EARNED + $weight)")
        DETAILS="${DETAILS}PASS ($weight): $name\n"
    else
        DETAILS="${DETAILS}FAIL ($weight): $name\n"
    fi
}

cd /repo

# ============================================================
# GATE: Rust syntax — changed files must parse
# ============================================================
GATE_PASS=1
for f in crates/uv-python/src/discovery.rs crates/uv-python/src/installation.rs crates/uv-python/src/lib.rs; do
    if [ -f "$f" ]; then
        rustfmt --check "$f" >/dev/null 2>&1
        RC=$?
        if [ "$RC" -gt 1 ]; then
            echo "GATE FAILED: $f has syntax errors"
            GATE_PASS=0
        fi
    fi
done
if [ "$GATE_PASS" = "0" ]; then
    echo "0.0" > /logs/verifier/reward.txt
    cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true
    exit 0
fi

# ============================================================
# GATE: cargo check -p uv-python — crate must compile
# No points, but blocks all other checks if it fails
# ============================================================
if ! timeout 180 cargo check -p uv-python 2>/dev/null; then
    echo "GATE FAILED: cargo check -p uv-python"
    echo "0.0" > /logs/verifier/reward.txt
    cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true
    exit 0
fi

# ============================================================
# [pr_diff] (0.15): cargo check -p uv — callers compile with updated API
# Verifies that all call sites in the uv crate work with the new API
# ============================================================
timeout 180 cargo check -p uv 2>/dev/null && PASS_UV=1 || PASS_UV=0
add_check "[pr_diff] cargo check -p uv (callers compile)" 0.15 "$PASS_UV"

# ============================================================
# [pr_diff] (0.20): satisfies_python_preference fully removed from codebase
# The old free function must not be defined, exported, or called anywhere
# ============================================================
python3 -c "
import re, sys, os

# 1. Must not be defined as a free function in discovery.rs
with open('crates/uv-python/src/discovery.rs') as f:
    src = f.read()
if re.search(r'^pub\s+fn\s+satisfies_python_preference\b', src, re.MULTILINE):
    print('FAIL: free function still defined in discovery.rs')
    sys.exit(1)

# 2. Must not be re-exported from lib.rs
with open('crates/uv-python/src/lib.rs') as f:
    if 'satisfies_python_preference' in f.read():
        print('FAIL: still exported from lib.rs')
        sys.exit(1)

# 3. Must not be called from any .rs file under crates/uv/
for root, dirs, files in os.walk('crates/uv/src'):
    for fname in files:
        if fname.endswith('.rs'):
            path = os.path.join(root, fname)
            with open(path) as f:
                content = f.read()
            if 'satisfies_python_preference(' in content:
                print(f'FAIL: {path} still calls satisfies_python_preference')
                sys.exit(1)

print('PASS: satisfies_python_preference fully removed')
sys.exit(0)
" && PASS_OLD_REMOVED=1 || PASS_OLD_REMOVED=0
add_check "[pr_diff] satisfies_python_preference fully removed" 0.20 "$PASS_OLD_REMOVED"

# ============================================================
# [pr_diff] (0.15): PythonPreference has a consolidation method taking PythonInstallation
# Accepts ANY method name — just verifies the consolidation pattern exists.
# Also accepts the reverse: PythonInstallation with a method taking PythonPreference.
# ============================================================
python3 -c "
import re, sys

with open('crates/uv-python/src/discovery.rs') as f:
    disc_src = f.read()

# Option A: impl PythonPreference { fn xxx(...PythonInstallation...) }
# We search for any fn inside an impl PythonPreference that mentions PythonInstallation
# Use a broad scan: find impl blocks, then check method signatures
found = False

# Scan for impl PythonPreference blocks
for m in re.finditer(r'impl\s+PythonPreference\s*\{', disc_src):
    start = m.start()
    depth = 0
    i = m.end() - 1
    block = ''
    while i < len(disc_src):
        c = disc_src[i]
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        block += c
        if depth == 0:
            break
        i += 1
    # Check if any fn in this block takes PythonInstallation
    if re.search(r'fn\s+\w+\s*\([^)]*PythonInstallation', block):
        found = True
        break

if found:
    print('PASS: PythonPreference has method taking PythonInstallation')
    sys.exit(0)

# Option B: impl PythonInstallation { fn xxx(...PythonPreference...) }
with open('crates/uv-python/src/installation.rs') as f:
    inst_src = f.read()

for m in re.finditer(r'impl\s+PythonInstallation\s*\{', inst_src):
    start = m.start()
    depth = 0
    i = m.end() - 1
    block = ''
    while i < len(inst_src):
        c = inst_src[i]
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        block += c
        if depth == 0:
            break
        i += 1
    if re.search(r'fn\s+\w+\s*\([^)]*PythonPreference', block):
        found = True
        break

if found:
    print('PASS: PythonInstallation has method taking PythonPreference')
    sys.exit(0)

# Option C: check discovery.rs for any fn taking both PythonInstallation and self
# (might be in a trait impl or different impl block)
if re.search(r'fn\s+\w+\s*\(\s*&?self[^)]*PythonInstallation', disc_src):
    print('PASS: method taking PythonInstallation found in discovery.rs')
    sys.exit(0)

print('FAIL: no consolidated method found on PythonPreference or PythonInstallation')
sys.exit(1)
" && PASS_CONSOLIDATED=1 || PASS_CONSOLIDATED=0
add_check "[pr_diff] preference checking consolidated into method" 0.15 "$PASS_CONSOLIDATED"

# ============================================================
# [pr_diff] (0.15): list.rs — inline PythonPreference variant match removed
# The bug: list.rs reimplemented preference filtering with an inline match
# that didn't account for explicit sources. Any correct fix removes this.
# ============================================================
python3 -c "
import sys

with open('crates/uv/src/commands/python/list.rs') as f:
    src = f.read()

# The old pattern: a filter closure containing a match on PythonPreference
# variants that directly calls is_managed() — this is the buggy code path
has_only_managed = 'PythonPreference::OnlyManaged' in src
has_only_system = 'PythonPreference::OnlySystem' in src
# Both variants present with is_managed() call = inline reimplementation
has_inline_match = has_only_managed and has_only_system and 'is_managed()' in src

if has_inline_match:
    print('FAIL: list.rs still has inline preference variant match')
    sys.exit(1)

print('PASS: inline preference match removed from list.rs')
sys.exit(0)
" && PASS_LIST=1 || PASS_LIST=0
add_check "[pr_diff] list.rs inline preference match removed" 0.15 "$PASS_LIST"

# ============================================================
# [pr_diff] (0.05): is_system_interpreter free function removed
# Logic should be consolidated into a method on PythonInstallation or PythonPreference
# ============================================================
python3 -c "
import re, sys

with open('crates/uv-python/src/discovery.rs') as f:
    src = f.read()

if re.search(r'^pub(\(crate\))?\s+fn\s+is_system_interpreter\b', src, re.MULTILINE):
    print('FAIL: is_system_interpreter free function still exists')
    sys.exit(1)

print('PASS: is_system_interpreter free function removed')
sys.exit(0)
" && PASS_SYSINTERP=1 || PASS_SYSINTERP=0
add_check "[pr_diff] is_system_interpreter consolidated" 0.05 "$PASS_SYSINTERP"

# ============================================================
# [pr_diff] (0.05): PythonInstallation has is_managed method
# Consolidation: installation should expose whether it's managed
# ============================================================
python3 -c "
import re, sys

with open('crates/uv-python/src/installation.rs') as f:
    src = f.read()

# Accept is_managed, is_managed_installation, or similar
if re.search(r'fn\s+is_managed\s*\(\s*&self', src):
    print('PASS: PythonInstallation has is_managed method')
    sys.exit(0)

# Also accept is_system as the inverse
if re.search(r'fn\s+is_system\s*\(\s*&self', src):
    print('PASS: PythonInstallation has is_system method')
    sys.exit(0)

# Check discovery.rs too in case method was placed in an impl block there
with open('crates/uv-python/src/discovery.rs') as f:
    disc = f.read()

# Look in impl PythonInstallation blocks
for block_match in re.finditer(r'impl\s+PythonInstallation', disc):
    region = disc[block_match.start():block_match.start()+2000]
    if re.search(r'fn\s+is_managed\s*\(\s*&self', region):
        print('PASS: PythonInstallation::is_managed in discovery.rs')
        sys.exit(0)

print('FAIL: PythonInstallation lacks is_managed/is_system method')
sys.exit(1)
" && PASS_IS_MANAGED=1 || PASS_IS_MANAGED=0
add_check "[pr_diff] PythonInstallation has is_managed method" 0.05 "$PASS_IS_MANAGED"

# ============================================================
# [pr_diff] (0.05): project/mod.rs updated — no old free function call
# ============================================================
python3 -c "
import sys

with open('crates/uv/src/commands/project/mod.rs') as f:
    src = f.read()

if 'satisfies_python_preference(' in src:
    print('FAIL: project/mod.rs still calls satisfies_python_preference')
    sys.exit(1)

print('PASS: project/mod.rs caller updated')
sys.exit(0)
" && PASS_PROJECT=1 || PASS_PROJECT=0
add_check "[pr_diff] project/mod.rs caller updated" 0.05 "$PASS_PROJECT"

# ============================================================
# [repo_tests] (0.10): lib.rs still exports core types (P2P regression)
# ============================================================
python3 -c "
import sys

with open('crates/uv-python/src/lib.rs') as f:
    src = f.read()

required = ['PythonPreference', 'PythonSource', 'find_python_installations', 'PythonRequest']
missing = [e for e in required if e not in src]
if missing:
    print(f'FAIL: lib.rs missing exports: {missing}')
    sys.exit(1)

print('PASS: lib.rs still exports core types')
sys.exit(0)
" && PASS_P2P=1 || PASS_P2P=0
add_check "[repo_tests] lib.rs still exports core types" 0.10 "$PASS_P2P"

# ============================================================
# [agent_config] (0.05): No unwrap/panic in PythonPreference impl — CLAUDE.md:7
# "AVOID using panic!, unreachable!, .unwrap(), unsafe code"
# ============================================================
python3 -c "
import sys

with open('crates/uv-python/src/discovery.rs') as f:
    src = f.read()

# Extract impl PythonPreference blocks
in_impl = False
brace_depth = 0
impl_content = []
for line in src.split('\n'):
    if 'impl PythonPreference' in line:
        in_impl = True
        brace_depth = 0
    if in_impl:
        brace_depth += line.count('{') - line.count('}')
        impl_content.append(line)
        if brace_depth <= 0 and len(impl_content) > 1:
            break

impl_text = '\n'.join(impl_content)
issues = []
for pattern in ['.unwrap()', 'panic!', 'unreachable!']:
    if pattern in impl_text:
        issues.append(pattern)

if issues:
    print(f'FAIL: Found {issues} in PythonPreference impl')
    sys.exit(1)

print('PASS: No unwrap/panic in PythonPreference methods')
sys.exit(0)
" && PASS_CONFIG=1 || PASS_CONFIG=0
add_check "[agent_config] No unwrap/panic in preference methods — CLAUDE.md:7" 0.05 "$PASS_CONFIG"

# ============================================================
# Compute final reward
# ============================================================
REWARD=$(python3 -c "print(round($EARNED, 2))")
echo -e "\n=== Results ==="
echo -e "$DETAILS"
echo "Total: $EARNED / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt
cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true

# Write reward.json
python3 -c "
import json
behavioral = round($PASS_UV * 0.15 + $PASS_P2P * 0.10, 2)
structural = round($PASS_OLD_REMOVED * 0.20 + $PASS_CONSOLIDATED * 0.15 + $PASS_LIST * 0.15 + $PASS_SYSINTERP * 0.05 + $PASS_IS_MANAGED * 0.05 + $PASS_PROJECT * 0.05, 2)
config = round($PASS_CONFIG * 0.05, 2)
print(json.dumps({
    'reward': $REWARD,
    'behavioral': behavioral,
    'structural': structural,
    'regression': round($PASS_P2P * 0.10, 2),
    'config': config,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json
cp /logs/verifier/reward.json reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
