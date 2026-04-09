"""
Task: bun-sccache-replace-ccache
Repo: oven-sh/bun @ 995d988c736293572f0a5a2c8a49fd1a2b6ca84c
PR:   24200

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_cmake_structure_valid():
    """CMakeLists.txt has balanced include directives and valid structure."""
    cmake_lists = Path(REPO) / "CMakeLists.txt"
    content = cmake_lists.read_text()
    includes = [l.strip() for l in content.splitlines() if "include(" in l]
    assert len(includes) > 0, "CMakeLists.txt should have include directives"
    for inc in includes:
        assert inc.count("(") >= 1, f"Malformed include: {inc}"


# [static] pass_to_pass
def test_bootstrap_syntax_valid():
    """bootstrap.sh is syntactically valid bash."""
    r = subprocess.run(
        ["bash", "-n", str(Path(REPO) / "scripts/bootstrap.sh")],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"bootstrap.sh syntax error: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior: build system migration
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_sccache_cmake_created():
    """SetupSccache.cmake exists with S3 bucket config, AWS credential checking, and CI detection."""
    cmake_file = Path(REPO) / "cmake/tools/SetupSccache.cmake"
    assert cmake_file.exists(), "SetupSccache.cmake must exist"
    content = cmake_file.read_text()
    # S3 bucket configuration
    assert "SCCACHE_BUCKET" in content, "Must set SCCACHE_BUCKET"
    assert "bun-build-sccache-store" in content, "Must use correct S3 bucket name"
    assert "SCCACHE_REGION" in content, "Must set SCCACHE_REGION"
    assert "us-west-1" in content, "Must use correct AWS region"
    # Credential checking function
    assert "check_aws_credentials" in content, "Must define check_aws_credentials function"
    assert "AWS_ACCESS_KEY_ID" in content, "Must check env var AWS_ACCESS_KEY_ID"
    # CI detection via EC2 metadata
    assert "check_running_in_ci" in content, "Must define check_running_in_ci function"
    assert "169.254.169.254" in content, "Must query EC2 instance metadata service"
    assert "buildkite-agent" in content, "Must check for buildkite-agent service tag"


# [pr_diff] fail_to_pass
def test_ccache_cmake_removed():
    """SetupCcache.cmake must be deleted (replaced by SetupSccache.cmake)."""
    ccache_file = Path(REPO) / "cmake/tools/SetupCcache.cmake"
    assert not ccache_file.exists(), "SetupCcache.cmake should be deleted"


# [pr_diff] fail_to_pass
def test_cmake_includes_sccache():
    """CMakeLists.txt includes SetupSccache, not SetupCcache."""
    content = (Path(REPO) / "CMakeLists.txt").read_text()
    assert "include(SetupSccache)" in content, "Must include SetupSccache"
    assert "include(SetupCcache)" not in content, "Must not include SetupCcache"


# [pr_diff] fail_to_pass
def test_cache_strategy_no_write_only():
    """CACHE_STRATEGY option no longer includes write-only mode."""
    content = (Path(REPO) / "cmake/Globals.cmake").read_text()
    cache_lines = [l for l in content.splitlines() if "CACHE_STRATEGY" in l and "option" in l.lower()]
    assert len(cache_lines) > 0, "Must find CACHE_STRATEGY option definition"
    combined = " ".join(cache_lines)
    assert "write-only" not in combined, "write-only should be removed from CACHE_STRATEGY options"
    # read-write and read-only should still be present
    assert "read-write" in combined, "read-write must still be an option"
    assert "read-only" in combined, "read-only must still be an option"


# [pr_diff] fail_to_pass
def test_build_mjs_sccache_migration():
    """build.mjs removes old ccache functions and integrates sccache stats."""
    result = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const src = fs.readFileSync('scripts/build.mjs', 'utf8');

// Old ccache cache management functions must be removed
const oldFns = ['getCachePath', 'isCacheReadEnabled', 'isCacheWriteEnabled', 'getDefaultBranch'];
const found = oldFns.filter(fn => src.includes('function ' + fn));
if (found.length > 0) {
    console.error('Old ccache functions still present: ' + found.join(', '));
    process.exit(1);
}

// Old fs imports that were only used for ccache cache copying
for (const sym of ['cpSync', 'mkdirSync', 'chmodSync']) {
    if (src.includes(sym)) {
        console.error('Old import still present: ' + sym);
        process.exit(1);
    }
}

// sccache --show-stats must be invoked after the build
if (!src.includes('sccache') || !src.includes('--show-stats')) {
    console.error('Missing sccache --show-stats integration');
    process.exit(1);
}

console.log('OK');
"""],
        cwd=REPO, capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"build.mjs check failed: {result.stderr or result.stdout}"


# [pr_diff] fail_to_pass
def test_bootstrap_sccache_install():
    """bootstrap.sh installs sccache from GitHub releases with correct version."""
    content = (Path(REPO) / "scripts/bootstrap.sh").read_text()
    # The install function should be install_sccache
    assert "install_sccache()" in content, "Must define install_sccache function"
    # Should download from mozilla/sccache GitHub releases
    assert "mozilla/sccache" in content, "Must download from mozilla/sccache releases"
    assert "v0.12.0" in content, "Must use correct sccache version 0.12.0"
    # The install_build_essentials should call install_sccache, not install_ccache
    lines = content.splitlines()
    in_essentials = False
    essentials_lines = []
    for line in lines:
        if "install_build_essentials()" in line:
            in_essentials = True
        elif in_essentials:
            if line.strip() == "}":
                break
            essentials_lines.append(line)
    essentials_text = "\n".join(essentials_lines)
    assert "install_sccache" in essentials_text, "install_build_essentials must call install_sccache"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation: CONTRIBUTING.md updates
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_contributing_sccache_install_section():
    """CONTRIBUTING.md documents sccache installation with S3 support."""
    content = (Path(REPO) / "CONTRIBUTING.md").read_text()
    # Must have a dedicated sccache installation section
    assert "sccache" in content.lower(), "CONTRIBUTING.md must mention sccache"
    # Must document S3 support requirement
    assert "S3" in content, "Must document S3 support requirement"
    # Must recommend cargo install with --features=s3
    assert "cargo install sccache" in content, "Must show cargo install command"
    assert "--features=s3" in content, "Must specify --features=s3 for S3 support"


# [pr_diff] fail_to_pass
def test_contributing_aws_credentials_section():
    """CONTRIBUTING.md documents AWS credentials setup for core developers."""
    content = (Path(REPO) / "CONTRIBUTING.md").read_text()
    assert "AWS" in content, "Must mention AWS credentials"
    assert "aws configure" in content, "Must document aws configure command"
    assert "core developer" in content.lower(), "Must clarify this section is for core developers"


# [pr_diff] fail_to_pass
def test_contributing_install_commands_use_sccache():
    """CONTRIBUTING.md macOS install command uses sccache, not ccache."""
    content = (Path(REPO) / "CONTRIBUTING.md").read_text()
    lines = content.splitlines()
    brew_lines = [l for l in lines if "brew install" in l and "automake" in l]
    assert len(brew_lines) > 0, "Must find macOS brew install line"
    assert "sccache" in brew_lines[0], "macOS brew install must include sccache"
    assert not re.search(r'\bccache\b', brew_lines[0]), "macOS brew install must not include standalone ccache (sccache is fine)"
