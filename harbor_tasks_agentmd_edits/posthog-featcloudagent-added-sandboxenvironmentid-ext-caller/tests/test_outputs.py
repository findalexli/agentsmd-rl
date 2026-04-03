"""
Task: posthog-featcloudagent-added-sandboxenvironmentid-ext-caller
Repo: PostHog/posthog @ a65a8fd19c2bed0c06c111f1d65b0deb87f31313
PR:   53163

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
from pathlib import Path

REPO = "/workspace/posthog"
MODELS_PY = Path(REPO) / "products" / "tasks" / "backend" / "models.py"
DOCS_MD = Path(REPO) / "docs" / "published" / "handbook" / "engineering" / "ai" / "sandboxed-agents.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_create_and_run_node() -> ast.FunctionDef:
    src = MODELS_PY.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
            return node
    raise AssertionError("create_and_run function not found in models.py")


def _get_create_and_run_source() -> str:
    src = MODELS_PY.read_text()
    lines = src.splitlines()
    node = _get_create_and_run_node()
    return "\n".join(lines[node.lineno - 1 : node.end_lineno])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile
    py_compile.compile(str(MODELS_PY), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_create_and_run_accepts_sandbox_environment_id():
    """create_and_run() must accept a sandbox_environment_id parameter."""
    node = _get_create_and_run_node()
    param_names = [arg.arg for arg in node.args.args + node.args.kwonlyargs]
    assert "sandbox_environment_id" in param_names, (
        "create_and_run() must have a 'sandbox_environment_id' parameter"
    )


# [pr_diff] fail_to_pass
def test_sandbox_env_validated_against_team():
    """create_and_run() must validate sandbox_environment_id is scoped to the team."""
    src = _get_create_and_run_source()
    assert "SandboxEnvironment" in src, (
        "create_and_run() must look up the SandboxEnvironment model"
    )
    # Must scope by team to prevent cross-team access (filter or get)
    assert re.search(r"(filter|get)\(.*team", src), (
        "SandboxEnvironment lookup must be scoped to the team"
    )


# [pr_diff] fail_to_pass
def test_invalid_sandbox_env_raises_error():
    """create_and_run() must raise an error when sandbox_environment_id is invalid."""
    src = _get_create_and_run_source()
    assert "ValueError" in src or "ValidationError" in src, (
        "create_and_run() must raise an error for invalid sandbox_environment_id"
    )
    # The error message should reference the invalid ID
    assert re.search(r'(sandbox_environment_id|sandbox.env)', src, re.IGNORECASE), (
        "Error handling must reference sandbox_environment_id"
    )


# [pr_diff] fail_to_pass
def test_sandbox_env_id_stored_in_extra_state():
    """sandbox_environment_id must be stored in extra_state for the task run."""
    src = _get_create_and_run_source()
    # The ID must end up in extra_state so the temporal workflow can read it
    assert "extra_state" in src, "Function must use extra_state"
    assert re.search(r'extra_state\[.*sandbox_environment_id.*\]|extra_state\[.*sandbox.*\]|"sandbox_environment_id"', src), (
        "sandbox_environment_id must be stored in extra_state"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub_create_and_run():
    """create_and_run() must have real logic, not just pass/return."""
    node = _get_create_and_run_node()
    body_stmts = [s for s in node.body
                  if not isinstance(s, (ast.Pass, ast.Expr))]
    assert len(body_stmts) >= 5, (
        f"create_and_run() body has only {len(body_stmts)} statements — looks like a stub"
    )
