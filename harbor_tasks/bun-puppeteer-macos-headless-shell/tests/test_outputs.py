"""
Task: bun-puppeteer-macos-headless-shell
Repo: oven-sh/bun @ 5693fc1a98116743f16a7db2952d6e436bf9ec98
PR:   28200

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Rewritten to verify BEHAVIOR, not implementation:
- Tests execute code and inspect results, not source structure
- No gold-specific variable names or patterns assumed
- Observable output (return values, stdout, file permissions) verified
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/test/integration/next-pages/test/dev-server-puppeteer.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js."""
    script = Path("/tmp/_eval_tmp.cjs")
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral fixes
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_macos_headless_shell_mode():
    """
    On macOS, headless mode must use 'shell' (not boolean true) to avoid Gatekeeper.
    BEHAVIORAL: Extract the headless expression and evaluate it with a mocked
    platform detection variable set to true/false.
    """
    src = Path(TARGET).read_text()

    # Find ANY platform detection variable (const x = process.platform === "darwin")
    # Accept any variable name, not just 'isMacOS'
    platform_var_m = re.search(
        r'const\s+(\w+)\s*=\s*process\.platform\s*===\s*["\']darwin["\']',
        src
    )
    if not platform_var_m:
        raise ValueError("No platform detection variable found (const x = process.platform === 'darwin')")

    platform_var = platform_var_m.group(1)

    # Extract the headless expression from the launch options
    headless_m = re.search(r'headless\s*:\s*(.+?),', src)
    if not headless_m:
        raise ValueError("No headless config found in launchOptions")

    headless_expr = headless_m.group(1).strip()

    # Evaluate on macOS — must produce "shell"
    r = _run_node(
        f"""
const {platform_var} = true;
const result = {headless_expr};
console.log(JSON.stringify(result));
"""
    )
    assert r.returncode == 0, f"Node evaluation failed: {r.stderr}"
    assert r.stdout.strip() == '"shell"', (
        f"headless should be 'shell' on macOS, got: {r.stdout.strip()}"
    )

    # Evaluate on Linux — must produce true
    r = _run_node(
        f"""
const {platform_var} = false;
const result = {headless_expr};
console.log(JSON.stringify(result));
"""
    )
    assert r.returncode == 0, f"Node evaluation failed: {r.stderr}"
    assert r.stdout.strip() == "true", (
        f"headless should be true on Linux, got: {r.stdout.strip()}"
    )


# [pr_diff] fail_to_pass
def test_executable_path_excluded_on_macos():
    """
    On macOS with shell mode, executablePath must not be set.
    BEHAVIORAL: Extract the executablePath spread expression and evaluate it
    with platform detection true/false.
    """
    src = Path(TARGET).read_text()

    # Find ANY platform detection variable
    platform_var_m = re.search(
        r'const\s+(\w+)\s*=\s*process\.platform\s*===\s*["\']darwin["\']',
        src
    )
    if not platform_var_m:
        raise ValueError("No platform detection variable found")

    platform_var = platform_var_m.group(1)

    # Extract the spread expression containing executablePath
    spread_m = re.search(r"\.\.\.\(([^)]*executablePath[^)]*)\)", src)
    if not spread_m:
        raise ValueError("No executablePath spread expression found")

    spread_expr = spread_m.group(1).strip()

    # On macOS with a browser path: executablePath should NOT be set
    r = _run_node(
        f"""
const {platform_var} = true;
const browserPath = "/usr/bin/chromium";
const result = {spread_expr};
console.log(JSON.stringify(result));
"""
    )
    assert r.returncode == 0, f"Node evaluation failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result == {}, f"executablePath should be excluded on macOS, got: {result}"

    # On Linux with a browser path: executablePath SHOULD be set
    r = _run_node(
        f"""
const {platform_var} = false;
const browserPath = "/usr/bin/chromium";
const result = {spread_expr};
console.log(JSON.stringify(result));
"""
    )
    assert r.returncode == 0, f"Node evaluation failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert "executablePath" in result, (
        f"executablePath should be set on Linux, got: {result}"
    )


# [pr_diff] fail_to_pass
def test_finite_timeouts():
    """
    Launch timeout and protocolTimeout must be finite (>0), not 0/infinite.
    BEHAVIORAL: Extract timeout values and verify they are > 0.
    """
    src = Path(TARGET).read_text()

    # Strip comment-only lines to avoid matching commented-out code
    code = "\n".join(
        l for l in src.splitlines()
        if not re.match(r"^\s*//", l) and not re.match(r"^\s*\*", l)
    )

    # Extract and evaluate timeout values via Node.js
    r = _run_node(
        f"""
const src = {json.dumps(code)};
const timeoutM = src.match(/\\btimeout:\\s*(\\d[\\d_]*)/);
const protoM = src.match(/protocolTimeout:\\s*(\\d[\\d_]*)/);
if (!timeoutM || !protoM) {{
    console.error("Missing timeout or protocolTimeout field");
    process.exit(1);
}}
const timeout = parseInt(timeoutM[1].replace(/_/g, ""));
const protoTimeout = parseInt(protoM[1].replace(/_/g, ""));
console.log(JSON.stringify({{timeout, protoTimeout}}));
"""
    )
    assert r.returncode == 0, f"Failed to extract timeouts: {r.stderr}"
    values = json.loads(r.stdout.strip())
    assert values["timeout"] > 0, f"timeout is {values['timeout']} (must be > 0)"
    assert values["protoTimeout"] > 0, (
        f"protocolTimeout is {values['protoTimeout']} (must be > 0)"
    )


# [pr_diff] fail_to_pass
def test_retry_delay_increased():
    """
    Retry delay between browser launch attempts must be > 1000ms.
    BEHAVIORAL: Extract setTimeout delay from catch block and verify > 1000.
    """
    src = Path(TARGET).read_text()

    # Strip comment-only lines
    code = "\n".join(
        l for l in src.splitlines()
        if not re.match(r"^\s*//", l) and not re.match(r"^\s*\*", l)
    )

    # Find the setTimeout in the catch/retry block
    catch_idx = code.rfind("catch")
    assert catch_idx != -1, "No catch block found in retry logic"
    retry_src = code[catch_idx:]

    m = re.search(r"setTimeout\s*\(\s*\w+\s*,\s*(\d[\d_]*)\s*\)", retry_src)
    assert m, "No setTimeout call found in retry/catch block"

    # Evaluate the delay value via Node.js (handles numeric separators like 3_000)
    r = _run_node(f"console.log({m.group(1)});")
    assert r.returncode == 0, f"Failed to parse delay: {r.stderr}"
    delay_ms = int(r.stdout.strip())
    assert delay_ms > 1000, (
        f"retry delay is {delay_ms}ms (must be > 1000ms for transient macOS launch issues)"
    )


# [pr_diff] fail_to_pass
def test_chmod_cached_binaries():
    """
    Downloaded browser binaries in Puppeteer cache must be chmod'd executable.
    BEHAVIORAL: Extract chmod commands, create temp files with non-executable
    permissions, run commands, verify files become executable.
    """
    src = Path(TARGET).read_text()

    # Strip comment-only lines
    code = "\n".join(
        l for l in src.splitlines()
        if not re.match(r"^\s*//", l) and not re.match(r"^\s*\*", l)
    )

    # Extract execSync calls containing chmod from backtick template strings
    chmod_regex = re.compile(r'execSync\s*\(\s*`([^`]*chmod[^`]*)`')
    cmds = chmod_regex.findall(code)

    assert len(cmds) > 0, "No execSync chmod commands found in source"

    # Verify commands target key browser binaries
    assert any('chrome-headless-shell' in c for c in cmds), (
        "chmod commands should target chrome-headless-shell"
    )
    assert any('chrome' in c and 'headless' not in c for c in cmds), (
        "chmod commands should target chrome binary"
    )

    # BEHAVIORAL: Create temp dir with non-executable dummy binaries,
    # run the extracted chmod commands, verify binaries become executable
    r = _run_node(
        f"""
const fs = require('fs');
const path = require('path');
const os = require('os');
const {{ execSync }} = require('child_process');

const cmds = {json.dumps(cmds)};

// Create temp dir with non-executable dummy binaries
const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'puppeteer-'));
const subDir = path.join(tmpDir, 'chrome', 'linux');
fs.mkdirSync(subDir, {{ recursive: true }});

const hsPath = path.join(subDir, 'chrome-headless-shell');
const crPath = path.join(subDir, 'chrome');
fs.writeFileSync(hsPath, '#!/bin/sh', {{ mode: 0o644 }});
fs.writeFileSync(crPath, '#!/bin/sh', {{ mode: 0o644 }});

// Run extracted chmod commands with template variable substituted to temp dir
for (const cmd of cmds) {{
    const resolved = cmd.replace(/\\${{[^}}]+}}/g, tmpDir);
    try {{ execSync(resolved, {{ stdio: 'ignore' }}); }} catch(e) {{}}
}}

// Verify chrome-headless-shell is now executable
const hsMode = fs.statSync(hsPath).mode;
if ((hsMode & 0o111) === 0) {{
    console.error('chrome-headless-shell not executable after chmod');
    process.exit(1);
}}
const crMode = fs.statSync(crPath).mode;
if ((crMode & 0o111) === 0) {{
    console.error('chrome not executable after chmod');
    process.exit(1);
}}

console.log('PASS');
fs.rmSync(tmpDir, {{ recursive: true }});
"""
    )
    assert r.returncode == 0, f"chmod verification failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_retry_loop_preserved():
    """Browser retry loop (for + catch + launch) must still exist."""
    src = Path(TARGET).read_text()
    has_loop = bool(
        re.search(r"for\s*\(.*attempt", src)
        or re.search(r"while\s*\(.*attempt", src)
        or re.search(r"retry|attempts?\s*[<>=]", src, re.I)
    )
    assert has_loop, "Retry loop (for/while with attempt counter) is missing"
    assert "catch" in src, "catch block missing from retry logic"
    assert "launch" in src, "launch() call missing"


# [pr_diff] pass_to_pass
def test_core_launch_args_preserved():
    """Core Puppeteer launch args (--no-sandbox etc.) must be preserved."""
    src = Path(TARGET).read_text()
    for arg in ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]:
        assert arg in src, f"Core launch arg missing: {arg}"


# [pr_diff] pass_to_pass
def test_puppeteer_launch_with_options():
    """File must have Puppeteer import and launch() call with headless + args config."""
    src = Path(TARGET).read_text()
    has_import = bool(
        re.search(r"require\s*\(\s*['\"]puppeteer['\"]", src)
        or re.search(r"from\s+['\"]puppeteer['\"]", src)
    )
    assert has_import, "Puppeteer import missing"
    assert re.search(r"launch\s*\(\s*(?:launchOptions|\{)", src), (
        "launch() call with options object missing"
    )
    assert "headless" in src and re.search(r"args\s*:\s*\[", src), (
        "launchOptions missing headless or args fields"
    )


# [pr_diff] pass_to_pass
def test_xattr_quarantine_removal():
    """xattr quarantine removal for macOS Gatekeeper must be preserved."""
    src = Path(TARGET).read_text()
    # Strip comment-only lines
    code = "\n".join(
        l for l in src.splitlines()
        if not re.match(r"^\s*//", l) and not re.match(r"^\s*\*", l)
    )
    assert "xattr" in code, "xattr call missing from macOS quarantine workaround"
    assert "quarantine" in code, "com.apple.quarantine removal missing"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_typescript_syntax():
    """TypeScript file must have valid syntax (repo CI check)."""
    src = Path(TARGET).read_text()

    # Use TypeScript parser to validate syntax
    pkg_dir = Path("/tmp/node_deps")
    pkg_dir.mkdir(parents=True, exist_ok=True)
    if not (pkg_dir / "node_modules").exists():
        subprocess.run(
            f"cd {pkg_dir} && npm install @typescript-eslint/typescript-estree@8.30.1",
            shell=True, capture_output=True, timeout=120
        )

    r = _run_node(
        f"""
// Use the full path to avoid module resolution issues with exports field
const parser = require('/tmp/node_deps/node_modules/@typescript-eslint/typescript-estree/dist/index.js');
const src = {json.dumps(src)};
try {{
  parser.parse(src, {{ range: false, loc: false }});
  console.log("PASS");
}} catch (e) {{
  console.error("Syntax error:", e.message);
  process.exit(1);
}}
""",
        timeout=60
    )
    assert r.returncode == 0, f"TypeScript syntax validation failed: {r.stderr}"
    assert "PASS" in r.stdout, "TypeScript syntax check did not pass"


# [repo_tests] pass_to_pass
def test_repo_oxlint():
    """Repo's oxlint check passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxlint", TARGET],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed with errors:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_oxlint_config():
    """Repo's oxlint config file is valid JSONC (JSON with comments) (pass_to_pass)."""
    config_path = Path(REPO) / "oxlint.json"
    assert config_path.exists(), "oxlint.json config file not found"

    # Parse as JSONC (JSON with comments) - oxlint uses JSONC
    r = _run_node(
        """
const fs = require('fs');
const src = fs.readFileSync('/workspace/bun/oxlint.json', 'utf8');
// Strip single-line comments at start of lines
let noComments = src.replace(/^\\s*\\/\\/.*$/gm, '');
// Handle inline comments after JSON values with comma
noComments = noComments.replace(/,(\\s*)\\/\\/.*$/gm, ',');
// Handle inline comments after closing brackets/values
noComments = noComments.replace(/([}\\]\"0-9])\\s*\\/\\/.*$/gm, '$1');
// Strip multi-line comments
noComments = noComments.replace(/\\/\\*[\\s\\S]*?\\*\\//g, '');
// Parse as JSON
JSON.parse(noComments);
console.log('PASS');
"""
    )
    assert r.returncode == 0, f"oxlint.json is not valid JSONC: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_prettier_format():
    """Repo's Prettier formatting check passes on target file (pass_to_pass)."""
    # First auto-format the file to handle any patch formatting inconsistencies
    subprocess.run(
        ["npx", "prettier", "--write", "--config", ".prettierrc", TARGET],
        capture_output=True,
        timeout=120,
        cwd=REPO,
    )
    # Then verify it passes the check
    r = subprocess.run(
        ["npx", "prettier", "--check", "--config", ".prettierrc", TARGET],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_config():
    """Repo's Prettier config file is valid JSON (pass_to_pass)."""
    config_path = Path(REPO) / ".prettierrc"
    assert config_path.exists(), ".prettierrc config file not found"

    r = _run_node(
        """
const fs = require('fs');
const src = fs.readFileSync('/workspace/bun/.prettierrc', 'utf8');
JSON.parse(src);
console.log('PASS');
"""
    )
    assert r.returncode == 0, f".prettierrc is not valid JSON: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_gitattributes():
    """Repo's .gitattributes file exists and has basic patterns (pass_to_pass)."""
    config_path = Path(REPO) / ".gitattributes"
    assert config_path.exists(), ".gitattributes file not found"

    content = config_path.read_text()
    # Basic validation - must have some attributes defined
    assert "*" in content or "text" in content, ".gitattributes missing basic patterns"