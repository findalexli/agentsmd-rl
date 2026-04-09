"""
Task: sglang-hfrunner-hang-fix
Repo: sgl-project/sglang @ 5ef56682b800c3905973c86beeddf1318cedb2a9
PR:   21582

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import multiprocessing as mp
import subprocess
import sys
import textwrap
import time
from pathlib import Path

REPO = "/workspace/sglang"
TARGET = f"{REPO}/python/sglang/test/runners.py"


# ---------------------------------------------------------------------------
# Helpers — extract HFRunner.forward() body for isolated testing
# (Module can't be imported directly: missing torch, sglang.srt, etc.)
# ---------------------------------------------------------------------------

def _extract_forward_body():
    """Parse runners.py, extract HFRunner.forward() body, return as reindented string."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "forward":
                    lines = source.splitlines()
                    body_lines = lines[item.body[0].lineno - 1 : item.end_lineno]
                    indent = len(body_lines[0]) - len(body_lines[0].lstrip())
                    reindented = []
                    for line in body_lines:
                        if line.strip() == "":
                            reindented.append("")
                        else:
                            reindented.append("    " + line[indent:])
                    return "\n".join(reindented)

    raise RuntimeError("HFRunner.forward() not found in source")


def _run_forward_test(script: str, timeout: int = 25) -> subprocess.CompletedProcess:
    """Write script to temp file and run it, returning the CompletedProcess."""
    test_file = Path("/tmp/_pytest_forward_test.py")
    test_file.write_text(script)
    return subprocess.run(
        [sys.executable, str(test_file)],
        timeout=timeout,
        capture_output=True,
        text=True,
    )


MOCK_PREAMBLE = textwrap.dedent("""\
    import multiprocessing as mp
    import queue as queue_mod
    import sys
    import time

    class FakeProcess:
        def __init__(self, exitcode, alive=False):
            self._exitcode = exitcode
            self._alive = alive
        def is_alive(self):
            return self._alive
        @property
        def exitcode(self):
            return self._exitcode
        @property
        def pid(self):
            return 12345 if self._alive else -1
        def terminate(self): pass
        def kill(self): pass
        def join(self, timeout=None): pass

    class FakeSelf:
        def __init__(self, exitcode=None, alive=True):
            self.in_queue = mp.Queue()
            self.out_queue = mp.Queue()
            self.model_proc = FakeProcess(exitcode, alive)
            self.model_type = "generation"
            self.output_str_only = False

    def forward(self, prompts=None, image_data=None, max_new_tokens=8,
                lora_paths=None, token_ids_logprob=None):
    """)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """runners.py must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dead_process_raises_runtime_error():
    """forward() raises RuntimeError with exit code info when subprocess dies."""
    body = _extract_forward_body()
    # Test multiple exit codes to prevent hardcoding
    for exitcode in [1, 42, 137]:
        script = MOCK_PREAMBLE + body + textwrap.dedent(f"""

    obj = FakeSelf(exitcode={exitcode}, alive=False)
    try:
        forward(obj, prompts=["test prompt"])
        print("FAIL: no exception raised")
        sys.exit(1)
    except RuntimeError as e:
        msg = str(e)
        assert "{exitcode}" in msg or "exit" in msg.lower(), \\
            f"RuntimeError should mention exit code {exitcode}: {{e}}"
        print(f"PASS exitcode={exitcode}: {{e}}")
    except Exception as e:
        print(f"FAIL: got {{type(e).__name__}} instead of RuntimeError: {{e}}")
        sys.exit(1)
        """)
        result = _run_forward_test(script)
        assert result.returncode == 0, (
            f"Dead process (exit={exitcode}) test failed:\n{result.stdout}\n{result.stderr}"
        )


# [pr_diff] fail_to_pass
def test_dead_process_negative_exitcode():
    """forward() raises RuntimeError when subprocess killed by signal (negative exitcode)."""
    body = _extract_forward_body()
    # Test multiple signal-killed exit codes
    for exitcode in [-9, -15, -11]:
        script = MOCK_PREAMBLE + body + textwrap.dedent(f"""

    obj = FakeSelf(exitcode={exitcode}, alive=False)
    try:
        forward(obj, prompts=["another prompt"])
        print("FAIL: no exception raised")
        sys.exit(1)
    except RuntimeError as e:
        msg = str(e)
        assert "{exitcode}" in msg or "exit" in msg.lower(), \\
            f"RuntimeError should mention exit code {exitcode}: {{e}}"
        print(f"PASS exitcode={exitcode}: {{e}}")
    except Exception as e:
        print(f"FAIL: got {{type(e).__name__}}: {{e}}")
        sys.exit(1)
        """)
        result = _run_forward_test(script)
        assert result.returncode == 0, (
            f"Dead process (exit={exitcode}) test failed:\n{result.stdout}\n{result.stderr}"
        )


# [pr_diff] fail_to_pass
def test_no_hang_on_dead_process():
    """forward() completes within 15s when subprocess is dead (original bug hangs forever)."""
    body = _extract_forward_body()
    script = MOCK_PREAMBLE + body + textwrap.dedent("""

    obj = FakeSelf(exitcode=1, alive=False)
    start = time.time()
    try:
        forward(obj, prompts=["test"])
    except Exception:
        pass  # We expect an error; timing is what matters
    elapsed = time.time() - start
    if elapsed < 15:
        print(f"PASS: completed in {elapsed:.1f}s")
    else:
        print(f"FAIL: took {elapsed:.1f}s (likely hanging)")
        sys.exit(1)
    """)
    result = _run_forward_test(script, timeout=20)
    assert result.returncode == 0, (
        f"Hang detection test failed (timeout or slow):\n{result.stdout}\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_forward_returns_when_alive():
    """forward() returns queued result when subprocess is healthy (normal operation)."""
    body = _extract_forward_body()
    # Test with varied result payloads to prevent hardcoding
    test_payloads = [
        {"output": "hello world", "logprobs": [1.0, 2.0]},
        {"output": "", "logprobs": []},
        [{"text": "batch1"}, {"text": "batch2"}],
        "simple string result",
    ]
    for payload in test_payloads:
        script = MOCK_PREAMBLE + body + textwrap.dedent(f"""

    obj = FakeSelf(exitcode=None, alive=True)
    expected = {payload!r}
    obj.out_queue.put(expected)

    result = forward(obj, prompts=["test"])
    assert result == expected, f"Got {{result!r}}, expected {{expected!r}}"
    print(f"PASS: {{expected!r}}")
        """)
        result = _run_forward_test(script, timeout=15)
        assert result.returncode == 0, (
            f"Pass-through test failed for {payload!r}:\n{result.stdout}\n{result.stderr}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """runners.py is not gutted: has expected classes, functions, and line count."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    line_count = len(source.splitlines())
    class_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    func_count = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))

    assert line_count > 100, f"File only has {line_count} lines (expected >100)"
    assert class_count >= 2, f"File gutted: only {class_count} classes"
    assert func_count >= 5, f"File gutted: only {func_count} functions"
