"""Tests for excalidraw/excalidraw#10679 - Keep input focus during generation."""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/excalidraw")
CHAT_INTERFACE_PATH = REPO / "packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx"
LOCALES_PATH = REPO / "packages/excalidraw/locales/en.json"


def read_file(path: Path) -> str:
    """Read file contents, fail test if not found."""
    if not path.exists():
        pytest.fail(f"Required file not found: {path}")
    return path.read_text()


def test_submit_blocked_during_generation():
    """F2P: handleSubmit must NOT be called when isGenerating is true.

    The bug: pressing Enter during generation would trigger submit and lose focus.
    The fix: Must guard handleSubmit() with isGenerating check (either early return
    or conditional wrapper).
    """
    content = read_file(CHAT_INTERFACE_PATH)

    # Find the handleKeyDown function - look for the function definition
    # Use a simpler approach: find the function and check its body
    func_start = content.find('const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>)')
    if func_start == -1:
        pytest.fail("Could not find handleKeyDown function")

    # Extract function body by finding matching braces
    func_content = content[func_start:]
    brace_start = func_content.find('{')
    if brace_start == -1:
        pytest.fail("Could not find handleKeyDown function body start")

    # Simple extraction: find the section from first { to the corresponding }
    depth = 0
    end_pos = None
    for i, char in enumerate(func_content[brace_start:], start=brace_start):
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                end_pos = i
                break

    if end_pos is None:
        pytest.fail("Could not find handleKeyDown function body end")

    keydown_body = func_content[brace_start:brace_start + end_pos + 1]

    # Must have an isGenerating check somewhere before/during handleSubmit
    # Valid patterns:
    # 1. if (!isGenerating) { handleSubmit() }
    # 2. if (isGenerating) { return; } handleSubmit()
    # 3. if (isGenerating) return; handleSubmit()
    valid_patterns = [
        r'if \(!isGenerating\)',  # Negative guard
        r'if \(isGenerating\)[^}]*(?:return|early)',  # Early return
    ]

    # Check for unconditional handleSubmit call (the bug)
    # The bug is: just `handleSubmit()` without any isGenerating check nearby
    has_generating_guard = any(
        re.search(pattern, keydown_body)
        for pattern in valid_patterns
    )

    if not has_generating_guard:
        pytest.fail(
            "handleSubmit() is not guarded by isGenerating check. "
            "Pressing Enter during generation will submit and lose focus. "
            "Add a guard like: if (!isGenerating) { handleSubmit(); } "
            "or: if (isGenerating) return; handleSubmit();"
        )


def test_input_not_disabled_during_generation():
    """F2P: Input must remain enabled during generation to preserve focus.

    The bug: input was disabled={isGenerating || ...} which loses focus.
    The fix: disabled={rateLimits?.rateLimitRemaining === 0} (no isGenerating).
    """
    content = read_file(CHAT_INTERFACE_PATH)

    # Find the textarea element - handle multiline by finding opening and closing >
    textarea_start = content.find('<textarea')
    if textarea_start == -1:
        pytest.fail("Could not find textarea element")

    # Find the closing > of the textarea tag (handling multiline)
    # Look for > followed by optional whitespace and newline or another attribute
    depth = 0
    textarea_end = None
    in_string = False
    string_char = None

    for i, char in enumerate(content[textarea_start:], start=textarea_start):
        if not in_string:
            if char in ('"', "'"):
                in_string = True
                string_char = char
            elif char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
            elif char == '>' and depth == 0:
                # Make sure this > is not inside a string or expression
                textarea_end = i
                break
        else:
            if char == string_char and content[i-1] != '\\':
                in_string = False

    if textarea_end is None:
        pytest.fail("Could not find end of textarea opening tag")

    textarea_tag = content[textarea_start:textarea_end + 1]

    # Find disabled prop in the textarea tag
    disabled_match = re.search(r'disabled=\{([^}]+)\}', textarea_tag)
    if not disabled_match:
        pytest.fail("Could not find textarea disabled prop")

    disabled_value = disabled_match.group(1).strip()

    # Must NOT contain isGenerating - should only check rateLimits
    if "isGenerating" in disabled_value:
        pytest.fail(
            f"Input is disabled based on isGenerating: {disabled_value}. "
            "This causes focus loss during generation."
        )

    # Must contain rateLimits check
    if "rateLimits" not in disabled_value:
        pytest.fail(
            f"Input disabled prop missing rateLimits check: {disabled_value}"
        )


def test_placeholder_shows_generating_state():
    """F2P: Placeholder must show "Generating..." when isGenerating is true.

    The fix adds a ternary at the start of placeholder that checks isGenerating
    and shows the generating message.
    """
    content = read_file(CHAT_INTERFACE_PATH)

    # Find the placeholder prop content
    placeholder_pattern = r'placeholder=\{\s*([^}]+t\("chat\.generating"\)[^}]+)\}'
    if not re.search(placeholder_pattern, content, re.DOTALL):
        # Alternative: check for the isGenerating ternary pattern
        ternary_pattern = r'isGenerating\s*\?\s*t\("chat\.generating"\)'
        if not re.search(ternary_pattern, content):
            pytest.fail(
                "Placeholder does not show 'Generating...' state when isGenerating is true. "
                "Expected: isGenerating ? t(\"chat.generating\") : ..."
            )


def test_localization_string_exists():
    """P2P: The "chat.generating" localization key must exist in en.json."""
    content = read_file(LOCALES_PATH)

    locales = json.loads(content)

    if "chat" not in locales:
        pytest.fail("Missing 'chat' section in locales")

    if "generating" not in locales["chat"]:
        pytest.fail(
            "Missing 'chat.generating' localization key. "
            "The placeholder references this string."
        )

    # Verify the value is what we expect
    expected = "Generating..."
    if locales["chat"]["generating"] != expected:
        pytest.fail(
            f"Unexpected value for 'chat.generating': {locales['chat']['generating']}. "
            f"Expected: {expected}"
        )


def test_visual_indicator_for_generating_state():
    """P2P: Visual border color indicator when generating.

    The fix adds a style prop to the input wrapper that changes border color
    when isGenerating is true.
    """
    content = read_file(CHAT_INTERFACE_PATH)

    # Find the input-wrapper div and its style prop
    # Should have: style={{ borderColor: isGenerating ? "var(--dialog-border-color)" : undefined }}
    style_pattern = r'style=\{\{\s*borderColor:\s*isGenerating\s*\?\s*"var\(--dialog-border-color\)"'
    if not re.search(style_pattern, content, re.DOTALL):
        pytest.fail(
            "Missing visual indicator (borderColor style) for generating state. "
            "The input wrapper should have a style prop that changes border color when generating."
        )


# =============================================================================
# Repo CI/CD Pass-to-Pass Tests
# =============================================================================
# These tests ensure the fix doesn't break existing CI/CD checks

REPO_ROOT = Path("/workspace/excalidraw")


def test_repo_typecheck():
    """P2P: Repo TypeScript typecheck passes (yarn test:typecheck)."""
    r = subprocess.run(
        ["yarn", "test:typecheck"],
        capture_output=True, text=True, timeout=120, cwd=REPO_ROOT,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_lint():
    """P2P: Repo ESLint passes (yarn test:code)."""
    r = subprocess.run(
        ["yarn", "test:code"],
        capture_output=True, text=True, timeout=120, cwd=REPO_ROOT,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_formatting():
    """P2P: Repo Prettier formatting passes (yarn test:other)."""
    r = subprocess.run(
        ["yarn", "test:other"],
        capture_output=True, text=True, timeout=120, cwd=REPO_ROOT,
    )
    assert r.returncode == 0, f"Prettier formatting check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# Import pytest at the end to allow module loading even if pytest isn't available
try:
    import pytest
except ImportError:
    # Create a minimal pytest stub for when running without pytest installed
    class PytestStub:
        @staticmethod
        def fail(msg):
            print(f"FAIL: {msg}")
            sys.exit(1)
    pytest = PytestStub()


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_submit_blocked_during_generation,
        test_input_not_disabled_during_generation,
        test_placeholder_shows_generating_state,
        test_localization_string_exists,
        test_visual_indicator_for_generating_state,
        test_repo_typecheck,
        test_repo_lint,
        test_repo_formatting,
    ]

    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__}: {e}")
            failed += 1

    if failed > 0:
        print(f"\n{failed} test(s) failed")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)
