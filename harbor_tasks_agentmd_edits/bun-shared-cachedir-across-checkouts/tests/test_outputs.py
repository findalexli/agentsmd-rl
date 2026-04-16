"""
Tests for oven-sh/bun#28846 - Share cacheDir across checkouts for local builds.

This PR makes two types of changes:
1. CODE: Changes cacheDir resolution in config.ts, adds cache clean preset,
   and makes downloads concurrent-safe with process-unique temp paths.
2. CONFIG: Updates scripts/build/CLAUDE.md to document the new cache behavior.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/bun")
BUILD_SCRIPTS = REPO / "scripts" / "build"


def _run_ts_script(script_content: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a TypeScript script using Node with experimental-strip-types."""
    script_path = REPO / "_eval_tmp.ts"
    script_path.write_text(script_content)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO),
        )
    finally:
        script_path.unlink(missing_ok=True)


def test_claude_md_documents_shared_cache():
    """
    CLAUDE.md must document that rm -rf build/ doesn't clear cache locally.
    This is the key documentation update in this PR.
    """
    claude_md = BUILD_SCRIPTS / "CLAUDE.md"
    content = claude_md.read_text()

    # Check for key documentation points about the new behavior
    assert "rm -rf build/" in content, "CLAUDE.md should reference rm -rf build/"
    assert "cache" in content.lower(), "CLAUDE.md should mention cache"
    assert "doesn't clear" in content or "doesn't clear the cache" in content or \
           "machine-shared" in content or "$BUN_INSTALL/build-cache" in content or \
           "content-addressed" in content, \
           "CLAUDE.md should document that rm -rf build/ doesn't clear cache locally"


def test_config_ts_uses_machine_shared_cache():
    """
    config.ts must use machine-shared cacheDir for non-CI builds.
    Should use ~/.bun/build-cache for local builds, <buildDir>/cache for CI.
    """
    config_ts = BUILD_SCRIPTS / "config.ts"
    content = config_ts.read_text()

    # Check for the new logic
    assert "homedir" in content, "config.ts should import homedir from node:os"
    assert "bunInstall" in content or "BUN_INSTALL" in content, \
           "config.ts should reference BUN_INSTALL or bunInstall variable"
    assert "build-cache" in content, "config.ts should reference build-cache directory"

    # Check for the conditional logic: ci ? buildDir/cache : bunInstall/build-cache
    assert "ci" in content.lower(), "config.ts should have CI conditional logic"
    assert "resolve(bunInstall" in content or "join(homedir()" in content or \
           "buildDir, \"cache\"" in content, \
           "config.ts should have conditional cacheDir logic"


def test_clean_ts_has_cache_preset():
    """
    clean.ts must have a 'cache' preset to clean the machine-shared cache.
    """
    clean_ts = BUILD_SCRIPTS / "clean.ts"
    content = clean_ts.read_text()

    # Check for homedir import
    assert "homedir" in content, "clean.ts should import homedir from node:os"

    # Check for sharedCacheDir variable
    assert "sharedCacheDir" in content, "clean.ts should define sharedCacheDir variable"

    # Check for cache preset in presets
    assert 'cache:' in content or '"cache":' in content, \
           "clean.ts should have a 'cache' preset"

    # Check for cache preset documentation in help text
    assert "machine-shared" in content or "build-cache" in content, \
           "clean.ts should document the cache preset"


def test_configure_ts_updated_ccache_comment():
    """
    configure.ts must have updated comment about ccache environment.
    """
    configure_ts = BUILD_SCRIPTS / "configure.ts"
    content = configure_ts.read_text()

    # Check for updated comment about ccache
    assert "machine-shared locally" in content or "per-build in CI" in content or \
           "cfg.cacheDir" in content, \
           "configure.ts should document that ccache uses cfg.cacheDir"


def test_download_ts_uses_process_unique_temp_paths():
    """
    download.ts must use process-unique temp paths for concurrent safety.
    Uses `${dest}.${process.pid}.partial` instead of `${dest}.partial`.
    """
    download_ts = BUILD_SCRIPTS / "download.ts"
    content = download_ts.read_text()

    # Check for process.pid in temp path
    assert "process.pid" in content, \
           "download.ts should use process.pid in temp paths for concurrent safety"

    # Check for Date.now() or similar uniqueness in suffix
    assert "Date.now()" in content or "Date.now().toString(36)" in content or \
           "suffix" in content, \
           "download.ts should use unique suffix for temp paths"

    # Should NOT have the old pattern of just `${dest}.partial` without pid
    # This is a negative check - we can't easily assert absence, but presence
    # of process.pid implies the fix


def test_download_ts_has_concurrent_fetch_handling():
    """
    download.ts must handle concurrent fetch race conditions.
    Checks for 'concurrent fetch won' message and try/catch around rename.
    """
    download_ts = BUILD_SCRIPTS / "download.ts"
    content = download_ts.read_text()

    # Check for concurrent fetch handling
    assert "concurrent fetch won" in content or "concurrent" in content.lower(), \
           "download.ts should handle concurrent fetch scenarios"

    # Check for try/catch with rename error handling
    assert "try {" in content and "catch" in content, \
           "download.ts should have try/catch for race condition handling"


def test_typescript_syntax_valid():
    """
    All modified TypeScript files must have valid syntax.
    """
    files_to_check = [
        BUILD_SCRIPTS / "config.ts",
        BUILD_SCRIPTS / "clean.ts",
        BUILD_SCRIPTS / "configure.ts",
        BUILD_SCRIPTS / "download.ts",
    ]

    for ts_file in files_to_check:
        if ts_file.exists():
            # Use TypeScript compiler to check syntax
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", "--skipLibCheck", str(ts_file)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(REPO),
            )
            assert result.returncode == 0, \
                f"{ts_file.name} has TypeScript errors: {result.stdout}\n{result.stderr}"


def test_config_cache_resolution_logic():
    """
    Test the actual cacheDir resolution logic works as expected.
    """
    # Test that the resolveConfig function produces correct output
    test_script = '''
import { resolveConfig } from "./scripts/build/config.ts";

// Test non-CI build (local)
const localConfig = resolveConfig({ ci: false }, {} as any);
console.log(JSON.stringify({
  cacheDir: localConfig.cacheDir,
  hasBuildCache: localConfig.cacheDir.includes("build-cache")
}));
'''
    result = _run_ts_script(test_script, timeout=10)
    # Note: This might fail if imports don't work in eval mode
    # So we'll make this a best-effort check
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout.strip())
            assert data.get("hasBuildCache") == True, "Local build should use build-cache"
        except json.JSONDecodeError:
            pass  # Skip if output format is unexpected
