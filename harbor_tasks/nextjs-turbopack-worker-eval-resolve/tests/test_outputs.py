"""
Task: nextjs-turbopack-worker-eval-resolve
Repo: vercel/next.js @ e9df6ed9dc381cf99e54c91d984799ca51e2940f

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: All checks are structural because turbopack requires ~200+ crates +
nightly Rust to compile. We verify source code patterns instead.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
REFS = Path(f"{REPO}/turbopack/crates/turbopack-ecmascript/src/references/mod.rs")
PARSE = Path(f"{REPO}/turbopack/crates/turbopack-core/src/resolve/parse.rs")


def strip_rust_comments(src: str) -> str:
    """Remove // line comments and /* */ block comments, preserving string literals."""
    result = []
    i = 0
    in_string = False
    string_char = None
    while i < len(src):
        if not in_string and src[i] == '"' and (i == 0 or src[i - 1] != '\\'):
            in_string = True
            string_char = '"'
            result.append(src[i])
            i += 1
            continue
        if in_string and src[i] == string_char and (i == 0 or src[i - 1] != '\\'):
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
    """Extract the NodeWorkerConstructor handler chunk from stripped source."""
    idx = src.find('NodeWorkerConstructor')
    assert idx >= 0, "NodeWorkerConstructor not found in mod.rs"
    rest = src[idx:]
    next_arm = re.search(
        r'WellKnownFunctionKind::\w+(?!.*NodeWorkerConstructor)', rest[50:]
    )
    if next_arm:
        return rest[:50 + next_arm.start()]
    return rest[:5000]


# ---------------------------------------------------------------------------
# Gates (static) — source files exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_files_exist():
    """Required source files must be present."""
    assert REFS.is_file(), f"Missing {REFS}"
    assert PARSE.is_file(), f"Missing {PARSE}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix: eval option detection in mod.rs
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_eval_option_detection():
    """NodeWorkerConstructor handler detects eval option and exits early
    before path resolution."""
    src = strip_rust_comments(REFS.read_text())
    chunk = get_worker_handler(src)

    # Must inspect second argument (args.get(1), args[1], destructuring, etc.)
    assert re.search(
        r'args\s*[\.\[].*1|second_arg|options_arg|\[_\s*,\s*\w+', chunk
    ), "Handler does not inspect the second Worker constructor argument"

    # Must reference "eval" key in code (comments already stripped)
    eval_refs = [m.start() for m in re.finditer(r'"eval"', chunk)]
    assert eval_refs, 'No reference to "eval" key in handler code'

    # "eval" reference must be inside a conditional structure
    eval_pos = eval_refs[0]
    before_eval = chunk[max(0, eval_pos - 300):eval_pos]
    after_eval = chunk[eval_pos:eval_pos + 500]
    assert re.search(
        r'\bif\b|\bmatch\b|\blet\b.*=.*\?|=>', before_eval + after_eval[:100]
    ), "eval check is not inside a conditional structure"

    # Must have early exit/branch BEFORE js_value_to_pattern
    exit_match = re.search(
        r'return\s+Ok\s*\(|return\s*;|continue\s*;|break\s*;', after_eval
    )
    pattern_match = re.search(r'js_value_to_pattern', after_eval)
    if pattern_match:
        if exit_match and exit_match.start() < pattern_match.start():
            return  # Good: exit before path resolution
        before_pattern = chunk[
            eval_pos:eval_pos + chunk[eval_pos:].find('js_value_to_pattern')
        ]
        assert re.search(
            r'\bif\b|\belse\b|\bmatch\b', before_pattern
        ), "No exit/branch path to skip js_value_to_pattern when eval is true"


# [pr_diff] fail_to_pass
def test_eval_branch_conditional_logic():
    """eval branch has real multi-path conditional logic handling
    true, false, and dynamic eval values."""
    src = strip_rust_comments(REFS.read_text())
    chunk = get_worker_handler(src)

    eval_idx = chunk.find('"eval"')
    assert eval_idx >= 0, "eval key not found in handler"

    context = chunk[max(0, eval_idx - 500):eval_idx + 1500]

    signals = 0
    # Signal 1: References to true/false values (static determination)
    if re.search(r'\btrue\b', context) and re.search(r'\bfalse\b', context):
        signals += 1
    elif re.search(r'JsValue::(Constant|Bool|Literal)', context):
        signals += 1
    # Signal 2: Warning or diagnostic emission
    if re.search(r'warn|diagnostic|report|issue|emit', context, re.IGNORECASE):
        signals += 1
    # Signal 3: Branch structure (if/else, match arms with =>)
    if len(re.findall(r'=>\s*\{|\belse\s*\{|\belse\s+if\b', context)) >= 2:
        signals += 1
    # Signal 4: Multiple return/flow-control paths
    if len(re.findall(r'return\s|continue\s*;|break\s*;', context)) >= 2:
        signals += 1

    assert signals >= 2, (
        f"eval handling has only {signals}/2 required signals "
        f"for real conditional logic"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix: DataUri/Uri separation in parse.rs
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_datauri_uri_separated_from_dynamic():
    """DataUri/Uri no longer grouped with Dynamic in parse.rs append_path."""
    src = strip_rust_comments(PARSE.read_text())

    # The BUGGY 3-way grouping must not exist
    assert not re.search(
        r'DataUri\s*\{[^}]*\}\s*\|\s*Request::Uri\s*\{[^}]*\}\s*\|\s*Request::Dynamic',
        src,
    ), "DataUri/Uri still grouped with Dynamic (buggy pattern present)"

    assert not re.search(
        r'Dynamic\s*\|\s*Request::(DataUri|Uri)', src
    ), "Dynamic still grouped with DataUri/Uri (reversed buggy pattern)"

    # All three variants must still exist
    assert 'DataUri' in src, "DataUri variant missing from parse.rs"
    assert re.search(r'Request::Uri\b', src), "Uri variant missing from parse.rs"
    assert re.search(r'Request::Dynamic\b', src), "Dynamic variant missing"


# [pr_diff] fail_to_pass
def test_datauri_uri_produce_dynamic_in_append_path():
    """DataUri and Uri individually produce Dynamic in append_path."""
    src = strip_rust_comments(PARSE.read_text())

    ap_idx = src.find('fn append_path')
    if ap_idx < 0:
        ap_idx = src.find('append_path')
    assert ap_idx >= 0, "append_path not found in parse.rs"

    chunk = src[ap_idx:ap_idx + 3000]

    # DataUri must be handled in append_path and produce Dynamic
    assert 'DataUri' in chunk, "DataUri not handled in append_path"
    datauri_idx = chunk.find('DataUri')
    nearby = chunk[datauri_idx:datauri_idx + 300]
    assert 'Dynamic' in nearby, "DataUri arm doesn't produce Dynamic"

    # Must not still be in the buggy 3-way grouping
    assert not re.search(
        r'DataUri[^|]*\|\s*[^|]*Uri[^|]*\|\s*[^|]*Dynamic', chunk
    ), "DataUri/Uri still grouped with Dynamic in append_path"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression check
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_worker_path_resolution_preserved():
    """Worker(path) resolution logic preserved — js_value_to_pattern and
    WorkerAssetReference still present in handler."""
    src = strip_rust_comments(REFS.read_text())
    chunk = get_worker_handler(src)

    assert 'js_value_to_pattern' in chunk, \
        "js_value_to_pattern removed — Worker(path) resolution broken"
    assert 'WorkerAssetReference' in chunk, \
        "WorkerAssetReference removed — Worker(path) broken"


# ---------------------------------------------------------------------------
# Anti-stub (static) — handler must have substantial new code
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_handler_not_stub():
    """NodeWorkerConstructor handler has substantial logic, not a minimal stub."""
    src = strip_rust_comments(REFS.read_text())
    chunk = get_worker_handler(src)

    code_lines = [
        l.strip() for l in chunk.split('\n')
        if l.strip() and l.strip() not in ('{', '}', '(', ')', ',')
    ]
    assert len(code_lines) >= 30, (
        f"Handler has only {len(code_lines)} code lines — "
        f"likely stubbed or incomplete"
    )

    bindings = len(re.findall(r'\blet\b', chunk))
    conditionals = len(re.findall(r'\bif\b|\bmatch\b', chunk))
    assert bindings >= 3, f"Handler has only {bindings} bindings — too simple"
    assert conditionals >= 2, (
        f"Handler has only {conditionals} conditionals — too simple"
    )
