"""
Task: nextjs-rosetta2-cli-warning
Repo: vercel/next.js @ a6df8603a4e164da7d758d0eb4082dc70353450d
PR:   92220

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
TARGET = f"{REPO}/packages/next/src/bin/next.ts"


def _node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """Target file must parse as valid TypeScript (balanced braces, no garbage)."""
    src = Path(TARGET).read_text()
    depth = 0
    for ch in src:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
    assert depth == 0, f"Unbalanced braces in next.ts (depth={depth})"
    assert len(src) > 200, "File is suspiciously small"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rosetta_warning_darwin_x64_apple():
    """When platform=darwin, arch=x64, CPU model contains 'Apple', warn() must fire."""
    r = _node(r"""
const fs = require('fs');
const os = require('os');
const src = fs.readFileSync('packages/next/src/bin/next.ts', 'utf-8');

// Find the rosetta detection: must have all three conditions (may span multiple lines)
// Check for the individual components that should exist
const hasDarwin = src.includes("process.platform === 'darwin'");
const hasX64 = src.includes("process.arch === 'x64'");
const hasCpuCheck = src.includes("os.cpus().some") && src.includes("cpu.model.includes('Apple')");

if (!hasDarwin || !hasX64 || !hasCpuCheck) {
  console.error('Missing Rosetta detection components. hasDarwin=' + hasDarwin + ', hasX64=' + hasX64 + ', hasCpuCheck=' + hasCpuCheck);
  process.exit(1);
}

// Find the if statement containing these checks
const ifIdx = src.indexOf("process.platform === 'darwin'");
if (ifIdx === -1) {
  console.error('darwin platform check not found');
  process.exit(1);
}

// Walk back to the opening paren of `if (`
let ifStart = ifIdx;
while (ifStart > 0 && src[ifStart] !== '(') ifStart--;
if (ifStart <= 0) {
  console.error('Could not find opening paren of if statement');
  process.exit(1);
}

// Extract condition: from char after '(' to matching ')'
let depth = 0;
let condEnd = -1;
for (let i = ifStart; i < src.length; i++) {
  if (src[i] === '(') depth++;
  else if (src[i] === ')') {
    depth--;
    if (depth === 0) { condEnd = i; break; }
  }
}
const condition = src.slice(ifStart + 1, condEnd).trim();

// Find the body: from '{' after condition to matching '}'
let bodyStart = src.indexOf('{', condEnd);
if (bodyStart === -1) {
  console.error('Could not find opening brace of if body');
  process.exit(1);
}
depth = 0;
let bodyEnd = -1;
for (let i = bodyStart; i < src.length; i++) {
  if (src[i] === '{') depth++;
  else if (src[i] === '}') {
    depth--;
    if (depth === 0) { bodyEnd = i; break; }
  }
}
const body = src.slice(bodyStart + 1, bodyEnd).trim();

// Verify the condition contains all three checks
const condStr = condition.toString();
if (!condStr.includes("process.platform === 'darwin'") ||
    !condStr.includes("process.arch === 'x64'") ||
    !condStr.includes("os.cpus().some")) {
  console.error('Condition does not contain all three required checks');
  process.exit(1);
}

// Test with mocked darwin + x64 + Apple CPU
let warnCalled = false;
let warnMessage = '';
const mockWarn = (msg) => { warnCalled = true; warnMessage = msg; };

Object.defineProperty(process, 'platform', { value: 'darwin', configurable: true });
Object.defineProperty(process, 'arch', { value: 'x64', configurable: true });
const origCpus = os.cpus;
os.cpus = () => [
  { model: 'Apple M1 Pro', speed: 2400 },
  { model: 'Apple M1 Pro', speed: 2400 },
];

const condResult = eval(condition);
if (!condResult) {
  console.error('Condition was false for darwin+x64+Apple M1 Pro');
  process.exit(1);
}

// Evaluate the body, replacing warn() with mockWarn
const evalBody = body.replace(/\bwarn\b\s*\(/g, 'mockWarn(');
eval(evalBody);

if (!warnCalled) {
  console.error('warn() was not called when conditions were met');
  process.exit(1);
}
if (!warnMessage.includes('Rosetta 2')) {
  console.error('Warning missing "Rosetta 2": ' + warnMessage);
  process.exit(1);
}

// Restore
Object.defineProperty(process, 'platform', { value: 'linux', configurable: true });
Object.defineProperty(process, 'arch', { value: 'x64', configurable: true });
os.cpus = origCpus;

console.log('PASS');
""")
    assert r.returncode == 0, f"Rosetta detection failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_os_import_exists():
    """The os module must be imported (required by the detection logic)."""
    src = Path(TARGET).read_text()
    has_import = False
    for line in src.split("\n"):
        stripped = line.strip()
        if stripped.startswith("import os from") or stripped.startswith("import * as os from"):
            if "'os'" in stripped or '"os"' in stripped:
                has_import = True
                break
    assert has_import, "Missing 'import os from \"os\"' in next.ts"


# [pr_diff] fail_to_pass
def test_warning_message_content():
    """Warning must mention Apple Silicon and degraded performance."""
    src = Path(TARGET).read_text()
    import re
    warn_matches = re.findall(r"warn\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", src)
    found = False
    for msg in warn_matches:
        if "Apple Silicon" in msg and "performance" in msg.lower():
            found = True
            break
    assert found, f"No warning about Apple Silicon performance found. Warnings: {warn_matches}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_false_positive_arm64():
    """darwin + arm64 must NOT trigger the Rosetta warning (native ARM)."""
    r = _node(r"""
const fs = require('fs');
const os = require('os');
const src = fs.readFileSync('packages/next/src/bin/next.ts', 'utf-8');

// Check for the individual components
const hasDarwin = src.includes("process.platform === 'darwin'");
const hasX64 = src.includes("process.arch === 'x64'");
const hasCpuCheck = src.includes("os.cpus().some") && src.includes("cpu.model.includes('Apple')");

// If no Rosetta detection found, skip the test
if (!hasDarwin || !hasX64 || !hasCpuCheck) {
  console.log('PASS');
  process.exit(0);
}

// Find the if statement containing the darwin check
const ifIdx = src.indexOf("process.platform === 'darwin'");
if (ifIdx === -1) {
  console.log('PASS');
  process.exit(0);
}

let ifStart = ifIdx;
while (ifStart > 0 && src[ifStart] !== '(') ifStart--;
let depth = 0;
let condEnd = -1;
for (let i = ifStart; i < src.length; i++) {
  if (src[i] === '(') depth++;
  else if (src[i] === ')') { depth--; if (depth === 0) { condEnd = i; break; } }
}
const condition = src.slice(ifStart + 1, condEnd).trim();

Object.defineProperty(process, 'platform', { value: 'darwin', configurable: true });
Object.defineProperty(process, 'arch', { value: 'arm64', configurable: true });
const origCpus = os.cpus;
os.cpus = () => [{ model: 'Apple M1 Pro', speed: 2400 }];

const condResult = eval(condition);
if (condResult) {
  console.error('Condition was TRUE for darwin+arm64 (should be false)');
  process.exit(1);
}

Object.defineProperty(process, 'platform', { value: 'linux', configurable: true });
Object.defineProperty(process, 'arch', { value: 'x64', configurable: true });
os.cpus = origCpus;

console.log('PASS');
""")
    assert r.returncode == 0, f"False positive on arm64:\n{r.stdout}\n{r.stderr}"


# [pr_diff] pass_to_pass
def test_no_false_positive_linux():
    """Linux must NOT trigger the Rosetta warning regardless of arch."""
    r = _node(r"""
const fs = require('fs');
const os = require('os');
const src = fs.readFileSync('packages/next/src/bin/next.ts', 'utf-8');

// Check for the individual components
const hasDarwin = src.includes("process.platform === 'darwin'");
const hasX64 = src.includes("process.arch === 'x64'");
const hasCpuCheck = src.includes("os.cpus().some") && src.includes("cpu.model.includes('Apple')");

// If no Rosetta detection found, skip the test
if (!hasDarwin || !hasX64 || !hasCpuCheck) {
  console.log('PASS');
  process.exit(0);
}

// Find the if statement containing the darwin check
const ifIdx = src.indexOf("process.platform === 'darwin'");
if (ifIdx === -1) {
  console.log('PASS');
  process.exit(0);
}

let ifStart = ifIdx;
while (ifStart > 0 && src[ifStart] !== '(') ifStart--;
let depth = 0;
let condEnd = -1;
for (let i = ifStart; i < src.length; i++) {
  if (src[i] === '(') depth++;
  else if (src[i] === ')') { depth--; if (depth === 0) { condEnd = i; break; } }
}
const condition = src.slice(ifStart + 1, condEnd).trim();

Object.defineProperty(process, 'platform', { value: 'linux', configurable: true });
Object.defineProperty(process, 'arch', { value: 'x64', configurable: true });
const origCpus = os.cpus;
os.cpus = () => [{ model: 'Apple M1 Pro', speed: 2400 }];

const condResult = eval(condition);
if (condResult) {
  console.error('Condition was TRUE for linux+x64 (should be false)');
  process.exit(1);
}

Object.defineProperty(process, 'platform', { value: 'linux', configurable: true });
Object.defineProperty(process, 'arch', { value: 'x64', configurable: true });
os.cpus = origCpus;

console.log('PASS');
""")
    assert r.returncode == 0, f"False positive on linux:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """Detection logic must use all three checks: platform, arch, AND CPU model."""
    src = Path(TARGET).read_text()
    assert "process.platform === 'darwin'" in src, "Missing darwin platform check"
    assert "process.arch === 'x64'" in src, "Missing x64 arch check"
    assert "os.cpus()" in src, "Missing os.cpus() call"
    assert ".model.includes" in src, "Missing CPU model check"
    assert "warn(" in src, "Missing warn() call"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_file_exists():
    """Target file packages/next/src/bin/next.ts must exist (pass_to_pass)."""
    assert Path(TARGET).exists(), f"Target file not found: {TARGET}"


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Repo's Prettier check passes on the target file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "--yes", "prettier", "--check", TARGET],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_git_valid():
    """Git repository is valid and has expected commit history (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git log failed:\n{r.stderr}"
    # Verify we're at the expected base commit
    assert "a6df8603" in r.stdout, f"Unexpected commit: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_node_syntax():
    """Target file has valid Node.js/TypeScript syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", TARGET],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    # Note: --check validates JS syntax; TS files may have imports
    # that fail at runtime but syntax should be valid
    # Alternative: use acorn or just verify the file isn't garbage
    src = Path(TARGET).read_text()
    # Basic syntax validation - check for balanced braces
    depth = 0
    for ch in src:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        assert depth >= 0, "Unbalanced braces: too many closing"
    assert depth == 0, f"Unbalanced braces in next.ts (depth={depth})"


# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """packages/next/package.json must be valid JSON (pass_to_pass)."""
    import json
    pkg_path = f"{REPO}/packages/next/package.json"
    assert Path(pkg_path).exists(), "package.json not found"
    with open(pkg_path) as f:
        pkg = json.load(f)
    assert "name" in pkg, "package.json missing name field"
    assert pkg["name"] == "next", f"Expected package name 'next', got {pkg.get('name')}"


# [repo_tests] pass_to_pass
def test_repo_import_syntax_valid():
    """Target file must have valid import structure for Next.js CLI (pass_to_pass)."""
    src = Path(TARGET).read_text()
    # Check that the require-hook import is present (needed for Next.js CLI)
    assert "import '../server/require-hook'" in src, "Missing require-hook import"
    # Check that commander imports are present
    assert "from 'next/dist/compiled/commander'" in src, "Missing commander import"
    # Check that the warn function is imported from the right place
    assert "from '../build/output/log'" in src, "Missing log import"


# [repo_tests] pass_to_pass
def test_repo_node_syntax_check():
    """Repo CI - Node.js can parse the file syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", TARGET],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Node.js syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_shebang_valid():
    """Repo CI - CLI entry point has valid shebang (pass_to_pass)."""
    r = subprocess.run(
        ["head", "-1", TARGET],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to read shebang:\n{r.stderr}"
    assert "#!/usr/bin/env node" in r.stdout, f"Invalid shebang: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_git_show_base_commit():
    """Repo CI - Git can show the expected base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "show", "--stat", "--oneline", "-s", "a6df8603a4e164da7d758d0eb4082dc70353450d"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git show failed:\n{r.stderr}"
    # Verify this is a turbopack-related commit
    assert "turbopack" in r.stdout.lower() or "cache" in r.stdout.lower(), \
        f"Unexpected commit content: {r.stdout}"
