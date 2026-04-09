"""
Task: lobe-chat-refactor-remove-legacy-messageloadingids-from
Repo: lobehub/lobe-chat @ 034c7c203b23926b09ebe228e19f0567ac729568
PR:   13662

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/lobe-chat"
INITIAL_STATE_FILE = f"{REPO}/src/store/chat/slices/message/initialState.ts"
RUNTIME_STATE_FILE = f"{REPO}/src/store/chat/slices/message/actions/runtimeState.ts"
SELECTORS_FILE = f"{REPO}/src/store/chat/slices/message/selectors/messageState.ts"
AGENT_GROUP_FILE = f"{REPO}/src/store/chat/slices/aiAgent/actions/agentGroup.ts"
RUN_AGENT_FILE = f"{REPO}/src/store/chat/slices/aiAgent/actions/runAgent.ts"
CONVERSATION_LIFECYCLE_FILE = f"{REPO}/src/store/chat/slices/aiChat/actions/conversationLifecycle.ts"
MESSAGE_OPTIMISTIC_FILE = f"{REPO}/src/store/chat/slices/message/actions/optimisticUpdate.ts"
PLUGIN_OPTIMISTIC_FILE = f"{REPO}/src/store/chat/slices/plugin/actions/optimisticUpdate.ts"
GENERATION_FILE = f"{REPO}/src/features/Conversation/store/slices/generation/action.ts"
SKILL_FILE = f"{REPO}/.agents/skills/zustand/SKILL.md"


def _read_file(path: str) -> str:
    """Read file content, return empty string if not found."""
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return ""


def _run_node_script(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript/TypeScript code via Node."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax_valid():
    """Modified TypeScript files must parse without errors."""
    files_to_check = [
        INITIAL_STATE_FILE,
        RUNTIME_STATE_FILE,
        SELECTORS_FILE,
        AGENT_GROUP_FILE,
        RUN_AGENT_FILE,
        CONVERSATION_LIFECYCLE_FILE,
        MESSAGE_OPTIMISTIC_FILE,
        PLUGIN_OPTIMISTIC_FILE,
        GENERATION_FILE,
    ]

    for file_path in files_to_check:
        content = _read_file(file_path)
        if not content:
            continue  # Skip files that don't exist (might be moved/deleted)

        # Check for basic syntax using TypeScript parser
        r = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck", file_path],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )

        # Allow warnings and "Cannot find module" errors, but not syntax errors
        if r.returncode != 0 and "error TS" in r.stderr:
            if "Cannot find module" not in r.stderr:
                assert False, f"Syntax error in {file_path}:\n{r.stderr}"

    assert True


# [static] pass_to_pass
def test_files_not_empty():
    """Modified files are not empty or stubbed."""
    files_to_check = [
        INITIAL_STATE_FILE,
        SELECTORS_FILE,
        SKILL_FILE,
    ]

    for file_path in files_to_check:
        content = _read_file(file_path)
        assert len(content) > 100, f"{file_path} seems too small or empty ({len(content)} chars)"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_message_loading_ids_removed_from_initial_state():
    """messageLoadingIds state removed from ChatMessageState interface and initialMessageState."""
    content = _read_file(INITIAL_STATE_FILE)
    assert content, f"File not found: {INITIAL_STATE_FILE}"

    # Check that messageLoadingIds is NOT in the interface
    assert "messageLoadingIds" not in content, \
        "messageLoadingIds still exists in initialState.ts - should be removed"

    # Verify the interface still has other expected properties
    assert "messageEditingIds" in content, \
        "messageEditingIds should still exist in initialState.ts"


# [pr_diff] fail_to_pass
def test_toggle_message_loading_action_removed():
    """internal_toggleMessageLoading action removed from runtimeState.ts."""
    content = _read_file(RUNTIME_STATE_FILE)
    assert content, f"File not found: {RUNTIME_STATE_FILE}"

    # Check that internal_toggleMessageLoading is NOT in the file
    assert "internal_toggleMessageLoading" not in content, \
        "internal_toggleMessageLoading still exists in runtimeState.ts - should be removed"

    # Verify other actions still exist
    assert "internal_preventLeaving" in content, \
        "internal_preventLeaving should still exist in runtimeState.ts"


# [pr_diff] fail_to_pass
def test_is_message_loading_uses_operation_system():
    """isMessageLoading selector simplified to only use operation system."""
    content = _read_file(SELECTORS_FILE)
    assert content, f"File not found: {SELECTORS_FILE}"

    # Check that isMessageLoading now only uses operationSelectors
    # The fix: isMessageLoading = (id) => (s) => operationSelectors.isMessageProcessing(id)(s)
    is_message_loading_pattern = r'isMessageLoading\s*=\s*\(id:\s*string\)\s*=>\s*\(s:\s*ChatStoreState\)\s*=>\s*operationSelectors\.isMessageProcessing\(id\)\(s\)'
    assert re.search(is_message_loading_pattern, content), \
        "isMessageLoading should be simplified to use only operationSelectors.isMessageProcessing"

    # Verify legacy fallback to messageLoadingIds is removed
    assert "s.messageLoadingIds" not in content, \
        "Legacy fallback to s.messageLoadingIds should be removed from isMessageLoading"


# [pr_diff] fail_to_pass
def test_dead_selectors_removed():
    """Dead selectors isHasMessageLoading and isSendButtonDisabledByMessage removed."""
    content = _read_file(SELECTORS_FILE)
    assert content, f"File not found: {SELECTORS_FILE}"

    # Check that dead selectors are removed
    assert "isHasMessageLoading" not in content, \
        "isHasMessageLoading selector should be removed"
    assert "isSendButtonDisabledByMessage" not in content, \
        "isSendButtonDisabledByMessage selector should be removed"

    # Verify messageStateSelectors export no longer includes dead selectors
    assert "messageStateSelectors = {" in content, \
        "messageStateSelectors export should exist"


# [pr_diff] fail_to_pass
def test_agent_group_no_longer_calls_toggle_loading():
    """agentGroup.ts no longer calls internal_toggleMessageLoading."""
    content = _read_file(AGENT_GROUP_FILE)
    assert content, f"File not found: {AGENT_GROUP_FILE}"

    # Check that internal_toggleMessageLoading is not called
    assert "internal_toggleMessageLoading" not in content, \
        "agentGroup.ts should not reference internal_toggleMessageLoading"


# [pr_diff] fail_to_pass
def test_run_agent_no_longer_calls_toggle_loading():
    """runAgent.ts no longer calls internal_toggleMessageLoading."""
    content = _read_file(RUN_AGENT_FILE)
    assert content, f"File not found: {RUN_AGENT_FILE}"

    # Check that internal_toggleMessageLoading is not called
    assert "internal_toggleMessageLoading" not in content, \
        "runAgent.ts should not reference internal_toggleMessageLoading"


# [pr_diff] fail_to_pass
def test_conversation_lifecycle_no_longer_calls_toggle_loading():
    """conversationLifecycle.ts no longer calls internal_toggleMessageLoading."""
    content = _read_file(CONVERSATION_LIFECYCLE_FILE)
    assert content, f"File not found: {CONVERSATION_LIFECYCLE_FILE}"

    # Check that internal_toggleMessageLoading is not called
    assert "internal_toggleMessageLoading" not in content, \
        "conversationLifecycle.ts should not reference internal_toggleMessageLoading"


# [pr_diff] fail_to_pass
def test_message_optimistic_no_longer_calls_toggle_loading():
    """message optimisticUpdate.ts no longer calls internal_toggleMessageLoading."""
    content = _read_file(MESSAGE_OPTIMISTIC_FILE)
    assert content, f"File not found: {MESSAGE_OPTIMISTIC_FILE}"

    # Check that internal_toggleMessageLoading is not called
    assert "internal_toggleMessageLoading" not in content, \
        "optimisticUpdate.ts should not reference internal_toggleMessageLoading"


# [pr_diff] fail_to_pass
def test_plugin_optimistic_no_longer_calls_toggle_loading():
    """plugin optimisticUpdate.ts no longer calls internal_toggleMessageLoading."""
    content = _read_file(PLUGIN_OPTIMISTIC_FILE)
    assert content, f"File not found: {PLUGIN_OPTIMISTIC_FILE}"

    # Check that internal_toggleMessageLoading is not called
    assert "internal_toggleMessageLoading" not in content, \
        "plugin optimisticUpdate.ts should not reference internal_toggleMessageLoading"


# [pr_diff] fail_to_pass
def test_generation_uses_operation_selectors():
    """generation action.ts uses operationSelectors.isMessageProcessing instead of messageLoadingIds."""
    content = _read_file(GENERATION_FILE)
    assert content, f"File not found: {GENERATION_FILE}"

    # Check that operationSelectors is imported and used
    assert "operationSelectors" in content, \
        "generation/action.ts should import and use operationSelectors"

    # Check that messageLoadingIds is not used
    assert "messageLoadingIds" not in content, \
        "generation/action.ts should not reference messageLoadingIds"

    # Check for the correct pattern: operationSelectors.isMessageProcessing(messageId)
    assert "operationSelectors.isMessageProcessing" in content, \
        "generation/action.ts should use operationSelectors.isMessageProcessing"


# -----------------------------------------------------------------------------
# Config-derived (agent_config) — rules from SKILL.md
# -----------------------------------------------------------------------------

# [agent_config] fail_to_pass — .agents/skills/zustand/SKILL.md @ 034c7c203b23926b09ebe228e19f0567ac729568
def test_skill_md_no_longer_references_message_loading_ids():
    """SKILL.md no longer references messageLoadingIds state."""
    content = _read_file(SKILL_FILE)
    assert content, f"File not found: {SKILL_FILE}"

    # Check that messageLoadingIds is NOT mentioned in SKILL.md
    assert "messageLoadingIds" not in content, \
        "SKILL.md should not reference messageLoadingIds - should be removed per refactor"


# [agent_config] fail_to_pass — .agents/skills/zustand/SKILL.md @ 034c7c203b23926b09ebe228e19f0567ac729568
def test_skill_md_no_longer_references_toggle_loading_action():
    """SKILL.md no longer references internal_toggleMessageLoading action."""
    content = _read_file(SKILL_FILE)
    assert content, f"File not found: {SKILL_FILE}"

    # Check that internal_toggleMessageLoading is NOT mentioned in SKILL.md
    assert "internal_toggleMessageLoading" not in content, \
        "SKILL.md should not reference internal_toggleMessageLoading - action was removed"

    # Verify that other toggle patterns still exist (to confirm we're not just checking empty file)
    assert "internal_dispatch" in content, \
        "SKILL.md should still reference other internal patterns"
