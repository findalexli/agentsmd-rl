#!/usr/bin/env bash
set +e

SCORE=0
TARGET="js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte"

echo "=== Grading: gradio-guide-right-sidebar-nav ==="

# ─── GATE: File exists and has substantial content ─────────────────
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > /logs/verifier/reward.txt
    cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true
    exit 0
fi

FILE_LINES=$(wc -l < "$TARGET")
if [ "$FILE_LINES" -lt 50 ]; then
    echo "GATE FAIL: $TARGET is suspiciously short ($FILE_LINES lines) — likely stubbed"
    echo "0.0" > /logs/verifier/reward.txt
    cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true
    exit 0
fi
echo "GATE PASS: File exists with $FILE_LINES lines"

# ─── Parse file into sections (script vs template), strip comments ─
# All checks below use this parsed context to defeat comment-injection gaming
python3 -c "
import re, json, sys

with open('$TARGET') as f:
    content = f.read()

# Extract <script> section (actual JS code)
script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
script_raw = script_match.group(1) if script_match else ''

# Strip JS comments
script = re.sub(r'//.*$', '', script_raw, flags=re.MULTILINE)
script = re.sub(r'/\*.*?\*/', '', script, flags=re.DOTALL)

# Extract template (everything outside <script> and <style>)
template_raw = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
template_raw = re.sub(r'<style[^>]*>.*?</style>', '', template_raw, flags=re.DOTALL)

# Strip HTML comments
template = re.sub(r'<!--.*?-->', '', template_raw, flags=re.DOTALL)

# Strip Svelte comments {# ... } inside HTML comments (already handled)
# Also strip any {* ... *} Svelte comments if present
template = re.sub(r'\{/\*.*?\*/\}', '', template, flags=re.DOTALL)

json.dump({
    'script': script,
    'template': template,
    'script_raw': script_raw,
    'content': content,
    'file_lines': len(content.splitlines())
}, open('/tmp/gradio_parsed.json', 'w'))
" || {
    echo "GATE FAIL: Could not parse Svelte file"
    echo "0.0" > /logs/verifier/reward.txt
    cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true
    exit 0
}

# ─── F2P: Right sidebar with guide_slug iteration in template (0.25) ─
# [pr_diff] (0.25): Guide page has a right-side TOC sidebar rendering guide_slug entries
# WHY structural: Svelte component requires full SvelteKit build to render
# Checks: {#each guide_slug} in actual template (not comments), inside a sticky/sidebar container
python3 -c "
import json, re, sys
d = json.load(open('/tmp/gradio_parsed.json'))
t = d['template']

# Must have {#each guide_slug ...} in the actual template (not comments)
has_each_slug = bool(re.search(r'\{#each\s+guide_slug', t))

# Must have a sticky or sidebar container near the iteration
# Look for sticky + the each block in proximity (within 500 chars)
has_sidebar_container = False
for m in re.finditer(r'sticky', t):
    region = t[max(0, m.start()-300):m.end()+500]
    if re.search(r'\{#each\s+guide_slug', region):
        has_sidebar_container = True
        break

# Also accept: a div with sidebar-related classes containing the each block
if not has_sidebar_container:
    for m in re.finditer(r'float-right|right.*sidebar|sidebar.*right', t):
        region = t[max(0, m.start()-100):m.end()+500]
        if re.search(r'\{#each\s+guide_slug', region):
            has_sidebar_container = True
            break

if has_each_slug and has_sidebar_container:
    print('PASS')
else:
    reasons = []
    if not has_each_slug: reasons.append('no {#each guide_slug} in template')
    if not has_sidebar_container: reasons.append('no sticky/sidebar container around slug iteration')
    print('FAIL:' + '; '.join(reasons))
    sys.exit(1)
" && {
    echo "PASS (0.25): Right sidebar with guide_slug iteration in template"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
} || {
    echo "FAIL (0.25): Missing right sidebar with guide_slug iteration"
}

# ─── F2P: Scroll tracking logic in script section (0.20) ───────────
# [pr_diff] (0.20): Reactive scroll tracking updates active section indicator
# Checks: actual JS variable + reactive statement in <script>, not comments
python3 -c "
import json, re, sys
d = json.load(open('/tmp/gradio_parsed.json'))
s = d['script']
t = d['template']

# Must declare a tracking variable in script (not just a comment)
# Patterns: let/const/var for current_header, active_section, current_id, activeId, etc.
has_tracking_var = bool(re.search(
    r'(?:let|const|var)\s+(?:current_header|active_section|active_slug|activeId|currentId|current_id|current_header_id|activeHeading)',
    s
))

# Must have reactive scroll logic: either $: with scroll/y/offset, or onMount with scroll listener
has_reactive_scroll = bool(
    re.search(r'\\\$:\s*(?:if\s*\(|{).*(?:y\b|scroll|offset)', s, re.DOTALL) or
    re.search(r'(?:addEventListener|onscroll|IntersectionObserver|scrollY|offsetTop)', s)
)

# The template must use the tracking variable for highlighting (class binding)
has_highlight = bool(re.search(
    r'(?:current_header|active_section|active_slug|activeId|currentId|current_id|current_header_id|activeHeading)',
    t
))

if has_tracking_var and has_reactive_scroll and has_highlight:
    print('PASS')
else:
    reasons = []
    if not has_tracking_var: reasons.append('no tracking variable declared in script')
    if not has_reactive_scroll: reasons.append('no reactive scroll logic in script')
    if not has_highlight: reasons.append('tracking variable not used in template for highlighting')
    print('FAIL:' + '; '.join(reasons))
    sys.exit(1)
" && {
    echo "PASS (0.20): Scroll tracking logic in script with template highlighting"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
} || {
    echo "FAIL (0.20): Missing scroll tracking logic"
}

# ─── F2P: Content layout accommodates sidebar (0.15) ───────────────
# [pr_diff] (0.15): Main content div no longer uses mx-auto, allows right sidebar space
# The base file has "lg:w-8/12 mx-auto" — the fix must remove mx-auto or adjust layout
python3 -c "
import json, re, sys
d = json.load(open('/tmp/gradio_parsed.json'))
c = d['content']

# Check that 'lg:w-8/12 mx-auto' does NOT appear (the buggy pattern)
if re.search(r'lg:w-8/12\s+mx-auto', c):
    print('FAIL: lg:w-8/12 mx-auto still present')
    sys.exit(1)

# Must still have some width class for main content area
if re.search(r'lg:w-(?:8/12|2/3|9/12|3/4)', c):
    print('PASS')
else:
    # Alternative: they restructured completely, which is fine if sidebar exists
    print('PASS')
" && {
    echo "PASS (0.15): Content layout adjusted for right sidebar"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
} || {
    echo "FAIL (0.15): Content area still uses mx-auto — no room for right sidebar"
}

# ─── F2P: Heading level for hierarchical indentation (0.10) ────────
# [pr_diff] (0.10): guide_slug entries rendered with level-based indentation
# Checks: template has dynamic padding/margin based on level/depth in the {#each} context
python3 -c "
import json, re, sys
d = json.load(open('/tmp/gradio_parsed.json'))
t = d['template']
s = d['script']

# In the template, inside or near {#each guide_slug}, there must be
# dynamic indentation using level/depth
# Find the {#each guide_slug} block region
each_match = re.search(r'\{#each\s+guide_slug.*?\{/each\}', t, re.DOTALL)
if not each_match:
    print('FAIL: no {#each guide_slug} block found')
    sys.exit(1)

each_block = each_match.group(0)

# Must reference level or depth for indentation
has_level_ref = bool(re.search(r'\.level|\.depth|heading_level', each_block))

# Must have dynamic style/class for indentation (padding-left, margin-left, pl-, ml-)
has_dynamic_indent = bool(re.search(r'(?:padding-left|margin-left|pl-|ml-|indent).*(?:level|depth)|(?:level|depth).*(?:padding-left|margin-left|pl-|ml-|indent)', each_block, re.DOTALL))

# Also accept: style= with computed value using level
if not has_dynamic_indent:
    has_dynamic_indent = bool(re.search(r'style=.*\{.*(?:level|depth)', each_block, re.DOTALL))

if has_level_ref and has_dynamic_indent:
    print('PASS')
else:
    reasons = []
    if not has_level_ref: reasons.append('no level/depth reference in each block')
    if not has_dynamic_indent: reasons.append('no dynamic indentation based on level')
    print('FAIL:' + '; '.join(reasons))
    sys.exit(1)
" && {
    echo "PASS (0.10): Heading level-based indentation in TOC"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
} || {
    echo "FAIL (0.10): Missing heading level indentation"
}

# ─── P2P: Left sidebar navigation preserved (0.10) ─────────────────
# [pr_diff] (0.10): Left sidebar with guide categories preserved
python3 -c "
import json, re, sys
d = json.load(open('/tmp/gradio_parsed.json'))
t = d['template']

# The template must still iterate guide_names for left sidebar
has_guide_names = bool(re.search(r'\{#each\s+(?:guide_names|data\.guide_names)', t))
has_category = bool(re.search(r'category', t))

if has_guide_names and has_category:
    print('PASS')
else:
    print('FAIL')
    sys.exit(1)
" && {
    echo "PASS (0.10): Left sidebar navigation preserved"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
} || {
    echo "FAIL (0.10): Left sidebar navigation broken or removed"
}

# ─── P2P: Previous/next navigation preserved (0.05) ────────────────
# [pr_diff] (0.05): Previous/next guide links still present in template
python3 -c "
import json, re, sys
d = json.load(open('/tmp/gradio_parsed.json'))
t = d['template']

has_prev = bool(re.search(r'prev_guide', t))
has_next = bool(re.search(r'next_guide', t))

if has_prev and has_next:
    print('PASS')
else:
    print('FAIL')
    sys.exit(1)
" && {
    echo "PASS (0.05): Previous/next guide navigation preserved"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
} || {
    echo "FAIL (0.05): Previous/next navigation missing"
}

# ─── Config: Tailwind CSS consistency (0.05) ────────────────────────
# [agent_config] (0.05): "Be consistent with the style of the surrounding code" — AGENTS.md:45 @ 41e98f9
# The right sidebar section must use Tailwind classes (not inline CSS for everything)
python3 -c "
import json, re, sys
d = json.load(open('/tmp/gradio_parsed.json'))
t = d['template']

# Find the right sidebar region (around {#each guide_slug})
each_match = re.search(r'\{#each\s+guide_slug.*?\{/each\}', t, re.DOTALL)
if not each_match:
    # No sidebar found — this check is moot (other checks will catch it)
    print('PASS')
    sys.exit(0)

region_start = max(0, each_match.start() - 300)
region = t[region_start:each_match.end() + 100]

# Must use Tailwind utility classes in the sidebar region
has_tailwind = bool(re.search(r'(?:text-sm|text-gray|dark:|lg:|hover:|space-y|font-)', region))

if has_tailwind:
    print('PASS')
else:
    print('FAIL')
    sys.exit(1)
" && {
    echo "PASS (0.05): Sidebar uses Tailwind CSS classes consistent with codebase"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
} || {
    echo "FAIL (0.05): Sidebar not using Tailwind CSS classes consistently"
}

# ─── Anti-stub: File has substantial content with both sections (0.10)
# [pr_diff] (0.10): File not gutted — must have script + template of reasonable size
python3 -c "
import json, sys
d = json.load(open('/tmp/gradio_parsed.json'))

# Base file is ~356 lines; fixed file should be ~380+
if d['file_lines'] < 350:
    print(f\"FAIL: only {d['file_lines']} lines\")
    sys.exit(1)

# Must have both script and template sections of reasonable size
script_lines = len([l for l in d['script'].strip().splitlines() if l.strip()])
template_lines = len([l for l in d['template'].strip().splitlines() if l.strip()])

if script_lines < 10:
    print(f'FAIL: script section too short ({script_lines} non-empty lines)')
    sys.exit(1)
if template_lines < 50:
    print(f'FAIL: template section too short ({template_lines} non-empty lines)')
    sys.exit(1)

print('PASS')
" && {
    echo "PASS (0.10): File has substantial script and template content"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
} || {
    echo "FAIL (0.10): File content is too short or missing sections"
}

# ─── Final score ─────────────────────────────────────────────────────
echo ""
echo "=== Final score: $SCORE ==="
echo "$SCORE" > /logs/verifier/reward.txt
cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true

# Build reward.json
python3 -c "
import json
score = float('$SCORE')
behavioral = min(score, 0.70)  # F2P checks: 0.25 + 0.20 + 0.15 + 0.10
regression = min(max(score - 0.70, 0), 0.15)  # P2P: 0.10 + 0.05
config = min(max(score - 0.85, 0), 0.05)  # config: 0.05
anti_stub = min(max(score - 0.90, 0), 0.10)  # anti-stub: 0.10
json.dump({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
    'anti_stub': round(anti_stub, 4)
}, open('/logs/verifier/reward.json', 'w'))
" 2>/dev/null || true
cp /logs/verifier/reward.json reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
