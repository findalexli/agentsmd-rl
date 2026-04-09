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
        if ch == '{':
            depth += 1
        elif ch == '}':
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

// Find the rosetta detection: must have all three conditions combined
const ifMarker = "process.platform === 'darwin' && process.arch === 'x64' && os.cpus().some";
const ifIdx = src.indexOf(ifMarker);
if (ifIdx === -1) {
  console.error('Combined Rosetta detection condition not found');
  process.exit(1);
}

// Walk back to the opening paren of `if (`
let ifStart = ifIdx;
while (ifStart > 0 && src[ifStart] !== '(') ifStart--;
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
    for line in src.split('\n'):
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
        if 'Apple Silicon' in msg and 'performance' in msg.lower():
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

const ifMarker = "process.platform === 'darwin' && process.arch === 'x64' && os.cpus().some";
const ifIdx = src.indexOf(ifMarker);
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

const ifMarker = "process.platform === 'darwin' && process.arch === 'x64' && os.cpus().some";
const ifIdx = src.indexOf(ifMarker);
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
