"""
Task: maui-ci-move-to-aces-dnceng
Repo: dotnet/maui @ bfe8e58dcab8b030d6d87edf30fbe3f53827795d
PR:   34690

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/maui"


def _get_yaml_files():
    """Get list of modified YAML files."""
    return [
        Path(f"{REPO}/eng/pipelines/ci-uitests.yml"),
        Path(f"{REPO}/eng/pipelines/ci-device-tests.yml"),
    ]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_yaml_syntax_valid():
    """Modified YAML files must parse without errors."""
    import yaml

    for yaml_file in _get_yaml_files():
        content = yaml_file.read_text()
        # Validate YAML parses
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise AssertionError(f"Invalid YAML in {yaml_file}: {e}")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ci_uitests_pools_split():
    """ci-uitests.yml has separate internal/public pool parameters."""
    import yaml

    yaml_file = Path(f"{REPO}/eng/pipelines/ci-uitests.yml")
    content = yaml_file.read_text()
    data = yaml.safe_load(content)

    params = {p['name'] for p in data.get('parameters', [])}

    # Must have internal pool variants
    assert 'androidPoolInternal' in params, "Missing androidPoolInternal parameter"
    assert 'iosPoolInternal' in params, "Missing iosPoolInternal parameter"
    assert 'windowsPoolInternal' in params, "Missing windowsPoolInternal parameter"
    assert 'windowsBuildPoolInternal' in params, "Missing windowsBuildPoolInternal parameter"
    assert 'macosPoolInternal' in params, "Missing macosPoolInternal parameter"

    # Must have public pool variants
    assert 'androidPoolPublic' in params, "Missing androidPoolPublic parameter"
    assert 'iosPoolPublic' in params, "Missing iosPoolPublic parameter"
    assert 'windowsPoolPublic' in params, "Missing windowsPoolPublic parameter"
    assert 'windowsBuildPoolPublic' in params, "Missing windowsBuildPoolPublic parameter"
    assert 'macosPoolPublic' in params, "Missing macosPoolPublic parameter"

    # Old combined pool names should not exist
    assert 'androidPool' not in params, "Old androidPool parameter should be removed"
    assert 'iosPool' not in params, "Old iosPool parameter should be removed"
    assert 'windowsPool' not in params, "Old windowsPool parameter should be removed"
    assert 'windowsBuildPool' not in params, "Old windowsBuildPool parameter should be removed"
    assert 'macosPool' not in params, "Old macosPool parameter should be removed"


# [pr_diff] fail_to_pass
def test_ci_uitests_conditional_pool_selection():
    """ci-uitests.yml uses System.TeamProject conditional for pool selection."""
    yaml_file = Path(f"{REPO}/eng/pipelines/ci-uitests.yml")
    content = yaml_file.read_text()

    # Must have conditional selection using System.TeamProject
    assert "${{ if eq(variables['System.TeamProject'], 'internal') }}:" in content, \
        "Missing internal conditional for pool selection"
    assert "${{ else }}:" in content, "Missing else branch for public pool selection"

    # Template invocation should use conditional syntax
    assert "androidPool: ${{ parameters.androidPoolInternal }}" in content, \
        "Missing internal androidPool mapping"
    assert "androidPool: ${{ parameters.androidPoolPublic }}" in content, \
        "Missing public androidPool mapping"


# [pr_diff] fail_to_pass
def test_no_hardcoded_netcore_public():
    """Pool defaults no longer reference non-existent NetCore-Public pool."""
    yaml_file = Path(f"{REPO}/eng/pipelines/ci-uitests.yml")
    content = yaml_file.read_text()

    # The problematic NetCore-Public pool was causing validation errors
    # because it doesn't exist in dnceng/internal
    assert "NetCore-Public" not in content, \
        "NetCore-Public pool reference found - this causes validation errors in internal project"


# [pr_diff] fail_to_pass
def test_ci_device_tests_conditional_windows():
    """ci-device-tests.yml uses conditional pool selection for Windows."""
    yaml_file = Path(f"{REPO}/eng/pipelines/ci-device-tests.yml")
    content = yaml_file.read_text()

    # Must have conditional selection for Windows Device Tests
    assert "${{ if eq(variables['System.TeamProject'], 'internal') }}:" in content, \
        "Missing internal conditional in ci-device-tests.yml"
    assert "${{ else }}:" in content, "Missing else branch in ci-device-tests.yml"
    assert "windowsPool: ${{ parameters.windowsPoolInternal }}" in content, \
        "Missing internal windowsPool mapping"
    assert "windowsPool: ${{ parameters.windowsPoolPublic }}" in content, \
        "Missing public windowsPool mapping"


# [pr_diff] fail_to_pass
def test_aces_shared_pool_present():
    """AcesShared pool is used for public Android/iOS tests."""
    yaml_file = Path(f"{REPO}/eng/pipelines/ci-uitests.yml")
    content = yaml_file.read_text()

    # The fix adds AcesShared pool for public builds
    assert "AcesShared" in content, "AcesShared pool not found for public builds"
    assert "ACES_VM_SharedPool_Tahoe" in content, "ACES image override not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) - regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified files contain actual changes, not just comments."""
    yaml_file = Path(f"{REPO}/eng/pipelines/ci-uitests.yml")
    content = yaml_file.read_text()

    # Should have substantial YAML structure changes
    lines = content.split('\n')
    non_empty = [l for l in lines if l.strip() and not l.strip().startswith('#')]
    assert len(non_empty) > 50, "YAML file appears to be a stub or empty"


# [static] pass_to_pass
def test_yaml_structure_valid():
    """YAML structure is valid and contains expected sections."""
    import yaml

    yaml_file = Path(f"{REPO}/eng/pipelines/ci-uitests.yml")
    data = yaml.safe_load(yaml_file.read_text())

    # Should have parameters section
    assert 'parameters' in data, "Missing parameters section"
    assert isinstance(data['parameters'], list), "Parameters should be a list"
    assert len(data['parameters']) > 0, "Parameters list is empty"

    # Should have stages section
    assert 'stages' in data, "Missing stages section"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) - rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# Note: The dotnet/maui repo has .github/skills/* files but the task is about
# CI pipeline configuration. No specific config-derived tests apply to YAML changes.
