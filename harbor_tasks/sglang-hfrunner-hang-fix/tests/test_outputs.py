"""
Task: sglang-hfrunner-hang-fix
Repo: sgl-project/sglang @ 5ef56682b800c3905973c86beeddf1318cedb2a9
PR:   21582

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import multiprocessing as mp
import os
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


MOCK_PREAMBLE = (
    "import multiprocessing as mp\n"
    "import queue as queue_mod\n"
    "import sys\n"
    "import time\n"
    "\n"
    "class FakeProcess:\n"
    "    def __init__(self, exitcode, alive=False):\n"
    "        self._exitcode = exitcode\n"
    "        self._alive = alive\n"
    "    def is_alive(self):\n"
    "        return self._alive\n"
    "    @property\n"
    "    def exitcode(self):\n"
    "        return self._exitcode\n"
    "    @property\n"
    "    def pid(self):\n"
    "        return 12345 if self._alive else -1\n"
    "    def terminate(self): pass\n"
    "    def kill(self): pass\n"
    "    def join(self, timeout=None): pass\n"
    "\n"
    "class MockQueue:\n"
    "    def __init__(self):\n"
    "        self._data = []\n"
    "        self._get_count = 0\n"
    "    def put(self, item):\n"
    "        self._data.append(item)\n"
    "    def get(self, timeout=None):\n"
    "        self._get_count += 1\n"
    "        if self._get_count > 3:\n"
    "            print('FAIL: infinite loop detected')\n"
    "            sys.exit(1)\n"
    "        actual_timeout = 2 if timeout is None else timeout\n"
    "        if not self._data:\n"
    "            import time\n"
    "            time.sleep(actual_timeout)\n"
    "            raise queue_mod.Empty()\n"
    "        return self._data.pop(0)\n"
    "    def empty(self):\n"
    "        return len(self._data) == 0\n"
    "\n"
    "class FakeSelf:\n"
    "    def __init__(self, exitcode=None, alive=True):\n"
    "        self.in_queue = MockQueue()\n"
    "        self.out_queue = MockQueue()\n"
    "        self.model_proc = FakeProcess(exitcode, alive)\n"
    "        self.model_type = 'generation'\n"
    "        self.output_str_only = False\n"
    "\n"
    "def forward(self, prompts=None, image_data=None, max_new_tokens=8,\n"
    "            lora_paths=None, token_ids_logprob=None):\n"
)


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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from repository
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_precommit_basic():
    """Repo pre-commit basic checks pass (symlinks, yaml, toml, ast, merge conflicts, private keys, debug statements)."""
    # Install pre-commit
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Install may fail if already installed, continue anyway

    env = {**os.environ, "SKIP": "no-commit-to-branch,lychee,clang-format,isort,ruff,black,black-jupyter,codespell,nbstripout,check-chinese-characters,sort-ci-permissions"}
    r = subprocess.run(
        [sys.executable, "-m", "pre_commit", "run", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Pre-commit basic checks failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo ruff lint checks pass (F401 unused imports, F821 undefined names) for runners.py."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select=F401,F821", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_compileall():
    """Repo Python files compile without syntax errors."""
    r = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", f"{REPO}/python/sglang/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # compileall returns 0 even with warnings, only fail on actual errors
    # Check stderr for SyntaxError patterns
    if r.stderr and ("SyntaxError" in r.stderr or "IndentationError" in r.stderr):
        assert False, f"Python compileall found syntax errors:\n{r.stderr[-1000:]}"
    assert r.returncode == 0, f"Python compileall failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_codespell():
    """Repo codespell passes on runners.py (no common typos)."""
    # Install codespell to user location
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--user", "codespell", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    # Find codespell in user bin
    user_base = Path.home() / ".local" / "bin"
    codespell_cmd = str(user_base / "codespell") if (user_base / "codespell").exists() else "codespell"

    r = subprocess.run(
        [codespell_cmd, "--config", f"{REPO}/.codespellrc", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Codespell found typos:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_isort():
    """Repo isort check passes on runners.py (imports are sorted)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    r = subprocess.run(
        [sys.executable, "-m", "isort", "--check-only", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed (imports not sorted):\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_pyflakes():
    """Repo pyflakes check passes on runners.py (no undefined names)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyflakes", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    r = subprocess.run(
        [sys.executable, "-m", "pyflakes", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pyflakes found issues:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_yamllint():
    """Repo yamllint check passes on CI workflow files (valid YAML syntax)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "yamllint", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    r = subprocess.run(
        [sys.executable, "-m", "yamllint", "-d", "relaxed", f"{REPO}/.github/workflows/lint.yml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # yamllint returns 0 on success, 1 on errors (warnings are ok)
    # We only care about errors, not warnings like line too long
    if r.returncode != 0 and "error" in r.stdout.lower():
        assert False, f"yamllint found errors:\n{r.stdout}\n{r.stderr}"
    # If only warnings, consider it a pass
    assert r.returncode == 0 or (r.returncode == 0 or "warning" in r.stdout.lower()), f"yamllint failed:\n{r.stdout}\n{r.stderr}"
