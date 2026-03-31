#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0
LOGS=""

log() { LOGS="$LOGS\n$1"; echo "$1"; }

award() {
    local pts=$1 max=$2 desc="$3"
    SCORE=$(python3 -c "print($SCORE + $pts)")
    TOTAL=$(python3 -c "print($TOTAL + $max)")
    log "  $desc: $pts / $max"
}

# ── GATE: syntax check on fonts.py ──
# [pr_diff] (gate): fonts.py must be valid Python
log "=== GATE: Syntax check ==="
if ! python3 -c "
import py_compile, sys
try:
    py_compile.compile('/workspace/gradio/gradio/themes/utils/fonts.py', doraise=True)
except py_compile.PyCompileError as e:
    print(f'Syntax error: {e}', file=sys.stderr)
    sys.exit(1)
"; then
    log "GATE FAILED: fonts.py has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
log "  GATE passed"

# ── GATE: syntax check on generate_theme.py ──
# [pr_diff] (gate): generate_theme.py must be valid Python
if ! python3 -c "
import py_compile, sys
try:
    py_compile.compile('/workspace/gradio/scripts/generate_theme.py', doraise=True)
except py_compile.PyCompileError as e:
    print(f'Syntax error: {e}', file=sys.stderr)
    sys.exit(1)
"; then
    log "GATE FAILED: generate_theme.py has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
log "  GATE passed"

# ── Behavioral: fail-to-pass tests ──
log ""
log "=== Behavioral Tests ==="

# [pr_diff] (0.30): LocalFont.stylesheet() must produce numeric font-weight values
BEHAV1=0
python3 -c "
import sys
sys.path.insert(0, '/workspace/gradio')
from gradio.themes.utils.fonts import LocalFont

font = LocalFont('IBM Plex Mono')
css = font.stylesheet()['css']

# font-weight must be numeric (400, 700), not text (Regular, Bold)
import re
weights = re.findall(r'font-weight:\s*(\S+);', css)
print(f'Found font-weight values: {weights}')
for w in weights:
    if not w.isdigit():
        print(f'FAIL: font-weight \"{w}\" is not numeric')
        sys.exit(1)
if '400' not in weights or '700' not in weights:
    print(f'FAIL: expected 400 and 700 in weights, got {weights}')
    sys.exit(1)
print('PASS: font-weight values are numeric')
" && BEHAV1=1 || true

if [ "$BEHAV1" = "1" ]; then
    award 0.30 0.30 "[pr_diff] numeric font-weight values"
else
    award 0.00 0.30 "[pr_diff] numeric font-weight values"
fi

# [pr_diff] (0.15): Font file paths still use text names (Regular/Bold) in URL
BEHAV2=0
python3 -c "
import sys
sys.path.insert(0, '/workspace/gradio')
from gradio.themes.utils.fonts import LocalFont

font = LocalFont('IBM Plex Mono')
css = font.stylesheet()['css']

# File paths should still reference IBMPlexMono-Regular.woff2 and IBMPlexMono-Bold.woff2
if 'IBMPlexMono-Regular.woff2' not in css:
    print(f'FAIL: expected IBMPlexMono-Regular.woff2 in URL')
    sys.exit(1)
if 'IBMPlexMono-Bold.woff2' not in css:
    print(f'FAIL: expected IBMPlexMono-Bold.woff2 in URL')
    sys.exit(1)
print('PASS: file paths use text weight names correctly')
" && BEHAV2=1 || true

if [ "$BEHAV2" = "1" ]; then
    award 0.15 0.15 "[pr_diff] file URLs use text weight names"
else
    award 0.00 0.15 "[pr_diff] file URLs use text weight names"
fi

# [pr_diff] (0.20): generate_theme.py --website flag rewrites static paths
BEHAV3=0
python3 -c "
import sys, subprocess, tempfile, os

# Run generate_theme.py with --website flag
with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
    tmp = f.name

result = subprocess.run(
    [sys.executable, '/workspace/gradio/scripts/generate_theme.py', '--website', '--outfile', tmp],
    capture_output=True, text=True, cwd='/workspace/gradio'
)
if result.returncode != 0:
    print(f'FAIL: generate_theme.py --website failed: {result.stderr}')
    os.unlink(tmp)
    sys.exit(1)

css = open(tmp).read()
os.unlink(tmp)

# Should NOT contain url('static/ — should be rewritten to url('/
if \"url('static/\" in css:
    print('FAIL: --website flag did not rewrite static/ paths')
    sys.exit(1)

# Should contain url('/ for font paths
if \"url('/\" not in css and 'url(\\'/') not in css:
    print('FAIL: expected rewritten paths starting with /')
    sys.exit(1)

print('PASS: --website flag rewrites paths correctly')
" && BEHAV3=1 || true

if [ "$BEHAV3" = "1" ]; then
    award 0.20 0.20 "[pr_diff] --website flag rewrites static paths"
else
    award 0.00 0.20 "[pr_diff] --website flag rewrites static paths"
fi

# [pr_diff] (0.10): generate_theme.py without --website preserves static/ paths
BEHAV4=0
python3 -c "
import sys, subprocess, tempfile, os

with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
    tmp = f.name

result = subprocess.run(
    [sys.executable, '/workspace/gradio/scripts/generate_theme.py', '--outfile', tmp],
    capture_output=True, text=True, cwd='/workspace/gradio'
)
if result.returncode != 0:
    print(f'FAIL: generate_theme.py failed: {result.stderr}')
    os.unlink(tmp)
    sys.exit(1)

css = open(tmp).read()
os.unlink(tmp)

# Without --website, should still have static/ paths
if \"url('static/\" not in css:
    print('FAIL: without --website, static/ paths should be preserved')
    sys.exit(1)

print('PASS: without --website, static paths preserved')
" && BEHAV4=1 || true

if [ "$BEHAV4" = "1" ]; then
    award 0.10 0.10 "[pr_diff] default mode preserves static/ paths"
else
    award 0.00 0.10 "[pr_diff] default mode preserves static/ paths"
fi

# ── Regression: pass-to-pass ──
log ""
log "=== Regression Tests ==="

# [regression] (0.10): GoogleFont still generates valid stylesheets
REGR1=0
python3 -c "
import sys
sys.path.insert(0, '/workspace/gradio')
from gradio.themes.utils.fonts import GoogleFont

font = GoogleFont('Source Sans Pro')
result = font.stylesheet()
if result['url'] is None:
    print('FAIL: GoogleFont should have a URL')
    sys.exit(1)
if 'fonts.googleapis.com' not in result['url']:
    print(f'FAIL: unexpected URL: {result[\"url\"]}')
    sys.exit(1)
print('PASS: GoogleFont stylesheet still works')
" && REGR1=1 || true

if [ "$REGR1" = "1" ]; then
    award 0.10 0.10 "[regression] GoogleFont stylesheet works"
else
    award 0.00 0.10 "[regression] GoogleFont stylesheet works"
fi

# [regression] (0.05): Font base class works
REGR2=0
python3 -c "
import sys
sys.path.insert(0, '/workspace/gradio')
from gradio.themes.utils.fonts import Font

font = Font('sans-serif')
assert str(font) == 'sans-serif', f'Expected sans-serif, got {str(font)}'
result = font.stylesheet()
assert result == {'url': None, 'css': None}, f'Unexpected result: {result}'
print('PASS: Font base class works')
" && REGR2=1 || true

if [ "$REGR2" = "1" ]; then
    award 0.05 0.05 "[regression] Font base class works"
else
    award 0.00 0.05 "[regression] Font base class works"
fi

# ── Config-derived checks ──
log ""
log "=== Config-derived Tests ==="

# [agent_config] (0.05): "Python code is formatted with ruff" — AGENTS.md:43
CONFIG1=0
if command -v ruff &>/dev/null; then
    ruff check /workspace/gradio/gradio/themes/utils/fonts.py --select E,W --quiet 2>/dev/null && CONFIG1=1 || true
else
    # ruff not available, check basic formatting with python
    python3 -c "
import ast, sys
try:
    with open('/workspace/gradio/gradio/themes/utils/fonts.py') as f:
        ast.parse(f.read())
    print('PASS: Python syntax valid (ruff unavailable)')
except SyntaxError as e:
    print(f'FAIL: {e}')
    sys.exit(1)
" && CONFIG1=1 || true
fi

if [ "$CONFIG1" = "1" ]; then
    award 0.05 0.05 "[agent_config] ruff-clean Python — AGENTS.md:43"
else
    award 0.00 0.05 "[agent_config] ruff-clean Python — AGENTS.md:43"
fi

# [agent_config] (0.05): "Be consistent with the style of the surrounding code" — AGENTS.md:45
# Check that generate_theme.py still uses argparse consistently
CONFIG2=0
python3 -c "
import ast, sys

with open('/workspace/gradio/scripts/generate_theme.py') as f:
    tree = ast.parse(f.read())

# Should still use argparse (consistent with existing style)
has_argparse = any(
    isinstance(node, ast.Import) and any(a.name == 'argparse' for a in node.names)
    for node in ast.walk(tree)
)
if not has_argparse:
    print('FAIL: generate_theme.py should use argparse (consistent style)')
    sys.exit(1)
print('PASS: generate_theme.py uses argparse consistently')
" && CONFIG2=1 || true

if [ "$CONFIG2" = "1" ]; then
    award 0.05 0.05 "[agent_config] consistent argparse style — AGENTS.md:45"
else
    award 0.00 0.05 "[agent_config] consistent argparse style — AGENTS.md:45"
fi

# ── Final score ──
log ""
log "=== Summary ==="

FINAL=$(python3 -c "print(round($SCORE, 4))")
log "Total: $FINAL / 1.00"

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt

BEHAV_SCORE=$(python3 -c "print(round($SCORE - 0.0, 4))")
python3 -c "
import json
score = $FINAL
# Approximate breakdown
print(json.dumps({
    'reward': score,
    'behavioral': min(score, 0.75),
    'regression': min(max(score - 0.75, 0), 0.15),
    'config': min(max(score - 0.90, 0), 0.10),
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
