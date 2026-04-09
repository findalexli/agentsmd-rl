"""
Task: vllm-abort-test-race-condition
Repo: vllm-project/vllm @ 171775f306a333a9cf105bfd533bf3e113d401d9
PR:   38414

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

REPO = "/repo"
FILE = f"{REPO}/tests/v1/engine/test_abort_final_step.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_test_func_node():
    """Parse file and return the AST node for test_abort_during_final_step."""
    # AST-only because: file imports vllm engine internals requiring GPU/CUDA
    source = Path(FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "test_abort_during_final_step":
            return node, source
    raise AssertionError("test_abort_during_final_step function not found")


def _get_test_func_source():
    """Return the source text of test_abort_during_final_step."""
    source = Path(FILE).read_text()
    lines = source.splitlines()
    node, _ = _get_test_func_node()
    return "\n".join(lines[node.lineno - 1 : node.end_lineno])


def _find_while_loops_in_func(func_node):
    """Find all While loop nodes anywhere inside the function (including nested)."""
    loops = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.While):
            loops.append(node)
    return loops


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    source = Path(FILE).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_no_standalone_fixed_sleep():
    """The buggy asyncio.sleep(0.1) must not remain as the sole wait mechanism.

    Base commit has `await asyncio.sleep(0.1)` outside any loop right after
    `await gen_task`. The fix replaces it with a polling loop.
    """
    # AST-only because: file imports vllm engine internals requiring GPU/CUDA
    func_node, source = _get_test_func_node()

    # Collect line ranges of all loops in the function
    loop_ranges = set()
    for node in ast.walk(func_node):
        if isinstance(node, (ast.While, ast.For, ast.AsyncFor)):
            loop_ranges.add((node.lineno, node.end_lineno))

    # Find any asyncio.sleep(0.1) call outside a loop
    for node in ast.walk(func_node):
        if not isinstance(node, ast.Expr):
            continue
        expr = node.value
        # Handle both `await asyncio.sleep(0.1)` and `asyncio.sleep(0.1)`
        call = None
        if isinstance(expr, ast.Await) and isinstance(expr.value, ast.Call):
            call = expr.value
        elif isinstance(expr, ast.Call):
            call = expr

        if call is None:
            continue

        # Check if it's asyncio.sleep with arg 0.1
        func = call.func
        is_sleep = False
        if isinstance(func, ast.Attribute) and func.attr == "sleep":
            if len(call.args) == 1 and isinstance(call.args[0], ast.Constant):
                if call.args[0].value == 0.1:
                    is_sleep = True

        if is_sleep:
            in_loop = any(start <= node.lineno <= end for start, end in loop_ranges)
            assert in_loop, (
                f"Buggy asyncio.sleep(0.1) at line {node.lineno} is outside any loop — "
                "this is the fixed-sleep pattern that causes the race condition"
            )


# [pr_diff] fail_to_pass
def test_polling_loop_with_file_read():
    """A while loop that reads the status file must exist after gen_task.

    Base commit has no polling loop — just a linear sleep then a one-shot
    file read. The fix adds a while loop that repeatedly opens and reads
    the status file, checking for FINISHED_ entries.
    """
    # AST-only because: file imports vllm engine internals requiring GPU/CUDA
    func_node, source = _get_test_func_node()

    # Look for a while loop that contains both:
    # 1. open() call (reading the file)
    # 2. Reference to "FINISHED_" or startswith("FINISHED_")
    while_loops = _find_while_loops_in_func(func_node)

    for loop in while_loops:
        seg = ast.get_source_segment(source, loop) or ""
        has_open = "open(" in seg
        has_finished = "FINISHED_" in seg
        has_status = "status" in seg.lower()
        if has_open and (has_finished or has_status):
            return  # Found the polling loop

    # Also check for helper functions called from the test
    called_names = set()
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            called_names.add(node.func.id)

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in called_names:
                for child in ast.walk(node):
                    if isinstance(child, ast.While):
                        seg = ast.get_source_segment(source, child) or ""
                        if "open(" in seg and ("FINISHED_" in seg or "status" in seg.lower()):
                            return

    raise AssertionError(
        "No polling loop (while loop reading status file) found — "
        "the status file must be read inside a loop, not as a one-shot read"
    )


# [pr_diff] fail_to_pass
def test_timeout_mechanism_exists():
    """The status-file polling loop must have a timeout to avoid hanging forever.

    Base commit has a TimeoutError for the execute_model wait, but NO timeout
    on the status file read. The fix adds a time-bounded while loop for polling
    the status file, with TimeoutError or similar on expiry.
    """
    # AST-only because: file imports vllm engine internals requiring GPU/CUDA
    func_node, source = _get_test_func_node()

    # Find while loops that reference status file / FINISHED_
    while_loops = _find_while_loops_in_func(func_node)
    for loop in while_loops:
        seg = ast.get_source_segment(source, loop) or ""
        if ("FINISHED_" in seg or "open(" in seg) and "status" in seg.lower():
            # This is the status-polling loop — check it has timeout
            has_time_condition = bool(re.search(r"time\.time\(\)", seg))
            has_timeout_error = "TimeoutError" in seg
            has_wait_for = "wait_for" in seg and "timeout" in seg.lower()
            assert has_time_condition or has_timeout_error or has_wait_for, (
                "Status file polling loop has no timeout — "
                "it will hang forever when status never appears"
            )
            return

    raise AssertionError(
        "No status-file polling loop found — cannot verify timeout mechanism"
    )


# ---------------------------------------------------------------------------
# Behavioral test: verify polling concept actually works
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_polling_captures_delayed_status():
    """Polling loop captures FINISHED_ABORTED written after a 300ms delay.

    This is a behavioral test: we write a small async script that simulates
    the polling pattern from the fix and verify it catches a delayed write.
    The base commit's approach (single sleep(0.1) + one-shot read) would miss it.

    We extract the while-loop code from the test function and execute it.
    """
    func_node, source = _get_test_func_node()
    all_lines = source.splitlines()

    # Find while loops in the function that reference status/FINISHED
    while_loops = _find_while_loops_in_func(func_node)
    polling_loop = None
    for loop in while_loops:
        seg = ast.get_source_segment(source, loop) or ""
        if ("FINISHED_" in seg or "status" in seg.lower()) and "open(" in seg:
            polling_loop = loop
            break

    if polling_loop is None:
        raise AssertionError("No polling loop found to test behaviorally")

    # Extract the polling loop source
    loop_lines = all_lines[polling_loop.lineno - 1 : polling_loop.end_lineno]
    # Dedent
    indents = [len(l) - len(l.lstrip()) for l in loop_lines if l.strip()]
    min_indent = min(indents) if indents else 0
    loop_code = "\n".join(l[min_indent:] for l in loop_lines)

    # Determine if it's async (contains await)
    is_async = "await " in loop_code

    # Create temp status file with initial content
    sf = tempfile.mktemp(suffix=".txt")
    with open(sf, "w") as f:
        f.write("INIT:WORKER\nINIT:SCHEDULER\n")

    # Build harness that:
    # 1. Starts a thread to write FINISHED_ABORTED after 300ms delay
    # 2. Runs the extracted polling loop
    # 3. Checks if captured_statuses contains FINISHED_ABORTED
    indent_loop = textwrap.indent(loop_code, "    ")

    if is_async:
        harness = f'''import asyncio, time, threading, sys

def delayed_write():
    time.sleep(0.3)
    with open("{sf}", "a") as f:
        f.write("FINISHED_ABORTED\\n")

threading.Thread(target=delayed_write, daemon=True).start()

async def _run():
    status_file = "{sf}"
    f4 = None  # may be used as context var name
    timeout = 2.0
    start = time.time()
    captured_statuses = []
    status_lines = []
{indent_loop}
    return captured_statuses

result = asyncio.run(_run())
sys.exit(0 if any("FINISHED_ABORTED" in s for s in result) else 1)
'''
    else:
        harness = f'''import time, threading, sys

def delayed_write():
    time.sleep(0.3)
    with open("{sf}", "a") as f:
        f.write("FINISHED_ABORTED\\n")

threading.Thread(target=delayed_write, daemon=True).start()

status_file = "{sf}"
timeout = 2.0
start = time.time()
captured_statuses = []
status_lines = []

{loop_code}

sys.exit(0 if any("FINISHED_ABORTED" in s for s in captured_statuses) else 1)
'''

    harness_file = tempfile.mktemp(suffix=".py")
    Path(harness_file).write_text(harness)

    try:
        result = subprocess.run(
            [sys.executable, harness_file],
            timeout=15,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"Polling did not capture delayed FINISHED_ABORTED.\n"
            f"stdout: {result.stdout[:300]}\n"
            f"stderr: {result.stderr[:500]}"
        )
    finally:
        for p in (harness_file, sf):
            try:
                Path(p).unlink()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_finished_aborted_assertion_preserved():
    """The assertion checking for FINISHED_ABORTED must still exist."""
    # AST-only because: file imports vllm engine internals requiring GPU/CUDA
    func_node, source = _get_test_func_node()

    for node in ast.walk(func_node):
        if isinstance(node, ast.Assert):
            seg = ast.get_source_segment(source, node) or ""
            if "FINISHED_ABORTED" in seg:
                return
    raise AssertionError(
        "No assertion references FINISHED_ABORTED — "
        "the test must still verify the KV connector sees FINISHED_ABORTED"
    )


# [pr_diff] pass_to_pass
def test_function_signature_preserved():
    """Test function and async_scheduling parametrize must still exist."""
    # AST-only because: file imports vllm engine internals requiring GPU/CUDA
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    found_func = False
    found_param = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "test_abort_during_final_step":
            found_func = True
            for dec in node.decorator_list:
                seg = ast.get_source_segment(source, dec) or ""
                if "parametrize" in seg and "async_scheduling" in seg:
                    found_param = True
            # Also check function args
            for arg in node.args.args:
                if arg.arg == "async_scheduling":
                    found_param = True

    assert found_func, "test_abort_during_final_step function not found"
    assert found_param, "async_scheduling parametrize not found"


# [pr_diff] fail_to_pass
def test_timeout_completes():
    """When status never appears, polling must complete (not hang forever).

    We extract the polling loop, run it against a file that never gets
    FINISHED_ written, and verify the script exits within a reasonable time.
    """
    func_node, source = _get_test_func_node()
    all_lines = source.splitlines()

    while_loops = _find_while_loops_in_func(func_node)
    polling_loop = None
    for loop in while_loops:
        seg = ast.get_source_segment(source, loop) or ""
        if ("FINISHED_" in seg or "status" in seg.lower()) and "open(" in seg:
            polling_loop = loop
            break

    if polling_loop is None:
        # If no polling loop found, the structural test will catch it
        raise AssertionError("No polling loop to test timeout behavior")

    loop_lines = all_lines[polling_loop.lineno - 1 : polling_loop.end_lineno]
    indents = [len(l) - len(l.lstrip()) for l in loop_lines if l.strip()]
    min_indent = min(indents) if indents else 0
    loop_code = "\n".join(l[min_indent:] for l in loop_lines)

    is_async = "await " in loop_code

    sf = tempfile.mktemp(suffix=".txt")
    with open(sf, "w") as f:
        f.write("INIT:WORKER\nINIT:SCHEDULER\n")

    indent_loop = textwrap.indent(loop_code, "    ")

    if is_async:
        harness = f'''import asyncio, time, sys

async def _run():
    status_file = "{sf}"
    timeout = 1.0
    start = time.time()
    captured_statuses = []
    status_lines = []
{indent_loop}
    return captured_statuses

try:
    result = asyncio.run(_run())
    sys.exit(0)
except (TimeoutError, asyncio.TimeoutError):
    sys.exit(0)
'''
    else:
        harness = f'''import time, sys

status_file = "{sf}"
timeout = 1.0
start = time.time()
captured_statuses = []
status_lines = []

try:
{textwrap.indent(loop_code, "    ")}
except TimeoutError:
    pass
sys.exit(0)
'''

    harness_file = tempfile.mktemp(suffix=".py")
    Path(harness_file).write_text(harness)

    try:
        result = subprocess.run(
            [sys.executable, harness_file],
            timeout=10,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"Timeout test failed (exit {result.returncode}).\n"
            f"stderr: {result.stderr[:500]}"
        )
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "Polling hangs forever — no timeout mechanism. "
            "The polling loop must exit after a bounded time."
        )
    finally:
        for p in (harness_file, sf):
            try:
                Path(p).unlink()
            except OSError:
                pass


# [static] pass_to_pass
def test_not_stub():
    """File must have substantial content (not trivially emptied)."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    line_count = len(source.splitlines())
    func_count = sum(
        1
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    )

    assert line_count > 200, f"File only has {line_count} lines — likely a stub"
    assert func_count > 5, f"File only has {func_count} functions — likely a stub"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and fix
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linter check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typos():
    """Repo's typos check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "typos", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["typos", FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Typos check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
