"""
Task: bun-puppeteer-macos-headless-shell
Repo: oven-sh/bun @ 5693fc1a98116743f16a7db2952d6e436bf9ec98
PR:   28200

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/test/integration/next-pages/test/dev-server-puppeteer.ts"


def _src():
    return Path(TARGET).read_text()


def _code_lines(src):
    """Strip comment-only lines to avoid matching commented-out code."""
    return "\n".join(
        l
        for l in src.splitlines()
        if not re.match(r"^\s*//", l) and not re.match(r"^\s*\*", l)
    )


def _run_node(code: str, timeout: int = 30, install_deps: list[str] | None = None) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js."""
    # Install dependencies if needed
    if install_deps:
        pkg_dir = Path("/tmp/node_deps")
        pkg_dir.mkdir(parents=True, exist_ok=True)
        # Check if already installed
        if not (pkg_dir / "node_modules").exists():
            deps_str = " ".join(install_deps)
            subprocess.run(
                f"cd {pkg_dir} && npm install {deps_str}",
                shell=True,
                capture_output=True,
            )

    script = Path("/tmp/_eval_tmp.cjs")
    script.write_text(code)
    try:
        env = os.environ.copy()
        # Add node_modules path if we installed deps
        if install_deps:
            pkg_dir = Path("/tmp/node_deps")
            node_path = str(pkg_dir / "node_modules")
            env["NODE_PATH"] = node_path
        return subprocess.run(
            ["node", str(script)],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral fixes
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_macos_headless_shell_mode():
    """On macOS, headless mode must use 'shell' (not boolean true) to avoid Gatekeeper."""
    src = _src()

    # Verify isMacOS variable exists
    assert re.search(r"const\s+isMacOS\s*=", src), "No isMacOS variable defined"

    # Extract the headless expression from the launch options
    headless_m = re.search(r"headless\s*:\s*(.+?),", src)
    assert headless_m, "No headless config found in launchOptions"
    headless_expr = headless_m.group(1).strip()

    # Evaluate on macOS — must produce "shell"
    r = _run_node(
        f"""
const isMacOS = true;
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
const isMacOS = false;
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
    """On macOS with shell mode, executablePath must not be set."""
    src = _src()

    # Extract the spread expression containing executablePath
    spread_m = re.search(r"\.\.\.\(([^)]*executablePath[^)]*)\)", src)
    assert spread_m, "No executablePath spread expression found"
    spread_expr = spread_m.group(1).strip()

    # On macOS with a browser path: executablePath should NOT be set
    r = _run_node(
        f"""
const isMacOS = true;
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
const isMacOS = false;
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
    """Launch timeout and protocolTimeout must be finite (>0), not 0/infinite."""
    src = _src()
    code = _code_lines(src)

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
    """Retry delay between browser launch attempts must be > 1000ms."""
    src = _src()
    code = _code_lines(src)

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
    """Downloaded browser binaries in Puppeteer cache must be chmod'd executable."""
    code = _code_lines(_src())

    # Extract the actual execSync chmod commands from the source, create a temp
    # directory with non-executable dummy binaries, run the commands, and verify
    # the binaries become executable.
    r = _run_node(
        f"""
const fs = require('fs');
const path = require('path');
const os = require('os');
const {{ execSync }} = require('child_process');

const src = {json.dumps(code)};

// Extract execSync calls containing chmod from backtick template strings
const chmodRegex = /execSync\\(\\s*`([^`]*chmod[^`]*)`/g;
const cmds = [];
let m;
while ((m = chmodRegex.exec(src)) !== null) cmds.push(m[1]);

if (cmds.length === 0) {{
    console.error('No execSync chmod commands found in source');
    process.exit(1);
}}

// Verify commands target key browser binaries
if (!cmds.some(c => c.includes('chrome-headless-shell'))) {{
    console.error('No chmod targeting chrome-headless-shell');
    process.exit(1);
}}
if (!cmds.some(c => c.includes('chrome') && !c.includes('headless'))) {{
    console.error('No chmod targeting chrome binary');
    process.exit(1);
}}

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
    const resolved = cmd.replace(/\\$\\{{[^}}]+\\}}/g, tmpDir);
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
    src = _src()
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
    src = _src()
    for arg in ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]:
        assert arg in src, f"Core launch arg missing: {arg}"


# [pr_diff] pass_to_pass
def test_puppeteer_launch_with_options():
    """File must have Puppeteer import and launch() call with headless + args config."""
    src = _src()
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
    code = _code_lines(_src())
    assert "xattr" in code, "xattr call missing from macOS quarantine workaround"
    assert "quarantine" in code, "com.apple.quarantine removal missing"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_typescript_syntax():
    """TypeScript file must have valid syntax (repo CI check)."""
    src = _src()

    # Use TypeScript parser to validate syntax
    r = _run_node(
        f"""
const parser = require("@typescript-eslint/typescript-estree");
const src = {json.dumps(src)};
try {{
  parser.parse(src, {{ range: false, loc: false }});
  console.log("PASS");
}} catch (e) {{
  console.error("Syntax error:", e.message);
  process.exit(1);
}}
""",
        timeout=60,
        install_deps=["@typescript-eslint/typescript-estree@8.30.1"],
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
    # Exit code 0 = success (warnings don't cause non-zero exit)
    # Exit code 1 = errors found
    assert r.returncode == 0, f"oxlint failed with errors:\\n{r.stderr[-500:]}"


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
noComments = noComments.replace(/([}\\]"0-9])\\s*\\/\\/.*$/gm, '$1');
// Strip multi-line comments
noComments = noComments.replace(/\\/\\*[\\s\\S]*?\\*\\//g, '');
// Parse as JSON
JSON.parse(noComments);
console.log('PASS');
"""
    )
    assert r.returncode == 0, f"oxlint.json is not valid JSONC: {r.stderr}"
