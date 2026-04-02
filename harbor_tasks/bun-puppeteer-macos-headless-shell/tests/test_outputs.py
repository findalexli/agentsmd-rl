"""
Task: bun-puppeteer-macos-headless-shell
Repo: oven-sh/bun @ 5693fc1a98116743f16a7db2952d6e436bf9ec98
PR:   28200

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/test/integration/next-pages/test/dev-server-puppeteer.ts"


def _src():
    return Path(TARGET).read_text()


def _code_src(src):
    """Strip comment-only lines to avoid matching commented-out code."""
    lines = [l for l in src.splitlines()
             if not re.match(r'^\s*//', l) and not re.match(r'^\s*\*', l)]
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral fixes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_macos_headless_shell_mode():
    """On macOS, headless mode must use 'shell' (not boolean true) to avoid Gatekeeper."""
    src = _src()
    # Base has: headless: true,
    # Fix has:  headless: isMacOS ? "shell" : true,
    assert re.search(r'''headless\s*:.*['"]shell['"]''', src), \
        "headless does not include 'shell' for macOS (expected: isMacOS ? \"shell\" : true)"
    # Must be conditional — not always "shell" (which would break non-macOS)
    headless_m = re.search(r'headless\s*:\s*(.+)', _code_src(src))
    assert headless_m, "No headless config line found"
    headless_val = headless_m.group(1)
    assert re.search(r'isMacOS|darwin|platform|\?', headless_val), \
        f"headless value is not platform-conditional: {headless_val.strip()}"


# [pr_diff] fail_to_pass
def test_executable_path_excluded_on_macos():
    """On macOS with shell mode, executablePath must not be set (would point to full Chrome)."""
    src = _src()
    # Base:  ...(browserPath ? { executablePath: browserPath } : {})  — no macOS guard
    # Fix:   ...(!isMacOS && browserPath ? { executablePath: browserPath } : {})

    # Find the spread expression that includes executablePath
    ep_spread = re.search(r'\.\.\.\(([^)]*executablePath[^)]*)\)', src, re.DOTALL)
    if ep_spread:
        expr = ep_spread.group(1)
        assert re.search(r'!isMacOS|!.*darwin|platform\s*!==?\s*[\'"]darwin', expr), \
            f"executablePath spread not guarded for macOS (found: {expr.strip()})"
    else:
        # executablePath might be in a different form — verify any usage is guarded
        ep_lines = [l for l in src.splitlines()
                    if 'executablePath' in l and not re.match(r'^\s*//', l)]
        assert ep_lines, "No executablePath usage found in file"
        for line in ep_lines:
            assert re.search(r'!isMacOS|!.*darwin|isLinux|platform\s*!==?\s*[\'"]darwin', line), \
                f"executablePath not guarded for macOS on line: {line.strip()}"


# [pr_diff] fail_to_pass
def test_finite_timeouts():
    """Launch timeout and protocolTimeout must be finite (>0), not 0/infinite."""
    src = _src()
    code = _code_src(src)

    # Check timeout: field (not protocolTimeout — use word boundary)
    timeout_m = re.search(r'\btimeout\s*:\s*(\d[\d_]*)', code)
    assert timeout_m, "No 'timeout:' field found in launch options"
    timeout_val = int(timeout_m.group(1).replace('_', ''))
    assert timeout_val > 0, f"timeout is {timeout_val} (must be > 0, not infinite)"

    # Check protocolTimeout: field
    proto_m = re.search(r'protocolTimeout\s*:\s*(\d[\d_]*)', code)
    assert proto_m, "No 'protocolTimeout:' field found in launch options"
    proto_val = int(proto_m.group(1).replace('_', ''))
    assert proto_val > 0, f"protocolTimeout is {proto_val} (must be > 0, not infinite)"


# [pr_diff] fail_to_pass
def test_retry_delay_increased():
    """Retry delay between browser launch attempts must be > 1000ms."""
    src = _src()
    code = _code_src(src)

    # setTimeout is in the catch/retry block — find the last catch and look after it
    catch_idx = code.rfind('catch')
    assert catch_idx != -1, "No catch block found in retry logic"
    retry_src = code[catch_idx:]

    m = re.search(r'setTimeout\s*\(\s*\w+\s*,\s*(\d[\d_]*)\s*\)', retry_src)
    assert m, "No setTimeout call found in retry/catch block"
    delay_ms = int(m.group(1).replace('_', ''))
    assert delay_ms > 1000, \
        f"retry delay is {delay_ms}ms (must be > 1000ms for transient macOS launch issues)"


# [pr_diff] fail_to_pass
def test_chmod_cached_binaries():
    """Downloaded browser binaries in Puppeteer cache must be chmod'd executable."""
    code = _code_src(_src())
    assert 'chmod' in code, \
        "No chmod call to make cached browser binaries executable"
    binary_names = ['chrome-headless-shell', 'chrome', 'Chrome for Testing', 'chromium']
    assert any(name.lower() in code.lower() for name in binary_names), \
        "chmod present but doesn't target a browser binary (chrome/chrome-headless-shell/chromium)"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_retry_loop_preserved():
    """Browser retry loop (for + catch + launch) must still exist."""
    src = _src()
    has_loop = bool(re.search(r'for\s*\(.*attempt', src) or
                    re.search(r'while\s*\(.*attempt', src) or
                    re.search(r'retry|attempts?\s*[<>=]', src, re.I))
    assert has_loop, "Retry loop (for/while with attempt counter) is missing"
    assert 'catch' in src, "catch block missing from retry logic"
    assert 'launch' in src, "launch() call missing"


# [pr_diff] pass_to_pass
def test_core_launch_args_preserved():
    """Core Puppeteer launch args (--no-sandbox etc.) must be preserved."""
    src = _src()
    for arg in ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']:
        assert arg in src, f"Core launch arg missing: {arg}"


# [pr_diff] pass_to_pass
def test_puppeteer_launch_with_options():
    """File must have Puppeteer import and launch() call with headless + args config."""
    src = _src()
    has_import = bool(re.search(r'require\s*\(\s*[\'"]puppeteer[\'"]', src) or
                      re.search(r'from\s+[\'"]puppeteer[\'"]', src))
    assert has_import, "Puppeteer import missing"
    assert re.search(r'launch\s*\(\s*(?:launchOptions|\{)', src), \
        "launch() call with options object missing"
    assert 'headless' in src and re.search(r'args\s*:\s*\[', src), \
        "launchOptions missing headless or args fields"


# [pr_diff] pass_to_pass
def test_xattr_quarantine_removal():
    """xattr quarantine removal for macOS Gatekeeper must be preserved."""
    code = _code_src(_src())
    assert 'xattr' in code, "xattr call missing from macOS quarantine workaround"
    assert 'quarantine' in code, "com.apple.quarantine removal missing"
