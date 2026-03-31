#!/usr/bin/env bash
# Verifier for nextjs-turbopack-graph-span-modules
#
# Enhancement: Add module count fields to turbopack module graph tracing spans.
# Three files changed: app.rs (per-endpoint span), project.rs (whole-app span),
# module_graph/mod.rs (expose module_count method).
#
# All checks are structural because this is Rust code requiring ~200+ crates to compile.
# However, checks are scoped to correct function bodies and strip comments/strings
# to prevent gaming via dead-code injection.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

APP_FILE="/workspace/next.js/crates/next-api/src/app.rs"
PROJECT_FILE="/workspace/next.js/crates/next-api/src/project.rs"
MOD_FILE="/workspace/next.js/turbopack/crates/turbopack-core/src/module_graph/mod.rs"

###############################################################################
# GATE: Source files exist
###############################################################################
if [ ! -f "$APP_FILE" ] || [ ! -f "$PROJECT_FILE" ] || [ ! -f "$MOD_FILE" ]; then
    echo "GATE FAILED: Required source files missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 [pr_diff]      (0.30): module_count method in impl SingleModuleGraph,
#                                  annotated with turbo_tasks, returns u64
#   TEST 2 [pr_diff]      (0.20): Per-endpoint code in app.rs records module count
#                                  into a tracing span
#   TEST 3 [pr_diff]      (0.20): whole_app_module_graph_operation records module
#                                  count into a tracing span
#   TEST 4 [pr_diff]      (0.10): Performance guard — module count only computed
#                                  when span is active
#   TEST 5 [pr_diff]      (0.05): Pass-to-pass — whole_app_module_graphs returns
#                                  BaseAndFullModuleGraph
#   TEST 6 [structural]   (0.15): Anti-stub — changed files have substantial
#                                  content and real Rust structure
#   TOTAL                 = 1.00
###############################################################################

SCORE="0.0"

###############################################################################
# Helper: Strip Rust comments and string literals to prevent dead-code gaming.
# This gives us "code-only" content for pattern matching.
###############################################################################
cat > /tmp/strip_rust.py << 'STRIP_EOF'
"""Strip Rust line comments, block comments, and string literals from source."""
import re, sys

def strip_rust(src):
    # Remove block comments (non-greedy, handles nesting poorly but good enough)
    src = re.sub(r'/\*.*?\*/', ' ', src, flags=re.DOTALL)
    # Remove line comments
    src = re.sub(r'//[^\n]*', '', src)
    # Remove string literals (handle escaped quotes)
    src = re.sub(r'"(?:[^"\\]|\\.)*"', '""', src)
    # Remove raw string literals r#"..."#
    src = re.sub(r'r#+"[^"]*"#+', '""', src)
    return src

if __name__ == '__main__':
    print(strip_rust(open(sys.argv[1]).read()))
STRIP_EOF

###############################################################################
# Helper: Extract a Rust function body by name (brace-balanced).
# Returns the code from `fn <name>` through its closing brace.
###############################################################################
cat > /tmp/extract_fn.py << 'EXTRACT_EOF'
"""Extract a Rust function body by name using brace-balancing."""
import re, sys

def extract_fn(src, fn_name):
    """Find `fn <fn_name>` and return the full function body (brace-balanced)."""
    pattern = re.compile(r'(pub\s+)?(async\s+)?fn\s+' + re.escape(fn_name) + r'\b')
    match = pattern.search(src)
    if not match:
        return None
    start = match.start()
    # Find the opening brace
    idx = src.index('{', match.end())
    depth = 1
    idx += 1
    while idx < len(src) and depth > 0:
        if src[idx] == '{':
            depth += 1
        elif src[idx] == '}':
            depth -= 1
        idx += 1
    return src[start:idx]

if __name__ == '__main__':
    filepath, fn_name = sys.argv[1], sys.argv[2]
    src = open(filepath).read()
    body = extract_fn(src, fn_name)
    if body:
        print(body)
    else:
        sys.exit(1)
EXTRACT_EOF

###############################################################################
# Helper: Extract an impl block for a type.
###############################################################################
cat > /tmp/extract_impl.py << 'EXTRACT_EOF'
"""Extract an impl block for a given type name."""
import re, sys

def extract_impl(src, type_name):
    """Find `impl <type_name>` and return the full impl body."""
    pattern = re.compile(r'impl\s+' + re.escape(type_name) + r'\b')
    results = []
    for match in pattern.finditer(src):
        start = match.start()
        idx = src.index('{', match.end())
        depth = 1
        idx += 1
        while idx < len(src) and depth > 0:
            if src[idx] == '{':
                depth += 1
            elif src[idx] == '}':
                depth -= 1
            idx += 1
        results.append(src[start:idx])
    return results

if __name__ == '__main__':
    filepath, type_name = sys.argv[1], sys.argv[2]
    src = open(filepath).read()
    blocks = extract_impl(src, type_name)
    if blocks:
        print('\n---IMPL_SEPARATOR---\n'.join(blocks))
    else:
        sys.exit(1)
EXTRACT_EOF

###############################################################################
# TEST 1 [pr_diff] (0.30): module_count method in impl SingleModuleGraph
#
# Requirements (any valid implementation):
#   - A method named module_count (or get_module_count, len, count) in an
#     impl SingleModuleGraph block
#   - Annotated with #[turbo_tasks::function]
#   - Returns something involving u64 (Vc<u64>, usize as u64, etc.)
#   - References the internal module count data (number_of_modules or equivalent)
#   - Has a real body (not a stub)
#
# WHY structural: Rust code requiring full turbopack workspace (~200 crates).
###############################################################################
echo ""
echo "TEST 1: [pr_diff] (0.30) module_count method in impl SingleModuleGraph"
python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_rust import strip_rust
from extract_impl import extract_impl

with open("/workspace/next.js/turbopack/crates/turbopack-core/src/module_graph/mod.rs") as f:
    raw_src = f.read()

# Strip comments/strings for matching
src = strip_rust(raw_src)

# Find impl SingleModuleGraph blocks
impl_blocks = extract_impl(src, "SingleModuleGraph")
if not impl_blocks:
    print("FAIL: No impl SingleModuleGraph block found")
    sys.exit(1)

# Look for a method that exposes module count in ANY impl block
found = False
for block in impl_blocks:
    # Accept: module_count, get_module_count, num_modules, module_len
    fn_match = re.search(
        r'fn\s+(module_count|get_module_count|num_modules|module_len)\b', block
    )
    if not fn_match:
        continue

    fn_name = fn_match.group(1)

    # Must be annotated with turbo_tasks::function (look in raw source near the fn)
    # Find the fn in raw source and check preceding lines for the attribute
    raw_lines = raw_src.split('\n')
    for i, line in enumerate(raw_lines):
        if f'fn {fn_name}' in line:
            # Check up to 5 lines above for the attribute
            preceding = '\n'.join(raw_lines[max(0, i-5):i+1])
            if 'turbo_tasks' in preceding and 'function' in preceding:
                break
    else:
        print(f"FAIL: {fn_name} not annotated with #[turbo_tasks::function]")
        sys.exit(1)

    # Must reference internal module data — accept number_of_modules or
    # self.graph, self.modules, self.entries, len() on internal data, etc.
    # Extract the function body within the impl block
    fn_start = fn_match.start()
    # Find opening brace after fn signature
    brace_idx = block.index('{', fn_start + len(fn_match.group(0)))
    depth = 1
    idx = brace_idx + 1
    while idx < len(block) and depth > 0:
        if block[idx] == '{': depth += 1
        elif block[idx] == '}': depth -= 1
        idx += 1
    fn_body = block[brace_idx:idx]

    # Body must not be trivially empty (anti-stub: >1 non-whitespace statement)
    body_content = fn_body.strip('{}').strip()
    if len(body_content) < 10:
        print(f"FAIL: {fn_name} body is a stub (too short)")
        sys.exit(1)

    # Must involve u64 somewhere (return type or cast)
    fn_context = block[fn_start:idx]
    if 'u64' not in fn_context and 'usize' not in fn_context:
        print(f"FAIL: {fn_name} doesn't return a numeric type (u64/usize)")
        sys.exit(1)

    found = True
    break

if not found:
    print("FAIL: No module count method found in impl SingleModuleGraph")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 2 [pr_diff] (0.20): Per-endpoint code in app.rs records module count
#                           into a tracing span.
#
# Accepts ANY valid tracing pattern:
#   - info_span! / span! / #[instrument] with a "modules" field
#   - .record("modules", ...) OR fields(modules = ...) with non-Empty value
#   - .instrument() OR .in_scope() OR #[instrument] to attach span
#   - module_count() call to get the data
#
# Scoped to code near the endpoint graph construction (not just anywhere).
# WHY structural: Rust code, can't compile.
###############################################################################
echo ""
echo "TEST 2: [pr_diff] (0.20) app.rs records module count in tracing span"
python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_rust import strip_rust

with open("/workspace/next.js/crates/next-api/src/app.rs") as f:
    raw_src = f.read()

src = strip_rust(raw_src)

# Check 1: A tracing span with a "modules" field must exist in code (not comments/strings)
# Accept: info_span!, span!, debug_span!, trace_span!, #[instrument(fields(modules))]
has_span_with_modules = bool(
    re.search(r'(info_span!|span!|debug_span!|trace_span!)\s*\([^;]*modules\s*=', src)
    or re.search(r'#\[instrument\s*\([^]]*fields\s*\([^)]*modules', src)
)
if not has_span_with_modules:
    print("FAIL: No tracing span with 'modules' field found in app.rs code")
    sys.exit(1)

# Check 2: Module count is recorded into the span
# Accept: .record("modules", ...) OR direct field assignment
has_record = bool(
    re.search(r'\.record\(\s*["\']modules["\']', src)
)
if not has_record:
    print("FAIL: No span.record(\"modules\", ...) found in app.rs code")
    sys.exit(1)

# Check 3: module_count (or equivalent) is called to get the data
# Accept: module_count(), num_modules(), get_module_count(), .len() on modules
has_count_call = bool(
    re.search(r'module_count\s*\(\)', src)
    or re.search(r'(num_modules|get_module_count|module_len)\s*\(\)', src)
)
if not has_count_call:
    print("FAIL: No module count retrieval call found in app.rs code")
    sys.exit(1)

# Check 4: Span is attached to async work
# Accept: .instrument(), .in_scope(), #[instrument], or span entered via .enter()/.entered()
has_attach = bool(
    re.search(r'\.(instrument|in_scope|enter|entered)\s*\(', src)
    or re.search(r'#\[instrument', src)
)
if not has_attach:
    print("FAIL: Span not attached to async work in app.rs")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 3 [pr_diff] (0.20): whole_app_module_graph_operation records module count
#
# Scoped to the whole_app_module_graph_operation function body.
# Accepts same range of valid tracing patterns as TEST 2.
# WHY structural: Rust code, can't compile.
###############################################################################
echo ""
echo "TEST 3: [pr_diff] (0.20) project.rs whole_app_module_graph_operation has span with modules"
python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_rust import strip_rust
from extract_fn import extract_fn

with open("/workspace/next.js/crates/next-api/src/project.rs") as f:
    raw_src = f.read()

# Strip comments/strings
src = strip_rust(raw_src)

# Extract the function body (scoped check — not whole file)
fn_body = extract_fn(src, "whole_app_module_graph_operation")
if fn_body is None:
    print("FAIL: whole_app_module_graph_operation function not found")
    sys.exit(1)

# Check 1: Tracing span with modules field
has_span = bool(
    re.search(r'(info_span!|span!|debug_span!|trace_span!)\s*\([^;]*modules\s*=', fn_body)
    or re.search(r'#\[instrument\s*\([^]]*fields\s*\([^)]*modules', fn_body)
)
if not has_span:
    print("FAIL: No tracing span with 'modules' field in whole_app_module_graph_operation")
    sys.exit(1)

# Check 2: Records module count
has_record = bool(re.search(r'\.record\(\s*["\']modules["\']', fn_body))
if not has_record:
    print("FAIL: span.record(\"modules\", ...) not found in whole_app_module_graph_operation")
    sys.exit(1)

# Check 3: Calls module_count (or equivalent)
has_count = bool(
    re.search(r'module_count\s*\(\)', fn_body)
    or re.search(r'(num_modules|get_module_count|module_len)\s*\(\)', fn_body)
)
if not has_count:
    print("FAIL: No module count call in whole_app_module_graph_operation")
    sys.exit(1)

# Check 4: Span attached to work
has_attach = bool(
    re.search(r'\.(instrument|in_scope|enter|entered)\s*\(', fn_body)
    or re.search(r'#\[instrument', fn_body)
)
if not has_attach:
    print("FAIL: Span not attached to work in whole_app_module_graph_operation")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 4 [pr_diff] (0.10): Performance guard — module count only computed
# when span is active.
#
# Accepts: is_disabled(), is_none(), !is_enabled(), has_field(), or any
# conditional guard near module_count computation.
# Checks BOTH files. Scoped to stripped code.
# WHY structural: Rust code, can't compile.
###############################################################################
echo ""
echo "TEST 4: [pr_diff] (0.10) Performance guard before module count computation"
python3 << 'PYEOF'
import re, sys
sys.path.insert(0, '/tmp')
from strip_rust import strip_rust

files = [
    ("/workspace/next.js/crates/next-api/src/app.rs", "app.rs"),
    ("/workspace/next.js/crates/next-api/src/project.rs", "project.rs"),
]

for path, name in files:
    with open(path) as f:
        src = strip_rust(f.read())

    # Accept various guard patterns:
    # is_disabled(), is_none(), !is_enabled(), has_field()
    guard_patterns = [
        r'is_disabled\s*\(\)',
        r'is_none\s*\(\)',
        r'!\s*\w+\.is_enabled\s*\(\)',
        r'has_field\s*\(',
    ]

    has_guard = any(re.search(p, src) for p in guard_patterns)
    if not has_guard:
        print(f"FAIL: {name} missing performance guard (is_disabled/is_none/is_enabled)")
        sys.exit(1)

    # Guard must be near (within 30 lines of) a module_count or record("modules") call
    lines = src.split('\n')
    guard_line = None
    for i, line in enumerate(lines):
        if any(re.search(p, line) for p in guard_patterns):
            guard_line = i
            break

    if guard_line is not None:
        window = '\n'.join(lines[guard_line:guard_line+30])
        if 'module_count' not in window and 'record' not in window:
            print(f"FAIL: {name} guard not near module count computation")
            sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 5 [pr_diff] (0.05): Pass-to-pass — whole_app_module_graphs returns
# BaseAndFullModuleGraph and whole_app_module_graph_operation still exists
###############################################################################
echo ""
echo "TEST 5: [pr_diff] (0.05) whole_app_module_graphs returns BaseAndFullModuleGraph"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from strip_rust import strip_rust

with open("/workspace/next.js/crates/next-api/src/project.rs") as f:
    src = strip_rust(f.read())

if 'fn whole_app_module_graphs' not in src:
    print("FAIL: whole_app_module_graphs function missing")
    sys.exit(1)

if 'BaseAndFullModuleGraph' not in src:
    print("FAIL: BaseAndFullModuleGraph return type missing")
    sys.exit(1)

if 'fn whole_app_module_graph_operation' not in src:
    print("FAIL: whole_app_module_graph_operation function missing")
    sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 6 [structural] (0.15): Anti-stub — changed files have substantial
# content and real Rust structure (functions, impl blocks).
###############################################################################
echo ""
echo "TEST 6: [structural] (0.15) Anti-stub — files not replaced with stubs"
python3 << 'PYEOF'
import re, sys

checks = [
    ("/workspace/next.js/crates/next-api/src/app.rs", "app.rs", 500),
    ("/workspace/next.js/crates/next-api/src/project.rs", "project.rs", 500),
    ("/workspace/next.js/turbopack/crates/turbopack-core/src/module_graph/mod.rs", "mod.rs", 500),
]

for path, name, min_lines in checks:
    with open(path) as f:
        lines = f.readlines()

    if len(lines) < min_lines:
        print(f"FAIL: {name} only has {len(lines)} lines — likely stubbed (need >= {min_lines})")
        sys.exit(1)

    content = ''.join(lines)

    # Must have real Rust structure: multiple fn definitions and impl blocks
    fn_count = len(re.findall(r'\bfn\s+\w+', content))
    impl_count = len(re.findall(r'\bimpl\b', content))

    if fn_count < 5:
        print(f"FAIL: {name} only has {fn_count} function defs — likely stubbed")
        sys.exit(1)

    if impl_count < 2:
        print(f"FAIL: {name} only has {impl_count} impl blocks — likely stubbed")
        sys.exit(1)

print("PASS")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "  FAIL"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "========================================="
echo "TOTAL SCORE: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
