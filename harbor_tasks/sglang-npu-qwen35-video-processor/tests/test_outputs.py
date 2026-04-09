"""
Task: sglang-npu-qwen35-video-processor
Repo: sglang @ 931dbceadc49eb36d6f76477e5666a03c7c641ca
PR:   22266

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

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
    transform_patches_to_flatten correctly reshapes and permutes patches for NPU compatibility.

    This function is the key to decomposing >8D permute operations
    into multiple <=8D permutes for NPU compatibility.
    """
    # Execute Python code that imports and tests the function with real tensors
    code = """
import sys
sys.path.insert(0, '/workspace/sglang/python')

import torch

# Import the function from the target module
from sglang.srt.hardware_backend.npu.modules.qwen_vl_processor import transform_patches_to_flatten

# Create test input: patches tensor simulating video data
# Shape: (batch_size, grid_t * temporal_patch_size, channel, grid_h * patch_size, grid_w * patch_size)
batch_size = 2
grid_t = 3
temporal_patch_size = 2
channel = 3
grid_h = 4
grid_w = 4
patch_size = 14
merge_size = 2

# Create patches tensor with appropriate shape
patches = torch.randn(
    batch_size,
    grid_t * temporal_patch_size,
    channel,
    grid_h * patch_size,
    grid_w * patch_size
)

# Call the function under test
result = transform_patches_to_flatten(
    patches,
    batch_size,
    grid_t,
    temporal_patch_size,
    channel,
    grid_h,
    grid_w,
    patch_size,
    merge_size,
)

# Verify output shape: (batch_size, grid_t * grid_h * grid_w, -1)
expected_first_dim = batch_size
expected_second_dim = grid_t * grid_h * grid_w

assert result.shape[0] == expected_first_dim, f"First dim should be {expected_first_dim}, got {result.shape[0]}"
assert result.shape[1] == expected_second_dim, f"Second dim should be {expected_second_dim}, got {result.shape[1]}"

# Verify the transformation is mathematically equivalent to manual computation
# Manual computation following the original pattern (but decomposed)
manual_patches = patches.view(
    batch_size * grid_t,
    temporal_patch_size * channel,
    grid_h // merge_size,
    merge_size,
    patch_size,
    grid_w // merge_size,
    merge_size,
    patch_size,
)
manual_patches = manual_patches.permute(0, 1, 2, 5, 3, 6, 4, 7)
manual_patches = manual_patches.reshape(
    batch_size,
    grid_t,
    temporal_patch_size,
    channel,
    grid_h * grid_w,
    patch_size,
    patch_size,
)
manual_patches = manual_patches.permute(0, 1, 4, 3, 2, 5, 6)
manual_flatten = manual_patches.reshape(batch_size, grid_t * grid_h * grid_w, -1)

# Results should be identical
assert torch.allclose(result, manual_flatten), "transform_patches_to_flatten output differs from manual computation"

print("PASS: transform_patches_to_flatten works correctly")
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output, got: {result.stdout}"


# [pr_diff] fail_to_pass
def test_video_preprocess_wrapper_exists():
    """
    npu_wrapper_video_preprocess wrapper exists for Qwen3VLVideoProcessor NPU support.

    This is the key fix for Qwen3VLVideoProcessor to work on NPU.
    """
    code = """
import sys
sys.path.insert(0, '/workspace/sglang/python')

# Import the function - this will fail if it doesn't exist
from sglang.srt.hardware_backend.npu.modules.qwen_vl_processor import npu_wrapper_video_preprocess

# Verify it's callable
assert callable(npu_wrapper_video_preprocess), "npu_wrapper_video_preprocess should be callable"

# Check function signature by inspecting it
import inspect
sig = inspect.signature(npu_wrapper_video_preprocess)
params = list(sig.parameters.keys())
assert 'func' in params, "npu_wrapper_video_preprocess must take a 'func' parameter"

# Call it with a mock function to verify it returns an inner function
def mock_func():
    pass

inner = npu_wrapper_video_preprocess(mock_func)
assert callable(inner), "npu_wrapper_video_preprocess must return a callable (_preprocess)"

# Check that the returned function has the right signature
inner_sig = inspect.signature(inner)
inner_params = list(inner_sig.parameters.keys())
expected_params = [
    'self', 'videos', 'do_convert_rgb', 'do_resize', 'size',
    'interpolation', 'do_rescale', 'rescale_factor', 'do_normalize',
    'image_mean', 'image_std', 'patch_size', 'temporal_patch_size',
    'merge_size', 'return_tensors'
]
for param in expected_params:
    assert param in inner_params, f"Inner function missing parameter: {param}"

print("PASS: npu_wrapper_video_preprocess exists and has correct structure")
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output, got: {result.stdout}"


# [pr_diff] fail_to_pass
def test_video_processor_patch_registered():
    """
    npu_apply_qwen_image_preprocess_patch registers the Qwen3VLVideoProcessor patch.

    This ensures the fix is actually applied to the transformers module.
    """
    code = """
import sys
sys.path.insert(0, '/workspace/sglang/python')

# Import the patch function
from sglang.srt.hardware_backend.npu.modules.qwen_vl_processor import npu_apply_qwen_image_preprocess_patch

# Read the source file to verify the patch registration
import inspect
source = inspect.getsource(npu_apply_qwen_image_preprocess_patch)

# Check that it contains the Qwen3VLVideoProcessor patch
assert 'qwen3_vl.video_processing_qwen3_vl.Qwen3VLVideoProcessor' in source, \
    "Patch must register for Qwen3VLVideoProcessor"
assert 'npu_wrapper_video_preprocess' in source, \
    "Patch must use npu_wrapper_video_preprocess wrapper"
assert 'apply_module_patch' in source, \
    "Patch function must call apply_module_patch"

print("PASS: Video processor patch is properly registered")
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output, got: {result.stdout}"


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


# [repo_tests] pass_to_pass - optional: run repo's own tests if they exist and are fast
def test_module_imports():
    """
    The modified module can be imported without errors.

    This is a basic pass-to-pass gate to ensure no import regressions.
    """
    code = """
import sys
sys.path.insert(0, '/workspace/sglang/python')

# Try importing the module - this exercises all imports in the file
from sglang.srt.hardware_backend.npu.modules.qwen_vl_processor import (
    transform_patches_to_flatten,
    npu_wrapper_preprocess,
    npu_wrapper_video_preprocess,
    npu_apply_qwen_image_preprocess_patch,
)

print("PASS: All imports work correctly")
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output, got: {result.stdout}"


# [repo_tests] pass_to_pass - ruff lint check
def test_repo_ruff():
    """
    Repo lint check: ruff F401/F821 checks pass on modified module.

    This ensures no unused imports or undefined names in the modified file.
    Uses the repo's pre-commit style ruff configuration.
    """
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        cwd=REPO,
    )

    r = subprocess.run(
        ["ruff", "check", TARGET_FILE, "--select=F401,F821"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - black formatting check
def test_repo_black():
    """
    Repo format check: black formatting passes on modified module.

    This ensures the modified code follows the repo's formatting standards.
    """
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "black", "-q"],
        capture_output=True,
        cwd=REPO,
    )

    r = subprocess.run(
        ["black", "--check", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Black check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# No specific programmatic agent config rules apply to this hardware backend fix.
# The add-sgl-kernel skill focuses on CUDA kernel development, not NPU compatibility.
