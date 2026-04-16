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

    import pytest

    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # Check if there's frontmatter (starts with ---)
    if not content.startswith("---"):
        return  # No frontmatter, that's fine

    lines = content.split("\n")
    if len(lines) < 2 or lines[0].strip() != "---":
        return  # No valid frontmatter start

    try:
        end_idx = lines[1:].index("---") + 1
        yaml_content = "\n".join(lines[1:end_idx])
        yaml.safe_load(yaml_content)  # Validate YAML syntax
    except ValueError:
        pass  # No closing ---, not a valid frontmatter block
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML frontmatter in AGENTS.md: {e}")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that should pass on base and gold
# ---------------------------------------------------------------------------

def test_repo_toml_valid():
    """Repo's TOML config files are valid (pass_to_pass)."""
    # Ensure tomli is available
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
            tomli.load(f)  # Validate TOML syntax


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
    import ast
    import glob
    import pytest

    src_files = glob.glob(f"{REPO}/src/**/*.py", recursive=True)
    assert len(src_files) > 0, "Must have at least one Python source file"

    for py_file in src_files:
        with open(py_file) as f:
            source = f.read()
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {py_file}: {e}")


def test_repo_skill_md_frontmatter():
    """Any SKILL.md files have valid YAML frontmatter (pass_to_pass)."""
    # Ensure pyyaml is available
    try:
        import yaml
    except ImportError:
        subprocess.run(["pip", "install", "pyyaml", "-q"], check=True, capture_output=True)
        import yaml

    import pytest

    skills_dir = Path(REPO) / "skills"
    if not skills_dir.exists():
        pytest.skip("skills/ directory does not exist yet (fail-to-pass tests cover this)")

    skill_md_files = list(skills_dir.rglob("SKILL.md"))
    if not skill_md_files:
        pytest.skip("No SKILL.md files found yet (fail-to-pass tests cover this)")

    for skill_file in skill_md_files:
        content = skill_file.read_text()
        # Check for frontmatter markers
        if not content.startswith("---"):
            continue  # No frontmatter, skip validation (fail-to-pass tests check existence)

        # Extract and validate YAML frontmatter
        lines = content.split("\n")
        if len(lines) < 2 or lines[0].strip() != "---":
            continue

        try:
            end_idx = lines[1:].index("---") + 1
            yaml_content = "\n".join(lines[1:end_idx])
            yaml.safe_load(yaml_content)  # Validate YAML syntax
        except ValueError:
            pass  # No closing ---, fail-to-pass tests will catch this
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML frontmatter in {skill_file}: {e}")



# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — skills directory structure tests
# ---------------------------------------------------------------------------

def test_skills_directory_exists():
    """skills/ directory must exist with proper structure."""
    skills_dir = Path(REPO) / "skills"
    assert skills_dir.exists(), "skills/ directory must exist"
    assert skills_dir.is_dir(), "skills/ must be a directory"


def _parse_skill_frontmatter(skill_file):
    """Parse YAML frontmatter from a SKILL.md file. Returns (frontmatter_dict, body_content)."""
    try:
        import yaml
    except ImportError:
        subprocess.run(["pip", "install", "pyyaml", "-q"], check=True, capture_output=True)
        import yaml

    content = skill_file.read_text()
    if not content.startswith("---"):
        return {}, content

    lines = content.split("\n")
    if len(lines) < 2 or lines[0].strip() != "---":
        return {}, content

    try:
        end_idx = lines[1:].index("---") + 1
        yaml_content = "\n".join(lines[1:end_idx])
        frontmatter = yaml.safe_load(yaml_content) or {}
        body = "\n".join(lines[end_idx + 1:])
        return frontmatter, body
    except (ValueError, yaml.YAMLError):
        return {}, content


def test_inference_server_skill_exists():
    """skills/inference-server/SKILL.md must exist with proper content."""
    skill_file = Path(REPO) / "skills" / "inference-server" / "SKILL.md"
    assert skill_file.exists(), "skills/inference-server/SKILL.md must exist"

    frontmatter, body = _parse_skill_frontmatter(skill_file)

    # Verify required frontmatter fields per instruction
    assert "name" in frontmatter, "SKILL.md must have name field in frontmatter"
    assert "description" in frontmatter, "SKILL.md must have description field in frontmatter"

    # Body must have substantive content about running inference server
    assert len(body.strip()) > 100, "SKILL.md body must have substantive content"

    # Behavioral check: does it document how to start the server using the entry point?
    # Look for evidence of actual command usage, not just the word "entry point"
    assert "uv run inference" in body, "SKILL.md must document how to run the inference entry point"

    # Behavioral check: does it document custom endpoints?
    # Check for at least one of the required custom endpoints being documented
    custom_endpoints = ["/v1/chat/completions/tokens", "/update_weights", "/load_lora_adapter", "/init_broadcaster"]
    has_endpoint = any(ep in body for ep in custom_endpoints)
    assert has_endpoint, "SKILL.md must document at least one custom endpoint"


def test_toml_config_skill_exists():
    """skills/toml-config/SKILL.md must exist with proper content."""
    skill_file = Path(REPO) / "skills" / "toml-config" / "SKILL.md"
    assert skill_file.exists(), "skills/toml-config/SKILL.md must exist"

    frontmatter, body = _parse_skill_frontmatter(skill_file)

    # Verify required frontmatter fields per instruction
    assert "name" in frontmatter, "SKILL.md must have name field in frontmatter"
    assert "description" in frontmatter, "SKILL.md must have description field in frontmatter"

    # Body must have substantive content about TOML configs
    assert len(body.strip()) > 100, "SKILL.md body must have substantive content"

    # Behavioral check: does it document config file usage with @ syntax?
    assert "@" in body and "config" in body.lower(), "SKILL.md must document @ config syntax"

    # Behavioral check: does it document CLI override syntax?
    # Look for actual CLI override examples (--key value pattern)
    assert "--" in body, "SKILL.md must document CLI override syntax"


def test_claude_skills_symlink_exists():
    """.claude/skills symlink must point to ../skills."""
    claude_skills = Path(REPO) / ".claude" / "skills"
    assert claude_skills.exists() or claude_skills.is_symlink(), \
        ".claude/skills symlink must exist"

    # Check it's a symlink pointing to the right place
    if claude_skills.is_symlink():
        target = os.readlink(claude_skills)
        assert "skills" in target, f".claude/skills must point to skills/, got: {target}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — AGENTS.md documentation update tests
# ---------------------------------------------------------------------------

def _has_section(content, section_marker):
    """Check if content has a section with the given marker (## Header or similar)."""
    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()
        # Check for markdown headers (##, ###, etc.) followed by section name
        if stripped.startswith("#") and section_marker.lower() in stripped.lower():
            return True
    return False


def _section_has_content(content, section_marker, min_length=50):
    """Check if a section exists and has substantive content."""
    lines = content.split("\n")
    in_section = False
    section_lines = []

    for line in lines:
        stripped = line.strip()
        # Check for section header
        if stripped.startswith("#") and section_marker.lower() in stripped.lower():
            in_section = True
            continue
        # Check if we've hit another header (end of section)
        if in_section and stripped.startswith("#"):
            break
        # Collect content lines
        if in_section and stripped:
            section_lines.append(stripped)

    section_content = " ".join(section_lines)
    return len(section_content) >= min_length


def test_agents_md_documents_skills_section():
    """AGENTS.md must have a Skills section documenting the skills system."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # Behavioral check: there must be a section about skills
    assert _section_has_content(content, "skills", min_length=50), \
        "AGENTS.md must have a Skills section with substantive content"

    # Behavioral check: must reference both skills/ directory and .claude/skills
    assert "skills/" in content, "AGENTS.md must reference skills/ directory"
    assert ".claude/skills" in content, "AGENTS.md must reference .claude/skills symlink"

    # Behavioral check: must explain what skills are for
    skills_section_found = False
    for line in content.split("\n"):
        if "skills" in line.lower() and ("teach" in line.lower() or "workflow" in line.lower()):
            skills_section_found = True
            break
    assert skills_section_found, "AGENTS.md must explain what skills are for"


def test_agents_md_documents_skill_maintenance():
    """AGENTS.md must explain skill maintenance responsibilities."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # Behavioral check: must explain agent responsibility for maintaining skills
    # Look for content about updating/keeping skills current when code changes
    maintenance_keywords = ["responsible", "update", "keep", "maintain", "when a workflow fails"]
    has_maintenance = any(kw in content.lower() for kw in maintenance_keywords)
    assert has_maintenance, "AGENTS.md must explain skill maintenance responsibilities"

    # Behavioral check: must have substantive content about maintenance
    # (not just a passing mention)
    maintenance_related_lines = [l for l in content.split("\n")
                                  if any(kw in l.lower() for kw in ["responsible", "update", "keep skills"])]
    assert len(maintenance_related_lines) >= 1, \
        "AGENTS.md must have substantive content about skill maintenance"


def test_agents_md_references_toml_config_skill():
    """AGENTS.md must reference the toml-config skill for CLI usage."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # Behavioral check: CLI usage section should direct users to skills
    # for detailed config documentation
    cli_section_found = False
    for line in content.split("\n"):
        if "cli" in line.lower() or "command" in line.lower() or "config" in line.lower():
            if "skill" in content[content.index(line):content.index(line)+200].lower():
                cli_section_found = True
                break
    assert cli_section_found, "AGENTS.md CLI section must reference skills for config details"

    # Behavioral check: must point to skills directory for additional info
    assert "skills/" in content, "AGENTS.md must reference skills/ directory for additional config details"