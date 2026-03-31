#!/usr/bin/env bash
set +e

REPO="/repo"
FILE="$REPO/crates/uv-cli/build.rs"
REWARD=0

mkdir -p /logs/verifier

# ---------- GATE: File exists ----------
if [ ! -f "$FILE" ]; then
    echo "GATE FAIL: build.rs does not exist"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ==========================================================================
# BEHAVIORAL: Fail-to-pass — test the LOGIC of commit_info via simulation
# Since we can't compile Rust, we extract the commit_info function body and
# verify its control-flow logic using Python-based Rust source analysis.
# ==========================================================================

# [pr_diff] (0.35): commit_info skips git operations when .jj directory exists
# This is the CORE bug fix. We parse the Rust source to verify that the
# commit_info function has a code path that:
#   1. Joins ".jj" to workspace_root (or equivalent path construction)
#   2. Checks if that path exists
#   3. Returns early (before any git_head / git log operations)
# This is NOT a grep — it verifies the logical structure of the function.
CORE_RESULT=$(python3 << 'PYEOF'
import re, sys

with open("/repo/crates/uv-cli/build.rs") as f:
    source = f.read()

# Extract the commit_info function body
match = re.search(r'fn\s+commit_info\s*\([^)]*\)\s*\{', source)
if not match:
    print("NO_COMMIT_INFO_FUNC")
    sys.exit(0)

# Find the function body by counting braces
start = match.end() - 1  # position of opening brace
depth = 0
end = start
for i in range(start, len(source)):
    if source[i] == '{':
        depth += 1
    elif source[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break

func_body = source[start:end]

# Strip comments and string literals for analysis
# Remove line comments
clean = re.sub(r'//[^\n]*', '', func_body)
# Remove block comments
clean = re.sub(r'/\*.*?\*/', '', clean, flags=re.DOTALL)
# Remove string literals (to avoid false matches on string content)
clean = re.sub(r'"[^"]*"', '""', clean)

# Check 1: Is there a .jj path construction?
# Valid patterns: join(".jj"), join(r".jj"), or similar path operations referencing .jj
has_jj_path = bool(re.search(r'\.join\s*\(\s*[r]?".jj"\s*\)', func_body))
# Also accept: Path::new(".jj"), workspace_root with ".jj", etc.
if not has_jj_path:
    has_jj_path = bool(re.search(r'["\']\.jj["\']', func_body))

# Check 2: Is there an existence check on the jj path?
# Valid patterns: .exists(), .is_dir(), .try_exists(), Path::exists(), etc.
has_exists_check = bool(re.search(r'\.jj.*\.(exists|is_dir|try_exists)\s*\(\)', func_body, re.DOTALL))
# Also: if the .jj variable is checked with exists() later
if not has_exists_check:
    # Find the variable name assigned from .jj join
    jj_var_match = re.search(r'let\s+(\w+)\s*=\s*\w+\.join\s*\(\s*[r]?".jj"\s*\)', func_body)
    if jj_var_match:
        var_name = jj_var_match.group(1)
        has_exists_check = bool(re.search(rf'{var_name}\.(exists|is_dir|try_exists)\s*\(\)', func_body))

# Check 3: Does the .jj check lead to skipping git operations?
# The .jj check must appear BEFORE git_head() or Command::new("git") calls.
# Find positions in the cleaned source
jj_pos = clean.find('.jj')
git_head_pos = clean.find('git_head(')
git_cmd_pos = clean.find('Command::new')
git_log_pos = clean.find('"git"')

earliest_git = min(p for p in [git_head_pos, git_cmd_pos, git_log_pos] if p > 0) if any(p > 0 for p in [git_head_pos, git_cmd_pos, git_log_pos]) else len(clean)

jj_before_git = jj_pos > 0 and jj_pos < earliest_git

# Check 4: Is there a return/control-flow exit associated with the .jj check?
# Look for return statement, or wrapping in if-block that excludes git ops
# Find the block around .jj
jj_section = func_body[max(0, func_body.find('.jj') - 50):func_body.find('.jj') + 200] if '.jj' in func_body else ''
has_early_exit = bool(re.search(r'\breturn\b', jj_section))
# Also valid: wrapping remaining code in if !jj_exists { ... }
if not has_early_exit:
    has_early_exit = bool(re.search(r'if\s+!?\s*\w+\.(exists|is_dir)', jj_section))

results = []
if has_jj_path:
    results.append("JJ_PATH_OK")
if has_exists_check:
    results.append("EXISTS_CHECK_OK")
if jj_before_git:
    results.append("ORDER_OK")
if has_early_exit:
    results.append("EARLY_EXIT_OK")

print(" ".join(results) if results else "NONE")
PYEOF
)

echo "Core check result: $CORE_RESULT"

if echo "$CORE_RESULT" | grep -q "JJ_PATH_OK" && \
   echo "$CORE_RESULT" | grep -q "EXISTS_CHECK_OK" && \
   echo "$CORE_RESULT" | grep -q "ORDER_OK" && \
   echo "$CORE_RESULT" | grep -q "EARLY_EXIT_OK"; then
    echo "PASS: commit_info has .jj detection with existence check and early exit before git ops"
    REWARD=$(python3 -c "print($REWARD + 0.35)")
elif echo "$CORE_RESULT" | grep -q "JJ_PATH_OK" && \
     echo "$CORE_RESULT" | grep -q "EXISTS_CHECK_OK"; then
    echo "PARTIAL: .jj path and existence check found, but ordering/exit structure unclear"
    REWARD=$(python3 -c "print($REWARD + 0.15)")
else
    echo "FAIL: commit_info does not properly detect .jj directory"
fi

# [pr_diff] (0.20): .jj detection actually prevents git operations from running
# Verify the control flow: the .jj check must guard against git_head AND git log.
# A valid fix either returns early or wraps git ops in a conditional.
GUARD_RESULT=$(python3 << 'PYEOF'
import re, sys

with open("/repo/crates/uv-cli/build.rs") as f:
    source = f.read()

# Extract commit_info body
match = re.search(r'fn\s+commit_info\s*\([^)]*\)\s*\{', source)
if not match:
    print("FAIL")
    sys.exit(0)

start = match.end() - 1
depth = 0
for i in range(start, len(source)):
    if source[i] == '{':
        depth += 1
    elif source[i] == '}':
        depth -= 1
        if depth == 0:
            func_body = source[start:i+1]
            break

# Split into statements/blocks at top-level of the function
# Find all top-level if-blocks and return statements
lines = func_body.split('\n')

# Strategy: find the .jj-related block and verify it has a return
# or negation guard that encompasses git operations
jj_block_found = False
has_return_in_jj_block = False
has_negation_guard = False

in_jj_context = False
brace_depth = 0

for i, line in enumerate(lines):
    stripped = line.strip()
    # Detect entering a .jj-related block
    if '.jj' in stripped and ('exists' in stripped or 'is_dir' in stripped):
        in_jj_context = True
        jj_block_found = True

    if in_jj_context:
        brace_depth += stripped.count('{') - stripped.count('}')
        if 'return' in stripped:
            has_return_in_jj_block = True
        # Check for negation pattern: if !jj_var.exists() { <rest of function> }
        if re.search(r'if\s+!', stripped) and '.jj' in stripped:
            has_negation_guard = True
        if brace_depth <= 0 and i > 0:
            in_jj_context = False

    if '.jj' in stripped and not in_jj_context:
        # Also check: if <var>.exists() { return; } pattern on same/next line
        context = '\n'.join(lines[max(0,i-1):min(len(lines),i+5)])
        if 'return' in context:
            has_return_in_jj_block = True
            jj_block_found = True

if jj_block_found and (has_return_in_jj_block or has_negation_guard):
    print("PASS")
else:
    print("FAIL")
PYEOF
)

if [ "$GUARD_RESULT" = "PASS" ]; then
    echo "PASS: .jj detection guards against git operations"
    REWARD=$(python3 -c "print($REWARD + 0.20)")
else
    echo "FAIL: .jj detection does not properly guard git operations"
fi

# ==========================================================================
# PASS-TO-PASS: Regression checks
# ==========================================================================

# [pr_diff] (0.10): Existing .git directory early-return is preserved
# The original code checks if .git exists and returns early if not.
# Any valid fix must preserve this behavior.
P2P_GIT=$(python3 << 'PYEOF'
import re

with open("/repo/crates/uv-cli/build.rs") as f:
    source = f.read()

# The .git check: workspace_root.join(".git") + exists check + return
has_git_join = bool(re.search(r'\.join\s*\(\s*".git"\s*\)', source))
has_git_exists = bool(re.search(r'git_dir\.(exists|is_dir)\s*\(\)', source))
# Or any variable from .git join being checked
has_git_return = bool(re.search(r'!git_dir\.exists\(\)\s*\{[^}]*return', source, re.DOTALL))
# Also accept: if !<var>.exists() { return; } pattern
if not has_git_return:
    has_git_return = bool(re.search(r'\.git.*exists.*return|return.*\.git.*exists', source, re.DOTALL))

if has_git_join and has_git_exists:
    print("PASS")
else:
    print("FAIL")
PYEOF
)

if [ "$P2P_GIT" = "PASS" ]; then
    echo "PASS: .git directory check preserved"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "FAIL: .git directory check was removed or broken"
fi

# [pr_diff] (0.10): git_head function and git log command are preserved
P2P_GITOPS=$(python3 << 'PYEOF'
import re

with open("/repo/crates/uv-cli/build.rs") as f:
    source = f.read()

has_git_head_fn = bool(re.search(r'fn\s+git_head\s*\(', source))
has_git_log = bool(re.search(r'Command::new\s*\(\s*"git"\s*\)', source))
has_env_vars = bool(re.search(r'UV_COMMIT_HASH', source))

if has_git_head_fn and has_git_log and has_env_vars:
    print("PASS")
else:
    print("FAIL")
PYEOF
)

if [ "$P2P_GITOPS" = "PASS" ]; then
    echo "PASS: git operations preserved (git_head fn, git log command, env vars)"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "FAIL: git operations were removed or broken"
fi

# ==========================================================================
# STRUCTURAL: Anti-stub
# ==========================================================================

# [pr_diff] (0.05): build.rs is not trivially short (anti-stub)
LINE_COUNT=$(wc -l < "$FILE")
if [ "$LINE_COUNT" -gt 50 ]; then
    echo "PASS: build.rs has $LINE_COUNT lines (not a stub)"
    REWARD=$(echo "$REWARD + 0.05" | bc)
else
    echo "FAIL: build.rs is suspiciously short ($LINE_COUNT lines)"
fi

# [pr_diff] (0.05): commit_info function has substantial body (anti-stub)
FUNC_SIZE=$(python3 << 'PYEOF'
import re

with open("/repo/crates/uv-cli/build.rs") as f:
    source = f.read()

match = re.search(r'fn\s+commit_info\s*\([^)]*\)\s*\{', source)
if not match:
    print("0")
else:
    start = match.end() - 1
    depth = 0
    for i in range(start, len(source)):
        if source[i] == '{':
            depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0:
                func_body = source[start:i+1]
                # Count non-blank, non-comment lines
                lines = [l.strip() for l in func_body.split('\n')
                         if l.strip() and not l.strip().startswith('//')]
                print(len(lines))
                break
    else:
        print("0")
PYEOF
)

if [ "$FUNC_SIZE" -gt 10 ]; then
    echo "PASS: commit_info has $FUNC_SIZE meaningful lines"
    REWARD=$(echo "$REWARD + 0.05" | bc)
else
    echo "FAIL: commit_info body too small ($FUNC_SIZE lines) — likely a stub"
fi

# ==========================================================================
# CONFIG-DERIVED: CLAUDE.md rules
# ==========================================================================

# [agent_config] (0.05): No .unwrap() in the .jj detection block — CLAUDE.md:7 @ cde48c8
JJ_UNWRAP=$(python3 << 'PYEOF'
import re

with open("/repo/crates/uv-cli/build.rs") as f:
    source = f.read()

# Find lines mentioning .jj and their surrounding context (10 lines)
lines = source.split('\n')
jj_lines = [i for i, l in enumerate(lines) if '.jj' in l]

if not jj_lines:
    print("NO_JJ")
else:
    # Check 10-line window around each .jj reference
    for jj_line in jj_lines:
        window = lines[max(0, jj_line-2):jj_line+8]
        for wl in window:
            if '.unwrap()' in wl:
                print("HAS_UNWRAP")
                exit()
    print("CLEAN")
PYEOF
)

if [ "$JJ_UNWRAP" = "CLEAN" ]; then
    echo "PASS: .jj detection block avoids .unwrap()"
    REWARD=$(echo "$REWARD + 0.05" | bc)
elif [ "$JJ_UNWRAP" = "NO_JJ" ]; then
    echo "FAIL: No .jj block found to check"
else
    echo "FAIL: .jj detection block uses .unwrap() (violates CLAUDE.md:7)"
fi

# [agent_config] (0.05): Descriptive variable names in .jj block — CLAUDE.md:14 @ cde48c8
JJ_NAMES=$(python3 << 'PYEOF'
import re

with open("/repo/crates/uv-cli/build.rs") as f:
    source = f.read()

lines = source.split('\n')
jj_lines = [i for i, l in enumerate(lines) if '.jj' in l]

if not jj_lines:
    print("NO_JJ")
else:
    bad_names = False
    for jj_line in jj_lines:
        window = lines[max(0, jj_line-2):jj_line+8]
        for wl in window:
            # Check for single-character let bindings
            if re.search(r'\blet\s+[a-z]\s*=', wl):
                bad_names = True
            # Check for very short abbreviated names (2 chars)
            if re.search(r'\blet\s+[a-z]{1,2}\s*=', wl):
                bad_names = True
    print("BAD" if bad_names else "GOOD")
PYEOF
)

if [ "$JJ_NAMES" = "GOOD" ]; then
    echo "PASS: Variable names in .jj block are descriptive"
    REWARD=$(echo "$REWARD + 0.05" | bc)
elif [ "$JJ_NAMES" = "NO_JJ" ]; then
    echo "FAIL: No .jj block to check variable names"
else
    echo "FAIL: Variable names in .jj block are too short (violates CLAUDE.md:14)"
fi

# ==========================================================================
# Final score
# ==========================================================================
echo "$REWARD" > /logs/verifier/reward.txt

# Build JSON output
python3 -c "
reward = $REWARD
behavioral = min(reward, 0.55)
regression = min(max(0, reward - 0.55), 0.20)
config_score = min(max(0, reward - 0.75), 0.10)
structural = max(0, reward - behavioral - regression - config_score)
print('{\"reward\": %.2f, \"behavioral\": %.2f, \"regression\": %.2f, \"config\": %.2f, \"style_rubric\": 0.0}' % (reward, behavioral, regression, config_score))
" > /logs/verifier/reward.json

echo "Total reward: $REWARD"
cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
