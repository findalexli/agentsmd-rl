"""
Task: sglang-reasoning-tokens-test-kit
Repo: sglang @ bb9e058f5b9d4754ac2965bb36864fee1cd978e8
PR:   22102

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------

def test_reasoning_tokens_kit_syntax():
    """reasoning_tokens_kit module must be importable with a ReasoningTokenUsageMixin class."""
    sys.path.insert(0, f"{REPO}/python")
    try:
        from sglang.test.kits import reasoning_tokens_kit
        mixin_class = getattr(reasoning_tokens_kit, "ReasoningTokenUsageMixin", None)
        assert mixin_class is not None, "ReasoningTokenUsageMixin not found in reasoning_tokens_kit module"
    except ImportError as e:
        assert False, f"Failed to import reasoning_tokens_kit: {e}"
    finally:
        sys.path.pop(0)


def test_modified_files_syntax():
    """Modified test files must parse without errors."""
    files = [
        f"{REPO}/test/registered/openai_server/features/test_enable_thinking.py",
        f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py",
    ]
    for path_str in files:
        path = Path(path_str)
        if not path.exists():
            continue
        src = path.read_text()
        try:
            ast.parse(src)
        except SyntaxError as e:
            assert False, f"Syntax error in {path.name}: {e}"


def _run_precommit_hook(hook_id: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["SKIP"] = "no-commit-to-branch,lychee,clang-format,mirrors-clang-format,nbstripout"
    return subprocess.run(
        ["pre-commit", "run", hook_id, "--all-files"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )


def test_repo_precommit_check_ast():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-ast")
    assert r.returncode == 0, f"check-ast failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_yaml():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-yaml")
    assert r.returncode == 0, f"check-yaml failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_toml():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-toml")
    assert r.returncode == 0, f"check-toml failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_ruff():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("ruff")
    assert r.returncode == 0, f"ruff failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_isort():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("isort")
    assert r.returncode == 0, f"isort failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_codespell():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("codespell")
    assert r.returncode == 0, f"codespell failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_black_jupyter():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("black-jupyter")
    assert r.returncode == 0, f"black-jupyter failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_workflow_jobs():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-workflow-job-names")
    assert r.returncode == 0, f"check-workflow-job-names failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_sort_ci_permissions():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("sort-ci-permissions")
    assert r.returncode == 0, f"sort-ci-permissions failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_symlinks():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-symlinks")
    assert r.returncode == 0, f"check-symlinks failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_destroyed_symlinks():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("destroyed-symlinks")
    assert r.returncode == 0, f"destroyed-symlinks failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_trailing_whitespace():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("trailing-whitespace")
    assert r.returncode == 0, f"trailing-whitespace failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_end_of_file_fixer():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("end-of-file-fixer")
    assert r.returncode == 0, f"end-of-file-fixer failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_added_large_files():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-added-large-files")
    assert r.returncode == 0, f"check-added-large-files failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_merge_conflict():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-merge-conflict")
    assert r.returncode == 0, f"check-merge-conflict failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_shebang_scripts():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-shebang-scripts-are-executable")
    assert r.returncode == 0, f"check-shebang-scripts-are-executable failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_detect_private_key():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("detect-private-key")
    assert r.returncode == 0, f"detect-private-key failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_debug_statements():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("debug-statements")
    assert r.returncode == 0, f"debug-statements failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


def test_reasoning_tokens_kit_exists():
    sys.path.insert(0, f"{REPO}/python")
    try:
        from sglang.test.kits import reasoning_tokens_kit
        mixin_class = getattr(reasoning_tokens_kit, "ReasoningTokenUsageMixin", None)
        assert mixin_class is not None, "ReasoningTokenUsageMixin not found in reasoning_tokens_kit"
    except ImportError as e:
        assert False, f"Could not import reasoning_tokens_kit: {e}"
    finally:
        sys.path.pop(0)


def test_mixin_has_required_methods():
    sys.path.insert(0, f"{REPO}/python")
    try:
        from sglang.test.kits import reasoning_tokens_kit
        mixin_cls = getattr(reasoning_tokens_kit, "ReasoningTokenUsageMixin", None)
        assert mixin_cls is not None, "ReasoningTokenUsageMixin not found"
        required_methods = [
            "test_reasoning_tokens_thinking",
            "test_reasoning_tokens_non_thinking",
            "test_reasoning_tokens_thinking_stream",
            "test_reasoning_tokens_non_thinking_stream",
            "test_reasoning_tokens_generate_exact_count",
        ]
        for m in required_methods:
            assert hasattr(mixin_cls, m), f"Method {m} not found on ReasoningTokenUsageMixin"
    finally:
        sys.path.pop(0)


def test_mixin_has_init_reasoning_token_verifier():
    sys.path.insert(0, f"{REPO}/python")
    try:
        from sglang.test.kits import reasoning_tokens_kit
        mixin_cls = getattr(reasoning_tokens_kit, "ReasoningTokenUsageMixin", None)
        assert mixin_cls is not None, "ReasoningTokenUsageMixin not found"
        init_method = getattr(mixin_cls, "init_reasoning_token_verifier", None)
        assert init_method is not None, "init_reasoning_token_verifier not found"
        assert hasattr(init_method, "__self__"), "init_reasoning_token_verifier must be a classmethod"
    finally:
        sys.path.pop(0)


def test_enable_thinking_imports_mixin():
    test_path = Path(f"{REPO}/test/registered/openai_server/features/test_enable_thinking.py")
    assert test_path.exists(), "test_enable_thinking.py does not exist"
    sys.path.insert(0, f"{REPO}/python")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_enable_thinking", test_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        test_cls = getattr(mod, "TestEnableThinking", None)
        assert test_cls is not None, "TestEnableThinking class not found"
        from sglang.test.kits.reasoning_tokens_kit import ReasoningTokenUsageMixin
        assert issubclass(test_cls, ReasoningTokenUsageMixin),             "TestEnableThinking does not inherit from ReasoningTokenUsageMixin"
    finally:
        sys.path.pop(0)


def test_enable_thinking_sets_reasoning_parser():
    test_path = Path(f"{REPO}/test/registered/openai_server/features/test_enable_thinking.py")
    assert test_path.exists(), "test_enable_thinking.py does not exist"
    sys.path.insert(0, f"{REPO}/python")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_enable_thinking", test_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        test_cls = getattr(mod, "TestEnableThinking", None)
        assert test_cls is not None, "TestEnableThinking class not found"
        assert hasattr(test_cls, "reasoning_parser_name"),             "TestEnableThinking missing reasoning_parser_name attribute"
        assert test_cls.reasoning_parser_name == "qwen3",             f"reasoning_parser_name should be 'qwen3', got {test_cls.reasoning_parser_name!r}"
    finally:
        sys.path.pop(0)


def test_qwen35_mtp_imports_mixin():
    test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
    assert test_path.exists(), "test_qwen35_models.py does not exist"
    sys.path.insert(0, f"{REPO}/python")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_qwen35_models", test_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        test_cls = getattr(mod, "TestQwen35FP4MTP", None)
        assert test_cls is not None, "TestQwen35FP4MTP class not found"
        from sglang.test.kits.reasoning_tokens_kit import ReasoningTokenUsageMixin
        assert issubclass(test_cls, ReasoningTokenUsageMixin),             "TestQwen35FP4MTP does not inherit from ReasoningTokenUsageMixin"
    finally:
        sys.path.pop(0)


def test_qwen35_mtpv2_imports_mixin():
    test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
    assert test_path.exists(), "test_qwen35_models.py does not exist"
    sys.path.insert(0, f"{REPO}/python")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_qwen35_models", test_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        test_cls = getattr(mod, "TestQwen35FP4MTPV2", None)
        assert test_cls is not None, "TestQwen35FP4MTPV2 class not found"
        from sglang.test.kits.reasoning_tokens_kit import ReasoningTokenUsageMixin
        assert issubclass(test_cls, ReasoningTokenUsageMixin),             "TestQwen35FP4MTPV2 does not inherit from ReasoningTokenUsageMixin"
    finally:
        sys.path.pop(0)


def test_qwen35_fp4_uses_custom_test_case():
    test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
    assert test_path.exists(), "test_qwen35_models.py does not exist"
    sys.path.insert(0, f"{REPO}/python")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_qwen35_models", test_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        test_cls = getattr(mod, "TestQwen35FP4", None)
        assert test_cls is not None, "TestQwen35FP4 class not found"
        import unittest
        assert not issubclass(test_cls, unittest.TestCase),             "TestQwen35FP4 should not inherit from unittest.TestCase"
        from sglang.test.test_utils import CustomTestCase
        assert issubclass(test_cls, CustomTestCase),             "TestQwen35FP4 should inherit from CustomTestCase"
    finally:
        sys.path.pop(0)


def test_old_reasoning_usage_tokens_deleted():
    old_test_path = Path(f"{REPO}/test/registered/openai_server/features/test_reasoning_usage_tokens.py")
    assert not old_test_path.exists(),         "Old test_reasoning_usage_tokens.py should be deleted but still exists"


def test_enable_thinking_calls_init_verifier():
    sys.path.insert(0, f"{REPO}/python")
    try:
        test_path = Path(f"{REPO}/test/registered/openai_server/features/test_enable_thinking.py")
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_enable_thinking", test_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        test_cls = getattr(mod, "TestEnableThinking", None)
        assert test_cls is not None, "TestEnableThinking class not found"
        init_method = getattr(test_cls, "init_reasoning_token_verifier", None)
        assert init_method is not None, "init_reasoning_token_verifier not found on test class"
        from sglang.test.kits.reasoning_tokens_kit import ReasoningTokenUsageMixin
        assert hasattr(ReasoningTokenUsageMixin, "init_reasoning_token_verifier"),             "Mixin should have init_reasoning_token_verifier"
    finally:
        sys.path.pop(0)


def test_qwen35_mtp_calls_init_verifier():
    sys.path.insert(0, f"{REPO}/python")
    try:
        test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_qwen35_models", test_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        test_cls = getattr(mod, "TestQwen35FP4MTP", None)
        assert test_cls is not None, "TestQwen35FP4MTP class not found"
        init_method = getattr(test_cls, "init_reasoning_token_verifier", None)
        assert init_method is not None, "init_reasoning_token_verifier not found on test class"
        from sglang.test.kits.reasoning_tokens_kit import ReasoningTokenUsageMixin
        assert hasattr(ReasoningTokenUsageMixin, "init_reasoning_token_verifier"),             "Mixin should have init_reasoning_token_verifier"
    finally:
        sys.path.pop(0)
