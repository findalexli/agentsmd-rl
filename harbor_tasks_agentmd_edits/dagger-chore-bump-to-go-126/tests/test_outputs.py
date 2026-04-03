"""
Task: dagger-chore-bump-to-go-126
Repo: dagger/dagger @ 4f82519986828ccfa6a018bf5b78c0fa8589afa2
PR:   11843

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/dagger"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified Go files have valid syntax (balanced braces, no obvious errors)."""
    for relpath in [
        "engine/distconsts/consts.go",
        "toolchains/go/main.go",
        "toolchains/cli-dev/publish.go",
    ]:
        src = Path(f"{REPO}/{relpath}").read_text()
        # Basic: file is non-empty and has balanced braces
        assert len(src) > 100, f"{relpath} is too short"
        assert src.count("{") == src.count("}"), f"{relpath} has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_golang_version_updated():
    """GolangVersion constant must be set to 1.26 in engine/distconsts/consts.go."""
    src = Path(f"{REPO}/engine/distconsts/consts.go").read_text()
    # Match GolangVersion = "1.26" or "1.26.0" etc.
    match = re.search(r'GolangVersion\s*=\s*"([^"]+)"', src)
    assert match is not None, "GolangVersion constant not found"
    version = match.group(1)
    assert version.startswith("1.26"), (
        f"GolangVersion should be 1.26.x, got {version!r}"
    )


def test_go_default_version_updated():
    """The +default annotation in toolchains/go/main.go must specify 1.26."""
    src = Path(f"{REPO}/toolchains/go/main.go").read_text()
    # Find the +default annotation for version
    match = re.search(r'\+default="([^"]+)"', src)
    assert match is not None, "+default annotation not found in toolchains/go/main.go"
    version = match.group(1)
    assert version.startswith("1.26"), (
        f"+default version should be 1.26.x, got {version!r}"
    )


def test_alpine_package_separator():
    """Alpine package name should use 'go-' separator (not 'go~') in toolchains/go/main.go."""
    src = Path(f"{REPO}/toolchains/go/main.go").read_text()
    # The package list construction should use "go-" not "go~"
    assert '"go-"' in src or "'go-'" in src, (
        "Expected 'go-' package separator in toolchains/go/main.go"
    )
    assert '"go~"' not in src, (
        "Found old 'go~' package separator — should be 'go-'"
    )


def test_arm_windows_skipped():
    """goreleaserBinaries must skip arm builds for both darwin AND windows."""
    src = Path(f"{REPO}/toolchains/cli-dev/publish.go").read_text()
    # Find the skip condition in the arch/os loop
    # Should mention both "darwin" and "windows" in the arm skip block
    # Look for a block that checks arch == "arm" and skips darwin+windows
    arm_block = re.search(
        r'arch\s*==\s*"arm"\s*&&.*?continue', src, re.DOTALL
    )
    assert arm_block is not None, "arm skip block not found in publish.go"
    block_text = arm_block.group(0)
    assert "windows" in block_text, (
        "arm skip block should also exclude windows builds"
    )
    assert "darwin" in block_text, (
        "arm skip block should still exclude darwin builds"
    )


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — skill file creation tests
# ---------------------------------------------------------------------------





