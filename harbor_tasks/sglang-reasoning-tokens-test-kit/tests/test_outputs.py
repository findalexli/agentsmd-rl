"""
Task: sglang-reasoning-tokens-test-kit
Repo: sglang @ bb9e058f5b9d4754ac2965bb36864fee1cd978e8
PR:   22102

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import importlib.machinery
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------

def test_reasoning_tokens_kit_syntax():
    """reasoning_tokens_kit module must be valid Python with ReasoningTokenUsageMixin."""
    kit_path = Path(f"{REPO}/python/sglang/test/kits/reasoning_tokens_kit.py")
    assert kit_path.exists(), "reasoning_tokens_kit.py does not exist"
    src = kit_path.read_text()
    tree = ast.parse(src)
    # Find ReasoningTokenUsageMixin class
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ReasoningTokenUsageMixin":
            found = True
            break
    assert found, "ReasoningTokenUsageMixin class not found in kit"


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
    assert r.returncode == 0, f"check-ast failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_yaml():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-yaml")
    assert r.returncode == 0, f"check-yaml failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_toml():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-toml")
    assert r.returncode == 0, f"check-toml failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_ruff():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("ruff")
    assert r.returncode == 0, f"ruff failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_isort():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("isort")
    assert r.returncode == 0, f"isort failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_codespell():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("codespell")
    assert r.returncode == 0, f"codespell failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_black_jupyter():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("black-jupyter")
    assert r.returncode == 0, f"black-jupyter failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_workflow_jobs():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-workflow-job-names")
    assert r.returncode == 0, f"check-workflow-job-names failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_sort_ci_permissions():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("sort-ci-permissions")
    assert r.returncode == 0, f"sort-ci-permissions failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_symlinks():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-symlinks")
    assert r.returncode == 0, f"check-symlinks failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_destroyed_symlinks():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("destroyed-symlinks")
    assert r.returncode == 0, f"destroyed-symlinks failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_trailing_whitespace():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("trailing-whitespace")
    assert r.returncode == 0, f"trailing-whitespace failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_end_of_file_fixer():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("end-of-file-fixer")
    assert r.returncode == 0, f"end-of-file-fixer failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_added_large_files():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-added-large-files")
    assert r.returncode == 0, f"check-added-large-files failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_merge_conflict():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-merge-conflict")
    assert r.returncode == 0, f"check-merge-conflict failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_check_shebang_scripts():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("check-shebang-scripts-are-executable")
    assert r.returncode == 0, f"check-shebang-scripts-are-executable failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_detect_private_key():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("detect-private-key")
    assert r.returncode == 0, f"detect-private-key failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_precommit_debug_statements():
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = _run_precommit_hook("debug-statements")
    assert r.returncode == 0, f"debug-statements failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core structural tests
# ---------------------------------------------------------------------------

def test_reasoning_tokens_kit_exists():
    """reasoning_tokens_kit.py must exist with ReasoningTokenUsageMixin class."""
    kit_path = Path(f"{REPO}/python/sglang/test/kits/reasoning_tokens_kit.py")
    assert kit_path.exists(), "reasoning_tokens_kit.py does not exist"
    src = kit_path.read_text()
    tree = ast.parse(src)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ReasoningTokenUsageMixin":
            found = True
            break
    assert found, "ReasoningTokenUsageMixin class not found in kit"


def test_mixin_has_required_methods():
    """ReasoningTokenUsageMixin must have all 5 test methods."""
    kit_path = Path(f"{REPO}/python/sglang/test/kits/reasoning_tokens_kit.py")
    assert kit_path.exists(), "reasoning_tokens_kit.py does not exist"
    src = kit_path.read_text()
    tree = ast.parse(src)
    
    required_methods = [
        "test_reasoning_tokens_thinking",
        "test_reasoning_tokens_non_thinking",
        "test_reasoning_tokens_thinking_stream",
        "test_reasoning_tokens_non_thinking_stream",
        "test_reasoning_tokens_generate_exact_count",
    ]
    
    found_methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ReasoningTokenUsageMixin":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in required_methods:
                    found_methods.add(item.name)
    
    missing = set(required_methods) - found_methods
    assert not missing, f"Missing methods in mixin: {missing}"


def test_mixin_has_init_reasoning_token_verifier():
    """Mixin must have init_reasoning_token_verifier as a classmethod."""
    kit_path = Path(f"{REPO}/python/sglang/test/kits/reasoning_tokens_kit.py")
    assert kit_path.exists(), "reasoning_tokens_kit.py does not exist"
    src = kit_path.read_text()
    tree = ast.parse(src)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ReasoningTokenUsageMixin":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "init_reasoning_token_verifier":
                    # Check it's a classmethod
                    for d in item.decorator_list:
                        if isinstance(d, ast.Name) and d.id == "classmethod":
                            return
                        elif isinstance(d, ast.Attribute) and d.attr == "classmethod":
                            return
    
    assert False, "init_reasoning_token_verifier classmethod not found in mixin"


def _load_module_from_path(name, path):
    """Load a Python module directly from a file path, bypassing package init."""
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    # Don't exec_module - just set the attribute so ast.parse works on the source
    return mod


def test_enable_thinking_imports_mixin():
    """TestEnableThinking must inherit from ReasoningTokenUsageMixin."""
    test_path = Path(f"{REPO}/test/registered/openai_server/features/test_enable_thinking.py")
    assert test_path.exists(), "test_enable_thinking.py does not exist"
    
    src = test_path.read_text()
    tree = ast.parse(src)
    
    # Find ReasoningTokenUsageMixin import
    mixin_imported = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "reasoning_tokens_kit" in node.module:
                for alias in node.names:
                    if alias.name == "ReasoningTokenUsageMixin":
                        mixin_imported = True
                        break
    
    assert mixin_imported, "ReasoningTokenUsageMixin not imported in test_enable_thinking.py"
    
    # Find TestEnableThinking and check its bases
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestEnableThinking":
            bases = []
            for b in node.bases:
                if isinstance(b, ast.Name):
                    bases.append(b.id)
                elif isinstance(b, ast.Attribute):
                    # Handle something.something
                    if isinstance(b.value, ast.Name):
                        bases.append(f"{b.value.id}.{b.attr}")
            
            assert "ReasoningTokenUsageMixin" in bases, \
                "TestEnableThinking does not inherit from ReasoningTokenUsageMixin"
            return
    
    assert False, "TestEnableThinking class not found"


def test_enable_thinking_sets_reasoning_parser():
    """TestEnableThinking must have reasoning_parser_name = 'qwen3'."""
    test_path = Path(f"{REPO}/test/registered/openai_server/features/test_enable_thinking.py")
    assert test_path.exists(), "test_enable_thinking.py does not exist"
    
    src = test_path.read_text()
    tree = ast.parse(src)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestEnableThinking":
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "reasoning_parser_name":
                            if isinstance(item.value, ast.Constant) and item.value.value == "qwen3":
                                return
    
    assert False, "reasoning_parser_name = 'qwen3' not found in TestEnableThinking"


def test_qwen35_mtp_imports_mixin():
    """TestQwen35FP4MTP must inherit from ReasoningTokenUsageMixin."""
    test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
    assert test_path.exists(), "test_qwen35_models.py does not exist"
    
    src = test_path.read_text()
    tree = ast.parse(src)
    
    # Find ReasoningTokenUsageMixin import
    mixin_imported = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "reasoning_tokens_kit" in node.module:
                for alias in node.names:
                    if alias.name == "ReasoningTokenUsageMixin":
                        mixin_imported = True
                        break
    
    assert mixin_imported, "ReasoningTokenUsageMixin not imported in test_qwen35_models.py"
    
    # Find TestQwen35FP4MTP
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestQwen35FP4MTP":
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            assert "ReasoningTokenUsageMixin" in bases, \
                "TestQwen35FP4MTP does not inherit from ReasoningTokenUsageMixin"
            return
    
    assert False, "TestQwen35FP4MTP class not found"


def test_qwen35_mtpv2_imports_mixin():
    """TestQwen35FP4MTPV2 must inherit from ReasoningTokenUsageMixin."""
    test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
    assert test_path.exists(), "test_qwen35_models.py does not exist"
    
    src = test_path.read_text()
    tree = ast.parse(src)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestQwen35FP4MTPV2":
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            assert "ReasoningTokenUsageMixin" in bases, \
                "TestQwen35FP4MTPV2 does not inherit from ReasoningTokenUsageMixin"
            return
    
    assert False, "TestQwen35FP4MTPV2 class not found"


def test_qwen35_fp4_uses_custom_test_case():
    """TestQwen35FP4 must use CustomTestCase, not unittest.TestCase."""
    test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
    assert test_path.exists(), "test_qwen35_models.py does not exist"
    
    src = test_path.read_text()
    tree = ast.parse(src)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestQwen35FP4":
            bases = []
            for b in node.bases:
                if isinstance(b, ast.Name):
                    bases.append(b.id)
                elif isinstance(b, ast.Attribute):
                    if isinstance(b.value, ast.Name):
                        bases.append(f"{b.value.id}.{b.attr}")
            
            assert "unittest.TestCase" not in bases, \
                "TestQwen35FP4 still inherits from unittest.TestCase"
            assert "CustomTestCase" in bases, \
                "TestQwen35FP4 does not inherit from CustomTestCase"
            return
    
    assert False, "TestQwen35FP4 class not found"


def test_old_reasoning_usage_tokens_deleted():
    """The old standalone test_reasoning_usage_tokens.py must be deleted."""
    old_test_path = Path(f"{REPO}/test/registered/openai_server/features/test_reasoning_usage_tokens.py")
    assert not old_test_path.exists(), \
        "Old test_reasoning_usage_tokens.py should be deleted but still exists"


def test_enable_thinking_calls_init_verifier():
    """TestEnableThinking.setUpClass must call init_reasoning_token_verifier."""
    test_path = Path(f"{REPO}/test/registered/openai_server/features/test_enable_thinking.py")
    assert test_path.exists(), "test_enable_thinking.py does not exist"
    
    src = test_path.read_text()
    
    assert "cls.init_reasoning_token_verifier()" in src or \
           "self.init_reasoning_token_verifier()" in src, \
        "init_reasoning_token_verifier() call not found in TestEnableThinking"


def test_qwen35_mtp_calls_init_verifier():
    """TestQwen35FP4MTP.setUpClass must call init_reasoning_token_verifier."""
    test_path = Path(f"{REPO}/test/registered/4-gpu-models/test_qwen35_models.py")
    assert test_path.exists(), "test_qwen35_models.py does not exist"
    
    src = test_path.read_text()
    
    assert "cls.init_reasoning_token_verifier()" in src or \
           "self.init_reasoning_token_verifier()" in src, \
        "init_reasoning_token_verifier() not called in TestQwen35FP4MTP.setUpClass"

# === CI-mined test (taskforge.ci_check_miner) ===
def test_ci_precommit_ruff():
    """pass_to_pass | Run ruff via pre-commit as a real CI tool (bash -lc form)"""
    r = subprocess.run(["pip", "install", "pre-commit", "-q"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Failed to install pre-commit: {r.stderr[-500:]}"
    r = subprocess.run(
        ["bash", "-lc", "cd /workspace/sglang && SKIP='no-commit-to-branch,lychee,clang-format,mirrors-clang-format,nbstripout' pre-commit run ruff --all-files"],
        capture_output=True, text=True, timeout=300, env=os.environ,
    )
    assert r.returncode == 0, f"ruff (bash -lc) failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_test_reasoning_tokens_thinking():
    """fail_to_pass | PR added test 'test_reasoning_tokens_thinking' in 'python/sglang/test/kits/reasoning_tokens_kit.py' (pytest)"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m pytest -x --no-header -p no:cacheprovider "python/sglang/test/kits/reasoning_tokens_kit.py::test_reasoning_tokens_thinking" 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'test_reasoning_tokens_thinking' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_test_reasoning_tokens_non_thinking():
    """fail_to_pass | PR added test 'test_reasoning_tokens_non_thinking' in 'python/sglang/test/kits/reasoning_tokens_kit.py' (pytest)"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m pytest -x --no-header -p no:cacheprovider "python/sglang/test/kits/reasoning_tokens_kit.py::test_reasoning_tokens_non_thinking" 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'test_reasoning_tokens_non_thinking' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_test_reasoning_tokens_thinking_stream():
    """fail_to_pass | PR added test 'test_reasoning_tokens_thinking_stream' in 'python/sglang/test/kits/reasoning_tokens_kit.py' (pytest)"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m pytest -x --no-header -p no:cacheprovider "python/sglang/test/kits/reasoning_tokens_kit.py::test_reasoning_tokens_thinking_stream" 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'test_reasoning_tokens_thinking_stream' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_test_reasoning_tokens_non_thinking_stream():
    """fail_to_pass | PR added test 'test_reasoning_tokens_non_thinking_stream' in 'python/sglang/test/kits/reasoning_tokens_kit.py' (pytest)"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m pytest -x --no-header -p no:cacheprovider "python/sglang/test/kits/reasoning_tokens_kit.py::test_reasoning_tokens_non_thinking_stream" 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'test_reasoning_tokens_non_thinking_stream' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_test_reasoning_tokens_generate_exact_count():
    """fail_to_pass | PR added test 'test_reasoning_tokens_generate_exact_count' in 'python/sglang/test/kits/reasoning_tokens_kit.py' (pytest)"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m pytest -x --no-header -p no:cacheprovider "python/sglang/test/kits/reasoning_tokens_kit.py::test_reasoning_tokens_generate_exact_count" 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'test_reasoning_tokens_generate_exact_count' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_stage_b_test_16_npu_a3_run_test():
    """pass_to_pass | CI job 'stage-b-test-16-npu-a3' → step 'Run test'"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 run_suite.py --hw npu --suite stage-b-test-16-npu-a3 --timeout-per-file 3600'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_stage_b_test_4_npu_a3_run_test():
    """pass_to_pass | CI job 'stage-b-test-4-npu-a3' → step 'Run test'"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 run_suite.py --hw npu --suite stage-b-test-4-npu-a3 --timeout-per-file 3600'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_stage_a_test_1_gpu_small_amd_start_ci_container():
    """pass_to_pass | CI job 'stage-a-test-1-gpu-small-amd' → step 'Start CI container'"""
    r = subprocess.run(
        ["bash", "-lc", 'bash scripts/ci/amd/amd_ci_start_container.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Start CI container' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")