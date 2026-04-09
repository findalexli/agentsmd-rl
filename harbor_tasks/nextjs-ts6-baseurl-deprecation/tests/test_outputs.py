"""
Task: nextjs-ts6-baseurl-deprecation
Repo: vercel/next.js @ b163a8bf6642c7c849964d1238c13cc91d0c2252
PR:   91855

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
from pathlib import Path

REPO = "/workspace/next.js"
TARGET = f"{REPO}/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts"


def _node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script in the repo directory."""
    env = {**os.environ, "REPO_DIR": REPO, "TARGET": TARGET}
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout,
        cwd=REPO, env=env,
    )


# JS helper: transpile the target TS to CJS, patch imports for temp-dir execution.
# We override typescript.version to '6.0.0' so the TS6-specific code path runs
# (the repo ships TS 5.x, but the fix specifically targets TS>=6).
_TRANSPILE_AND_LOAD = r"""
const fs = require('fs');
const path = require('path');
const os = require('os');
const ts = require('/opt/ts-deps/node_modules/typescript');

const REPO_DIR = process.env.REPO_DIR;
const TARGET = process.env.TARGET;
const tmpdir = fs.mkdtempSync(path.join(os.tmpdir(), 'ts-test-'));

const src = fs.readFileSync(TARGET, 'utf-8');
const transpiled = ts.transpileModule(src, {
    compilerOptions: {
        module: ts.ModuleKind.CommonJS,
        target: ts.ScriptTarget.ES2020,
        esModuleInterop: true,
    }
});
let code = transpiled.outputText;

// Patch imports that can't resolve from the temp directory
code = code.replace(
    /require\("next\/dist\/compiled\/semver"\)/g,
    'require("/opt/ts-deps/node_modules/semver")'
);
code = code.replace(
    /require\("\.\.\/picocolors"\)/g,
    '({ bold: function(s){return s}, cyan: function(s){return s} })'
);
code = code.replace(
    /require\("\.\.\/fatal-error"\)/g,
    '({ FatalError: class FatalError extends Error {} })'
);
code = code.replace(
    /require\("\.\.\/is-error"\)/g,
    '({ default: function(e){ return e instanceof Error } })'
);

const jsPath = path.join(tmpdir, 'mod.js');
fs.writeFileSync(jsPath, code);
const mod = require(jsPath);

// Create a TS proxy that reports version 6.0.0 (to trigger the TS6 code path)
// but delegates all API calls to the real TypeScript module.
const mockTs = Object.create(ts);
Object.defineProperty(mockTs, 'version', { value: '6.0.0', writable: true });
"""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid_typescript():
    """Target file must parse as valid TypeScript."""
    r = _node(r"""
const fs = require('fs');
const ts = require('/opt/ts-deps/node_modules/typescript');
const src = fs.readFileSync(process.env.TARGET, 'utf-8');
if (src.length < 200) { console.error('file too small'); process.exit(1); }
ts.createSourceFile('test.ts', src, ts.ScriptTarget.Latest, true);
console.log('OK');
""")
    assert r.returncode == 0, f"TypeScript parse failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_inherited_baseurl_removed_ts6():
    """Inherited baseUrl (via extends) must be deleted from parsed options on TS>=6."""
    script = _TRANSPILE_AND_LOAD + r"""
(async () => {
    const scenarios = [
        { baseUrl: './src', label: 'relative ./src' },
        { baseUrl: '.', label: 'current dir dot' },
        { baseUrl: './lib/shared', label: 'nested relative path' },
    ];

    for (const { baseUrl, label } of scenarios) {
        const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'scenario-'));
        fs.writeFileSync(path.join(dir, 'base.json'), JSON.stringify({
            compilerOptions: { baseUrl, paths: { '@/*': ['./*'] } }
        }));
        fs.writeFileSync(path.join(dir, 'tsconfig.json'), JSON.stringify({
            extends: './base.json', compilerOptions: {}
        }));

        const result = await mod.getTypeScriptConfiguration(
            mockTs, path.join(dir, 'tsconfig.json'), true
        );
        const hasBaseUrl = result && result.options &&
            'baseUrl' in result.options && result.options.baseUrl !== undefined;
        if (hasBaseUrl) {
            console.error('FAIL [' + label + ']: baseUrl still present: ' + result.options.baseUrl);
            process.exit(1);
        }
        fs.rmSync(dir, { recursive: true, force: true });
    }

    fs.rmSync(tmpdir, { recursive: true, force: true });
    console.log('PASS');
})().catch(e => { console.error(e.message); process.exit(1); });
"""
    r = _node(script)
    assert r.returncode == 0, f"Inherited baseUrl not removed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_paths_rewritten_inherited_baseurl():
    """Paths must be rewritten to relative form when inherited baseUrl is removed on TS>=6."""
    script = _TRANSPILE_AND_LOAD + r"""
(async () => {
    const scenarios = [
        {
            baseUrl: './src',
            inputPaths: { '@/*': ['./*'], '@lib/*': ['lib/*'] },
            label: 'two aliases from ./src',
        },
        {
            baseUrl: '.',
            inputPaths: { 'utils/*': ['utils/*'] },
            label: 'current-dir single alias',
        },
        {
            baseUrl: './packages/core',
            inputPaths: { '#/*': ['./*'], '#utils/*': ['utils/*'] },
            label: 'nested baseUrl with hash aliases',
        },
    ];

    for (const { baseUrl, inputPaths, label } of scenarios) {
        const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'scenario-'));
        fs.writeFileSync(path.join(dir, 'base.json'), JSON.stringify({
            compilerOptions: { baseUrl, paths: inputPaths }
        }));
        fs.writeFileSync(path.join(dir, 'tsconfig.json'), JSON.stringify({
            extends: './base.json', compilerOptions: {}
        }));

        const result = await mod.getTypeScriptConfiguration(
            mockTs, path.join(dir, 'tsconfig.json'), true
        );
        const outPaths = result && result.options && result.options.paths;
        if (!outPaths) {
            console.error('FAIL [' + label + ']: no paths in result');
            process.exit(1);
        }

        // All path values must be relative (./ prefix)
        for (const [key, values] of Object.entries(outPaths)) {
            if (Array.isArray(values)) {
                for (const v of values) {
                    if (typeof v === 'string' && !v.startsWith('./')) {
                        console.error('FAIL [' + label + ']: non-relative path ' + key + ': ' + v);
                        process.exit(1);
                    }
                }
            }
        }

        // Must have wildcard '*' fallback
        if (!('*' in outPaths)) {
            console.error('FAIL [' + label + ']: missing * wildcard: ' + JSON.stringify(outPaths));
            process.exit(1);
        }

        fs.rmSync(dir, { recursive: true, force: true });
    }

    fs.rmSync(tmpdir, { recursive: true, force: true });
    console.log('PASS');
})().catch(e => { console.error(e.message); process.exit(1); });
"""
    r = _node(script)
    assert r.returncode == 0, f"Paths not rewritten:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_direct_baseurl_still_works():
    """Direct-declared baseUrl (not inherited) is still handled correctly."""
    script = _TRANSPILE_AND_LOAD + r"""
(async () => {
    const scenarios = [
        { baseUrl: '.', paths: { '@/*': ['src/*'] }, label: 'dot with src alias' },
        { baseUrl: './src', paths: { '#/*': ['./*'] }, label: './src with hash alias' },
        { baseUrl: '.', paths: {}, label: 'dot with empty paths' },
    ];

    for (const { baseUrl, paths: inputPaths, label } of scenarios) {
        const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'scenario-'));
        fs.writeFileSync(path.join(dir, 'tsconfig.json'), JSON.stringify({
            compilerOptions: { baseUrl, paths: inputPaths }
        }));

        const result = await mod.getTypeScriptConfiguration(
            mockTs, path.join(dir, 'tsconfig.json'), true
        );
        if (!result || !result.options || !result.options.paths ||
            Object.keys(result.options.paths).length === 0) {
            console.error('FAIL [' + label + ']: direct baseUrl handling broken');
            process.exit(1);
        }
        fs.rmSync(dir, { recursive: true, force: true });
    }

    fs.rmSync(tmpdir, { recursive: true, force: true });
    console.log('PASS');
})().catch(e => { console.error(e.message); process.exit(1); });
"""
    r = _node(script)
    assert r.returncode == 0, f"Direct baseUrl broken:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """Target file has substantial implementation, not stubs."""
    src = Path(TARGET).read_text()
    assert "export async function getTypeScriptConfiguration" in src, \
        "Missing getTypeScriptConfiguration export"
    lines = [l for l in src.split("\n") if l.strip() and not l.strip().startswith("//")]
    assert len(lines) >= 80, f"Only {len(lines)} meaningful lines"
    assert "semver" in src, "Missing semver reference"


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI/CD tests (p2p_enrichment)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typescript_lib_parses():
    """Repo TypeScript files in lib/typescript parse as valid TypeScript (pass_to_pass)."""
    script = r"""
const fs = require('fs');
const ts = require('/opt/ts-deps/node_modules/typescript');

const files = [
    '/workspace/next.js/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts',
    '/workspace/next.js/packages/next/src/lib/typescript/writeConfigurationDefaults.ts',
];

for (const file of files) {
    const src = fs.readFileSync(file, 'utf-8');
    // Check file has substantial content
    const lines = src.split('\n').filter(l => l.trim() && !l.trim().startsWith('//'));
    if (lines.length < 10) {
        console.error('File too small: ' + file + ' (' + lines.length + ' lines)');
        process.exit(1);
    }
    // Must parse as valid TypeScript
    try {
        ts.createSourceFile('test.ts', src, ts.ScriptTarget.Latest, true);
    } catch (e) {
        console.error('Parse failed for ' + file + ': ' + e.message);
        process.exit(1);
    }
}
console.log('PASS');
"""
    r = _node(script)
    assert r.returncode == 0, f"TypeScript lib files parse failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_getTypeScriptConfiguration_exports():
    """Target file exports required functions and types (pass_to_pass)."""
    src = Path(TARGET).read_text()

    # Required exports must exist
    assert "export async function getTypeScriptConfiguration" in src, \
        "Missing getTypeScriptConfiguration export"

    # Check for helper functions (they're used in the fix)
    required_patterns = [
        "resolvePathAliasTarget",
        "semver",
    ]
    for pattern in required_patterns:
        assert pattern in src, f"Missing required pattern: {pattern}"
