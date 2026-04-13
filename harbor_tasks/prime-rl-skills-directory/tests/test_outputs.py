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


def test_inference_server_skill_exists():
    """skills/inference-server/SKILL.md must exist with proper content."""
    skill_file = Path(REPO) / "skills" / "inference-server" / "SKILL.md"
    assert skill_file.exists(), "skills/inference-server/SKILL.md must exist"

    content = skill_file.read_text()
    # Check for frontmatter markers
    assert "---" in content, "SKILL.md must have YAML frontmatter"
    # Check for required content sections
    assert "inference-server" in content, "Must reference inference-server skill name"
    assert "vllm" in content.lower() or "vLLM" in content, "Must mention vLLM"
    assert "entry point" in content.lower() or "uv run inference" in content, \
        "Must document the inference entry point"


def test_toml_config_skill_exists():
    """skills/toml-config/SKILL.md must exist with proper content."""
    skill_file = Path(REPO) / "skills" / "toml-config" / "SKILL.md"
    assert skill_file.exists(), "skills/toml-config/SKILL.md must exist"

    content = skill_file.read_text()
    # Check for frontmatter markers
    assert "---" in content, "SKILL.md must have YAML frontmatter"
    # Check for required content sections
    assert "toml-config" in content, "Must reference toml-config skill name"
    assert "TOML" in content, "Must mention TOML"
    assert "@" in content, "Must document the @ config syntax"


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

def test_agents_md_documents_skills_section():
    """AGENTS.md must have a Skills section documenting the skills system."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # Check for Skills section header
    assert "## Skills" in content, "AGENTS.md must have a ## Skills section"
    # Check for key concepts
    assert "skills/" in content, "Must reference skills/ directory"
    assert ".claude/skills" in content, "Must reference .claude/skills symlink"


def test_agents_md_documents_skill_maintenance():
    """AGENTS.md must explain skill maintenance responsibilities."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # Check for maintenance guidance
    assert "maintaining" in content.lower() or "maintain" in content.lower(), \
        "Must mention skill maintenance"
    # Check for explicit agent responsibility
    assert "you are responsible" in content.lower() or "responsible for" in content.lower(), \
        "Must state agent responsibility for maintaining skills"


def test_agents_md_references_toml_config_skill():
    """AGENTS.md must reference the toml-config skill for CLI usage."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # Check that CLI usage section points to skills
    assert "toml-config" in content, "AGENTS.md must reference toml-config skill"
    assert "skills/" in content, "Must reference skills/ directory for config details"
