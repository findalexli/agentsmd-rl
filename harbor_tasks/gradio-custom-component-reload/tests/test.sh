#!/usr/bin/env bash
set +e

MOUNT_CUSTOM="/workspace/gradio/js/core/src/MountCustomComponent.svelte"
MOUNT_COMPONENTS="/workspace/gradio/js/core/src/MountComponents.svelte"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_effect_cleanup]=0.30
WEIGHTS[behavioral_prop_reads]=0.25
WEIGHTS[behavioral_no_inspect]=0.10
WEIGHTS[structural_unmount_spelling]=0.15
WEIGHTS[antistub]=0.20

for key in behavioral_effect_cleanup behavioral_prop_reads behavioral_no_inspect structural_unmount_spelling antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: Files exist ----------
if [ ! -f "$MOUNT_CUSTOM" ]; then
    echo "GATE FAIL: $MOUNT_CUSTOM not found"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: target files exist"

# ---------- PRIMARY 1 (30%): Behavioral - $effect returns cleanup function ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/core/src/MountCustomComponent.svelte") as f:
    content = f.read()

# The fix changes from onDestroy to returning a cleanup function from $effect
# Look for: return () => { ... unmount ... }
has_return_cleanup = bool(re.search(r'return\s*\(\)\s*=>\s*\{', content))
# Also check that onDestroy is NOT imported/used
has_on_destroy = "onDestroy" in content

if has_return_cleanup and not has_on_destroy:
    print("BEHAVIORAL_CLEANUP PASS: $effect returns cleanup function, no onDestroy")
    sys.exit(0)
elif has_return_cleanup:
    print("BEHAVIORAL_CLEANUP PARTIAL: returns cleanup but onDestroy still present")
    sys.exit(0)
else:
    print("BEHAVIORAL_CLEANUP FAIL: $effect does not return cleanup function")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_effect_cleanup]=1
    echo "TEST behavioral_effect_cleanup: PASS"
else
    echo "TEST behavioral_effect_cleanup: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - Props read inside effect for reactivity ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/core/src/MountCustomComponent.svelte") as f:
    content = f.read()

# The fix reads node.props.shared_props and node.props.props inside the effect
# so that when the app tree reloads, the effect re-runs
# Check that the effect body references these props
effect_match = re.search(r'\$effect\(\(\)\s*=>\s*\{(.*?)\n\t\}\)', content, re.DOTALL)
if not effect_match:
    # Try broader match
    effect_match = re.search(r'\$effect\(\(\)\s*=>\s*\{(.+?)\}\s*\)', content, re.DOTALL)

if effect_match:
    effect_body = effect_match.group(1)
    has_shared_props = "shared_props" in effect_body
    has_props = "node.props.props" in effect_body or "_props" in effect_body

    if has_shared_props and has_props:
        print("BEHAVIORAL_PROP_READS PASS: effect body reads both shared_props and props")
        sys.exit(0)
    elif has_shared_props or has_props:
        print("BEHAVIORAL_PROP_READS PARTIAL: effect reads some props")
        sys.exit(0)
    else:
        print("BEHAVIORAL_PROP_READS FAIL: effect does not read prop references")
        sys.exit(1)
else:
    # Fallback: check if the file has prop reads near mount
    if "shared_props" in content and "mount" in content:
        print("BEHAVIORAL_PROP_READS PASS: shared_props and mount both present")
        sys.exit(0)
    print("BEHAVIORAL_PROP_READS FAIL: could not find $effect block")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_prop_reads]=1
    echo "TEST behavioral_prop_reads: PASS"
else
    echo "TEST behavioral_prop_reads: FAIL"
fi

# ---------- PRIMARY 3 (10%): Behavioral - No $inspect debug call in MountComponents ----------
python3 << 'PYEOF'
import sys

MOUNT_COMPONENTS = "/workspace/gradio/js/core/src/MountComponents.svelte"

try:
    with open(MOUNT_COMPONENTS) as f:
        content = f.read()
except FileNotFoundError:
    print("BEHAVIORAL_NO_INSPECT PASS: MountComponents.svelte not found (may be refactored)")
    sys.exit(0)

if "$inspect" in content:
    print("BEHAVIORAL_NO_INSPECT FAIL: $inspect debug call still present in MountComponents")
    sys.exit(1)
else:
    print("BEHAVIORAL_NO_INSPECT PASS: no $inspect call in MountComponents")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_no_inspect]=1
    echo "TEST behavioral_no_inspect: PASS"
else
    echo "TEST behavioral_no_inspect: FAIL"
fi

# ---------- SUPPLEMENTARY (15%): Structural - unmount spelled correctly ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/core/src/MountCustomComponent.svelte") as f:
    content = f.read()

# The original had a typo: "umount" instead of "unmount"
has_unmount = "unmount" in content
has_umount_typo = bool(re.search(r'\bumount\b', content))

if has_unmount and not has_umount_typo:
    print("STRUCTURAL PASS: uses correct 'unmount' spelling, no 'umount' typo")
    sys.exit(0)
elif has_unmount:
    print("STRUCTURAL PARTIAL: has 'unmount' but also has 'umount'")
    sys.exit(0)
else:
    print("STRUCTURAL FAIL: 'unmount' not found")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural_unmount_spelling]=1
    echo "TEST structural_unmount_spelling: PASS"
else
    echo "TEST structural_unmount_spelling: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
LINE_COUNT=$(wc -l < "$MOUNT_CUSTOM")
HAS_MOUNT=$(grep -c "mount\|Mount" "$MOUNT_CUSTOM" 2>/dev/null || echo "0")
HAS_EFFECT=$(grep -c "effect" "$MOUNT_CUSTOM" 2>/dev/null || echo "0")
if [ "$LINE_COUNT" -gt 10 ] && [ "$HAS_MOUNT" -ge 1 ] && [ "$HAS_EFFECT" -ge 1 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_effect_cleanup': ${WEIGHTS[behavioral_effect_cleanup]}, 'behavioral_prop_reads': ${WEIGHTS[behavioral_prop_reads]}, 'behavioral_no_inspect': ${WEIGHTS[behavioral_no_inspect]}, 'structural_unmount_spelling': ${WEIGHTS[structural_unmount_spelling]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral_effect_cleanup': ${RESULTS[behavioral_effect_cleanup]}, 'behavioral_prop_reads': ${RESULTS[behavioral_prop_reads]}, 'behavioral_no_inspect': ${RESULTS[behavioral_no_inspect]}, 'structural_unmount_spelling': ${RESULTS[structural_unmount_spelling]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_effect_cleanup   (${WEIGHTS[behavioral_effect_cleanup]}): ${RESULTS[behavioral_effect_cleanup]}"
echo "  behavioral_prop_reads       (${WEIGHTS[behavioral_prop_reads]}): ${RESULTS[behavioral_prop_reads]}"
echo "  behavioral_no_inspect       (${WEIGHTS[behavioral_no_inspect]}): ${RESULTS[behavioral_no_inspect]}"
echo "  structural_unmount_spelling (${WEIGHTS[structural_unmount_spelling]}): ${RESULTS[structural_unmount_spelling]}"
echo "  antistub                    (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
