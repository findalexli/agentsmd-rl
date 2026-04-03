"""
Task: payload-mongodb-port-conflict
Repo: payloadcms/payload @ 4c91d049c2a76b41ca10b770ec67338a9f97904b
PR:   14993

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / YAML validity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Docker compose YAML files must be valid YAML."""
    import json

    for compose_path in [
        "test/helpers/db/mongodb/docker-compose.yml",
        "test/helpers/db/mongodb-atlas/docker-compose.yml",
    ]:
        full = Path(REPO) / compose_path
        content = full.read_text()
        # Basic YAML sanity: must have 'services' key and balanced quotes
        assert "services:" in content, f"{compose_path} missing 'services' key"
        assert content.count("'") % 2 == 0, f"{compose_path} has unbalanced quotes"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: port changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mongodb_docker_compose_port():
    """MongoDB docker-compose must map host port 27018 (not 27017) to container port 27017."""
    compose = Path(REPO) / "test/helpers/db/mongodb/docker-compose.yml"
    content = compose.read_text()
    # Must have the new port mapping
    assert "'27018:27017'" in content or '"27018:27017"' in content, \
        "MongoDB docker-compose should map host port 27018 to container port 27017"
    # Must NOT still have the old mapping
    assert "'27017:27017'" not in content and '"27017:27017"' not in content, \
        "MongoDB docker-compose should no longer use host port 27017"


# [pr_diff] fail_to_pass
def test_mongodb_atlas_docker_compose_port():
    """MongoDB Atlas docker-compose must map host port 27019 (not 27018) to container port 27017."""
    compose = Path(REPO) / "test/helpers/db/mongodb-atlas/docker-compose.yml"
    content = compose.read_text()
    assert "'27019:27017'" in content or '"27019:27017"' in content, \
        "MongoDB Atlas docker-compose should map host port 27019 to container port 27017"
    assert "'27018:27017'" not in content and '"27018:27017"' not in content, \
        "MongoDB Atlas docker-compose should no longer use host port 27018"


# [pr_diff] fail_to_pass
def test_adapter_mongodb_url_port():
    """generateDatabaseAdapter.ts must use port 27018 for MongoDB default URL."""
    adapter = Path(REPO) / "test/generateDatabaseAdapter.ts"
    content = adapter.read_text()
    assert "localhost:27018/payload?authSource=admin" in content, \
        "MongoDB adapter default URL should use port 27018"
    # Must not still reference old port for authenticated MongoDB
    assert "localhost:27017/payload?authSource=admin" not in content, \
        "MongoDB adapter should no longer use port 27017"


# [pr_diff] fail_to_pass
def test_adapter_mongodb_atlas_url_port():
    """generateDatabaseAdapter.ts must use port 27019 for MongoDB Atlas default URL."""
    adapter = Path(REPO) / "test/generateDatabaseAdapter.ts"
    content = adapter.read_text()
    assert "localhost:27019/payload?directConnection=true" in content, \
        "MongoDB Atlas adapter default URL should use port 27019"
    assert "localhost:27018/payload?directConnection=true" not in content, \
        "MongoDB Atlas adapter should no longer use port 27018 for Atlas"


# [pr_diff] fail_to_pass
def test_ci_action_mongodb_url():
    """GitHub Actions start-database must reference port 27018 for MongoDB."""
    action = Path(REPO) / ".github/actions/start-database/action.yml"
    content = action.read_text()
    assert "localhost:27018/payload?authSource=admin" in content, \
        "CI action should use port 27018 for MongoDB"
    assert "localhost:27017/payload?authSource=admin" not in content, \
        "CI action should no longer use port 27017 for MongoDB"


# [pr_diff] fail_to_pass
def test_ci_action_mongodb_atlas_url():
    """GitHub Actions start-database must reference port 27019 for MongoDB Atlas."""
    action = Path(REPO) / ".github/actions/start-database/action.yml"
    content = action.read_text()
    assert "localhost:27019/payload?directConnection=true" in content, \
        "CI action should use port 27019 for MongoDB Atlas"


# [pr_diff] fail_to_pass
def test_connection_test_mongodb_url():
    """MongoDB run-test-connection.ts must use port 27018."""
    conn = Path(REPO) / "test/helpers/db/mongodb/run-test-connection.ts"
    content = conn.read_text()
    assert "localhost:27018" in content, \
        "MongoDB connection test should use port 27018"
    assert "localhost:27017" not in content, \
        "MongoDB connection test should no longer use port 27017"


# [pr_diff] fail_to_pass
def test_connection_test_mongodb_atlas_url():
    """MongoDB Atlas run-test-connection.ts must use port 27019."""
    conn = Path(REPO) / "test/helpers/db/mongodb-atlas/run-test-connection.ts"
    content = conn.read_text()
    assert "localhost:27019" in content, \
        "MongoDB Atlas connection test should use port 27019"
    assert "localhost:27018" not in content, \
        "MongoDB Atlas connection test should no longer use port 27018"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation / config file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — CLAUDE.md compliance
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
