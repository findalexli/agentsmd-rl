"""
Task: vscode-chat-copy-final-response
Repo: microsoft/vscode @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
PR:   306184

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: TypeScript repo — tests use structural/regex checks on source files.
# AST-only because: TypeScript cannot be imported or executed in Python
"""

import re
from pathlib import Path

REPO = Path("/workspace/vscode")
CHATMODEL_SRC = REPO / "src/vs/workbench/contrib/chat/common/model/chatModel.ts"
CHATMODEL_TEST = REPO / "src/vs/workbench/contrib/chat/test/common/model/chatModel.test.ts"
COPY_ACTIONS_SRC = REPO / "src/vs/workbench/contrib/chat/browser/actions/chatCopyActions.ts"
LIST_WIDGET_SRC = REPO / "src/vs/workbench/contrib/chat/browser/widget/chatListWidget.ts"
APPROVAL_TEST = REPO / "src/vs/workbench/contrib/chat/test/browser/agentSessions/agentSessionApprovalModel.test.ts"
CONTROLLER_TEST = REPO / "src/vs/workbench/contrib/chat/test/browser/agentSessions/localAgentSessionsController.test.ts"


def _extract_method_body(content: str, method_sig: str, max_chars: int = 3000) -> str:
    """Extract a method body by matching braces from its signature."""
    idx = content.find(method_sig)
    assert idx != -1, f"Method signature '{method_sig}' not found"
    brace_start = content.find("{", idx)
    assert brace_start != -1, f"No opening brace after '{method_sig}'"
    depth = 0
    for i in range(brace_start, min(brace_start + max_chars, len(content))):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                return content[idx : i + 1]
    return content[idx : brace_start + max_chars]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — interface & implementation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interface_has_getFinalResponse():
    """IResponse interface declares getFinalResponse(): string."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = CHATMODEL_SRC.read_text()
    # Must be in the IResponse interface (not just anywhere in the file)
    iface_match = re.search(
        r"export\s+interface\s+IResponse\s*\{(.*?)\n\}",
        content,
        re.DOTALL,
    )
    assert iface_match, "IResponse interface not found in chatModel.ts"
    iface_body = iface_match.group(1)
    assert "getFinalResponse()" in iface_body, (
        "IResponse interface is missing getFinalResponse() declaration"
    )
    assert "string" in iface_body.split("getFinalResponse()")[1].split("\n")[0], (
        "getFinalResponse() should return string"
    )


# [pr_diff] fail_to_pass
def test_getFinalResponse_impl_exists():
    """AbstractResponse/Response class implements getFinalResponse with real logic."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = CHATMODEL_SRC.read_text()
    body = _extract_method_body(content, "getFinalResponse(): string {")
    # Must have meaningful logic, not a stub
    lines = [
        ln.strip()
        for ln in body.splitlines()
        if ln.strip() and not ln.strip().startswith("//") and not ln.strip().startswith("*")
    ]
    assert len(lines) >= 8, (
        f"getFinalResponse implementation has only {len(lines)} non-comment lines — "
        "expected substantial logic for walking backwards through response parts"
    )


# [pr_diff] fail_to_pass
def test_impl_handles_three_part_kinds():
    """getFinalResponse handles markdownContent, markdownVuln, and inlineReference."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = CHATMODEL_SRC.read_text()
    body = _extract_method_body(content, "getFinalResponse(): string {")
    assert "markdownContent" in body, (
        "getFinalResponse must handle 'markdownContent' parts"
    )
    assert "markdownVuln" in body, (
        "getFinalResponse must handle 'markdownVuln' parts"
    )
    assert "inlineReference" in body, (
        "getFinalResponse must handle 'inlineReference' parts"
    )


# [pr_diff] fail_to_pass
def test_impl_reverse_iteration():
    """getFinalResponse walks backwards through parts (reverse iteration)."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = CHATMODEL_SRC.read_text()
    body = _extract_method_body(content, "getFinalResponse(): string {")
    # The algorithm must iterate in reverse — check for decrement or reverse patterns
    has_decrement = "i--" in body or "i -= 1" in body or "--i" in body
    has_reverse = ".reverse()" in body or "reduceRight" in body
    has_length_minus = re.search(r"\.length\s*-\s*1", body)
    assert has_decrement or has_reverse or has_length_minus, (
        "getFinalResponse must walk backwards through response parts — "
        "expected reverse iteration (i--, .reverse(), or similar)"
    )


# [pr_diff] fail_to_pass
def test_impl_skips_empty_content():
    """getFinalResponse skips empty markdown parts."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = CHATMODEL_SRC.read_text()
    body = _extract_method_body(content, "getFinalResponse(): string {")
    # Must check for empty content (length > 0 or length === 0 or similar)
    has_length_check = re.search(r"\.(?:length|value)\s*[><=!]", body)
    has_empty_check = '""' in body or "=== ''" in body or ".length" in body
    assert has_length_check or has_empty_check, (
        "getFinalResponse must check for empty markdown content to skip trailing empties"
    )


# [pr_diff] fail_to_pass
def test_impl_returns_empty_for_no_parts():
    """getFinalResponse returns empty string when no eligible parts found."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = CHATMODEL_SRC.read_text()
    body = _extract_method_body(content, "getFinalResponse(): string {")
    # Must have an early return for the case where no markdown parts exist
    assert "return ''" in body or 'return ""' in body, (
        "getFinalResponse must return empty string when no markdown parts are found"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — action registration & overlay
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_action_registered():
    """CopyFinalResponseAction is registered in chatCopyActions.ts."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = COPY_ACTIONS_SRC.read_text()
    assert "CopyFinalResponseAction" in content, (
        "CopyFinalResponseAction not found in chatCopyActions.ts"
    )
    assert "registerAction2" in content, (
        "CopyFinalResponseAction must be registered via registerAction2"
    )


# [pr_diff] fail_to_pass
def test_action_invokes_getFinalResponse():
    """CopyFinalResponseAction calls getFinalResponse() on the response."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = COPY_ACTIONS_SRC.read_text()
    assert "getFinalResponse()" in content, (
        "CopyFinalResponseAction must call getFinalResponse() on the response"
    )


# [pr_diff] fail_to_pass
def test_action_writes_to_clipboard():
    """CopyFinalResponseAction writes the result to the clipboard."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = COPY_ACTIONS_SRC.read_text()
    idx = content.find("CopyFinalResponseAction")
    assert idx != -1, "CopyFinalResponseAction not found"
    action_block = content[idx : idx + 1500]
    assert "clipboardService" in action_block.lower() or "writeText" in action_block, (
        "CopyFinalResponseAction must write to the clipboard via clipboardService"
    )


# [pr_diff] fail_to_pass
def test_action_gated_by_isResponse():
    """CopyFinalResponseAction menu is gated by ChatContextKeys.isResponse."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = COPY_ACTIONS_SRC.read_text()
    # Find the CopyFinalResponseAction section
    idx = content.find("CopyFinalResponseAction")
    assert idx != -1
    action_block = content[idx : idx + 800]
    assert "isResponse" in action_block, (
        "CopyFinalResponseAction must use ChatContextKeys.isResponse for menu visibility"
    )


# [pr_diff] fail_to_pass
def test_context_key_in_overlay():
    """isResponse context key is added to createOverlay() in chatListWidget.ts."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = LIST_WIDGET_SRC.read_text()
    # The overlay must include ChatContextKeys.isResponse.key (not just isResponseVM)
    assert "ChatContextKeys.isResponse.key" in content, (
        "ChatContextKeys.isResponse.key not found in chatListWidget.ts — "
        "needed for the context menu to show/hide the copy action"
    )
    # Verify it's in the createOverlay call context
    overlay_idx = content.find("createOverlay")
    assert overlay_idx != -1, "createOverlay() call not found in chatListWidget.ts"
    window = content[overlay_idx : overlay_idx + 500]
    assert "isResponse.key" in window, (
        "ChatContextKeys.isResponse.key must be inside the createOverlay() call"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — unit tests & mocks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_unit_tests_added():
    """chatModel.test.ts contains getFinalResponse unit tests."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = CHATMODEL_TEST.read_text()
    assert "getFinalResponse" in content, (
        "chatModel.test.ts must have tests for getFinalResponse"
    )
    # Verify multiple test cases exist (at least 3 of the 5 expected scenarios)
    test_patterns = [
        "tool call",     # after tool call scenario
        "empty",         # empty markdown / empty response scenario
        "inline",        # inline reference scenario
    ]
    matches = sum(1 for p in test_patterns if p.lower() in content.lower())
    assert matches >= 2, (
        f"Expected at least 2 distinct getFinalResponse test scenarios, found {matches}"
    )


# [pr_diff] fail_to_pass
def test_mocks_updated():
    """Mock IResponse objects include getFinalResponse in test helper files."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    found = 0
    for test_file in [APPROVAL_TEST, CONTROLLER_TEST]:
        if test_file.exists():
            content = test_file.read_text()
            if "getFinalResponse" in content:
                found += 1
    assert found >= 1, (
        "At least one mock response in agentSessions test files must include getFinalResponse"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_original_interface_preserved():
    """IResponse still declares getMarkdown() and toString() (not broken by changes)."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = CHATMODEL_SRC.read_text()
    iface_match = re.search(
        r"export\s+interface\s+IResponse\s*\{(.*?)\n\}",
        content,
        re.DOTALL,
    )
    assert iface_match, "IResponse interface not found"
    iface_body = iface_match.group(1)
    assert "getMarkdown()" in iface_body, "IResponse.getMarkdown() was removed"
    assert "toString()" in iface_body, "IResponse.toString() was removed"


# ---------------------------------------------------------------------------
# Agent config checks
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:99 @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
def test_action_label_title_case():
    """Copy Final Response action label uses title-case capitalization."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = COPY_ACTIONS_SRC.read_text()
    # Title-style capitalization required for command labels (copilot-instructions.md:99)
    assert "Copy Final Response" in content, (
        "Action label should be 'Copy Final Response' (title case) — "
        "required by .github/copilot-instructions.md:99"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:140 @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
def test_no_any_in_getFinalResponse():
    """getFinalResponse body does not use 'any' or 'unknown' types."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = CHATMODEL_SRC.read_text()
    body = _extract_method_body(content, "getFinalResponse(): string {")
    assert ": any" not in body, (
        "getFinalResponse uses ': any' — forbidden by .github/copilot-instructions.md:140"
    )
    assert ": unknown" not in body, (
        "getFinalResponse uses ': unknown' — forbidden by .github/copilot-instructions.md:140"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:132 @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
def test_action_label_localized():
    """CopyFinalResponseAction label uses localize/localize2 (not a raw string)."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    content = COPY_ACTIONS_SRC.read_text()
    idx = content.find("CopyFinalResponseAction")
    assert idx != -1, "CopyFinalResponseAction not found"
    action_block = content[idx : idx + 600]
    assert "localize" in action_block, (
        "Action label must be localized using localize/localize2 — "
        "required by .github/copilot-instructions.md:132"
    )
