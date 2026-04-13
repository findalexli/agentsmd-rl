"""
Task: bun-install-scanner-silent-exit
Repo: oven-sh/bun @ 1d50d640f8fec6ce2d144f0cfd204e30da373c64
PR:   28196

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
IWM = f"{REPO}/src/install/PackageManager/install_with_manager.zig"
SS = f"{REPO}/src/install/PackageManager/security_scanner.zig"
REGRESSION_TEST = f"{REPO}/test/regression/issue/28193.test.ts"


def _node(script, timeout=30):
    """Execute JavaScript via node subprocess."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _parse_json(r):
    """Parse the last line of node output as JSON."""
    assert r.returncode == 0, f"Node error: {r.stderr}"
    lines = r.stdout.strip().splitlines()
    assert lines, f"No output from node: {r.stderr}"
    return json.loads(lines[-1])


# Shared: extract the security scanner error switch block from install_with_manager.zig
_IWM_BLOCK = (
    r"const fs = require('fs');"
    "\n"
    r"const text = fs.readFileSync('" + IWM + r"', 'utf8');"
    "\n"
    r"const m = text.match(/performSecurityScanAfterResolution[\s\S]*?catch\s*\|\w+\|\s*\{([\s\S]*?)\n\s*Global\.exit/);"
    "\n"
    r"if (!m) { console.log(JSON.stringify({error: 'block_not_found'})); process.exit(0); }"
    "\n"
    r"const block = m[1];"
    "\n"
)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — subprocess-executed tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_catch_all_produces_output():
    """Empty else => {} catch-all replaced with Output.* error messages."""
    r = _node(_IWM_BLOCK + r"""
    if (/else\s*=\>\s*\{\s*\}/.test(block)) {
        console.log(JSON.stringify({error: 'empty_else'})); process.exit(0);
    }
    const em = block.match(/else\s*=\>\s*\|?\w*\|?\s*\{([\s\S]*?)\}/);
    if (em) {
        const body = em[1].trim();
        if (!body || !/Output\.\w+\s*\(/.test(body)) {
            console.log(JSON.stringify({error: 'else_no_output'})); process.exit(0);
        }
    }
    const branches = block.match(/=\>\s*(?:\|[^|]*\|)?\s*\{[^}]*Output\.\w+\s*\(/g) || [];
    if (branches.length < 2) {
        console.log(JSON.stringify({error: 'few_branches', count: branches.length})); process.exit(0);
    }
    console.log(JSON.stringify({ok: true, branches: branches.length}));
    """)
    data = _parse_json(r)
    assert "ok" in data, f"Check failed: {data}"


# [pr_diff] fail_to_pass
def test_error_variant_coverage():
    """3+ named error variants or dynamic catch-all produce diagnostic output."""
    r = _node(_IWM_BLOCK + r"""
    const named = block.match(/error\.\w+\s*=>/g) || [];
    const outputCalls = block.match(/Output\.\w+\(/g) || [];
    const hasDynamic = /else\s*=\>\s*\|(\w+)\|[\s\S]*?@errorName\(\1\)/.test(block);
    if (named.length >= 3 && outputCalls.length >= 3) {
        console.log(JSON.stringify({ok: true, strategy: 'named', named: named.length}));
    } else if (hasDynamic) {
        console.log(JSON.stringify({ok: true, strategy: 'dynamic'}));
    } else {
        console.log(JSON.stringify({error: 'insufficient', named: named.length, calls: outputCalls.length}));
    }
    """)
    data = _parse_json(r)
    assert "ok" in data, f"Insufficient coverage: {data}"


# [pr_diff] fail_to_pass
def test_error_printing_centralized():
    """Error printing removed from security_scanner.zig, centralized in install_with_manager.zig."""
    r = _node(r"""
    const fs = require('fs');
    const text = fs.readFileSync('""" + SS + r"""', 'utf8');
    const errors = ['InvalidPackageID', 'PartialInstallFailed', 'NoPackagesInstalled', 'SecurityScannerInWorkspace'];
    const violations = [];
    for (const err of errors) {
        const pat = new RegExp('Output\\\\.(?:errGeneric|pretty)\\\\([^)]*\\\\)[\\\\s\\\\S]*?return error\\\\.' + err);
        if (pat.test(text)) violations.push(err);
    }
    if (violations.length > 0) {
        console.log(JSON.stringify({error: 'duplicates', violations}));
    } else {
        console.log(JSON.stringify({ok: true}));
    }
    """)
    data = _parse_json(r)
    assert "ok" in data, f"Duplication found: {data}"


# [pr_diff] fail_to_pass
def test_error_variant_propagated():
    """The .error variant propagated instead of collapsed into SecurityScannerRetryFailed."""
    r = _node(r"""
    const fs = require('fs');
    const text = fs.readFileSync('""" + SS + r"""', 'utf8');
    const m = text.match(/fn performSecurityScanAfterResolution\b([\s\S]*?)(?:\nfn |\npub fn |$)/);
    if (!m) { console.log(JSON.stringify({error: 'func_not_found'})); process.exit(0); }
    const func = m[1];
    const hasCollapse = /else\s*=\>\s*return\s+error\.SecurityScannerRetryFailed/.test(func);
    const hasProp = /\.@"error"\s*=\>\s*\|/.test(func) || /\.error\s*=\>\s*\|/.test(func) || /inline\s+else\s*=\>\s*\|/.test(func);
    if (hasCollapse) {
        console.log(JSON.stringify({error: 'collapsed'}));
    } else if (hasProp) {
        console.log(JSON.stringify({ok: true}));
    } else {
        console.log(JSON.stringify({error: 'no_propagation'}));
    }
    """)
    data = _parse_json(r)
    assert "ok" in data, f"Propagation issue: {data}"


# [pr_diff] fail_to_pass
def test_uses_err_generic():
    """Error messages use Output.errGeneric, not Output.pretty with <red>."""
    r = _node(_IWM_BLOCK + r"""
    const hasPrettyErrors = /Output\.pretty\s*\(\s*"<red>/.test(block);
    const hasErrOutput = /Output\.err/.test(block);
    if (!hasErrOutput) { console.log(JSON.stringify({error: 'no_err_output'})); process.exit(0); }
    if (hasPrettyErrors) { console.log(JSON.stringify({error: 'uses_pretty_red'})); process.exit(0); }
    console.log(JSON.stringify({ok: true}));
    """)
    data = _parse_json(r)
    assert "ok" in data, f"Formatting check failed: {data}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — regression test validation via node
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass
def test_regression_test_location():
    """Regression test at test/regression/issue/28193.test.ts with valid test structure."""
    r = _node(r"""
    const fs = require('fs');
    const p = '""" + REGRESSION_TEST + r"""';
    if (!fs.existsSync(p)) { console.log(JSON.stringify({error: 'not_found'})); process.exit(0); }
    const content = fs.readFileSync(p, 'utf8');
    const lines = content.split('\n');
    if (lines.length <= 5) { console.log(JSON.stringify({error: 'too_short', lines: lines.length})); process.exit(0); }
    const tests = (content.match(/\btest\(/g) || []).length;
    const expects = (content.match(/\bexpect\(/g) || []).length;
    if (tests === 0) { console.log(JSON.stringify({error: 'no_tests'})); process.exit(0); }
    console.log(JSON.stringify({ok: true, tests, expects, lines: lines.length}));
    """)
    data = _parse_json(r)
    assert "ok" in data, f"Regression test check failed: {data}"


# [agent_config] fail_to_pass
def test_regression_test_uses_harness():
    """Regression test imports bunExe and bunEnv from 'harness'."""
    r = _node(r"""
    const fs = require('fs');
    const p = '""" + REGRESSION_TEST + r"""';
    if (!fs.existsSync(p)) { console.log(JSON.stringify({error: 'not_found'})); process.exit(0); }
    const content = fs.readFileSync(p, 'utf8');
    if (!/from\s+"harness"/.test(content)) { console.log(JSON.stringify({error: 'no_harness_import'})); process.exit(0); }
    if (!content.includes('bunExe')) { console.log(JSON.stringify({error: 'no_bunExe'})); process.exit(0); }
    if (!content.includes('bunEnv')) { console.log(JSON.stringify({error: 'no_bunEnv'})); process.exit(0); }
    console.log(JSON.stringify({ok: true}));
    """)
    data = _parse_json(r)
    assert "ok" in data, f"Harness check failed: {data}"


# [agent_config] fail_to_pass
def test_regression_test_uses_tempdir():
    """Regression test uses tempDir from 'harness', not tmpdirSync/mkdtempSync."""
    r = _node(r"""
    const fs = require('fs');
    const p = '""" + REGRESSION_TEST + r"""';
    if (!fs.existsSync(p)) { console.log(JSON.stringify({error: 'not_found'})); process.exit(0); }
    const content = fs.readFileSync(p, 'utf8');
    if (!content.includes('tempDir')) { console.log(JSON.stringify({error: 'no_tempDir'})); process.exit(0); }
    if (content.includes('tmpdirSync')) { console.log(JSON.stringify({error: 'uses_tmpdirSync'})); process.exit(0); }
    if (content.includes('mkdtempSync')) { console.log(JSON.stringify({error: 'uses_mkdtempSync'})); process.exit(0); }
    console.log(JSON.stringify({ok: true}));
    """)
    data = _parse_json(r)
    assert "ok" in data, f"tempDir check failed: {data}"


# ---------------------------------------------------------------------------
# Pass-to-pass — preserved from original
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_workspace_error_preserved():
    """SecurityScannerInWorkspace error handling still present in install_with_manager.zig."""
    text = Path(IWM).read_text()
    assert "SecurityScannerInWorkspace" in text


# [pr_diff] pass_to_pass
def test_error_types_preserved():
    """security_scanner.zig still returns proper error types."""
    text = Path(SS).read_text()
    expected = ["InvalidPackageID", "PartialInstallFailed", "NoPackagesInstalled", "SecurityScannerInWorkspace"]
    found = sum(1 for e in expected if f"return error.{e}" in text)
    assert found >= 3, f"Only {found}/4 expected error types still returned"


# [static] pass_to_pass
def test_anti_stub():
    """Both Zig source files have substantial content."""
    assert len(Path(IWM).read_text().splitlines()) > 200
    assert len(Path(SS).read_text().splitlines()) > 50


# [agent_config] pass_to_pass
def test_exit_code_assertion_last():
    """Regression test asserts content before exit code (CLAUDE.md:101)."""
    test_file = Path(REGRESSION_TEST)
    assert test_file.exists(), "Regression test file missing"
    lines = test_file.read_text().splitlines()
    exit_lines = [i for i, l in enumerate(lines) if re.search(r"expect\s*\(\s*exitCode\s*\)", l)]
    content_lines = [i for i, l in enumerate(lines) if re.search(r"expect\s*\(\s*std(?:out|err)\s*\)", l)]
    assert exit_lines, "No exit code assertions found"
    assert content_lines, "No content assertions found"
    for ec in exit_lines:
        assert any(ca < ec for ca in content_lines), "exit code before content assertion"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_banned_words():
    """Repo banned words check passes (CI check from package.json scripts.banned)."""
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Banned words check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_glob_sources():
    """Repo glob-sources script passes (CI check from package.json scripts.glob-sources)."""
    r = subprocess.run(
        ["bun", "run", "glob-sources"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Glob sources failed:\n{r.stderr[-500:]}"
    # Verify output contains expected "Globbed" message
    assert "Globbed" in r.stdout, f"Expected 'Globbed' in output, got:\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Repo Prettier formatting check passes on package.json."""
    r = subprocess.run(
        ["bunx", "--bun", "prettier@latest", "--check", "package.json"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Prettier exits 0 if files are formatted correctly
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """Repo package.json is valid JSON and parseable by bun."""
    r = subprocess.run(
        ["bun", "-e", "const d = JSON.parse(require('fs').readFileSync('package.json', 'utf8')); console.log('name:', d.name, 'version:', d.version)"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"package.json validation failed:\n{r.stderr[-500:]}"
    assert "name: bun" in r.stdout and "version:" in r.stdout, "package.json not properly parsed"


# [repo_tests] pass_to_pass
def test_repo_tsconfig_valid():
    """Repo tsconfig.json is valid JSON and parseable by node."""
    r = subprocess.run(
        ["node", "-e", "const d = JSON.parse(require('fs').readFileSync('tsconfig.json', 'utf8')); console.log('compilerOptions:', !!d.compilerOptions)"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"tsconfig.json validation failed:\n{r.stderr[-500:]}"
    assert "compilerOptions: true" in r.stdout, "tsconfig.json not properly parsed"


# [repo_tests] pass_to_pass
def test_repo_harness_imports():
    """Test harness imports resolve correctly (bun:test and harness)."""
    r = subprocess.run(
        ["bun", "-e", "import('bun:test').then(m => console.log('bun:test ok')); import('./test/harness.ts').then(m => console.log('harness ok')).catch(e => console.log('harness not needed'))"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Harness imports check failed:\n{r.stderr[-500:]}"
    assert "bun:test ok" in r.stdout, "bun:test import failed"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — File structure and content checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass - uses Path.read_text() not subprocess
def test_repo_source_files_valid():
    """Modified source files exist and have valid content structure."""
    # Verify install_with_manager.zig exists and has substantial content
    iwm_file = Path(IWM)
    assert iwm_file.exists(), "install_with_manager.zig not found"
    iwm_lines = len(iwm_file.read_text().splitlines())
    assert iwm_lines > 200, f"install_with_manager.zig has only {iwm_lines} lines (expected > 200)"

    # Verify security_scanner.zig exists and has substantial content
    ss_file = Path(SS)
    assert ss_file.exists(), "security_scanner.zig not found"
    ss_lines = len(ss_file.read_text().splitlines())
    assert ss_lines > 50, f"security_scanner.zig has only {ss_lines} lines (expected > 50)"


# [static] pass_to_pass - uses Path.read_text() not subprocess
def test_repo_zig_files_valid():
    """Zig source files have valid structure with expected keywords."""
    # Check install_with_manager.zig for basic syntax validity
    iwm_content = Path(IWM).read_text()
    assert "pub fn" in iwm_content or "const" in iwm_content, "install_with_manager.zig doesn't look like valid Zig"
    assert "installWithManager" in iwm_content, "install_with_manager.zig missing expected function"

    # Check security_scanner.zig for basic syntax validity
    ss_content = Path(SS).read_text()
    assert "pub fn" in ss_content or "const" in ss_content, "security_scanner.zig doesn't look like valid Zig"
    assert "performSecurityScanAfterResolution" in ss_content, "security_scanner.zig missing expected function"


# [static] pass_to_pass - file existence check, should pass even if not found on base
def test_repo_typescript_check():
    """TypeScript regression test location is valid (file may not exist on base commit)."""
    rt_file = Path(REGRESSION_TEST)
    if rt_file.exists():
        content = rt_file.read_text()
        assert "import" in content, "No imports in regression test"
        assert "test(" in content or "describe(" in content, "No test definitions found"
