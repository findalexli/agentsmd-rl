"""
Task: phidata-chore-update-ag-infra-templates
Repo: phidata @ 156d4e43e6281d0ff65a2351379df732348ffadc
PR:   6079

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/phidata"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    files = [
        Path(REPO) / "libs" / "agno_infra" / "agno" / "infra" / "enums.py",
        Path(REPO) / "libs" / "agno_infra" / "agno" / "infra" / "operator.py",
    ]
    for f in files:
        src = f.read_text()
        ast.parse(src)  # raises SyntaxError on bad code


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_enum_values_renamed():
    """InfraStarterTemplate enum values must use short names without -template suffix."""
    result = subprocess.run(
        ["python3", "-c", (
            "import sys; sys.path.insert(0, 'libs/agno_infra'); "
            "from agno.infra.enums import InfraStarterTemplate; "
            "members = list(InfraStarterTemplate.__members__.keys()); "
            "values = [m.value for m in InfraStarterTemplate]; "
            "print(','.join(members)); print(','.join(values))"
        )],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    lines = result.stdout.strip().split("\n")
    member_names = lines[0].split(",")
    member_values = lines[1].split(",")

    # Member names must NOT have _template suffix
    for name in member_names:
        assert not name.endswith("_template"), (
            f"Enum member '{name}' still has '_template' suffix"
        )

    # Member values must NOT have -template suffix
    for val in member_values:
        assert not val.endswith("-template"), (
            f"Enum value '{val}' still has '-template' suffix"
        )

    # Verify specific expected names exist
    assert "agentos_docker" in member_names, "Missing agentos_docker member"
    assert "agentos_aws" in member_names, "Missing agentos_aws member"
    assert "agentos_railway" in member_names, "Missing agentos_railway member"


# [pr_diff] fail_to_pass
def test_template_name_map_updated():
    """TEMPLATE_TO_NAME_MAP values must use short names without -template suffix."""
    operator_py = Path(REPO) / "libs" / "agno_infra" / "agno" / "infra" / "operator.py"
    tree = ast.parse(operator_py.read_text())
    # Find the TEMPLATE_TO_NAME_MAP assignment and extract string values
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TEMPLATE_TO_NAME_MAP":
                    assert isinstance(node.value, ast.Dict), "TEMPLATE_TO_NAME_MAP is not a dict"
                    values = []
                    for v in node.value.values:
                        assert isinstance(v, ast.Constant), f"Expected string constant, got {type(v)}"
                        values.append(v.value)
                    assert len(values) == 3, f"Expected 3 entries, got {len(values)}"
                    for val in values:
                        assert not val.endswith("-template"), (
                            f"TEMPLATE_TO_NAME_MAP value '{val}' still has '-template' suffix"
                        )
                    assert "agentos-docker" in values
                    assert "agentos-aws" in values
                    assert "agentos-railway" in values
                    return
    assert False, "TEMPLATE_TO_NAME_MAP not found in operator.py"


# [pr_diff] fail_to_pass
def test_default_template_prompt_updated():
    """User prompt must show 'agentos-docker' not 'agentos-docker-template'."""
    operator_py = Path(REPO) / "libs" / "agno_infra" / "agno" / "infra" / "operator.py"
    content = operator_py.read_text()
    # The prompt string shown to users
    assert 'default (agentos-docker)' in content, (
        "User prompt should say 'agentos-docker' not 'agentos-docker-template'"
    )
    assert 'default (agentos-docker-template)' not in content, (
        "User prompt still references 'agentos-docker-template'"
    )


# [pr_diff] pass_to_pass
def test_repo_urls_unchanged():
    """TEMPLATE_TO_REPO_MAP must still point to original GitHub URLs (unchanged)."""
    operator_py = Path(REPO) / "libs" / "agno_infra" / "agno" / "infra" / "operator.py"
    tree = ast.parse(operator_py.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TEMPLATE_TO_REPO_MAP":
                    assert isinstance(node.value, ast.Dict)
                    urls = [v.value for v in node.value.values if isinstance(v, ast.Constant)]
                    assert "https://github.com/agno-agi/agentos-docker-template" in urls
                    assert "https://github.com/agno-agi/agentos-aws-template" in urls
                    assert "https://github.com/agno-agi/agentos-railway-template" in urls
                    return
    assert False, "TEMPLATE_TO_REPO_MAP not found in operator.py"


# [pr_diff] fail_to_pass
def test_version_bumped():
    """agno-infra version must be bumped to 1.0.7."""
    pyproject = Path(REPO) / "libs" / "agno_infra" / "pyproject.toml"
    content = pyproject.read_text()
    assert 'version = "1.0.7"' in content, (
        "pyproject.toml version should be 1.0.7"
    )


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit required)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_github_operations_section():
    """CLAUDE.md must contain a GitHub Operations section with gh api usage guidance."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()
    assert "GitHub Operations" in content, (
        "CLAUDE.md should have a 'GitHub Operations' section"
    )
    assert "gh api" in content, (
        "CLAUDE.md GitHub Operations section should mention 'gh api'"
    )
    assert "gh pr edit" in content, (
        "CLAUDE.md should mention 'gh pr edit' (the command that can fail)"
    )


# [pr_diff] fail_to_pass
def test_claude_md_graphql_workaround():
    """CLAUDE.md must document the GraphQL / classic projects workaround."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()
    # Must mention the failure mode and the API alternative
    assert "GraphQL" in content or "graphql" in content.lower(), (
        "CLAUDE.md should mention GraphQL errors as the reason for the workaround"
    )
    assert "PATCH" in content, (
        "CLAUDE.md should show the -X PATCH flag for the API call"
    )
    assert "repos/" in content and "/pulls/" in content, (
        "CLAUDE.md should show the API path format for updating PRs"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_template_repo_map_keys_match_enum():
    """TEMPLATE_TO_REPO_MAP keys must match all InfraStarterTemplate members."""
    # Extract enum member names from enums.py
    enums_py = Path(REPO) / "libs" / "agno_infra" / "agno" / "infra" / "enums.py"
    enums_tree = ast.parse(enums_py.read_text())
    enum_members = set()
    for node in ast.walk(enums_tree):
        if isinstance(node, ast.ClassDef) and node.name == "InfraStarterTemplate":
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for t in item.targets:
                        if isinstance(t, ast.Name):
                            enum_members.add(t.id)

    # Extract map key attribute names from operator.py
    operator_py = Path(REPO) / "libs" / "agno_infra" / "agno" / "infra" / "operator.py"
    op_tree = ast.parse(operator_py.read_text())

    def _get_map_key_attrs(tree, map_name):
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == map_name:
                        keys = set()
                        for k in node.value.keys:
                            if isinstance(k, ast.Attribute):
                                keys.add(k.attr)
                        return keys
        return set()

    repo_keys = _get_map_key_attrs(op_tree, "TEMPLATE_TO_REPO_MAP")
    name_keys = _get_map_key_attrs(op_tree, "TEMPLATE_TO_NAME_MAP")

    assert enum_members == repo_keys, f"TEMPLATE_TO_REPO_MAP keys {repo_keys} != enum {enum_members}"
    assert enum_members == name_keys, f"TEMPLATE_TO_NAME_MAP keys {name_keys} != enum {enum_members}"


# [agent_config] pass_to_pass — CLAUDE.md:195 @ 156d4e43
def test_no_fstring_without_vars():
    """Code must not use f-strings where there are no variables (CLAUDE.md: Don't use f-strings for print lines where there are no variables)."""
    # Check the modified operator.py for any f-string print_info calls without variables
    operator_py = Path(REPO) / "libs" / "agno_infra" / "agno" / "infra" / "operator.py"
    content = operator_py.read_text()
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Name) and call.func.id in ("print_info", "print_subheading"):
                for arg in call.args:
                    if isinstance(arg, ast.JoinedStr) and not any(
                        isinstance(v, ast.FormattedValue) for v in arg.values
                    ):
                        assert False, (
                            f"Line {node.lineno}: f-string in {call.func.id}() "
                            "with no variables — use a plain string"
                        )
