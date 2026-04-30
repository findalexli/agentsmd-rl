"""
Task: payload-chore-add-docker-clean-script
Repo: payloadcms/payload @ a188556e99d94c96266671b2129e5c8cb05e46a5
PR:   16000

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — new script must exist and be valid JS
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_docker_clean_js_syntax():
    """scripts/docker-clean.js must exist and be valid JavaScript (ESM)."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js does not exist"
    # Use --check on the file directly (no --input-type flag, incompatible with file paths in Node 22+)
    r = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"JS syntax error:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_docker_clean_removes_all_containers():
    """docker-clean.js must force-remove all named test containers."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js does not exist"
    content = script.read_text()

    expected_containers = [
        "postgres-payload-test",
        "mongodb-payload-test",
        "mongot-payload-test",
        "mongodb-atlas-payload-test",
        "localstack_demo",
    ]
    for name in expected_containers:
        assert name in content, f"docker-clean.js missing container: {name}"

    assert "docker rm -f" in content, "docker-clean.js must use 'docker rm -f' to force-remove"


# [pr_diff] fail_to_pass
def test_docker_clean_runs_compose_down():
    """docker-clean.js must also run docker compose down with -v and --remove-orphans."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js does not exist"
    content = script.read_text()

    assert "docker compose" in content, "docker-clean.js must run docker compose"
    assert "down" in content, "docker-clean.js must run compose down"
    assert "-v" in content, "docker-clean.js must pass -v to remove volumes"
    assert "--remove-orphans" in content, "docker-clean.js must pass --remove-orphans"


# [pr_diff] fail_to_pass
def test_package_json_scripts():
    """package.json must define docker:clean and update docker:start to chain it."""
    r = subprocess.run(
        ["node", "-e", """
const pkg = require('./package.json');
const scripts = pkg.scripts;
const result = {
    hasClean: 'docker:clean' in scripts,
    cleanValue: scripts['docker:clean'] || '',
    hasStop: 'docker:stop' in scripts,
    startValue: scripts['docker:start'] || '',
    startChainsClean: (scripts['docker:start'] || '').includes('docker:clean'),
};
console.log(JSON.stringify(result));
"""],
        cwd=REPO, capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Failed to parse package.json:\n{r.stderr}"

    data = json.loads(r.stdout.strip())
    assert data["hasClean"], "package.json must have a docker:clean script"
    assert "docker-clean.js" in data["cleanValue"], \
        f"docker:clean should run docker-clean.js, got: {data['cleanValue']}"
    assert not data["hasStop"], "docker:stop should be removed from package.json"
    assert data["startChainsClean"], \
        f"docker:start should chain docker:clean, got: {data['startValue']}"


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_docker_commands():
    """CLAUDE.md must reference docker:clean instead of docker:stop."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    assert "docker:clean" in content, "CLAUDE.md should reference docker:clean"
    # Ensure docker:stop is no longer documented as a command
    lines = content.splitlines()
    has_stop_ref = any("docker:stop" in l for l in lines if "docker:" in l)
    assert not has_stop_ref, "CLAUDE.md should not reference docker:stop anymore"


# [pr_diff] fail_to_pass
def test_contributing_md_docker_commands():
    """CONTRIBUTING.md must reference docker:clean instead of docker:stop."""
    contributing = Path(REPO) / "CONTRIBUTING.md"
    content = contributing.read_text()

    assert "docker:clean" in content, "CONTRIBUTING.md should reference docker:clean"
    # Check the bash code block section specifically
    lines = content.splitlines()
    has_stop_ref = any("docker:stop" in l for l in lines if "pnpm" in l and "docker" in l)
    assert not has_stop_ref, "CONTRIBUTING.md should not reference pnpm docker:stop anymore"


# [pr_diff] fail_to_pass
def test_docker_compose_yml_comments():
    """test/docker-compose.yml usage comments must reference docker:clean."""
    dc = Path(REPO) / "test" / "docker-compose.yml"
    content = dc.read_text()

    # Check the Usage comment block at the top
    usage_lines = []
    in_usage = False
    for line in content.splitlines():
        if "Usage:" in line:
            in_usage = True
        elif in_usage and line.strip().startswith("#"):
            usage_lines.append(line)
        elif in_usage and not line.strip().startswith("#"):
            break

    usage_text = "\n".join(usage_lines)
    assert "docker:clean" in usage_text, \
        f"docker-compose.yml Usage block should reference docker:clean, got:\n{usage_text}"
    assert "docker:stop" not in usage_text, \
        "docker-compose.yml Usage block should not reference docker:stop"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI checks that should pass at base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """Repo's package.json must be valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.stringify(require('./package.json')); console.log('Valid JSON')"],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"package.json is not valid JSON:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_scripts_syntax():
    """Repo's script files must have valid JavaScript syntax (pass_to_pass)."""
    scripts_dir = Path(REPO) / "scripts"
    js_files = list(scripts_dir.glob("*.js"))
    assert len(js_files) > 0, "No .js files found in scripts/ directory"

    for js_file in js_files:
        r = subprocess.run(
            ["node", "--check", str(js_file)],
            capture_output=True, text=True, timeout=15,
        )
        assert r.returncode == 0, f"Syntax error in {js_file.name}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_docker_compose_yml_readable():
    """Repo's docker-compose.yml must be readable and well-formed (pass_to_pass)."""
    dc = Path(REPO) / "test" / "docker-compose.yml"
    assert dc.exists(), "test/docker-compose.yml does not exist"

    # Read and validate it's not empty and contains expected content
    content = dc.read_text()
    assert "services:" in content, "docker-compose.yml missing 'services' section"
    assert "version:" in content or "name:" in content, "docker-compose.yml missing version or name"
