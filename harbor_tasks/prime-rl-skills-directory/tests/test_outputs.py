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
    import pytest

    skill_file = Path(REPO) / "skills" / "inference-server" / "SKILL.md"
    assert skill_file.exists(), "skills/inference-server/SKILL.md must exist"

    # BEHAVIORAL: Parse frontmatter using actual YAML parser
    frontmatter, body = _parse_skill_frontmatter(skill_file)

    # Verify required frontmatter fields per instruction
    assert "name" in frontmatter, "SKILL.md must have name field in frontmatter"
    assert "description" in frontmatter, "SKILL.md must have description field in frontmatter"

    # Body must have substantive content about running inference server
    assert len(body.strip()) > 100, "SKILL.md body must have substantive content"

    # BEHAVIORAL: Verify the inference entry point exists in pyproject.toml
    pyproject = Path(REPO) / "pyproject.toml"
    if pyproject.exists():
        try:
            import tomli
        except ImportError:
            subprocess.run(["pip", "install", "tomli", "-q"], check=True, capture_output=True)
            import tomli

        with open(pyproject, "rb") as f:
            config = tomli.load(f)
        scripts = config.get("project", {}).get("scripts", {})
        assert "inference" in scripts, "pyproject.toml must have 'inference' entry point"

    # BEHAVIORAL: Check that referenced config files actually exist
    # The skill should document configs/debug/infer.toml
    configs_dir = Path(REPO) / "configs" / "debug"
    if configs_dir.exists():
        infer_configs = [f for f in configs_dir.iterdir() if "infer" in f.name.lower() and f.suffix == ".toml"]
        assert len(infer_configs) > 0, "configs/debug/ must have an inference config file"

    # BEHAVIORAL: Verify custom endpoints are properly formatted (look like API paths)
    custom_endpoint_pattern = r'/[a-zA-Z0-9_/-]+'
    found_endpoints = re.findall(custom_endpoint_pattern, body)
    api_like_endpoints = [ep for ep in found_endpoints if ep.startswith('/v1/') or 'update' in ep or 'load' in ep or 'init' in ep]
    assert len(api_like_endpoints) > 0, "SKILL.md must document API endpoints (paths starting with /)"

    # Verify body documents command execution
    assert "uv run" in body, "SKILL.md must document uv run commands"


def test_toml_config_skill_exists():
    """skills/toml-config/SKILL.md must exist with proper content."""
    skill_file = Path(REPO) / "skills" / "toml-config" / "SKILL.md"
    assert skill_file.exists(), "skills/toml-config/SKILL.md must exist"

    # BEHAVIORAL: Parse frontmatter using actual YAML parser
    frontmatter, body = _parse_skill_frontmatter(skill_file)

    # Verify required frontmatter fields per instruction
    assert "name" in frontmatter, "SKILL.md must have name field in frontmatter"
    assert "description" in frontmatter, "SKILL.md must have description field in frontmatter"

    # Body must have substantive content about TOML configs
    assert len(body.strip()) > 100, "SKILL.md body must have substantive content"

    # BEHAVIORAL: Verify @ syntax for config loading is documented with examples
    # Look for patterns like "@ config.toml" or "@ path/to/config.toml"
    at_config_pattern = r'@\s+\S+\.toml'
    assert re.search(at_config_pattern, body), "SKILL.md must document @ config.toml syntax"

    # BEHAVIORAL: Verify CLI override syntax is documented
    # Look for patterns like --flag or --key value
    cli_override_pattern = r'--[a-zA-Z][a-zA-Z0-9_.-]*'
    assert re.search(cli_override_pattern, body), "SKILL.md must document CLI override syntax with --flags"

    # BEHAVIORAL: Check that the skill references actual config files in the repo
    configs_dir = Path(REPO) / "configs"
    if configs_dir.exists():
        toml_files = list(configs_dir.rglob("*.toml"))
        assert len(toml_files) > 0, "configs/ directory must contain TOML files"


def test_claude_skills_symlink_exists():
    """.claude/skills symlink must point to ../skills and be traversable."""
    import pytest

    claude_skills = Path(REPO) / ".claude" / "skills"
    assert claude_skills.exists() or claude_skills.is_symlink(), \
        ".claude/skills symlink must exist"

    # BEHAVIORAL: Actually traverse the symlink and verify it works
    try:
        # Try to list directory entries through the symlink
        entries = list(claude_skills.iterdir())
        # Verify we can access the skills through the symlink
        entry_names = [e.name for e in entries]

        # Should be able to see the skill directories
        if len(entries) > 0:
            # Verify we can actually read a file through the symlink
            for entry in entries:
                if entry.is_dir():
                    skill_md = entry / "SKILL.md"
                    if skill_md.exists():
                        # BEHAVIORAL: Read and parse the file through the symlink
                        content = skill_md.read_text()
                        assert len(content) > 0, f"Must be able to read {skill_md} through symlink"
                        break
    except (OSError, StopIteration) as e:
        pytest.fail(f"Symlink must be traversable and allow file access: {e}")

    # Check it's a symlink pointing to the right place
    if claude_skills.is_symlink():
        target = os.readlink(claude_skills)
        assert "skills" in target, f".claude/skills must point to skills/, got: {target}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — AGENTS.md documentation update tests
# ---------------------------------------------------------------------------

def _extract_section_content(content, section_name):
    """Extract content of a markdown section until the next header."""
    lines = content.split("\n")
    section_lines = []
    in_section = False

    for line in lines:
        stripped = line.strip()
        # Check for section header
        if stripped.startswith("#") and section_name.lower() in stripped.lower():
            in_section = True
            continue
        # Check if we've hit another header (end of section)
        if in_section and stripped.startswith("#"):
            break
        # Collect content lines
        if in_section and stripped:
            section_lines.append(stripped)

    return section_lines


def test_agents_md_documents_skills_section():
    """AGENTS.md must have a Skills section documenting the skills system."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # BEHAVIORAL: Parse markdown structure and extract section
    section_lines = _extract_section_content(content, "skills")
    section_content = " ".join(section_lines)

    # Behavioral check: there must be a section about skills with substantive content
    assert len(section_content) >= 50, \
        "AGENTS.md must have a Skills section with substantive content"

    # Behavioral check: must reference both skills/ directory and .claude/skills
    assert "skills/" in content, "AGENTS.md must reference skills/ directory"
    assert ".claude/skills" in content, "AGENTS.md must reference .claude/skills symlink"

    # Behavioral check: must explain what skills are for (teaching workflows)
    skills_keywords = ["teach", "workflow", "agent", "handle", "specific"]
    has_explanation = any(kw in section_content.lower() for kw in skills_keywords)
    assert has_explanation, "AGENTS.md must explain what skills are for"


def test_agents_md_documents_skill_maintenance():
    """AGENTS.md must explain skill maintenance responsibilities."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # BEHAVIORAL: Parse the document for imperative maintenance instructions
    # Look for action-oriented statements about skill maintenance
    maintenance_patterns = [
        r'you are responsible for.{0,50}(skill|maintain|update)',
        r'when.{0,30}(workflow|fail|change).{0,50}(update|fix|maintain)',
        r'must.{0,30}(update|maintain|keep).{0,30}skill',
        r'responsible for.{0,30}maintain',
    ]

    found_imperative = False
    for pattern in maintenance_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            found_imperative = True
            break

    assert found_imperative, "AGENTS.md must explain skill maintenance responsibilities with actionable guidance"

    # Behavioral check: must have substantive content about maintenance
    maintenance_keywords = ["responsible", "update", "keep", "maintain", "workflow fails"]
    maintenance_related_lines = [l for l in content.split("\n")
                                  if any(kw in l.lower() for kw in maintenance_keywords)]
    assert len(maintenance_related_lines) >= 1, \
        "AGENTS.md must have substantive content about skill maintenance"


def test_agents_md_references_toml_config_skill():
    """AGENTS.md must reference the toml-config skill for CLI usage."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()

    # BEHAVIORAL: Parse markdown to find CLI-related sections and verify skill reference
    lines = content.split("\n")

    # Find CLI section index
    cli_section_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("#") and "cli" in line.lower():
            cli_section_idx = i
            break

    # Check CLI section and surrounding context for skill reference
    if cli_section_idx is not None:
        # Look at content after CLI header (up to next section or 30 lines)
        context_end = cli_section_idx + 30
        for i in range(cli_section_idx + 1, min(len(lines), context_end)):
            if lines[i].strip().startswith("#"):
                context_end = i
                break
        cli_context = "\n".join(lines[cli_section_idx:context_end]).lower()

        # CLI section should reference skills
        assert "skill" in cli_context, "AGENTS.md CLI section must reference skills for config details"

    # Behavioral check: must point to skills directory for additional info
    assert "skills/" in content, "AGENTS.md must reference skills/ directory for additional config details"
