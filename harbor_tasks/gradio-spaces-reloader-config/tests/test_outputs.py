"""
Task: gradio-spaces-reloader-config
Repo: gradio-app/gradio @ 34ee825ae7111488655e68f983e45d55673455a2
PR:   12874

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/workspace/gradio"
TARGET = f"{REPO}/gradio/utils.py"


def _load_spaces_reloader_class():
    """Extract SpacesReloader from source and compile with a mock parent.

    This lets us call real methods without importing the full Gradio stack.
    # AST-extract + exec because: importing gradio requires heavy deps (fastapi,
    # uvicorn, pydantic, etc.) not installed in the test environment.
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SpacesReloader":
            cls_src = "\n".join(source.splitlines()[node.lineno - 1 : node.end_lineno])
            break
    else:
        raise AssertionError("SpacesReloader class not found in utils.py")

    class _MockServerReloader:
        """Stand-in for ServerReloader that tracks swap_blocks calls."""

        def swap_blocks(self, demo):
            self._parent_swap_called = True
            self._parent_swap_demo = demo

    import threading
    from types import ModuleType

    ns = {
        "ServerReloader": _MockServerReloader,
        "Blocks": type("Blocks", (), {}),
        "App": type("App", (), {}),
        "ModuleType": ModuleType,
        "threading": threading,
        "NO_RELOAD": MagicMock(),
    }
    exec(cls_src, ns)
    return ns["SpacesReloader"], _MockServerReloader


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_valid():
    """gradio/utils.py must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_swap_blocks_regenerates_config():
    """After swap_blocks, demo.config must equal demo.get_config_file()."""
    SpacesReloader, _ = _load_spaces_reloader_class()
    reloader = SpacesReloader.__new__(SpacesReloader)

    # Test with three different config shapes to prevent hardcoding
    configs = [
        {"mode": "blocks", "components": [1, 2, 3]},
        {"mode": "interface", "components": []},
        {"mode": "chat", "components": [{"id": 1}, {"id": 2}], "theme": "dark"},
    ]
    for new_config in configs:
        demo = MagicMock()
        demo.get_config_file.return_value = new_config
        demo.config = {"stale": True}

        reloader.swap_blocks(demo)

        assert demo.config == new_config, (
            f"demo.config should be regenerated from get_config_file(), "
            f"expected {new_config}, got {demo.config}"
        )
    demo.get_config_file.assert_called()


# [pr_diff] fail_to_pass
def test_config_varies_per_demo():
    """Swapping to different demos must produce their respective configs."""
    SpacesReloader, _ = _load_spaces_reloader_class()
    reloader = SpacesReloader.__new__(SpacesReloader)

    demo_a = MagicMock()
    demo_a.get_config_file.return_value = {"demo": "A", "components": ["textbox"]}
    demo_a.config = None

    reloader.swap_blocks(demo_a)
    assert demo_a.config == {"demo": "A", "components": ["textbox"]}

    demo_b = MagicMock()
    demo_b.get_config_file.return_value = {"demo": "B", "components": ["image", "slider"]}
    demo_b.config = None

    reloader.swap_blocks(demo_b)
    assert demo_b.config == {"demo": "B", "components": ["image", "slider"]}

    # Configs must be independent — demo_a's config unchanged
    assert demo_a.config == {"demo": "A", "components": ["textbox"]}


# [pr_diff] fail_to_pass
def test_postrun_updates_config_on_swap():
    """When postrun detects a changed demo, config must be regenerated."""
    SpacesReloader, _ = _load_spaces_reloader_class()
    reloader = SpacesReloader.__new__(SpacesReloader)

    old_demo = MagicMock()
    new_demo = MagicMock()
    new_config = {"refreshed": True, "components": ["audio"]}
    new_demo.get_config_file.return_value = new_config
    new_demo.config = {"stale": True}

    reloader.watch_module = MagicMock()
    reloader.demo_name = "demo"
    setattr(reloader.watch_module, "demo", new_demo)
    reloader.app = MagicMock()
    reloader.app.blocks = old_demo  # different from new_demo -> triggers swap

    result = reloader.postrun()

    assert result is True, "postrun should return True when demo changed"
    assert new_demo.config == new_config, (
        f"After postrun swap, demo.config should be refreshed, got {new_demo.config}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_swap_blocks_calls_parent():
    """swap_blocks must delegate to the parent class (super().swap_blocks)."""
    SpacesReloader, _ = _load_spaces_reloader_class()
    reloader = SpacesReloader.__new__(SpacesReloader)

    demo = MagicMock()
    demo.get_config_file.return_value = {"test": True}

    reloader.swap_blocks(demo)

    assert getattr(reloader, "_parent_swap_called", False), (
        "swap_blocks must call super().swap_blocks(demo) to delegate to parent"
    )
    assert getattr(reloader, "_parent_swap_demo", None) is demo, (
        "super().swap_blocks must be called with the same demo argument"
    )


# [pr_diff] pass_to_pass
def test_postrun_returns_false_when_unchanged():
    """postrun returns False when the demo has not changed."""
    SpacesReloader, _ = _load_spaces_reloader_class()
    reloader = SpacesReloader.__new__(SpacesReloader)

    same_demo = MagicMock()
    reloader.watch_module = MagicMock()
    reloader.demo_name = "demo"
    setattr(reloader.watch_module, "demo", same_demo)
    reloader.app = MagicMock()
    reloader.app.blocks = same_demo  # same object -> no change

    result = reloader.postrun()
    assert result is False, "postrun should return False when demo hasn't changed"


# [static] pass_to_pass
def test_not_stub():
    """SpacesReloader must have a swap_blocks method with real logic."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SpacesReloader":
            method_names = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            assert "postrun" in method_names, "postrun method not found in SpacesReloader"

            # Check swap_blocks has a non-trivial body (not just pass/return None)
            for n in node.body:
                if isinstance(n, ast.FunctionDef) and n.name == "swap_blocks":
                    body_stmts = [
                        s for s in n.body
                        if not isinstance(s, (ast.Pass, ast.Expr))
                        or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Call))
                    ]
                    assert len(body_stmts) >= 2, (
                        "swap_blocks body is too short — must call super and set config"
                    )
                    break
            break
    else:
        raise AssertionError("SpacesReloader class not found in utils.py")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates from the actual repo
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_syntax():
    """Repo's Python syntax check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", f"{REPO}/gradio/utils.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ruff lint check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select", "E9,F63,F7,F82",
         "--target-version", "py310", f"{REPO}/gradio/utils.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff lint check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_format():
    """Repo's ruff format check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", f"{REPO}/gradio/utils.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_reload():
    """Repo's reload module unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", f"{REPO}/requirements.txt", "pytest", "hypothesis", "--quiet"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f"{REPO}/test/test_reload.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Reload tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_utils_delete_none():
    """Repo's utils delete_none unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", f"{REPO}/requirements.txt", "pytest", "hypothesis", "--quiet"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f"{REPO}/test/test_utils.py::TestDeleteNone", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Utils delete_none tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_utils_sanitize_csv():
    """Repo's utils sanitize CSV unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", f"{REPO}/requirements.txt", "pytest", "hypothesis", "--quiet"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f"{REPO}/test/test_utils.py::TestSanitizeForCSV", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Utils sanitize CSV tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_utils_format_ner():
    """Repo's utils format NER unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", f"{REPO}/requirements.txt", "pytest", "hypothesis", "--quiet"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f"{REPO}/test/test_utils.py::TestFormatNERList", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Utils format NER tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_utils_append_suffix():
    """Repo's utils append unique suffix unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", f"{REPO}/requirements.txt", "pytest", "hypothesis", "--quiet"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f"{REPO}/test/test_utils.py::TestAppendUniqueSuffix", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Utils append suffix tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_utils_function_params():
    """Repo's utils function params unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", f"{REPO}/requirements.txt", "pytest", "hypothesis", "--quiet"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f"{REPO}/test/test_utils.py::TestFunctionParams", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Utils function params tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
