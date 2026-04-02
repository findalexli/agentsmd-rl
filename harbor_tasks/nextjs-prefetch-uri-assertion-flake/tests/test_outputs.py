"""
Task: nextjs-prefetch-uri-assertion-flake
Repo: vercel/next.js @ 138092696c355fa38ec8409e7f2c6c67c97e4f6b
PR:   #91734

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = Path("/repo")
TARGET = REPO / "test/e2e/app-dir/app-prefetch/prefetching.test.ts"


def _strip_comments(content: str) -> str:
    """Remove JS/TS comments to prevent comment-injection gaming."""
    content = re.sub(r'(?<![:\'"])//[^\n]*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    return content


def _get_target_test_body(content: str) -> str:
    """Get the body of the target test case (from its title to the next test)."""
    m = re.search(
        r'should not unintentionally modify the requested prefetch', content
    )
    assert m, "Target test not found in file"
    return content[m.end():]


def _get_after_click(content: str) -> str:
    """Get the region after click on prefetch-via-link in the target test."""
    rest = _get_target_test_body(content)
    click = re.search(r'prefetch-via-link.*?\.click\(\)', rest, re.DOTALL)
    assert click, "Click on prefetch-via-link not found in target test"
    return rest[click.end():]


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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_accordion_assertion_retried():
    """accordion-to-dashboard assertion must be inside a retry/waitFor/polling
    wrapper after clicking prefetch-via-link."""
    content = _strip_comments(TARGET.read_text())
    after_click = _get_after_click(content)

    acc = re.search(r'accordion-to-dashboard', after_click)
    assert acc, "accordion-to-dashboard assertion not found after click"

    region_before = after_click[:acc.start()]

    # Strategy 1: wrapper function (retry, waitFor, poll, …) still open at
    # the accordion position (brace depth > 0).
    wrapper_patterns = [
        r'\bretry\s*\(', r'\bwaitFor\s*\(', r'\bpoll\s*\(',
        r'\bwaitUntil\s*\(',
    ]
    for pat in wrapper_patterns:
        wm = re.search(pat, region_before)
        if wm:
            depth = 0
            for ch in after_click[wm.start():acc.start()]:
                if ch in '({':
                    depth += 1
                elif ch in ')}':
                    depth -= 1
            if depth > 0:
                return  # pass

    # Strategy 2: polling assertion (waitForSelector, waitForElementByCss, …)
    window = after_click[:acc.end() + 100]
    if re.search(
        r'\b(waitForSelector|waitForElementByCss|waitForElement)\s*\([^)]*accordion-to-dashboard',
        window,
    ):
        return

    # Strategy 3: Playwright locator().waitFor()
    if re.search(r'accordion-to-dashboard[^;]*\.waitFor\s*\(', window):
        return

    raise AssertionError(
        "accordion-to-dashboard assertion not wrapped in retry/waitFor/polling "
        "after click"
    )


# [pr_diff] fail_to_pass
def test_assertion_in_async_callback():
    """The accordion assertion must not be a bare expect at test-body level —
    it must be inside an async callback (retry/waitFor) or a direct wait call."""
    content = _strip_comments(TARGET.read_text())
    after_click = _get_after_click(content)

    acc = re.search(r'accordion-to-dashboard', after_click)
    assert acc, "accordion-to-dashboard not found after click"

    region = after_click[:acc.start()]
    window = after_click[:acc.end() + 100]

    # Strategy 1: async callback (retry/waitFor pattern)
    has_callback = bool(
        re.search(r'(?:async\s*)?\(.*?\)\s*=>\s*\{', region)
    ) or bool(re.search(r'async\s+function\s*\(', region))

    # Strategy 2: direct wait call (waitForElementByCss, waitForSelector, etc.)
    has_direct_wait = bool(re.search(
        r'\b(waitForSelector|waitForElementByCss|waitForElement)\s*\([^)]*accordion-to-dashboard',
        window,
    )) or bool(re.search(r'accordion-to-dashboard[^;]*\.waitFor\s*\(', window))

    assert has_callback or has_direct_wait, (
        "accordion assertion not inside an async callback or direct wait — "
        "should use retry(async () => { ... }), waitForElementByCss, or similar"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_other_tests_intact():
    """Other test cases in the file must not be removed or renamed."""
    content = _strip_comments(TARGET.read_text())

    required = [
        'should show layout eagerly when prefetched with loading one level down',
        'should not have prefetch error for static path',
        'should navigate when prefetch is false',
        'should not re-render error component when triggering a prefetch action',
        'should not fetch again when a static page was prefetched',
    ]
    missing = [t for t in required if t not in content]
    assert not missing, f"Missing test cases: {missing}"


# [pr_diff] pass_to_pass
def test_uri_encoding_preserved():
    """URI encoding test logic (param=with%20space, rscRequests) must be preserved."""
    content = _strip_comments(TARGET.read_text())

    has_uri = 'param=with%20space' in content or (
        'encodeURI' in content and 'param' in content
    )
    has_rsc = 'rscRequests' in content or 'RSC' in content
    assert has_uri and has_rsc, "URI encoding test logic removed"


# [pr_diff] pass_to_pass
def test_navigation_flow_preserved():
    """Test must still click prefetch-via-link and call waitForIdleNetwork."""
    content = _strip_comments(TARGET.read_text())
    assert 'prefetch-via-link' in content, "prefetch-via-link click removed"
    assert 'waitForIdleNetwork' in content, "waitForIdleNetwork call removed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:180 @ 138092696c355fa38ec8409e7f2c6c67c97e4f6b
def test_no_settimeout_in_fix():
    """Fix area must not use setTimeout — use retry()/waitFor() per AGENTS.md:180."""
    content = _strip_comments(TARGET.read_text())
    fix_area = '\n'.join(_get_target_test_body(content).split('\n')[:80])

    assert 'setTimeout' not in fix_area, (
        "setTimeout used in fix area — should use retry()/waitFor() per AGENTS.md"
    )


# [agent_config] pass_to_pass — AGENTS.md:194 @ 138092696c355fa38ec8409e7f2c6c67c97e4f6b
def test_no_deprecated_check():
    """Must not use deprecated check() — use retry() + expect() per AGENTS.md:194."""
    content = _strip_comments(TARGET.read_text())
    fix_area = '\n'.join(_get_target_test_body(content).split('\n')[:80])

    assert not re.search(r'(?<!\w)check\s*\(', fix_area), (
        "Uses deprecated check() — should use retry() + expect() per AGENTS.md"
    )


# [agent_config] pass_to_pass — AGENTS.md:180 @ 138092696c355fa38ec8409e7f2c6c67c97e4f6b
def test_retry_imported_from_next_test_utils():
    """retry() must be imported from next-test-utils, not a custom implementation."""
    content = TARGET.read_text()

    # If retry is used in the fix, it must be imported from next-test-utils
    fix_area = '\n'.join(_get_target_test_body(_strip_comments(content)).split('\n')[:80])
    if 'retry' not in fix_area:
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
