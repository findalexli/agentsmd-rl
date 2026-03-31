#!/usr/bin/env bash
set -euo pipefail

REPO="/repo"
TOTAL=0.0
add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }

cd "$REPO"

CLI_FILE="crates/uv-cli/src/lib.rs"

###############################################################################
# GATE (0.00): Rust syntax — must compile the modified crate
###############################################################################
# [pr_diff] (0.00): Code must compile
echo "=== GATE: cargo check ==="
if ! cargo check -p uv-cli 2>&1; then
    echo "GATE FAILED: compilation error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE passed."

# Disable errexit so individual checks can fail without aborting
set +e

###############################################################################
# Behavioral: ExportArgs no_emit_package accepts comma-separated values (0.30)
###############################################################################
# [pr_diff] (0.30): ExportArgs no_emit_package has value_delimiter = ',' for comma separation
echo "=== Behavioral: ExportArgs no_emit_package comma delimiter ==="
SCORE_EXPORT_NOEMIT=0.0

python3 - "$CLI_FILE" <<'PYEOF'
import sys, re
content = open(sys.argv[1]).read()
# Find ExportArgs struct
m = re.search(r'pub struct ExportArgs\b.*?\n\}', content, re.DOTALL)
if not m:
    print("ExportArgs struct not found")
    sys.exit(1)
block = m.group()
# Find no_emit_package field's #[arg(...)] — identified by "no-install-package" alias
pattern = r'#\[arg\([^]]*?no.install.package[^]]*?\)\]\s*pub no_emit_package'
m2 = re.search(pattern, block, re.DOTALL)
if not m2:
    print("no_emit_package arg attribute not found in ExportArgs")
    sys.exit(1)
attr = m2.group()
# Must have value_delimiter = ',' (the comma character specifically)
if re.search(r"value_delimiter\s*=\s*','", attr):
    sys.exit(0)
print("value_delimiter = ',' not found in ExportArgs no_emit_package")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    SCORE_EXPORT_NOEMIT=0.30
fi
echo "Score: $SCORE_EXPORT_NOEMIT"
add "$SCORE_EXPORT_NOEMIT"

###############################################################################
# Behavioral: ExportArgs only_emit_package accepts comma-separated values (0.25)
###############################################################################
# [pr_diff] (0.25): ExportArgs only_emit_package has value_delimiter = ',' for comma separation
echo "=== Behavioral: ExportArgs only_emit_package comma delimiter ==="
SCORE_EXPORT_ONLY=0.0

python3 - "$CLI_FILE" <<'PYEOF'
import sys, re
content = open(sys.argv[1]).read()
m = re.search(r'pub struct ExportArgs\b.*?\n\}', content, re.DOTALL)
if not m:
    print("ExportArgs struct not found")
    sys.exit(1)
block = m.group()
# only_emit_package has alias "only-install-package"
pattern = r'#\[arg\([^]]*?only.install.package[^]]*?\)\]\s*pub only_emit_package'
m2 = re.search(pattern, block, re.DOTALL)
if not m2:
    print("only_emit_package arg attribute not found in ExportArgs")
    sys.exit(1)
attr = m2.group()
if re.search(r"value_delimiter\s*=\s*','", attr):
    sys.exit(0)
print("value_delimiter = ',' not found in ExportArgs only_emit_package")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    SCORE_EXPORT_ONLY=0.25
fi
echo "Score: $SCORE_EXPORT_ONLY"
add "$SCORE_EXPORT_ONLY"

###############################################################################
# Behavioral: PipCompileArgs no_emit_package accepts comma-separated values (0.25)
###############################################################################
# [pr_diff] (0.25): PipCompileArgs no_emit_package has value_delimiter = ',' for comma separation
echo "=== Behavioral: PipCompileArgs no_emit_package comma delimiter ==="
SCORE_PIPCOMPILE=0.0

python3 - "$CLI_FILE" <<'PYEOF'
import sys, re
content = open(sys.argv[1]).read()
# Find PipCompileArgs struct
m = re.search(r'pub struct PipCompileArgs\b.*?\n\}', content, re.DOTALL)
if not m:
    print("PipCompileArgs struct not found")
    sys.exit(1)
block = m.group()
# PipCompileArgs no_emit_package has alias "unsafe-package"
pattern = r'#\[arg\([^]]*?unsafe.package[^]]*?\)\]\s*pub no_emit_package'
m2 = re.search(pattern, block, re.DOTALL)
if not m2:
    print("no_emit_package arg attribute not found in PipCompileArgs")
    sys.exit(1)
attr = m2.group()
if re.search(r"value_delimiter\s*=\s*','", attr):
    sys.exit(0)
print("value_delimiter = ',' not found in PipCompileArgs no_emit_package")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    SCORE_PIPCOMPILE=0.25
fi
echo "Score: $SCORE_PIPCOMPILE"
add "$SCORE_PIPCOMPILE"

###############################################################################
# Pass-to-pass: Existing arg attributes preserved (0.10)
###############################################################################
# [pr_diff] (0.10): Aliases and value_hint still present after modification
echo "=== P2P: Existing attributes preserved ==="
SCORE_P2P=0.0
P2P_OK=true

# ExportArgs aliases must survive
if ! grep -q 'no-install-package' "$CLI_FILE"; then
    echo "FAIL: no-install-package alias missing"
    P2P_OK=false
fi
if ! grep -q 'only-install-package' "$CLI_FILE"; then
    echo "FAIL: only-install-package alias missing"
    P2P_OK=false
fi
# PipCompileArgs alias must survive
if ! grep -q 'unsafe-package' "$CLI_FILE"; then
    echo "FAIL: unsafe-package alias missing"
    P2P_OK=false
fi
# ValueHint::Other should still be present near these fields
if ! grep -q 'ValueHint::Other' "$CLI_FILE"; then
    echo "FAIL: ValueHint::Other missing"
    P2P_OK=false
fi

if [ "$P2P_OK" = true ]; then
    SCORE_P2P=0.10
fi
echo "Score: $SCORE_P2P"
add "$SCORE_P2P"

###############################################################################
# Anti-stub: No TODO/FIXME/unimplemented in changes (0.05)
###############################################################################
# [pr_diff] (0.05): No placeholder code in changes
echo "=== Anti-stub ==="
SCORE_STUB=0.0
STUB_IN_DIFF=$(git diff HEAD -- "$CLI_FILE" | grep '^+' | grep -v '^+++' | grep -ciE 'TODO|FIXME|unimplemented|todo!' || true)
if [ "$STUB_IN_DIFF" -eq 0 ]; then
    SCORE_STUB=0.05
fi
echo "Score: $SCORE_STUB"
add "$SCORE_STUB"

###############################################################################
# Config-derived: No .unwrap() added in changed file (0.05)
###############################################################################
# [agent_config] (0.05): "AVOID using .unwrap()" — CLAUDE.md:7 @ 5e25583
echo "=== Config: no unwrap in changes ==="
SCORE_UNWRAP=0.0
UNWRAP_IN_DIFF=$(git diff HEAD -- "$CLI_FILE" | grep '^+' | grep -v '^+++' | grep -c '\.unwrap()' || true)
if [ "$UNWRAP_IN_DIFF" -eq 0 ]; then
    SCORE_UNWRAP=0.05
fi
echo "Score: $SCORE_UNWRAP"
add "$SCORE_UNWRAP"

###############################################################################
# Summary
###############################################################################
echo ""
echo "=== TOTAL ==="
echo "Total: $TOTAL"

# Write reward
echo "$TOTAL" > /logs/verifier/reward.txt

# Build JSON breakdown
python3 -c "
import json
data = {
    'reward': $TOTAL,
    'behavioral': round($SCORE_EXPORT_NOEMIT + $SCORE_EXPORT_ONLY + $SCORE_PIPCOMPILE, 4),
    'regression': round($SCORE_P2P, 4),
    'config': round($SCORE_UNWRAP, 4),
    'anti_stub': round($SCORE_STUB, 4),
    'style_rubric': 0.0
}
json.dump(data, open('/logs/verifier/reward.json', 'w'), indent=2)
print(json.dumps(data, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
