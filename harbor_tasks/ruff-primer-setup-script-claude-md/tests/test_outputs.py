"""
Task: ruff-primer-setup-script-claude-md
Repo: ruff @ bbaa7698227fcf4f7ec001af6aa5110d405ee54f
PR:   astral-sh/ruff#23195

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/ruff"


# ---------------------------------------------------------------------------
# Fail-to-pass — gate (script must exist and be valid)
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_script_syntax():
    """setup_primer_project.py must exist and be valid Python."""
    r = subprocess.run(
        ["python3", "-c",
         f"import ast; ast.parse(open('{REPO}/scripts/setup_primer_project.py').read())"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Script missing or has syntax error: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_script_help_flag():
    """Script must accept --help and display usage information."""
    r = subprocess.run(
        ["python3", str(Path(REPO) / "scripts" / "setup_primer_project.py"), "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"--help should exit 0, got {r.returncode}: {r.stderr}"
    out = r.stdout.lower()
    assert "project" in out, f"Help should mention 'project' argument: {r.stdout}"


# [pr_diff] fail_to_pass
def test_script_rejects_unknown_project():
    """Script must exit with a clear error for an unknown project name."""
    r = subprocess.run(
        ["python3", str(Path(REPO) / "scripts" / "setup_primer_project.py"),
         "nonexistent_project_xyz_99"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode != 0, "Should exit non-zero for unknown project"
    assert "not found" in r.stderr.lower(), \
        f"Should report 'not found' in stderr, got: {r.stderr}"


# [pr_diff] fail_to_pass
def test_script_find_project():
    """Script's find_project() locates a known project from the mypy_primer registry."""
    r = subprocess.run(
        ["python3", "-c", "\n".join([
            "import importlib.util",
            f"spec = importlib.util.spec_from_file_location('spp', '{REPO}/scripts/setup_primer_project.py')",
            "assert spec and spec.loader, 'setup_primer_project.py not found'",
            "mod = importlib.util.module_from_spec(spec)",
            "spec.loader.exec_module(mod)",
            "from mypy_primer.projects import get_projects",
            "projects = get_projects()",
            "assert len(projects) > 0, 'No projects in registry'",
            "p = mod.find_project(projects[0].name)",
            "assert p is not None, 'find_project returned None'",
            "assert p.name == projects[0].name",
            "print(f'OK: found {p.name}')",
        ])],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"find_project failed: {r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_pyproject_mypy_primer_dependency():
    """scripts/pyproject.toml declares mypy-primer as a project dependency (TOML-parsed)."""
    r = subprocess.run(
        ["python3", "-c", "\n".join([
            "import tomllib",
            f"data = tomllib.loads(open('{REPO}/scripts/pyproject.toml').read())",
            "deps = data.get('project', {}).get('dependencies', [])",
            "assert any('mypy-primer' in d for d in deps), f'mypy-primer not in deps: {deps}'",
            "print('OK')",
        ])],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"


# [pr_diff] fail_to_pass
def test_pyproject_uv_sources():
    """scripts/pyproject.toml configures uv git source for mypy-primer (TOML-parsed)."""
    r = subprocess.run(
        ["python3", "-c", "\n".join([
            "import tomllib",
            f"data = tomllib.loads(open('{REPO}/scripts/pyproject.toml').read())",
            "sources = data.get('tool', {}).get('uv', {}).get('sources', {})",
            "mp = sources.get('mypy-primer', {})",
            "assert 'git' in mp, f'mypy-primer source missing git key: {mp}'",
            "assert 'hauntsaninja/mypy_primer' in mp['git'], f'Wrong git URL: {mp.get(\"git\")}'",
            "print('OK')",
        ])],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_has_ecosystem_section():
    """CLAUDE.md must document how to reproduce ty ecosystem changes."""
    content = (Path(REPO) / "CLAUDE.md").read_text()
    lower = content.lower()
    assert "ecosystem" in lower, "CLAUDE.md should mention ecosystem"
    assert "setup_primer_project" in content, \
        "CLAUDE.md should reference the setup_primer_project script"


# [pr_diff] fail_to_pass
def test_claude_md_shows_usage_command():
    """CLAUDE.md must include the uv run command for the primer setup script."""
    content = (Path(REPO) / "CLAUDE.md").read_text()
    assert "uv run scripts/setup_primer_project.py" in content, \
        "CLAUDE.md should show the uv run command for the script"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_claude_md_preserves_test_instructions():
    """CLAUDE.md must still contain the existing test running instructions."""
    content = (Path(REPO) / "CLAUDE.md").read_text()
    assert "cargo nextest run" in content, \
        "CLAUDE.md should preserve existing 'cargo nextest run' instructions"
    assert "cargo run --bin ty" in content, \
        "CLAUDE.md should preserve existing ty run instructions"


# [static] pass_to_pass
def test_script_not_stub():
    """Script main() has substantive logic, not just pass/return."""
    script = Path(REPO) / "scripts" / "setup_primer_project.py"
    if not script.exists():
        return  # gated by test_script_syntax
    source = script.read_text()
    tree = ast.parse(source)
    main_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            main_func = node
            break
    assert main_func is not None, "Script must have a main() function"
    body_stmts = [s for s in main_func.body if not isinstance(s, (ast.Pass, ast.Expr))]
    assert len(body_stmts) >= 3, "main() should have substantive logic, not a stub"


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI/CD checks (p2p enrichment)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_ruff_check_scripts():
    """Repo's ruff linter passes on scripts directory (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"
    r = subprocess.run(
        ["ruff", "check", str(Path(REPO) / "scripts"), "--select", "E,W,F", "--ignore", "E501"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_python_syntax_scripts():
    """All Python files in scripts directory have valid syntax (pass_to_pass)."""
    scripts_dir = Path(REPO) / "scripts"
    py_files = list(scripts_dir.glob("*.py"))
    assert len(py_files) > 0, "No Python files found in scripts directory"
    for py_file in py_files:
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(py_file)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Syntax error in {py_file.name}: {r.stderr}"


# [repo_tests] pass_to_pass
def test_scripts_pyproject_valid():
    """scripts/pyproject.toml is valid TOML (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "tomli", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install tomli: {r.stderr}"
    pyproject_path = Path(REPO) / "scripts" / "pyproject.toml"
    r = subprocess.run(
        ["python3", "-c",
         f"import tomli; tomli.loads(open('{pyproject_path}').read()); print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Invalid TOML in scripts/pyproject.toml: {r.stderr}"


# [repo_tests] pass_to_pass
def test_root_pyproject_valid():
    """Root pyproject.toml is valid TOML (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         f"import tomllib; tomllib.loads(open('{REPO}/pyproject.toml').read()); print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Invalid TOML in root pyproject.toml: {r.stderr}"


# [repo_tests] pass_to_pass
def test_add_rule_script_valid():
    """add_rule.py passes syntax validation (pass_to_pass)."""
    script_path = Path(REPO) / "scripts" / "add_rule.py"
    # Syntax check
    r = subprocess.run(
        ["python3", "-m", "py_compile", str(script_path)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax error in add_rule.py: {r.stderr}"


# [repo_tests] pass_to_pass
def test_setup_primer_script_valid_ast():
    """setup_primer_project.py has valid Python AST (pass_to_pass)."""
    script_path = Path(REPO) / "scripts" / "setup_primer_project.py"
    if not script_path.exists():
        return  # File doesn't exist at base commit
    r = subprocess.run(
        ["python3", "-c",
         f"import ast; ast.parse(open('{script_path}').read()); print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parsing failed: {r.stderr}"
    assert "OK" in r.stdout


# [repo_tests] pass_to_pass
def test_validate_pyproject_scripts():
    """scripts/pyproject.toml passes validate-pyproject (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "validate-pyproject", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install validate-pyproject: {r.stderr}"
    pyproject_path = Path(REPO) / "scripts" / "pyproject.toml"
    r = subprocess.run(
        ["validate-pyproject", str(pyproject_path)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"validate-pyproject failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_typos_scripts():
    """No typos detected in scripts directory (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "typos", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install typos: {r.stderr}"
    r = subprocess.run(
        ["typos", str(Path(REPO) / "scripts")],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Typos found:\n{r.stdout}\n{r.stderr}"
