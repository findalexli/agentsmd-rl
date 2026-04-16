"""
Test_outputs.py for prisma/prisma#29424
Tests the bootstrap CLI changes: auto-install deps, timeout handling, package manager detection
"""
import subprocess
import os
import tempfile

REPO = "/workspace/prisma"


def test_detect_package_manager_from_package_json_pnpm():
    """detectPackageManager reads packageManager field from package.json for pnpm (fail_to_pass)."""
    # Check the source code has the packageManager field detection logic
    with open(os.path.join(REPO, "packages/cli/src/bootstrap/template-scaffold.ts"), "r") as f:
        source = f.read()

    # The fix adds reading packageManager field from package.json
    # It should have code like: pkg.packageManager
    assert "pkg.packageManager" in source, \
        "detectPackageManager should read packageManager field from package.json"

    # Also check it handles pnpm specifically
    assert 'pm.startsWith("pnpm")' in source or "pm.startsWith('pnpm')" in source, \
        "detectPackageManager should check for pnpm in packageManager field"


def test_detect_package_manager_from_package_json_yarn():
    """detectPackageManager reads packageManager field from package.json for yarn (fail_to_pass)."""
    with open(os.path.join(REPO, "packages/cli/src/bootstrap/template-scaffold.ts"), "r") as f:
        source = f.read()

    assert 'pm.startsWith("yarn")' in source or "pm.startsWith('yarn')" in source, \
        "detectPackageManager should check for yarn in packageManager field"


def test_detect_package_manager_from_package_json_bun():
    """detectPackageManager reads packageManager field from package.json for bun (fail_to_pass)."""
    with open(os.path.join(REPO, "packages/cli/src/bootstrap/template-scaffold.ts"), "r") as f:
        source = f.read()

    assert 'pm.startsWith("bun")' in source or "pm.startsWith('bun')" in source, \
        "detectPackageManager should check for bun in packageManager field"


def test_detect_package_manager_lockfile_priority():
    """Lockfile takes priority over packageManager field (fail_to_pass)."""
    with open(os.path.join(REPO, "packages/cli/src/bootstrap/template-scaffold.ts"), "r") as f:
        source = f.read()

    # The existing lockfile checks should come BEFORE the packageManager check
    # Find positions of lockfile checks and packageManager check
    lockfile_pos = source.find("fs.existsSync(path.join(baseDir, 'yarn.lock'))")
    pkg_manager_pos = source.find("pkg.packageManager")

    assert lockfile_pos != -1, "Should have yarn.lock check"
    assert pkg_manager_pos != -1, "Should have packageManager check"
    assert lockfile_pos < pkg_manager_pos, \
        "Lockfile checks must come BEFORE packageManager check for priority to work"


def test_add_dev_dependencies_exists():
    """addDevDependencies function exists and is importable (fail_to_pass)."""
    with open(os.path.join(REPO, "packages/cli/src/bootstrap/template-scaffold.ts"), "r") as f:
        source = f.read()
    assert "export async function addDevDependencies" in source, \
        "addDevDependencies function should exist in template-scaffold.ts"


def test_template_scaffold_timeout_constant():
    """Template download timeout is 120 seconds (fail_to_pass)."""
    with open(os.path.join(REPO, "packages/cli/src/bootstrap/template-scaffold.ts"), "r") as f:
        source = f.read()
    # After fix: timeout should be 120_000 (120 seconds)
    # Before fix: timeout was 30_000 (30 seconds)
    assert "AbortSignal.timeout(120_000)" in source, \
        "Template download timeout should be 120_000 (120 seconds), not 30_000"


def test_decompress_gzip_has_error_handling():
    """decompressGzip has error handling for nodeStream (fail_to_pass)."""
    with open(os.path.join(REPO, "packages/cli/src/bootstrap/template-scaffold.ts"), "r") as f:
        source = f.read()
    # After fix: should have nodeStream.on('error', reject)
    # Before fix: no error handler
    assert "nodeStream.on('error', reject)" in source or 'nodeStream.on("error", reject)' in source, \
        "decompressGzip should handle errors from nodeStream with nodeStream.on('error', reject)"


def test_scaffold_template_method_exists():
    """Bootstrap.ts has scaffoldTemplate private method (fail_to_pass)."""
    with open(os.path.join(REPO, "packages/cli/src/bootstrap/Bootstrap.ts"), "r") as f:
        source = f.read()
    assert "scaffoldTemplate(" in source or "scaffoldTemplate (" in source, \
        "Bootstrap.ts should have a scaffoldTemplate method"


def test_repo_prettier_check():
    """Repo's prettier check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "prettier-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "FORCE_COLOR": "0"}
    )
    assert r.returncode == 0, f"prettier-check failed:\n{r.stderr[-500:]}"


def test_repo_check_engines_override():
    """Repo's check-engines-override script passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "check-engines-override"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "FORCE_COLOR": "0"}
    )
    assert r.returncode == 0, f"check-engines-override failed:\n{r.stderr[-500:]}"


def test_repo_vitest_passes():
    """Repo's vitest tests for template-scaffold pass (pass_to_pass)."""
    # Run vitest tests for the template-scaffold (package name is 'prisma')
    r = subprocess.run(
        ["pnpm", "--filter", "prisma", "test", "template-scaffold.vitest"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "FORCE_COLOR": "0"}
    )
    output = r.stdout + r.stderr

    # Check that tests passed
    assert r.returncode == 0, f"Vitest tests failed with code {r.returncode}:\n{output[-2000:]}"
    # Look for test success indicators
    assert ("template-scaffold" in output.lower() or "PASS" in output or "passed" in output.lower()), \
        f"Expected template-scaffold tests to pass:\n{output[-1000:]}"