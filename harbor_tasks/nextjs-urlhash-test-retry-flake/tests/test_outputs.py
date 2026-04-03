"""
Task: nextjs-urlhash-test-retry-flake
Repo: vercel/next.js @ 78f73b27069ffe2dc1ddfb2b16013220d2a86569
PR:   #91649

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flaky_click_chains_removed():
    """Flaky .click().text()/.eval() chains are broken apart.

    The buggy code chains .click() with .text() or .eval() in a single
    expression, causing race conditions. A correct fix separates
    click from read and wraps the read in retry/polling.
    Also requires >=10 expect() calls remain (not just deleted).
    """
    src = _read_stripped()
    chains = re.findall(
        r"\.click\(\)(?:\s*\.\w+\([^)]*\))*\s*\.(?:text|eval)\s*\(",
        src,
        re.DOTALL,
    )
    assert len(chains) < 3, (
        f"{len(chains)} flaky click-to-read chains remain (expected <3)"
    )
    expect_count = len(re.findall(r"\bexpect\s*\(", src))
    assert expect_count >= 10, (
        f"Only {expect_count} expect() calls remain (expected >=10)"
    )


# [pr_diff] fail_to_pass
def test_retry_wraps_browser_assertions():
    """retry/polling wrappers surround browser assertions.

    The buggy code has 0 retry/polling wrappers. A correct fix wraps flaky
    browser assertions in retry(), toPass(), waitFor(), etc.
    Counts only retry/polling calls that have browser.* within a 5-line
    window to prevent keyword-stuffing.
    """
    src = _read_stripped()
    lines = src.split("\n")
    retry_pat = re.compile(
        r"(?:\bretry\s*\(|\.\s*toPass\s*\(|\bwaitFor\s*\(|\bwaitForFunction\s*\(|\bpoll\s*\()"
    )
    browser_pat = re.compile(r"\bbrowser\b\s*\.")
    count = 0
    for i, line in enumerate(lines):
        if retry_pat.search(line):
            window = lines[max(0, i - 1) : i + 6]
            if any(browser_pat.search(l) for l in window):
                count += 1
    assert count >= 5, (
        f"Only {count} retry/polling blocks wrap browser assertions (expected >=5)"
    )


# [pr_diff] fail_to_pass
def test_retry_mechanism_imported():
    """A retry/polling mechanism is imported or defined.

    The buggy code has no retry utility. A correct fix must import or
    define one (retry, waitFor, toPass, waitForFunction, etc.).
    """
    src = _read_stripped()
    checks = [
        re.search(r"import\s*\{[^}]*\bretry\b", src),
        re.search(r"import\s*\{[^}]*\bwaitFor\b", src),
        re.search(r"(?:const|let|var|function)\s+retry\b", src),
        re.search(r"\.toPass\s*\(", src),
        re.search(r"\bwaitForFunction\s*\(", src),
        re.search(r"require\s*\([^)]*\)\.retry\b", src),
    ]
    assert any(checks), "No retry/polling mechanism found (import or definition)"


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
    # Detect the anti-pattern: nextTestSetup with an inline object as `files`
    # i.e. files: { or files:{ (with optional whitespace)
    assert not re.search(
        r"nextTestSetup\s*\(\s*\{[^}]*\bfiles\s*:\s*\{",
        src,
        re.DOTALL,
    ), "nextTestSetup uses inline files object — should use files: __dirname instead"


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
