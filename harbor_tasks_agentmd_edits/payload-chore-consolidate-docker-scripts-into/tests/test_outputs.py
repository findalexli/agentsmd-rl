"""
Task: payload-chore-consolidate-docker-scripts-into
Repo: payloadcms/payload @ 5efc2ffa032b6b5f908b9c94c34276f23a62b71d
PR:   #15974

Consolidate 18 per-database docker scripts and 4 separate docker-compose files
into 3 unified scripts and 1 docker-compose.yml with Docker Compose profiles.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """package.json must parse as valid JSON."""
    pkg_path = Path(REPO) / "package.json"
    json.loads(pkg_path.read_text())


# [static] pass_to_pass
def test_docker_compose_syntax():
    """test/docker-compose.yml must be valid YAML with required structure."""
    import yaml

    compose_path = Path(REPO) / "test" / "docker-compose.yml"
    content = compose_path.read_text()
    data = yaml.safe_load(content)

    # Must have services
    assert "services" in data, "docker-compose.yml must have services section"
    services = data["services"]

    # Required services must exist
    required_services = ["postgres", "mongodb", "mongodb-atlas", "localstack"]
    for svc in required_services:
        assert svc in services, f"Required service '{svc}' not found in docker-compose.yml"

    # Services must have profiles defined
    for svc in ["postgres", "mongodb", "mongodb-atlas", "localstack"]:
        profiles = services[svc].get("profiles", [])
        assert "all" in profiles, f"Service '{svc}' must have 'all' profile"


# [static] pass_to_pass
def test_ci_action_syntax():
    """.github/actions/start-database/action.yml must be valid YAML."""
    import yaml

    action_path = Path(REPO) / ".github" / "actions" / "start-database" / "action.yml"
    content = action_path.read_text()
    data = yaml.safe_load(content)

    # Must have runs.steps structure
    assert "runs" in data, "action.yml must have runs section"
    assert "steps" in data["runs"], "action.yml must have steps"


# [static] pass_to_pass
def test_docker_compose_schema():
    """test/docker-compose.yml has valid schema with name and volumes."""
    import yaml

    compose_path = Path(REPO) / "test" / "docker-compose.yml"
    content = compose_path.read_text()
    data = yaml.safe_load(content)

    # Must have a name field (compose project name)
    assert "name" in data, "docker-compose.yml must have a name field for the project"
    assert data["name"], "docker-compose.yml name must not be empty"

    # Must have volumes section for persistent data
    assert "volumes" in data, "docker-compose.yml must have volumes section"
    volumes = data["volumes"]
    required_volumes = ["postgres_data", "mongodb_data", "mongodb_configdb"]
    for vol in required_volumes:
        assert vol in volumes, f"Required volume '{vol}' not defined in docker-compose.yml"

    # Check that healthcheck is configured for databases
    for svc in ["postgres", "mongodb"]:
        service = data["services"].get(svc, {})
        assert "healthcheck" in service, f"Service '{svc}' must have healthcheck configured"


# [static] pass_to_pass
def test_package_scripts_consistent():
    """package.json docker scripts are consistent and reference valid compose file."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = pkg.get("scripts", {})

    # docker:start should reference test/docker-compose.yml
    docker_start = scripts.get("docker:start", "")
    if docker_start:
        assert "test/docker-compose.yml" in docker_start, (
            "docker:start must reference test/docker-compose.yml"
        )

    # docker:stop should reference test/docker-compose.yml
    docker_stop = scripts.get("docker:stop", "")
    if docker_stop:
        assert "test/docker-compose.yml" in docker_stop, (
            "docker:stop must reference test/docker-compose.yml"
        )


# [static] pass_to_pass
def test_ci_action_valid():
    """.github/actions/start-database/action.yml references valid profiles and compose file."""
    import yaml

    action_path = Path(REPO) / ".github" / "actions" / "start-database" / "action.yml"
    content = action_path.read_text()
    data = yaml.safe_load(content)

    # Convert steps to string for validation
    steps_str = json.dumps(data.get("runs", {}).get("steps", []))

    # Must reference the unified compose file (not old per-db paths)
    assert "test/docker-compose.yml" in steps_str, (
        "CI action must reference unified test/docker-compose.yml"
    )

    # Must use valid profile values
    valid_profiles = ["postgres", "mongodb", "mongodb-atlas", "all"]
    found_profile = False
    for profile in valid_profiles:
        if f"--profile {profile}" in steps_str:
            found_profile = True
            break
    assert found_profile, (
        "CI action must use a valid --profile flag (postgres, mongodb, mongodb-atlas, or all)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - Real CI/CD gates using subprocess.run()
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - CI/CD gate using subprocess.run()
def test_docker_start_script_shell_valid():
    """docker:start script has valid shell syntax (pass_to_pass)."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = pkg.get("scripts", {})
    start_cmd = scripts.get("docker:start", "")

    # Skip if not present (will be caught by other tests)
    if not start_cmd:
        return

    # Validate shell syntax using bash -n
    r = subprocess.run(
        ["bash", "-n", "-c", start_cmd],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"docker:start command has invalid bash syntax: {r.stderr}"


# [repo_tests] pass_to_pass - CI/CD gate using subprocess.run()
def test_docker_stop_script_shell_valid():
    """docker:stop script has valid shell syntax (pass_to_pass)."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = pkg.get("scripts", {})
    stop_cmd = scripts.get("docker:stop", "")

    # Skip if not present (will be caught by other tests)
    if not stop_cmd:
        return

    # Validate shell syntax using bash -n
    r = subprocess.run(
        ["bash", "-n", "-c", stop_cmd],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"docker:stop command has invalid bash syntax: {r.stderr}"


# [repo_tests] pass_to_pass - CI/CD gate using subprocess.run()
def test_ci_action_shell_valid():
    """CI action shell commands have valid syntax (pass_to_pass)."""
    import yaml

    action_path = Path(REPO) / ".github" / "actions" / "start-database" / "action.yml"
    content = action_path.read_text()
    data = yaml.safe_load(content)

    # Extract all shell commands from the action
    steps = data.get("runs", {}).get("steps", [])
    shell_commands = []
    for step in steps:
        if "run" in step:
            shell_commands.append(step["run"])

    # Validate each shell command
    for i, cmd in enumerate(shell_commands):
        r = subprocess.run(
            ["bash", "-n", "-c", cmd],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"CI action step {i+1} has invalid shell syntax: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - code / infrastructure changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_docker_start_uses_profiles():
    """docker:start script uses --profile all and cleans volumes before starting."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = pkg.get("scripts", {})
    start_cmd = scripts.get("docker:start", "")

    # Verify command structure
    assert "--profile all" in start_cmd, (
        f"docker:start should use --profile all, got: {start_cmd}"
    )
    assert "up" in start_cmd, "docker:start should bring services up"
    assert "down -v" in start_cmd or "down" in start_cmd, (
        "docker:start should tear down old containers first"
    )

    # Behavioral test: validate the shell command structure
    r = subprocess.run(
        ["bash", "-n", "-c", start_cmd],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"docker:start command has invalid bash syntax: {r.stderr}"


# [pr_diff] fail_to_pass
def test_docker_stop_uses_profiles():
    """docker:stop script uses --profile all to stop all services."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = pkg.get("scripts", {})
    stop_cmd = scripts.get("docker:stop", "")

    assert "--profile all" in stop_cmd, (
        f"docker:stop should use --profile all, got: {stop_cmd}"
    )
    assert "down" in stop_cmd, "docker:stop should stop services with 'down'"

    # Behavioral test: validate the shell command structure
    r = subprocess.run(
        ["bash", "-n", "-c", stop_cmd],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"docker:stop command has invalid bash syntax: {r.stderr}"


# [pr_diff] fail_to_pass
def test_old_docker_scripts_removed():
    """Per-database docker scripts (docker:mongodb:start, etc.) must be removed."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = pkg.get("scripts", {})
    old_scripts = [
        k for k in scripts
        if re.match(r"docker:(mongodb|postgres|mongodb-atlas):", k)
    ]
    assert old_scripts == [], (
        f"Old per-database docker scripts still present: {old_scripts}"
    )


# [pr_diff] fail_to_pass
def test_compose_profiles_defined():
    """test/docker-compose.yml defines profiles for postgres, mongodb, mongodb-atlas, storage."""
    import yaml

    compose_path = Path(REPO) / "test" / "docker-compose.yml"
    content = compose_path.read_text()
    data = yaml.safe_load(content)

    services = data.get("services", {})
    required_profiles = ["postgres", "mongodb", "mongodb-atlas", "storage"]

    for profile in required_profiles:
        # Find at least one service with this profile
        found = any(
            profile in svc.get("profiles", [])
            for svc in services.values()
        )
        assert found, f"Profile '{profile}' not assigned to any service in docker-compose.yml"


# [pr_diff] fail_to_pass
def test_old_compose_files_removed():
    """Separate per-database docker-compose files must be deleted."""
    old_files = [
        "test/__helpers/shared/db/postgres/docker-compose.yml",
        "test/__helpers/shared/db/mongodb/docker-compose.yml",
        "test/__helpers/shared/db/mongodb-atlas/docker-compose.yml",
        "packages/storage-s3/docker-compose.yml",
    ]
    for f in old_files:
        p = Path(REPO) / f
        assert not p.exists(), f"Old compose file should be removed: {f}"


# [pr_diff] fail_to_pass
def test_ci_action_uses_unified_compose():
    """CI start-database action references unified test/docker-compose.yml with --profile."""
    import yaml

    action_path = Path(REPO) / ".github" / "actions" / "start-database" / "action.yml"
    content = action_path.read_text()
    data = yaml.safe_load(content)

    # Convert steps to string for checking
    steps_str = json.dumps(data.get("runs", {}).get("steps", []))

    # Must reference unified compose file
    assert "test/docker-compose.yml" in steps_str, (
        "CI action should reference test/docker-compose.yml"
    )

    # Must use --profile flag
    assert "--profile" in steps_str, "CI action should use --profile flag"

    # Must not reference old per-database compose paths
    old_paths = [
        "test/__helpers/shared/db/mongodb/docker-compose.yml",
        "test/__helpers/shared/db/postgres/docker-compose.yml",
        "test/__helpers/shared/db/mongodb-atlas/docker-compose.yml",
    ]
    for old_path in old_paths:
        assert old_path not in steps_str, (
            f"CI action should not reference old compose path: {old_path}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) - documentation/config consistency
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
def test_contributing_docs_reference_unified_commands():
    """CONTRIBUTING.md documents the unified docker:start/docker:stop commands."""
    contrib_path = Path(REPO) / "CONTRIBUTING.md"
    content = contrib_path.read_text()

    # Should reference new unified commands
    assert "pnpm docker:start" in content, (
        "CONTRIBUTING.md should reference pnpm docker:start"
    )
    assert "pnpm docker:stop" in content, (
        "CONTRIBUTING.md should reference pnpm docker:stop"
    )


# [agent_config] pass_to_pass
def test_claude_md_references_docker_test():
    """CLAUDE.md references docker:test instead of removed docker:restart."""
    claude_path = Path(REPO) / "CLAUDE.md"
    content = claude_path.read_text()

    # Should reference docker:test (new) instead of docker:restart (removed)
    assert "docker:test" in content, (
        "CLAUDE.md should reference docker:test command"
    )
