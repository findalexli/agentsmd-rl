"""
Task: posthog-featcloudagent-added-sandboxenvironmentid-ext-caller
Repo: PostHog/posthog @ a65a8fd19c2bed0c06c111f1d65b0deb87f31313
PR:   53163

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/posthog"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified Python file must parse without errors."""
    import py_compile

    py_compile.compile(
        f"{REPO}/products/tasks/backend/models.py", doraise=True
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_create_and_run_accepts_sandbox_env_id():
    """create_and_run must accept sandbox_environment_id keyword argument."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            """
import ast, sys
src = open("products/tasks/backend/models.py").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
        kwonly = [a.arg for a in node.args.kwonlyargs]
        if "sandbox_environment_id" not in kwonly:
            print(f"FAIL: sandbox_environment_id not in {kwonly}", file=sys.stderr)
            sys.exit(1)
        # Verify default is None
        for i, arg in enumerate(node.args.kwonlyargs):
            if arg.arg == "sandbox_environment_id":
                d = node.args.kw_defaults[i]
                if d is None or not (isinstance(d, ast.Constant) and d.value is None):
                    print("FAIL: sandbox_environment_id must default to None", file=sys.stderr)
                    sys.exit(1)
        print("OK")
        sys.exit(0)
print("FAIL: create_and_run not found", file=sys.stderr)
sys.exit(1)
""",
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    assert result.returncode == 0, f"Signature check failed:\n{result.stderr}"
    assert "OK" in result.stdout


# [pr_diff] fail_to_pass
def test_invalid_sandbox_env_id_raises_valueerror():
    """create_and_run must validate sandbox_environment_id and raise ValueError if invalid."""
    source = Path(f"{REPO}/products/tasks/backend/models.py").read_text()
    assert "SandboxEnvironment.objects.filter" in source, (
        "Must look up SandboxEnvironment via objects.filter"
    )
    assert "Invalid sandbox_environment_id" in source, (
        "Must raise ValueError with descriptive message for invalid sandbox_environment_id"
    )
    assert "sandbox_env" in source, (
        "Must assign lookup result to sandbox_env variable"
    )


# [pr_diff] fail_to_pass
def test_sandbox_env_id_stored_in_extra_state():
    """sandbox_environment_id must be stored in extra_state dict when a valid env is provided."""
    source = Path(f"{REPO}/products/tasks/backend/models.py").read_text()
    assert 'extra_state["sandbox_environment_id"]' in source or "extra_state['sandbox_environment_id']" in source, (
        "Must store sandbox_environment_id in extra_state dict"
    )
    assert "str(sandbox_env.id)" in source, (
        "Must store the string representation of sandbox_env.id"
    )


# ---------------------------------------------------------------------------
# Agent config compliance (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — AGENTS.md:87 @ a65a8fd19c2bed0c06c111f1d65b0deb87f31313
def test_team_filter_in_sandbox_lookup():
    """SandboxEnvironment lookup must filter by team (AGENTS.md: always filter querysets by team_id)."""
    source = Path(f"{REPO}/products/tasks/backend/models.py").read_text()
    assert "SandboxEnvironment.objects.filter" in source, (
        "Must use SandboxEnvironment.objects.filter for lookup"
    )
    # Verify team filter is present in the same filter call
    assert "team=team" in source, (
        "SandboxEnvironment filter must include team=team per AGENTS.md rule"
    )


# ---------------------------------------------------------------------------
# Config/documentation update checks (REQUIRED for agentmd-edit tasks)
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_docs_parameter_table_includes_sandbox_env_id():
    """Handbook must document sandbox_environment_id in the Parameters section."""
    doc = Path(f"{REPO}/docs/published/handbook/engineering/ai/sandboxed-agents.md").read_text()
    params_idx = doc.find("### Parameters")
    assert params_idx != -1, "Parameters section not found in handbook"
    params_section = doc[params_idx:]
    assert "sandbox_environment_id" in params_section, (
        "Parameters table must include sandbox_environment_id entry"
    )
    assert "SandboxEnvironment" in params_section, (
        "sandbox_environment_id description must reference SandboxEnvironment"
    )


# [pr_diff] fail_to_pass
def test_docs_include_usage_example():
    """Handbook must include code example showing how to create SandboxEnvironment and pass its ID."""
    doc = Path(f"{REPO}/docs/published/handbook/engineering/ai/sandboxed-agents.md").read_text()
    assert "SandboxEnvironment.objects.create" in doc, (
        "Handbook must show SandboxEnvironment.objects.create in usage example"
    )
    assert "network_access_level" in doc, (
        "Usage example must demonstrate network_access_level configuration"
    )
    assert "allowed_domains" in doc, (
        "Usage example must mention allowed_domains"
    )
    assert "sandbox_environment_id=str(env.id)" in doc, (
        "Usage example must show passing sandbox_environment_id to create_and_run"
    )


# ---------------------------------------------------------------------------
# Anti-stub (pass_to_pass)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """create_and_run has real sandbox_environment_id validation logic, not just a parameter."""
    import ast

    src = Path(f"{REPO}/products/tasks/backend/models.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
            body_src = ast.get_source_segment(src, node)
            # Must have at least 3 distinct references to sandbox_env logic
            refs = body_src.count("sandbox_env") + body_src.count("sandbox_environment_id")
            assert refs >= 5, (
                f"create_and_run body has only {refs} refs to sandbox logic — likely a stub"
            )
            return
    raise AssertionError("create_and_run method not found")
