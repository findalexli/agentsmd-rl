"""
Task: quickwit-rationalize-deps
Repo: quickwit-oss/quickwit @ eca4f763214604006262fc6a29dcf59c754813e3
PR:   6125

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

REPO = "/workspace/quickwit"
CARGO_TOML = Path(REPO) / "quickwit" / "Cargo.toml"


def _load_workspace_deps():
    """Parse workspace Cargo.toml and return the [workspace.dependencies] table."""
    content = CARGO_TOML.read_text()
    data = tomllib.loads(content)
    return data["workspace"]["dependencies"]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_toml_valid():
    """Cargo.toml must be valid TOML after modifications."""
    content = CARGO_TOML.read_text()
    # Will raise if invalid TOML
    data = tomllib.loads(content)
    assert "workspace" in data, "Missing [workspace] section"
    assert "dependencies" in data["workspace"], "Missing [workspace.dependencies]"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for Cargo.toml changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_hyper_util_not_full():
    """hyper-util must not use the 'full' feature — should list specific features."""
    deps = _load_workspace_deps()
    hu = deps["hyper-util"]
    assert isinstance(hu, dict), "hyper-util should be a table, not a plain version string"
    features = hu.get("features", [])
    assert "full" not in features, "hyper-util should not use 'full' feature"
    assert hu.get("default-features") is False, "hyper-util should set default-features = false"
    # Must retain essential features for the project
    assert "tokio" in features, "hyper-util must keep 'tokio' feature"
    assert "service" in features, "hyper-util must keep 'service' feature"


# [pr_diff] fail_to_pass
def test_tokio_util_not_full():
    """tokio-util must not use the 'full' feature — should list specific features."""
    deps = _load_workspace_deps()
    tu = deps["tokio-util"]
    assert isinstance(tu, dict), "tokio-util should be a table, not a plain version string"
    features = tu.get("features", [])
    assert "full" not in features, "tokio-util should not use 'full' feature"
    assert tu.get("default-features") is False, "tokio-util should set default-features = false"


# [pr_diff] fail_to_pass
def test_prometheus_defaults_disabled():
    """prometheus must have default-features = false (protobuf not needed)."""
    deps = _load_workspace_deps()
    prom = deps["prometheus"]
    assert isinstance(prom, dict), "prometheus should be a table, not a plain version string"
    assert prom.get("default-features") is False, \
        "prometheus should set default-features = false"
    # Must keep process feature
    features = prom.get("features", [])
    assert "process" in features, "prometheus must keep 'process' feature"


# [pr_diff] fail_to_pass
def test_dialoguer_defaults_disabled():
    """dialoguer must have default-features = false (editor/password not needed)."""
    deps = _load_workspace_deps()
    dlg = deps["dialoguer"]
    assert isinstance(dlg, dict), "dialoguer should be a table, not a plain version string"
    assert dlg.get("default-features") is False, \
        "dialoguer should set default-features = false"


# [pr_diff] fail_to_pass
def test_zstd_defaults_disabled():
    """zstd must have default-features = false (legacy/arrays/zdict not needed)."""
    deps = _load_workspace_deps()
    z = deps["zstd"]
    assert isinstance(z, dict), "zstd should be a table, not a plain version string"
    assert z.get("default-features") is False, \
        "zstd should set default-features = false"


# [pr_diff] fail_to_pass
def test_env_logger_defaults_disabled():
    """env_logger must have default-features = false (humantime/regex not needed)."""
    deps = _load_workspace_deps()
    el = deps["env_logger"]
    assert isinstance(el, dict), "env_logger should be a table, not a plain version string"
    assert el.get("default-features") is False, \
        "env_logger should set default-features = false"


# ---------------------------------------------------------------------------
# Pass-to-pass — ensure we didn't break existing deps
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_essential_deps_unchanged():
    """Critical dependencies (tokio, serde, hyper) must still be present."""
    deps = _load_workspace_deps()
    for crate in ["tokio", "serde", "hyper", "hyper-util", "tokio-util",
                   "prometheus", "dialoguer", "zstd", "env_logger"]:
        assert crate in deps, f"Dependency '{crate}' must still be present in workspace deps"


# [static] pass_to_pass
def test_hyper_util_has_required_features():
    """hyper-util must retain essential features (tokio, service) for the project to compile."""
    deps = _load_workspace_deps()
    hu = deps["hyper-util"]
    if isinstance(hu, str):
        # Plain version string — defaults are on, all features available
        return
    features = hu.get("features", [])
    # If full is used, all features are included
    if "full" in features:
        return
    # Otherwise, must have the essentials
    assert "tokio" in features, "hyper-util must keep 'tokio' feature"
    assert "service" in features, "hyper-util must keep 'service' feature"


# ---------------------------------------------------------------------------
# Config file update tests (config_edit) — SKILL.md creation
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
