#!/usr/bin/env bash
set +e

REWARD=0
MOUNT_SVELTE="/workspace/js/core/src/MountCustomComponent.svelte"
PLUGINS_TS="/workspace/js/preview/src/plugins.ts"
MAIN_TS="/workspace/js/spa/src/main.ts"

pass() { REWARD=$(python3 -c "print(round($REWARD + $1, 4))"); echo "PASS ($1): $2"; }
fail() { echo "FAIL ($1): $2"; }

# ── GATE (0): Files must exist ──
# [pr_diff] (0): Syntax gate — abort if target files are missing
for f in "$MOUNT_SVELTE" "$PLUGINS_TS" "$MAIN_TS"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAIL: $f does not exist"
        echo "0.0" > /logs/verifier/reward.txt
        exit 0
    fi
done
echo "GATE: All target files exist"

# ── FAIL-TO-PASS BEHAVIORAL (0.60) ──

# [pr_diff] (0.20): MountCustomComponent.svelte must not log reactive state
if grep -q 'console\.log({ el, comp, runtime })' "$MOUNT_SVELTE"; then
    fail 0.20 "MountCustomComponent.svelte still has console.log({ el, comp, runtime })"
else
    pass 0.20 "MountCustomComponent.svelte: reactive state console.log removed"
fi

# [pr_diff] (0.20): plugins.ts must not log 'init gradio'
if grep -q 'console\.log("init gradio")' "$PLUGINS_TS"; then
    fail 0.20 "plugins.ts still has console.log(\"init gradio\")"
else
    pass 0.20 "plugins.ts: 'init gradio' console.log removed"
fi

# [pr_diff] (0.20): main.ts must not log mode
if grep -q 'console\.log("mode", mode)' "$MAIN_TS"; then
    fail 0.20 "main.ts still has console.log(\"mode\", mode)"
else
    pass 0.20 "main.ts: mode console.log removed"
fi

# ── PASS-TO-PASS REGRESSION (0.30) ──

# [pr_diff] (0.10): MountCustomComponent.svelte — core mounting logic intact
SVELTE_OK=true
for marker in \
    '\$effect' \
    'comp = runtime.mount(component.default' \
    'runtime.umount(comp)' \
    'shared_props: node.props.shared_props' \
    'bind:this={el}'; do
    if ! grep -q "$marker" "$MOUNT_SVELTE"; then
        SVELTE_OK=false
        break
    fi
done
if [ "$SVELTE_OK" = true ]; then
    pass 0.10 "MountCustomComponent.svelte: all core code markers present"
else
    fail 0.10 "MountCustomComponent.svelte: core mounting logic damaged"
fi

# [pr_diff] (0.10): plugins.ts — plugin factory and module resolution intact
PLUGINS_OK=true
for marker in \
    'export function make_gradio_plugin(' \
    'function resolve_svelte_entry(id' \
    'window.__GRADIO_DEV__' \
    'prebundleSvelteLibraries' \
    'const resolved_v_id_2' \
    'virtual:cc-init'; do
    if ! grep -q "$marker" "$PLUGINS_TS"; then
        PLUGINS_OK=false
        break
    fi
done
if [ "$PLUGINS_OK" = true ]; then
    pass 0.10 "plugins.ts: all core code markers present"
else
    fail 0.10 "plugins.ts: plugin factory or resolution code damaged"
fi

# [pr_diff] (0.10): main.ts — custom element registration and lifecycle intact
MAIN_OK=true
for marker in \
    'async function get_index' \
    'function create_custom_element' \
    'GradioApp extends HTMLElement' \
    'customElements.define("gradio-app"' \
    'connectedCallback' \
    'attributeChangedCallback'; do
    if ! grep -q "$marker" "$MAIN_TS"; then
        MAIN_OK=false
        break
    fi
done
if [ "$MAIN_OK" = true ]; then
    pass 0.10 "main.ts: all core code markers present"
else
    fail 0.10 "main.ts: custom element or lifecycle code damaged"
fi

# ── ANTI-STUB / STRUCTURAL (0.10) ──

# [pr_diff] (0.05): File sizes within expected range
# Originals: svelte ~37, plugins ~148, main ~172. Fix removes 1 line each.
SIZE_OK=true
SVELTE_LINES=$(wc -l < "$MOUNT_SVELTE")
PLUGINS_LINES=$(wc -l < "$PLUGINS_TS")
MAIN_LINES=$(wc -l < "$MAIN_TS")
if [ "$SVELTE_LINES" -lt 25 ] || [ "$SVELTE_LINES" -gt 50 ]; then SIZE_OK=false; fi
if [ "$PLUGINS_LINES" -lt 130 ] || [ "$PLUGINS_LINES" -gt 165 ]; then SIZE_OK=false; fi
if [ "$MAIN_LINES" -lt 155 ] || [ "$MAIN_LINES" -gt 190 ]; then SIZE_OK=false; fi
if [ "$SIZE_OK" = true ]; then
    pass 0.05 "All files within expected line count range"
else
    fail 0.05 "File sizes outside expected range (svelte=$SVELTE_LINES plugins=$PLUGINS_LINES main=$MAIN_LINES)"
fi

# [pr_diff] (0.05): No console.log statements remain in changed files
SVELTE_LOGS=$(grep -c 'console\.log' "$MOUNT_SVELTE" || true)
PLUGINS_LOGS=$(grep -c 'console\.log' "$PLUGINS_TS" || true)
MAIN_LOGS=$(grep -c 'console\.log' "$MAIN_TS" || true)
TOTAL_LOGS=$((SVELTE_LOGS + PLUGINS_LOGS + MAIN_LOGS))
if [ "$TOTAL_LOGS" -eq 0 ]; then
    pass 0.05 "No console.log statements remain in changed files"
else
    fail 0.05 "Found $TOTAL_LOGS console.log statement(s) still in changed files"
fi

# ── Final score ──
echo ""
echo "Final score: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
json.dump({
    'reward': $REWARD,
    'behavioral': min(round($REWARD, 4), 0.60),
    'regression': min(round(max($REWARD - 0.60, 0), 4), 0.30),
    'structural': min(round(max($REWARD - 0.90, 0), 4), 0.10)
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
