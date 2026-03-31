#!/usr/bin/env bash
set +e

INDEX="/workspace/gradio/js/html/Index.svelte"
SHARED="/workspace/gradio/js/html/shared/HTML.svelte"
PYHTML="/workspace/gradio/gradio/components/html.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TOTAL=0

# Helper: strip JS/Svelte comments and HTML comments from a file
# so regex checks can't be gamed by adding patterns in comments.
strip_comments() {
    python3 -c "
import re, sys
content = open(sys.argv[1]).read()
content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
print(content)
" "$1"
}

# ---------- GATE: Files exist ----------
if [ ! -f "$INDEX" ] || [ ! -f "$SHARED" ] || [ ! -f "$PYHTML" ]; then
    echo "GATE FAIL: required files missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: files exist"

# ---------- F2P 1 (0.30): Falsy value fix — || replaced with ?? ----------
# [pr_diff] (0.30): Value of 0 no longer coerced to empty string
# The bug: `gradio.props.value || ""` treats 0 as falsy.
# Any correct fix must avoid `||` with a string fallback on value derivation.
# Svelte code — no Node.js runtime available, structural check justified.
python3 << 'PYEOF'
import re, sys

with open("/workspace/gradio/js/html/Index.svelte") as f:
    raw = f.read()

# Strip comments to prevent gaming
content = re.sub(r'//.*$', '', raw, flags=re.MULTILINE)
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

# Bug pattern: value derived with || (treats 0 as falsy)
bug = re.search(r'(?:gradio\.props\.value|\.value)\s*\|\|\s*["\']', content)

# Accept any of these fixes:
#   ?? ""   (nullish coalescing)
#   ternary: value != null ? value : "" or value !== null && value !== undefined ? value : ""
#   No fallback at all (just use the value directly)
fix_nullish = re.search(r'(?:gradio\.props\.value|\.value)\s*\?\?\s*["\']', content)
fix_ternary = re.search(r'(?:value\s*!==?\s*null|value\s*!==?\s*undefined).*\?', content)
fix_no_fallback = not bug and 'value' in content  # value used without || or ??

if bug:
    print("FAIL: bug pattern (|| with string fallback) still present")
    sys.exit(1)
elif fix_nullish or fix_ternary or fix_no_fallback:
    print("PASS: falsy value bug fixed")
    sys.exit(0)
else:
    print("FAIL: value derivation not found")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.30)")
    echo "TEST falsy_value_fix: PASS (0.30)"
else
    echo "TEST falsy_value_fix: FAIL"
fi

# ---------- F2P 2 (0.25): Watch/observe capability exposed in js_on_load ----------
# [pr_diff] (0.25): js_on_load can register callbacks for prop changes
# Svelte code — no Node.js runtime, structural check justified.
# Accept: watch, observe, subscribe, onPropChange, or similar naming.
python3 << 'PYEOF'
import re, sys

with open("/workspace/gradio/js/html/shared/HTML.svelte") as f:
    raw = f.read()

# Strip comments
content = re.sub(r'//.*$', '', raw, flags=re.MULTILINE)
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

# The Function constructor creates the js_on_load scope.
# A watch/observe capability must be passed into it.
# Accept these patterns:
# 1. "watch"/"observe" as a named param in new Function(..., "watch", ...)
#    AND the function call passes a corresponding argument
# 2. watch/observe added to the props/reactiveProps object before the function call
# 3. Any mechanism where "watch" or "observe" appears as a callable passed to func()

# Pattern 1: Function constructor with watch/observe param
func_constructor = re.search(
    r'new\s+Function\s*\([^)]*["\'](?:watch|observe|onPropChange|subscribe)["\']',
    content)

# Pattern 2: func() call with watch/observe argument
func_call_watch = re.search(
    r'func\s*\([^)]*(?:watch|observe|onPropChange|subscribe)',
    content)

# Pattern 3: watch/observe set on reactiveProps or a context object
props_watch = re.search(
    r'(?:reactiveProps|context|scope)\s*\.\s*(?:watch|observe|onPropChange|subscribe)\s*=',
    content)

# Pattern 4: watch/observe is a destructured prop (Svelte $props)
prop_destructure = re.search(
    r'(?:watch|observe|onPropChange|subscribe)(?:_fn)?\s*[=,}]',
    content)

# At least one mechanism for exposing + one for accepting
has_exposure = func_constructor or func_call_watch or props_watch
has_prop = prop_destructure

if has_exposure or (has_prop and (func_constructor or func_call_watch)):
    print("PASS: watch/observe capability exposed in js_on_load scope")
    sys.exit(0)
else:
    # Broader check: is there a function named watch/observe that accepts a callback?
    has_watch_fn = re.search(
        r'(?:function\s+(?:watch|observe|onPropChange|subscribe)\s*\(|'
        r'(?:watch|observe|onPropChange|subscribe)\s*[:=]\s*(?:\([^)]*\)\s*=>|function))',
        content)
    if has_watch_fn and (func_constructor or func_call_watch):
        print("PASS: watch/observe function defined and passed to js_on_load")
        sys.exit(0)

    print("FAIL: no watch/observe capability found in js_on_load scope")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.25)")
    echo "TEST watch_exposed: PASS (0.25)"
else
    echo "TEST watch_exposed: FAIL"
fi

# ---------- F2P 3 (0.20): Prop changes trigger watcher notifications ----------
# [pr_diff] (0.20): Backend prop changes invoke registered watch callbacks
# Svelte code — no Node.js runtime, structural check justified.
python3 << 'PYEOF'
import re, sys

with open("/workspace/gradio/js/html/shared/HTML.svelte") as f:
    raw = f.read()

content = re.sub(r'//.*$', '', raw, flags=re.MULTILINE)
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

# Two requirements:
# 1. Change detection — comparing old/new prop values to find which changed
# 2. Notification — calling fire_watchers/notify/dispatch/emit with changed keys

# Change detection: must compare values (not just assign)
# Accept: !== / != / Object.is / JSON.stringify comparison + tracking changed keys
has_comparison = bool(re.search(
    r'(?:!==|!=|Object\.is|JSON\.stringify).*(?:props|key|value)', content))
has_changed_tracking = bool(re.search(
    r'(?:changed|diff|modified|updated)\w*\s*(?:\.|\.push|\[|=\s*\[)', content))

# Notification: calling a function with changed info
# Accept any of: fire_watchers, notifyWatchers, emitChanges, dispatchWatch, etc.
has_notification = bool(re.search(
    r'(?:fire|notify|dispatch|emit|invoke|call|trigger)\w*\s*\(\s*(?:changed|diff|modified|updated)',
    content))

# Alternative: iterate watchers directly
has_iter_watchers = bool(re.search(
    r'(?:for|forEach|map)\b.*(?:watch|observe|callback|listener|subscriber|entry|handler)',
    content) and has_comparison)

# Alternative: queueMicrotask/setTimeout wrapping notification (fires after re-render)
has_queued = bool(re.search(
    r'(?:queueMicrotask|requestAnimationFrame|setTimeout|tick)\s*\(\s*\(\)\s*=>\s*(?:fire|notify|dispatch|emit)',
    content))

if (has_comparison or has_changed_tracking) and (has_notification or has_iter_watchers or has_queued):
    print("PASS: prop change detection and watcher notification found")
    sys.exit(0)
else:
    print(f"FAIL: comparison={has_comparison}, tracking={has_changed_tracking}, "
          f"notification={has_notification}, iter={has_iter_watchers}, queued={has_queued}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.20)")
    echo "TEST prop_change_notify: PASS (0.20)"
else
    echo "TEST prop_change_notify: FAIL"
fi

# ---------- P2P (0.10): Existing functionality preserved ----------
# [repo_tests] (0.10): Existing component props and features intact
python3 << 'PYEOF'
import re, sys

with open("/workspace/gradio/js/html/Index.svelte") as f:
    content = f.read()

# These patterns exist in the original code and must survive any fix.
# We check the raw content (not comment-stripped) since these are
# existing code that should remain.
checks = [
    ("label" in content, "label prop present"),
    ("visible" in content, "visible prop present"),
    ("upload" in content, "upload functionality present"),
    ("Gradio" in content, "Gradio class usage present"),
]

failed = [desc for ok, desc in checks if not ok]
if failed:
    for f in failed:
        print(f"  FAIL: {f}")
    sys.exit(1)
else:
    print("PASS: existing functionality preserved")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.10)")
    echo "TEST p2p_existing: PASS (0.10)"
else
    echo "TEST p2p_existing: FAIL"
fi

# ---------- DOCSTRING (0.05): Python docstring documents watch ----------
# [pr_diff] (0.05): html.py docstring updated to describe watch function
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/components/html.py") as f:
    source = f.read()

# Parse AST to find the class or __init__ docstring — not just any string
tree = ast.parse(source)
found_watch_in_docstring = False

for node in ast.walk(tree):
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        docstring = ast.get_docstring(node)
        if docstring and "watch" in docstring.lower():
            found_watch_in_docstring = True
            break

# Also accept module-level docstring
module_doc = ast.get_docstring(tree)
if module_doc and "watch" in module_doc.lower():
    found_watch_in_docstring = True

# Also accept inline comments in the js_on_load parameter description
# (the gold patch puts it in a param docstring which may be a raw string, not a docstring node)
if not found_watch_in_docstring:
    # Check if "watch" appears in a string literal (docstring or param description)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if len(node.value) > 50 and "watch" in node.value.lower() and "js_on_load" in node.value.lower():
                found_watch_in_docstring = True
                break

if found_watch_in_docstring:
    print("PASS: docstring documents watch functionality")
    sys.exit(0)
else:
    print("FAIL: no docstring mentions watch")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.05)")
    echo "TEST docstring_watch: PASS (0.05)"
else
    echo "TEST docstring_watch: FAIL"
fi

# ---------- ANTI-STUB (0.10): Files are real, not stubs ----------
python3 << 'PYEOF'
import sys

files = [
    ("/workspace/gradio/js/html/Index.svelte", 40, ["Gradio", "upload", "props"]),
    ("/workspace/gradio/js/html/shared/HTML.svelte", 80, ["Handlebars", "js_on_load", "trigger"]),
]

for path, min_lines, required in files:
    try:
        with open(path) as f:
            content = f.read()
    except FileNotFoundError:
        print(f"FAIL: {path} not found")
        sys.exit(1)

    lines = len(content.strip().splitlines())
    if lines < min_lines:
        print(f"FAIL: {path} has {lines} lines, expected >= {min_lines}")
        sys.exit(1)
    for req in required:
        if req not in content:
            print(f"FAIL: {path} missing expected content '{req}'")
            sys.exit(1)

print("PASS: files are not stubs")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.10)")
    echo "TEST antistub: PASS (0.10)"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Final score ----------
SCORE=$(python3 -c "print(f'{$TOTAL:.2f}')")
echo ""
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# Optional JSON output
python3 -c "
import json
score = $TOTAL
json.dump({
    'reward': round(score, 2),
    'behavioral': round(min(score, 0.75), 2),
    'regression': round(min(0.10, score), 2),
    'config': 0.0,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
