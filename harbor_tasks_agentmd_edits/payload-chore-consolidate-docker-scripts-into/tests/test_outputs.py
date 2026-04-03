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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code / infrastructure changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_docker_start_uses_profiles():
    """docker:start script uses --profile all and cleans volumes before starting."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = pkg.get("scripts", {})
    start_cmd = scripts.get("docker:start", "")
    assert "--profile all" in start_cmd, (
        f"docker:start should use --profile all, got: {start_cmd}"
    )
    assert "up" in start_cmd, "docker:start should bring services up"
    assert "down -v" in start_cmd or "down" in start_cmd, (
        "docker:start should tear down old containers first"
    )


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
    compose_path = Path(REPO) / "test" / "docker-compose.yml"
    content = compose_path.read_text()
    for profile in ["postgres", "mongodb", "mongodb-atlas", "storage"]:
        assert profile in content, (
            f"Profile '{profile}' not found in docker-compose.yml"
        )
    assert re.search(r"profiles:\s*\[", content), (
        "docker-compose.yml should define profiles arrays on services"
    )


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
    action_path = Path(REPO) / ".github" / "actions" / "start-database" / "action.yml"
    content = action_path.read_text()
    assert "test/docker-compose.yml" in content, (
        "CI action should reference test/docker-compose.yml"
    )
    assert "--profile" in content, "CI action should use --profile flag"
    # Must not reference old per-database compose paths
    assert "test/__helpers/shared/db/mongodb/docker-compose.yml" not in content, (
        "CI action should not reference old mongodb compose path"
    )
    assert "test/__helpers/shared/db/postgres/docker-compose.yml" not in content, (
        "CI action should not reference old postgres compose path"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — agent config / documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
