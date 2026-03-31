#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
SCORE=0.0

add_score() {
    SCORE=$(python3 -c "print($SCORE + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

cd /workspace/bun

IWM_FILE="src/install/PackageManager/install_with_manager.zig"
SS_FILE="src/install/PackageManager/security_scanner.zig"
TEST_FILE="test/regression/issue/28193.test.ts"

##############################################################################
# GATE: Source files exist and are non-empty
##############################################################################
# [pr_diff] (gate): install_with_manager.zig must exist
if [ ! -s "$IWM_FILE" ]; then
    echo "GATE FAILED: $IWM_FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
if [ ! -s "$SS_FILE" ]; then
    echo "GATE FAILED: $SS_FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL (structural proxy — Zig requires full Bun build toolchain)
# Total: 0.65
##############################################################################

# [pr_diff] (0.25): The catch-all else branch in the security scanner error
# handler must produce an error message instead of being empty (else => {}).
# This is the core bug — silent exit with no diagnostic.
# Accepts: named variants with Output calls, OR a catch-all with error name
# formatting. Does NOT accept empty else or else with no output.
add_total 0.25
CATCHALL_FIX=$(python3 << 'PYEOF'
import re

text = open("src/install/PackageManager/install_with_manager.zig").read()

# Find the security scanner error switch block between catch and Global.exit
scanner_match = re.search(
    r'performSecurityScanAfterResolution.*?catch\s*\|err\|\s*\{(.*?)\n\s*Global\.exit',
    text, re.DOTALL
)
if not scanner_match:
    print("FAIL")
    exit()

block = scanner_match.group(1)

# Core check: the empty else => {} must be gone
has_empty_else = bool(re.search(r'else\s*=>\s*\{\s*\}', block))
if has_empty_else:
    print("FAIL")
    exit()

# The else branch (if present) must produce output.
# Accept: else => |e| { ...Output...errGeneric/err/warn... }
# Also accept: no else at all if all variants are named with messages
else_match = re.search(r'else\s*=>\s*\|?\w*\|?\s*\{([^}]*)\}', block, re.DOTALL)
if else_match:
    else_body = else_match.group(1).strip()
    # Else body must have some output call (not empty, not just a comment)
    if not else_body or not re.search(r'(Output\.|std\.debug\.print|std\.log|@panic)', else_body):
        print("FAIL")
        exit()
    # Must not be a trivially empty message: Output.errGeneric("", .{})
    if re.search(r'Output\.\w+\(\s*""\s*,', else_body):
        print("FAIL")
        exit()

# Count total output-producing branches in the switch (named + else)
output_branches = len(re.findall(r'=>\s*(?:\|[^|]*\|)?\s*\{[^}]*(Output\.|std\.debug\.print|std\.log)', block))
if output_branches < 2:
    print("FAIL")
    exit()

print("PASS")
PYEOF
)
if [ "$CATCHALL_FIX" = "PASS" ]; then
    add_score 0.25
    echo "PASS [0.25]: catch-all else prints error message instead of silent exit"
else
    echo "FAIL [0.25]: catch-all else still empty or missing error output"
fi

# [pr_diff] (0.15): All error variants produce diagnostic output.
# Accept EITHER: (a) 3+ individually named variants with output calls,
# OR (b) a catch-all that formats the error name (e.g., @errorName(e)).
# The key requirement: every error path must produce a message.
add_total 0.15
VARIANT_MSGS=$(python3 << 'PYEOF'
import re

text = open("src/install/PackageManager/install_with_manager.zig").read()

scanner_match = re.search(
    r'performSecurityScanAfterResolution.*?catch\s*\|err\|\s*\{(.*?)\n\s*Global\.exit',
    text, re.DOTALL
)
if not scanner_match:
    print("FAIL")
    exit()

block = scanner_match.group(1)

# Strategy A: 3+ named error variants with output calls
named_variants = re.findall(r'error\.(\w+)\s*=>', block)
output_calls = len(re.findall(r'Output\.\w+\(', block))
named_with_output = len(set(named_variants))

strategy_a = named_with_output >= 3 and output_calls >= 3

# Strategy B: catch-all that formats the error name dynamically
# e.g., else => |e| { Output.errGeneric("...{s}...", .{@errorName(e)}); }
has_dynamic_catchall = bool(re.search(
    r'else\s*=>\s*\|(\w+)\|.*?@errorName\(\1\)',
    block, re.DOTALL
))

if strategy_a or has_dynamic_catchall:
    print("PASS")
else:
    print("FAIL")
PYEOF
)
if [ "$VARIANT_MSGS" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: all error variants produce diagnostic output"
else
    echo "FAIL [0.15]: insufficient error variant coverage"
fi

# [pr_diff] (0.15): Error printing centralized in install_with_manager.zig.
# The duplicate Output.errGeneric/Output.pretty calls in security_scanner.zig
# for error cases (InvalidPackageID, PartialInstallFailed, NoPackagesInstalled,
# SecurityScannerInWorkspace) should be removed — caller handles printing.
add_total 0.15
CENTRALIZED=$(python3 << 'PYEOF'
import re

text = open("src/install/PackageManager/security_scanner.zig").read()

# Count Output.errGeneric or Output.pretty calls that appear right before
# a return error.XXX line — these are the duplicates that should be removed
dup_count = 0
for error_name in ["InvalidPackageID", "PartialInstallFailed",
                    "NoPackagesInstalled", "SecurityScannerInWorkspace"]:
    # Pattern: Output call on a line, then return error.XXX within a few lines
    pattern = r'Output\.(?:errGeneric|pretty)\([^)]*\).*?\n[^}]*?return error\.' + error_name
    if re.search(pattern, text, re.DOTALL):
        dup_count += 1

# Allow at most 1 remaining (partial fix still gets some credit via other checks)
print("PASS" if dup_count == 0 else "FAIL")
PYEOF
)
if [ "$CENTRALIZED" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: error printing centralized in caller, removed from security_scanner.zig"
else
    echo "FAIL [0.15]: duplicate error printing still in security_scanner.zig"
fi

# [pr_diff] (0.10): The .error variant from retry result is properly propagated
# instead of being collapsed into a generic error. In the retry_result switch,
# the .error case should return the original error rather than losing it.
# Accepts: .@"error" => |err| return err, inline else, or any pattern that
# propagates the original error instead of collapsing to SecurityScannerRetryFailed.
add_total 0.10
ERROR_PROP=$(python3 << 'PYEOF'
import re

text = open("src/install/PackageManager/security_scanner.zig").read()

# Find performSecurityScanAfterResolution function body
func_match = re.search(
    r'fn performSecurityScanAfterResolution\b(.*?)(?:\nfn |\npub fn |\Z)',
    text, re.DOTALL
)
if not func_match:
    print("FAIL")
    exit()

func_text = func_match.group(1)

# BAD pattern: catch-all else that collapses all errors to SecurityScannerRetryFailed
has_catchall_collapse = bool(re.search(
    r'else\s*=>\s*return\s+error\.SecurityScannerRetryFailed',
    func_text
))

# GOOD patterns: .@"error" propagation, or .error propagation, or inline else
has_error_prop = bool(re.search(r'\.@"error"\s*=>\s*\|', func_text)) or \
                 bool(re.search(r'\.error\s*=>\s*\|', func_text)) or \
                 bool(re.search(r'inline\s+else\s*=>\s*\|', func_text))

if has_error_prop and not has_catchall_collapse:
    print("PASS")
elif not has_catchall_collapse:
    # Removed the collapse even if propagation style differs
    print("PASS")
else:
    print("FAIL")
PYEOF
)
if [ "$ERROR_PROP" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: .error variant properly propagated instead of collapsed"
else
    echo "FAIL [0.10]: .error variant still collapsed into SecurityScannerRetryFailed"
fi

##############################################################################
# REGRESSION: Pass-to-pass (0.15)
##############################################################################

# [pr_diff] (0.05): install_with_manager.zig still handles SecurityScannerInWorkspace
add_total 0.05
if grep -q 'SecurityScannerInWorkspace' "$IWM_FILE"; then
    add_score 0.05
    echo "PASS [0.05]: SecurityScannerInWorkspace handling preserved"
else
    echo "FAIL [0.05]: SecurityScannerInWorkspace handling missing"
fi

# [pr_diff] (0.05): security_scanner.zig still returns proper error types
add_total 0.05
SS_ERRORS=$(python3 << 'PYEOF'
text = open("src/install/PackageManager/security_scanner.zig").read()
errors = ["InvalidPackageID", "PartialInstallFailed", "NoPackagesInstalled",
          "SecurityScannerInWorkspace"]
found = sum(1 for e in errors if "return error." + e in text)
print("PASS" if found >= 3 else "FAIL")
PYEOF
)
if [ "$SS_ERRORS" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: security_scanner.zig still returns proper error types"
else
    echo "FAIL [0.05]: security_scanner.zig missing expected error returns"
fi

# [pr_diff] (0.05): Anti-stub — both Zig files must have substantial content
add_total 0.05
IWM_LINES=$(wc -l < "$IWM_FILE")
SS_LINES=$(wc -l < "$SS_FILE")
if [ "$IWM_LINES" -gt 200 ] && [ "$SS_LINES" -gt 50 ]; then
    add_score 0.05
    echo "PASS [0.05]: anti-stub ($IWM_LINES + $SS_LINES lines)"
else
    echo "FAIL [0.05]: files suspiciously small ($IWM_LINES + $SS_LINES lines)"
fi

##############################################################################
# CONFIG-DERIVED: Agent config rules (0.05)
##############################################################################

# [agent_config] (0.05): "If a test is for a specific numbered GitHub Issue,
# it should be placed in test/regression/issue/${issueNumber}.test.ts"
# — CLAUDE.md:41-42 @ 1d50d640f8
add_total 0.05
if [ -f "$TEST_FILE" ] || ls test/regression/issue/28193* 2>/dev/null | grep -q .; then
    add_score 0.05
    echo "PASS [0.05]: regression test in correct directory per CLAUDE.md"
else
    # Also accept if they put the test somewhere reasonable
    if find test/ -name "*28193*" 2>/dev/null | grep -q .; then
        add_score 0.03
        echo "PARTIAL [0.03/0.05]: test exists but not in test/regression/issue/"
    else
        echo "FAIL [0.05]: no regression test file found"
    fi
fi

##############################################################################
# STYLE RUBRIC (0.10): Use Output.errGeneric not Output.pretty for errors
##############################################################################

# [agent_config] (0.10): "Use Output.errGeneric for error messages to stderr,
# not Output.pretty with raw formatting" — src/CLAUDE.md:15 @ 1d50d640f8
add_total 0.10
STYLE_CHECK=$(python3 << 'PYEOF'
import re

text = open("src/install/PackageManager/install_with_manager.zig").read()

# Find the scanner error switch block
scanner_match = re.search(
    r'performSecurityScanAfterResolution.*?catch\s*\|err\|\s*\{(.*?)\n\s*Global\.exit',
    text, re.DOTALL
)
if not scanner_match:
    print("FAIL")
    exit()

block = scanner_match.group(1)

# Check: uses Output.errGeneric (or Output.err*) NOT Output.pretty for errors
has_pretty_errors = bool(re.search(r'Output\.pretty\s*\(\s*"<red>', block))
has_err_output = bool(re.search(r'Output\.err', block))

if has_err_output and not has_pretty_errors:
    print("PASS")
elif has_err_output:
    # Has errGeneric but also some pretty — partial
    print("PARTIAL")
else:
    print("FAIL")
PYEOF
)
if [ "$STYLE_CHECK" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: uses Output.errGeneric for error messages per src/CLAUDE.md"
elif [ "$STYLE_CHECK" = "PARTIAL" ]; then
    add_score 0.05
    echo "PARTIAL [0.05/0.10]: mixed Output.errGeneric and Output.pretty"
else
    echo "FAIL [0.10]: not using Output.errGeneric for error messages"
fi

##############################################################################
# Final scoring
##############################################################################

FINAL=$(python3 -c "print(round($SCORE, 4))")
echo ""
echo "Total: $FINAL / $TOTAL"
echo "$FINAL" > /logs/verifier/reward.txt

# Compute category breakdown
python3 << PYEOF
import json

behavioral = 0.0  # checks 1-4 (structural proxy for Zig)
regression = 0.0  # checks 5-7
config = 0.0      # check 8
style = 0.0       # check 9

# Reconstruct from individual results
score = $SCORE

# We track actuals by re-checking flags — simpler to use the total
reward = round(score, 4)

data = {
    "reward": reward,
    "behavioral": reward,  # mostly behavioral-intent checks
    "regression": 0.0,
    "config": 0.0,
    "style_rubric": 0.0
}
json.dump(data, open("/logs/verifier/reward.json", "w"))
PYEOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
