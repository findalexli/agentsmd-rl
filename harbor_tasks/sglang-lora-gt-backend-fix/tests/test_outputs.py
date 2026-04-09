"""
Task: sglang-lora-gt-backend-fix
Repo: sglang @ 41c7c97ff30a8f5e969cefc3efac57f0f3fdbb64
PR:   22157

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This task tests the fix for LoRA cases in GT (ground truth) generation mode:
1. LoRA cases should NOT be forced to --backend diffusers in GT mode
2. Dynamic LoRA loading should run in GT mode (not be skipped)
"""

import ast
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = "/workspace/sglang"
TARGET_FILE = "python/sglang/multimodal_gen/test/server/test_server_common.py"


def _get_target_file_content():
    """Read the target file content."""
    return Path(f"{REPO}/{TARGET_FILE}").read_text()


def _parse_target_file():
    """Parse the target file into an AST."""
    content = _get_target_file_content()
    return ast.parse(content)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified file must parse without errors."""
    try:
        _parse_target_file()
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in {TARGET_FILE}: {e}")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_is_lora_case_function_exists():
    """The _is_lora_case helper function must exist."""
    content = _get_target_file_content()
    tree = _parse_target_file()

    # Find the function definition
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_is_lora_case":
            found = True
            break

    assert found, "_is_lora_case function not found in the file"


def test_is_lora_case_checks_all_lora_paths():
    """_is_lora_case must check lora_path, dynamic_lora_path, and second_lora_path."""
    content = _get_target_file_content()
    tree = _parse_target_file()

    # Find the function and check its body
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_is_lora_case":
            func_source = ast.unparse(node)
            assert "lora_path" in func_source, "_is_lora_case must check lora_path"
            assert "dynamic_lora_path" in func_source, "_is_lora_case must check dynamic_lora_path"
            assert "second_lora_path" in func_source, "_is_lora_case must check second_lora_path"
            return

    raise AssertionError("_is_lora_case function not found")


def test_lora_case_skips_forced_diffusers():
    """In GT mode, LoRA cases should NOT be forced to --backend diffusers."""
    content = _get_target_file_content()

    # Find the GT mode backend selection logic
    # The fix adds: "if not _is_lora_case(case) and \"--backend\" not in extra_args:"
    # The old code was: "if \"--backend\" not in extra_args:"

    # Look for the pattern that includes _is_lora_case check
    assert "not _is_lora_case(case)" in content, \
        "GT mode backend selection must check _is_lora_case to skip LoRA cases"

    # Make sure the pattern is in the right context (after SGLANG_GEN_GT check)
    lines = content.split('\n')
    in_gt_block = False
    found_proper_check = False

    for i, line in enumerate(lines):
        if 'SGLANG_GEN_GT' in line and '== "1"' in line:
            in_gt_block = True
        if in_gt_block and 'not _is_lora_case(case)' in line:
            found_proper_check = True
            break
        if in_gt_block and line.strip() and not line.strip().startswith('#') and 'if' not in line:
            # We've moved past the GT block
            in_gt_block = False

    assert found_proper_check, "_is_lora_case check must be in the GT mode block"


def test_dynamic_lora_runs_in_gt_mode():
    """Dynamic LoRA loading should NOT be skipped in GT mode."""
    content = _get_target_file_content()

    # The old code had: "if case.run_lora_dynamic_load_check and not is_gt_gen_mode:"
    # The fix removes the "and not is_gt_gen_mode" check

    # Check that the NOT GT mode check is removed
    bad_pattern = "run_lora_dynamic_load_check and not is_gt_gen_mode"
    assert bad_pattern not in content, \
        "Dynamic LoRA loading should NOT be gated by 'not is_gt_gen_mode'"

    # Verify the corrected pattern exists
    good_pattern = "if case.run_lora_dynamic_load_check:"
    assert good_pattern in content, \
        "Dynamic LoRA loading should check only run_lora_dynamic_load_check"


def test_gt_comment_updated():
    """The comment about GT mode must reflect the LoRA exception."""
    content = _get_target_file_content()

    # Look for the updated comment near the GT backend logic
    lines = content.split('\n')

    for i, line in enumerate(lines):
        if 'Keep LoRA GT on the normal backend' in line or \
           'LoRA GT on the normal backend path' in line:
            return

    # Check that the old misleading comment is not present
    assert "In GT generation mode, force --backend diffusers" not in content, \
        "Old misleading comment must be updated to reflect LoRA exception"


def test_dynamic_lora_comment_updated():
    """The comment for dynamic LoRA must reflect GT mode support."""
    content = _get_target_file_content()

    # Check for updated comment about GT generation needing set_lora
    assert "GT generation also needs the dynamic set_lora step" in content or \
           "GT generation also needs" in content, \
        "Comment should indicate that GT mode needs dynamic LoRA loading"
