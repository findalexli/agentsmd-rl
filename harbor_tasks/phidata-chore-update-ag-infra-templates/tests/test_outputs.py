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


def _get_map_from_ast(tree, map_name):
    """Helper to extract dict values from either Assign or AnnAssign nodes."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == map_name:
                    if isinstance(node.value, ast.Dict):
                        return node.value
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == map_name:
                if isinstance(node.value, ast.Dict):
                    return node.value
    return None


# [pr_diff] fail_to_pass
def test_template_name_map_updated():
    """TEMPLATE_TO_NAME_MAP values must use short names without -template suffix."""
    operator_py = Path(REPO) / "libs" / "agno_infra" / "agno" / "infra" / "operator.py"
    tree = ast.parse(operator_py.read_text())
    dict_node = _get_map_from_ast(tree, "TEMPLATE_TO_NAME_MAP")
    
    assert dict_node is not None, "TEMPLATE_TO_NAME_MAP not found in operator.py"
    
    values = []
    for v in dict_node.values:
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
    dict_node = _get_map_from_ast(tree, "TEMPLATE_TO_REPO_MAP")
    
    assert dict_node is not None, "TEMPLATE_TO_REPO_MAP not found in operator.py"
    
    urls = [v.value for v in dict_node.values if isinstance(v, ast.Constant)]
    assert "https://github.com/agno-agi/agentos-docker-template" in urls
    assert "https://github.com/agno-agi/agentos-aws-template" in urls
    assert "https://github.com/agno-agi/agentos-railway-template" in urls


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
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == map_name:
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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_agno_infra_ruff_check():
    """Repo's ruff linter passes on agno_infra (pass_to_pass)."""
    # Install dev dependencies first
    install = subprocess.run(
        ["pip", "install", "-e", f"{REPO}/libs/agno_infra[dev]", "-q"],
        capture_output=True, text=True, timeout=300,
    )
    assert install.returncode == 0, f"Failed to install dev dependencies: {install.stderr}"
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/libs/agno_infra"],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_agno_infra_mypy():
    """Repo's mypy typecheck passes on agno_infra (pass_to_pass)."""
    # Install dev dependencies first
    install = subprocess.run(
        ["pip", "install", "-e", f"{REPO}/libs/agno_infra[dev]", "-q"],
        capture_output=True, text=True, timeout=300,
    )
    assert install.returncode == 0, f"Failed to install dev dependencies: {install.stderr}"
    r = subprocess.run(
        ["mypy", f"{REPO}/libs/agno_infra", "--config-file", f"{REPO}/libs/agno_infra/pyproject.toml"],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Mypy check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_agno_infra_validate_script():
    """Repo's validate script passes on agno_infra (pass_to_pass)."""
    # Install dev dependencies first
    install = subprocess.run(
        ["pip", "install", "-e", f"{REPO}/libs/agno_infra[dev]", "-q"],
        capture_output=True, text=True, timeout=300,
    )
    assert install.returncode == 0, f"Failed to install dev dependencies: {install.stderr}"
    r = subprocess.run(
        ["bash", f"{REPO}/libs/agno_infra/scripts/validate.sh"],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Validate script failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_agno_infra_modules_importable():
    """Modified agno_infra modules can be imported successfully (pass_to_pass)."""
    # Install both agno and agno_infra first
    install_result = subprocess.run(
        ["pip", "install", "-e", f"{REPO}/libs/agno[dev]", "-e", f"{REPO}/libs/agno_infra[dev]", "-q"],
        capture_output=True, text=True, timeout=300,
    )
    assert install_result.returncode == 0, f"Failed to install dependencies: {install_result.stderr}"

    # Test importing enums module
    r = subprocess.run(
        ["python3", "-c",
         f"import sys; sys.path.insert(0, '{REPO}/libs/agno_infra'); "
         "from agno.infra.enums import InfraStarterTemplate; "
         "print('Enums import OK')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed to import enums module: {r.stderr}"
    assert "Enums import OK" in r.stdout

    # Test importing operator module (requires agno)
    r = subprocess.run(
        ["python3", "-c",
         f"import sys; sys.path.insert(0, '{REPO}/libs/agno_infra'); "
         "from agno.infra.operator import TEMPLATE_TO_NAME_MAP, TEMPLATE_TO_REPO_MAP; "
         "print('Operator import OK')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed to import operator module: {r.stderr}"
    assert "Operator import OK" in r.stdout


# [repo_tests] pass_to_pass
def test_agno_infra_ruff_format_check():
    """Repo's ruff format check passes on agno_infra (pass_to_pass)."""
    # Install dev dependencies first
    install = subprocess.run(
        ["pip", "install", "-e", f"{REPO}/libs/agno_infra[dev]", "-q"],
        capture_output=True, text=True, timeout=300,
    )
    assert install.returncode == 0, f"Failed to install dev dependencies: {install.stderr}"
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/libs/agno_infra"],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_agno_infra_format_script():
    """Repo's format.sh script runs successfully on agno_infra (pass_to_pass)."""
    # Install dev dependencies first
    install = subprocess.run(
        ["pip", "install", "-e", f"{REPO}/libs/agno_infra[dev]", "-q"],
        capture_output=True, text=True, timeout=300,
    )
    assert install.returncode == 0, f"Failed to install dev dependencies: {install.stderr}"
    r = subprocess.run(
        ["bash", f"{REPO}/libs/agno_infra/scripts/format.sh"],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Format script failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_agno_infra_import_check():
    """Repo's agno_infra package imports correctly from installed location (pass_to_pass)."""
    # Install agno_infra first
    install = subprocess.run(
        ["pip", "install", "-e", f"{REPO}/libs/agno_infra[dev]", "-q"],
        capture_output=True, text=True, timeout=300,
    )
    assert install.returncode == 0, f"Failed to install agno_infra: {install.stderr}"

    # Verify imports work after pip install
    r = subprocess.run(
        ["python3", "-c",
         "from agno.infra.enums import InfraStarterTemplate; "
         "from agno.infra.operator import TEMPLATE_TO_NAME_MAP, TEMPLATE_TO_REPO_MAP; "
         "print('All agno.infra imports OK')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Import check failed: {r.stderr}"
    assert "All agno.infra imports OK" in r.stdout
