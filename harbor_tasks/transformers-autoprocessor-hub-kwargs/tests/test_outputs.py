"""
Task: transformers-autoprocessor-hub-kwargs
Repo: huggingface/transformers @ c17877c2ad39f8f736d5ea8a34f98e562843fc83
PR:   44710

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
from pathlib import Path

REPO = "/workspace/transformers"
TARGET = f"{REPO}/src/transformers/models/auto/processing_auto.py"


def _capture_cached_file_kwargs(test_kwargs: dict) -> dict:
    """Execute from_pretrained's kwargs-filtering logic and capture what reaches cached_file.

    Uses AST to extract the from_pretrained method body up to the first
    cached_file() call, then executes it with a mock cached_file that captures
    its kwargs.  This tests the actual filtering behavior regardless of variable
    names or implementation strategy used in the fix.
    """
    import inspect as inspect_mod

    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    # Find the from_pretrained method in AutoProcessor
    method_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AutoProcessor":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "from_pretrained":
                    method_node = item
                    break
            break

    assert method_node is not None, "AutoProcessor.from_pretrained not found"

    # Find all direct calls to cached_file in the method, pick the first by line
    cached_file_calls = []
    for child in ast.walk(method_node):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Name) and func.id == "cached_file":
                cached_file_calls.append(child)

    assert cached_file_calls, "No call to cached_file found in from_pretrained"
    cached_file_calls.sort(key=lambda n: n.lineno)
    first_call = cached_file_calls[0]

    # Extract code from method body start to first cached_file call (inclusive)
    source_lines = source.splitlines()
    body_start = method_node.body[0].lineno - 1  # 0-indexed
    code_end = first_call.end_lineno  # 1-indexed, inclusive
    code = textwrap.dedent("\n".join(source_lines[body_start:code_end]))

    # Mock cached_file with the same signature as the real one so that
    # inspect.signature() returns the same parameter names on the base commit.
    captured = {}

    def mock_cached_file(path_or_repo_id, filename, **kwargs):
        captured.update(kwargs)
        return None

    ns = {
        "kwargs": dict(test_kwargs),
        "pretrained_model_name_or_path": "fake-model",
        "cached_file": mock_cached_file,
        "inspect": inspect_mod,
        "PROCESSOR_NAME": "processor_config.json",
    }
    exec(code, ns)

    # Strip internal control flags that every implementation adds unconditionally
    return {k: v for k, v in captured.items() if not k.startswith("_raise_exceptions")}


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """processing_auto.py must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# [static] pass_to_pass - repo CI/CD check
def test_py_compile():
    """Repo CI: processing_auto.py must compile without syntax errors (pass_to_pass)."""
    import subprocess

    r = subprocess.run(
        ["python", "-m", "py_compile", TARGET],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass — ruff check (CI/CD gate)
def test_repo_ruff_check():
    """Repo CI: processing_auto.py must pass ruff linting (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass — ruff format check (CI/CD gate)
def test_repo_ruff_format():
    """Repo CI: processing_auto.py must be formatted correctly (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        ["ruff", "format", "--check", TARGET],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"ruff format check failed:\n{result.stdout}\n{result.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioural tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_hub_kwargs_forwarded():
    """force_download, cache_dir, and token must survive the cached_file filter."""
    test_kwargs = {
        "force_download": True,
        "cache_dir": "/tmp/hf_cache",
        "token": "hf_test_token_123",
        "processor_class": "SomeProcessor",
    }
    result = _capture_cached_file_kwargs(test_kwargs)

    for key in ("force_download", "cache_dir", "token"):
        assert key in result, f"{key} was dropped by the cached_file kwargs filter"
        assert result[key] == test_kwargs[key], f"{key} has wrong value"
    assert "processor_class" not in result, "processor_class should not be forwarded to cached_file"


# [pr_diff] fail_to_pass
def test_revision_and_subfolder_forwarded():
    """revision, subfolder, local_files_only, user_agent must survive the filter."""
    test_kwargs = {
        "revision": "refs/pr/42",
        "subfolder": "models/processor",
        "local_files_only": True,
        "user_agent": "test-agent/1.0",
        "task": "image-classification",
    }
    result = _capture_cached_file_kwargs(test_kwargs)

    for key in ("revision", "subfolder", "local_files_only", "user_agent"):
        assert key in result, f"{key} was dropped by the cached_file kwargs filter"
        assert result[key] == test_kwargs[key], f"{key} has wrong value"
    assert "task" not in result, "task should not be forwarded to cached_file"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + cleanup
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """from_pretrained must have a substantial implementation, not a stub."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AutoProcessor":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "from_pretrained":
                    body = [s for s in item.body if not isinstance(s, (ast.Pass, ast.Expr))]
                    assert len(body) >= 10, (
                        f"from_pretrained has only {len(body)} statements — likely a stub"
                    )
                    return
    assert False, "AutoProcessor.from_pretrained not found"


# [pr_diff] fail_to_pass
def test_all_nine_hub_kwargs():
    """All 9 hub kwargs must be forwarded; non-hub kwargs must be excluded."""
    hub_kwargs = {
        "cache_dir": "/data/cache",
        "force_download": False,
        "proxies": {"https": "http://proxy:8080"},
        "token": "hf_abc",
        "revision": "v2.0",
        "local_files_only": False,
        "subfolder": "checkpoints",
        "repo_type": "model",
        "user_agent": "my-app/2.0",
    }
    non_hub_kwargs = {
        "processor_class": "WhisperProcessor",
        "task": "automatic-speech-recognition",
        "torch_dtype": "float16",
    }
    result = _capture_cached_file_kwargs({**hub_kwargs, **non_hub_kwargs})

    for key in hub_kwargs:
        assert key in result, f"hub kwarg '{key}' was dropped"
        assert result[key] == hub_kwargs[key], f"hub kwarg '{key}' has wrong value"
    for key in non_hub_kwargs:
        assert key not in result, f"non-hub kwarg '{key}' should not be forwarded"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:17 @ c17877c2ad39f8f736d5ea8a34f98e562843fc83
def test_ruff_clean():
    """processing_auto.py must pass ruff linting (code style enforced in CI)."""
    import subprocess

    result = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"


# [pr_diff] pass_to_pass
def test_no_unused_inspect_import():
    """If inspect is imported it must be used; otherwise it should be removed."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    has_inspect_import = any(
        (isinstance(n, ast.Import) and any(a.name == "inspect" for a in n.names))
        or (isinstance(n, ast.ImportFrom) and n.module == "inspect")
        for n in ast.walk(tree)
    )

    if has_inspect_import:
        usages = sum(
            1
            for line in source.splitlines()
            if "inspect." in line
            and not line.strip().startswith("#")
            and "import" not in line
        )
        assert usages > 0, "inspect is imported but never used — remove the import"


# ---------------------------------------------------------------------------
# Additional pass-to-pass (repo_tests) — repository CI consistency checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — check_inits utility
def test_repo_check_inits():
    """Repo CI: utils/check_inits.py must pass (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        ["python", f"{REPO}/utils/check_inits.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"check_inits failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass — sort_auto_mappings utility
def test_repo_sort_auto_mappings():
    """Repo CI: utils/sort_auto_mappings.py must pass (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        ["python", f"{REPO}/utils/sort_auto_mappings.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"sort_auto_mappings failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass — custom_init_isort utility
def test_repo_init_isort():
    """Repo CI: utils/custom_init_isort.py --check_only must pass (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        ["python", f"{REPO}/utils/custom_init_isort.py", "--check_only"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"custom_init_isort check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass — pytest on utils/import_utils (CI/CD test runner gate)
def test_pytest_utils_import_utils():
    """CI: pytest tests/utils/test_hf_argparser.py must pass (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        ["bash", "-lc", "cd /workspace/transformers && python -m pytest tests/utils/test_hf_argparser.py -x --tb=short -q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"pytest test_hf_argparser failed:\n{result.stdout}\n{result.stderr}"
