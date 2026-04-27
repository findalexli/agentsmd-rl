"""
Task: prime-rl-skills-directory
Repo: PrimeIntellect-ai/prime-rl @ 31b48b8b10db390d835909a6fd976f29d9880c81
PR:   1747

This task requires both structural changes (skills directory + symlink) and
documentation updates (AGENTS.md describing the skills system).

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path
import os
import re

REPO = "/workspace/prime-rl"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural checks
# ---------------------------------------------------------------------------

def test_agents_md_exists():
    """AGENTS.md must exist and be readable."""
    agents_md = Path(REPO) / "AGENTS.md"
    assert agents_md.exists(), "AGENTS.md must exist"
    content = agents_md.read_text()
    assert len(content) > 0, "AGENTS.md must not be empty"


def test_agents_md_frontmatter_valid():
    """AGENTS.md has valid YAML frontmatter if present (pass_to_pass)."""
    try:
        import yaml
    except ImportError:
        subprocess.run(["pip", "install", "pyyaml", "-q"], check=True, capture_output=True)
        import yaml

    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    if not content.startswith("---"):
        return

    lines = content.split("\n")
    if len(lines) < 2 or lines[0].strip() != "---":
        return

    try:
        end_idx = lines[1:].index("---") + 1
        yaml_content = "\n".join(lines[1:end_idx])
        yaml.safe_load(yaml_content)
    except ValueError:
        pass
    except yaml.YAMLError as e:
        import pytest
        pytest.fail(f"Invalid YAML frontmatter in AGENTS.md: {e}")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that should pass on base and gold
# ---------------------------------------------------------------------------

def test_repo_toml_valid():
    """Repo's TOML config files are valid (pass_to_pass)."""
    try:
        import tomli
    except ImportError:
        subprocess.run(["pip", "install", "tomli", "-q"], check=True, capture_output=True)
        import tomli

    config_dir = Path(REPO) / "configs"
    assert config_dir.exists(), "configs/ directory must exist"

    toml_files = list(config_dir.rglob("*.toml"))
    assert len(toml_files) > 0, "Must have at least one TOML config file"

    for toml_file in toml_files:
        with open(toml_file, "rb") as f:
            tomli.load(f)


def test_repo_ruff_check():
    """Repo's Python linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "--config=pyproject.toml", "src/", "tests/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo's Python formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "--config=pyproject.toml", "src/", "tests/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_python_syntax_valid():
    """All Python source files have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import ast, glob, sys
src_files = glob.glob(sys.argv[1] + "/src/**/*.py", recursive=True)
assert len(src_files) > 0, "Must have at least one Python source file"
for py_file in src_files:
    with open(py_file) as f:
        source = f.read()
    try:
        ast.parse(source)
    except SyntaxError as e:
        print(f"FAIL: Syntax error in {py_file}: {e}", file=sys.stderr)
        sys.exit(1)
print("PASS")
""", REPO],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_skill_md_frontmatter():
    """Any SKILL.md files have valid YAML frontmatter (pass_to_pass)."""
    import pytest

    skills_dir = Path(REPO) / "skills"
    if not skills_dir.exists():
        pytest.skip("skills/ directory does not exist yet (fail-to-pass tests cover this)")

    skill_md_files = list(skills_dir.rglob("SKILL.md"))
    if not skill_md_files:
        pytest.skip("No SKILL.md files found yet (fail-to-pass tests cover this)")

    r = subprocess.run(
        ["python3", "-c", """
import yaml, sys, pathlib
skills_dir = pathlib.Path(sys.argv[1]) / "skills"
for skill_file in skills_dir.rglob("SKILL.md"):
    content = skill_file.read_text()
    if not content.startswith("---"):
        continue
    lines = content.split("\\n")
    try:
        end = lines[1:].index("---") + 1
        fm = yaml.safe_load("\\n".join(lines[1:end]))
        if fm is None:
            print(f"WARN: empty frontmatter in {skill_file}", file=sys.stderr)
    except (ValueError, yaml.YAMLError) as e:
        print(f"FAIL: {skill_file}: {e}", file=sys.stderr)
        sys.exit(1)
print("PASS")
""", REPO],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        pytest.fail(f"SKILL.md frontmatter validation failed: {r.stderr}")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — skills directory structure tests
# ---------------------------------------------------------------------------

def test_skills_directory_exists():
    """skills/ directory must exist with proper structure."""
    r = subprocess.run(
        ["python3", "-c", """
import pathlib, sys
repo = sys.argv[1]
skills = pathlib.Path(repo) / "skills"
assert skills.exists(), "skills/ directory must exist"
assert skills.is_dir(), "skills/ must be a directory"
subdirs = [d.name for d in skills.iterdir() if d.is_dir()]
assert len(subdirs) > 0, "skills/ must contain at least one subdirectory"
print("PASS")
""", REPO],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"skills/ directory check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_inference_server_skill_exists():
    """skills/inference-server/SKILL.md must exist with proper content."""
    skill_file = Path(REPO) / "skills" / "inference-server" / "SKILL.md"
    assert skill_file.exists(), "skills/inference-server/SKILL.md must exist"

    r = subprocess.run(
        ["python3", "-c", """
import yaml, sys, pathlib, re
repo = sys.argv[1]
skill_file = pathlib.Path(repo) / "skills" / "inference-server" / "SKILL.md"
content = skill_file.read_text()

# Parse YAML frontmatter
assert content.startswith("---"), "Must have YAML frontmatter"
lines = content.split("\\n")
end = lines[1:].index("---") + 1
fm = yaml.safe_load("\\n".join(lines[1:end]))
assert fm and "name" in fm, "frontmatter must have 'name' field"
assert "description" in fm, "frontmatter must have 'description' field"

body = "\\n".join(lines[end+1:])
assert len(body.strip()) > 100, "body must have substantive content"

# Must document the inference command
assert "uv run" in body, "must document uv run commands"

# Must document custom endpoints (API paths)
endpoint_pattern = r'/v1/|/update_weights|/load_lora_adapter|/init_broadcaster'
assert re.search(endpoint_pattern, body), "must document custom API endpoints"

print("PASS")
""", REPO],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"SKILL.md validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_inference_entry_point_exists():
    """The inference entry point documented in SKILL.md must exist in the codebase."""
    # This cross-reference test verifies the SKILL.md exists AND that the
    # entry point it documents is real (defined in pyproject.toml with valid module)
    r = subprocess.run(
        ["python3", "-c", """
import sys, pathlib, ast

repo = sys.argv[1]

# 1. SKILL.md must exist (fails on NOP, passes on gold)
skill_file = pathlib.Path(repo) / "skills" / "inference-server" / "SKILL.md"
assert skill_file.exists(), "skills/inference-server/SKILL.md must exist"
body = skill_file.read_text()
assert "uv run inference" in body, "SKILL.md must document the inference command"

# 2. Verify the documented entry point actually exists in pyproject.toml
try:
    import tomli
except ImportError:
    import subprocess as sp
    sp.run(["pip", "install", "tomli", "-q"], check=True, capture_output=True)
    import tomli

pyproject = pathlib.Path(repo) / "pyproject.toml"
with open(pyproject, "rb") as f:
    config = tomli.load(f)
scripts = config.get("project", {}).get("scripts", {})
assert "inference" in scripts, "pyproject.toml must have 'inference' script entry"
entry = scripts["inference"]

# 3. Resolve the module and verify the function exists via AST
module_path, func_name = entry.rsplit(":", 1)
parts = module_path.split(".")
file_path = pathlib.Path(repo) / "src" / "/".join(parts)
py_file = file_path.with_suffix(".py")
init_file = file_path / "__init__.py"
assert py_file.exists() or init_file.exists(), f"Module file must exist"

target = py_file if py_file.exists() else init_file
source = target.read_text()
tree = ast.parse(source)
func_names = [node.name for node in ast.walk(tree)
              if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
assert func_name in func_names, f"Function '{func_name}' must exist in {target}"

print("PASS")
""", REPO],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Entry point verification failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_toml_config_skill_exists():
    """skills/toml-config/SKILL.md must exist with proper content."""
    skill_file = Path(REPO) / "skills" / "toml-config" / "SKILL.md"
    assert skill_file.exists(), "skills/toml-config/SKILL.md must exist"

    r = subprocess.run(
        ["python3", "-c", """
import yaml, sys, pathlib, re
repo = sys.argv[1]
skill_file = pathlib.Path(repo) / "skills" / "toml-config" / "SKILL.md"
content = skill_file.read_text()

# Parse YAML frontmatter
assert content.startswith("---"), "Must have YAML frontmatter"
lines = content.split("\\n")
end = lines[1:].index("---") + 1
fm = yaml.safe_load("\\n".join(lines[1:end]))
assert fm and "name" in fm, "frontmatter must have 'name' field"
assert "description" in fm, "frontmatter must have 'description' field"

body = "\\n".join(lines[end+1:])
assert len(body.strip()) > 100, "body must have substantive content"

# Must document @ config syntax
at_pattern = r'@\\s+\\S+\\.toml'
assert re.search(at_pattern, body), "must document @ config.toml syntax"

# Must document CLI override syntax (--flags)
cli_pattern = r'--[a-zA-Z][a-zA-Z0-9_.-]*'
assert re.search(cli_pattern, body), "must document CLI override syntax with --flags"

print("PASS")
""", REPO],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"SKILL.md validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_claude_skills_symlink_exists():
    """.claude/skills symlink must point to ../skills and be traversable."""
    r = subprocess.run(
        ["python3", "-c", """
import sys, pathlib, os
repo = sys.argv[1]
symlink = pathlib.Path(repo) / ".claude" / "skills"

# Verify it exists and is a symlink
assert symlink.exists() or symlink.is_symlink(), ".claude/skills must exist"
assert symlink.is_symlink(), ".claude/skills must be a symlink"
target = os.readlink(symlink)
assert "skills" in target, f"symlink must point to skills, got: {target}"

# Verify traversal: list contents and read a file through the symlink
entries = list(symlink.iterdir())
assert len(entries) > 0, "symlink must be traversable and contain entries"

found_skill = False
for entry in entries:
    if entry.is_dir():
        skill_md = entry / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text()
            assert len(content) > 0, f"must be able to read {skill_md} through symlink"
            found_skill = True
            break
assert found_skill, "must find at least one SKILL.md through .claude/skills symlink"
print("PASS")
""", REPO],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Symlink verification failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — AGENTS.md documentation update tests
# ---------------------------------------------------------------------------

def test_agents_md_documents_skills_section():
    """AGENTS.md must have a Skills section documenting the skills system."""
    r = subprocess.run(
        ["python3", "-c", """
import sys, pathlib
repo = sys.argv[1]
agents_md = pathlib.Path(repo) / "AGENTS.md"
content = agents_md.read_text()

# Extract Skills section
lines = content.split("\\n")
section_lines = []
in_section = False
for line in lines:
    stripped = line.strip()
    if stripped.startswith("#") and "skills" in stripped.lower():
        in_section = True
        continue
    if in_section and stripped.startswith("#"):
        break
    if in_section and stripped:
        section_lines.append(stripped)

section_content = " ".join(section_lines)
assert len(section_content) >= 50, "AGENTS.md must have a Skills section with substantive content"

# Must reference skills/ and .claude/skills
assert "skills/" in content, "must reference skills/ directory"
assert ".claude/skills" in content, "must reference .claude/skills symlink"

# Must explain what skills are for
keywords = ["teach", "workflow", "agent", "handle", "specific"]
assert any(kw in section_content.lower() for kw in keywords), "must explain what skills are for"

print("PASS")
""", REPO],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"AGENTS.md Skills section check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_agents_md_documents_skill_maintenance():
    """AGENTS.md must explain skill maintenance responsibilities."""
    r = subprocess.run(
        ["python3", "-c", """
import sys, pathlib, re
repo = sys.argv[1]
agents_md = pathlib.Path(repo) / "AGENTS.md"
content = agents_md.read_text()

# Look for actionable maintenance guidance
patterns = [
    r'you are responsible for.{0,50}(skill|maintain|update)',
    r'when.{0,30}(workflow|fail|change).{0,50}(update|fix|maintain)',
    r'must.{0,30}(update|maintain|keep).{0,30}skill',
    r'responsible for.{0,30}maintain',
]
found = False
for pattern in patterns:
    if re.search(pattern, content, re.IGNORECASE):
        found = True
        break
assert found, "must explain skill maintenance responsibilities"

# Must have substantive maintenance content
keywords = ["responsible", "update", "keep", "maintain", "workflow fails"]
lines_with_kw = [l for l in content.split("\\n") if any(kw in l.lower() for kw in keywords)]
assert len(lines_with_kw) >= 1, "must have substantive maintenance content"

print("PASS")
""", REPO],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Maintenance documentation check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_agents_md_references_toml_config_skill():
    """AGENTS.md must reference the toml-config skill for CLI usage."""
    r = subprocess.run(
        ["python3", "-c", """
import sys, pathlib
repo = sys.argv[1]
agents_md = pathlib.Path(repo) / "AGENTS.md"
content = agents_md.read_text()
lines = content.split("\\n")

# Find CLI section and check for skill reference
cli_idx = None
for i, line in enumerate(lines):
    if line.strip().startswith("#") and "cli" in line.lower():
        cli_idx = i
        break

if cli_idx is not None:
    end = cli_idx + 30
    for i in range(cli_idx + 1, min(len(lines), end)):
        if lines[i].strip().startswith("#"):
            end = i
            break
    cli_ctx = "\\n".join(lines[cli_idx:end]).lower()
    assert "skill" in cli_ctx, "CLI section must reference skills for config details"

# Must reference skills/ directory
assert "skills/" in content, "must reference skills/ directory"

print("PASS")
""", REPO],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"CLI skill reference check failed: {r.stderr}"
    assert "PASS" in r.stdout
