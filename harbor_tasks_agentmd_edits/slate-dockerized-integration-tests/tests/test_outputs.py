"""
Task: slate-dockerized-integration-tests
Repo: ianstormtaylor/slate @ 33e74a822b82c4b9ce1444f456c5343970441ccb
PR:   5967

Add Docker-based integration test infrastructure so developers can reproduce
CI failures locally. Includes orchestration scripts, Docker config, Playwright
config changes, and contributing documentation updates.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
from pathlib import Path

REPO = "/workspace/slate"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_playwright_config():
    """playwright.config.ts must still have a valid config export structure."""
    config_path = Path(REPO) / "playwright.config.ts"
    content = config_path.read_text()
    assert "PlaywrightTestConfig" in content, (
        "playwright.config.ts should reference PlaywrightTestConfig type"
    )
    assert "export default" in content, (
        "playwright.config.ts should export a default config"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behaviour
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_package_json_docker_script():
    """package.json must have a test:integration-docker script."""
    pkg = json.loads(Path(os.path.join(REPO, "package.json")).read_text())
    scripts = pkg.get("scripts", {})
    assert "test:integration-docker" in scripts, (
        "package.json should have a 'test:integration-docker' script"
    )
    script_val = scripts["test:integration-docker"]
    assert "docker" in script_val.lower() or "run-tests" in script_val.lower(), (
        "test:integration-docker script should reference docker or a run-tests script"
    )


# [pr_diff] fail_to_pass
def test_playwright_base_url_env_configurable():
    """playwright.config.ts must use PLAYWRIGHT_BASE_URL env var for baseURL."""
    content = Path(os.path.join(REPO, "playwright.config.ts")).read_text()
    assert "PLAYWRIGHT_BASE_URL" in content, (
        "playwright.config.ts should reference PLAYWRIGHT_BASE_URL env var"
    )
    assert "baseURL" in content, (
        "playwright.config.ts should set baseURL from env var"
    )


# [pr_diff] fail_to_pass
def test_run_tests_script_orchestration():
    """run-tests.sh must manage dev server lifecycle and invoke docker compose."""
    script_path = Path(REPO) / "playwright" / "docker" / "run-tests.sh"
    assert script_path.exists(), "playwright/docker/run-tests.sh should exist"
    content = script_path.read_text()
    assert content.startswith("#!"), "run-tests.sh should have a shebang line"
    # Must detect if server is already running
    assert "localhost:3000" in content or "127.0.0.1:3000" in content, (
        "run-tests.sh should check if dev server is running on port 3000"
    )
    # Must invoke docker compose
    assert "docker compose" in content or "docker-compose" in content, (
        "run-tests.sh should invoke docker compose to run tests"
    )


# [pr_diff] fail_to_pass
def test_docker_compose_service_config():
    """docker-compose.yml must mount the project and configure networking."""
    compose_path = Path(REPO) / "playwright" / "docker" / "docker-compose.yml"
    assert compose_path.exists(), "playwright/docker/docker-compose.yml should exist"
    content = compose_path.read_text()
    # Must mount the project directory
    assert "/app" in content or "volumes:" in content, (
        "docker-compose.yml should mount the project as a volume"
    )
    # Must set PLAYWRIGHT_BASE_URL for Docker networking
    assert "PLAYWRIGHT_BASE_URL" in content, (
        "docker-compose.yml should set PLAYWRIGHT_BASE_URL environment variable"
    )
    # Must handle host networking (host.docker.internal or network_mode)
    assert "host.docker.internal" in content or "network_mode" in content, (
        "docker-compose.yml should configure host networking"
    )


# [pr_diff] fail_to_pass
def test_entrypoint_server_health_check():
    """entrypoint.sh must wait for the dev server to be ready before running tests."""
    entry_path = Path(REPO) / "playwright" / "docker" / "entrypoint.sh"
    assert entry_path.exists(), "playwright/docker/entrypoint.sh should exist"
    content = entry_path.read_text()
    assert content.startswith("#!"), "entrypoint.sh should have a shebang line"
    # Must have health check / wait loop
    assert "curl" in content or "wget" in content, (
        "entrypoint.sh should use curl or wget to check server health"
    )
    # Must run playwright tests
    assert "playwright" in content.lower(), (
        "entrypoint.sh should invoke playwright to run tests"
    )


# [pr_diff] fail_to_pass
def test_dockerfile_installs_playwright():
    """Dockerfile must install Playwright with browser dependencies."""
    df_path = Path(REPO) / "playwright" / "docker" / "Dockerfile"
    assert df_path.exists(), "playwright/docker/Dockerfile should exist"
    content = df_path.read_text()
    assert "playwright" in content.lower(), (
        "Dockerfile should install Playwright"
    )
    assert "install" in content.lower(), (
        "Dockerfile should install dependencies"
    )
    # Must be based on a Node image or install Node
    assert "node" in content.lower() or "npm" in content.lower(), (
        "Dockerfile should use Node.js (needed for Playwright)"
    )


# [pr_diff] fail_to_pass
def test_docker_playwright_config_extends_base():
    """Docker-specific Playwright config must extend/import the base config."""
    config_path = Path(REPO) / "playwright" / "docker" / "playwright.config.docker.ts"
    assert config_path.exists(), (
        "playwright/docker/playwright.config.docker.ts should exist"
    )
    content = config_path.read_text()
    # Must import from or reference the base config
    assert "import" in content and ("playwright.config" in content or "baseConfig" in content.lower()), (
        "Docker Playwright config should import/extend the base playwright.config"
    )
    assert "export" in content, (
        "Docker Playwright config should export a config"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
