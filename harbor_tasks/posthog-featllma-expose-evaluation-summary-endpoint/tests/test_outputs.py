"""
Task: posthog-featllma-expose-evaluation-summary-endpoint
Repo: PostHog/posthog @ c68338921ad4d5598a9830cca90c9e1f34c2dc8f
PR:   53656

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/posthog"
TOOLS_YAML = Path(REPO) / "products" / "llm_analytics" / "mcp" / "tools.yaml"
SKILLS_README = Path(REPO) / "products" / "llm_analytics" / "skills" / "README.md"
SKILL_FILE = (
    Path(REPO) / "products" / "llm_analytics" / "skills"
    / "exploring-llm-evaluations" / "SKILL.md"
)
SKILLS_DIR = Path(REPO) / "products" / "llm_analytics" / "skills"
LLM_ANALYTICS_DIR = Path(REPO) / "products" / "llm_analytics"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_yaml_valid_syntax():
    """tools.yaml must parse as valid YAML without errors."""
    r = subprocess.run(
        ["python3", "-c", """
import yaml
data = yaml.safe_load(open('products/llm_analytics/mcp/tools.yaml'))
assert isinstance(data, dict), f"Expected dict, got {type(data)}"
assert 'tools' in data, "Missing 'tools' key"
assert isinstance(data['tools'], dict), "tools must be a mapping"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML parse failed: {r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — validating tools.yaml schema per MCP tools guide
def test_tools_yaml_schema():
    """Tools.yaml follows MCP tools schema: enabled tools have scopes and annotations."""
    r = subprocess.run(
        ["python3", "-c", """
import yaml
import re

data = yaml.safe_load(open('products/llm_analytics/mcp/tools.yaml'))
assert 'tools' in data, "Missing 'tools' key"
tools = data['tools']

# Per implementing-mcp-tools guide:
# - Tool names must be kebab-case, max 56 chars
# - Enabled tools must have scopes (non-empty list) and annotations
kebab_pattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')

errors = []
for name, tool in tools.items():
    # Validate tool name format (kebab-case)
    if not kebab_pattern.match(name):
        errors.append(f"Tool '{name}': invalid kebab-case name")
    if len(name) > 56:
        errors.append(f"Tool '{name}': name exceeds 56 chars ({len(name)})")

    # Validate enabled tools have required fields
    if tool.get('enabled'):
        if 'scopes' not in tool or not isinstance(tool['scopes'], list) or len(tool['scopes']) == 0:
            errors.append(f"Tool '{name}': enabled but missing required 'scopes' (non-empty list)")
        if 'annotations' not in tool or not isinstance(tool['annotations'], dict):
            errors.append(f"Tool '{name}': enabled but missing required 'annotations'")
        else:
            ann = tool['annotations']
            for field in ['readOnly', 'destructive', 'idempotent']:
                if field not in ann:
                    errors.append(f"Tool '{name}': missing annotations.{field}")

if errors:
    print("SCHEMA ERRORS:")
    for e in errors:
        print(f"  - {e}")
    exit(1)

print("PASS: All tools follow schema")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Tools.yaml schema validation failed:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass — validating skills README structure
def test_skills_readme_structure():
    """Skills README lists all existing skill directories."""
    readme_content = SKILLS_README.read_text()

    # Check required sections exist
    assert "## Skills" in readme_content, "Skills README missing '## Skills' section"
    assert "## Adding a new skill" in readme_content, "Skills README missing '## Adding a new skill' section"

    # Check that existing skills are referenced
    skills_dir = Path(REPO) / "products" / "llm_analytics" / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and skill_dir.name != "__pycache__":
                # Skill should be mentioned in README
                assert skill_dir.name in readme_content, \
                    f"Skill '{skill_dir.name}' not referenced in Skills README"


# [repo_tests] pass_to_pass — validating skill files have frontmatter
def test_existing_skills_have_frontmatter():
    """All existing SKILL.md files have valid frontmatter with name and description."""
    skills_dir = Path(REPO) / "products" / "llm_analytics" / "skills"
    if not skills_dir.exists():
        return  # No skills yet

    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and skill_dir.name != "__pycache__":
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                # Check YAML frontmatter delimited by ---
                assert content.startswith('---'), \
                    f"Skill '{skill_dir.name}': Missing YAML frontmatter delimiter"
                try:
                    end = content.index('---', 3)
                    frontmatter = content[3:end]
                except ValueError:
                    raise AssertionError(f"Skill '{skill_dir.name}': Invalid frontmatter format")

                assert 'name:' in frontmatter, \
                    f"Skill '{skill_dir.name}': Missing 'name' in frontmatter"
                assert 'description:' in frontmatter, \
                    f"Skill '{skill_dir.name}': Missing 'description' in frontmatter"


# ---------------------------------------------------------------------------
# Pass-to-pass repo tests (CI/CD tests from the actual repo)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — validate mcp prompts.yaml syntax
def test_mcp_prompts_yaml_valid():
    """MCP prompts.yaml parses as valid YAML."""
    r = subprocess.run(
        ["python3", "-c", """
import yaml
data = yaml.safe_load(open('products/llm_analytics/mcp/prompts.yaml'))
assert isinstance(data, dict), f"Expected dict, got {type(data)}"
print("PASS: prompts.yaml is valid YAML")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"prompts.yaml validation failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — verify existing skills are listed in README
def test_all_existing_skills_in_readme():
    """All existing skill directories are referenced in README."""
    r = subprocess.run(
        ["python3", "-c", f"""
from pathlib import Path
readme = Path('{REPO}/products/llm_analytics/skills/README.md').read_text()
skills_dir = Path('{REPO}/products/llm_analytics/skills')

missing = []
for skill_dir in skills_dir.iterdir():
    if skill_dir.is_dir() and skill_dir.name != '__pycache__':
        skill_name = skill_dir.name
        # Check that skill is mentioned in README (either as bold name or directory reference)
        if skill_name not in readme and skill_dir.name.replace('-', ' ') not in readme.lower():
            # Try alternate forms
            display_name = skill_name.replace('-', ' ').title()
            if display_name not in readme:
                missing.append(skill_name)

if missing:
    print(f"FAIL: Skills not in README: {{missing}}")
    exit(1)
print("PASS: All skills referenced in README")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Skill README check failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — validate existing skill structure
def test_existing_skills_valid_structure():
    """Existing skill directories have valid SKILL.md with required frontmatter."""
    r = subprocess.run(
        ["python3", "-c", f"""
from pathlib import Path
import re

skills_dir = Path('{REPO}/products/llm_analytics/skills')
errors = []

for skill_dir in skills_dir.iterdir():
    if skill_dir.is_dir() and skill_dir.name != '__pycache__':
        skill_file = skill_dir / 'SKILL.md'
        if not skill_file.exists():
            errors.append(f"{{skill_dir.name}}: Missing SKILL.md")
            continue

        content = skill_file.read_text()

        # Check YAML frontmatter
        if not content.startswith('---'):
            errors.append(f"{{skill_dir.name}}: Missing frontmatter delimiter")
            continue

        try:
            end = content.index('---', 3)
            frontmatter = content[3:end]
        except ValueError:
            errors.append(f"{{skill_dir.name}}: Invalid frontmatter (no closing ---)")
            continue

        # Check required fields
        if 'name:' not in frontmatter:
            errors.append(f"{{skill_dir.name}}: Missing 'name' in frontmatter")
        if 'description:' not in frontmatter:
            errors.append(f"{{skill_dir.name}}: Missing 'description' in frontmatter")

        # Check that name matches kebab-case format
        name_match = re.search(r'^name:\\s*(.+)$', frontmatter, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            if name_value != skill_dir.name:
                errors.append(f"{{skill_dir.name}}: Frontmatter name '{{name_value}}' doesn't match directory name")

if errors:
    print("FAIL: Skill structure errors:")
    for e in errors:
        print(f"  - {{e}}")
    exit(1)
print("PASS: All skills have valid structure")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Skill structure validation failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — validate llm_analytics directory structure
def test_llm_analytics_directory_structure():
    """Required directories exist in llm_analytics product."""
    r = subprocess.run(
        ["python3", "-c", f"""
from pathlib import Path

base = Path('{REPO}/products/llm_analytics')
required_dirs = ['mcp', 'skills', 'backend']

missing = []
for d in required_dirs:
    if not (base / d).exists():
        missing.append(d)

if missing:
    print(f"FAIL: Missing directories: {{missing}}")
    exit(1)
print("PASS: Required llm_analytics directories exist")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Directory structure check failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tool_enabled_in_yaml():
    """llm-analytics-evaluation-summary-create must be enabled in tools.yaml."""
    r = subprocess.run(
        ["python3", "-c", """
import yaml
data = yaml.safe_load(open('products/llm_analytics/mcp/tools.yaml'))
tool = data['tools']['llm-analytics-evaluation-summary-create']
assert tool.get('enabled') is True, (
    f"Tool enabled={tool.get('enabled')}, expected True"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_tool_has_description_and_title():
    """Enabled tool must have title and description metadata."""
    r = subprocess.run(
        ["python3", "-c", """
import yaml
data = yaml.safe_load(open('products/llm_analytics/mcp/tools.yaml'))
tool = data['tools']['llm-analytics-evaluation-summary-create']
assert 'title' in tool, "Missing 'title' field"
assert 'description' in tool, "Missing 'description' field"
assert len(str(tool['title'])) > 0, "Title is empty"
assert len(str(tool['description'])) > 10, "Description too short"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_skill_file_exists():
    """Exploring LLM evaluations skill file must exist with evaluation content."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path
skill = Path('products/llm_analytics/skills/exploring-llm-evaluations/SKILL.md')
assert skill.exists(), f"Skill file not found: {skill}"
content = skill.read_text()
assert len(content) > 100, f"Skill file too short ({len(content)} chars)"
assert 'evaluation' in content.lower(), "Skill file doesn't mention evaluations"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_skills_readme_references_evaluations():
    """Skills README must list the exploring-llm-evaluations skill."""
    content = SKILLS_README.read_text()
    assert "exploring-llm-evaluations" in content, \
        "Skills README does not reference exploring-llm-evaluations"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .agents/skills/implementing-mcp-tools/SKILL.md:116-146
def test_tool_has_required_yaml_fields():
    """Enabled MCP tool must have scopes and annotations per implementing-mcp-tools guide."""
    r = subprocess.run(
        ["python3", "-c", """
import yaml
data = yaml.safe_load(open('products/llm_analytics/mcp/tools.yaml'))
tool = data['tools']['llm-analytics-evaluation-summary-create']

# Per implementing-mcp-tools SKILL.md "Key fields" section,
# enabled tools must have scopes and annotations.
assert 'scopes' in tool, "Missing 'scopes' (required per MCP tools guide)"
assert isinstance(tool['scopes'], list) and len(tool['scopes']) > 0, (
    "Scopes must be a non-empty list"
)

assert 'annotations' in tool, "Missing 'annotations' (required per MCP tools guide)"
ann = tool['annotations']
assert 'readOnly' in ann, "Missing annotations.readOnly"
assert 'destructive' in ann, "Missing annotations.destructive"
assert 'idempotent' in ann, "Missing annotations.idempotent"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [agent_config] fail_to_pass — .agents/skills/writing-skills/SKILL.md:42-49
def test_skill_has_frontmatter():
    """Skill file must have name and description frontmatter per writing-skills guide."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path

skill = Path('products/llm_analytics/skills/exploring-llm-evaluations/SKILL.md')
assert skill.exists(), "Skill file not found"
content = skill.read_text()

# Check YAML frontmatter delimited by ---
assert content.startswith('---'), "Missing YAML frontmatter delimiter"
end = content.index('---', 3)
frontmatter = content[3:end]

assert 'name:' in frontmatter, "Missing 'name' in frontmatter"
assert 'description:' in frontmatter, "Missing 'description' in frontmatter"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_openapi_codegen_tests_run_tests():
    """pass_to_pass | CI job 'OpenAPI codegen tests' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter=@posthog/openapi-codegen test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_agent_skills_from_source_run_migrations():
    """pass_to_pass | CI job 'Build agent skills from source' → step 'Run migrations'"""
    r = subprocess.run(
        ["bash", "-lc", 'python manage.py migrate --noinput && python manage.py setup_dev --no-data'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run migrations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_rust_services_run_cargo_build():
    """pass_to_pass | CI job 'Build Rust services' → step 'Run cargo build'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo build --all --locked --release'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run cargo build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_rust_set_up_databases():
    """pass_to_pass | CI job 'Test Rust' → step 'Set up databases'"""
    r = subprocess.run(
        ["bash", "-lc", 'python manage.py setup_test_environment'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Set up databases' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_rust_services_check_format():
    """pass_to_pass | CI job 'Lint Rust services' → step 'Check format'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo fmt -- --check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check format' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_rust_services_run_clippy():
    """pass_to_pass | CI job 'Lint Rust services' → step 'Run clippy'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo clippy --all-targets --all-features -- -D warnings'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run clippy' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_rust_services_run_cargo_check():
    """pass_to_pass | CI job 'Lint Rust services' → step 'Run cargo check'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo check --all-features'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run cargo check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_rust_services_run_cargo_shear():
    """pass_to_pass | CI job 'Lint Rust services' → step 'Run cargo shear'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo shear'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run cargo shear' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_node_js_build_check_builds_correctly():
    """pass_to_pass | CI job 'Node.js Build' → step 'Check builds correctly'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter=@posthog/nodejs build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check builds correctly' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_node_js_tests_set_up_databases_fast_path_restore_schem():
    """pass_to_pass | CI job 'Node.js Tests' → step 'Set up databases (fast path - restore schema)'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run setup:test:rust && pnpm run setup:test:persons-parity'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Set up databases (fast path - restore schema)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_node_js_tests_set_up_databases_slow_path_run_migration():
    """pass_to_pass | CI job 'Node.js Tests' → step 'Set up databases (slow path - run migrations)'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter=@posthog/nodejs setup:test && pnpm run setup:test:persons-parity'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Set up databases (slow path - run migrations)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_node_js_tests_test_postgres_parity_isolated_db():
    """pass_to_pass | CI job 'Node.js Tests' → step 'Test postgres-parity (isolated DB)'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run test:postgres-parity'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test postgres-parity (isolated DB)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")