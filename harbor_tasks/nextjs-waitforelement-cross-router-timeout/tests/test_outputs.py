"""
Task: nextjs-waitforelement-cross-router-timeout
Repo: vercel/next.js @ ad65b1bdcf3d10e5213c80bea56a73038bbf1c99
PR:   #91918

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
TEST_FILE = f"{REPO}/test/e2e/app-dir/interoperability-with-pages/navigation.test.ts"


def _read_test_file() -> str:
    return Path(TEST_FILE).read_text()


def _code_lines(src: str) -> list[str]:
    """Return non-comment lines from the source."""
    out = []
    for line in src.splitlines():
        t = line.strip()
        if t.startswith("//") or t.startswith("*") or t.startswith("/*"):
            continue
        out.append(line)
    return out


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Test file must parse without TypeScript syntax errors."""
    r = subprocess.run(
        ["node", "-e", f"require('fs').readFileSync('{TEST_FILE}', 'utf8')"],
        capture_output=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Cannot read test file: {r.stderr.decode()}"
    src = _read_test_file()
    assert len(src.splitlines()) >= 30, "Test file is too short — likely a stub"


# [static] pass_to_pass
def test_anti_stub_real_waitfor_calls():
    """At least 6 real .waitForElementByCss calls in non-comment code."""
    code_text = "\n".join(_code_lines(_read_test_file()))
    count = len(re.findall(r"\.waitForElementByCss\(", code_text))
    assert count >= 6, f"Only {count}/6 real .waitForElementByCss calls found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_all_waitfor_calls_have_timeout():
    """Every .waitForElementByCss call must have an explicit timeout >= 15000."""
    src = _read_test_file()
    lines = src.splitlines()
    code_lines = []
    for i, line in enumerate(lines):
        t = line.strip()
        if t.startswith("//") or t.startswith("*") or t.startswith("/*"):
            continue
        code_lines.append((i, line))

    call_count = 0
    with_timeout = 0
    failures = []

    for idx, (i, line) in enumerate(code_lines):
        if ".waitForElementByCss(" not in line:
            continue
        call_count += 1

        # Gather context: this line + next 4 original lines (for multiline calls)
        context = "\n".join(lines[i : min(i + 5, len(lines))])

        # Check for inline { timeout: N }
        inline = re.search(
            r"waitForElementByCss\s*\([^)]*,\s*\{[^}]*timeout\s*:", context, re.DOTALL
        )
        # Check for numeric second arg like waitForElementByCss('#sel', 30000)
        numeric_arg = re.search(
            r"waitForElementByCss\s*\(\s*['\"`][^'\"` ]*['\"`]\s*,\s*(\d+)\s*\)",
            context,
        )
        # Check for variable arg defined elsewhere with timeout
        var_match = re.search(
            r"waitForElementByCss\s*\(\s*['\"`][^'\"`]*['\"`]\s*,\s*([a-zA-Z_]\w*)\s*\)",
            context,
        )
        var_timeout = False
        if var_match:
            var_name = var_match.group(1)
            if re.search(rf"{var_name}\s*=\s*\{{[^}}]*timeout\s*:", src, re.DOTALL):
                var_timeout = True

        if inline:
            val_match = re.search(r"timeout\s*:\s*(\d[\d_]*)", context)
            if val_match:
                val = int(val_match.group(1).replace("_", ""))
                if val < 15000:
                    failures.append(f"Line {i + 1}: timeout={val} < 15000")
                    continue
            with_timeout += 1
        elif numeric_arg:
            val = int(numeric_arg.group(1))
            if val < 15000:
                failures.append(f"Line {i + 1}: timeout={val} < 15000")
                continue
            with_timeout += 1
        elif var_timeout:
            with_timeout += 1
        else:
            failures.append(f"Line {i + 1}: no timeout option found")

    assert call_count > 0, "No .waitForElementByCss calls found"
    assert with_timeout == call_count, (
        f"{with_timeout}/{call_count} have timeout. Issues: {'; '.join(failures)}"
    )


# [pr_diff] fail_to_pass
def test_at_least_6_calls_with_timeout():
    """At least 6 waitForElementByCss calls have explicit timeout (covers all cross-router waits)."""
    src = _read_test_file()
    code_text = "\n".join(_code_lines(src))

    # Count calls that have a second argument (timeout)
    # Pattern: .waitForElementByCss('...', <something>)  or  .waitForElementByCss('...', { timeout: ... })
    calls_with_arg = len(
        re.findall(
            r"\.waitForElementByCss\(\s*['\"`#][^)]*,\s*(?:\{|[0-9])", code_text
        )
    )
    assert calls_with_arg >= 6, (
        f"Only {calls_with_arg}/6 waitForElementByCss calls have timeout arg"
    )


# [pr_diff] fail_to_pass
def test_explanatory_comment_present():
    """A comment near waitForElementByCss explaining why timeout is increased."""
    src = _read_test_file()
    lines = src.splitlines()

    for i, line in enumerate(lines):
        t = line.strip()
        if not t.startswith("//"):
            continue
        lower = t.lower()
        # Must mention reason (compilation/CI/on-demand/slow/cross-router/dev)
        if not re.search(
            r"compil|on.?demand|cross.?router|dev.?mode|ci\b|resource|load|slow|flak|build|longer|increas",
            lower,
        ):
            continue
        # Must mention timeout/wait
        if not re.search(r"timeout|wait|time", lower):
            continue
        # Must be within 10 lines of a waitForElementByCss call
        for j in range(max(0, i - 10), min(len(lines), i + 10)):
            if j != i and "waitForElementByCss" in lines[j]:
                return  # PASS
    assert False, "No explanatory comment found near waitForElementByCss about increased timeout"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: test structure preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_all_four_test_cases_present():
    """All 4 navigation test cases (app->pages, pages->app, + back/forward variants) present."""
    src = _read_test_file()
    assert re.search(r"it\s*\(['\"`][^'\"`]*app[^'\"`]*pages", src, re.IGNORECASE), (
        "Missing app->pages test case"
    )
    assert re.search(r"it\s*\(['\"`][^'\"`]*pages[^'\"`]*app", src, re.IGNORECASE), (
        "Missing pages->app test case"
    )
    it_blocks = len(re.findall(r"it\s*\(['\"`]", src))
    assert it_blocks >= 4, f"Only {it_blocks}/4 test cases found"


# [pr_diff] pass_to_pass
def test_infrastructure_intact():
    """Core test infrastructure (describe, webdriver import, createNext) present."""
    code_text = "\n".join(_code_lines(_read_test_file()))
    assert re.search(r"describe\s*\(", code_text), "Missing describe() block"
    assert "webdriver" in code_text and re.search(
        r"import|require", code_text
    ), "Missing webdriver import"
    assert "createNext" in code_text, "Missing createNext call"


# [pr_diff] pass_to_pass
def test_navigation_logic_intact():
    """Navigation actions (click, back, forward) and element checks present."""
    code_text = "\n".join(_code_lines(_read_test_file()))
    assert re.search(r"\.click\s*\(", code_text), "Missing .click() calls"
    assert re.search(r"\.back\s*\(", code_text) or re.search(
        r"\.forward\s*\(", code_text
    ), "Missing .back()/.forward() calls"
    assert re.search(
        r"elementByCss|waitForElementByCss", code_text
    ), "Missing element check calls"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:180 @ ad65b1bdcf3d10e5213c80bea56a73038bbf1c99
def test_no_settimeout_for_waiting():
    """No setTimeout or manual Promise delays used for waiting (use retry/waitFor helpers)."""
    code_lines = _code_lines(_read_test_file())
    for line in code_lines:
        assert not re.search(
            r"setTimeout|new\s+Promise\s*\(\s*\(?\s*resolve\b", line
        ), f"setTimeout/Promise delay found: {line.strip()}"


# [agent_config] pass_to_pass — AGENTS.md:194 @ ad65b1bdcf3d10e5213c80bea56a73038bbf1c99
def test_no_deprecated_check():
    """No deprecated check() usage (use retry() + expect() instead)."""
    code_lines = _code_lines(_read_test_file())
    for line in code_lines:
        assert not re.search(r"(?<!\w)check\s*\(", line), (
            f"Deprecated check() found: {line.strip()}"
        )


# [agent_config] pass_to_pass — AGENTS.md:207-220 @ ad65b1bdcf3d10e5213c80bea56a73038bbf1c99
def test_no_inline_fixture_files():
    """createNext/nextTestSetup must use a real fixture directory, not an inline files object."""
    src = _read_test_file()
    # Inline files object pattern: files: { 'some/path': `...` or '...' }
    assert not re.search(
        r"(?:createNext|nextTestSetup)\s*\(\s*\{[^}]*files\s*:\s*\{",
        src,
        re.DOTALL,
    ), "Inline files object found in createNext/nextTestSetup — use files: __dirname instead"
