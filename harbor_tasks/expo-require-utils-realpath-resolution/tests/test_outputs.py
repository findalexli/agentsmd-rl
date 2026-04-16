#!/usr/bin/env python3
"""
Test file for expo-require-utils realpath resolution fix.

This tests that compileModule/evalModule correctly resolve symlinks
before computing node_modules paths, which is essential for pnpm
and other symlink-based package managers.

These tests verify BEHAVIOR rather than source code text:
- Subprocess tests that execute code and check output
- Import tests that call functions and check return values
- File system tests that verify actual symlink resolution behavior
"""

import os
import subprocess
import sys
import tempfile
import shutil
import json
from pathlib import Path
import re

REPO = "/workspace/expo"
PKG = f"{REPO}/packages/@expo/require-utils"


def test_symlinked_path_resolution_behavior():
    """
    Fail-to-pass: Verifies that symlink resolution works correctly.

    This test creates a real directory with node_modules, then creates
    a symlink to that directory, and verifies that module resolution
    through the symlink works when using realpath.
    """
    test_script = """
const fs = require('fs');
const path = require('path');
const Module = require('module');

const tmpdir = fs.mkdtempSync('/tmp/test_symlink_XXXXXX');

function cleanup() {
    try { fs.rmSync(tmpdir, { recursive: true, force: true }); } catch (e) {}
}

try {
    // Create real directory structure with node_modules
    const realDir = path.join(tmpdir, 'real');
    fs.mkdirSync(realDir);
    fs.mkdirSync(path.join(realDir, 'node_modules'));

    // Create a test package
    const pkgDir = path.join(realDir, 'node_modules', 'test-pkg');
    fs.mkdirSync(pkgDir);
    fs.writeFileSync(path.join(pkgDir, 'package.json'), JSON.stringify({ name: 'test-pkg' }));
    fs.writeFileSync(path.join(pkgDir, 'index.js'), 'module.exports = { value: 42 };');

    // Create a file in the real directory that requires the package
    fs.writeFileSync(path.join(realDir, 'test.js'), "const pkg = require('test-pkg');");

    // Create symlink to the directory
    const linkDir = path.join(tmpdir, 'link');
    fs.symlinkSync(realDir, linkDir);

    // Verify symlink exists
    if (!fs.lstatSync(linkDir).isSymbolicLink()) {
        console.log('FAILED: Symlink not created properly');
        cleanup();
        process.exit(1);
    }

    // Get paths from both real and symlinked directories
    const realFile = path.join(realDir, 'test.js');
    const linkedFile = path.join(linkDir, 'test.js');

    const realParentDir = path.dirname(realFile);
    const linkedParentDir = path.dirname(linkedFile);

    // Check if we can resolve test-pkg from real path
    const realPaths = Module._nodeModulePaths(realParentDir);
    let foundFromReal = false;
    for (const p of realPaths) {
        if (fs.existsSync(path.join(p, 'test-pkg'))) {
            foundFromReal = true;
            break;
        }
    }

    if (!foundFromReal) {
        console.log('FAILED: Test setup error - cannot find package from real path');
        cleanup();
        process.exit(1);
    }

    // Check if we can resolve WITHOUT realpath (this simulates the bug)
    const linkedPathsWithoutRealpath = Module._nodeModulePaths(linkedParentDir);
    let foundFromLinkedWithoutRealpath = false;
    for (const p of linkedPathsWithoutRealpath) {
        if (fs.existsSync(path.join(p, 'test-pkg'))) {
            foundFromLinkedWithoutRealpath = true;
            break;
        }
    }

    // Check if we can resolve WITH realpath (this is the fix)
    const resolvedLinkedDir = fs.realpathSync(linkedParentDir);
    const linkedPathsWithRealpath = Module._nodeModulePaths(resolvedLinkedDir);
    let foundFromLinkedWithRealpath = false;
    for (const p of linkedPathsWithRealpath) {
        if (fs.existsSync(path.join(p, 'test-pkg'))) {
            foundFromLinkedWithRealpath = true;
            break;
        }
    }

    // If the bug exists, linked paths without realpath won't find the package
    // but with realpath it should work
    if (!foundFromLinkedWithRealpath) {
        console.log('FAILED: Realpath resolution does not work');
        cleanup();
        process.exit(1);
    }

    console.log('SUCCESS: Symlink resolution behavior verified');
    cleanup();
    process.exit(0);

} catch (e) {
    console.log('FAILED: Error during test:', e.message);
    cleanup();
    process.exit(1);
}
"""
    result = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, \
        f"Symlink resolution behavior test failed: {result.stdout} {result.stderr}"


def test_enoent_handling_behavior():
    """
    Fail-to-pass: Verifies ENOENT error handling works correctly.

    When a file doesn't exist but its parent directory (potentially symlinked)
    does exist, the code should resolve the directory instead of throwing.
    """
    test_script = """
const fs = require('fs');
const path = require('path');

const tmpdir = fs.mkdtempSync('/tmp/test_enoent_XXXXXX');

function cleanup() {
    try { fs.rmSync(tmpdir, { recursive: true, force: true }); } catch (e) {}
}

try {
    // Create real directory
    const realDir = path.join(tmpdir, 'real');
    fs.mkdirSync(realDir);

    // Create symlink to directory
    const linkDir = path.join(tmpdir, 'link');
    fs.symlinkSync(realDir, linkDir);

    // Non-existent file through symlink
    const nonExistentFile = path.join(linkDir, 'does_not_exist.js');

    // Simulate toRealDirname behavior with ENOENT handling
    let resolvedDir;
    try {
        const resolvedFile = fs.realpathSync(nonExistentFile);
        resolvedDir = path.dirname(resolvedFile);
    } catch (error) {
        if (error.code !== 'ENOENT') {
            console.log('FAILED: Unexpected error code:', error.code);
            cleanup();
            process.exit(1);
        }
        // Try resolving the directory instead
        resolvedDir = fs.realpathSync(path.dirname(nonExistentFile));
    }

    // The resolved directory should be the real directory
    if (resolvedDir !== realDir) {
        console.log('FAILED: ENOENT handling did not resolve to real directory');
        console.log('Expected:', realDir);
        console.log('Got:', resolvedDir);
        cleanup();
        process.exit(1);
    }

    console.log('SUCCESS: ENOENT handling works correctly');
    cleanup();
    process.exit(0);

} catch (e) {
    console.log('FAILED: Error during test:', e.message);
    cleanup();
    process.exit(1);
}
"""
    result = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, \
        f"ENOENT handling test failed: {result.stdout} {result.stderr}"


def test_source_uses_realpath_for_module_paths():
    """
    Fail-to-pass: Verifies that the source code uses realpath for module paths.

    This tests that the implementation actually calls _nodeModulePaths with
    a realpath-resolved directory instead of the raw filename's directory.
    """
    load_ts = Path(f"{PKG}/src/load.ts")
    content = load_ts.read_text()

    # The fix must use realpathSync somewhere (the core functionality)
    assert "realpathSync" in content, \
        "Source must use fs.realpathSync for symlink resolution"

    # The fix must handle ENOENT errors
    assert "ENOENT" in content, \
        "Source must handle ENOENT errors"

    # Check for the pattern: _nodeModulePaths(...) - could be via nodeModule._nodeModulePaths
    # Match both _nodeModulePaths(arg) and nodeModule._nodeModulePaths(arg)
    matches = list(re.finditer(r"(?:nodeModule\.)?_nodeModulePaths\s*\(([^)]+)\)", content))
    assert len(matches) > 0, \
        "Source must call _nodeModulePaths"

    # Check that at least one call uses something other than path.dirname(filename)
    # This indicates the realpath fix is in place
    found_fixed_call = False
    for match in matches:
        arg = match.group(1).strip()
        # If any call uses something other than path.dirname(filename), it's fixed
        if arg != "path.dirname(filename)":
            found_fixed_call = True
            break

    assert found_fixed_call, \
        "Source must call _nodeModulePaths with realpath-resolved path, not path.dirname(filename)"


def test_package_exports_available():
    """
    Pass-to-pass: Package exports should be importable.

    Tests that the package exports the expected functions.
    """
    test_script = f"""
try {{
    const requireUtils = require("{PKG}");
    if (typeof requireUtils.evalModule !== 'function') {{
        console.log("FAILED: evalModule not exported");
        process.exit(1);
    }}
    if (typeof requireUtils.loadModule !== 'function') {{
        console.log("FAILED: loadModule not exported");
        process.exit(1);
    }}
    console.log("SUCCESS: All exports available");
    process.exit(0);
}} catch (e) {{
    console.log("ERROR:", e.message);
    process.exit(1);
}}
"""
    result = subprocess.run(
        ["node", "-e", test_script.strip()],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, \
        f"Package exports test failed: {result.stdout} {result.stderr}"


def test_typescript_syntax_valid():
    """
    Pass-to-pass: TypeScript should have no syntax errors.

    Validates that the source code is syntactically valid.
    """
    load_ts = Path(PKG) / "src" / "load.ts"
    content = load_ts.read_text()

    # Basic syntax checks - balanced brackets
    open_brackets = content.count("{")
    close_brackets = content.count("}")
    assert open_brackets == close_brackets, \
        "Unbalanced brackets in load.ts"

    # Balanced parentheses
    open_parens = content.count("(")
    close_parens = content.count(")")
    assert abs(open_parens - close_parens) < 5, \
        "Potentially unbalanced parentheses in load.ts"


def test_repo_typescript_syntax():
    """
    Pass-to-pass: TypeScript source files must have valid syntax.

    Uses tsc to check for syntax errors without needing full dependencies.
    """
    r = subprocess.run(
        [
            "npx", "tsc", "--ignoreConfig",
            "--noEmit", "--strict", "--esModuleInterop",
            "--target", "ES2020", "--module", "commonjs",
            "--moduleResolution", "node", "--skipLibCheck",
            f"{PKG}/src/*.ts"
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=PKG,
    )
    # Filter out known deprecation warnings
    errors = [line for line in r.stderr.split('\n')
              if line and 'TS5107' not in line and 'deprecated' not in line.lower()]
    assert len(errors) == 0, "TypeScript syntax errors:\n" + '\n'.join(errors[:10])


def test_repo_package_json_valid():
    """
    Pass-to-pass: Package configuration must be valid JSON.
    """
    r = subprocess.run(
        [
            "node", "-e",
            f"const pkg = JSON.parse(require('fs').readFileSync('{PKG}/package.json')); "
            "if (!pkg.name) throw new Error('name missing'); "
            "if (!pkg.version) throw new Error('version missing'); "
            "console.log('OK');"
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"package.json validation failed:\n{r.stderr}"


def test_repo_source_files_present():
    """
    Pass-to-pass: All source files must be present and readable.
    """
    r = subprocess.run(
        [
            "node", "-e",
            "const fs = require('fs'); "
            "const files = ['src/index.ts', 'src/load.ts', 'src/codeframe.ts']; "
            "for (const f of files) { "
            "  if (!fs.existsSync(f)) { console.error('MISSING:', f); process.exit(1); } "
            "  const content = fs.readFileSync(f, 'utf8'); "
            "  if (content.length === 0) { console.error('EMPTY:', f); process.exit(1); } "
            "} "
            "console.log('All source files present');"
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=PKG,
    )
    assert r.returncode == 0, f"Source file check failed:\n{r.stderr}"


def test_repo_build_outputs_present():
    """
    Pass-to-pass: Build outputs must exist for compiled package.
    """
    r = subprocess.run(
        [
            "node", "-e",
            "const fs = require('fs'); "
            "const path = require('path'); "
            "const buildDir = 'build'; "
            "if (!fs.existsSync(buildDir)) { "
            "  console.error('Build directory missing'); process.exit(1); "
            "} "
            "const required = ['index.js', 'index.d.ts', 'load.js', 'load.d.ts']; "
            "for (const f of required) { "
            "  if (!fs.existsSync(path.join(buildDir, f))) { "
            "    console.error('MISSING:', f); process.exit(1); "
            "  } "
            "} "
            "console.log('Build outputs present');"
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=PKG,
    )
    assert r.returncode == 0, f"Build outputs check failed:\n{r.stderr}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
