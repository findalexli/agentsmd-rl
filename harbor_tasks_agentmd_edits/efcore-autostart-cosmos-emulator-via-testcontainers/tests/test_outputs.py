"""
Task: efcore-autostart-cosmos-emulator-via-testcontainers
Repo: dotnet/efcore @ dd9da572feeb9851a0c4a6579b05163c48574c29
PR:   37999

Replace explicit Docker scripts for the Cosmos emulator with automatic
Testcontainers.CosmosDb lifecycle management. Also update the agent skill
file to reflect the new approach.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/efcore"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified C# files are present and non-empty."""
    files = [
        "test/EFCore.Cosmos.FunctionalTests/TestUtilities/TestEnvironment.cs",
        "test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosTestStore.cs",
        "test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosDbContextOptionsBuilderExtensions.cs",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} must have substantial content"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_testenvironment_has_initialize_async():
    """TestEnvironment.cs must have an InitializeAsync method with 3-path logic."""
    src = (Path(REPO) / "test/EFCore.Cosmos.FunctionalTests/TestUtilities/TestEnvironment.cs").read_text()
    assert "InitializeAsync" in src, "TestEnvironment must define InitializeAsync"
    assert "async Task InitializeAsync" in src or "async Task InitializeAsync()" in src, \
        "InitializeAsync must be an async Task method"
    # Must have probe logic (path 2)
    assert "TryProbeEmulator" in src or "probe" in src.lower(), \
        "InitializeAsync should probe for a running emulator"
    # Must reference Testcontainers (path 3)
    assert "CosmosDbContainer" in src or "Testcontainers" in src, \
        "InitializeAsync should use Testcontainers for fallback"


def test_cosmos_config_default_connection_null():
    """cosmosConfig.json DefaultConnection must be null (not hardcoded URL)."""
    config_path = Path(REPO) / "test/EFCore.Cosmos.FunctionalTests/cosmosConfig.json"
    data = json.loads(config_path.read_text())
    conn = data["Test"]["Cosmos"]["DefaultConnection"]
    assert conn is None, \
        f"DefaultConnection should be null, got {conn!r}"


def test_docker_scripts_removed():
    """The old Docker startup scripts must be removed."""
    ps1 = Path(REPO) / "eng/testing/run-cosmos-container.ps1"
    sh = Path(REPO) / "eng/testing/run-cosmos-container.sh"
    assert not ps1.exists(), "run-cosmos-container.ps1 should be deleted"
    assert not sh.exists(), "run-cosmos-container.sh should be deleted"


def test_testcontainers_package_referenced():
    """Testcontainers.CosmosDb must be added as a package dependency."""
    props = (Path(REPO) / "test/Directory.Packages.props").read_text()
    assert "Testcontainers.CosmosDb" in props, \
        "test/Directory.Packages.props must reference Testcontainers.CosmosDb"
    csproj = (Path(REPO) / "test/EFCore.Cosmos.FunctionalTests/EFCore.Cosmos.FunctionalTests.csproj").read_text()
    assert "Testcontainers.CosmosDb" in csproj, \
        "EFCore.Cosmos.FunctionalTests.csproj must reference Testcontainers.CosmosDb"






# ---------------------------------------------------------------------------
# Config edit (config_edit) — SKILL.md update
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Agent config compliance (agent_config, pass_to_pass)
# ---------------------------------------------------------------------------

