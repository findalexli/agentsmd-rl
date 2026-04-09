"""
Task: workers-sdk-c3-expect-param-injection
Repo: workers-sdk @ f23c455ca2f762f0067ed0bfc810209ee3ab8323
PR:   13245

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/workers-sdk"
C3 = f"{REPO}/packages/create-cloudflare"

FRAMEWORK_HELPERS = f"{C3}/e2e/helpers/framework-helpers.ts"
WORKERS_HELPERS = f"{C3}/e2e/helpers/workers-helpers.ts"
TO_EXIST = f"{C3}/e2e/helpers/to-exist.ts"
MOCKS = f"{C3}/src/helpers/__tests__/mocks.ts"
FRAMEWORKS_TEST = f"{C3}/e2e/tests/frameworks/frameworks.test.ts"
WORKERS_TEST = f"{C3}/e2e/tests/workers/workers.test.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — eslint-disable comment cleanup
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_eslint_disable_comments_resolved():
    """Bare eslint-disable-next-line no-restricted-imports comments are removed or justified."""
    # These 3 files should have NO eslint-disable-next-line no-restricted-imports at all
    for filepath in [FRAMEWORK_HELPERS, WORKERS_HELPERS, MOCKS]:
        content = Path(filepath).read_text()
        matches = re.findall(r"//\s*eslint-disable-next-line\s+no-restricted-imports", content)
        assert len(matches) == 0, (
            f"{Path(filepath).name} still has {len(matches)} bare eslint-disable comment(s)"
        )

    # to-exist.ts should KEEP the comment but with a justification (-- reason)
    to_exist_content = Path(TO_EXIST).read_text()
    justified = re.findall(
        r"//\s*eslint-disable-next-line\s+no-restricted-imports\s+--\s+\S",
        to_exist_content,
    )
    assert len(justified) >= 1, (
        "to-exist.ts eslint-disable comment is missing or lacks justification (-- reason)"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — expect dependency injection
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_helpers_accept_expect_param():
    """E2E helper functions accept expect as an injected parameter instead of importing it."""
    # framework-helpers.ts: 8 exported async functions should accept expect param
    fw_content = Path(FRAMEWORK_HELPERS).read_text()

    fw_functions = [
        "runC3ForFrameworkTest",
        "verifyDeployment",
        "verifyDevScript",
        "verifyPreviewScript",
        "verifyTypes",
        "verifyCloudflareVitePluginConfigured",
        "testGitCommitMessage",
        "testDeploymentCommitMessage",
    ]

    for fn_name in fw_functions:
        # Find the function declaration and check its parameters include expect
        pattern = rf"(?:export\s+)?(?:async\s+)?function\s+{fn_name}\s*\("
        match = re.search(pattern, fw_content)
        assert match, f"Function {fn_name} not found in framework-helpers.ts"
        # Get the text from function start through next ~200 chars to see params
        snippet = fw_content[match.start():match.start() + 300]
        assert re.search(r"\bexpect\b", snippet), (
            f"{fn_name} in framework-helpers.ts does not accept an 'expect' parameter"
        )

    # workers-helpers.ts: 2 exported async functions should accept expect param
    wk_content = Path(WORKERS_HELPERS).read_text()

    wk_functions = ["runC3ForWorkerTest", "verifyLocalDev"]

    for fn_name in wk_functions:
        pattern = rf"(?:export\s+)?(?:async\s+)?function\s+{fn_name}\s*\("
        match = re.search(pattern, wk_content)
        assert match, f"Function {fn_name} not found in workers-helpers.ts"
        snippet = wk_content[match.start():match.start() + 300]
        assert re.search(r"\bexpect\b", snippet), (
            f"{fn_name} in workers-helpers.ts does not accept an 'expect' parameter"
        )


# [pr_diff] fail_to_pass
def test_mocks_throw_error():
    """mocks.ts uses throw new Error() instead of expect.fail() for validation checks."""
    # Use node subprocess to parse and verify the file
    script = r"""
    const fs = require('fs');
    const content = fs.readFileSync('%s', 'utf8');
    const expectFailCount = (content.match(/expect\.fail\s*\(/g) || []).length;
    const throwErrorCount = (content.match(/throw new Error\s*\(/g) || []).length;
    const result = { expectFailCount, throwErrorCount };
    console.log(JSON.stringify(result));
    if (expectFailCount > 0) {
        console.error('mocks.ts still uses expect.fail() — should use throw new Error()');
        process.exit(1);
    }
    if (throwErrorCount < 3) {
        console.error('Expected at least 3 throw new Error() calls, found ' + throwErrorCount);
        process.exit(1);
    }
    """ % MOCKS

    r = subprocess.run(["node", "-e", script], capture_output=True, timeout=10)
    assert r.returncode == 0, (
        f"mocks.ts validation failed:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    )


# [pr_diff] fail_to_pass
def test_call_sites_pass_expect():
    """Test files pass expect as an argument to refactored helper functions."""
    # Check frameworks.test.ts passes expect to helper calls
    fw_test = Path(FRAMEWORKS_TEST).read_text()

    # runC3ForFrameworkTest should be called with expect as first arg
    # Pattern: await runC3ForFrameworkTest(\n\t+expect,
    assert re.search(
        r"runC3ForFrameworkTest\s*\(\s*\n?\s*expect\b", fw_test
    ), "frameworks.test.ts does not pass expect to runC3ForFrameworkTest"

    assert re.search(
        r"verifyDeployment\s*\(\s*\n?\s*expect\b", fw_test
    ), "frameworks.test.ts does not pass expect to verifyDeployment"

    assert re.search(
        r"verifyDevScript\s*\(\s*\n?\s*expect\b", fw_test
    ), "frameworks.test.ts does not pass expect to verifyDevScript"

    # Check workers.test.ts passes expect to helper calls
    wk_test = Path(WORKERS_TEST).read_text()

    assert re.search(
        r"runC3ForWorkerTest\s*\(\s*\n?\s*expect\b", wk_test
    ), "workers.test.ts does not pass expect to runC3ForWorkerTest"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — AGENTS.md type-only import rule
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:91 @ f23c455ca2f762f0067ed0bfc810209ee3ab8323
def test_type_only_vitest_import():
    """Helper files use type-only imports for vitest types per AGENTS.md consistent-type-imports rule."""
    for filepath in [FRAMEWORK_HELPERS, WORKERS_HELPERS]:
        content = Path(filepath).read_text()
        fname = Path(filepath).name

        # Should NOT have a value import of expect from vitest
        value_import = re.search(
            r'^import\s+\{[^}]*\bexpect\b[^}]*\}\s+from\s+["\']vitest["\']',
            content,
            re.MULTILINE,
        )
        assert value_import is None, (
            f"{fname} still has a value import of 'expect' from vitest — "
            "should use import type or receive expect as parameter"
        )

        # Should have a type-only import from vitest (ExpectStatic or similar)
        type_import = re.search(
            r'^import\s+type\s+\{[^}]+\}\s+from\s+["\']vitest["\']',
            content,
            re.MULTILINE,
        )
        assert type_import is not None, (
            f"{fname} is missing a type-only import from vitest for the expect parameter type"
        )

    # mocks.ts should not import expect from vitest at all
    mocks_content = Path(MOCKS).read_text()
    expect_import = re.search(
        r'^import\s+\{[^}]*\bexpect\b[^}]*\}\s+from\s+["\']vitest["\']',
        mocks_content,
        re.MULTILINE,
    )
    assert expect_import is None, (
        "mocks.ts still imports 'expect' from vitest — should only import { vi }"
    )
