"""
Task: prime-rl-dppo-kl-default-loss
Repo: PrimeIntellect-ai/prime-rl @ 27645f39ab6f1550b2990ba4c5bb47be7f35402e
PR:   2187

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/prime-rl"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    files = [
        "src/prime_rl/trainer/rl/loss.py",
        "src/prime_rl/configs/trainer.py",
        ".cursor/BUGBOT.md",  # Not Python, but checked separately
    ]
    for f in files:
        path = Path(REPO) / f
        if f.endswith(".py"):
            src = path.read_text()
            ast.parse(src)  # Will raise SyntaxError if invalid


# [static] pass_to_pass
def test_import_check():
    """Key modules can be imported without errors."""
    result = subprocess.run(
        ["python3", "-c", "from src.prime_rl.configs.trainer import DefaultLossConfig"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    # Allow import to fail due to missing deps, but not syntax errors
    # We just want to verify the config structure is parseable
    stderr = result.stderr.lower()
    assert "syntaxerror" not in stderr, f"Syntax error in configs: {result.stderr}"
    assert "indentationerror" not in stderr, f"Indentation error in configs: {result.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_config_fields_renamed():
    """Config fields must be renamed from ipo_mask_* to dppo_mask_*."""
    config_path = Path(REPO) / "src/prime_rl/configs/trainer.py"
    src = config_path.read_text()

    # Should have new field names
    assert "dppo_mask_low" in src, "dppo_mask_low field not found in DefaultLossConfig"
    assert "dppo_mask_high" in src, "dppo_mask_high field not found in DefaultLossConfig"

    # Should NOT have old field names
    assert "ipo_mask_low" not in src, "Old ipo_mask_low field still exists"
    assert "ipo_mask_high" not in src, "Old ipo_mask_high field still exists"


# [pr_diff] fail_to_pass
def test_loss_logic_updated():
    """Loss function must use new dppo_mask variables with advantage-based masking."""
    loss_path = Path(REPO) / "src/prime_rl/trainer/rl/loss.py"
    src = loss_path.read_text()

    # Should use new variable names
    assert "dppo_invalid_mask_high" in src, "dppo_invalid_mask_high not found"
    assert "dppo_invalid_mask_low" in src, "dppo_invalid_mask_low not found"
    assert "dppo_invalid_mask" in src, "dppo_invalid_mask not found"

    # Should NOT have old variable names
    assert "ipo_invalid_mask_high" not in src, "Old ipo_invalid_mask_high still exists"
    assert "ipo_invalid_mask_low" not in src, "Old ipo_invalid_mask_low still exists"
    assert "ipo_invalid_mask" not in src, "Old ipo_invalid_mask still exists"

    # Should have advantage-based masking (the key behavioral change)
    assert "torch.where(advantages > 0" in src, "Advantage-based masking not implemented"
    assert "(advantages > 0) & dppo_invalid_mask_high" in src, "High mask not conditioned on positive advantages"
    assert "(advantages < 0) & dppo_invalid_mask_low" in src, "Low mask not conditioned on negative advantages"


# [pr_diff] fail_to_pass
def test_loss_docstring_updated():
    """Loss function docstring must describe DPPO+KL instead of IPO."""
    loss_path = Path(REPO) / "src/prime_rl/trainer/rl/loss.py"
    src = loss_path.read_text()

    # Find the default_loss_fn function
    tree = ast.parse(src)

    found_func = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "default_loss_fn":
            found_func = True
            docstring = ast.get_docstring(node)
            assert docstring is not None, "default_loss_fn has no docstring"

            # Should describe the new loss name
            assert "DPPO+KL" in docstring, "Docstring should mention DPPO+KL loss"

            # Should describe advantage-based masking
            assert "advantage" in docstring.lower(), "Docstring should mention advantage-based masking"

            # Should NOT describe the old unconditional masking
            assert "mask independently" not in docstring.lower(), "Docstring still describes old unconditional masking"

    assert found_func, "default_loss_fn function not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bugbot_documentation_updated():
    """BUGBOT.md must be updated with new breaking changes definition."""
    bugbot_path = Path(REPO) / ".cursor/BUGBOT.md"

    if not bugbot_path.exists():
        # If file doesn't exist, that's a fail (PR adds changes to it)
        assert False, "BUGBOT.md not found - config documentation not updated"

    content = bugbot_path.read_text()

    # Should define breaking changes specifically
    assert "**breaking**" in content, "BUGBOT.md should define breaking changes"
    assert "Renamed**" in content or "renamed" in content.lower(), "Should list renamed as breaking change"
    assert "Removed**" in content or "removed" in content.lower(), "Should list removed as breaking change"
    assert "Moved**" in content or "moved" in content.lower(), "Should list moved as breaking change"

    # Should clarify additive changes don't require changelog
    assert "Additive changes" in content or "additive" in content.lower(), "Should mention additive changes"

    # Should specify correct config path
    assert "src/prime_rl/configs/" in content, "BUGBOT.md should reference src/prime_rl/configs/"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_loss_function_not_stub():
    """default_loss_fn must have meaningful implementation, not just pass/return."""
    loss_path = Path(REPO) / "src/prime_rl/trainer/rl/loss.py"
    src = loss_path.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "default_loss_fn":
            # Count non-trivial statements (exclude docstring, Pass, simple returns)
            non_trivial = []
            for stmt in node.body:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                    continue  # Docstring
                if isinstance(stmt, ast.Pass):
                    continue
                if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Constant):
                    continue  # Simple return None/0/etc
                non_trivial.append(stmt)

            assert len(non_trivial) >= 5, f"default_loss_fn appears to be a stub (only {len(non_trivial)} meaningful statements)"


# [static] pass_to_pass
def test_config_class_not_stub():
    """DefaultLossConfig must have actual field definitions, not empty."""
    config_path = Path(REPO) / "src/prime_rl/configs/trainer.py"
    src = config_path.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "DefaultLossConfig":
            # Count field definitions
            field_count = 0
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign):  # Annotated assignment like `field: Type = value`
                    field_count += 1

            assert field_count >= 3, f"DefaultLossConfig has too few fields ({field_count}) - likely a stub"
