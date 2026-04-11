"""Tests for excalidraw TTD chat fixes"""
# NOTE: These tests validate both fail_to_pass (fix works) and pass_to_pass (existing CI still passes)
import subprocess
import re
import json
import os
from pathlib import Path

REPO = Path("/workspace/excalidraw")


def test_typescript_compiles():
    """TypeScript should compile without errors after the fix"""
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"TypeScript check failed:\n{result.stdout}\n{result.stderr}"


def test_chat_interface_uses_layout_effect():
    """ChatInterface.tsx should use useLayoutEffect for scroll behavior to prevent flicker"""
    content = (REPO / "packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx").read_text()

    # Check useLayoutEffect is imported
    assert "useLayoutEffect" in content, "useLayoutEffect should be imported"

    # Check useLayoutEffect is used for scrolling (not useEffect)
    # The fix uses useLayoutEffect for messagesEndRef scrollIntoView
    assert "useLayoutEffect(() => {" in content or "useLayoutEffect (() => {" in content, \
        "useLayoutEffect should be used for scroll behavior"

    # Check messagesEndRef scroll happens in useLayoutEffect
    pattern = r'useLayoutEffect\(\s*\(\)\s*=>\s*\{[^}]*messagesEndRef\.current\?\.scrollIntoView'
    assert re.search(pattern, content, re.DOTALL), \
        "useLayoutEffect should call messagesEndRef.current?.scrollIntoView()"


def test_ongenerate_type_defined():
    """types.ts should define OnGenerate type with object parameter"""
    content = (REPO / "packages/excalidraw/components/TTDDialog/types.ts").read_text()

    # Check OnGenerate type exists with object parameter
    assert "export type OnGenerate = (opts:" in content or "export type OnGenerate = ({" in content, \
        "OnGenerate type should be defined with object parameter"

    # Check it has prompt and isRepairFlow properties
    assert "prompt: string" in content, "OnGenerate should have prompt: string property"
    assert "isRepairFlow?: boolean" in content, "OnGenerate should have isRepairFlow?: boolean property"


def test_chat_interface_uses_ongenerate_prop():
    """ChatInterface.tsx should use onGenerate prop instead of onSendMessage"""
    content = (REPO / "packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx").read_text()

    # Check onSendMessage is renamed to onGenerate
    assert "onSendMessage" not in content, "onSendMessage should be renamed to onGenerate"
    assert "onGenerate:" in content or "onGenerate," in content or "onGenerate}" in content, \
        "onGenerate prop should be used"

    # Check the call uses object parameter
    assert "onGenerate({ prompt:" in content, "onGenerate should be called with object parameter { prompt: ... }"


def test_allow_fixing_parse_error_prop():
    """ChatMessage should receive allowFixingParseError prop for repair button control"""
    interface_content = (REPO / "packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx").read_text()
    message_content = (REPO / "packages/excalidraw/components/TTDDialog/Chat/ChatMessage.tsx").read_text()

    # Check ChatInterface passes allowFixingParseError
    assert "allowFixingParseError={" in interface_content, \
        "ChatInterface should pass allowFixingParseError prop to ChatMessage"

    # Check the logic: only allow fixing if parse error AND is last message
    assert 'message.errorType === "parse"' in interface_content and "index === messages.length - 1" in interface_content, \
        "allowFixingParseError should only be true for parse errors that are the last message"

    # Check ChatMessage accepts the prop
    assert "allowFixingParseError?:" in message_content or "allowFixingParseError?" in message_content, \
        "ChatMessage should accept allowFixingParseError prop"

    # Check the prop gates the repair UI
    assert "allowFixingParseError &&" in message_content, \
        "allowFixingParseError should gate the display of repair buttons"


def test_text_to_diagram_uses_ongenerate_object():
    """TextToDiagram.tsx should call onGenerate with object parameter"""
    content = (REPO / "packages/excalidraw/components/TTDDialog/TextToDiagram.tsx").read_text()

    # Check onGenerate is called with object syntax
    assert "onGenerate({ prompt:" in content, \
        "onGenerate should be called with { prompt: ... } syntax"

    # Check repair flow uses isRepairFlow property
    assert "isRepairFlow: true" in content, \
        "onGenerate should be called with isRepairFlow: true for repairs"


def test_use_text_generation_signature():
    """useTextGeneration.ts should have correct onGenerate signature"""
    content = (REPO / "packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts").read_text()

    # Check onGenerate is typed with OnGenerate
    assert "onGenerate: TTTDDialog.OnGenerate" in content, \
        "onGenerate should be typed as TTTDDialog.OnGenerate"

    # Check it destructures opts parameter
    assert "async ({" in content and "prompt," in content, \
        "onGenerate should destructure opts parameter"

    # Check isRepairFlow default
    assert "isRepairFlow = false" in content, \
        "isRepairFlow should have default value of false"


def test_regeneration_shows_pending_immediately():
    """On regeneration (repair flow), immediately show pending with empty content"""
    content = (REPO / "packages/excalidraw/components/TTDDialog/hooks/useTextGeneration.ts").read_text()

    # In the else branch (isRepairFlow), should always set isGenerating: true and content: ""
    # The fix removes the check for errorType === "network" and always sets these
    pattern = r'if\s*\(\s*!isRepairFlow\s*\)'
    match = re.search(pattern, content)
    assert match, "Should have if (!isRepairFlow) branch"

    # After the else block starts, check for isGenerating: true and content: ""
    else_pattern = r'\}\s*else\s*\{[^}]*updateAssistantContent\([^}]*\{[^}]*isGenerating:\s*true[^}]*content:\s*""[^}]*\}'
    assert re.search(else_pattern, content, re.DOTALL), \
        "In repair flow, should immediately set isGenerating: true and content: \"\""


def test_content_type_check():
    """useTTDChatStorage.ts should use typeof check for content"""
    content = (REPO / "packages/excalidraw/components/TTDDialog/useTTDChatStorage.ts").read_text()

    # Should use typeof check instead of truthy check
    assert 'typeof firstUserMessage.content !== "string"' in content, \
        "Should use typeof check for content (typeof ... !== 'string')"

    # Old pattern should not exist
    assert "!firstUserMessage.content" not in content, \
        "Should not use truthy check (!firstUserMessage.content)"


def test_find_last_index_usage():
    """utils/chat.ts should use findLastIndex helper correctly"""
    content = (REPO / "packages/excalidraw/components/TTDDialog/utils/chat.ts").read_text()

    # Should use findLastIndex function (not method on array)
    assert "findLastIndex(" in content, "Should call findLastIndex as a function"

    # Should pass array as first argument
    assert "findLastIndex(" in content and "chatHistory.messages" in content, \
        "findLastIndex should be called with array as first argument"


def test_messages_end_has_id():
    """messages-end div should have id for testability"""
    content = (REPO / "packages/excalidraw/components/TTDDialog/Chat/ChatInterface.tsx").read_text()

    assert '<div ref={messagesEndRef} id="messages-end"' in content, \
        "messages-end div should have id='messages-end'"


def test_ttd_chat_panel_uses_ongenerate():
    """TTDChatPanel.tsx should use onGenerate instead of onSendMessage"""
    content = (REPO / "packages/excalidraw/components/TTDDialog/Chat/TTDChatPanel.tsx").read_text()

    assert "onSendMessage" not in content, "onSendMessage should be renamed to onGenerate"
    assert "onGenerate:" in content or "onGenerate," in content, \
        "TTDChatPanel should use onGenerate prop"
    assert "onGenerate={onGenerate}" in content, \
        "TTDChatPanel should pass onGenerate to ChatInterface"


def test_chat_message_error_structure():
    """ChatMessage.tsx should have correct error message structure"""
    content = (REPO / "packages/excalidraw/components/TTDDialog/Chat/ChatMessage.tsx").read_text()

    # Check error content is in its own div (not wrapped with error details)
    assert 'className="chat-message__error">{message.content}</div>' in content, \
        "Error content should be in its own div with chat-message__error class"

    # Should use Fragment (<>...</>) for error section structure
    fragment_pattern = r'message\.error\s*\?\s*\(\s*<>[^<]*<div\s+className="chat-message__error">'
    assert re.search(fragment_pattern, content, re.DOTALL), \
        "Error section should use React Fragment for proper structure"


# =============================================================================
# PASS-TO-PASS TESTS: Verify existing CI/CD still passes on base commit
# These ensure candidate solutions don't break existing functionality
# =============================================================================

def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:typecheck"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_lint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:code"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_prettier():
    """Repo's Prettier formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:other"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--watch=false", "--reporter=dot"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_ttd_chat_utils():
    """TTDDialog chat utils tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/excalidraw/components/TTDDialog/utils/chat.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TTD chat utils tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_ttd_stream_fetch():
    """TTDDialog stream fetch tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/excalidraw/components/TTDDialog/utils/TTDstreamFetch.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TTD stream fetch tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_ttd_mermaid_validation():
    """TTDDialog mermaid validation tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/excalidraw/components/TTDDialog/utils/mermaidValidation.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TTD mermaid validation tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
