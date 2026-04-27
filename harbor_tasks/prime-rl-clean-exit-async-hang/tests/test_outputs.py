"""
Task: prime-rl-clean-exit-async-hang
Repo: PrimeIntellect-ai/prime-rl @ 27c35b1ce136c85c120b0486128316ae022b53a5
PR:   2092

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import asyncio
import functools
import os
import subprocess
import sys
import types
from pathlib import Path
from typing import Any, Callable

REPO = "/workspace/prime-rl"
UTILS_PY = Path(REPO) / "src/prime_rl/utils/utils.py"


# ---------------------------------------------------------------------------
# Subprocess helper for behavioral f2p tests
# ---------------------------------------------------------------------------

SETUP_SCRIPT = '''\
import sys, types, asyncio, functools
from pathlib import Path
from typing import Any, Callable

# Mock wandb
wandb_mock = types.ModuleType("wandb")
wandb_mock.finish = lambda exit_code=None: None
sys.modules["wandb"] = wandb_mock

# Mock torch.distributed
dist_mock = types.ModuleType("torch.distributed")
dist_mock.is_initialized = lambda: False
dist_mock.destroy_process_group = lambda: None
sys.modules.setdefault("torch", types.ModuleType("torch"))
sys.modules["torch.distributed"] = dist_mock

# Load clean_exit from source
src = Path("src/prime_rl/utils/utils.py").read_text()
lines = src.split("\\n")
start = end = None
for i, line in enumerate(lines):
    if line.startswith("def clean_exit("):
        start = i
    elif start is not None and i > start and line and not line[0].isspace() and line[0] != "#":
        end = i
        break
if end is None:
    end = len(lines)

ns = {"asyncio": asyncio, "functools": functools, "wandb": wandb_mock, "dist": dist_mock,
      "sys": sys, "Callable": Callable, "Any": Any,
      "get_logger": lambda: types.SimpleNamespace(opt=lambda **kw: types.SimpleNamespace(error=lambda msg: None))}
exec("\\n".join(lines[start:end]), ns)
clean_exit = ns["clean_exit"]
'''


def _run_subprocess(test_body: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute test code against clean_exit in an isolated subprocess."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(SETUP_SCRIPT + "\n" + test_body)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# In-process helper for p2p tests needing mock callbacks
# ---------------------------------------------------------------------------

def _extract_clean_exit(*, wandb_finish=None, dist_initialized=False, dist_destroy=None):
    """Extract and exec the clean_exit decorator with mocked dependencies."""
    src = UTILS_PY.read_text()

    lines = src.split("\n")
    start = end = None
    for i, line in enumerate(lines):
        if line.startswith("def clean_exit("):
            start = i
        elif start is not None and i > start and line and not line[0].isspace() and line[0] != "#":
            end = i
            break
    if end is None:
        end = len(lines)

    wandb_mock = types.ModuleType("wandb")
    wandb_mock.finish = wandb_finish or (lambda exit_code=None: None)
    sys.modules["wandb"] = wandb_mock

    dist_mock = types.ModuleType("torch.distributed")
    dist_mock.is_initialized = lambda: dist_initialized
    dist_mock.destroy_process_group = dist_destroy or (lambda: None)
    sys.modules.setdefault("torch", types.ModuleType("torch"))
    sys.modules["torch.distributed"] = dist_mock

    ns = {
        "asyncio": asyncio,
        "functools": functools,
        "wandb": wandb_mock,
        "dist": dist_mock,
        "sys": sys,
        "Callable": Callable,
        "Any": Any,
        "get_logger": lambda: types.SimpleNamespace(
            opt=lambda **kw: types.SimpleNamespace(error=lambda msg: None)
        ),
    }
    exec("\n".join(lines[start:end]), ns)
    return ns["clean_exit"], wandb_mock, dist_mock


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """utils.py must parse without syntax errors."""
    src = UTILS_PY.read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — subprocess behavioral tests
#
# These tests verify OBSERVABLE OUTCOMES, not implementation:
#   1. The process actually terminates with exit code 1 (doesn't hang)
#   2. Cleanup (destroy_process_group) is called in the finally block
#   3. wandb.finish is called with exit_code=1
#
# We do NOT assert on the specific exception mechanism (SystemExit vs os._exit).
# Any implementation that achieves termination + cleanup + wandb.finish passes.
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_async_exit():
    """Async clean_exit must terminate the process (not hang) when an exception occurs."""
    r = _run_subprocess("""\
@clean_exit
async def failing_async():
    raise ValueError("dataset is not set")

try:
    asyncio.run(failing_async())
    print("NO_EXCEPTION")
    sys.exit(2)  # Should not reach here
except SystemExit as e:
    # Either sys.exit was used OR the script was killed — both mean process terminated
    print(f"EXIT_CODE:{e.code}")
    sys.exit(0)  # Signal test passed cleanly
except Exception as e:
    # Some other exception propagated — process didn't terminate properly
    print(f"UNHANDLED_EXCEPTION:{type(e).__name__}")
    sys.exit(3)
""")
    # The script itself exits with 0 only if SystemExit was caught (clean termination)
    # Check that stdout contains the termination signal
    assert "EXIT_CODE:1" in r.stdout, (
        f"Async exit did not terminate via exception with code 1. "
        f"stdout: {r.stdout.strip()}, stderr: {r.stderr.strip()}, rc: {r.returncode}"
    )


# [pr_diff] fail_to_pass
def test_sync_exit():
    """Sync clean_exit must terminate the process (not hang) when an exception occurs."""
    r = _run_subprocess("""\
@clean_exit
def failing_sync():
    raise RuntimeError("config missing")

try:
    failing_sync()
    print("NO_EXCEPTION")
    sys.exit(2)  # Should not reach here
except SystemExit as e:
    print(f"EXIT_CODE:{e.code}")
    sys.exit(0)
except Exception as e:
    print(f"UNHANDLED_EXCEPTION:{type(e).__name__}")
    sys.exit(3)
""")
    assert "EXIT_CODE:1" in r.stdout, (
        f"Sync exit did not terminate via exception with code 1. "
        f"stdout: {r.stdout.strip()}, stderr: {r.stderr.strip()}, rc: {r.returncode}"
    )


# [pr_diff] fail_to_pass
def test_async_exit_different_exception():
    """Async clean_exit terminates with exit code 1 for various exception types."""
    r = _run_subprocess("""\
results = []
for exc_type, msg in [(TypeError, "bad type"), (KeyError, "missing key"), (OSError, "io fail")]:
    @clean_exit
    async def failing_async(et=exc_type, m=msg):
        raise et(m)

    try:
        asyncio.run(failing_async())
        results.append(f"NO_EXCEPTION:{exc_type.__name__}")
    except SystemExit as e:
        results.append(f"EXIT:{exc_type.__name__}:{e.code}")
    except Exception as orig:
        results.append(f"UNHANDLED:{exc_type.__name__}:{type(orig).__name__}")

print("\\n".join(results))
sys.exit(0)  # normal termination of test script
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    for line in r.stdout.strip().split("\n"):
        if line.startswith("EXIT:"):
            code = line.split(":")[-1]
            assert code == "1", f"Expected exit code 1, got {code} in line: {line}"
        else:
            assert False, f"Expected EXIT with code 1, got: {line}"


# [pr_diff] fail_to_pass
def test_sync_exit_different_exception():
    """Sync clean_exit terminates with exit code 1 for various exception types."""
    r = _run_subprocess("""\
results = []
for exc_type, msg in [(TypeError, "bad type"), (KeyError, "missing key"), (OSError, "io fail")]:
    @clean_exit
    def failing_sync(et=exc_type, m=msg):
        raise et(m)

    try:
        failing_sync()
        results.append(f"NO_EXCEPTION:{exc_type.__name__}")
    except SystemExit as e:
        results.append(f"EXIT:{exc_type.__name__}:{e.code}")
    except Exception as orig:
        results.append(f"UNHANDLED:{exc_type.__name__}:{type(orig).__name__}")

print("\\n".join(results))
sys.exit(0)
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    for line in r.stdout.strip().split("\n"):
        if line.startswith("EXIT:"):
            code = line.split(":")[-1]
            assert code == "1", f"Expected exit code 1, got {code} in line: {line}"
        else:
            assert False, f"Expected EXIT with code 1, got: {line}"


# ---------------------------------------------------------------------------
# Additional behavioral test: verify cleanup runs even on exception path
# This is the key behavior that would break with os._exit (finally doesn't run)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_async_cleanup_runs():
    """Async clean_exit must call destroy_process_group in finally block on error."""
    r = _run_subprocess("""\
import sys, types, asyncio
from pathlib import Path

wandb_mock = types.ModuleType("wandb")
wandb_mock.finish = lambda exit_code=None: None
sys.modules["wandb"] = wandb_mock

dist_mock = types.ModuleType("torch.distributed")
cleanup_calls = []
dist_mock.is_initialized = lambda: True
dist_mock.destroy_process_group = lambda: cleanup_calls.append(True)
sys.modules.setdefault("torch", types.ModuleType("torch"))
sys.modules["torch.distributed"] = dist_mock

src = Path("src/prime_rl/utils/utils.py").read_text()
lines = src.split("\\n")
start = end = None
for i, line in enumerate(lines):
    if line.startswith("def clean_exit("):
        start = i
    elif start is not None and i > start and line and not line[0].isspace() and line[0] != "#":
        end = i
        break
if end is None:
    end = len(lines)

ns = {"asyncio": asyncio, "functools": functools, "wandb": wandb_mock, "dist": dist_mock,
      "sys": sys, "Callable": Callable, "Any": Any,
      "get_logger": lambda: types.SimpleNamespace(opt=lambda **kw: types.SimpleNamespace(error=lambda msg: None))}
exec("\\n".join(lines[start:end]), ns)
clean_exit = ns["clean_exit"]

@clean_exit
async def failing_async():
    raise ValueError("boom")

try:
    asyncio.run(failing_async())
except SystemExit:
    pass
except Exception:
    pass

if cleanup_calls:
    print("CLEANUP_DONE")
else:
    print("CLEANUP_MISSING")
    sys.exit(1)
""")
    assert "CLEANUP_DONE" in r.stdout, (
        f"Async cleanup (destroy_process_group) was not called. "
        f"stdout: {r.stdout.strip()}, stderr: {r.stderr.strip()}"
    )


# [pr_diff] fail_to_pass
def test_sync_cleanup_runs():
    """Sync clean_exit must call destroy_process_group in finally block on error."""
    r = _run_subprocess("""\
import sys, types
from pathlib import Path

wandb_mock = types.ModuleType("wandb")
wandb_mock.finish = lambda exit_code=None: None
sys.modules["wandb"] = wandb_mock

dist_mock = types.ModuleType("torch.distributed")
cleanup_calls = []
dist_mock.is_initialized = lambda: True
dist_mock.destroy_process_group = lambda: cleanup_calls.append(True)
sys.modules.setdefault("torch", types.ModuleType("torch"))
sys.modules["torch.distributed"] = dist_mock

src = Path("src/prime_rl/utils/utils.py").read_text()
lines = src.split("\\n")
start = end = None
for i, line in enumerate(lines):
    if line.startswith("def clean_exit("):
        start = i
    elif start is not None and i > start and line and not line[0].isspace() and line[0] != "#":
        end = i
        break
if end is None:
    end = len(lines)

ns = {"asyncio": asyncio, "functools": functools, "wandb": wandb_mock, "dist": dist_mock,
      "sys": sys, "Callable": Callable, "Any": Any,
      "get_logger": lambda: types.SimpleNamespace(opt=lambda **kw: types.SimpleNamespace(error=lambda msg: None))}
exec("\\n".join(lines[start:end]), ns)
clean_exit = ns["clean_exit"]

@clean_exit
def failing_sync():
    raise RuntimeError("boom")

try:
    failing_sync()
except SystemExit:
    pass
except Exception:
    pass

if cleanup_calls:
    print("CLEANUP_DONE")
else:
    print("CLEANUP_MISSING")
    sys.exit(1)
""")
    assert "CLEANUP_DONE" in r.stdout, (
        f"Sync cleanup (destroy_process_group) was not called. "
        f"stdout: {r.stdout.strip()}, stderr: {r.stderr.strip()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — in-process with mock callbacks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_finally_cleanup():
    """The finally block must still execute, destroying the process group on error."""
    cleanup_called = []
    finish_calls = []
    clean_exit, _, _ = _extract_clean_exit(
        dist_initialized=True,
        dist_destroy=lambda: cleanup_called.append(True),
        wandb_finish=lambda exit_code=None: finish_calls.append(exit_code),
    )

    @clean_exit
    async def failing_async():
        raise ValueError("boom")

    try:
        asyncio.run(failing_async())
    except (SystemExit, Exception):
        pass

    assert cleanup_called, "destroy_process_group was not called in the finally block"
    assert 1 in finish_calls, "wandb.finish(exit_code=1) not called before cleanup"


# [pr_diff] pass_to_pass
def test_wandb_cleanup():
    """wandb.finish(exit_code=1) must be called when an exception occurs."""
    finish_calls = []
    clean_exit, _, _ = _extract_clean_exit(
        wandb_finish=lambda exit_code=None: finish_calls.append(exit_code),
    )

    @clean_exit
    async def failing_async():
        raise ValueError("dataset error")

    try:
        asyncio.run(failing_async())
    except (SystemExit, Exception):
        pass

    assert 1 in finish_calls, f"wandb.finish(exit_code=1) not called; calls were: {finish_calls}"


# [repo_tests] pass_to_pass
def test_success_path_async():
    """Async success path returns values normally."""
    clean_exit, _, _ = _extract_clean_exit()

    @clean_exit
    async def success_async():
        return 42

    result = asyncio.run(success_async())
    assert result == 42, f"Async success returned {result} instead of 42"


# [repo_tests] pass_to_pass
def test_success_path_sync():
    """Sync success path returns values normally."""
    clean_exit, _, _ = _extract_clean_exit()

    @clean_exit
    def success_sync():
        return "ok"

    result = success_sync()
    assert result == "ok", f"Sync success returned {result!r} instead of 'ok'"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:23 @ 27c35b1
def test_error_never_silent():
    """AGENTS.md line 23: 'Errors should never pass silently.'
    The error path must call wandb.finish(exit_code=1) and terminate, not silently hang."""
    finish_calls = []
    clean_exit, _, _ = _extract_clean_exit(
        wandb_finish=lambda exit_code=None: finish_calls.append(exit_code),
    )

    for wrapper_type, make_fn in [("async", True), ("sync", False)]:
        finish_calls.clear()
        if make_fn:
            @clean_exit
            async def fn():
                raise ValueError("must not be silent")
            run = lambda: asyncio.run(fn())
        else:
            @clean_exit
            def fn():
                raise ValueError("must not be silent")
            run = fn

        raised = False
        try:
            run()
        except SystemExit as e:
            raised = True
            assert e.code, (
                f"{wrapper_type}: sys.exit called with falsy code {e.code!r} — "
                "errors should never pass silently (AGENTS.md:23)"
            )
        except Exception:
            raised = True  # at least it didn't pass silently

        assert raised, f"{wrapper_type}: no exception raised — error passed silently"
        assert 1 in finish_calls, (
            f"{wrapper_type}: wandb.finish(exit_code=1) not called — "
            "errors must be reported to wandb before termination (AGENTS.md:23)"
        )


# [static] pass_to_pass
def test_not_stub():
    """clean_exit must not be stubbed — must have async+sync wrappers with try/except/finally."""
    src = UTILS_PY.read_text()
    tree = ast.parse(src)

    non_blank = [l for l in src.strip().split("\n") if l.strip()]
    assert len(non_blank) >= 50, f"utils.py has only {len(non_blank)} non-blank lines (likely gutted)"

    clean_exit_node = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "clean_exit":
            clean_exit_node = node
            break
    assert clean_exit_node is not None, "clean_exit function not found"

    inner_funcs = [
        n for n in ast.walk(clean_exit_node)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name != "clean_exit"
    ]
    assert len(inner_funcs) >= 2, f"clean_exit has only {len(inner_funcs)} inner functions (need >=2)"

    has_async = any(isinstance(f, ast.AsyncFunctionDef) for f in inner_funcs)
    assert has_async, "clean_exit has no async inner function"

    has_try = any(
        isinstance(node, ast.Try)
        for func in inner_funcs
        for node in ast.walk(func)
    )
    assert has_try, "Inner wrappers have no try/except (likely stubbed)"

    has_dpg = any(
        isinstance(node, ast.Attribute) and node.attr == "destroy_process_group"
        for node in ast.walk(clean_exit_node)
    )
    assert has_dpg, "destroy_process_group not referenced in clean_exit"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff lint check passes (pass_to_pass)."""
    # Install ruff if not present
    try:
        subprocess.run(["python3", "-c", "import ruff"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["pip3", "install", "-q", "ruff"], capture_output=True, check=False)

    r = subprocess.run(
        ["python3", "-m", "ruff", "check", str(UTILS_PY), "--config", str(Path(REPO) / "pyproject.toml")],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes (pass_to_pass)."""
    # Install ruff if not present
    try:
        subprocess.run(["python3", "-c", "import ruff"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["pip3", "install", "-q", "ruff"], capture_output=True, check=False)

    r = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check", str(UTILS_PY), "--config", str(Path(REPO) / "pyproject.toml")],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_pathing():
    """Repo's unit tests for utils/pathing.py pass (pass_to_pass).
    Tests that don't require heavy dependencies (torch, wandb, loguru)."""
    # Install pytest if not present
    try:
        subprocess.run(["python3", "-c", "import pytest"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["pip3", "install", "-q", "pytest"], capture_output=True, check=False)

    # Temporarily rename conftest.py to avoid import errors with heavy deps
    conftest = Path(REPO) / "tests" / "conftest.py"
    conftest_bak = Path(REPO) / "tests" / "conftest.py.bak"

    try:
        if conftest.exists():
            conftest.rename(conftest_bak)

        # Run only the tests that don't require loguru (skip tests with clean=True flag)
        env = {**os.environ, "PYTHONPATH": f"{REPO}/src"}
        r = subprocess.run(
            [
                "python3", "-m", "pytest",
                "tests/unit/utils/test_pathing.py::test_nonexistent_dir_passes",
                "tests/unit/utils/test_pathing.py::test_empty_dir_passes",
                "tests/unit/utils/test_pathing.py::test_dir_with_only_logs_passes",
                "tests/unit/utils/test_pathing.py::test_dir_with_checkpoints_raises",
                "tests/unit/utils/test_pathing.py::test_dir_with_checkpoints_passes_when_resuming",
                "-v", "--tb=short"
            ],
            capture_output=True, text=True, timeout=120, cwd=REPO, env=env,
        )
    finally:
        if conftest_bak.exists():
            conftest_bak.rename(conftest)

    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_pyproject_toml():
    """Repo's pyproject.toml is valid TOML and has required sections (pass_to_pass)."""
    # Use tomllib (Python 3.11+) or install tomli for older versions
    try:
        import tomllib
    except ImportError:
        subprocess.run(["pip3", "install", "-q", "tomli"], capture_output=True, check=False)
        import tomli as tomllib

    pyproject_path = Path(REPO) / "pyproject.toml"
    content = pyproject_path.read_bytes()

    # Must be valid TOML
    data = tomllib.loads(content.decode("utf-8"))

    # Check required sections exist
    assert "project" in data, "Missing [project] section"
    assert "tool" in data, "Missing [tool] section"
    assert "ruff" in data["tool"], "Missing [tool.ruff] section"

    # Verify project metadata
    project = data["project"]
    assert project.get("name") == "prime-rl", "Project name should be prime-rl"
    assert "dependencies" in project, "Missing dependencies in [project]"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint_all():
    """Repo's ruff lint check passes on entire src/ directory (pass_to_pass)."""
    # Install ruff if not present
    try:
        subprocess.run(["python3", "-c", "import ruff"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["pip3", "install", "-q", "ruff"], capture_output=True, check=False)

    r = subprocess.run(
        ["python3", "-m", "ruff", "check", f"{REPO}/src", "--config", f"{REPO}/pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint on src/ failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_all():
    """Repo's ruff format check passes on entire src/ directory (pass_to_pass)."""
    # Install ruff if not present
    try:
        subprocess.run(["python3", "-c", "import ruff"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["pip3", "install", "-q", "ruff"], capture_output=True, check=False)

    r = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check", f"{REPO}/src", "--config", f"{REPO}/pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check on src/ failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tests_dir_lint():
    """Repo's tests directory passes ruff lint (pass_to_pass)."""
    # Install ruff if not present
    try:
        subprocess.run(["python3", "-c", "import ruff"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["pip3", "install", "-q", "ruff"], capture_output=True, check=False)

    r = subprocess.run(
        ["python3", "-m", "ruff", "check", f"{REPO}/tests", "--config", f"{REPO}/pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint on tests/ failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"