"""Tests for excalidraw TTD 429 error handling fix."""

import subprocess
import json
import re

REPO = "/workspace/excalidraw"


def test_translation_key_moved():
    """Mermaid syntax error translation key moved from ttd to chat.errors section."""
    with open(f"{REPO}/packages/excalidraw/locales/en.json", "r") as f:
        content = f.read()

    locales = json.loads(content)

    # Old key should be removed
    assert "errorMermaidSyntax" not in locales.get("ttd", {}), \
        "Old translation key 'ttd.errorMermaidSyntax' should be removed"

    # New key should exist in chat.errors
    chat_errors = locales.get("chat", {}).get("errors", {})
    assert "mermaidParseError" in chat_errors, \
        "New translation key 'chat.errors.mermaidParseError' should exist"

    # Value should be correct
    assert chat_errors["mermaidParseError"] == "Mermaid syntax error", \
        "Translation value should be 'Mermaid syntax error'"


def test_ttd_dialog_uses_new_translation_key():
    """TTDDialogOutput.tsx uses chat.errors.mermaidParseError instead of ttd.errorMermaidSyntax."""
    with open(f"{REPO}/packages/excalidraw/components/TTDDialog/TTDDialogOutput.tsx", "r") as f:
        content = f.read()

    # Should use the new translation key
    assert 't("chat.errors.mermaidParseError")' in content, \
        "TTDDialogOutput.tsx should use 'chat.errors.mermaidParseError'"

    # Should NOT use the old translation key
    assert 't("ttd.errorMermaidSyntax")' not in content, \
        "TTDDialogOutput.tsx should not use 'ttd.errorMermaidSyntax'"


def test_getreadableerrormsg_removed():
    """getReadableErrorMsg helper function should be removed from useTextGeneration.ts."""
    with open(f"{REPO}/packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts", "r") as f:
        content = f.read()

    # getReadableErrorMsg should be removed
    assert "const getReadableErrorMsg" not in content, \
        "getReadableErrorMsg function should be removed"


def test_handleerror_removed():
    """handleError helper function should be removed from useTextGeneration.ts."""
    with open(f"{REPO}/packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts", "r") as f:
        content = f.read()

    # handleError should be removed
    assert "const handleError" not in content, \
        "handleError function should be removed"


def test_new_error_keys_present():
    """New error translation keys should be present in useTextGeneration.ts."""
    with open(f"{REPO}/packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts", "r") as f:
        content = f.read()

    # Should use chat.errors.requestFailed
    assert 't("chat.errors.requestFailed")' in content, \
        "Should use 'chat.errors.requestFailed' for network errors"

    # Should use chat.errors.mermaidParseError
    assert 't("chat.errors.mermaidParseError")' in content, \
        "Should use 'chat.errors.mermaidParseError' for parse errors"

    # Should use chat.errors.generationFailed
    assert 't("chat.errors.generationFailed")' in content, \
        "Should use 'chat.errors.generationFailed' for generation errors"


def test_consolidated_429_error_handling():
    """Consolidated error handling for 429 status and rate limiting."""
    with open(f"{REPO}/packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts", "r") as f:
        content = f.read()

    # Check for consolidated error handling pattern
    # The fix should have: if (error?.status === 429 || rateLimitRemaining === 0)
    pattern = r"error\?\.status === 429.*rateLimitRemaining === 0"
    assert re.search(pattern, content), \
        "Should have consolidated 429 and rate limit remaining check"

    # Check that removeLastAssistantMessage is called in the setChatHistory callback
    # This indicates the proper cleanup of the assistant message on 429
    assert "removeLastAssistantMessage(chatHistory)" in content or \
           "removeLastAssistantMessage" in content, \
        "Should call removeLastAssistantMessage in the error handling"


def test_mermaid_parse_success_tracking():
    """Mermaid parse success should be tracked after successful parsing."""
    with open(f"{REPO}/packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts", "r") as f:
        content = f.read()

    # Should track mermaid parse success
    assert 'trackEvent("ai", "mermaid parse success", "ttd")' in content, \
        "Should track mermaid parse success event"


def test_typescript_compiles():
    """TypeScript type checking passes (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"TypeScript type check failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_lint():
    """ESLint passes on repo code (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"ESLint failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_repo_prettier():
    """Prettier formatting check passes (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Prettier check failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_ttd_stream_fetch():
    """TTD stream fetch utility tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "packages/excalidraw/components/TTDDialog/utils/TTDstreamFetch.test.ts", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"TTDStreamFetch tests failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_mermaid_validation():
    """Mermaid validation utility tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "packages/excalidraw/components/TTDDialog/utils/mermaidValidation.test.ts", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Mermaid validation tests failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_mermaid_utils():
    """Mermaid utility tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "packages/excalidraw/mermaid.test.ts", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Mermaid utils tests failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_mermaid_to_excalidraw():
    """MermaidToExcalidraw component tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "packages/excalidraw/tests/MermaidToExcalidraw.test.tsx", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"MermaidToExcalidraw tests failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"
