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
import sys
import types
from pathlib import Path
from typing import Any, Callable

REPO = "/workspace/prime-rl"
UTILS_PY = Path(REPO) / "src/prime_rl/utils/utils.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_clean_exit(*, wandb_finish=None, dist_initialized=False, dist_destroy=None):
    """Extract and exec the clean_exit decorator with mocked dependencies.

    Args:
        wandb_finish: custom callback for wandb.finish(exit_code=...)
        dist_initialized: whether dist.is_initialized() returns True
        dist_destroy: custom callback for dist.destroy_process_group()
    """
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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_async_exit():
    """Async clean_exit must raise SystemExit (via sys.exit) instead of re-raising the original exception."""
    clean_exit, _, _ = _extract_clean_exit()

    @clean_exit
    async def failing_async():
        raise ValueError("dataset is not set")

    try:
        asyncio.run(failing_async())
        assert False, "No exception raised at all"
    except SystemExit as e:
        assert e.code, f"sys.exit called with falsy code {e.code!r} — error path must exit non-zero"
    except ValueError:
        raise AssertionError("Async wrapper re-raised ValueError instead of calling sys.exit")


# [pr_diff] fail_to_pass
def test_sync_exit():
    """Sync clean_exit must raise SystemExit (via sys.exit) instead of re-raising the original exception."""
    clean_exit, _, _ = _extract_clean_exit()

    @clean_exit
    def failing_sync():
        raise RuntimeError("config missing")

    try:
        failing_sync()
        assert False, "No exception raised at all"
    except SystemExit as e:
        assert e.code, f"sys.exit called with falsy code {e.code!r} — error path must exit non-zero"
    except RuntimeError:
        raise AssertionError("Sync wrapper re-raised RuntimeError instead of calling sys.exit")


# [pr_diff] fail_to_pass
def test_async_exit_different_exception():
    """Async clean_exit terminates with SystemExit for various exception types, not just ValueError."""
    clean_exit, _, _ = _extract_clean_exit()

    for exc_type, msg in [(TypeError, "bad type"), (KeyError, "missing key"), (OSError, "io fail")]:
        @clean_exit
        async def failing_async(et=exc_type, m=msg):
            raise et(m)

        try:
            asyncio.run(failing_async())
            assert False, f"No exception raised for {exc_type.__name__}"
        except SystemExit as e:
            assert e.code, f"sys.exit called with falsy code for {exc_type.__name__}"
        except Exception as orig:
            raise AssertionError(
                f"Async wrapper re-raised {type(orig).__name__} instead of calling sys.exit"
            )


# [pr_diff] fail_to_pass
def test_sync_exit_different_exception():
    """Sync clean_exit terminates with SystemExit for various exception types."""
    clean_exit, _, _ = _extract_clean_exit()

    for exc_type, msg in [(TypeError, "bad type"), (KeyError, "missing key"), (OSError, "io fail")]:
        @clean_exit
        def failing_sync(et=exc_type, m=msg):
            raise et(m)

        try:
            failing_sync()
            assert False, f"No exception raised for {exc_type.__name__}"
        except SystemExit as e:
            assert e.code, f"sys.exit called with falsy code for {exc_type.__name__}"
        except Exception as orig:
            raise AssertionError(
                f"Sync wrapper re-raised {type(orig).__name__} instead of calling sys.exit"
            )


# [pr_diff] pass_to_pass
def test_finally_cleanup():
    """The finally block must still execute, destroying the process group on error."""
    cleanup_called = []
    clean_exit, _, _ = _extract_clean_exit(
        dist_initialized=True,
        dist_destroy=lambda: cleanup_called.append(True),
    )

    @clean_exit
    async def failing_async():
        raise ValueError("boom")

    try:
        asyncio.run(failing_async())
    except (SystemExit, Exception):
        pass

    assert cleanup_called, "destroy_process_group was not called in the finally block"


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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

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
    The error path must terminate with a non-zero exit, not silently hang or return None."""
    clean_exit, _, _ = _extract_clean_exit()

    for wrapper_type, make_fn in [("async", True), ("sync", False)]:
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
