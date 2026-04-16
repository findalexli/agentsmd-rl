"""Test outputs for TanStack Router PR #6955 - Vite 7/8 bundler compatibility."""

import subprocess
import sys
import os

REPO = "/workspace/router"
PACKAGE_DIR = f"{REPO}/packages/start-plugin-core"


def test_utils_exports_exist():
    """Fail-to-pass: utils.ts exports the bundler detection functions."""
    # Read the utils.ts file
    utils_path = f"{PACKAGE_DIR}/src/utils.ts"
    with open(utils_path, 'r') as f:
        content = f.read()

    # Check for required exports
    assert "isRolldown" in content, "isRolldown export not found"
    assert "bundlerOptionsKey" in content, "bundlerOptionsKey export not found"
    assert "getBundlerOptions" in content, "getBundlerOptions export not found"


def test_isRolldown_logic():
    """Fail-to-pass: isRolldown checks for 'rolldownVersion' in vite."""
    utils_path = f"{PACKAGE_DIR}/src/utils.ts"
    with open(utils_path, 'r') as f:
        content = f.read()

    # Check the detection logic
    assert "'rolldownVersion' in vite" in content, \
        "isRolldown must check 'rolldownVersion' in vite"


def test_bundlerOptionsKey_logic():
    """Fail-to-pass: bundlerOptionsKey returns correct key based on isRolldown."""
    utils_path = f"{PACKAGE_DIR}/src/utils.ts"
    with open(utils_path, 'r') as f:
        content = f.read()

    # Should return 'rolldownOptions' or 'rollupOptions'
    assert "'rolldownOptions'" in content, "Should reference 'rolldownOptions'"
    assert "'rollupOptions'" in content, "Should reference 'rollupOptions'"
    assert "isRolldown" in content, "Should reference isRolldown"


def test_getBundlerOptions_logic():
    """Fail-to-pass: getBundlerOptions reads correct options from build config."""
    utils_path = f"{PACKAGE_DIR}/src/utils.ts"
    with open(utils_path, 'r') as f:
        content = f.read()

    # Should read rolldownOptions first, then rollupOptions
    assert "build?.rolldownOptions" in content, "Should check rolldownOptions first"
    assert "build?.rollupOptions" in content, "Should check rollupOptions as fallback"


def test_plugin_imports_utils():
    """Fail-to-pass: plugin.ts imports from utils.ts."""
    plugin_path = f"{PACKAGE_DIR}/src/plugin.ts"
    with open(plugin_path, 'r') as f:
        content = f.read()

    # Check import statement
    assert "from './utils'" in content, "plugin.ts should import from utils"
    assert "bundlerOptionsKey" in content, "Should import bundlerOptionsKey"
    assert "getBundlerOptions" in content, "Should import getBundlerOptions"


def test_plugin_uses_bundlerOptionsKey():
    """Fail-to-pass: plugin.ts uses bundlerOptionsKey instead of hardcoded 'rollupOptions'."""
    plugin_path = f"{PACKAGE_DIR}/src/plugin.ts"
    with open(plugin_path, 'r') as f:
        content = f.read()

    # Should use computed property [bundlerOptionsKey]
    assert "[bundlerOptionsKey]" in content, \
        "plugin.ts should use [bundlerOptionsKey] for dynamic key"

    # Should NOT have hardcoded rollupOptions: in the build config sections
    lines = content.split('\n')
    in_build_config = False
    hardcoded_count = 0
    for line in lines:
        if 'build:' in line:
            in_build_config = True
        if in_build_config:
            # Check for hardcoded rollupOptions: (not [bundlerOptionsKey])
            if 'rollupOptions:' in line and '[bundlerOptionsKey]' not in line:
                hardcoded_count += 1

    # The fix should eliminate hardcoded rollupOptions: in build configs
    # We allow rollupOptions in comments or imports
    assert hardcoded_count == 0, \
        f"Found {hardcoded_count} hardcoded 'rollupOptions:' in build configs"


def test_plugin_uses_getBundlerOptions():
    """Fail-to-pass: plugin.ts uses getBundlerOptions for reading input."""
    plugin_path = f"{PACKAGE_DIR}/src/plugin.ts"
    with open(plugin_path, 'r') as f:
        content = f.read()

    # Should call getBundlerOptions
    assert "getBundlerOptions(" in content, \
        "plugin.ts should call getBundlerOptions to read bundler options"


def test_preview_plugin_imports_utils():
    """Fail-to-pass: preview-server-plugin/plugin.ts imports from utils."""
    preview_path = f"{PACKAGE_DIR}/src/preview-server-plugin/plugin.ts"
    with open(preview_path, 'r') as f:
        content = f.read()

    assert "from '../utils'" in content, "preview plugin should import from utils"
    assert "getBundlerOptions" in content, "Should import getBundlerOptions"


def test_preview_plugin_uses_getBundlerOptions():
    """Fail-to-pass: preview plugin uses getBundlerOptions instead of direct access."""
    preview_path = f"{PACKAGE_DIR}/src/preview-server-plugin/plugin.ts"
    with open(preview_path, 'r') as f:
        content = f.read()

    # Should use getBundlerOptions
    assert "getBundlerOptions(serverEnv?.build)" in content, \
        "preview plugin should use getBundlerOptions for reading server input"

    # Should NOT directly access build.rollupOptions.input
    assert "build.rollupOptions.input" not in content, \
        "preview plugin should not directly access build.rollupOptions.input"


def test_modified_files_parseable():
    """Pass-to-pass: Modified TypeScript files have valid structure."""
    # Basic structural validation
    files_to_check = [
        f"{PACKAGE_DIR}/src/utils.ts",
        f"{PACKAGE_DIR}/src/plugin.ts",
        f"{PACKAGE_DIR}/src/preview-server-plugin/plugin.ts"
    ]

    for path in files_to_check:
        with open(path, 'r') as f:
            content = f.read()

        # Basic checks for valid TypeScript structure
        # Count opening and closing braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, f"Mismatched braces in {path}"

        # Check for basic import/export syntax (handle multiline imports)
        lines = content.split('\n')
        in_import = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import '):
                in_import = True
            if in_import:
                # Check for 'from' keyword or side-effect import completion
                if 'from' in stripped:
                    in_import = False
                elif stripped.endswith(';') and 'from' not in stripped:
                    # Side-effect import
                    in_import = False
                elif stripped.endswith('}'):
                    # End of import block, expect from on same or next line
                    pass
                # Check if this is the last line or next line has from
                if i < len(lines) - 1:
                    next_stripped = lines[i + 1].strip()
                    if 'from' in next_stripped or next_stripped.startswith('}'):
                        in_import = True
                else:
                    in_import = False


def test_code_no_duplicate_imports():
    """Pass-to-pass: No duplicate or conflicting import statements added."""
    # Read plugin.ts
    plugin_path = f"{PACKAGE_DIR}/src/plugin.ts"
    with open(plugin_path, 'r') as f:
        content = f.read()

    # Check for duplicate imports from utils
    import_count = content.count("from './utils'")
    assert import_count == 1, f"Should have exactly one import from utils, found {import_count}"

    # Read preview plugin
    preview_path = f"{PACKAGE_DIR}/src/preview-server-plugin/plugin.ts"
    with open(preview_path, 'r') as f:
        preview_content = f.read()

    import_count = preview_content.count("from '../utils'")
    assert import_count == 1, f"Should have exactly one import from utils in preview plugin, found {import_count}"


def test_utils_functions_exported_correctly():
    """Pass-to-pass: New utility functions are properly exported."""
    utils_path = f"{PACKAGE_DIR}/src/utils.ts"
    with open(utils_path, 'r') as f:
        content = f.read()

    # Check for export keywords
    assert content.count("export") >= 3, "Should have at least 3 export statements"

    # Check the functions are exported properly
    assert "export const isRolldown" in content or "export const bundlerOptionsKey" in content, \
        "Constants should be exported"
    assert "export function getBundlerOptions" in content or "export const getBundlerOptions" in content, \
        "getBundlerOptions should be exported"


def test_no_placeholder_code():
    """Pass-to-pass: No TODO or placeholder comments in implementation."""
    files_to_check = [
        f"{PACKAGE_DIR}/src/utils.ts",
        f"{PACKAGE_DIR}/src/plugin.ts",
        f"{PACKAGE_DIR}/src/preview-server-plugin/plugin.ts"
    ]

    for path in files_to_check:
        with open(path, 'r') as f:
            content = f.read()

        # Check for placeholder comments
        assert "TODO" not in content.upper(), f"Found TODO in {path}"
        assert "FIXME" not in content.upper(), f"Found FIXME in {path}"
        assert "XXX" not in content, f"Found XXX placeholder in {path}"


def test_repo_unit_tests_import_protection():
    """Repo's import protection unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run",
         "tests/importProtection/defaults.test.ts",
         "tests/importProtection/matchers.test.ts",
         "tests/importProtection/trace.test.ts",
         "tests/importProtection/utils.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=PACKAGE_DIR,
    )
    assert r.returncode == 0, f"Import protection tests failed:\n{r.stderr[-500:]}"


def test_repo_unit_tests_server():
    """Repo's server-related unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run",
         "tests/post-server-build.test.ts",
         "tests/prerender-ssrf.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=PACKAGE_DIR,
    )
    assert r.returncode == 0, f"Server-related tests failed:\n{r.stderr[-500:]}"


def test_repo_build():
    """Repo's build command for start-plugin-core passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:build", "--skip-nx-cache"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"
