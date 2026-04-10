"""
Task: nextjs-instant-navs-devtools-deflake
Repo: vercel/next.js @ 60e71ac90c4f150982fda3ca937b1b0e4c9a7b29
PR:   vercel/next.js#91912

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
TEST_FILE = (
    f"{REPO}/test/development/app-dir/instant-navs-devtools/"
    "instant-navs-devtools.test.ts"
)


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _read_test_file() -> str:
    return Path(TEST_FILE).read_text()


def _extract_function(src: str, name: str) -> str:
    """Extract body of async function <name>(...) (top-level in describe)."""
    pattern = rf"async function {name}\b[^{{]*\{{(.*?)\n  \}}"
    m = re.search(pattern, src, re.DOTALL)
    return m.group(1) if m else ""


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_click_start_no_instant_selector():
    """clickStartClientNav must not use elementByCssInstant for the client button."""
    r = _run_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{TEST_FILE}', 'utf8');

// Extract clickStartClientNav function body
const regex = /async function clickStartClientNav\\b[^{{]*\\{{([\\s\\S]*?)\\n  \}}/;
const m = regex.exec(src);
if (!m) {{
    console.error('clickStartClientNav function not found');
    process.exit(1);
}}

const body = m[1];
if (body.includes('elementByCssInstant')) {{
    console.error('clickStartClientNav still uses elementByCssInstant');
    process.exit(1);
}}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_click_start_uses_bounded_wait():
    """clickStartClientNav should use elementByCss with an explicit timeout option."""
    r = _run_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{TEST_FILE}', 'utf8');

// Extract clickStartClientNav function body
const regex = /async function clickStartClientNav\\b[^{{]*\\{{([\\s\\S]*?)\\n  \}}/;
const m = regex.exec(src);
if (!m) {{
    console.error('clickStartClientNav function not found');
    process.exit(1);
}}

const body = m[1];

// Must use elementByCss (not elementByCssInstant) with a timeout option
const hasElementByCss = body.includes('elementByCss(');
const hasTimeout = /timeout\\s*:/.test(body);

// Also accept waitForElementByCss or retry as alternatives
const hasWaitFor = body.includes('waitForElementByCss');
const hasRetry = /retry\\(/.test(body);

if (!hasElementByCss && !hasWaitFor && !hasRetry) {{
    console.error('No bounded wait mechanism found (elementByCss/waitFor/retry)');
    process.exit(1);
}}

if (hasElementByCss && !hasTimeout) {{
    console.error('elementByCss found but missing timeout option');
    process.exit(1);
}}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + structural integrity
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_click_target_selector_preserved():
    """The click target must still be [data-instant-nav-client]."""
    src = _read_test_file()
    body = _extract_function(src, "clickStartClientNav")
    assert body, "clickStartClientNav function not found"
    assert "data-instant-nav-client" in body, (
        "clickStartClientNav must target the [data-instant-nav-client] element"
    )


# [static] pass_to_pass
def test_cookie_wait_after_click():
    """waitForInstantModeCookie must still be called in clickStartClientNav."""
    src = _read_test_file()
    body = _extract_function(src, "clickStartClientNav")
    assert body, "clickStartClientNav function not found"
    assert "waitForInstantModeCookie" in body, (
        "clickStartClientNav must call waitForInstantModeCookie after the click"
    )


# [static] pass_to_pass
def test_panel_helpers_preserved():
    """Other instant-nav helper functions must still exist and not be broken."""
    src = _read_test_file()
    for helper in [
        "openInstantNavPanel",
        "clickInstantNavMenuItem",
        "getInstantNavPanelText",
        "closePanelViaHeader",
    ]:
        assert f"function {helper}" in src, f"Helper function {helper} is missing"


# [static] pass_to_pass
def test_file_structure_intact():
    """File must retain describe block and at least 3 it() test cases."""
    src = _read_test_file()
    assert "describe(" in src, "Missing describe block"
    # Match it( with word boundary
    it_count = len(re.findall(r"\bit\(", src))
    assert it_count >= 3, f"Expected >= 3 test cases, found {it_count}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:194 @ 60e71ac
def test_no_deprecated_check_usage():
    """Do NOT use check() — it is deprecated (AGENTS.md:194)."""
    src = _read_test_file()
    matches = re.findall(r"\bcheck\s*\(", src)
    assert len(matches) == 0, (
        f"Found {len(matches)} deprecated check() call(s) — "
        "use retry() + expect() instead per AGENTS.md:194"
    )


# [agent_config] pass_to_pass — AGENTS.md:180 @ 60e71ac
def test_no_settimeout_for_waiting():
    """Do not use setTimeout for waiting — use retry() instead (AGENTS.md:180)."""
    src = _read_test_file()
    body = _extract_function(src, "clickStartClientNav")
    assert body, "clickStartClientNav function not found"
    assert "setTimeout" not in body, (
        "clickStartClientNav uses setTimeout for waiting — "
        "use retry() from next-test-utils instead per AGENTS.md:180"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD tests (pass_to_pass) — verify fix doesn't break existing functionality
# ---------------------------------------------------------------------------


def _run_pnpm_install():
    """Install pnpm and dependencies if needed."""
    # Check if pnpm is available
    r = subprocess.run(["which", "pnpm"], capture_output=True, text=True)
    if r.returncode != 0:
        # Install pnpm
        subprocess.run(
            ["npm", "install", "-g", "pnpm@9.6.0"],
            capture_output=True, text=True, timeout=120
        )
    # Check if node_modules exists
    if not Path(f"{REPO}/node_modules").exists():
        subprocess.run(
            ["pnpm", "install"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Repo's Prettier formatting check passes on the test file (pass_to_pass)."""
    _run_pnpm_install()
    r = subprocess.run(
        ["pnpm", "prettier", "--check", TEST_FILE],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint():
    """Repo's ESLint check passes on the test file (pass_to_pass)."""
    _run_pnpm_install()
    r = subprocess.run(
        ["pnpm", "lint-eslint", TEST_FILE],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
