"""
Task: payload-docker-clean-script
Repo: payloadcms/payload @ a188556e99d94c96266671b2129e5c8cb05e46a5
PR:   16000

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import re
from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """docker-clean.js must parse as valid JavaScript."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js does not exist"
    r = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, (
        f"scripts/docker-clean.js has syntax errors:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_docker_clean_script_exists():
    """A Node.js cleanup script must exist at scripts/docker-clean.js using child_process."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js must be created"
    content = script.read_text()
    # Must use child_process to run docker commands
    assert "execSync" in content or "exec(" in content or "spawn" in content, (
        "docker-clean.js should use child_process to execute docker commands"
    )


# [pr_diff] fail_to_pass
def test_docker_clean_removes_containers():
    """The cleanup script must force-remove test containers using docker rm."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js must exist"
    content = script.read_text()
    # Must use docker rm to remove containers (regex to allow different formats)
    assert re.search(r'docker\s+rm', content), (
        "Script should use 'docker rm' to force-remove containers"
    )


# [pr_diff] fail_to_pass
def test_docker_clean_handles_named_containers():
    """The cleanup script must reference the named test containers from docker-compose.yml."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js must exist"
    content = script.read_text()
    # Must reference the key container names from docker-compose.yml
    # Use regex to allow flexible formatting (spaces, newlines, template literals)
    has_postgres = re.search(r'postgres[_-]payload[_-]test', content, re.IGNORECASE)
    has_mongo = re.search(r'mongo(?:db)?[_-]payload[_-]test', content, re.IGNORECASE)
    assert has_postgres and has_mongo, (
        "Script should reference both postgres-payload-test and mongodb-payload-test containers"
    )


# [pr_diff] fail_to_pass
def test_docker_clean_runs_compose_down():
    """The cleanup script must run docker compose down for full cleanup."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js must exist"
    content = script.read_text()
    assert re.search(r'docker\s+compose', content) and "down" in content, (
        "Script should run docker compose down for full cleanup"
    )


# [pr_diff] fail_to_pass
def test_package_json_has_docker_clean():
    """package.json must define a docker:clean script that invokes the cleanup script."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "docker:clean" in scripts, (
        "package.json must have a docker:clean script"
    )
    # Verify it runs a Node.js script in the scripts/ directory
    clean_cmd = scripts["docker:clean"]
    assert "node" in clean_cmd and "scripts" in clean_cmd, (
        "docker:clean should invoke a Node.js script from the scripts/ directory"
    )


# [pr_diff] fail_to_pass
def test_docker_start_calls_clean():
    """docker:start must call docker:clean before starting services."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    start_cmd = scripts.get("docker:start", "")
    assert "docker:clean" in start_cmd or "pnpm docker:clean" in start_cmd, (
        "docker:start should invoke the cleanup step before starting"
    )
    assert "up" in start_cmd, (
        "docker:start should still run docker compose up"
    )


# [pr_diff] fail_to_pass
def test_docker_stop_removed():
    """docker:stop script should be removed from package.json."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "docker:stop" not in scripts, (
        "docker:stop should be replaced by docker:clean"
    )


# [pr_diff] fail_to_pass
def test_docker_clean_behavior():
    """The docker:clean script can be invoked and runs without errors (behavioral test)."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js must exist"
    # Run the cleanup script to verify it executes
    # The script doesn't have flags, so we just verify it runs (will error on real docker but that's ok)
    r = subprocess.run(
        ["node", str(script)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # We don't assert returncode==0 because docker may not be available in test env
    # But we verify the script was invoked and produced output (not a stub that crashes immediately)
    # The key behavioral check: script should exist and be runnable
    assert r.returncode in (0, 1), (
        f"docker-clean.js should be runnable (exit code {r.returncode}), stderr: {r.stderr}"
    )


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation/config update checks
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass
def test_claude_md_docker_clean_reference():
    """CLAUDE.md must reference docker:clean instead of docker:stop."""
    claude_md = Path(REPO) / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md must exist"
    content = claude_md.read_text()
    # Should reference docker:clean
    assert "docker:clean" in content, (
        "CLAUDE.md should reference docker:clean command"
    )
    # Should NOT reference docker:stop
    # (Use regex to check docker:stop is not mentioned in the docker services line)
    lines = content.split("\n")
    for line in lines:
        if "docker services" in line.lower() or "pnpm docker:" in line:
            assert "docker:stop" not in line, (
                "CLAUDE.md should not reference docker:stop (replaced by docker:clean)"
            )


# [config_edit] fail_to_pass
def test_contributing_md_docker_clean_reference():
    """CONTRIBUTING.md must reference docker:clean instead of docker:stop."""
    contributing_md = Path(REPO) / "CONTRIBUTING.md"
    assert contributing_md.exists(), "CONTRIBUTING.md must exist"
    content = contributing_md.read_text()
    # Should reference docker:clean
    assert "docker:clean" in content, (
        "CONTRIBUTING.md should reference docker:clean command"
    )
    # Should NOT reference docker:stop
    lines = content.split("\n")
    for line in lines:
        if "pnpm docker:" in line:
            assert "docker:stop" not in line, (
                "CONTRIBUTING.md should not reference docker:stop (replaced by docker:clean)"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "test:unit"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_type_tests():
    """Repo's TypeScript type tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "test:types", "--target", ">=5.7"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Type tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_docker_compose_config():
    """Docker compose configuration is valid (pass_to_pass)."""
    r = subprocess.run(
        ["docker", "compose", "-f", "test/docker-compose.yml", "config"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Docker compose config failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """docker-clean.js must have real cleanup logic, not just a stub."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js must exist"
    content = script.read_text()
    lines = [l.strip() for l in content.split("\n") if l.strip() and not l.strip().startswith("//")]
    assert len(lines) >= 8, (
        "docker-clean.js should have substantive logic (at least 8 non-comment lines)"
    )
    # Also check it has actual docker command execution (not just variable declarations)
    assert re.search(r'exec(Sync)?\s*\(', content), (
        "Script should actually execute docker commands via exec/execSync"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_lint_typescript_javascript():
    """pass_to_pass | CI job 'lint' → step 'Lint TypeScript/JavaScript'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint -- --quiet'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint TypeScript/JavaScript' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_lint_scss():
    """pass_to_pass | CI job 'lint' → step 'Lint SCSS'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run lint:scss'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint SCSS' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_pnpm():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run build:all'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_tests_types_types_tests():
    """pass_to_pass | CI job 'tests-types' → step 'Types Tests'"""
    r = subprocess.run(
        ["bash", "-lc", "pnpm test:types --target '>=5.7'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Types Tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_tests_unit_unit_tests():
    """pass_to_pass | CI job 'tests-unit' → step 'Unit Tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test:unit'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Unit Tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_tests_type_generation_generate_payload_types():
    """pass_to_pass | CI job 'tests-type-generation' → step 'Generate Payload Types'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm dev:generate-types fields'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate Payload Types' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_tests_type_generation_generate_graphql_schema_file():
    """pass_to_pass | CI job 'tests-type-generation' → step 'Generate GraphQL schema file'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm dev:generate-graphql-schema graphql-schema-gen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate GraphQL schema file' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_prep_prepare_prod_test_environment():
    """pass_to_pass | CI job 'E2E Prep' → step 'Prepare prod test environment'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm prepare-run-test-against-prod:ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare prod test environment' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")