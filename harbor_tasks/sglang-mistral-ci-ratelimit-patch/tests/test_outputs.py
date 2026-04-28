"""
Task: sglang-mistral-ci-ratelimit-patch
Repo: sgl-project/sglang @ 33cca495ae75e745be62b5b009f4c87fb40dd044
PR:   21729

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import contextlib
import logging
import subprocess
import sys
import textwrap
import types
from pathlib import Path

import pytest

REPO = "/repo"
TARGET = f"{REPO}/python/sglang/srt/utils/hf_transformers_utils.py"


def _ensure_sglang_importable():
    """Check if sglang package is importable; skip test if not."""
    r = subprocess.run(
        ["python3", "-c", "import sglang"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    if r.returncode != 0:
        pytest.skip(f"sglang not importable (missing heavy deps): {r.stderr.strip()}")


# ---------------------------------------------------------------------------
# Pass-to-pass gates (static) - file structure checks (NOT actual CI commands)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_repo_file_structure():
    """Repo file structure is valid (pass_to_pass)."""
    python_dir = Path(REPO) / "python" / "sglang"
    assert python_dir.exists(), f"Python sglang directory not found: {python_dir}"
    assert python_dir.is_dir(), f"Python sglang path is not a directory: {python_dir}"

    target_path = Path(TARGET)
    assert target_path.exists(), f"Target file not found: {TARGET}"
    assert target_path.is_file(), f"Target path is not a file: {TARGET}"


# [static] pass_to_pass
def test_repo_pyproject_toml_valid():
    """Repo's pyproject.toml is valid TOML (pass_to_pass)."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    pyproject_path = Path(REPO) / "python" / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        parsed = tomllib.loads(content)
        assert "project" in parsed, "pyproject.toml missing [project] section"
        assert "name" in parsed["project"], "pyproject.toml missing project.name"


# [static] pass_to_pass
def test_repo_ast_valid():
    """All Python files in sglang/srt/utils parse without syntax errors (pass_to_pass)."""
    utils_dir = Path(REPO) / "python" / "sglang" / "srt" / "utils"
    if not utils_dir.exists():
        return

    for py_file in utils_dir.glob("*.py"):
        source = py_file.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {py_file}: {e}")


# [static] pass_to_pass
def test_repo_precommit_config_valid():
    """Repo's pre-commit config is valid YAML (pass_to_pass)."""
    import yaml
    precommit_path = Path(REPO) / ".pre-commit-config.yaml"
    if precommit_path.exists():
        content = precommit_path.read_text()
        parsed = yaml.safe_load(content)
        assert "repos" in parsed, "pre-commit config missing repos"


# ---------------------------------------------------------------------------
# Pass-to-pass gates (repo_tests) - REAL CI commands via subprocess.run()
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_linting():
    """Ruff linting passes on srt/utils (matches CI lint.yml) (pass_to_pass)."""
    check = subprocess.run(
        ["python3", "-m", "ruff", "--version"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    if check.returncode != 0:
        pytest.skip("ruff not installed (requires dev dependencies)")
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", "python/sglang/srt/utils/",
         "--select=F401,F821"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed: {r.stdout} {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax_check():
    """Python can parse target file via subprocess (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         f"import ast; ast.parse(open('{TARGET}').read())"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Target file syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_tokenizer_unit_tests():
    """Tokenizer unit tests pass (test_patch_tokenizer.py) (pass_to_pass)."""
    _ensure_sglang_importable()
    r = subprocess.run(
        ["python3", "-m", "pytest", "test/registered/unit/utils/test_patch_tokenizer.py",
         "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode in [0, 5], (
        f"Tokenizer unit tests failed:\n{r.stdout}\n{r.stderr}"
    )


# [repo_tests] pass_to_pass
def test_repo_pytest_version():
    """pytest is available and functional (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "--version"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"pytest not available:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """Python syntax check via py_compile passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_import_utils():
    """Target module imports successfully (pass_to_pass)."""
    _ensure_sglang_importable()
    r = subprocess.run(
        ["python3", "-c", "from sglang.srt.utils import hf_transformers_utils; print('OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr}"
    assert "OK" in r.stdout, f"Import did not print OK:\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_get_tokenizer_import():
    """get_tokenizer and TokenizerWarningsFilter are importable (pass_to_pass)."""
    _ensure_sglang_importable()
    r = subprocess.run(
        ["python3", "-c",
         "from sglang.srt.utils.hf_transformers_utils import get_tokenizer, TokenizerWarningsFilter; print('OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr}"
    assert "OK" in r.stdout, f"Import did not print OK:\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_ast_parse():
    """AST parsing of target file succeeds via subprocess (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         f"import ast; ast.parse(open('{TARGET}').read()); print('AST_OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed:\n{r.stderr}"
    assert "AST_OK" in r.stdout, f"AST check did not print AST_OK:\n{r.stdout}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _extract_source_range(source, tree, names):
    """Extract module-level declarations (assignments + functions) by name."""
    lines = source.splitlines(keepends=True)
    chunks = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))
    return "\n\n".join(chunks)


@contextlib.contextmanager
def _patch_env(ci_mode, transformers_version="5.3.0"):
    """Context manager: exec extracted patch code with mocked sglang/transformers deps.

    Yields (namespace, mock_tut) where namespace has the extracted functions and
    mock_tut is the mock transformers.tokenization_utils_tokenizers module.
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    code = _extract_source_range(source, tree, {
        "_is_base_mistral_patched",
        "_TRANSFORMERS_PATCHED_VERSION",
        "_patch_is_base_mistral_in_ci",
    })
    if not code.strip():
        yield None, None
        return

    mock_envs = types.SimpleNamespace(
        SGLANG_IS_IN_CI=types.SimpleNamespace(get=lambda: ci_mode)
    )

    mock_tut = types.ModuleType("transformers.tokenization_utils_tokenizers")
    mock_tut.is_base_mistral = lambda model_id: True

    mock_transformers = types.ModuleType("transformers")
    mock_transformers.__version__ = transformers_version
    mock_transformers.tokenization_utils_tokenizers = mock_tut

    mock_modules = {
        "sglang": types.ModuleType("sglang"),
        "sglang.srt": types.ModuleType("sglang.srt"),
        "sglang.srt.environ": types.SimpleNamespace(envs=mock_envs),
        "transformers": mock_transformers,
        "transformers.tokenization_utils_tokenizers": mock_tut,
    }

    saved = {}
    for name, mod in mock_modules.items():
        saved[name] = sys.modules.get(name)
        sys.modules[name] = mod

    try:
        ns = {"logger": logging.getLogger("test_patch"), "__builtins__": __builtins__}
        exec(compile(code, "<patch>", "exec"), ns)
        yield ns, mock_tut
    finally:
        for name, orig in saved.items():
            if orig is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = orig


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """hf_transformers_utils.py must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ci_patches_is_base_mistral():
    """In CI mode, _patch_is_base_mistral_in_ci replaces is_base_mistral with False."""
    r = _run_py("""\
import ast, types, sys, logging

TARGET = "/repo/python/sglang/srt/utils/hf_transformers_utils.py"
source = open(TARGET).read()
tree = ast.parse(source)

names = {
    "_is_base_mistral_patched",
    "_TRANSFORMERS_PATCHED_VERSION",
    "_patch_is_base_mistral_in_ci",
}
lines = source.splitlines(keepends=True)
chunks = []
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in names:
                chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))
    elif isinstance(node, ast.FunctionDef) and node.name in names:
        chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))

code = "\\n\\n".join(chunks)
assert code.strip(), "Patch function _patch_is_base_mistral_in_ci not found"

mock_envs = types.SimpleNamespace(
    SGLANG_IS_IN_CI=types.SimpleNamespace(get=lambda: True)
)
mock_tut = types.ModuleType("transformers.tokenization_utils_tokenizers")
mock_tut.is_base_mistral = lambda model_id: True
mock_tf = types.ModuleType("transformers")
mock_tf.__version__ = "5.3.0"
mock_tf.tokenization_utils_tokenizers = mock_tut

sys.modules["sglang"] = types.ModuleType("sglang")
sys.modules["sglang.srt"] = types.ModuleType("sglang.srt")
sys.modules["sglang.srt.environ"] = types.SimpleNamespace(envs=mock_envs)
sys.modules["transformers"] = mock_tf
sys.modules["transformers.tokenization_utils_tokenizers"] = mock_tut

ns = {"logger": logging.getLogger("test"), "__builtins__": __builtins__}
exec(compile(code, "<patch>", "exec"), ns)
ns["_patch_is_base_mistral_in_ci"]()

for model_id in ["mistralai/Mistral-7B", "some-other-model", "", "x" * 100]:
    result = mock_tut.is_base_mistral(model_id)
    assert result is False, f"Expected False for {model_id!r}, got {result!r}"

print("PASS")
""")
    assert r.returncode == 0, f"Subprocess failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_idempotent_multiple_calls():
    """Calling _patch_is_base_mistral_in_ci multiple times doesn't break the patch."""
    r = _run_py("""\
import ast, types, sys, logging

TARGET = "/repo/python/sglang/srt/utils/hf_transformers_utils.py"
source = open(TARGET).read()
tree = ast.parse(source)

names = {
    "_is_base_mistral_patched",
    "_TRANSFORMERS_PATCHED_VERSION",
    "_patch_is_base_mistral_in_ci",
}
lines = source.splitlines(keepends=True)
chunks = []
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in names:
                chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))
    elif isinstance(node, ast.FunctionDef) and node.name in names:
        chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))

code = "\\n\\n".join(chunks)
assert code.strip(), "Patch function not found"

mock_envs = types.SimpleNamespace(
    SGLANG_IS_IN_CI=types.SimpleNamespace(get=lambda: True)
)
mock_tut = types.ModuleType("transformers.tokenization_utils_tokenizers")
mock_tut.is_base_mistral = lambda model_id: True
mock_tf = types.ModuleType("transformers")
mock_tf.__version__ = "5.3.0"
mock_tf.tokenization_utils_tokenizers = mock_tut

sys.modules["sglang"] = types.ModuleType("sglang")
sys.modules["sglang.srt"] = types.ModuleType("sglang.srt")
sys.modules["sglang.srt.environ"] = types.SimpleNamespace(envs=mock_envs)
sys.modules["transformers"] = mock_tf
sys.modules["transformers.tokenization_utils_tokenizers"] = mock_tut

ns = {"logger": logging.getLogger("test"), "__builtins__": __builtins__}
exec(compile(code, "<patch>", "exec"), ns)
patch_fn = ns["_patch_is_base_mistral_in_ci"]
for _ in range(5):
    patch_fn()
for model_id in ["model-a", "model-b", "model-c"]:
    result = mock_tut.is_base_mistral(model_id)
    assert result is False, f"Expected False for {model_id!r} after 5 calls"

print("PASS")
""")
    assert r.returncode == 0, f"Subprocess failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_patch_before_from_pretrained():
    """_patch_is_base_mistral_in_ci() is called before AutoTokenizer.from_pretrained in get_tokenizer."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_tokenizer":
            patch_line = None
            pretrained_line = None

            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name) and child.func.id == "_patch_is_base_mistral_in_ci":
                        patch_line = child.lineno
                    if (isinstance(child.func, ast.Attribute)
                            and child.func.attr == "from_pretrained"
                            and isinstance(child.func.value, ast.Name)
                            and child.func.value.id == "AutoTokenizer"):
                        if pretrained_line is None:
                            pretrained_line = child.lineno

            assert patch_line is not None, (
                "_patch_is_base_mistral_in_ci() not called in get_tokenizer"
            )
            assert pretrained_line is not None, (
                "AutoTokenizer.from_pretrained not found in get_tokenizer"
            )
            assert patch_line < pretrained_line, (
                f"Patch (line {patch_line}) must come before "
                f"from_pretrained (line {pretrained_line})"
            )
            return

    raise AssertionError("get_tokenizer function not found")


# [static] fail_to_pass
def test_not_stub():
    """File has non-trivial CI patching logic (not a stub)."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    assert "is_base_mistral" in source, "File does not reference is_base_mistral"

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            body_types = {type(n).__name__ for n in ast.walk(node)}
            has_conditional = "If" in body_types
            has_import = "Import" in body_types or "ImportFrom" in body_types
            has_assign_or_global = "Global" in body_types or "Assign" in body_types
            stmt_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.stmt))

            if has_conditional and has_import and has_assign_or_global and stmt_count >= 6:
                return

    raise AssertionError(
        "No function with CI patching logic found "
        "(need conditionals + imports + assignments, 6+ statements)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_patch_without_ci_env():
    """Without SGLANG_IS_IN_CI, is_base_mistral is NOT replaced."""
    with _patch_env(ci_mode=False) as (ns, mock_tut):
        if ns is None:
            return
        ns["_patch_is_base_mistral_in_ci"]()
        for model_id in ["test-1", "test-2", "test-3"]:
            assert mock_tut.is_base_mistral(model_id) is True, (
                "is_base_mistral should NOT be patched without CI env"
            )


# [pr_diff] pass_to_pass
def test_version_guard_skips_on_mismatch():
    """Mismatched transformers version causes patch to be skipped."""
    with _patch_env(ci_mode=True, transformers_version="99.0.0") as (ns, mock_tut):
        if ns is None:
            return
        ns["_patch_is_base_mistral_in_ci"]()
        for model_id in ["test-1", "test-2"]:
            assert mock_tut.is_base_mistral(model_id) is True, (
                "is_base_mistral should NOT be patched when version mismatches"
            )


# [pr_diff] pass_to_pass
def test_get_tokenizer_signature():
    """get_tokenizer function exists with expected parameters."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_tokenizer":
            pos_params = [arg.arg for arg in node.args.args]
            kw_params = [arg.arg for arg in node.args.kwonlyargs]
            all_params = pos_params + kw_params
            assert "tokenizer_name" in all_params, f"tokenizer_name not in params: {all_params}"
            assert "tokenizer_mode" in all_params, f"tokenizer_mode not in params: {all_params}"
            return

    raise AssertionError("get_tokenizer function not found")


# [pr_diff] pass_to_pass
def test_tokenizer_warnings_filter_exists():
    """TokenizerWarningsFilter class exists with a filter() method."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TokenizerWarningsFilter":
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            assert "filter" in methods, "TokenizerWarningsFilter missing filter() method"
            return

    raise AssertionError("TokenizerWarningsFilter class not found")


# === CI-mined tests (taskforge.ci_check_miner) ===
# These test real CI commands. They are skipped when required infrastructure
# (Docker, GPU, NPU) is not available inside the test container.

def test_ci_stage_a_test_1_gpu_small_amd_ensure_vram_is_clear():
    """pass_to_pass | CI job 'stage-a-test-1-gpu-small-amd' -> step 'Ensure VRAM is clear'

    Requires AMD GPU hardware with ROCm; skipped in CPU-only test environments.
    """
    pytest.skip("requires AMD GPU hardware not available in test container")


def test_ci_stage_a_test_1_gpu_small_amd_start_ci_container():
    """pass_to_pass | CI job 'stage-a-test-1-gpu-small-amd' -> step 'Start CI container'

    Requires Docker daemon and AMD GPU; skipped in test container.
    """
    pytest.skip("requires docker daemon and AMD GPU not available in test container")


def test_ci_multimodal_gen_test_2_npu_a3_run_test():
    """pass_to_pass | CI job 'multimodal-gen-test-2-npu-a3' -> step 'Run test'

    Requires NPU A3 hardware; skipped in CPU-only test environments.
    """
    pytest.skip("requires NPU A3 hardware not available in test container")


def test_ci_multimodal_gen_test_1_npu_a3_run_test():
    """pass_to_pass | CI job 'multimodal-gen-test-1-npu-a3' -> step 'Run test'

    Requires NPU A3 hardware; skipped in CPU-only test environments.
    """
    pytest.skip("requires NPU A3 hardware not available in test container")


def test_ci_multimodal_gen_test_8_npu_a3_run_test():
    """pass_to_pass | CI job 'multimodal-gen-test-8-npu-a3' -> step 'Run test'

    Requires NPU A3 hardware; skipped in CPU-only test environments.
    """
    pytest.skip("requires NPU A3 hardware not available in test container")
