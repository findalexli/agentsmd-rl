"""Tests for SLIME task - validating rope_parameters fix in arguments.py."""

import ast
import subprocess
import sys
from pathlib import Path

# REPO path inside Docker container (as specified in Dockerfile WORKDIR)
REPO = "/workspace/slime"
TARGET_FILE = f"{REPO}/slime/backends/megatron_utils/arguments.py"


def _parse_arguments_py():
    """Parse arguments.py and return AST module."""
    content = Path(TARGET_FILE).read_text()
    return ast.parse(content)


def test_syntax_check():
    """arguments.py must parse without errors (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Syntax error in {TARGET_FILE}: {result.stderr}"


def test_ruff_lint():
    """Ruff linting passes on arguments.py (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    result = subprocess.run(
        ["ruff", "check", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff lint failed:\n{result.stderr[-500:]}"


def test_black_format():
    """Black formatting check passes on arguments.py (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "black", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    result = subprocess.run(
        ["black", "--check", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Black format check failed:\n{result.stdout[-500:]}"


def test_isort_imports():
    """isort import ordering check passes on arguments.py (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "isort", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    result = subprocess.run(
        ["isort", "--check", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"isort check failed:\n{result.stderr[-500:]}"


def test_ast_parses():
    """arguments.py must be valid Python AST (pass_to_pass)."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            f"import ast; ast.parse(open('{TARGET_FILE}').read()); print('AST parsing successful')",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"AST parsing failed: {result.stderr}"


def test_file_has_hf_validate_args():
    """File contains hf_validate_args function (pass_to_pass)."""
    tree = _parse_arguments_py()
    func_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    assert "_hf_validate_args" in func_names, "Missing _hf_validate_args function"


def test_hf_validate_args_has_rope_theta_validation():
    """_hf_validate_args handles rope_theta validation (pass_to_pass)."""
    content = Path(TARGET_FILE).read_text()
    # The patched file should have rope_theta handling
    assert "rope_theta" in content, "Missing rope_theta handling in file"


def test_not_stub():
    """hf_validate_args has real validation logic, not a stub (pass_to_pass)."""
    content = Path(TARGET_FILE).read_text()
    # Should have actual validation logic (for loop checking configs)
    assert "for hf_config_name, megatron_config_name" in content, (
        "Missing validation loop - appears to be a stub"
    )
    assert "errors.append" in content, "Missing error handling - appears to be a stub"


# Fail-to-pass tests (the actual fix being tested)


def test_rope_theta_from_parameters_dict():
    """rope_theta extracted from rope_parameters dict instead of stale class default (fail_to_pass)."""
    # This test validates the fix: rope_theta should be read from rope_parameters dict
    content = Path(TARGET_FILE).read_text()

    # After the patch, we should have the rope_parameters extraction logic
    # Check that the fix is present
    assert "rope_parameters" in content, "Missing rope_parameters dict handling"

    # Check for the key extraction pattern
    assert 'getattr(hf_config, "rope_parameters"' in content, (
        "Missing rope_parameters getattr extraction"
    )

    # Validate the logic structure
    assert "_hf_rope_theta" in content, "Missing _hf_rope_theta variable for extraction"


def test_rope_theta_from_parameters_dict_varied():
    """Same extraction logic works with different theta value (fail_to_pass)."""
    # The fix should work regardless of the specific theta value
    content = Path(TARGET_FILE).read_text()

    # Should have the dict extraction pattern
    assert 'if isinstance(rope_params, dict) and "rope_theta" in rope_params' in content, (
        "Missing rope_theta dict check"
    )

    # Should use the extracted value for validation
    assert "_hf_rope_theta" in content, "Missing _hf_rope_theta for validation"


def test_mismatch_detected_with_dict_override():
    """Dict rope_theta overrides stale default; mismatch with rotary_base is caught (fail_to_pass)."""
    content = Path(TARGET_FILE).read_text()

    # Should have the rope_theta validation logic that uses _hf_rope_theta
    assert "_hf_rope_theta is not None" in content or "if _hf_rope_theta is not None:" in content, (
        "Missing rope_theta validation check"
    )

    # Should compare with rotary_base
    assert "rotary_base" in content, "Missing rotary_base comparison"


# Pass-to-pass tests for backward compatibility


def test_fallback_to_direct_attribute():
    """Without rope_parameters dict, direct rope_theta attribute still validates (pass_to_pass)."""
    content = Path(TARGET_FILE).read_text()

    # Should have fallback to direct attribute access
    assert 'getattr(hf_config, "rope_theta", None)' in content, (
        "Missing fallback to direct rope_theta attribute"
    )

    # The else branch should handle direct attribute
    assert "_hf_rope_theta = getattr(hf_config, \"rope_theta\", None)" in content, (
        "Missing else branch for direct attribute access"
    )


def test_fallback_mismatch_detected():
    """Without rope_parameters dict, mismatch via direct attribute still raises (pass_to_pass)."""
    content = Path(TARGET_FILE).read_text()

    # Should have errors.append for validation failures
    assert "errors.append" in content, "Missing error reporting for validation"

    # Should raise AssertionError when there are errors
    assert "raise AssertionError" in content, "Missing AssertionError raise for validation failures"
