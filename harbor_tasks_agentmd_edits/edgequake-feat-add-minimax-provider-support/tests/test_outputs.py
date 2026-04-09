"""
Task: edgequake-feat-add-minimax-provider-support
Repo: raphaelmansuy/edgequake @ ffa9283e410ea0205be73bf3088193a34006d3d8
PR:   99

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tomllib
import os
from pathlib import Path

REPO = "/workspace/edgequake"
EDGEQUAKE_CRATES = Path(REPO) / "edgequake"


def _setup_rust_env():
    """Ensure Rust and system dependencies are installed."""
    # Install system dependencies
    subprocess.run(
        ["apt-get", "update"],
        capture_output=True, timeout=60
    )
    subprocess.run(
        ["apt-get", "install", "-y", "--no-install-recommends", "pkg-config", "libssl-dev"],
        capture_output=True, timeout=60
    )
    # Ensure rustup is installed
    rustup_path = Path("/root/.cargo/bin/cargo")
    if not rustup_path.exists():
        r = subprocess.run(
            ["curl", "--proto", "=https", "--tlsv1.2", "-sSf", "https://sh.rustup.rs"],
            capture_output=True, timeout=60
        )
        if r.returncode == 0:
            subprocess.run(
                ["sh", "-s", "--", "-y"],
                input=r.stdout,
                capture_output=True, timeout=180
            )
    return "/root/.cargo/bin"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


def test_models_toml_valid():
    """models.toml must parse as valid TOML."""
    toml_path = Path(REPO) / "edgequake" / "models.toml"
    content = toml_path.read_text()
    data = tomllib.loads(content)
    assert "providers" in data, "models.toml must have a [[providers]] section"
    assert "defaults" in data, "models.toml must have a [defaults] section"


def test_existing_providers_intact():
    """Existing providers (openai, ollama, mock) must still be present."""
    toml_path = Path(REPO) / "edgequake" / "models.toml"
    data = tomllib.loads(toml_path.read_text())
    provider_names = [p["name"] for p in data["providers"]]
    for expected in ["openai", "ollama", "mock"]:
        assert expected in provider_names, f"Provider '{expected}' missing from models.toml"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks
# ---------------------------------------------------------------------------


def test_repo_cargo_fmt():
    """Repo's Rust code formatting passes (pass_to_pass)."""
    cargo_bin = _setup_rust_env()
    env = {**os.environ, "PATH": f"{cargo_bin}:{os.environ.get('PATH', '')}"}
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        capture_output=True, text=True, timeout=120, cwd=EDGEQUAKE_CRATES, env=env
    )
    assert r.returncode == 0, f"Cargo fmt failed:\n{r.stderr[-500:]}"


def test_repo_cargo_check():
    """Repo's Rust code compiles (pass_to_pass)."""
    cargo_bin = _setup_rust_env()
    env = {**os.environ, "PATH": f"{cargo_bin}:{os.environ.get('PATH', '')}"}
    r = subprocess.run(
        ["cargo", "check", "--workspace", "--lib"],
        capture_output=True, text=True, timeout=180, cwd=EDGEQUAKE_CRATES, env=env
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-500:]}"


def test_repo_cargo_test():
    """Repo's Rust library tests pass (pass_to_pass)."""
    cargo_bin = _setup_rust_env()
    env = {**os.environ, "PATH": f"{cargo_bin}:{os.environ.get('PATH', '')}"}
    r = subprocess.run(
        ["cargo", "test", "--workspace", "--lib", "--no-fail-fast"],
        capture_output=True, text=True, timeout=180, cwd=EDGEQUAKE_CRATES, env=env
    )
    assert r.returncode == 0, f"Cargo test failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


def test_models_toml_has_minimax_provider():
    """models.toml must define a 'minimax' provider with correct base config."""
    r = _run_py("""
import tomllib
from pathlib import Path

data = tomllib.loads(Path("edgequake/models.toml").read_text())
minimax = [p for p in data["providers"] if p["name"] == "minimax"]
assert len(minimax) == 1, f"Expected 1 minimax provider, found {len(minimax)}"

p = minimax[0]
assert p["type"] == "openaicompatible", f"Expected type 'openaicompatible', got '{p['type']}'"
assert "api.minimax.io" in p.get("api_base", ""), f"api_base should contain api.minimax.io, got '{p.get('api_base')}'"
assert p.get("api_key_env") == "MINIMAX_API_KEY", f"api_key_env should be MINIMAX_API_KEY, got '{p.get('api_key_env')}'"
assert p.get("enabled") is True, "MiniMax provider should be enabled"
print("PASS")
""")
    assert r.returncode == 0, f"MiniMax provider config check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_minimax_has_four_models():
    """MiniMax provider must define M2.7, M2.7-highspeed, M2.5, M2.5-highspeed with correct specs."""
    r = _run_py("""
import tomllib
from pathlib import Path

data = tomllib.loads(Path("edgequake/models.toml").read_text())
minimax = [p for p in data["providers"] if p["name"] == "minimax"]
assert len(minimax) == 1, "MiniMax provider not found"

models = minimax[0].get("models", [])
names = [m["name"] for m in models]
expected = ["MiniMax-M2.7", "MiniMax-M2.7-highspeed", "MiniMax-M2.5", "MiniMax-M2.5-highspeed"]

for name in expected:
    assert name in names, f"Model '{name}' missing from MiniMax provider"

# M2.7 flagship must have >= 200K context
m27 = [m for m in models if m["name"] == "MiniMax-M2.7"][0]
ctx = m27.get("capabilities", {}).get("context_length", 0)
assert ctx >= 200000, f"MiniMax-M2.7 context_length should be >= 200000, got {ctx}"

# All models should be LLM type
for m in models:
    assert m.get("model_type") == "llm", f"Model {m['name']} should be type 'llm'"

print("PASS")
""")
    assert r.returncode == 0, f"MiniMax model definitions check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_provider_types_registers_minimax():
    """provider_types.rs must register MiniMax provider with env var check and default model."""
    r = _run_py("""
from pathlib import Path

content = Path("edgequake/crates/edgequake-api/src/provider_types.rs").read_text()

# Must have a ProviderInfo with id "minimax"
assert 'id: "minimax"' in content, "provider_types.rs must register id 'minimax'"

# Must check MINIMAX_API_KEY for availability
assert "MINIMAX_API_KEY" in content, "provider_types.rs must reference MINIMAX_API_KEY"

# Must set MiniMax-M2.7 as default chat model
assert "MiniMax-M2.7" in content, "provider_types.rs must set MiniMax-M2.7 as default chat model"

print("PASS")
""")
    assert r.returncode == 0, f"Provider registration check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_safety_limits_minimax_default():
    """safety_limits.rs must map 'minimax' provider to 'MiniMax-M2.7' default model."""
    r = _run_py("""
from pathlib import Path

content = Path("edgequake/crates/edgequake-api/src/safety_limits.rs").read_text()

assert '"minimax"' in content, "safety_limits.rs must reference minimax"
assert '"MiniMax-M2.7"' in content, "safety_limits.rs must reference MiniMax-M2.7"

# Verify both strings appear in the same match arm (within 50 chars)
idx_provider = content.index('"minimax"')
idx_model = content.index('"MiniMax-M2.7"')
dist = abs(idx_model - idx_provider)
assert dist < 50, f"minimax and MiniMax-M2.7 should be in the same match arm, got distance {dist}"

print("PASS")
""")
    assert r.returncode == 0, f"Safety limits default model check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_ui_provider_display_name():
    """use-providers.ts must map 'minimax' to display name 'MiniMax'."""
    r = _run_py("""
from pathlib import Path

content = Path("edgequake_webui/src/hooks/use-providers.ts").read_text()

assert "minimax" in content, "use-providers.ts must reference minimax"

# The display name mapping should include MiniMax near the minimax key
idx_key = content.index("minimax")
window = content[idx_key:idx_key + 100]
assert "MiniMax" in window, "use-providers.ts must map minimax to display name MiniMax"

print("PASS")
""")
    assert r.returncode == 0, f"UI display name check failed: {r.stderr}"
    assert "PASS" in r.stdout
