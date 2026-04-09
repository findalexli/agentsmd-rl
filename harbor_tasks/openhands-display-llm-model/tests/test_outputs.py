"""Test outputs for the OpenHands LLM model display feature.

This test suite verifies that the LLM model field is properly plumbed through:
1. Backend: ConversationInfo dataclass has llm_model field
2. Backend: manage_conversations.py populates the field
3. Frontend: TypeScript types include llm_model
4. Frontend: Components display the LLM model with CircuitIcon
"""

import subprocess
import sys
import os
import re
import json

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"


def test_backend_conversation_info_has_llm_model():
    """Verify ConversationInfo dataclass has llm_model field."""
    file_path = f"{REPO}/openhands/server/data_models/conversation_info.py"
    with open(file_path, 'r') as f:
        content = f.read()

    # Check that the dataclass has llm_model field
    assert "llm_model: str | None = None" in content, \
        "ConversationInfo dataclass missing llm_model field"

    # Verify it's in the class body (not just a comment)
    class_pattern = r'class ConversationInfo:.*?llm_model: str \| None = None'
    assert re.search(class_pattern, content, re.DOTALL), \
        "llm_model field not properly defined in ConversationInfo class"


def test_backend_manage_conversations_populates_llm_model():
    """Verify _to_conversation_info function populates llm_model field."""
    file_path = f"{REPO}/openhands/server/routes/manage_conversations.py"
    with open(file_path, 'r') as f:
        content = f.read()

    # Check that llm_model is populated from app_conversation
    assert "llm_model=app_conversation.llm_model" in content, \
        "_to_conversation_info function doesn't populate llm_model field"

    # Verify it's in the return statement
    return_pattern = r'return ConversationInfo\([^)]*llm_model=app_conversation\.llm_model'
    assert re.search(return_pattern, content, re.DOTALL), \
        "llm_model not properly set in ConversationInfo constructor call"


def test_frontend_types_include_llm_model():
    """Verify TypeScript Conversation interface includes llm_model."""
    file_path = f"{FRONTEND}/src/api/open-hands.types.ts"
    with open(file_path, 'r') as f:
        content = f.read()

    # Check Conversation interface has llm_model
    assert "llm_model?: string | null;" in content, \
        "Conversation interface missing llm_model field"

    # Verify it's in the Conversation interface specifically
    interface_pattern = r'export interface Conversation \{[^}]*llm_model\?: string \| null;'
    assert re.search(interface_pattern, content, re.DOTALL), \
        "llm_model not properly defined in Conversation interface"


def test_conversation_card_accepts_llm_model_prop():
    """Verify ConversationCard component accepts llmModel prop."""
    file_path = f"{FRONTEND}/src/components/features/conversation-panel/conversation-card/conversation-card.tsx"
    with open(file_path, 'r') as f:
        content = f.read()

    # Check interface has llmModel prop
    assert "llmModel?: string | null;" in content, \
        "ConversationCardProps missing llmModel prop"

    # Check component destructures llmModel
    assert "llmModel," in content, \
        "ConversationCard component doesn't destructure llmModel prop"

    # Check llmModel is passed to ConversationCardFooter
    footer_pattern = r'<ConversationCardFooter[^>]*llmModel=\{llmModel\}'
    assert re.search(footer_pattern, content, re.DOTALL), \
        "llmModel prop not passed to ConversationCardFooter"


def test_conversation_card_footer_displays_llm_model():
    """Verify ConversationCardFooter displays LLM model with CircuitIcon."""
    file_path = f"{FRONTEND}/src/components/features/conversation-panel/conversation-card/conversation-card-footer.tsx"
    with open(file_path, 'r') as f:
        content = f.read()

    # Check for CircuitIcon import
    assert 'import CircuitIcon' in content, \
        "CircuitIcon not imported in conversation-card-footer.tsx"

    # Check interface has llmModel prop
    assert "llmModel?: string | null;" in content, \
        "ConversationCardFooterProps missing llmModel prop"

    # Check for llmModel conditional rendering
    assert "{llmModel && (" in content or "llmModel &&" in content, \
        "llmModel not conditionally rendered in footer"

    # Check for data-testid attribute
    assert 'data-testid="conversation-card-llm-model"' in content, \
        "Missing data-testid for llm model display"

    # Check for CircuitIcon usage
    assert "<CircuitIcon" in content, \
        "CircuitIcon not used in llm_model display"

    # Check for truncation
    assert "truncate" in content, \
        "LLM model display missing truncation for long names"

    # Check for title attribute (tooltip)
    assert "title={llmModel}" in content, \
        "LLM model display missing title tooltip"


def test_conversation_panel_passes_llm_model():
    """Verify ConversationPanel passes llm_model to ConversationCard."""
    file_path = f"{FRONTEND}/src/components/features/conversation-panel/conversation-panel.tsx"
    with open(file_path, 'r') as f:
        content = f.read()

    # Check llm_model is passed to ConversationCard
    assert "llmModel={project.llm_model}" in content, \
        "llm_model not passed from project to ConversationCard"


def test_conversation_name_displays_llm_model():
    """Verify ConversationName component displays LLM model."""
    file_path = f"{FRONTEND}/src/components/features/conversation/conversation-name.tsx"
    with open(file_path, 'r') as f:
        content = f.read()

    # Check for CircuitIcon import
    assert 'import CircuitIcon' in content, \
        "CircuitIcon not imported in conversation-name.tsx"

    # Check for conversation.llm_model usage
    assert "conversation.llm_model" in content, \
        "conversation.llm_model not used in ConversationName"

    # Check for conditional rendering with titleMode check
    assert "titleMode !== \"edit\" && conversation.llm_model" in content, \
        "llm_model not conditionally rendered with titleMode check"

    # Check for data-testid attribute
    assert 'data-testid="conversation-name-llm-model"' in content, \
        "Missing data-testid for llm model display in conversation-name"

    # Check for CircuitIcon usage
    assert "<CircuitIcon" in content, \
        "CircuitIcon not used in conversation-name llm_model display"

    # Check for title attribute (tooltip)
    assert "title={conversation.llm_model}" in content, \
        "LLM model display missing title tooltip in conversation-name"


def test_recent_conversation_displays_llm_model():
    """Verify RecentConversation component displays LLM model."""
    file_path = f"{FRONTEND}/src/components/features/home/recent-conversations/recent-conversation.tsx"
    with open(file_path, 'r') as f:
        content = f.read()

    # Check for CircuitIcon import
    assert 'import CircuitIcon' in content, \
        "CircuitIcon not imported in recent-conversation.tsx"

    # Check for conversation.llm_model usage
    assert "conversation.llm_model" in content, \
        "conversation.llm_model not used in RecentConversation"

    # Check for conditional rendering
    assert "{conversation.llm_model && (" in content or "conversation.llm_model &&" in content, \
        "llm_model not conditionally rendered in RecentConversation"

    # Check for data-testid attribute
    assert 'data-testid="recent-conversation-llm-model"' in content, \
        "Missing data-testid for llm model display in recent-conversation"

    # Check for CircuitIcon usage
    assert "<CircuitIcon" in content, \
        "CircuitIcon not used in recent-conversation llm_model display"

    # Check for title attribute (tooltip)
    assert "title={conversation.llm_model}" in content, \
        "LLM model display missing title tooltip in recent-conversation"


def test_frontend_typescript_compiles():
    """Verify frontend TypeScript compiles without errors (pass_to_pass)."""
    # Use npm run typecheck which runs react-router typegen && tsc
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_frontend_lint_passes():
    """Verify frontend lint passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )

    # Allow both 0 (success) and non-zero but without 'error' in output
    # Some warnings are acceptable
    if result.returncode != 0:
        assert "error" not in result.stdout.lower() and "error" not in result.stderr.lower(), \
            f"Lint failed with errors:\n{result.stdout}\n{result.stderr}"


def test_frontend_build_passes():
    """Verify frontend builds successfully (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Frontend build failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_frontend_unit_tests_conversation_components():
    """Verify conversation component unit tests pass (pass_to_pass)."""
    # Run tests for conversation-related components modified in this PR
    test_files = [
        "__tests__/components/features/conversation-panel/conversation-card.test.tsx",
        "__tests__/components/features/conversation-panel/conversation-panel.test.tsx",
        "__tests__/components/features/conversation/conversation-name.test.tsx",
        "__tests__/components/features/home/recent-conversations.test.tsx",
    ]
    result = subprocess.run(
        ["npx", "vitest", "run"] + test_files,
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Conversation component tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
