#!/usr/bin/env bash
set +e

REPO="/repo"
PRINTER="$REPO/crates/uv/src/printer.rs"
SELF_UPDATE="$REPO/crates/uv/src/commands/self_update.rs"
TOTAL=0.0
RESULTS=()

add_score() {
    local score="$1" weight="$2" label="$3"
    local weighted
    weighted=$(python3 -c "print(round($score * $weight, 4))")
    TOTAL=$(python3 -c "print(round($TOTAL + $weighted, 4))")
    RESULTS+=("$label: score=$score weight=$weight weighted=$weighted")
}

# ────────────────────────────────────────────────────────────
# GATE: Rust syntax check on modified files
# ────────────────────────────────────────────────────────────
# [pr_diff] (gate): Rust files must parse without syntax errors
GATE_PASS=1
for f in "$PRINTER" "$SELF_UPDATE"; do
    if [ -f "$f" ]; then
        if ! rustc --edition 2021 --crate-type lib "$f" -Z parse-only 2>/dev/null; then
            echo "GATE FAIL: syntax error in $f"
            GATE_PASS=0
        fi
    else
        echo "GATE FAIL: $f not found"
        GATE_PASS=0
    fi
done

if [ "$GATE_PASS" -eq 0 ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "gate": "FAIL"}' > /logs/verifier/reward.json
    echo "GATE FAILED — aborting"
    exit 0
fi

# ────────────────────────────────────────────────────────────
# BEHAVIORAL F2P (0.45): Extract Printer, compile, test behavior
# [pr_diff] (0.45): stderr_important returns Enabled for Quiet, Disabled for Silent;
#                    stderr() still returns Disabled for Quiet (regression)
# ────────────────────────────────────────────────────────────
TEST_DIR=$(mktemp -d)

# Extract Printer enum + impl blocks returning Stderr via Python
python3 << PYEOF > "$TEST_DIR/printer_extract.rs"
import re, sys

with open("$PRINTER") as f:
    src = f.read()

# Extract the Printer enum definition
enum_match = re.search(r'((?:#\[derive[^\]]*\]\s*)*pub(?:\(crate\))?\s+enum\s+Printer\s*\{[^}]+\})', src)
if not enum_match:
    print("// ERROR: Could not extract Printer enum", file=sys.stderr)
    sys.exit(1)

enum_def = enum_match.group(1)
enum_def = enum_def.replace('pub(crate)', 'pub')
enum_def = re.sub(r'#\[derive[^\]]*\]', '', enum_def)
enum_def = re.sub(r'\s*///[^\n]*', '', enum_def)

print("#[derive(Debug, Copy, Clone, PartialEq)]")
print(enum_def)
print()

# Extract all impl Printer blocks — get methods returning Stderr
impl_blocks = re.findall(r'(impl\s+Printer\s*\{.*?\n\})', src, re.DOTALL)
for block in impl_blocks:
    methods = re.findall(
        r'((?:\s*///[^\n]*\n)*\s*pub(?:\(crate\))?\s+fn\s+\w+\(self\)\s*->\s*Stderr\s*\{[^}]+\})',
        block
    )
    if methods:
        print("impl Printer {")
        for m in methods:
            m = m.replace('pub(crate)', 'pub')
            m = re.sub(r'\s*///[^\n]*\n', '\n', m)
            print(m)
        print("}")
        print()
PYEOF

# Build the test binary: Stderr enum + extracted printer + test main
cat > "$TEST_DIR/test_combined.rs" << 'RUSTEOF'
use std::process;

#[derive(Debug, Copy, Clone, PartialEq)]
enum Stderr { Enabled, Disabled }

RUSTEOF

grep -v "enum Stderr" "$TEST_DIR/printer_extract.rs" >> "$TEST_DIR/test_combined.rs"

cat >> "$TEST_DIR/test_combined.rs" << 'RUSTEOF'

fn main() {
    let mut passed = 0;
    let mut total = 0;

    // F2P Test 1: stderr_important(Quiet) == Enabled (THE core bug)
    total += 1;
    if Printer::Quiet.stderr_important() == Stderr::Enabled {
        passed += 1;
        eprintln!("PASS: Quiet.stderr_important() == Enabled");
    } else {
        eprintln!("FAIL: Quiet.stderr_important() should be Enabled");
    }

    // F2P Test 2: stderr_important(Silent) == Disabled
    total += 1;
    if Printer::Silent.stderr_important() == Stderr::Disabled {
        passed += 1;
        eprintln!("PASS: Silent.stderr_important() == Disabled");
    } else {
        eprintln!("FAIL: Silent.stderr_important() should be Disabled");
    }

    // F2P Test 3: stderr_important(Default) == Enabled
    total += 1;
    if Printer::Default.stderr_important() == Stderr::Enabled {
        passed += 1;
        eprintln!("PASS: Default.stderr_important() == Enabled");
    } else {
        eprintln!("FAIL: Default.stderr_important() should be Enabled");
    }

    // F2P Test 4: stderr_important(Verbose) == Enabled
    total += 1;
    if Printer::Verbose.stderr_important() == Stderr::Enabled {
        passed += 1;
        eprintln!("PASS: Verbose.stderr_important() == Enabled");
    } else {
        eprintln!("FAIL: Verbose.stderr_important() should be Enabled");
    }

    // F2P Test 5: stderr_important(NoProgress) == Enabled
    total += 1;
    if Printer::NoProgress.stderr_important() == Stderr::Enabled {
        passed += 1;
        eprintln!("PASS: NoProgress.stderr_important() == Enabled");
    } else {
        eprintln!("FAIL: NoProgress.stderr_important() should be Enabled");
    }

    // P2P Test 6: stderr(Quiet) still Disabled (regression guard)
    total += 1;
    if Printer::Quiet.stderr() == Stderr::Disabled {
        passed += 1;
        eprintln!("PASS: Quiet.stderr() == Disabled (unchanged)");
    } else {
        eprintln!("FAIL: Quiet.stderr() should still be Disabled");
    }

    // P2P Test 7: stderr(Silent) still Disabled
    total += 1;
    if Printer::Silent.stderr() == Stderr::Disabled {
        passed += 1;
        eprintln!("PASS: Silent.stderr() == Disabled (unchanged)");
    } else {
        eprintln!("FAIL: Silent.stderr() should still be Disabled");
    }

    eprintln!("Passed {passed}/{total}");
    process::exit((total - passed) as i32);
}
RUSTEOF

BEHAVIORAL_SCORE=0
if grep -q 'fn stderr_important' "$TEST_DIR/printer_extract.rs" 2>/dev/null; then
    if rustc --edition 2021 -o "$TEST_DIR/test_printer" "$TEST_DIR/test_combined.rs" 2>/dev/null; then
        OUTPUT=$("$TEST_DIR/test_printer" 2>&1)
        if [ $? -eq 0 ]; then
            BEHAVIORAL_SCORE=1
        else
            # Partial credit based on pass count
            PASS_COUNT=$(echo "$OUTPUT" | grep -c "^PASS:" || echo 0)
            BEHAVIORAL_SCORE=$(python3 -c "print(round($PASS_COUNT / 7, 4))")
        fi
        echo "$OUTPUT"
    else
        echo "Failed to compile printer test"
    fi
else
    echo "stderr_important method not found in printer.rs"
fi

# [pr_diff] (0.45): Behavioral test of stderr_important + stderr regression
add_score "$BEHAVIORAL_SCORE" 0.45 "behavioral_stderr_important"

# ────────────────────────────────────────────────────────────
# BEHAVIORAL F2P (0.25): self_update.rs uses stderr_important in actual code
# [pr_diff] (0.25): Important messages in self_update.rs wired through stderr_important
# ────────────────────────────────────────────────────────────
# Count .stderr_important() calls in self_update.rs with comments stripped
WIRING_COUNT=$(python3 << PYEOF
import re

with open("$SELF_UPDATE") as f:
    src = f.read()

# Strip single-line comments (// ...)
src_clean = re.sub(r'//[^\n]*', '', src)
# Strip multi-line comments (/* ... */)
src_clean = re.sub(r'/\*.*?\*/', '', src_clean, flags=re.DOTALL)
# Strip string literals to avoid matches inside strings
src_clean = re.sub(r'"(?:[^"\\]|\\.)*"', '""', src_clean)

# Count actual code usages of .stderr_important()
count = len(re.findall(r'\.stderr_important\(\)', src_clean))
print(count)
PYEOF
)

echo "Wiring count (comment-stripped): $WIRING_COUNT"

if [ "$WIRING_COUNT" -ge 5 ]; then
    WIRING_SCORE=1
elif [ "$WIRING_COUNT" -ge 3 ]; then
    WIRING_SCORE=$(python3 -c "print(round($WIRING_COUNT / 5, 4))")
elif [ "$WIRING_COUNT" -ge 1 ]; then
    WIRING_SCORE=$(python3 -c "print(round($WIRING_COUNT / 7, 4))")
else
    WIRING_SCORE=0
fi

# [pr_diff] (0.25): self_update.rs wires important messages through stderr_important
add_score "$WIRING_SCORE" 0.25 "behavioral_self_update_wiring"

# ────────────────────────────────────────────────────────────
# PASS-TO-PASS (0.10): stderr() method exists with correct signature
# [pr_diff] (0.10): stderr() method preserved and returns Stderr
# ────────────────────────────────────────────────────────────
P2P_SCORE=1

# Verify stderr() method still exists with correct signature
if ! python3 -c "
import re
with open('$PRINTER') as f:
    src = f.read()
# Must have fn stderr(self) -> Stderr (not stderr_important)
if not re.search(r'fn\s+stderr\(self\)\s*->\s*Stderr', src):
    exit(1)
"; then
    echo "FAIL: stderr() method missing or has wrong signature"
    P2P_SCORE=0
fi

# Verify stderr_important also exists with correct signature
if ! python3 -c "
import re
with open('$PRINTER') as f:
    src = f.read()
if not re.search(r'fn\s+stderr_important\(self\)\s*->\s*Stderr', src):
    exit(1)
"; then
    echo "FAIL: stderr_important() method missing or has wrong signature"
    P2P_SCORE=0
fi

# [pr_diff] (0.10): Both stderr methods exist with correct signatures
add_score "$P2P_SCORE" 0.10 "p2p_methods_exist"

# ────────────────────────────────────────────────────────────
# STRUCTURAL (0.10): Anti-stub — stderr_important has meaningful body
# [pr_diff] (0.10): stderr_important has complete match arms, not a trivial stub
# ────────────────────────────────────────────────────────────
STRUCT_SCORE=$(python3 << PYEOF
import re

with open("$PRINTER") as f:
    src = f.read()

# Find stderr_important method body
m = re.search(r'fn\s+stderr_important\(self\)\s*->\s*Stderr\s*\{(.*?)\n\s*\}', src, re.DOTALL)
if not m:
    print(0)
    exit()

body = m.group(1)

# Must have a match expression (not just a single return)
has_match = bool(re.search(r'\bmatch\b', body))

# Must map Silent differently from Quiet (the key semantic distinction)
# Check that both Silent and Quiet appear in the body
has_silent = 'Silent' in body
has_quiet = 'Quiet' in body

# Must have at least one Disabled mapping (for Silent)
has_disabled = 'Disabled' in body

# Must have at least one Enabled mapping (for Quiet and others)
has_enabled = 'Enabled' in body

score = 0
checks = 4
if has_match: score += 1
if has_silent and has_quiet: score += 1
if has_disabled: score += 1
if has_enabled: score += 1

print(round(score / checks, 4))
PYEOF
)

# [pr_diff] (0.10): Anti-stub check for stderr_important body
add_score "$STRUCT_SCORE" 0.10 "structural_anti_stub"

# ────────────────────────────────────────────────────────────
# CONFIG (0.10): CLAUDE.md programmatic rules
# [agent_config] (0.10): Rules from CLAUDE.md @ 262a50bb
# ────────────────────────────────────────────────────────────
CONFIG_PASS=0
CONFIG_CHECKS=2

# [agent_config] (0.05): "AVOID using panic!, unreachable!, .unwrap()" — CLAUDE.md:6 @ 262a50bb
IMPORTANT_BODY=$(python3 << PYEOF
import re
with open("$PRINTER") as f:
    src = f.read()
m = re.search(r'fn\s+stderr_important\(self\)\s*->\s*Stderr\s*\{(.*?)\n\s*\}', src, re.DOTALL)
if m:
    print(m.group(1))
PYEOF
)

if echo "$IMPORTANT_BODY" | grep -qE '(panic!|unreachable!|\.unwrap\(\))'; then
    echo "FAIL: stderr_important uses panic!/unreachable!/unwrap()"
else
    CONFIG_PASS=$((CONFIG_PASS + 1))
fi

# [agent_config] (0.05): "AVOID shortening variable names" — CLAUDE.md:15 @ 262a50bb
# Check that method name is descriptive (>= 8 chars after stderr_)
METHOD_NAME=$(python3 << PYEOF
import re
with open("$PRINTER") as f:
    src = f.read()
# Find any new stderr-related method that returns Stderr and isn't stderr()
methods = re.findall(r'fn\s+(stderr_\w+)\(self\)\s*->\s*Stderr', src)
for m in methods:
    if m != 'stderr':
        print(m)
        break
PYEOF
)

if [ -n "$METHOD_NAME" ] && [ ${#METHOD_NAME} -ge 10 ]; then
    CONFIG_PASS=$((CONFIG_PASS + 1))
else
    echo "FAIL: New method name '$METHOD_NAME' is too short or missing"
fi

CONFIG_SCORE=$(python3 -c "print(round($CONFIG_PASS / $CONFIG_CHECKS, 4))")

# [agent_config] (0.10): CLAUDE.md programmatic rules
add_score "$CONFIG_SCORE" 0.10 "config_claude_md"

# ────────────────────────────────────────────────────────────
# FINAL SCORE
# ────────────────────────────────────────────────────────────
echo ""
echo "=== SCORING ==="
for r in "${RESULTS[@]}"; do
    echo "  $r"
done
echo "  TOTAL: $TOTAL"
echo ""

# Clamp to [0, 1]
FINAL=$(python3 -c "print(max(0.0, min(1.0, round($TOTAL, 4))))")
echo "$FINAL" > /logs/verifier/reward.txt

# Detailed breakdown
python3 << PYEOF > /logs/verifier/reward.json
import json
results = {}
for r in """$(printf '%s\n' "${RESULTS[@]}")""".strip().split('\n'):
    parts = r.split(':')
    name = parts[0].strip()
    weighted = float(r.split('weighted=')[1])
    results[name] = weighted
results['reward'] = $FINAL
print(json.dumps(results, indent=2))
PYEOF

echo "Final reward: $FINAL"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
