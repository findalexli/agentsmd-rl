"""
Task: playwright-feat-pwpausecli-exposes-a-playwrightcli
Repo: microsoft/playwright @ 982b9b279557229b12d049ebd3063da408ba5253
PR:   39408

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_modified_files_exist():
    """Key modified TypeScript source files exist and are non-empty."""
    files = [
        "packages/playwright-core/src/server/utils/network.ts",
        "packages/playwright/src/worker/testInfo.ts",
        "packages/playwright/src/program.ts",
        "packages/playwright/src/cli/daemon/daemon.ts",
        "packages/playwright/src/mcp/test/browserBackend.ts",
        "packages/playwright/src/index.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} does not exist"
        assert p.stat().st_size > 0, f"{f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_decorate_server_exported():
    """decorateServer is exported from network.ts so daemon.ts can import it."""
    src = (Path(REPO) / "packages/playwright-core/src/server/utils/network.ts").read_text()
    # Must be 'export function decorateServer' (not just 'function decorateServer')
    assert re.search(r'\bexport\s+function\s+decorateServer\b', src), \
        "decorateServer must be exported from network.ts"


# [pr_diff] fail_to_pass
def test_finish_callbacks_supports_multiple():
    """_onDidFinishTestFunctionCallbacks uses a Set to support multiple callbacks."""
    src = (Path(REPO) / "packages/playwright/src/worker/testInfo.ts").read_text()
    # The property must be a Set, not a single optional callback
    assert "_onDidFinishTestFunctionCallbacks" in src, \
        "testInfo.ts must have _onDidFinishTestFunctionCallbacks (plural)"
    assert re.search(r'new\s+Set\s*<', src), \
        "_onDidFinishTestFunctionCallbacks must be initialized as a Set"
    # Verify iteration over the set (for...of)
    assert re.search(r'for\s*\(\s*const\s+\w+\s+of\s+this\._onDidFinishTestFunctionCallbacks\s*\)', src), \
        "Must iterate over _onDidFinishTestFunctionCallbacks with for...of"


# [pr_diff] fail_to_pass
def test_pwpause_cli_sets_timeouts():
    """PWPAUSE=cli sets timeout=0 and actionTimeout=5000 in program.ts."""
    src = (Path(REPO) / "packages/playwright/src/program.ts").read_text()
    # Check that PWPAUSE === 'cli' branch exists
    assert re.search(r"process\.env\.PWPAUSE\s*===?\s*['\"]cli['\"]", src), \
        "program.ts must check for PWPAUSE === 'cli'"
    # Check that timeout is set to 0
    assert re.search(r'overrides\.timeout\s*=\s*0', src), \
        "PWPAUSE=cli must set overrides.timeout = 0"
    # Check that actionTimeout is set to a small value (5000)
    assert re.search(r'actionTimeout\s*[:=]\s*5000', src), \
        "PWPAUSE=cli must set actionTimeout = 5000"
    # The old behavior (any truthy PWPAUSE → pause: true) should still exist
    # but only for non-'cli' values (else if branch)
    assert re.search(r'else\s+if\s*\(\s*process\.env\.PWPAUSE\s*\)', src), \
        "Non-cli PWPAUSE values should still set pause = true via else-if"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — SKILL.md and reference doc tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
