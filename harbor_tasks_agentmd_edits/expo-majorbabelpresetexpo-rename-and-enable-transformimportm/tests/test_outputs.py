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
    script = """\
const babel = require('@babel/core');
const { expoImportMetaTransformPluginFactory } = require('./build/import-meta-transform-plugin');
const plugin = expoImportMetaTransformPluginFactory(true);
const result = babel.transformSync('var x = import.meta.url;', {
    plugins: [plugin],
    filename: 'test.js',
    caller: { name: 'metro', platform: 'ios' }
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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_error_message_stable_name():
    """When plugin is disabled, error message references 'transformImportMeta' (not unstable_)."""
    script = """\
const babel = require('@babel/core');
const { expoImportMetaTransformPluginFactory } = require('./build/import-meta-transform-plugin');
const plugin = expoImportMetaTransformPluginFactory(false);
try {
    babel.transformSync('var x = import.meta.url;', {
        plugins: [plugin],
        filename: 'test.js',
        caller: { name: 'metro', platform: 'ios' }
    });
    console.log('NO_ERROR');
} catch(e) {
    console.log(e.message);
}
"""
    r = subprocess.run(
        ["node", "-e", script],
        cwd=PKG,
        capture_output=True,
        timeout=15,
    )
    out = r.stdout.decode()
    assert r.returncode == 0, f"Script failed:\n{r.stderr.decode()}"
    assert "NO_ERROR" not in out, "Expected error to be thrown for disabled plugin on iOS"
    # The error message must reference the stable option name
    assert "transformImportMeta" in out, (
        f"Error message should reference 'transformImportMeta', got: {out}"
    )
    assert "unstable_transformImportMeta" not in out, (
        f"Error message should NOT reference 'unstable_transformImportMeta', got: {out}"
    )


# [pr_diff] fail_to_pass
def test_type_definition_renamed():
    """build/index.d.ts exports transformImportMeta (not unstable_) as the option type."""
    dts = Path(f"{PKG}/build/index.d.ts").read_text()
    assert "transformImportMeta?: boolean" in dts, (
        "build/index.d.ts should declare 'transformImportMeta?: boolean'"
    )
    assert "unstable_transformImportMeta" not in dts, (
        "build/index.d.ts should not contain 'unstable_transformImportMeta'"
    )


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit tests — README.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

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

    assert "defaults to `true`" in section_lower or "default" in section_lower and "`true`" in section, (
        "README transformImportMeta section should state default is true"
    )

    # Should NOT say "at your own risk" anymore
    assert "at your own risk" not in section_lower, (
        "README should not say 'at your own risk' for the stable option"
    )
