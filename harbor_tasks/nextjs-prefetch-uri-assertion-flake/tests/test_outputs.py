"""
Task: nextjs-prefetch-uri-assertion-flake
Repo: vercel/next.js @ 138092696c355fa38ec8409e7f2c6c67c97e4f6b
PR:   #91734

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/repo")
TARGET = REPO / "test/e2e/app-dir/app-prefetch/prefetching.test.ts"


def _strip_comments(content: str) -> str:
    """Remove JS/TS comments to prevent comment-injection gaming."""
    content = re.sub(r"(?<![:'\"])//[^\n]*", "", content)
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    return content


def _run_node(code: str) -> subprocess.CompletedProcess:
    """Execute a Node.js snippet with TARGET path as argv[1]."""
    return subprocess.run(
        ["node", "-e", code, str(TARGET)],
        capture_output=True,
        text=True,
        timeout=30,
    )


# Node.js helper: strip comments, locate target test, extract region after click
_NODE_FIND_REGION = r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const stripped = content.replace(/(?<![:'"])\/\/[^\n]*/g, '').replace(/\/\*[\s\S]*?\*\//g, '');

const testIdx = stripped.indexOf('should not unintentionally modify the requested prefetch');
if (testIdx === -1) { process.stderr.write('target test not found\n'); process.exit(1); }

const afterTitle = stripped.substring(testIdx);
const clickMatch = afterTitle.match(/prefetch-via-link[\s\S]*?\.click\(\)/);
if (!clickMatch) { process.stderr.write('click not found\n'); process.exit(1); }

const afterClick = afterTitle.substring(clickMatch.index + clickMatch[0].length);
const accIdx = afterClick.indexOf('accordion-to-dashboard');
if (accIdx === -1) { process.stderr.write('accordion assertion not found after click\n'); process.exit(1); }

const beforeAcc = afterClick.substring(0, accIdx);
const window = afterClick.substring(0, accIdx + 200);
"""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists_and_substantial():
    """Target test file must exist and not be a stub."""
    assert TARGET.exists(), f"{TARGET} does not exist"
    lines = TARGET.read_text().splitlines()
    assert len(lines) >= 150, (
        f"File has {len(lines)} lines (expected ~430) — likely a stub"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (subprocess)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_accordion_assertion_retried():
    """accordion-to-dashboard assertion wrapped in retry() after click,
    using hasElementByCss (not hasElementByCssSelector)."""
    r = _run_node(
        _NODE_FIND_REGION
        + r"""
// Must have retry(async wrapping the accordion assertion
if (!/retry\s*\(\s*async/.test(beforeAcc)) {
    process.stderr.write('no retry(async) wrapper before accordion assertion\n');
    process.exit(1);
}

// Must use hasElementByCss, NOT hasElementByCssSelector, near accordion
if (window.includes('hasElementByCssSelector')) {
    process.stderr.write('still uses hasElementByCssSelector — should be hasElementByCss\n');
    process.exit(1);
}
if (!/hasElementByCss\b/.test(window)) {
    process.stderr.write('hasElementByCss not found near accordion assertion\n');
    process.exit(1);
}

console.log('PASS');
"""
    )
    assert r.returncode == 0, f"Node check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_assertion_in_async_callback():
    """accordion assertion inside async callback, not bare expect at test-body level."""
    r = _run_node(
        _NODE_FIND_REGION
        + r"""
// Must have an async callback wrapper: retry(async () => { or similar
const hasAsyncCallback =
    /retry\s*\(\s*async\s*\(\s*\)\s*=>\s*\{/.test(beforeAcc) ||
    /retry\s*\(\s*async\s+function/.test(beforeAcc) ||
    /waitFor\s*\(\s*async/.test(beforeAcc);

// Or a direct wait call wrapping accordion (waitForSelector, etc.)
const hasDirectWait =
    /waitForSelector[\s\S]*accordion-to-dashboard/.test(window) ||
    /waitForElementByCss[\s\S]*accordion-to-dashboard/.test(window);

if (!hasAsyncCallback && !hasDirectWait) {
    process.stderr.write('accordion assertion not inside async callback or direct wait\n');
    process.exit(1);
}

console.log('PASS');
"""
    )
    assert r.returncode == 0, f"Node check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_other_tests_intact():
    """Other test cases in the file must not be removed or renamed."""
    content = _strip_comments(TARGET.read_text())

    required = [
        "should show layout eagerly when prefetched with loading one level down",
        "should not have prefetch error for static path",
        "should navigate when prefetch is false",
        "should not re-render error component when triggering a prefetch action",
        "should not fetch again when a static page was prefetched",
    ]
    missing = [t for t in required if t not in content]
    assert not missing, f"Missing test cases: {missing}"


# [pr_diff] pass_to_pass
def test_uri_encoding_preserved():
    """URI encoding test logic (param=with%20space, rscRequests) must be preserved."""
    content = _strip_comments(TARGET.read_text())

    has_uri = "param=with%20space" in content or (
        "encodeURI" in content and "param" in content
    )
    has_rsc = "rscRequests" in content or "RSC" in content
    assert has_uri and has_rsc, "URI encoding test logic removed"


# [pr_diff] pass_to_pass
def test_navigation_flow_preserved():
    """Test must still click prefetch-via-link and call waitForIdleNetwork."""
    content = _strip_comments(TARGET.read_text())
    assert "prefetch-via-link" in content, "prefetch-via-link click removed"
    assert "waitForIdleNetwork" in content, "waitForIdleNetwork call removed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

def _get_target_test_body(content: str) -> str:
    """Extract the body of the target test case."""
    test_start = content.find("should not unintentionally modify the requested prefetch")
    if test_start == -1:
        return ""
    after_title = content[test_start:]
    # Find the next test case or end of file
    next_test = after_title.find("it(", 1)
    if next_test == -1:
        return after_title
    return after_title[:next_test]


# [agent_config] pass_to_pass — AGENTS.md:180 @ 138092696c355fa38ec8409e7f2c6c67c97e4f6b
def test_no_settimeout_in_fix():
    """Fix area must not use setTimeout — use retry()/waitFor() per AGENTS.md:180."""
    content = _strip_comments(TARGET.read_text())
    fix_area = "\n".join(_get_target_test_body(content).split("\n")[:80])

    assert "setTimeout" not in fix_area, (
        "setTimeout used in fix area — should use retry()/waitFor() per AGENTS.md"
    )


# [agent_config] pass_to_pass — AGENTS.md:194 @ 138092696c355fa38ec8409e7f2c6c67c97e4f6b
def test_no_deprecated_check():
    """Must not use deprecated check() — use retry() + expect() per AGENTS.md:194."""
    content = _strip_comments(TARGET.read_text())
    fix_area = "\n".join(_get_target_test_body(content).split("\n")[:80])

    assert not re.search(r"(?<!\w)check\s*\(", fix_area), (
        "Uses deprecated check() — should use retry() + expect() per AGENTS.md"
    )


# [agent_config] pass_to_pass — AGENTS.md:180 @ 138092696c355fa38ec8409e7f2c6c67c97e4f6b
def test_retry_imported_from_next_test_utils():
    """retry() must be imported from next-test-utils, not a custom implementation."""
    content = TARGET.read_text()

    # If retry is used in the fix, it must be imported from next-test-utils
    fix_area = "\n".join(
        _get_target_test_body(_strip_comments(content)).split("\n")[:80]
    )
    if "retry" not in fix_area:
        return  # not using retry — other tests cover alternative valid patterns

    # Check the file imports retry from next-test-utils
    import_patterns = [
        r"from\s+['\"]next-test-utils['\"].*?\bretry\b",
        r"import\s*\{[^}]*\bretry\b[^}]*\}\s*from\s*['\"]next-test-utils['\"]",
        r"require\s*\(\s*['\"]next-test-utils['\"]\s*\).*?\bretry\b",
    ]
    has_import = any(re.search(p, content, re.DOTALL) for p in import_patterns)
    assert has_import, (
        "retry() used but not imported from 'next-test-utils' — "
        "per AGENTS.md:180, use retry from next-test-utils"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD checks (pass_to_pass) — repo_tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_error_codes():
    """Repo's error code check passes (pnpm check-error-codes)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm check-error-codes"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Error codes check failed:\n{r.stderr[-500:]}"
