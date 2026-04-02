"""
Task: vscode-chat-instructions-error-handling
Repo: microsoft/vscode @ ba1bdcd30b83d8090ee0f28549299a52874d71ac

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: This is a TypeScript repo — tests use grep/regex on the source file.
# AST-only because: TypeScript cannot be imported or executed in Python
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"
TARGET_FILE = f"{REPO}/src/vs/workbench/contrib/chat/browser/widget/chatWidget.ts"


def _get_method_body(method_name: str, lookahead: int = 60) -> str:
    """Return lines starting from the first occurrence of async <method_name>."""
    content = Path(TARGET_FILE).read_text()
    lines = content.splitlines()
    start = None
    for i, line in enumerate(lines):
        if f"async {method_name}" in line:
            start = i
            break
    assert start is not None, f"Method {method_name!r} not found in {TARGET_FILE}"
    return "\n".join(lines[start : start + lookahead])


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_try_block_around_collect():
    """_autoAttachInstructions wraps await computer.collect() in a try block."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    body = _get_method_body("_autoAttachInstructions")
    # Both the try keyword and the collect call must appear in the method body
    assert "try {" in body, "No 'try {' block found in _autoAttachInstructions"
    assert "await computer.collect" in body, (
        "await computer.collect() not found inside _autoAttachInstructions"
    )
    # The try must come before the collect call (i.e., collect is inside the try)
    try_pos = body.index("try {")
    collect_pos = body.index("await computer.collect")
    assert try_pos < collect_pos, (
        "try { must appear before await computer.collect() in the method"
    )


# [pr_diff] fail_to_pass
def test_catch_block_logs_error():
    """Catch block catches the exception and logs it via logService.error."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    body = _get_method_body("_autoAttachInstructions")
    assert re.search(r"catch\s*\(", body), (
        "No catch block found in _autoAttachInstructions"
    )
    assert "logService.error" in body, (
        "logService.error not called in catch block — error is silently swallowed"
    )
    assert "failed to compute automatic instructions" in body, (
        "Expected error message 'failed to compute automatic instructions' not found in catch block"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_original_logic_preserved():
    """Core instruction-computation logic is still present inside the try block."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    body = _get_method_body("_autoAttachInstructions")
    assert "ComputeAutomaticInstructions" in body, (
        "ComputeAutomaticInstructions class instantiation was removed"
    )
    assert "enabledTools" in body, "enabledTools assignment was removed"
    assert "enabledSubAgents" in body, "enabledSubAgents assignment was removed"
    assert "CancellationToken.None" in body, "CancellationToken.None was removed"


# [static] pass_to_pass
def test_catch_is_not_empty():
    """Catch block has real error handling — not an empty {} or just a comment."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    body = _get_method_body("_autoAttachInstructions")
    # Find the catch block
    catch_match = re.search(r"catch\s*\(err\)\s*\{([^}]*)\}", body, re.DOTALL)
    assert catch_match is not None, "Could not locate catch block body"
    catch_body = catch_match.group(1).strip()
    # Must have actual statements (not just whitespace/comments)
    non_comment = re.sub(r"//.*", "", catch_body).strip()
    assert len(non_comment) > 0, "Catch block is empty — exception is silently swallowed"
    assert "logService" in catch_body, (
        "Catch block must call logService to record the error"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:147 @ ba1bdcd30b83d8090ee0f28549299a52874d71ac
def test_no_promise_then_in_method():
    """Fix uses async/await, not .then() chains (copilot-instructions.md:147)."""
    # AST-only because: TypeScript cannot be imported or executed in Python
    body = _get_method_body("_autoAttachInstructions")
    # Check no .then( calls are present inside the method
    assert ".then(" not in body, (
        "Fix must use 'await' syntax, not Promise.then() chains"
        " (see .github/copilot-instructions.md:147)"
    )
