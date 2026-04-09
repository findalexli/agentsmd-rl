"""
Task: sglang-scheduler-ready-cleanup
Repo: sgl-project/sglang @ c34593f9512a0be2eb9d252303a7bd12f47f881f
PR:   #21626

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import multiprocessing
import signal
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace"
ENGINE_FILE = Path(REPO) / "python/sglang/srt/entrypoints/engine.py"


def _extract_wait_function():
    """Extract _wait_for_scheduler_ready and nearby helpers from engine.py
    without importing the module (which pulls in torch, numpy, etc.)."""
    source = ENGINE_FILE.read_text()
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)

    func_ranges = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_ranges[node.name] = (node.lineno - 1, node.end_lineno)

    assert "_wait_for_scheduler_ready" in func_ranges, \
        "_wait_for_scheduler_ready not found in engine.py"

    target_names = {"_wait_for_scheduler_ready"}

    # Find functions called inside _wait_for_scheduler_ready
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_wait_for_scheduler_ready":
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and child.id in func_ranges:
                    target_names.add(child.id)

    # Include functions defined immediately before (helpers like _scheduler_died_error)
    wait_start = func_ranges["_wait_for_scheduler_ready"][0]
    for name, (start, end) in func_ranges.items():
        if end >= wait_start - 3 and start < wait_start:
            target_names.add(name)

    chunks = []
    for name in sorted(target_names, key=lambda n: func_ranges[n][0]):
        start, end = func_ranges[name]
        chunks.append("".join(lines[start:end]))

    header = (
        "from __future__ import annotations\n"
        "from typing import List, Dict\n"
        "import multiprocessing\n\n"
    )
    return header + "\n\n".join(chunks)


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess within the repo directory."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# Build subprocess preamble: extracted function source + test helpers
_SUBPROCESS_PREAMBLE = (
    _extract_wait_function()
    + "\nimport signal\nimport sys\n\n"
    + textwrap.dedent("""\
    class FakeProc:
        def __init__(self, alive=True, exitcode=None):
            self._alive = alive
            self.exitcode = exitcode
        def is_alive(self):
            return self._alive
        def join(self, timeout=None):
            pass
    """)
)

# In-process extraction for pass_to_pass tests
_ns = {}
exec(_extract_wait_function(), _ns)
_wait_for_scheduler_ready = _ns["_wait_for_scheduler_ready"]


class FakeProc:
    """Mock multiprocessing.Process for testing."""
    def __init__(self, alive=True, exitcode=None):
        self._alive = alive
        self.exitcode = exitcode

    def is_alive(self):
        return self._alive

    def join(self, timeout=None):
        pass


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass
def test_repo_ruff_check():
    """Ruff lint check on engine.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", str(ENGINE_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_black_check():
    """Black format check on engine.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["black", "--check", str(ENGINE_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black check failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_isort_check():
    """isort import order check on engine.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["isort", "--check", str(ENGINE_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_syntax_check():
    """engine.py must parse without errors."""
    ast.parse(ENGINE_FILE.read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_immediate_nonready_first_rank():
    """Non-ready rank 0 detected immediately, not after polling all ranks.

    Bug: rank 0 sends non-ready, rank 1 never sends -> hangs polling rank 1.
    Fix: rank 0 non-ready detected right after recv -> raises immediately.
    """
    r = _run_py(_SUBPROCESS_PREAMBLE + textwrap.dedent("""\

    def timeout_handler(signum, frame):
        print("HUNG")
        sys.exit(1)

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)

    r0, w0 = multiprocessing.Pipe(duplex=False)
    w0.send({"status": "error", "message": "init failed"})

    r1, w1 = multiprocessing.Pipe(duplex=False)
    # rank 1 never sends — alive but slow

    try:
        _wait_for_scheduler_ready([r0, r1], [FakeProc(), FakeProc()])
        print("NO_ERROR")
        sys.exit(1)
    except RuntimeError as e:
        msg = str(e).lower()
        if "failed" in msg or "error" in msg:
            print("PASS")
        else:
            print(f"WRONG_ERROR: {e}")
            sys.exit(1)
    """), timeout=20)
    assert r.returncode == 0, f"Failed (rc={r.returncode}): stdout={r.stdout} stderr={r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS: {r.stdout}"


# [pr_diff] fail_to_pass
def test_immediate_nonready_middle_rank():
    """Mid-rank non-ready detected before reaching later ranks.

    Bug: rank 0 ready, rank 1 non-ready, rank 2 never sends -> hangs on rank 2.
    Fix: rank 1 non-ready detected right after recv -> raises immediately.
    """
    r = _run_py(_SUBPROCESS_PREAMBLE + textwrap.dedent("""\

    def timeout_handler(signum, frame):
        print("HUNG")
        sys.exit(1)

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)

    r0, w0 = multiprocessing.Pipe(duplex=False)
    w0.send({"status": "ready", "rank": 0})

    r1, w1 = multiprocessing.Pipe(duplex=False)
    w1.send({"status": "error", "message": "rank 1 init failed"})

    r2, w2 = multiprocessing.Pipe(duplex=False)
    # rank 2 never sends

    try:
        _wait_for_scheduler_ready(
            [r0, r1, r2],
            [FakeProc(), FakeProc(), FakeProc()]
        )
        print("NO_ERROR")
        sys.exit(1)
    except RuntimeError as e:
        msg = str(e).lower()
        if "failed" in msg or "error" in msg:
            print("PASS")
        else:
            print(f"WRONG_ERROR: {e}")
            sys.exit(1)
    """), timeout=20)
    assert r.returncode == 0, f"Failed (rc={r.returncode}): stdout={r.stdout} stderr={r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS: {r.stdout}"


# [pr_diff] fail_to_pass
# AST-only because: deduplication is a structural property — can't be tested behaviorally
def test_error_message_deduplicated():
    """Dead-scheduler error message appears at most once in _wait_for_scheduler_ready.

    Bug: multi-line RuntimeError string copy-pasted in EOFError handler and
    process liveness check.
    Fix: extracted into helper function.
    """
    source = ENGINE_FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_wait_for_scheduler_ready":
            func_src = ast.get_source_segment(source, node)
            count = func_src.count("scheduler died during initialization")
            assert count <= 1, (
                f"Error message appears {count} times — still duplicated"
            )
            return
    assert False, "_wait_for_scheduler_ready not found"


# [pr_diff] fail_to_pass
# AST-only because: nesting structure is a code organization property, not runtime behavior
def test_poll_timeout_check_unnested():
    """Dead-process check after poll timeout is NOT nested inside an else clause.

    Bug: the for-loop checking is_alive() is inside 'else:' of 'if poll()'.
    Fix: the check runs at the while-loop body level (after the if/break).
    """
    source = ENGINE_FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_wait_for_scheduler_ready":
            # Look for while loops in the function
            for child in ast.walk(node):
                if isinstance(child, ast.While):
                    # Find if statements inside the while body
                    for stmt in child.body:
                        if isinstance(stmt, ast.If):
                            # The buggy pattern: if poll(): ... else: <dead-check>
                            if stmt.orelse:
                                else_src = ast.get_source_segment(source, stmt)
                                if else_src and "is_alive" in else_src:
                                    assert False, (
                                        "Dead-process check is nested inside "
                                        "else clause of if poll()"
                                    )
            return
    assert False, "_wait_for_scheduler_ready not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression + happy path
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_happy_path_single_rank():
    """Single rank ready returns list with one result."""
    r0, w0 = multiprocessing.Pipe(duplex=False)
    w0.send({"status": "ready", "rank": 0})

    result = _wait_for_scheduler_ready([r0], [FakeProc()])
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["status"] == "ready"
    assert result[0]["rank"] == 0


# [pr_diff] pass_to_pass
def test_happy_path_multi_rank():
    """Multiple ranks all ready returns correct ordered results."""
    pipes = []
    for i in range(3):
        r, w = multiprocessing.Pipe(duplex=False)
        w.send({"status": "ready", "rank": i, "info": f"data_{i}"})
        pipes.append(r)

    procs = [FakeProc() for _ in range(3)]
    result = _wait_for_scheduler_ready(pipes, procs)
    assert isinstance(result, list)
    assert len(result) == 3
    for i in range(3):
        assert result[i]["rank"] == i
        assert result[i]["info"] == f"data_{i}"


# [pr_diff] pass_to_pass
def test_eoferror_descriptive_error():
    """Closed pipe (scheduler died) raises RuntimeError with rank and exit code."""
    r0, w0 = multiprocessing.Pipe(duplex=False)
    w0.close()

    try:
        _wait_for_scheduler_ready([r0], [FakeProc(alive=False, exitcode=-9)])
        assert False, "Expected RuntimeError"
    except RuntimeError as e:
        msg = str(e)
        # Must mention the rank number and exit code in some form
        assert "0" in msg and ("exit" in msg.lower() or "-9" in msg), (
            f"Error not descriptive enough (should mention rank and exit code): {e}"
        )


# [pr_diff] pass_to_pass
def test_dead_process_detected():
    """Dead process during poll timeout raises RuntimeError."""
    class SlowPipe:
        def poll(self, timeout=None):
            return False

    try:
        _wait_for_scheduler_ready(
            [SlowPipe()],
            [FakeProc(alive=False, exitcode=-9)]
        )
        assert False, "Expected RuntimeError"
    except RuntimeError as e:
        msg = str(e).lower()
        assert any(w in msg for w in ("died", "dead", "exit", "killed", "crash")), (
            f"Error doesn't mention process death: {e}"
        )


# ---------------------------------------------------------------------------
# Anti-stub (static, pass_to_pass)
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass
def test_repo_ruff_check():
    """Ruff lint check on engine.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", str(ENGINE_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_black_check():
    """Black format check on engine.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["black", "--check", str(ENGINE_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black check failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_isort_check():
    """isort import order check on engine.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["isort", "--check", str(ENGINE_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_not_stub():
    """_wait_for_scheduler_ready has meaningful implementation, not a stub."""
    source = ENGINE_FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_wait_for_scheduler_ready":
            meaningful = sum(
                1 for child in ast.walk(node)
                if isinstance(child, (ast.For, ast.While, ast.If, ast.Try,
                                       ast.Assign, ast.AugAssign, ast.Return,
                                       ast.Raise, ast.Call))
            )
            assert meaningful >= 5, (
                f"Only {meaningful} meaningful statements — likely a stub"
            )
            return
    assert False, "_wait_for_scheduler_ready not found"
