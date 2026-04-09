"""
Task: gradio-generator-cancel-chatinterface
Repo: gradio-app/gradio @ 5c4dc6aca11575cf4fec6704afd48a54664f983f
PR:   13047

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import asyncio
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"


def _extract_utils_ns():
    """Extract SyncToAsyncIterator and safe_aclose_iterator via AST + exec.

    We avoid importing gradio.utils because the full gradio package has heavy
    deps (fastapi, pydantic, etc.) that may not be installed.  The functions
    under test only need asyncio and time.
    """
    src = Path(f"{REPO}/gradio/utils.py").read_text()
    tree = ast.parse(src)

    segments = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SyncToAsyncIterator":
            segments.append(ast.get_source_segment(src, node))
        elif isinstance(node, ast.AsyncFunctionDef) and node.name == "safe_aclose_iterator":
            segments.append(ast.get_source_segment(src, node))

    assert len(segments) == 2, (
        f"Expected SyncToAsyncIterator + safe_aclose_iterator, got {len(segments)} segments"
    )

    code = "import asyncio\nimport time\n\n" + "\n\n".join(segments)
    ns: dict = {}
    exec(compile(code, "<utils_extract>", "exec"), ns)
    return ns


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """chat_interface.py and utils.py must parse without errors."""
    import py_compile

    for f in ["gradio/chat_interface.py", "gradio/utils.py"]:
        py_compile.compile(f"{REPO}/{f}", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioural tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_aclose_is_coroutine():
    """SyncToAsyncIterator.aclose() must be async (return a coroutine)."""
    ns = _extract_utils_ns()
    SyncToAsyncIterator = ns["SyncToAsyncIterator"]

    # Test with three different generators to vary inputs
    for values in [[1], ["a", "b"], list(range(5))]:

        def make_gen(vals):
            def gen():
                yield from vals
            return gen

        it = SyncToAsyncIterator(make_gen(values)(), limiter=None)
        result = it.aclose()
        assert asyncio.iscoroutine(result), (
            f"aclose() did not return a coroutine for generator({values})"
        )
        # Clean up coroutine to avoid RuntimeWarning
        result.close()


# [pr_diff] fail_to_pass
def test_aclose_closes_underlying_generator():
    """Awaiting SyncToAsyncIterator.aclose() must close the underlying sync generator."""
    ns = _extract_utils_ns()
    SyncToAsyncIterator = ns["SyncToAsyncIterator"]

    async def check_close(values):
        close_record: list[bool] = []

        def tracked_gen():
            try:
                for v in values:
                    yield v
            finally:
                close_record.append(True)

        gen = tracked_gen()
        next(gen)  # Start the generator so it enters the try block
        it = SyncToAsyncIterator(gen, limiter=None)
        await it.aclose()
        assert close_record, f"Generator({values}) finally block never ran -- aclose failed"

    async def run():
        await check_close(["a", "b"])
        await check_close([1, 2, 3])
        await check_close(list(range(10)))

    asyncio.run(run())


# [pr_diff] fail_to_pass
def test_safe_aclose_iterator_awaits_generic_async_iterator():
    """safe_aclose_iterator must await aclose() on generic async iterators."""
    ns = _extract_utils_ns()
    safe_aclose_iterator = ns["safe_aclose_iterator"]

    class MockAsyncIterator:
        def __init__(self):
            self.closed = False

        async def aclose(self):
            await asyncio.sleep(0)
            self.closed = True

    async def run():
        for _ in range(3):
            mock = MockAsyncIterator()
            await safe_aclose_iterator(mock)
            assert mock.closed, "safe_aclose_iterator did not await aclose() on generic iterator"

    asyncio.run(run())


# [pr_diff] fail_to_pass
def test_aclosing_used_in_stream_fn():
    """_stream_fn must wrap generator iteration with aclosing() context manager."""
    # AST-only because: _stream_fn is an async generator method on ChatInterface,
    # which requires the full gradio framework (blocks, routes, etc.) to instantiate
    src = Path(f"{REPO}/gradio/chat_interface.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_stream_fn":
            for child in ast.walk(node):
                if isinstance(child, ast.AsyncWith):
                    for item in child.items:
                        if (
                            isinstance(item.context_expr, ast.Call)
                            and isinstance(item.context_expr.func, ast.Name)
                            and item.context_expr.func.id == "aclosing"
                        ):
                            return  # Found it
            raise AssertionError("_stream_fn does not use `async with aclosing(generator)`")

    raise AssertionError("_stream_fn method not found in chat_interface.py")


# [pr_diff] fail_to_pass
def test_aclosing_used_in_examples_stream_fn():
    """_examples_stream_fn must wrap generator iteration with aclosing() context manager."""
    # AST-only because: _examples_stream_fn is an async generator on ChatInterface,
    # requires full gradio framework to instantiate and invoke
    src = Path(f"{REPO}/gradio/chat_interface.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_examples_stream_fn":
            for child in ast.walk(node):
                if isinstance(child, ast.AsyncWith):
                    for item in child.items:
                        if (
                            isinstance(item.context_expr, ast.Call)
                            and isinstance(item.context_expr.func, ast.Name)
                            and item.context_expr.func.id == "aclosing"
                        ):
                            return  # Found it
            raise AssertionError(
                "_examples_stream_fn does not use `async with aclosing(generator)`"
            )

    raise AssertionError("_examples_stream_fn method not found in chat_interface.py")


# ---------------------------------------------------------------------------
# Pass-to-pass (static / pr_diff) -- anti-stub + regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_safe_aclose_iterator_awaits_sync_to_async():
    """safe_aclose_iterator must close a SyncToAsyncIterator properly.

    On base: sync aclose works without await. On fix: async aclose + await works.
    Catches incomplete fixes where only one of the two changes is applied.
    """
    ns = _extract_utils_ns()
    SyncToAsyncIterator = ns["SyncToAsyncIterator"]
    safe_aclose_iterator = ns["safe_aclose_iterator"]

    async def check(values):
        close_record: list[bool] = []

        def tracked_gen():
            try:
                for v in values:
                    yield v
            finally:
                close_record.append(True)

        gen = tracked_gen()
        next(gen)  # Start the generator so it enters the try block
        it = SyncToAsyncIterator(gen, limiter=None)
        await safe_aclose_iterator(it)
        assert close_record, (
            f"safe_aclose_iterator did not close SyncToAsyncIterator({values})"
        )

    async def run():
        await check([10, 20])
        await check(["x"])
        await check(list(range(5)))

    asyncio.run(run())


# [static] pass_to_pass
def test_aclose_not_stub():
    """SyncToAsyncIterator.aclose must have a real body (not just pass/return None)."""
    # AST-only because: checking function body shape (stub detection), not behavior
    src = Path(f"{REPO}/gradio/utils.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SyncToAsyncIterator":
            for item in node.body:
                if isinstance(item, (ast.AsyncFunctionDef, ast.FunctionDef)) and item.name == "aclose":
                    stmts = [
                        s for s in item.body
                        if not isinstance(s, ast.Pass)
                        and not (
                            isinstance(s, ast.Expr)
                            and isinstance(s.value, ast.Constant)
                            and isinstance(s.value.value, str)
                        )
                    ]
                    assert len(stmts) >= 1, "aclose() body is a stub"
                    return

    raise AssertionError("SyncToAsyncIterator.aclose not found")


# [static] pass_to_pass
def test_safe_aclose_not_stub():
    """safe_aclose_iterator must have substantial logic (retry loop, branching)."""
    # AST-only because: checking function body shape (stub detection), not behavior
    src = Path(f"{REPO}/gradio/utils.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "safe_aclose_iterator":
            stmts = [
                s for s in node.body
                if not isinstance(s, ast.Pass)
                and not (
                    isinstance(s, ast.Expr)
                    and isinstance(s.value, ast.Constant)
                    and isinstance(s.value.value, str)
                )
            ]
            assert len(stmts) >= 2, "safe_aclose_iterator body is a stub"
            return

    raise AssertionError("safe_aclose_iterator not found")


# [static] pass_to_pass
def test_aclosing_imported():
    """chat_interface.py must import aclosing from contextlib."""
    # AST-only because: checking import presence, not runtime behavior
    src = Path(f"{REPO}/gradio/chat_interface.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "contextlib":
            if any(alias.name == "aclosing" for alias in node.names):
                return

    raise AssertionError("aclosing not imported from contextlib in chat_interface.py")


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates -- ensure fix doesn't break existing functionality
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check_modified():
    """Modified Python files pass ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, timeout=60,
    )
    for f in ["gradio/chat_interface.py", "gradio/utils.py"]:
        r = subprocess.run(
            ["ruff", "check", f],
            cwd=REPO, capture_output=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"ruff check failed on {f}:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
        )


# [repo_tests] pass_to_pass
def test_repo_ruff_format_modified():
    """Modified Python files pass ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, timeout=60,
    )
    for f in ["gradio/chat_interface.py", "gradio/utils.py"]:
        r = subprocess.run(
            ["ruff", "format", "--check", f],
            cwd=REPO, capture_output=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"ruff format --check failed on {f}:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
        )


# [repo_tests] pass_to_pass
def test_repo_imports():
    """gradio package imports successfully (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "import gradio"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"gradio import failed:\n{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_import_modified_modules():
    """Modified modules import successfully (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "from gradio import utils; from gradio import chat_interface"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Module import failed:\n{r.stderr.decode()[-500:]}"

# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- AGENTS.md:43 @ 5c4dc6aca11575cf4fec6704afd48a54664f983f
def test_ruff_format_check():
    """Modified Python files must pass ruff formatting (AGENTS.md: 'Python code is formatted with ruff')."""
    subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, timeout=60,
    )
    for f in ["gradio/chat_interface.py", "gradio/utils.py"]:
        r = subprocess.run(
            ["ruff", "format", "--check", f],
            cwd=REPO, capture_output=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"ruff format --check failed on {f}:\n{r.stdout.decode()}\n{r.stderr.decode()}"
        )
