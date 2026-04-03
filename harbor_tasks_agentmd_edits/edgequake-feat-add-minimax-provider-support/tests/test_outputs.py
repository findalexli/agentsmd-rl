"""
Task: edgequake-feat-add-minimax-provider-support
Repo: raphaelmansuy/edgequake @ ffa9283e410ea0205be73bf3088193a34006d3d8
PR:   99

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import tomllib
from pathlib import Path

REPO = "/workspace/edgequake"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_models_toml_valid():
    """models.toml must parse as valid TOML."""
    toml_path = Path(REPO) / "edgequake" / "models.toml"
    content = toml_path.read_text()
    data = tomllib.loads(content)
    assert "providers" in data, "models.toml must have a [[providers]] section"
    assert "defaults" in data, "models.toml must have a [defaults] section"


# [static] pass_to_pass
def test_existing_providers_intact():
    """Existing providers (openai, ollama, mock) must still be present."""
    toml_path = Path(REPO) / "edgequake" / "models.toml"
    data = tomllib.loads(toml_path.read_text())
    provider_names = [p["name"] for p in data["providers"]]
    for expected in ["openai", "ollama", "mock"]:
        assert expected in provider_names, f"Provider '{expected}' missing from models.toml"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_models_toml_has_minimax_provider():
    """models.toml must define a 'minimax' provider with correct base config."""
    toml_path = Path(REPO) / "edgequake" / "models.toml"
    data = tomllib.loads(toml_path.read_text())
    minimax_providers = [p for p in data["providers"] if p["name"] == "minimax"]
    assert len(minimax_providers) == 1, "Expected exactly one 'minimax' provider in models.toml"
    provider = minimax_providers[0]
    assert provider["type"] == "openaicompatible", \
        f"MiniMax provider type should be 'openaicompatible', got '{provider['type']}'"
    assert "api.minimax.io" in provider.get("api_base", ""), \
        "MiniMax api_base should point to api.minimax.io"
    assert provider.get("api_key_env") == "MINIMAX_API_KEY", \
        "MiniMax api_key_env should be 'MINIMAX_API_KEY'"


# [pr_diff] fail_to_pass
def test_minimax_has_four_models():
    """MiniMax provider must define M2.7, M2.7-highspeed, M2.5, M2.5-highspeed."""
    toml_path = Path(REPO) / "edgequake" / "models.toml"
    data = tomllib.loads(toml_path.read_text())
    minimax_providers = [p for p in data["providers"] if p["name"] == "minimax"]
    assert len(minimax_providers) == 1, "MiniMax provider not found"
    models = minimax_providers[0].get("models", [])
    model_names = [m["name"] for m in models]
    expected_models = ["MiniMax-M2.7", "MiniMax-M2.7-highspeed", "MiniMax-M2.5", "MiniMax-M2.5-highspeed"]
    for expected in expected_models:
        assert expected in model_names, f"Model '{expected}' missing from MiniMax provider"
    # Verify M2.7 has 204K context
    m27 = [m for m in models if m["name"] == "MiniMax-M2.7"][0]
    ctx = m27.get("capabilities", {}).get("context_length", 0)
    assert ctx >= 200000, f"MiniMax-M2.7 context_length should be >= 200000, got {ctx}"


# [pr_diff] fail_to_pass
def test_provider_types_registers_minimax():
    """provider_types.rs must register a MiniMax provider with id 'minimax'."""
    rs_path = Path(REPO) / "edgequake" / "crates" / "edgequake-api" / "src" / "provider_types.rs"
    content = rs_path.read_text()
    assert 'id: "minimax"' in content, \
        "provider_types.rs must register a provider with id 'minimax'"
    assert "MINIMAX_API_KEY" in content, \
        "provider_types.rs must check MINIMAX_API_KEY env var"
    assert "MiniMax-M2.7" in content, \
        "provider_types.rs must set MiniMax-M2.7 as default chat model"


# [pr_diff] fail_to_pass
def test_safety_limits_minimax_default():
    """safety_limits.rs must map 'minimax' to a default model."""
    rs_path = Path(REPO) / "edgequake" / "crates" / "edgequake-api" / "src" / "safety_limits.rs"
    content = rs_path.read_text()
    # Check that "minimax" appears in the match arms with a model mapping
    assert '"minimax"' in content, \
        "safety_limits.rs must have a 'minimax' match arm in default_model_for_provider"
    assert re.search(r'"minimax"\s*=>\s*"MiniMax-M2\.7"', content), \
        "safety_limits.rs must map 'minimax' to 'MiniMax-M2.7'"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation/config update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression / anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ui_provider_display_name():
    """UI hooks must map 'minimax' to a display name."""
    hooks_path = Path(REPO) / "edgequake_webui" / "src" / "hooks" / "use-providers.ts"
    content = hooks_path.read_text()
    assert "minimax" in content, \
        "use-providers.ts must include minimax in provider display names"
    # Verify the display name value is meaningful (not empty)
    assert re.search(r'minimax["\']?\s*:\s*["\']MiniMax', content), \
        "use-providers.ts must map minimax to display name 'MiniMax'"
