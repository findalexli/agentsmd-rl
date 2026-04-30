"""
Task: transformers-imgproc-fast-import-compat
Repo: huggingface/transformers @ e6ed96c7e93a6408a151e3177793212b02b8bb53
PR:   #44897

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = "/repo"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    for f in [
        "src/transformers/__init__.py",
        "src/transformers/image_processing_backends.py",
    ]:
        py_compile.compile(f"{REPO}/{f}", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_base_image_processor_fast_importable():
    """BaseImageProcessorFast importable from legacy path and resolves to TorchvisionBackend."""
    from transformers.image_processing_utils_fast import BaseImageProcessorFast
    from transformers.image_processing_backends import TorchvisionBackend

    assert BaseImageProcessorFast is TorchvisionBackend, (
        f"Expected same class: got {BaseImageProcessorFast!r} vs {TorchvisionBackend!r}"
    )


# [pr_diff] fail_to_pass
def test_divide_to_patches_importable():
    """divide_to_patches importable from legacy path and is the same function."""
    from transformers.image_processing_utils_fast import divide_to_patches
    from transformers.image_transforms import divide_to_patches as original

    assert callable(divide_to_patches), "divide_to_patches not callable"
    assert divide_to_patches is original, (
        f"Expected same function: got {divide_to_patches!r} vs {original!r}"
    )


# [pr_diff] fail_to_pass
def test_divide_to_patches_callable_via_alias():
    """divide_to_patches imported via alias actually works with real numpy arrays."""
    import numpy as np

    from transformers.image_processing_utils_fast import divide_to_patches

    # Test with multiple image sizes in CHW format to prevent hardcoding
    for c, h, w, patch_size, expected in [
        (3, 100, 100, 50, 4),   # 2x2 grid
        (3, 60, 80, 20, 12),    # 3x4 grid
        (1, 64, 64, 32, 4),     # 2x2 grid
    ]:
        img = np.random.randint(0, 256, (c, h, w), dtype=np.uint8)
        patches = divide_to_patches(img, patch_size)
        assert isinstance(patches, list), f"Expected list, got {type(patches)}"
        assert len(patches) == expected, (
            f"Expected {expected} patches for {c}x{h}x{w} ps={patch_size}, got {len(patches)}"
        )
        for p in patches:
            assert isinstance(p, np.ndarray), f"Each patch should be ndarray, got {type(p)}"


# [pr_diff] fail_to_pass
def test_alias_registered_in_sys_modules():
    """Alias module registered in sys.modules and accessible as a package attribute."""
    import transformers  # noqa: F401

    assert "transformers.image_processing_utils_fast" in sys.modules, (
        "image_processing_utils_fast not in sys.modules after import transformers"
    )
    # The alias module must be reachable as an attribute on the transformers package
    assert hasattr(transformers, "image_processing_utils_fast"), (
        "image_processing_utils_fast not accessible as attribute on transformers package"
    )
    mod = sys.modules["transformers.image_processing_utils_fast"]
    assert transformers.image_processing_utils_fast is mod, (
        "transformers.image_processing_utils_fast attr and sys.modules entry must be the same object"
    )


# [pr_diff] fail_to_pass
def test_inspect_no_circular_import():
    """inspect operations on alias module do not trigger circular import."""
    import inspect

    import transformers  # noqa: F401

    mod = sys.modules["transformers.image_processing_utils_fast"]
    # hasattr(mod, '__file__') must not fall through to __getattr__
    # which would trigger a premature (possibly circular) import.
    assert hasattr(mod, "__file__"), "hasattr(__file__) should be True"
    # inspect.getfile raises TypeError for __file__=None (like built-in modules) —
    # the key is that it does NOT raise ImportError from circular import.
    try:
        inspect.getfile(mod)
    except TypeError:
        pass  # Expected: __file__ is None, which is correct behavior


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_tokenization_aliases_still_work():
    """Existing tokenization module aliases are not broken."""
    import transformers  # noqa: F401

    assert "transformers.tokenization_utils_fast" in sys.modules, (
        "tokenization_utils_fast alias broken"
    )
    assert "transformers.tokenization_utils" in sys.modules, (
        "tokenization_utils alias broken"
    )


# [repo_tests] pass_to_pass — CI-derived checks
# These tests verify that the repo's CI checks pass on both base and gold commits

def test_repo_ruff_check_modified_files():
    """Repo's ruff check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        [
            "ruff", "check",
            "src/transformers/__init__.py",
            "src/transformers/image_processing_backends.py",
            "--quiet",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stderr}"


def test_repo_ruff_format_check_modified_files():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        [
            "ruff", "format", "--check",
            "src/transformers/__init__.py",
            "src/transformers/image_processing_backends.py",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stderr}"


def test_repo_import_transformers():
    """Repo's main package imports without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "import transformers; print(transformers.__version__)"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"transformers import failed:\n{r.stderr}"


# [pr_diff] pass_to_pass
def test_direct_import_image_processing_backends():
    """Direct import from image_processing_backends still works and provides a real class."""
    import inspect

    from transformers.image_processing_backends import TorchvisionBackend

    assert inspect.isclass(TorchvisionBackend), "TorchvisionBackend should be a class"
    assert hasattr(TorchvisionBackend, "to_dict"), "TorchvisionBackend missing to_dict method"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — .ai/skills/add-or-fix-type-checking/SKILL.md:185-186 @ e6ed96c
def test_no_bare_type_ignore():
    """No bare '# type: ignore' without error code in modified files."""
    for f in [
        "src/transformers/__init__.py",
        "src/transformers/image_processing_backends.py",
    ]:
        content = Path(f"{REPO}/{f}").read_text()
        bare_ignores = re.findall(r"#\s*type:\s*ignore(?!\[)", content)
        assert len(bare_ignores) == 0, (
            f"Bare '# type: ignore' (no error code) found in {f}"
        )


# ---------------------------------------------------------------------------
# Anti-stub — behavioral verification in a fresh subprocess
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """The image_processing_utils_fast alias provides real functionality in a fresh process."""
    r = subprocess.run(
        [
            "python", "-c",
            "import inspect; "
            "from transformers.image_processing_utils_fast import BaseImageProcessorFast, divide_to_patches; "
            "from transformers.image_processing_backends import TorchvisionBackend; "
            # BaseImageProcessorFast must be a real class (not a dummy/stub)
            "assert inspect.isclass(BaseImageProcessorFast); "
            "assert BaseImageProcessorFast is TorchvisionBackend; "
            # divide_to_patches must be a real callable function
            "assert callable(divide_to_patches); "
            "assert inspect.isfunction(divide_to_patches); "
            "print('OK')"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Anti-stub behavioral check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass — CI-derived checks
def test_repo_check_dummies():
    """Repo's check_dummies.py utility passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_dummies.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_dummies.py failed:\n{r.stderr[-500:]}"


def test_repo_check_inits():
    """Repo's check_inits.py utility passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_inits.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_inits.py failed:\n{r.stderr[-500:]}"


def test_repo_image_processing_backends_import():
    """image_processing_backends module imports without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "from transformers.image_processing_backends import TorchvisionBackend; print(TorchvisionBackend)"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"image_processing_backends import failed:\n{r.stderr[-500:]}"


def test_repo_divide_to_patches_importable():
    """divide_to_patches function is importable from image_transforms (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "from transformers.image_transforms import divide_to_patches; print('divide_to_patches:', callable(divide_to_patches))"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"divide_to_patches import failed:\n{r.stderr[-500:]}"


def test_repo_modified_files_parse_ast():
    """Modified Python files parse without AST errors (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-c",
            "import ast; ast.parse(open('src/transformers/__init__.py').read()); ast.parse(open('src/transformers/image_processing_backends.py').read()); print('AST OK')"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"AST parsing failed:\n{r.stderr[-500:]}"


def test_repo_check_copies():
    """Repo's check_copies.py utility passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_copies.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_copies.py failed:\n{r.stderr[-500:]}"


def test_repo_check_doc_toc():
    """Repo's check_doc_toc.py utility passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_doc_toc.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_doc_toc.py failed:\n{r.stderr[-500:]}"


def test_repo_check_doctest_list():
    """Repo's check_doctest_list.py utility passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_doctest_list.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_doctest_list.py failed:\n{r.stderr[-500:]}"


def test_repo_check_pipeline_typing():
    """Repo's check_pipeline_typing.py utility passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_pipeline_typing.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_pipeline_typing.py failed:\n{r.stderr[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_check_timestamps_verify_merge_commit_timestamp_is_older_t():
    """pass_to_pass | CI job 'Check timestamps' → step 'Verify `merge_commit` timestamp is older than the issue comment timestamp'"""
    r = subprocess.run(
        ["bash", "-lc", 'COMMENT_TIMESTAMP=$(date -d "${COMMENT_DATE}" +"%s")\necho "COMMENT_DATE: $COMMENT_DATE"\necho "COMMENT_TIMESTAMP: $COMMENT_TIMESTAMP"\nif [ $COMMENT_TIMESTAMP -le $PR_MERGE_COMMIT_TIMESTAMP ]; then\n  echo "Last commit on the pull request is newer than the issue comment triggering this run! Abort!";\n  exit -1;\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify `merge_commit` timestamp is older than the issue comment timestamp' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_get_tests_verify_merge_commit_sha():
    """pass_to_pass | CI job 'get-tests' → step 'Verify merge commit SHA'"""
    r = subprocess.run(
        ["bash", "-lc", 'PR_MERGE_SHA=$(git log -1 --format=%H)\nif [ $PR_MERGE_SHA != $VERIFIED_PR_MERGE_SHA ]; then\n  echo "The merged commit SHA is not the same as the verified one! Security issue detected, abort the workflow!";\n  exit -1;\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify merge commit SHA' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_get_tests_get_models_to_test():
    """pass_to_pass | CI job 'get-tests' → step 'Get models to test'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -m pip install GitPython'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Get models to test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_get_tests_show_models_to_test():
    """pass_to_pass | CI job 'get-tests' → step 'Show models to test'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "$models"\necho "models=$models" >> $GITHUB_OUTPUT\necho "$quantizations"\necho "quantizations=$quantizations" >> $GITHUB_OUTPUT'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show models to test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check___report_process_and_filter_reports():
    """pass_to_pass | CI job 'Check & Report' → step 'Process and filter reports'"""
    r = subprocess.run(
        ["bash", "-lc", "python3 << 'PYTHON_SCRIPT'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Process and filter reports' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")