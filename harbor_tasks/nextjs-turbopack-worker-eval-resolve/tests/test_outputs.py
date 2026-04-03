"""
Task: nextjs-turbopack-worker-eval-resolve
Repo: vercel/next.js @ e9df6ed9dc381cf99e54c91d984799ca51e2940f
PR:   91666

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: All checks are structural because turbopack requires nightly Rust +
200+ crates to compile — code cannot be executed in the test container.
# AST-only because: Rust code requires full cargo build with nightly toolchain
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
REFS = Path(f"{REPO}/turbopack/crates/turbopack-ecmascript/src/references/mod.rs")
PARSE = Path(f"{REPO}/turbopack/crates/turbopack-core/src/resolve/parse.rs")


def strip_rust_comments(src: str) -> str:
    """Remove // line comments and /* */ block comments, preserving strings."""
    result = []
    i = 0
    in_string = False
    while i < len(src):
        if not in_string and src[i] == '"' and (i == 0 or src[i - 1] != '\\'):
            in_string = True
            result.append(src[i])
            i += 1
            continue
        if in_string and src[i] == '"' and (i == 0 or src[i - 1] != '\\'):
            in_string = False
            result.append(src[i])
            i += 1
            continue
        if in_string:
            result.append(src[i])
            i += 1
            continue
        if src[i:i + 2] == '//':
            while i < len(src) and src[i] != '\n':
                i += 1
            continue
        if src[i:i + 2] == '/*':
            i += 2
            while i < len(src) - 1 and src[i:i + 2] != '*/':
                i += 1
            i += 2
            continue
        result.append(src[i])
        i += 1
    return ''.join(result)


def get_worker_handler(src: str) -> str:
    """Extract NodeWorkerConstructor match arm from mod.rs source."""
    # Find the specific match arm (not enum definition or import)
    match = re.search(r'NodeWorkerConstructor\s*=>', src)
    assert match, "NodeWorkerConstructor match arm not found in mod.rs"
    start = match.start()
    rest = src[start:]

    # Find the next WellKnownFunctionKind:: match arm to bound the handler
    next_match = re.search(r'WellKnownFunctionKind::\w+\s*=>', rest[80:])
    if next_match:
        return rest[:80 + next_match.start()]
    return rest[:5000]


def get_append_path_body(src: str) -> str:
    """Extract append_path method body from parse.rs."""
    match = re.search(r'fn\s+append_path', src)
    if not match:
        match = re.search(r'append_path\s*\(', src)
    assert match, "append_path not found in parse.rs"
    return src[match.start():match.start() + 3000]


# ---------------------------------------------------------------------------
# Gates (static) — source files exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_files_exist():
    """Required source files (mod.rs, parse.rs) must be present."""
    assert REFS.is_file(), f"Missing {REFS}"
    assert PARSE.is_file(), f"Missing {PARSE}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix: eval option detection in mod.rs
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_eval_option_detection():
    """NodeWorkerConstructor handler detects eval option in second arg
    and exits early before path resolution."""
    src = strip_rust_comments(REFS.read_text())
    handler = get_worker_handler(src)

    # Must reference "eval" key in code (comments already stripped)
    assert '"eval"' in handler, 'Handler does not check for "eval" key'

    # "eval" check must appear BEFORE js_value_to_pattern — this ensures
    # there is an early-exit path that skips path resolution for eval: true
    eval_pos = handler.find('"eval"')
    pattern_pos = handler.find('js_value_to_pattern')
    assert pattern_pos >= 0, "js_value_to_pattern not found in handler"
    assert eval_pos < pattern_pos, (
        '"eval" check must come before js_value_to_pattern for early exit'
    )


# [pr_diff] fail_to_pass
def test_eval_branch_conditional_logic():
    """eval branch has real multi-path conditional logic handling
    true, false, and dynamic values."""
    src = strip_rust_comments(REFS.read_text())
    handler = get_worker_handler(src)

    assert '"eval"' in handler, '"eval" key not found in handler'
    eval_idx = handler.find('"eval"')
    context = handler[max(0, eval_idx - 200):eval_idx + 1500]

    signals = 0

    # Signal 1: Handles true AND false values (via JsConstantValue or booleans)
    if re.search(r'True\b', context) and re.search(r'False\b', context):
        signals += 1
    elif re.search(r'\btrue\b', context) and re.search(r'\bfalse\b', context):
        signals += 1

    # Signal 2: Warning/diagnostic emission for dynamic eval value
    if re.search(r'warn|diagnostic|emit', context, re.IGNORECASE):
        signals += 1

    # Signal 3: Multiple branch paths (match arms or if/else chains)
    if len(re.findall(r'=>\s*\{|\belse\s*\{|\belse\s+if\b', context)) >= 2:
        signals += 1

    # Signal 4: Multiple return/flow-control statements
    if len(re.findall(r'return\b', context)) >= 2:
        signals += 1

    assert signals >= 2, (
        f"eval handling has only {signals}/4 signals for multi-path logic"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix: DataUri/Uri separation in parse.rs
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_datauri_uri_separated_from_dynamic():
    """DataUri/Uri no longer grouped with Dynamic in parse.rs append_path
    match arm."""
    src = strip_rust_comments(PARSE.read_text())

    # Buggy 3-way grouping: DataUri | Uri | Dynamic in one arm
    assert not re.search(
        r'DataUri\s*\{[^}]*\}\s*\|\s*Request::Uri\s*\{[^}]*\}\s*\|\s*Request::Dynamic',
        src,
    ), "DataUri/Uri still grouped with Dynamic (buggy 3-way pattern)"

    assert not re.search(
        r'Dynamic\s*\|\s*Request::(DataUri|Uri)',
        src,
    ), "Dynamic still grouped with DataUri/Uri (reversed pattern)"

    # All three variants must still exist in parse.rs
    assert 'DataUri' in src, "DataUri variant missing"
    assert re.search(r'Request::Uri\b', src), "Uri variant missing"
    assert re.search(r'Request::Dynamic\b', src), "Dynamic variant missing"


# [pr_diff] fail_to_pass
def test_datauri_uri_produce_dynamic_in_append_path():
    """DataUri and Uri individually produce Dynamic when append_path is called
    (separate match arm from Dynamic)."""
    src = strip_rust_comments(PARSE.read_text())
    chunk = get_append_path_body(src)

    # The fix creates: Request::DataUri { .. } | Request::Uri { .. } => { return Dynamic; }
    # On base, the arm was: DataUri | Uri | Dynamic => { return Dynamic; }
    # Key: DataUri|Uri arm ends with => (no | Request::Dynamic before =>)
    has_separate_arm = re.search(
        r'DataUri\s*\{[^}]*\}\s*\|\s*Request::Uri\s*\{[^}]*\}\s*=>',
        chunk,
    )
    assert has_separate_arm, (
        "No separate DataUri|Uri match arm found in append_path "
        "(still grouped with Dynamic?)"
    )

    # That arm must produce Dynamic
    arm_end = chunk[has_separate_arm.end():has_separate_arm.end() + 200]
    assert 'Dynamic' in arm_end, "DataUri|Uri arm doesn't produce Request::Dynamic"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression check
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_worker_path_resolution_preserved():
    """Worker(path) resolution logic preserved — js_value_to_pattern and
    WorkerAssetReference still present in handler."""
    src = strip_rust_comments(REFS.read_text())
    handler = get_worker_handler(src)

    assert 'js_value_to_pattern' in handler, \
        "js_value_to_pattern removed — Worker(path) resolution broken"
    assert 'WorkerAssetReference' in handler, \
        "WorkerAssetReference removed — Worker(path) broken"


# ---------------------------------------------------------------------------
# Anti-stub (static) — handler must have substantial code
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_handler_not_stub():
    """NodeWorkerConstructor handler has substantial logic
    (>=20 code lines, >=2 bindings, >=1 conditional)."""
    src = strip_rust_comments(REFS.read_text())
    handler = get_worker_handler(src)

    code_lines = [
        l.strip() for l in handler.split('\n')
        if l.strip() and l.strip() not in ('{', '}', '(', ')', ',')
    ]
    assert len(code_lines) >= 20, (
        f"Handler has only {len(code_lines)} code lines — likely stubbed"
    )

    bindings = len(re.findall(r'\blet\b', handler))
    assert bindings >= 2, f"Handler has only {bindings} let bindings"

    conditionals = len(re.findall(r'\bif\b|\bmatch\b', handler))
    assert conditionals >= 1, f"Handler has only {conditionals} conditionals"
