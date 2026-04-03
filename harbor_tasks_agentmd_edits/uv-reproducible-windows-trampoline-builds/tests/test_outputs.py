"""
Task: uv-reproducible-windows-trampoline-builds
Repo: uv @ 222f98860116165f39d4d990bebc449ae7d14732
PR:   18665

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/uv"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_normalize_pe_handles_coff_and_codeview():
    """PE normalizer must zero both COFF header timestamp and CodeView GUID."""
    src = Path(REPO) / "crates/uv-trampoline-builder/src/bin/normalize-pe-timestamps.rs"
    content = src.read_text()

    # Must handle COFF header TimeDateStamp
    content_lower = content.lower()
    assert "coff" in content_lower or "time_date_stamp" in content_lower or "timestamp" in content_lower, \
        "Must reference COFF timestamp"
    # Must zero out bytes
    assert ".fill(0)" in content or "fill(0)" in content or "[0u8;" in content or "= 0;" in content, \
        "Must zero out bytes in the PE"
    # Must handle CodeView/PDB70 GUID
    assert "codeview" in content_lower or "pdb70" in content_lower or \
        "guid" in content_lower or "signature" in content_lower, \
        "Must handle CodeView GUID"
    # Must handle debug directory
    assert "debug" in content_lower, "Must handle debug directory entries"


def test_normalize_pe_rva_resolution():
    """PE normalizer must convert RVA to file offset using section table."""
    src = Path(REPO) / "crates/uv-trampoline-builder/src/bin/normalize-pe-timestamps.rs"
    content = src.read_text()

    # Must have RVA-to-file-offset logic using sections
    assert "rva" in content.lower() or "virtual_address" in content, \
        "Must have RVA resolution logic"
    assert "section" in content.lower(), "Must reference PE sections"
    assert "pointer_to_raw_data" in content or "raw_data" in content.lower(), \
        "Must use pointer_to_raw_data for offset calculation"


def test_build_script_all_architectures():
    """Build script must target i686, x86_64, and aarch64 Windows via Docker."""
    script = Path(REPO) / "scripts/build-trampolines.sh"
    content = script.read_text()

    assert "i686" in content, "Must build for i686"
    assert "x86_64" in content, "Must build for x86_64"
    assert "aarch64" in content, "Must build for aarch64"
    # Must use Docker for reproducibility
    assert "docker" in content.lower(), "Must use Docker for reproducible builds"
    # Must run normalize-pe-timestamps
    assert "normalize" in content.lower(), "Must run PE timestamp normalization"


def test_cargo_config_brepro():
    """Cargo config must include /Brepro linker flag for reproducible PE builds."""
    config = Path(REPO) / "crates/uv-trampoline/.cargo/config.toml"
    content = config.read_text()

    assert "Brepro" in content, "Must have /Brepro flag for reproducible PE timestamps"
    assert "rustflags" in content.lower(), "Must set rustflags"


def test_goblin_pe_features():
    """Root Cargo.toml must enable pe32 and pe64 features for goblin crate."""
    cargo_toml = Path(REPO) / "Cargo.toml"
    content = cargo_toml.read_text()

    assert '"pe32"' in content or "'pe32'" in content, \
        "Must enable pe32 feature for goblin"
    assert '"pe64"' in content or "'pe64'" in content, \
        "Must enable pe64 feature for goblin"


def test_trampoline_builder_declares_binary():
    """uv-trampoline-builder Cargo.toml must declare normalize-pe-timestamps binary."""
    cargo_toml = Path(REPO) / "crates/uv-trampoline-builder/Cargo.toml"
    content = cargo_toml.read_text()

    assert "normalize-pe-timestamps" in content, \
        "Must declare normalize-pe-timestamps binary"
    assert "goblin" in content, \
        "Must depend on goblin for PE parsing"


# ---------------------------------------------------------------------------
# Config edit — README documentation update
# ---------------------------------------------------------------------------


    # Must mention the build script
    assert "build-trampolines" in content, \
        "README must reference scripts/build-trampolines.sh"
    # Must mention reproducible or Docker
    has_reproducible = "reproducible" in content.lower()
    has_docker = "docker" in content.lower()
    assert has_reproducible or has_docker, \
        "README must mention reproducible builds or Docker"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression
# ---------------------------------------------------------------------------


    assert "Cross-compiling from Linux" in content, \
        "Must preserve Linux cross-compiling docs"
    assert "Cross-compiling from macOS" in content, \
        "Must preserve macOS cross-compiling docs"
    assert "cargo xwin" in content.lower() or "cargo-xwin" in content.lower(), \
        "Must preserve cargo-xwin references"
