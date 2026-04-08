"""
Task: nextjs-urlhash-test-retry-flake
Repo: vercel/next.js @ 78f73b27069ffe2dc1ddfb2b16013220d2a86569
PR:   #91649

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/next.js"
TEST_FILE = Path(REPO) / "test/development/pages-dir/client-navigation/url-hash.test.ts"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_comments(src: str) -> str:
    """Remove // and /* */ comments from TypeScript, preserving string literals."""
    result = []
    i = 0
    in_single = False
    in_double = False
    in_template = False
    while i < len(src):
        c = src[i]
        if not in_single and not in_double and not in_template:
            if c == "/" and i + 1 < len(src) and src[i + 1] == "/":
                while i < len(src) and src[i] != "\n":
                    i += 1
                continue
            elif c == "/" and i + 1 < len(src) and src[i + 1] == "*":
                i += 2
                while i + 1 < len(src) and not (src[i] == "*" and src[i + 1] == "/"):
                    i += 1
                i += 2
                continue
            elif c == '"' and (i == 0 or src[i - 1] != "\\"):
                in_double = True
            elif c == "'" and (i == 0 or src[i - 1] != "\\"):
                in_single = True
            elif c == "`":
                in_template = True
        elif in_double and c == '"' and src[i - 1] != "\\":
            in_double = False
        elif in_single and c == "'" and src[i - 1] != "\\":
            in_single = False
        elif in_template and c == "`" and src[i - 1] != "\\":
            in_template = False
        result.append(c)
        i += 1
    return "".join(result)


def _read_stripped() -> str:
    """Read the test file with comments stripped."""
    return _strip_comments(TEST_FILE.read_text())


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — file exists and has balanced syntax
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Test file exists and has balanced braces/parens."""
    assert TEST_FILE.exists(), f"{TEST_FILE} missing"
    src = TEST_FILE.read_text()
    depth = 0
    for c in src:
        if c in "{(":
            depth += 1
        elif c in "})":
            depth -= 1
        assert depth >= 0, "Unbalanced braces/parens (depth went negative)"
    assert depth == 0, f"Unbalanced braces/parens (final depth={depth})"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_retry_mechanism_imported():
    """A retry/polling mechanism is imported or defined.

    The base commit has no retry utility. The fix must import or define one
    (retry, waitFor, toPass, waitForFunction, etc.).
    """
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync(
  'test/development/pages-dir/client-navigation/url-hash.test.ts', 'utf8'
);
const stripped = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
const checks = [
  /import\s*\{[^}]*\bretry\b/.test(stripped),
  /import\s*\{[^}]*\bwaitFor\b/.test(stripped),
  /(?:const|let|var|function)\s+retry\b/.test(stripped),
  /\.toPass\s*\(/.test(stripped),
  /\bwaitForFunction\s*\(/.test(stripped),
  /require\s*\([^)]*\)\.retry\b/.test(stripped),
];
if (!checks.some(Boolean)) {
  console.error('No retry/polling mechanism found');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Node check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_flaky_click_chains_removed():
    """Flaky .click().text()/.eval() chains are broken apart.

    The buggy code chains .click() with .text() or .eval() in a single
    expression, causing race conditions. A correct fix separates
    click from read and wraps the read in retry/polling.
    Also requires >=10 expect() calls remain (not just deleted).
    """
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync(
  'test/development/pages-dir/client-navigation/url-hash.test.ts', 'utf8'
);
const stripped = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
const chainPattern = /\.click\(\)(?:\s*\.\w+\([^)]*\))*\s*\.(?:text|eval)\s*\(/g;
const chains = stripped.match(chainPattern) || [];
if (chains.length >= 3) {
  console.error('Too many flaky click-to-read chains: ' + chains.length);
  process.exit(1);
}
const expectMatches = stripped.match(/\bexpect\s*\(/g) || [];
if (expectMatches.length < 10) {
  console.error('Too few expect() calls: ' + expectMatches.length);
  process.exit(1);
}
console.log('PASS chains=' + chains.length + ' expects=' + expectMatches.length);
""")
    assert r.returncode == 0, f"Node check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_retry_wraps_browser_assertions():
    """retry/polling wrappers surround browser assertions (>=5 with proximity check).

    The base code has 0 retry/polling wrappers. The fix adds retry() around
    browser assertions. Counts retry/polling calls that have browser.* within
    a 5-line window to prevent keyword-stuffing.
    """
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync(
  'test/development/pages-dir/client-navigation/url-hash.test.ts', 'utf8'
);
const stripped = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
const lines = stripped.split('\n');
const retryPat = /(?:\bretry\s*\(|\.\s*toPass\s*\(|\bwaitFor\s*\(|\bwaitForFunction\s*\(|\bpoll\s*\()/;
const browserPat = /\bbrowser\b\s*\./;
let count = 0;
for (let i = 0; i < lines.length; i++) {
  if (retryPat.test(lines[i])) {
    const window = lines.slice(Math.max(0, i - 1), i + 6);
    if (window.some(l => browserPat.test(l))) {
      count++;
    }
  }
}
if (count < 5) {
  console.error('Only ' + count + ' retry/polling blocks wrap browser assertions');
  process.exit(1);
}
console.log('PASS count=' + count);
""")
    assert r.returncode == 0, f"Node check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_names_preserved():
    """Existing describe blocks and test names are preserved."""
    src = TEST_FILE.read_text()
    required = [
        "Client navigation with URL hash",
        "when hash changes",
        "should not run getInitialProps",
        "should scroll to the specified position",
        "should not scroll to hash when scroll={false}",
        "Should update asPath",
        "when hash changes with state",
        "should increment the history state counter",
        "should increment the shallow history state counter",
    ]
    missing = [name for name in required if name not in src]
    assert not missing, f"Missing test names/blocks: {missing}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """File has substantial content: >=150 lines, >=10 it() blocks,
    >=10 expect() calls, >=15 browser.* references."""
    src = _read_stripped()
    lines = [l for l in src.split("\n") if l.strip()]
    line_count = len(lines)
    it_count = len(re.findall(r"\bit\s*\(", src))
    expect_count = len(re.findall(r"\bexpect\s*\(", src))
    browser_count = len(re.findall(r"\bbrowser\s*\.", src))

    failures = []
    if line_count < 150:
        failures.append(f"only {line_count} non-blank lines (expected >=150)")
    if it_count < 10:
        failures.append(f"only {it_count} it() blocks (expected >=10)")
    if expect_count < 10:
        failures.append(f"only {expect_count} expect() calls (expected >=10)")
    if browser_count < 15:
        failures.append(f"only {browser_count} browser.* refs (expected >=15)")
    assert not failures, "; ".join(failures)


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:194 @ 78f73b27069ffe2dc1ddfb2b16013220d2a86569
def test_no_deprecated_check():
    """No deprecated check() usage — must use retry() + expect() instead."""
    src = _read_stripped()
    assert not re.search(r"\bawait\s+check\s*\(", src), (
        "File uses deprecated check() — should use retry() + expect()"
    )


# [agent_config] pass_to_pass — AGENTS.md:207-221 @ 78f73b27069ffe2dc1ddfb2b16013220d2a86569
def test_no_inline_files_object():
    """nextTestSetup uses a real fixture directory, not inline file object literals.

    AGENTS.md prefers `files: __dirname` over `files: { 'path': 'content' }`.
    Inline file objects are harder to maintain and the existing test follows
    the real-directory pattern — a correct fix must not regress this.
    """
    src = TEST_FILE.read_text()
    assert not re.search(
        r"nextTestSetup\s*\(\s*\{[^}]*\bfiles\s*:\s*\{",
        src,
        re.DOTALL,
    ), "nextTestSetup uses inline files object — should use file: __dirname instead"


# [agent_config] pass_to_pass — AGENTS.md:180 @ 78f73b27069ffe2dc1ddfb2b16013220d2a86569
def test_no_settimeout_waiting():
    """No setTimeout-based waiting — must use retry() instead."""
    src = _read_stripped()
    assert not re.search(r"new\s+Promise.*setTimeout", src, re.DOTALL), (
        "File uses setTimeout for waiting — should use retry()"
    )
    assert not re.search(
        r"await\s+new\s+Promise\s*\(\s*(?:resolve|r)\s*=>\s*setTimeout", src, re.DOTALL
    ), "File uses setTimeout-based sleep — should use retry()"
