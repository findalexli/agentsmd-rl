"""
Task: expo-majorbabelpresetexpo-rename-and-enable-transformimportm
Repo: expo/expo @ e7f9f0359afa2414576dd57c9166272e3b64c5df
PR:   44239

Rename unstable_transformImportMeta → transformImportMeta and enable by default.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/expo"
PKG = f"{REPO}/packages/babel-preset-expo"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified build JS files must parse without errors."""
    for js_file in [
        "build/index.js",
        "build/import-meta-transform-plugin.js",
    ]:
        r = subprocess.run(
            ["node", "--check", js_file],
            cwd=PKG,
            capture_output=True,
            timeout=15,
        )
        assert r.returncode == 0, (
            f"{js_file} has syntax errors:\n{r.stderr.decode()}"
        )


# [static] pass_to_pass
def test_plugin_transforms_import_meta():
    """The import.meta transform plugin converts import.meta to globalThis.__ExpoImportMetaRegistry."""
    script = """const babel = require("@babel/core");
const { expoImportMetaTransformPluginFactory } = require("./build/import-meta-transform-plugin");
const plugin = expoImportMetaTransformPluginFactory(true);
const result = babel.transformSync("var x = import.meta.url;", {
    plugins: [plugin],
    filename: "test.js",
    caller: { name: "metro", platform: "ios" }
});
console.log(result.code);
"""
    r = subprocess.run(
        ["node", "-e", script],
        cwd=PKG,
        capture_output=True,
        timeout=15,
    )
    out = r.stdout.decode()
    assert r.returncode == 0, f"Plugin invocation failed:\n{r.stderr.decode()}"
    assert "globalThis.__ExpoImportMetaRegistry" in out, (
        f"Expected globalThis.__ExpoImportMetaRegistry in output, got: {out}"
    )


# ---------------------------------------------------------------------------
# Repo CI tests (pass_to_pass, repo_tests) — actual CI commands that work in Docker
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_preset_loads():
    """Repo's babel-preset-expo can be loaded with its dependencies (pass_to_pass)."""
    # Install deps outside workspace and test preset loading
    script = """
mkdir -p /tmp/test-preset
cd /tmp/test-preset
echo '{"name": "test", "version": "1.0.0"}' > package.json
npm install @babel/core @babel/generator @babel/helper-module-imports debug resolve-from @babel/plugin-proposal-decorators @babel/plugin-proposal-export-default-from @babel/plugin-syntax-export-default-from @babel/plugin-transform-class-static-block @babel/plugin-transform-export-namespace-from @babel/plugin-transform-flow-strip-types @babel/plugin-transform-modules-commonjs @babel/plugin-transform-object-rest-spread @babel/plugin-transform-parameters @babel/plugin-transform-private-methods @babel/plugin-transform-private-property-in-object @babel/plugin-transform-runtime @babel/preset-react @babel/preset-typescript babel-plugin-react-native-web babel-plugin-syntax-hermes-parser babel-plugin-transform-flow-enums @babel/runtime @react-native/babel-preset --silent 2>&1 | tail -1
mkdir -p node_modules/babel-preset-expo
cp -r /workspace/expo/packages/babel-preset-expo/build/* node_modules/babel-preset-expo/
cp /workspace/expo/packages/babel-preset-expo/lazy-imports-blacklist.js node_modules/babel-preset-expo/
node -e "const preset = require('babel-preset-expo'); console.log('PRESET_LOADED:', typeof preset);"
"""
    r = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Preset load test failed:\n{r.stderr[-500:]}"
    assert "PRESET_LOADED: function" in r.stdout, f"Preset not loaded as function:\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_import_meta_transform():
    """Repo's import.meta transform works with the preset (pass_to_pass)."""
    script = """
mkdir -p /tmp/test-transform
cd /tmp/test-transform
echo '{"name": "test", "version": "1.0.0"}' > package.json
npm install @babel/core @babel/generator @babel/helper-module-imports debug resolve-from @babel/plugin-proposal-decorators @babel/plugin-proposal-export-default-from @babel/plugin-syntax-export-default-from @babel/plugin-transform-class-static-block @babel/plugin-transform-export-namespace-from @babel/plugin-transform-flow-strip-types @babel/plugin-transform-modules-commonjs @babel/plugin-transform-object-rest-spread @babel/plugin-transform-parameters @babel/plugin-transform-private-methods @babel/plugin-transform-private-property-in-object @babel/plugin-transform-runtime @babel/preset-react @babel/preset-typescript babel-plugin-react-native-web babel-plugin-syntax-hermes-parser babel-plugin-transform-flow-enums @babel/runtime @react-native/babel-preset --silent 2>&1 | tail -1
mkdir -p node_modules/babel-preset-expo
cp -r /workspace/expo/packages/babel-preset-expo/build/* node_modules/babel-preset-expo/
cp /workspace/expo/packages/babel-preset-expo/lazy-imports-blacklist.js node_modules/babel-preset-expo/
node -e 'const babel = require("@babel/core"); const preset = require("babel-preset-expo"); function getCaller(props) { return props; } const options = { filename: "/unknown", babelrc: false, presets: [[preset, { unstable_transformImportMeta: true }]], sourceMaps: true, configFile: false, compact: false, comments: true, retainLines: true, caller: getCaller({ name: "metro", engine: "hermes", platform: "ios", isDev: true }) }; const sourceCode = "var url = import.meta.url;"; const result = babel.transformSync(sourceCode, options); if (result.code.includes("globalThis.__ExpoImportMetaRegistry")) { console.log("TRANSFORM_SUCCESS"); } else { console.log("TRANSFORM_FAILED:" + result.code); }'
"""
    r = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Transform test failed:\n{r.stderr[-500:]}"
    assert "TRANSFORM_SUCCESS" in r.stdout, f"Transform did not succeed:\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_build_syntax():
    """Repo's build files have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "build/index.js"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"build/index.js syntax check failed:\n{r.stderr}"

    r = subprocess.run(
        ["node", "--check", "build/import-meta-transform-plugin.js"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"build/import-meta-transform-plugin.js syntax check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_error_message_stable_name():
    """When plugin is disabled, error message references 'transformImportMeta' (not unstable_)."""
    script = """const babel = require("@babel/core");
const { expoImportMetaTransformPluginFactory } = require("./build/import-meta-transform-plugin");
const plugin = expoImportMetaTransformPluginFactory(false);
try {
    babel.transformSync("var x = import.meta.url;", {
        plugins: [plugin],
        filename: "test.js",
        caller: { name: "metro", platform: "ios" }
    });
    console.log("NO_ERROR");
} catch(e) {
    console.log(e.message);
}
"""
    r = subprocess.run(
        ["node", "-e", script],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=15,
    )
    out = r.stdout
    assert r.returncode == 0, f"Script failed:\n{r.stderr}"
    assert "NO_ERROR" not in out, "Expected error to be thrown for disabled plugin on iOS"
    # The error message must reference the stable option name
    assert "transformImportMeta" in out, (
        f"Error message should reference 'transformImportMeta', got: {out}"
    )
    assert "unstable_transformImportMeta" not in out, (
        f"Error message should NOT reference 'unstable_transformImportMeta', got: {out}"
    )


# [pr_diff] fail_to_pass
def test_readme_stable_option_name():
    """README documents transformImportMeta with default true (not unstable_ with default false)."""
    readme = Path(f"{PKG}/README.md").read_text()

    # Must have the stable option name as a heading (not unstable_)
    assert "### `transformImportMeta`" in readme, (
        "README should have a '### `transformImportMeta`' heading"
    )
    assert "### `unstable_transformImportMeta`" not in readme, (
        "README should not have '### `unstable_transformImportMeta`' heading"
    )

    # Must document the default as true (not false/server-only)
    # Find the transformImportMeta section
    idx = readme.index("### `transformImportMeta`")
    section = readme[idx:idx + 500]
    section_lower = section.lower()

    assert "defaults to `true`" in section_lower or ("default" in section_lower and "`true`" in section), (
        "README transformImportMeta section should state default is true"
    )

    # Should NOT say "at your own risk" anymore
    assert "at your own risk" not in section_lower, (
        "README should not say 'at your own risk' for the stable option"
    )


# [pr_diff] fail_to_pass
def test_typescript_types_use_stable_name():
    """TypeScript definitions use transformImportMeta (not unstable_)."""
    dts_file = Path(f"{PKG}/build/index.d.ts").read_text()

    # Check for stable option name
    assert "transformImportMeta?: boolean" in dts_file, (
        "TypeScript definitions should have 'transformImportMeta?: boolean'"
    )

    # Check that unstable_ version does NOT exist
    assert "unstable_transformImportMeta" not in dts_file, (
        "TypeScript definitions should NOT have 'unstable_transformImportMeta'"
    )

    # Check default is documented as true
    assert "@default `true`" in dts_file, (
        "TypeScript definitions should document @default `true`"
    )
