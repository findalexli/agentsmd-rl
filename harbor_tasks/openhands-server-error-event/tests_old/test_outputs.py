"""Tests for OpenHands ServerErrorEvent handling PR.

This task verifies that the frontend properly handles the new ServerErrorEvent type
from the Agent Server, displaying error banners for server-side errors like MCP
configuration failures.
"""

import subprocess
import sys
import os

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"


def test_typescript_compilation():
    """Frontend TypeScript compilation passes (pass_to_pass).

    This is a basic CI check that ensures the code compiles without type errors.
    """
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stderr[-1000:]}"


def test_server_error_event_type_exists():
    """ServerErrorEvent type definition exists in conversation-state-event.ts (fail_to_pass).

    The ServerErrorEvent interface must be defined with the correct structure:
    - kind: "ServerErrorEvent"
    - source: "environment"
    - code: string
    - detail: string
    """
    # Check that the type definition file contains ServerErrorEvent
    type_file = f"{FRONTEND}/src/types/v1/core/events/conversation-state-event.ts"

    with open(type_file, "r") as f:
        content = f.read()

    # Verify ServerErrorEvent interface exists
    assert "ServerErrorEvent" in content, "ServerErrorEvent interface not found"
    assert 'kind: "ServerErrorEvent"' in content, "ServerErrorEvent kind discriminator not found"
    assert 'source: "environment"' in content, "ServerErrorEvent source not found"
    assert "code: string" in content, "ServerErrorEvent code property not found"
    assert "detail: string" in content, "ServerErrorEvent detail property not found"


def test_is_server_error_event_guard_exists():
    """isServerErrorEvent type guard exists and is correctly implemented (fail_to_pass).

    The type guard must:
    1. Be exported from type-guards.ts
    2. Check that event.kind === "ServerErrorEvent"
    3. Return event is ServerErrorEvent
    """
    guards_file = f"{FRONTEND}/src/types/v1/type-guards.ts"

    with open(guards_file, "r") as f:
        content = f.read()

    # Verify isServerErrorEvent function exists
    assert "isServerErrorEvent" in content, "isServerErrorEvent function not found"
    assert "ServerErrorEvent" in content, "ServerErrorEvent import or reference not found in type-guards.ts"


def test_is_displayable_error_event_guard_exists():
    """isDisplayableErrorEvent type guard exists and combines both error types (fail_to_pass).

    The type guard must:
    1. Be exported from type-guards.ts
    2. Return true for both ConversationErrorEvent and ServerErrorEvent
    3. Use isConversationErrorEvent and isServerErrorEvent internally
    """
    guards_file = f"{FRONTEND}/src/types/v1/type-guards.ts"

    with open(guards_file, "r") as f:
        content = f.read()

    # Verify isDisplayableErrorEvent function exists
    assert "isDisplayableErrorEvent" in content, "isDisplayableErrorEvent function not found"

    # Verify it calls both individual guards
    assert "isConversationErrorEvent(event)" in content or "isConversationErrorEvent ( event )" in content, \
        "isDisplayableErrorEvent should call isConversationErrorEvent"
    assert "isServerErrorEvent(event)" in content or "isServerErrorEvent ( event )" in content, \
        "isDisplayableErrorEvent should call isServerErrorEvent"


def test_websocket_context_uses_displayable_error():
    """WebSocket context uses isDisplayableErrorEvent instead of just isConversationErrorEvent (fail_to_pass).

    The conversation-websocket-context.tsx must:
    1. Import isDisplayableErrorEvent
    2. Use it in place of isConversationErrorEvent for showing error banners
    3. Handle both ConversationErrorEvent and ServerErrorEvent uniformly
    """
    context_file = f"{FRONTEND}/src/contexts/conversation-websocket-context.tsx"

    with open(context_file, "r") as f:
        content = f.read()

    # Verify isDisplayableErrorEvent is imported and used
    assert "isDisplayableErrorEvent" in content, "isDisplayableErrorEvent not used in websocket context"

    # Verify isConversationErrorEvent is no longer used directly for error checking
    # (it should only appear in the import statement or as part of isDisplayableErrorEvent)
    lines = content.split("\n")
    in_import = False
    for line in lines:
        if "import" in line and "isConversationErrorEvent" in line:
            in_import = True
            break

    # Should use isDisplayableErrorEvent, not isConversationErrorEvent directly
    assert "isConversationErrorEvent(" not in content or in_import, \
        "isConversationErrorEvent should not be called directly, use isDisplayableErrorEvent instead"


def test_openhands_event_includes_server_error():
    """OpenHandsEvent union type includes ServerErrorEvent (fail_to_pass).

    The main event union type must include ServerErrorEvent to allow it to flow
    through the event system.
    """
    event_file = f"{FRONTEND}/src/types/v1/core/openhands-event.ts"

    with open(event_file, "r") as f:
        content = f.read()

    # Verify ServerErrorEvent is imported
    assert "ServerErrorEvent" in content, "ServerErrorEvent not imported in openhands-event.ts"

    # Verify ServerErrorEvent is in the union type
    assert "| ServerErrorEvent" in content or "ServerErrorEvent |" in content, \
        "ServerErrorEvent not included in OpenHandsEvent union type"


def test_mock_helper_includes_server_error():
    """Mock helper includes createMockServerErrorEvent function (fail_to_pass).

    The mock helpers must provide a way to create ServerErrorEvent test data.
    """
    mock_file = f"{FRONTEND}/src/mocks/mock-ws-helpers.ts"

    with open(mock_file, "r") as f:
        content = f.read()

    # Verify createMockServerErrorEvent exists
    assert "createMockServerErrorEvent" in content, "createMockServerErrorEvent function not found"

    # Verify ServerErrorEvent is imported
    assert "ServerErrorEvent" in content, "ServerErrorEvent not imported in mock-ws-helpers.ts"


def test_websocket_handler_tests_exist():
    """Tests for ServerErrorEvent handling exist in the test file (fail_to_pass).

    The PR should add tests for:
    1. Basic ServerErrorEvent handling
    2. Different error codes
    3. Error clearing after ServerErrorEvent
    """
    test_file = f"{FRONTEND}/__tests__/conversation-websocket-handler.test.tsx"

    with open(test_file, "r") as f:
        content = f.read()

    # Verify createMockServerErrorEvent is imported
    assert "createMockServerErrorEvent" in content, "createMockServerErrorEvent not imported in tests"

    # Verify ServerErrorEvent tests exist
    assert "ServerErrorEvent" in content, "No ServerErrorEvent tests found"

    # Verify at least one specific test for ServerErrorEvent
    assert "should update error message store on ServerErrorEvent" in content or \
           "should handle different ServerErrorEvent error codes" in content or \
           "should clear error message when a successful event is received after a ServerErrorEvent" in content, \
        "Specific ServerErrorEvent tests not found"


def test_frontend_lint():
    """Frontend linting passes (pass_to_pass).

    This is a basic CI check that ensures the code follows the project's style guidelines.
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Linting failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_repo_build():
    """Frontend build passes (pass_to_pass).

    This is a basic CI check that ensures the frontend builds without errors.
    From .github/workflows/fe-unit-tests.yml
    """
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-1000:]}"


def test_repo_translation_completeness():
    """Translation completeness check passes (pass_to_pass).

    This is a basic CI check that ensures all translation keys have complete
    language coverage. From .github/workflows/lint.yml
    """
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Translation check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_repo_websocket_handler_tests():
    """WebSocket handler tests pass (pass_to_pass).

    Tests for the conversation WebSocket handler which is the relevant module
    being modified by this PR. From the repo's test suite.
    """
    result = subprocess.run(
        ["npx", "vitest", "run", "__tests__/conversation-websocket-handler.test.tsx"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"WebSocket handler tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_repo_error_message_banner_tests():
    """Error message banner tests pass (pass_to_pass).

    Tests for the error message banner component which is relevant to the
    ServerErrorEvent handling changes. From the repo's test suite.
    """
    result = subprocess.run(
        ["npx", "vitest", "run", "__tests__/components/chat/error-message-banner.test.tsx"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Error message banner tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_repo_use_websocket_hook_tests():
    """useWebSocket hook tests pass (pass_to_pass).

    Tests for the useWebSocket hook which is core infrastructure for WebSocket
    communication. Relevant to the ServerErrorEvent handling changes.
    From the repo's test suite.
    """
    result = subprocess.run(
        ["npx", "vitest", "run", "__tests__/hooks/use-websocket.test.ts"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"useWebSocket hook tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_repo_use_event_store_tests():
    """useEventStore tests pass (pass_to_pass).

    Tests for the useEventStore which manages event state including error events.
    Relevant to the ServerErrorEvent handling changes.
    From the repo's test suite.
    """
    result = subprocess.run(
        ["npx", "vitest", "run", "__tests__/stores/use-event-store.test.ts"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"useEventStore tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_repo_ws_client_provider_tests():
    """WebSocket client provider tests pass (pass_to_pass).

    Tests for the WsClientProvider which manages WebSocket connections.
    Relevant to the ServerErrorEvent handling changes.
    From the repo's test suite.
    """
    result = subprocess.run(
        ["npx", "vitest", "run", "__tests__/context/ws-client-provider.test.tsx"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"WsClientProvider tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_repo_conversation_store_tests():
    """Conversation store tests pass (pass_to_pass).

    Tests for the conversation store which manages conversation state.
    Relevant to the ServerErrorEvent handling changes.
    From the repo's test suite.
    """
    result = subprocess.run(
        ["npx", "vitest", "run", "__tests__/stores/conversation-store.test.ts"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Conversation store tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_repo_i18n_duplicate_keys_tests():
    """i18n duplicate keys tests pass (pass_to_pass).

    Tests for i18n translation key duplicates which ensures translation integrity.
    From the repo's test suite via .github/workflows/lint.yml.
    """
    result = subprocess.run(
        ["npx", "vitest", "run", "__tests__/i18n/duplicate-keys.test.ts"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"i18n duplicate keys tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
