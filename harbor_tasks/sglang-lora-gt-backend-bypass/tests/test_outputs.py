"""
Task: {{TASK_NAME}}
Repo: {{REPO}} @ {{BASE_COMMIT}}
PR:   {{PR_NUMBER}}

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/{{REPO_SHORT}}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    # TODO: add py_compile / cargo check / tsc --noEmit for each modified file
    raise NotImplementedError("Replace with syntax check for modified files")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_core_bug_fixed():
    """TODO: describe the core behavioral change from the PR."""
    # TODO: import the function/class under test, call it with bug-triggering input,
    #       assert it returns the correct result (not just "doesn't crash")
    raise NotImplementedError("Replace with behavioral test")


# [pr_diff] fail_to_pass
def test_edge_case():
    """TODO: test a second input or edge case for the same fix."""
    raise NotImplementedError("Replace with edge case test")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_pass():
    """Upstream test suite (CPU-safe subset) still passes."""
    # TODO: run a focused subset of the repo's own tests
    # Example:
    #   r = subprocess.run(
    #       ["python3", "-m", "pytest", "tests/test_utils.py", "-x", "--timeout=30", "-q"],
    #       cwd=REPO, capture_output=True, timeout=60,
    #   )
    #   assert r.returncode == 0, f"Upstream tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    raise NotImplementedError("Replace with upstream test suite or remove if none available")


# [static] pass_to_pass
def test_not_stub():
    """Modified function is not a stub (has real logic, not just pass/return)."""
    import ast

    # TODO: check that modified function(s) have meaningful body
    # Example:
    #   src = Path(f"{REPO}/path/to/file.py").read_text()
    #   tree = ast.parse(src)
    #   for node in ast.walk(tree):
    #       if isinstance(node, ast.FunctionDef) and node.name == "target_func":
    #           stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
    #           assert len(stmts) >= 2, "Function body is a stub"
    raise NotImplementedError("Replace with anti-stub check")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — {{CONFIG_FILE}}:{{LINES}} @ {{COMMIT}}
def test_config_rule():
    """TODO: programmatic check for a rule from agent config files."""
    # Only include if the rule is programmatically verifiable.
    # Soft/subjective rules go in eval_manifest.yaml rubric section instead.
    raise NotImplementedError("Replace with config-derived check or remove")
