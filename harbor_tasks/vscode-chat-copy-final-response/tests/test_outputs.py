"""
Task: vscode-chat-copy-final-response
Repo: microsoft/vscode @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
PR:   306184

Compiles TypeScript once (session-scoped fixture), then runs mocha unit tests
and structural grep checks.  Binary scoring: all pass = 1, any fail = 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import pytest
from pathlib import Path

REPO = Path("/workspace/vscode")
CHATMODEL_SRC = REPO / "src/vs/workbench/contrib/chat/common/model/chatModel.ts"
CHATMODEL_TEST_JS = REPO / "out/vs/workbench/contrib/chat/test/common/model/chatModel.test.js"
COPY_ACTIONS_SRC = REPO / "src/vs/workbench/contrib/chat/browser/actions/chatCopyActions.ts"
LIST_WIDGET_SRC = REPO / "src/vs/workbench/contrib/chat/browser/widget/chatListWidget.ts"


@pytest.fixture(scope="module", autouse=True)
def compile_typescript():
    """Compile TypeScript once before all tests in this module."""
    r = subprocess.run(
        ["npm", "run", "compile"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"TypeScript compilation failed:\n"
        f"{r.stdout.decode()[-3000:]}\n{r.stderr.decode()[-1000:]}"
    )


def _mocha_test(grep: str) -> None:
    """Run mocha with a test-name filter; assert at least one test ran and all passed."""
    r = subprocess.run(
        [
            "npx", "mocha",
            "--require", "./test/unit/node/index.js",
            "--grep", grep,
            str(CHATMODEL_TEST_JS),
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"mocha exited non-zero for '{grep}':\n{output}"
    m = re.search(r"(\d+) passing", output)
    assert m and int(m.group(1)) > 0, (
        f"No tests ran for '{grep}' — test may not exist yet:\n{output}"
    )


# ---------------------------------------------------------------------------
# Structural checks (fail_to_pass, pr_diff)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interface_has_getFinalResponse():
    """IResponse interface declares getFinalResponse(): string."""
    content = CHATMODEL_SRC.read_text()
    assert "getFinalResponse(): string" in content, \
        "IResponse interface is missing getFinalResponse() declaration"


# [pr_diff] fail_to_pass
def test_action_registered():
    """CopyFinalResponseAction is registered in chatCopyActions.ts."""
    content = COPY_ACTIONS_SRC.read_text()
    assert "CopyFinalResponseAction" in content, \
        "CopyFinalResponseAction not found in chatCopyActions.ts"


# [pr_diff] fail_to_pass
def test_context_key_in_overlay():
    """isResponse context key is added to the createOverlay() call in chatListWidget.ts."""
    content = LIST_WIDGET_SRC.read_text()
    assert "ChatContextKeys.isResponse.key, isResponseVM" in content, \
        "isResponse key missing from the context overlay in chatListWidget.ts"


# ---------------------------------------------------------------------------
# Behavioral tests via mocha (fail_to_pass, pr_diff)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_getFinalResponse_returns_last_markdown():
    """getFinalResponse returns last contiguous markdown after a tool call."""
    _mocha_test("getFinalResponse returns last contiguous markdown after tool call")


# [pr_diff] fail_to_pass
def test_getFinalResponse_skips_empty_trailing():
    """getFinalResponse skips trailing empty markdown and tool calls."""
    _mocha_test("getFinalResponse skips trailing empty markdown and tool calls")


# [pr_diff] fail_to_pass
def test_getFinalResponse_includes_inline_refs():
    """getFinalResponse includes inline references in the final block."""
    _mocha_test("getFinalResponse includes inline references in final block")


# [pr_diff] fail_to_pass
def test_getFinalResponse_empty_when_no_markdown():
    """getFinalResponse returns empty string when response has no markdown parts."""
    _mocha_test("getFinalResponse returns empty string when no markdown")


# [pr_diff] fail_to_pass
def test_getFinalResponse_all_markdown_no_tools():
    """getFinalResponse returns all markdown when there are no tool calls."""
    _mocha_test("getFinalResponse returns all markdown when there are no tool calls")


# ---------------------------------------------------------------------------
# Regression (pass_to_pass, repo_tests)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_response_tests_pass():
    """Pre-existing Response test suite still passes after the fix."""
    r = subprocess.run(
        [
            "npx", "mocha",
            "--require", "./test/unit/node/index.js",
            "--grep", "^Response",
            str(CHATMODEL_TEST_JS),
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Response test suite had failures:\n{output}"
    m = re.search(r"(\d+) passing", output)
    assert m and int(m.group(1)) > 0, f"No Response tests found:\n{output}"


# ---------------------------------------------------------------------------
# Agent config checks
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:101 @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
def test_getFinalResponse_has_jsdoc():
    """getFinalResponse method has a JSDoc comment (required by copilot-instructions.md:101)."""
    content = CHATMODEL_SRC.read_text()
    idx = content.find("getFinalResponse(): string {")
    assert idx != -1, "getFinalResponse() implementation not found in chatModel.ts"
    preceding = content[max(0, idx - 600) : idx]
    assert "/**" in preceding, (
        "getFinalResponse() is missing a JSDoc comment (/** ... */) — "
        "required by .github/copilot-instructions.md:101"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:147 @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
def test_no_any_in_getFinalResponse():
    """getFinalResponse body does not use 'any' or 'unknown' types."""
    content = CHATMODEL_SRC.read_text()
    start = content.find("getFinalResponse(): string {")
    assert start != -1, "getFinalResponse() implementation not found in chatModel.ts"
    # Walk to the matching closing brace to extract just the method body.
    depth = 0
    end = start
    for i, ch in enumerate(content[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    body = content[start : end + 1]
    assert ": any" not in body, (
        "getFinalResponse uses ': any' — forbidden by .github/copilot-instructions.md:147"
    )
    assert ": unknown" not in body, (
        "getFinalResponse uses ': unknown' — forbidden by .github/copilot-instructions.md:147"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:108 @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
def test_action_label_title_case():
    """The Copy Final Response action label uses title-case capitalization."""
    content = COPY_ACTIONS_SRC.read_text()
    assert "Copy Final Response" in content, (
        "Action label should be 'Copy Final Response' (title case) — "
        "required by .github/copilot-instructions.md:108"
    )
