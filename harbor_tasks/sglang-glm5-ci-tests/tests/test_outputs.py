"""
Task: sglang-glm5-ci-tests
Repo: sgl-project/sglang @ c3c13dd5e3b42850d5a96adca4092deb72bf1e4a
PR:   22285

This task adds CI tests for the GLM-5 model. Since the tests require 8 GPUs
and actual model weights to run, we verify the structural changes:
1. Test files are renamed correctly (test_deepseek_v32_* -> test_dsa_models_*)
2. New GLM5 test classes are added with correct structure
3. Code changes are syntactically valid
4. Configuration changes (est_time, env vars) are applied correctly

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import py_compile
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"

# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_basic_file_syntax():
    """The renamed test_dsa_models_basic.py must compile without errors."""
    basic_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")
    assert basic_file.exists(), f"File not found: {basic_file}"
    py_compile.compile(str(basic_file), doraise=True)


# [static] pass_to_pass
def test_mtp_file_syntax():
    """The renamed test_dsa_models_mtp.py must compile without errors."""
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")
    assert mtp_file.exists(), f"File not found: {mtp_file}"
    py_compile.compile(str(mtp_file), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_glm5_model_path_constant_exists():
    """GLM5_MODEL_PATH constant must be defined in both test files."""
    basic_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")

    expected = 'GLM5_MODEL_PATH = "zai-org/GLM-5-FP8"'

    basic_content = basic_file.read_text()
    mtp_content = mtp_file.read_text()

    assert expected in basic_content, f"GLM5_MODEL_PATH not found in basic test file"
    assert expected in mtp_content, f"GLM5_MODEL_PATH not found in mtp test file"


# [pr_diff] fail_to_pass
def test_glm5_test_classes_exist():
    """GLM5 test classes must be defined in both test files."""
    basic_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")

    basic_tree = ast.parse(basic_file.read_text())
    mtp_tree = ast.parse(mtp_file.read_text())

    basic_classes = [
        node.name for node in ast.walk(basic_tree)
        if isinstance(node, ast.ClassDef)
    ]
    mtp_classes = [
        node.name for node in ast.walk(mtp_tree)
        if isinstance(node, ast.ClassDef)
    ]

    # Basic file should have: TestDeepseekV32DP, TestDeepseekV32TP, TestGLM5DP, TestGLM5TP
    assert "TestGLM5DP" in basic_classes, "TestGLM5DP class not found in basic test file"
    assert "TestGLM5TP" in basic_classes, "TestGLM5TP class not found in basic test file"

    # MTP file should have: TestDeepseekV32DPMTP, TestDeepseekV32TPMTP, TestGLM5DPMTP, TestGLM5TPMTP
    assert "TestGLM5DPMTP" in mtp_classes, "TestGLM5DPMTP class not found in mtp test file"
    assert "TestGLM5TPMTP" in mtp_classes, "TestGLM5TPMTP class not found in mtp test file"


# [pr_diff] fail_to_pass
def test_est_time_updated():
    """register_cuda_ci est_time must be updated from 360 to 720 in basic test."""
    basic_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")
    content = basic_file.read_text()

    # Should have est_time=720, not 360
    assert 'register_cuda_ci(est_time=720' in content, "est_time not updated to 720 in basic test"
    assert 'register_cuda_ci(est_time=360' not in content, "Old est_time=360 still present in basic test"


# [pr_diff] fail_to_pass
def test_mtp_env_override_added():
    """SGLANG_ENABLE_SPEC_V2 environment override must wrap server launch in MTP tests."""
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")
    content = mtp_file.read_text()

    # Check for envs.SGLANG_ENABLE_SPEC_V2.override(True) wrapping
    assert "envs.SGLANG_ENABLE_SPEC_V2.override(True)" in content, \
        "SGLANG_ENABLE_SPEC_V2 override not found in MTP tests"


# [pr_diff] fail_to_pass
def test_mtp_class_renamed_correctly():
    """TestDeepseekV32DPMTPV2 must be renamed to TestDeepseekV32TPMTP."""
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")
    content = mtp_file.read_text()

    # New name should exist
    assert "class TestDeepseekV32TPMTP" in content, "TestDeepseekV32TPMTP class not found"
    # Old name should NOT exist
    assert "class TestDeepseekV32DPMTPV2" not in content, "Old TestDeepseekV32DPMTPV2 class still exists"


# [pr_diff] fail_to_pass
def test_mtp_mem_frac_updated():
    """mem-frac should be updated from 0.7 to 0.8 in GLM5 tests."""
    mtp_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")
    content = mtp_file.read_text()

    # Count occurrences of 0.8 for mem-frac (should appear twice for GLM5 tests)
    # The DeepSeek tests keep 0.7, only GLM5 tests use 0.8
    assert '"0.8"' in content, 'mem-frac "0.8" not found in MTP tests'


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_old_files_removed():
    """Old test file names should not exist (they were renamed)."""
    old_basic = Path(f"{REPO}/test/registered/8-gpu-models/test_deepseek_v32_basic.py")
    old_mtp = Path(f"{REPO}/test/registered/8-gpu-models/test_deepseek_v32_mtp.py")

    assert not old_basic.exists(), "Old test_deepseek_v32_basic.py should not exist (renamed)"
    assert not old_mtp.exists(), "Old test_deepseek_v32_mtp.py should not exist (renamed)"


# [static] pass_to_pass
def test_new_files_exist():
    """New test file names should exist."""
    new_basic = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")
    new_mtp = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_mtp.py")

    assert new_basic.exists(), "New test_dsa_models_basic.py should exist"
    assert new_mtp.exists(), "New test_dsa_models_mtp.py should exist"


# [static] pass_to_pass
def test_glm5_classes_have_required_methods():
    """GLM5 test classes must have setUpClass, tearDownClass, and test methods."""
    basic_file = Path(f"{REPO}/test/registered/8-gpu-models/test_dsa_models_basic.py")
    tree = ast.parse(basic_file.read_text())

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.startswith("TestGLM5"):
            methods = [
                n.name for n in ast.walk(node)
                if isinstance(n, ast.FunctionDef)
            ]
            assert "setUpClass" in methods, f"{node.name} missing setUpClass"
            assert "tearDownClass" in methods, f"{node.name} missing tearDownClass"
            # Should have test methods
            test_methods = [m for m in methods if m.startswith("test_")]
            assert len(test_methods) >= 1, f"{node.name} has no test methods"
