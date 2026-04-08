"""
Task: sglang-streaming-backlog-warning
Repo: sgl-project/sglang @ 4dd4e06f1d5fd1d294cb82a84b803256760cbfff
PR:   21432

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/repo"
FILE = f"{REPO}/python/sglang/srt/managers/tokenizer_manager.py"


def _get_method_node():
    """Parse the file and return the _wait_one_response AST node."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_wait_one_response":
            return node, source
    raise AssertionError("_wait_one_response method not found in tokenizer_manager.py")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """tokenizer_manager.py must parse without syntax errors."""
    source = Path(FILE).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_no_backlog_warning_at_runtime():
    """Execute the streaming drain path and verify no WARNING log is emitted.

    Extracts if-blocks in _wait_one_response containing logger.warning with
    backlog keywords, executes them with mock objects at multiple pending
    sizes, and asserts no WARNING-level output is produced.
    """
    r = subprocess.run(
        ["python3", "-c", _RUNTIME_SCRIPT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Script failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS:\nstdout: {r.stdout}\nstderr: {r.stderr}"


_RUNTIME_SCRIPT = r'''
import ast, textwrap, logging, io, types, sys

source = open("python/sglang/srt/managers/tokenizer_manager.py").read()
tree = ast.parse(source)
lines = source.splitlines()

method = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_wait_one_response":
        method = node
        break

if method is None:
    print("FAIL: _wait_one_response not found")
    sys.exit(1)

backlog_kw = ["backlog", "queued chunks", "p99 tbt", "inflate"]
warning_blocks = []

for child in ast.walk(method):
    if not isinstance(child, ast.If):
        continue
    for sub in ast.walk(child):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        if not (isinstance(func, ast.Attribute) and func.attr in ("warning", "warn")):
            continue
        for arg in sub.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if any(kw in arg.value.lower() for kw in backlog_kw):
                    warning_blocks.append(child)
                    break

if not warning_blocks:
    print("PASS: no backlog warning blocks found in source")
    sys.exit(0)

for block in warning_blocks:
    code = textwrap.dedent("\n".join(lines[block.lineno - 1 : block.end_lineno]))
    for n in [2, 5, 10]:
        cap = io.StringIO()
        handler = logging.StreamHandler(cap)
        handler.setLevel(logging.WARNING)
        lg = logging.getLogger("backlog_test_%d" % n)
        lg.handlers.clear()
        lg.addHandler(handler)
        lg.setLevel(logging.DEBUG)
        ns = {
            "is_stream": True,
            "pending": [{"t": str(i)} for i in range(n)],
            "logger": lg,
            "obj": types.SimpleNamespace(rid="test-rid-%d" % n),
            "len": len,
        }
        try:
            exec(code, ns)
        except Exception:
            pass
        output = cap.getvalue().strip()
        if output:
            print("FAIL: WARNING emitted with %d pending: %s" % (n, output))
            sys.exit(1)

print("PASS: warning blocks exist but do not emit WARNING-level output")
'''


def test_no_warning_call_in_method():
    """No WARNING-level logger calls about streaming backlog in _wait_one_response.

    Parses the source AST via subprocess and verifies the warning call has been
    removed, not just silenced or reconfigured.
    """
    r = subprocess.run(
        ["python3", "-c", _AST_CHECK_SCRIPT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Script failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS:\nstdout: {r.stdout}\nstderr: {r.stderr}"


_AST_CHECK_SCRIPT = r'''
import ast, sys

source = open("python/sglang/srt/managers/tokenizer_manager.py").read()
tree = ast.parse(source)

method = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_wait_one_response":
        method = node
        break

if method is None:
    print("FAIL: _wait_one_response not found")
    sys.exit(1)

backlog_kw = ["backlog", "queued chunks", "p99 tbt", "inflate"]

for child in ast.walk(method):
    if not isinstance(child, ast.Call):
        continue
    func = child.func
    if not (isinstance(func, ast.Attribute) and func.attr in ("warning", "warn")):
        continue
    for arg in child.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            low = arg.value.lower()
            if any(kw in low for kw in backlog_kw):
                print("FAIL: WARNING-level backlog log at line %d: %r" % (child.lineno, arg.value))
                sys.exit(1)

print("PASS: no backlog warning calls in _wait_one_response")
'''


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_async_generator_preserved():
    """_wait_one_response must remain an async generator with drain loop and event handling."""
    method, _ = _get_method_node()

    assert isinstance(method, ast.AsyncFunctionDef), (
        "_wait_one_response must be an async function"
    )

    yields = sum(1 for n in ast.walk(method) if isinstance(n, ast.Yield))
    assert yields >= 2, f"Expected >=2 yields (async generator), found {yields}"

    for_loops = sum(1 for n in ast.walk(method) if isinstance(n, ast.For))
    assert for_loops >= 1, "Drain loop (for-loop over pending chunks) is missing"

    has_event = any(
        isinstance(n, ast.Attribute) and n.attr in ("wait", "clear")
        for n in ast.walk(method)
    )
    assert has_event, "Event coordination (.wait/.clear) is missing"


def test_method_not_stubbed():
    """_wait_one_response must have a substantial body with real logic."""
    method, _ = _get_method_node()

    line_count = method.end_lineno - method.lineno
    assert line_count >= 25, f"Method is only {line_count} lines (expected >=25)"

    meaningful = sum(
        1
        for n in ast.walk(method)
        if isinstance(
            n,
            (ast.Assign, ast.AugAssign, ast.If, ast.For, ast.While,
             ast.Try, ast.Yield, ast.Delete, ast.Raise),
        )
    )
    assert meaningful >= 15, f"Only {meaningful} meaningful statements (expected >=15)"

    has_try = any(isinstance(n, ast.Try) for n in ast.walk(method))
    assert has_try, "Error handling (try/except) is missing"

    has_finished = any(
        (isinstance(n, ast.Name) and n.id == "finished")
        or (isinstance(n, ast.Attribute) and n.attr == "finished")
        for n in ast.walk(method)
    )
    assert has_finished, "Completion detection ('finished' reference) is missing"
