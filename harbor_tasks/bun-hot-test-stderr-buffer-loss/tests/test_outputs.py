"""
Task: bun-hot-test-stderr-buffer-loss
Repo: oven-sh/bun @ af24e281ebacd6ac77c0f14b4206599cf4ae1c9f
PR:   28202

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral tests verify actual behavior by:
  - Running Node.js scripts that read and analyze the test file's code structure
  - Checking spawn configurations via JavaScript execution
  - Verifying absence of known buggy patterns through code analysis
"""

import re
import subprocess
import os
import tempfile
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/test/cli/hot/hot.test.ts"


def _run_node(script: str, args: list = None, timeout: int = 10) -> subprocess.CompletedProcess:
    """Execute a Node.js script file. Returns the CompletedProcess."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, dir='/tmp') as f:
        f.write(script)
        tmp = f.name
    try:
        cmd = ["node", tmp] + (args or [])
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    finally:
        os.unlink(tmp)


def _read_code() -> str:
    """Read the target file, stripping single-line comments to prevent gaming."""
    lines = Path(TARGET).read_text().splitlines()
    result = []
    in_block = False
    for line in lines:
        s = line.strip()
        if in_block:
            if "*/" in s:
                in_block = False
            continue
        if s.startswith("/*") and "*/" not in s:
            in_block = True
            continue
        if s.startswith("/*") and "*/" in s:
            continue
        if s.startswith("//"):
            continue
        result.append(line)
    return "\n".join(result)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_target_file_exists():
    """Target test file must exist and be non-empty."""
    p = Path(TARGET)
    assert p.exists(), f"{TARGET} does not exist"
    assert p.stat().st_size > 0, f"{TARGET} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_data_loss_pattern_fixed():
    """Buggy `str="" + continue outer` must be removed; remaining lines preserved.

    BEHAVIORAL: A Node.js script reads the test file, extracts the three
    sourcemap test blocks, and verifies that none contain the data-loss
    anti-pattern where the buffer is cleared before jumping to the outer loop.
    """
    r = _run_node(
        "const fs = require('fs');\n"
        "const TARGET = process.argv[2];\n"
        "const code = fs.readFileSync(TARGET, 'utf8');\n"
        "\n"
        "// Extract sourcemap test blocks\n"
        "const blocks = code.split(/(?=it\\s*\\()/);\n"
        "const smBlocks = blocks.filter(b =>\n"
        "    b.includes('sourcemap generation') ||\n"
        "    b.includes('sourcemap loading') ||\n"
        "    b.includes('large files')\n"
        ");\n"
        "\n"
        "if (smBlocks.length < 3) {\n"
        "    console.error('Expected >= 3 sourcemap test blocks, found ' + smBlocks.length);\n"
        "    process.exit(1);\n"
        "}\n"
        "\n"
        "// Check each block for the buggy pattern: str='' followed by continue outer.\n"
        "// This is the root cause of data loss: clearing the buffer and jumping to\n"
        "// the outer loop discards all remaining unprocessed lines from the current chunk.\n"
        "for (const block of smBlocks) {\n"
        "    if (/str\\s*=\\s*[\"'][\"'].*?continue\\s+outer/s.test(block)) {\n"
        "        console.error('BUGGY: str= + continue outer pattern found in sourcemap block');\n"
        "        process.exit(1);\n"
        "    }\n"
        "}\n"
        "\n"
        "console.log('OK: data-loss pattern absent from all sourcemap test blocks');\n",
        [TARGET]
    )
    assert r.returncode == 0, f"Data loss check failed: {r.stderr}"
    assert "OK" in r.stdout, f"Unexpected: {r.stdout}"


def test_trailing_partial_lines_preserved():
    """Trailing partial line from stderr split must be saved for next chunk.

    BEHAVIORAL: A Node.js script reads the test file's sourcemap blocks and
    checks that the stderr line-processing loop does NOT unconditionally clear
    the buffer variable (str = ""), which would discard trailing partial lines.
    Any correct fix -- whether using pop(), slice(), a helper function, or any
    other approach -- avoids this unconditional clearing inside the loop body.
    """
    r = _run_node(
        "const fs = require('fs');\n"
        "const TARGET = process.argv[2];\n"
        "const code = fs.readFileSync(TARGET, 'utf8');\n"
        "\n"
        "// Extract sourcemap test blocks\n"
        "const blocks = code.split(/(?=it\\s*\\()/);\n"
        "const smBlocks = blocks.filter(b =>\n"
        "    b.includes('sourcemap generation') ||\n"
        "    b.includes('sourcemap loading') ||\n"
        "    b.includes('large files')\n"
        ");\n"
        "\n"
        "if (smBlocks.length < 3) {\n"
        "    console.error('Expected >= 3 sourcemap test blocks, found ' + smBlocks.length);\n"
        "    process.exit(1);\n"
        "}\n"
        "\n"
        "// The specific bug: inside a while/for loop that processes lines from a\n"
        "// stderr split, the code does str = '' which discards the trailing partial\n"
        "// line.  A correct fix does NOT clear str to empty inside the loop body.\n"
        "for (const block of smBlocks) {\n"
        "    const lines = block.split('\\n');\n"
        "    let inLineLoop = false;\n"
        "    let braceDepth = 0;\n"
        "    for (const line of lines) {\n"
        "        const trimmed = line.trim();\n"
        "        // Detect entry into a line-processing loop (while/for with shift or line iterator)\n"
        "        if (/^(?:while|for)\\s*\\(/.test(trimmed) &&\n"
        "            (trimmed.includes('.shift') || /\\bit\\b/.test(trimmed))) {\n"
        "            inLineLoop = true;\n"
        "            braceDepth = 0;\n"
        "        }\n"
        "        if (inLineLoop) {\n"
        "            braceDepth += (line.match(/\\{/g) || []).length;\n"
        "            braceDepth -= (line.match(/\\}/g) || []).length;\n"
        "            // Check for unconditional str = '' inside the loop\n"
        "            if (/^\\s*str\\s*=\\s*[\"'][\"']/.test(line)) {\n"
        "                console.error('BUGGY: unconditional str= found inside line-processing loop');\n"
        "                console.error('Line: ' + trimmed);\n"
        "                process.exit(1);\n"
        "            }\n"
        "            if (braceDepth <= 0) inLineLoop = false;\n"
        "        }\n"
        "    }\n"
        "}\n"
        "\n"
        "console.log('OK: no unconditional buffer clearing in line-processing loops');\n",
        [TARGET]
    )
    assert r.returncode == 0, f"Trailing lines check failed: {r.stderr}"
    assert "OK" in r.stdout, f"Unexpected: {r.stdout}"


def test_bundler_no_inherit_pipes():
    """Bundler subprocesses must not use stdout/stderr:'inherit'.

    BEHAVIORAL: A Node.js script reads the test file, finds spawn calls for
    bundler processes (those with --watch), and verifies they do not use
    'inherit' for stdout or stderr.
    """
    r = _run_node(
        "const fs = require('fs');\n"
        "const TARGET = process.argv[2];\n"
        "const code = fs.readFileSync(TARGET, 'utf8');\n"
        "\n"
        "// Split into test blocks and find bundler-related ones\n"
        "const blocks = code.split(/(?=it\\s*\\()/);\n"
        "const bundlerBlocks = blocks.filter(b =>\n"
        "    b.includes('sourcemap loading') || b.includes('large files')\n"
        ");\n"
        "\n"
        "if (bundlerBlocks.length < 2) {\n"
        "    console.error('Expected >= 2 bundler test blocks, found ' + bundlerBlocks.length);\n"
        "    process.exit(1);\n"
        "}\n"
        "\n"
        "const violations = [];\n"
        "for (const block of bundlerBlocks) {\n"
        "    // Find spawn calls with --watch (bundler processes)\n"
        "    const spawnMatches = block.match(/spawn\\s*\\(\\s*\\{[\\s\\S]*?\\}\\s*\\)/g) || [];\n"
        "    for (const spawn of spawnMatches) {\n"
        "        if (spawn.includes('--watch') || spawn.includes('\"watch\"')) {\n"
        "            if (/std(?:out|err)\\s*:\\s*[\"']inherit[\"']/.test(spawn)) {\n"
        "                violations.push(spawn.substring(0, 80));\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "}\n"
        "\n"
        "if (violations.length > 0) {\n"
        "    console.error('INHERIT VIOLATION in bundler spawn:');\n"
        "    violations.forEach(v => console.error('  ' + v));\n"
        "    process.exit(1);\n"
        "}\n"
        "console.log('OK: no bundler spawns use inherit for stdout/stderr');\n",
        [TARGET]
    )
    assert r.returncode == 0, f"Bundler pipe check failed: {r.stderr}"
    assert "OK" in r.stdout, f"Unexpected: {r.stdout}"


def test_early_bundler_exit_detection():
    """Bundler-based tests must detect early bundler exit instead of hanging.

    BEHAVIORAL: A Node.js script reads the test file and verifies that
    bundler test blocks include some mechanism to detect when the bundler
    process exits unexpectedly (e.g., Promise.race, exit handler, abort signal,
    or any other early-exit detection approach).
    """
    r = _run_node(
        "const fs = require('fs');\n"
        "const TARGET = process.argv[2];\n"
        "const code = fs.readFileSync(TARGET, 'utf8');\n"
        "\n"
        "// Split into test blocks and find bundler-related ones\n"
        "const blocks = code.split(/(?=it\\s*\\()/);\n"
        "const bundlerBlocks = blocks.filter(b =>\n"
        "    b.includes('sourcemap loading') || b.includes('large files')\n"
        ");\n"
        "\n"
        "if (bundlerBlocks.length < 2) {\n"
        "    console.error('Expected >= 2 bundler test blocks, found ' + bundlerBlocks.length);\n"
        "    process.exit(1);\n"
        "}\n"
        "\n"
        "const missing = [];\n"
        "for (const block of bundlerBlocks) {\n"
        "    // Accept ANY mechanism that detects early process exit\n"
        "    const hasExitDetection = (\n"
        "        /Promise\\.\\s*(?:race|any|allSettled)\\s*\\(/.test(block) ||\n"
        "        /bundler\\.\\s*exited/.test(block) ||\n"
        "        /\\.on\\s*\\(\\s*[\"'](?:exit|close)[\"']/.test(block) ||\n"
        "        /AbortController/.test(block) ||\n"
        "        /exited\\s*\\.\\s*then\\s*\\(/.test(block) ||\n"
        "        /process\\.\\s*on\\s*\\(\\s*[\"']exit[\"']/.test(block) ||\n"
        "        /await\\s+.*exited/.test(block)\n"
        "    );\n"
        "    if (!hasExitDetection) {\n"
        "        const name = (block.match(/[\"']([^\"']+)[\"']/) || [])[1] || 'unknown';\n"
        "        missing.push(name);\n"
        "    }\n"
        "}\n"
        "\n"
        "if (missing.length > 0) {\n"
        "    console.error('NO EXIT DETECTION in blocks: ' + missing.join(', '));\n"
        "    process.exit(1);\n"
        "}\n"
        "console.log('OK: all bundler tests have early exit detection');\n",
        [TARGET]
    )
    assert r.returncode == 0, f"Exit detection check failed: {r.stderr}"
    assert "OK" in r.stdout, f"Unexpected: {r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static)
# ---------------------------------------------------------------------------

def test_sourcemap_tests_preserved():
    """All three sourcemap hot-reload tests must exist and verify 50 reload cycles."""
    code = _read_code()

    tests = [
        "should work with sourcemap generation",
        "should work with sourcemap loading",
        "should work with sourcemap loading with large files",
    ]
    for t in tests:
        assert t in code, "Test '" + t + "' missing from file"

    reload_checks = len(re.findall(r'(?:toBe|toEqual|===)\s*\(\s*50\s*\)', code))
    assert reload_checks >= 3, (
        "Expected >= 3 reload-count assertions (toBe/toEqual 50), found "
        + str(reload_checks)
    )


def test_not_stub():
    """Modified file must have meaningful code changes, not just comments or trivial edits."""
    diff = subprocess.run(
        ["git", "diff", "HEAD", "--", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, cwd=REPO,
    ).stdout

    added = removed = 0
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:].strip()
            if content and not content.startswith("//") and not content.startswith("/*"):
                added += 1
        elif line.startswith("-") and not line.startswith("---"):
            content = line[1:].strip()
            if content and not content.startswith("//") and not content.startswith("/*"):
                removed += 1

    total_changes = added + removed
    assert total_changes >= 10, (
        "Only " + str(total_changes) + " non-comment lines changed "
        + "- fix should touch ~50+ lines"
    )

    code = Path(TARGET).read_text()
    assert len(code.splitlines()) > 300, "File appears gutted (< 300 lines)"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests)
# ---------------------------------------------------------------------------

def test_repo_format():
    subprocess.run(
        ["npm", "install", "-g", "prettier@3.6.2"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["npx", "prettier", "--check", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, "Prettier format check failed:\n" + r.stdout[-500:] + "\n" + r.stderr[-500:]


def test_repo_oxlint():
    subprocess.run(
        ["npm", "install", "-g", "oxlint"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["npx", "oxlint", "--quiet", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, "oxlint found errors:\n" + r.stdout[-1000:] + "\n" + r.stderr[-500:]


def test_repo_typescript_project():
    subprocess.run(
        ["npm", "install", "-g", "typescript@5.9.2"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/test",
    )
    errors = [line for line in r.stderr.splitlines() if "error TS" in line]
    real_errors = [e for e in errors if "regression/issue/14477" not in e]
    assert len(real_errors) == 0, "TypeScript errors found:\n" + "\n".join(real_errors[:10])


def test_target_typescript_syntax():
    subprocess.run(
        ["npm", "install", "-g", "typescript@5.9.2"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ESNext",
         "--module", "ESNext", "--moduleResolution", "bundler", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    errors = [line for line in r.stderr.splitlines() if "error TS" in line and "hot.test.ts" in line]
    assert len(errors) == 0, "TypeScript syntax errors in target file:\n" + "\n".join(errors[:5])


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

def test_buffer_alloc_convention():
    """Large repetitive strings (>=100 chars) must use Buffer.alloc, not .repeat()."""
    code = _read_code()

    large_repeats = re.findall(
        r'["\'][^"\']*["\']\s*\.\s*repeat\s*\(\s*(\d+)\s*\)', code
    )
    has_large_repeat = any(int(n) >= 100 for n in large_repeats)
    assert not has_large_repeat, (
        "Found .repeat() with large count: "
        + str([n for n in large_repeats if int(n) >= 100])
    )

    has_buffer = bool(re.search(r'Buffer\.\s*alloc\s*\(', code))
    has_uint8 = bool(re.search(r'new\s+Uint8Array\s*\(', code))
    assert has_buffer or has_uint8, (
        "No Buffer.alloc or Uint8Array found for large repetitive strings"
    )
