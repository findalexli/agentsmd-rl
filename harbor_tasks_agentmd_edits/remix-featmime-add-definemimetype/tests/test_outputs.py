"""
Task: remix-featmime-add-definemimetype
Repo: remix-run/remix @ 9c05f82591c422ffc958bd61deb1b29c181ae225
PR:   10921

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
import tempfile
from pathlib import Path

REPO = "/workspace/remix"


def _run_ts(code: str) -> subprocess.CompletedProcess:
    """Write a TypeScript snippet to a temp file and run it with tsx."""
    fd, path = tempfile.mkstemp(suffix=".ts", dir=REPO)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        return subprocess.run(
            ["tsx", path],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified and new TypeScript files parse without errors."""
    r = _run_ts("""
import { detectMimeType } from './packages/mime/src/index.ts'
import { isCompressibleMimeType } from './packages/mime/src/index.ts'
import { mimeTypeToContentType } from './packages/mime/src/index.ts'
// If defineMimeType exists, import it too
try {
  const mod = await import('./packages/mime/src/index.ts')
  if (typeof mod.defineMimeType === 'function') {
    console.log('defineMimeType found')
  }
} catch (e) {
  // OK if it doesn't exist yet on base
}
console.log('syntax OK')
""")
    assert r.returncode == 0, f"Syntax check failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_registers_custom_extension():
    """defineMimeType registers a custom extension that detectMimeType resolves."""
    r = _run_ts("""
import { defineMimeType, detectMimeType } from './packages/mime/src/index.ts'

defineMimeType({ extensions: 'myformat', mimeType: 'application/x-myformat' })
let result = detectMimeType('myformat')
if (result !== 'application/x-myformat') {
  console.error('bare ext: expected application/x-myformat, got', result)
  process.exit(1)
}

// Also works with filename
result = detectMimeType('file.myformat')
if (result !== 'application/x-myformat') {
  console.error('filename: expected application/x-myformat, got', result)
  process.exit(1)
}

console.log('PASS')
""")
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_overrides_builtin_extension():
    """defineMimeType can override a built-in extension mapping."""
    r = _run_ts("""
import { defineMimeType, detectMimeType } from './packages/mime/src/index.ts'

// .ts is video/mp2t by default
let before = detectMimeType('ts')
if (before !== 'video/mp2t') {
  console.error('expected video/mp2t before override, got', before)
  process.exit(1)
}

defineMimeType({ extensions: 'ts', mimeType: 'text/typescript' })
let after = detectMimeType('ts')
if (after !== 'text/typescript') {
  console.error('expected text/typescript after override, got', after)
  process.exit(1)
}

console.log('PASS')
""")
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_custom_compressible():
    """defineMimeType compressible option affects isCompressibleMimeType."""
    r = _run_ts("""
import { defineMimeType, isCompressibleMimeType } from './packages/mime/src/index.ts'

// application/x-myformat is not compressible by default heuristics
if (isCompressibleMimeType('application/x-myformat')) {
  console.error('should not be compressible by default')
  process.exit(1)
}

defineMimeType({
  extensions: 'myext',
  mimeType: 'application/x-myformat',
  compressible: true,
})

if (!isCompressibleMimeType('application/x-myformat')) {
  console.error('should be compressible after registration')
  process.exit(1)
}

console.log('PASS')
""")
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_custom_charset():
    """defineMimeType charset option affects mimeTypeToContentType."""
    r = _run_ts("""
import { defineMimeType, mimeTypeToContentType } from './packages/mime/src/index.ts'

// application/x-myformat gets no charset by default
let before = mimeTypeToContentType('application/x-myformat')
if (before !== 'application/x-myformat') {
  console.error('expected no charset by default, got', before)
  process.exit(1)
}

defineMimeType({
  extensions: 'myext',
  mimeType: 'application/x-myformat',
  charset: 'utf-8',
})

let after = mimeTypeToContentType('application/x-myformat')
if (after !== 'application/x-myformat; charset=utf-8') {
  console.error('expected charset after registration, got', after)
  process.exit(1)
}

console.log('PASS')
""")
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_multiple_extensions():
    """defineMimeType accepts an array of extensions."""
    r = _run_ts("""
import { defineMimeType, detectMimeType } from './packages/mime/src/index.ts'

defineMimeType({
  extensions: ['fmt1', 'fmt2', 'fmt3'],
  mimeType: 'application/x-multi',
})

for (let ext of ['fmt1', 'fmt2', 'fmt3']) {
  let result = detectMimeType(ext)
  if (result !== 'application/x-multi') {
    console.error('extension', ext, ': expected application/x-multi, got', result)
    process.exit(1)
  }
}

console.log('PASS')
""")
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_detect_mime_type():
    """Existing detectMimeType behavior is preserved (txt -> text/plain)."""
    r = _run_ts("""
import { detectMimeType } from './packages/mime/src/index.ts'

let cases: [string, string | undefined][] = [
  ['txt', 'text/plain'],
  ['.txt', 'text/plain'],
  ['file.txt', 'text/plain'],
  ['json', 'application/json'],
  ['html', 'text/html'],
  ['unknown_xyz', undefined],
]

for (let [input, expected] of cases) {
  let result = detectMimeType(input)
  if (result !== expected) {
    console.error(input, ': expected', expected, ', got', result)
    process.exit(1)
  }
}

console.log('PASS')
""")
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation update checks
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Check that the README documents the new function
    assert "defineMimeType" in content, \
        "README.md should mention defineMimeType"

    # Check it shows the function signature or usage heading
    assert "defineMimeType(" in content or "### `defineMimeType" in content, \
        "README.md should document defineMimeType as an API section"

    # Check it includes a usage example with extensions and mimeType
    content_lower = content.lower()
    assert "extensions" in content_lower and "mimetype" in content_lower, \
        "README.md should show usage with extensions and mimeType options"


# ---------------------------------------------------------------------------
# Agent config (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:44 @ 9c05f82

    # Look for a minor changeset file (this is a new feature for a v0.x package)
    changeset_files = list(changes_dir.glob("minor.*.md"))
    assert len(changeset_files) > 0, \
        "Should have a minor.*.md changeset file in packages/mime/.changes/ for a new feature"

    # Verify the changeset mentions the feature
    found_relevant = False
    for cf in changeset_files:
        text = cf.read_text().lower()
        if "definemimetype" in text or "define" in text and "mime" in text:
            found_relevant = True
            break

    assert found_relevant, \
        "Changeset file should describe the defineMimeType feature"
