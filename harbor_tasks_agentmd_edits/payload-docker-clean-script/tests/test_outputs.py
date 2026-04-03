"""
Task: payload-docker-clean-script
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
    """A Node.js cleanup script must exist at scripts/docker-clean.js."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js must be created"
    content = script.read_text()
    # Must use child_process to run docker commands
    assert "execSync" in content or "exec(" in content or "spawn" in content, (
        "docker-clean.js should use child_process to execute docker commands"
    )


# [pr_diff] fail_to_pass
def test_docker_clean_removes_named_containers():
    """The cleanup script must force-remove the named test containers."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js must exist"
    content = script.read_text()
    # Must reference the key container names from docker-compose.yml
    assert "postgres-payload-test" in content, (
        "Script should remove postgres-payload-test container"
    )
    assert "mongodb-payload-test" in content, (
        "Script should remove mongodb-payload-test container"
    )
    assert "docker rm" in content or "docker remove" in content, (
        "Script should use docker rm to force-remove containers"
    )


# [pr_diff] fail_to_pass
def test_docker_clean_runs_compose_down():
    """The cleanup script must also run docker compose down."""
    script = Path(REPO) / "scripts" / "docker-clean.js"
    assert script.exists(), "scripts/docker-clean.js must exist"
    content = script.read_text()
    assert "docker compose" in content and "down" in content, (
        "Script should run docker compose down for full cleanup"
    )


# [pr_diff] fail_to_pass
def test_package_json_has_docker_clean():
    """package.json must define a docker:clean script."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "docker:clean" in scripts, (
        "package.json must have a docker:clean script"
    )
    clean_cmd = scripts["docker:clean"]
    assert "docker-clean" in clean_cmd or "docker_clean" in clean_cmd, (
        "docker:clean should invoke the cleanup script"
    )


# [pr_diff] fail_to_pass
def test_docker_start_calls_clean():
    """docker:start must call docker:clean before starting services."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    start_cmd = scripts.get("docker:start", "")
    assert "docker:clean" in start_cmd or "docker-clean" in start_cmd, (
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


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation/config update checks
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


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
    assert len(lines) >= 5, (
        "docker-clean.js should have substantive logic (at least 5 non-comment lines)"
    )
