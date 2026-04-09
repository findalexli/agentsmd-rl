"""
Task: sglang-npu-qwen35-video-processor
Repo: sglang @ 931dbceadc49eb36d6f76477e5666a03c7c641ca
PR:   22266

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
from pathlib import Path

import torch

REPO = "/workspace/sglang"
TARGET_FILE = f"{REPO}/python/sglang/srt/hardware_backend/npu/modules/qwen_vl_processor.py"


def _get_target_source():
    """Get the source code of the target file."""
    return Path(TARGET_FILE).read_text()


def _get_target_ast():
    """Get the AST of the target file."""
    src = _get_target_source()
    return ast.parse(src)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    src = _get_target_source()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_transform_patches_to_flatten_logic():
    """
    transform_patches_to_flatten must exist with correct signature and logic.

    This function is the key to decomposing >8D permute operations
    into multiple <=8D permutes for NPU compatibility.
    """
    tree = _get_target_ast()

    # Find the function
    func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "transform_patches_to_flatten":
            func = node
            break

    assert func is not None, "transform_patches_to_flatten function not found"

    # Check function signature has required parameters
    args = [arg.arg for arg in func.args.args]
    required_args = ['patches', 'batch_size', 'grid_t', 'temporal_patch_size',
                     'channel', 'grid_h', 'grid_w', 'patch_size', 'merge_size']
    for arg in required_args:
        assert arg in args, f"Required parameter '{arg}' not found in function signature"

    # Check function body contains view/permute/reshape operations
    src = _get_target_source()

    # Should have view operation
    assert "patches.view(" in src, "Function must use patches.view()"

    # Should have permute with exactly 8 dimensions (0,1,2,5,3,6,4,7)
    assert "patches.permute(0, 1, 2, 5, 3, 6, 4, 7)" in src, \
        "First permute must be exactly 8D: (0, 1, 2, 5, 3, 6, 4, 7)"

    # Should have reshape
    assert "patches.reshape(" in src, "Function must use patches.reshape()"

    # Should have second permute with 7 dimensions
    assert "patches.permute(0, 1, 4, 3, 2, 5, 6)" in src, \
        "Second permute must be exactly 7D: (0, 1, 4, 3, 2, 5, 6)"

    # Should return flatten_patches
    assert "return flatten_patches" in src, "Function must return flatten_patches"


# [pr_diff] fail_to_pass
def test_video_preprocess_wrapper_exists():
    """
    npu_wrapper_video_preprocess must exist as a proper wrapper function.

    This is the key fix for Qwen3VLVideoProcessor to work on NPU.
    """
    tree = _get_target_ast()

    # Find the function
    func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "npu_wrapper_video_preprocess":
            func = node
            break

    assert func is not None, "npu_wrapper_video_preprocess function not found"

    # Check it takes a 'func' parameter (wrapper pattern)
    args = [arg.arg for arg in func.args.args]
    assert "func" in args, "npu_wrapper_video_preprocess must take a 'func' parameter"

    # Check function body is substantial
    src = _get_target_source()

    # Should define an inner _preprocess function
    assert "def _preprocess(" in src, "Wrapper must define inner _preprocess function"

    # Should return _preprocess
    assert "return _preprocess" in src, "Wrapper must return _preprocess function"

    # Should use transform_patches_to_flatten
    assert "transform_patches_to_flatten(" in src, \
        "npu_wrapper_video_preprocess must call transform_patches_to_flatten"


# [pr_diff] fail_to_pass
def test_video_processor_patch_registered():
    """
    The npu_apply_qwen_image_preprocess_patch function must register the video patch.

    This ensures the fix is actually applied to the transformers module.
    """
    src = _get_target_source()

    # Check for apply_module_patch call with Qwen3VLVideoProcessor
    assert 'apply_module_patch(' in src, "Must call apply_module_patch"
    assert 'qwen3_vl.video_processing_qwen3_vl.Qwen3VLVideoProcessor' in src, \
        "Must patch transformers.models.qwen3_vl.video_processing_qwen3_vl.Qwen3VLVideoProcessor"
    assert '[npu_wrapper_video_preprocess]' in src, \
        "Must register npu_wrapper_video_preprocess wrapper"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified functions have real logic, not just pass/return."""
    tree = _get_target_ast()
    src = _get_target_source()

    # For transform_patches_to_flatten - check it has substantial body
    func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "transform_patches_to_flatten":
            func = node
            break

    assert func is not None, "transform_patches_to_flatten not found"

    # Count non-trivial statements
    stmts = []
    for s in func.body:
        if isinstance(s, ast.Pass):
            continue
        if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant):
            continue
        stmts.append(s)

    assert len(stmts) >= 5, \
        f"transform_patches_to_flatten has only {len(stmts)} statements, expected real implementation"

    # For npu_wrapper_video_preprocess - check it defines inner function with substantial body
    wrapper = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "npu_wrapper_video_preprocess":
            wrapper = node
            break

    assert wrapper is not None, "npu_wrapper_video_preprocess not found"

    # Check that it defines an inner _preprocess function
    inner_funcs = [n for n in ast.walk(wrapper) if isinstance(n, ast.FunctionDef) and n.name == "_preprocess"]
    assert len(inner_funcs) > 0, "npu_wrapper_video_preprocess must define inner _preprocess function"

    # Verify the wrapper calls transform_patches_to_flatten
    assert "transform_patches_to_flatten(" in src, \
        "npu_wrapper_video_preprocess must call transform_patches_to_flatten"


# [static] pass_to_pass
def test_function_decomposes_permute():
    """
    The fix must decompose >8D permute into <=8D permutes.

    This is the core requirement for NPU compatibility.
    """
    src = _get_target_source()

    # The function should use view/reshape to break up the dimensions
    # and use permute with at most 8 dimensions
    assert "patches.view(" in src
    assert "patches.permute(0, 1, 2, 5, 3, 6, 4, 7)" in src, \
        "First permute must be exactly 8D for NPU compatibility"
    assert "patches.reshape(" in src
    assert "patches.permute(0, 1, 4, 3, 2, 5, 6)" in src, \
        "Second permute must be exactly 7D (under 8D limit)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# No specific programmatic agent config rules apply to this hardware backend fix.
# The add-sgl-kernel skill focuses on CUDA kernel development, not NPU compatibility.
