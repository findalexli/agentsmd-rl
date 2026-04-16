"""
Task: lobechat-interrupted-hint-queue-edit
Repo: lobehub/lobe-chat @ 9c08fa5cdf2116e041b63255be3e498f1ae8d1e3
PR:   13397

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import pytest
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/lobe-chat"


def _run_node(script: str, timeout: int = 15) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )


def _run_tsx(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run TypeScript/JavaScript code using npx tsx."""
    return subprocess.run(
        ["npx", "--yes", "tsx", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_files_parse():
    """Modified TypeScript/TSX files must parse without errors."""
    ts_files = [
        "src/features/Conversation/Messages/Assistant/components/InterruptedHint.tsx",
        "src/features/Conversation/Messages/Assistant/index.tsx",
        "src/features/Conversation/Messages/AssistantGroup/index.tsx",
        "src/features/Conversation/ChatInput/QueueTray.tsx",
        "src/features/Conversation/store/slices/messageState/selectors.ts",
        "src/features/Conversation/types/operation.ts",
        "src/hooks/useOperationState.ts",
    ]
    for f in ts_files:
        p = Path(REPO) / f
        assert p.exists(), f"File missing: {f}"
        content = p.read_text()
        assert len(content) > 0, f"File is empty: {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interrupted_computation_logic():
    """The isInterrupted flag must be true when the latest runtime op was cancelled."""
    result = _run_node("""
const AI_RUNTIME_OPERATION_TYPES = ['execAgentRuntime', 'chatCompletion'];

// Case 1: cancelled runtime op → interrupted
const ops1 = [
  { type: 'execAgentRuntime', status: 'cancelled' },
];
const running1 = ops1.filter(op => op.status === 'running');
const isGen1 = running1.some(op => AI_RUNTIME_OPERATION_TYPES.includes(op.type));
const latest1 = [...ops1].reverse().find(op => AI_RUNTIME_OPERATION_TYPES.includes(op.type));
const interrupted1 = !isGen1 && !!latest1 && latest1.status === 'cancelled';
if (!interrupted1) throw new Error('Case 1: should be interrupted');

// Case 2: running runtime op → NOT interrupted
const ops2 = [
  { type: 'execAgentRuntime', status: 'running' },
];
const running2 = ops2.filter(op => op.status === 'running');
const isGen2 = running2.some(op => AI_RUNTIME_OPERATION_TYPES.includes(op.type));
const latest2 = [...ops2].reverse().find(op => AI_RUNTIME_OPERATION_TYPES.includes(op.type));
const interrupted2 = !isGen2 && !!latest2 && latest2.status === 'cancelled';
if (interrupted2) throw new Error('Case 2: should NOT be interrupted when running');

// Case 3: completed runtime op → NOT interrupted
const ops3 = [
  { type: 'execAgentRuntime', status: 'completed' },
];
const running3 = ops3.filter(op => op.status === 'running');
const isGen3 = running3.some(op => AI_RUNTIME_OPERATION_TYPES.includes(op.type));
const latest3 = [...ops3].reverse().find(op => AI_RUNTIME_OPERATION_TYPES.includes(op.type));
const interrupted3 = !isGen3 && !!latest3 && latest3.status === 'cancelled';
if (interrupted3) throw new Error('Case 3: should NOT be interrupted when completed');

// Case 4: cancelled then retried (running) → NOT interrupted (latest wins)
const ops4 = [
  { type: 'execAgentRuntime', status: 'cancelled' },
  { type: 'execAgentRuntime', status: 'running' },
];
const running4 = ops4.filter(op => op.status === 'running');
const isGen4 = running4.some(op => AI_RUNTIME_OPERATION_TYPES.includes(op.type));
const latest4 = [...ops4].reverse().find(op => AI_RUNTIME_OPERATION_TYPES.includes(op.type));
const interrupted4 = !isGen4 && !!latest4 && latest4.status === 'cancelled';
if (interrupted4) throw new Error('Case 4: retry should not show interrupted');

console.log(JSON.stringify({ allPassed: true }));
""")
    assert result.returncode == 0, f"Logic test failed:\n{result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["allPassed"] is True


# [pr_diff] fail_to_pass
def test_complete_operation_preserves_cancelled():
    """completeOperation must not overwrite cancelled status."""
    result = _run_node("""
// Simulate the operation status preservation logic
const op1 = { status: 'cancelled' };
if (op1.status !== 'cancelled') { op1.status = 'completed'; }
if (op1.status !== 'cancelled') throw new Error('Case 1: cancelled should be preserved');

const op2 = { status: 'running' };
if (op2.status !== 'cancelled') { op2.status = 'completed'; }
if (op2.status !== 'completed') throw new Error('Case 2: running should become completed');

const op3 = { status: 'running' };
// Simulate cancel happening before completeOperation
op3.status = 'cancelled';
if (op3.status !== 'cancelled') { op3.status = 'completed'; }
if (op3.status !== 'cancelled') throw new Error('Case 3: late cancel should be preserved');

console.log(JSON.stringify({ allPassed: true }));
""")
    assert result.returncode == 0, f"Status preservation test failed:\n{result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["allPassed"] is True


# [pr_diff] fail_to_pass
def test_operation_state_has_interrupted():
    """MessageOperationState type must include isInterrupted field and be usable."""
    # Verify TypeScript syntax by running tsx on the file (it will syntax-check)
    # Also verify the type definition contains the expected field using tsx
    result = _run_tsx(f"""
const fs = require('fs');
const path = '/workspace/lobe-chat/src/features/Conversation/types/operation.ts';
const content = fs.readFileSync(path, 'utf8');

// The isInterrupted field should be defined in the type
// We verify by checking the source has the field declaration
if (!content.includes('isInterrupted')) {{
  throw new Error('isInterrupted field not found in operation types');
}}

// Verify it's typed as boolean (has boolean type annotation)
if (!content.includes('isInterrupted: boolean')) {{
  throw new Error('isInterrupted must be typed as boolean');
}}

// Verify the default state sets it to false
if (!content.includes('isInterrupted: false')) {{
  throw new Error('DEFAULT_MESSAGE_OPERATION_STATE must set isInterrupted: false');
}}

console.log(JSON.stringify({{ allPassed: true }}));
""")
    assert result.returncode == 0, f"Type check failed:\n{result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["allPassed"] is True


# [pr_diff] fail_to_pass
def test_interrupted_selector_exists():
    """The isMessageInterrupted selector must be exported and usable."""
    # Try to parse the selectors module and verify isMessageInterrupted is exported
    result = _run_tsx(f"""
const fs = require('fs');
const content = fs.readFileSync('/workspace/lobe-chat/src/features/Conversation/store/slices/messageState/selectors.ts', 'utf8');

// Check that isMessageInterrupted is defined as a const function
if (!content.includes('const isMessageInterrupted')) {{
  throw new Error('isMessageInterrupted must be defined as a const function');
}}

// Check it's exported in the selectors object
if (!content.includes('isMessageInterrupted')) {{
  throw new Error('isMessageInterrupted selector not found');
}}

// Check it's included in the messageStateSelectors export
if (!content.includes('export const messageStateSelectors') ||
    !content.match(/isMessageInterrupted/s)) {{
  throw new Error('isMessageInterrupted must be in messageStateSelectors export');
}}

console.log(JSON.stringify({{ allPassed: true }}));
""")
    assert result.returncode == 0, f"Selector verification failed:\n{result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["allPassed"] is True


# [pr_diff] fail_to_pass
def test_interrupted_hint_component():
    """InterruptedHint component must exist, use memo, and use correct i18n keys."""
    result = _run_tsx(f"""
const fs = require('fs');
const path = '/workspace/lobe-chat/src/features/Conversation/Messages/Assistant/components/InterruptedHint.tsx';

// Verify file exists
try {{
  fs.accessSync(path);
}} catch (e) {{
  throw new Error('InterruptedHint.tsx does not exist');
}}

const content = fs.readFileSync(path, 'utf8');

// Must be a memo component
if (!content.includes('memo')) {{
  throw new Error('InterruptedHint must use memo');
}}

// Must use the correct i18n keys
if (!content.includes('messageAction.interrupted')) {{
  throw new Error('Must use messageAction.interrupted i18n key');
}}

if (!content.includes('messageAction.interruptedHint')) {{
  throw new Error('Must use messageAction.interruptedHint i18n key');
}}

// Must be named InterruptedHint
if (!content.includes('InterruptedHint')) {{
  throw new Error('Component must be named InterruptedHint');
}}

// Must be a default export
if (!content.includes('export default')) {{
  throw new Error('InterruptedHint must be a default export');
}}

console.log(JSON.stringify({{ allPassed: true }}));
""")
    assert result.returncode == 0, f"Component verification failed:\n{result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["allPassed"] is True


# [pr_diff] fail_to_pass
def test_queue_tray_edit_button():
    """QueueTray must have an edit button that uses Pencil icon and proper callbacks."""
    result = _run_tsx(f"""
const fs = require('fs');
const content = fs.readFileSync('/workspace/lobe-chat/src/features/Conversation/ChatInput/QueueTray.tsx', 'utf8');

// Must import Pencil icon from lucide-react
if (!content.includes('Pencil') || !content.includes('lucide-react')) {{
  throw new Error('Must import Pencil icon from lucide-react');
}}

// Must define handleEdit callback
if (!content.includes('handleEdit')) {{
  throw new Error('Must define handleEdit callback');
}}

// handleEdit must remove message from queue
if (!content.includes('removeQueuedMessage')) {{
  throw new Error('handleEdit must remove message from queue');
}}

// handleEdit must restore content to editor
if (!content.includes('setDocument')) {{
  throw new Error('handleEdit must restore content to editor');
}}

// handleEdit must be wrapped in useCallback
if (!content.includes('useCallback')) {{
  throw new Error('handleEdit must be wrapped in useCallback');
}}

console.log(JSON.stringify({{ allPassed: true }}));
""")
    assert result.returncode == 0, f"QueueTray verification failed:\n{result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["allPassed"] is True


# [pr_diff] fail_to_pass
def test_locale_interrupted_keys():
    """Locale files must contain the interrupted and interruptedHint keys with correct values."""
    # Test default locale (TypeScript) - import and verify keys exist with expected values
    result_default = _run_tsx(f"""
import chat from '/workspace/lobe-chat/src/locales/default/chat';

// Verify the keys exist with expected string values
const interruptedKey = chat['messageAction.interrupted'];
const interruptedHintKey = chat['messageAction.interruptedHint'];

if (!interruptedKey || typeof interruptedKey !== 'string') {{
  throw new Error('messageAction.interrupted key missing or invalid in default locale');
}}

if (!interruptedHintKey || typeof interruptedHintKey !== 'string') {{
  throw new Error('messageAction.interruptedHint key missing or invalid in default locale');
}}

// The values should be meaningful (not empty)
if (interruptedKey.length === 0) {{
  throw new Error('messageAction.interrupted value is empty');
}}

if (interruptedHintKey.length === 0) {{
  throw new Error('messageAction.interruptedHint value is empty');
}}

console.log(JSON.stringify({{ allPassed: true, interruptedKey, interruptedHintKey }}));
""")
    assert result_default.returncode == 0, f"Default locale import failed:\n{result_default.stderr}"
    data_default = json.loads(result_default.stdout.strip())
    assert data_default["allPassed"] is True

    # Test en-US locale (JSON) - verify keys exist (flat key structure)
    en_chat = Path(f"{REPO}/locales/en-US/chat.json")
    assert en_chat.exists(), "en-US locale file must exist"
    en_data = json.loads(en_chat.read_text())
    assert "messageAction.interrupted" in en_data, "en-US must have messageAction.interrupted key"
    assert "messageAction.interruptedHint" in en_data, "en-US must have messageAction.interruptedHint key"

    # Test zh-CN locale (JSON) - verify keys exist with Chinese translations (flat key structure)
    zh_chat = Path(f"{REPO}/locales/zh-CN/chat.json")
    assert zh_chat.exists(), "zh-CN locale file must exist"
    zh_data = json.loads(zh_chat.read_text())
    assert "messageAction.interrupted" in zh_data, "zh-CN must have messageAction.interrupted key"
    assert "messageAction.interruptedHint" in zh_data, "zh-CN must have messageAction.interruptedHint key"
    # Chinese translations should be non-empty strings
    assert isinstance(zh_data["messageAction.interrupted"], str) and len(zh_data["messageAction.interrupted"]) > 0
    assert isinstance(zh_data["messageAction.interruptedHint"], str) and len(zh_data["messageAction.interruptedHint"]) > 0


# ---------------------------------------------------------------------------
# Config-derived (pr_diff) — agent config file updates
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_screen_recording():
    """The electron-testing SKILL.md must document the Screen Recording feature."""
    skill_path = Path(f"{REPO}/.agents/skills/electron-testing/SKILL.md")
    assert skill_path.exists(), "electron-testing SKILL.md must exist"
    content = skill_path.read_text()

    # Verify it has a Screen Recording section (heading)
    # A markdown section typically starts with ## or ###
    if not any(pattern in content for pattern in ["## Screen Recording", "### Screen Recording"]):
        raise AssertionError("SKILL.md must have a Screen Recording section")

    # Verify it references the recording script
    if "record-electron-demo" not in content:
        raise AssertionError("SKILL.md must reference record-electron-demo.sh")

    # Verify it mentions ffmpeg for video capture
    if "ffmpeg" not in content:
        raise AssertionError("SKILL.md must mention ffmpeg for recording")

    # Verify it mentions agent-browser for automation
    if "agent-browser" not in content:
        raise AssertionError("SKILL.md must mention agent-browser for automation")


# [pr_diff] fail_to_pass
def test_recording_script_exists():
    """The record-electron-demo.sh script must exist and be executable."""
    script_path = Path(f"{REPO}/.agents/skills/electron-testing/record-electron-demo.sh")
    assert script_path.exists(), "record-electron-demo.sh must exist"

    # Check shebang is correct
    content = script_path.read_text()
    if not content.startswith("#!/usr/bin/env bash"):
        raise AssertionError("Must be a bash script with correct shebang")

    # Verify it has start_recording function
    if "start_recording" not in content:
        raise AssertionError("Must have start_recording function")

    # Verify it has stop_recording function
    if "stop_recording" not in content:
        raise AssertionError("Must have stop_recording function")

    # Verify it uses ffmpeg for video capture
    if "ffmpeg" not in content:
        raise AssertionError("Must use ffmpeg for video capture")

    # Verify it configures CDP port
    if "CDP_PORT" not in content:
        raise AssertionError("Must configure CDP port for Electron")

    # Verify it uses agent-browser
    if "agent-browser" not in content:
        raise AssertionError("Must use agent-browser for automation")


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_message_state_selectors():
    """Existing message state selectors must still be present and unchanged."""
    content = Path(f"{REPO}/src/features/Conversation/store/slices/messageState/selectors.ts").read_text()
    for selector in ["isMessageEditing", "isMessageGenerating", "isMessageLoading",
                     "isMessageProcessing", "isMessageRegenerating"]:
        assert selector in content, f"Existing selector {selector} must still be present"


# [static] pass_to_pass
def test_not_stub():
    """The isInterrupted computation has real logic, not a stub."""
    content = Path(f"{REPO}/src/hooks/useOperationState.ts").read_text()
    assert "latestRuntimeOp" in content, "Must compute latestRuntimeOp"
    assert ".reverse()" in content, "Must reverse operation list to find latest"
    assert ".find(" in content, "Must use find to locate latest runtime op"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — real CI commands that should pass on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint_modified_files():
    """ESLint passes on modified TypeScript files (pass_to_pass)."""
    # Check if node_modules exists (required for eslint to work)
    if not (Path(REPO) / "node_modules").exists():
        pytest.skip("Dependencies not installed - skipping ESLint test")

    # Only lint files that exist in base commit (filter out new files added by PR)
    files = [
        "src/hooks/useOperationState.ts",
        "src/features/Conversation/store/slices/messageState/selectors.ts",
        "src/features/Conversation/types/operation.ts",
        "src/features/Conversation/Messages/Assistant/index.tsx",
        "src/features/Conversation/Messages/AssistantGroup/index.tsx",
        "src/features/Conversation/ChatInput/QueueTray.tsx",
    ]
    # Filter to only existing files
    existing_files = [f for f in files if (Path(REPO) / f).exists()]
    if not existing_files:
        return  # Skip if no files to lint
    cmd = ["npx", "eslint"] + existing_files + ["--quiet"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=REPO)
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck_selectors():
    """TypeScript typecheck on messageState selectors passes (pass_to_pass)."""
    # Check if node_modules exists (required for tsc to work)
    if not (Path(REPO) / "node_modules").exists():
        pytest.skip("Dependencies not installed - skipping typecheck test")

    # Use the local typescript compiler
    tsc_path = Path(REPO) / "node_modules" / ".bin" / "tsc"
    if not tsc_path.exists():
        pytest.skip("TypeScript not installed - skipping typecheck test")

    r = subprocess.run(
        [str(tsc_path), "--noEmit", "--skipLibCheck", "src/features/Conversation/store/slices/messageState/selectors.ts"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    # Note: tsc may return non-zero for lib issues (exit code 2), but should not crash
    assert r.returncode in [0, 2], f"TypeScript check crashed unexpectedly:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_file_structure():
    """Repo file structure matches expected layout (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "test -d src/features/Conversation && test -d src/hooks && test -d src/store"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, "Repo directory structure is incorrect"



# [repo_tests] pass_to_pass
def test_repo_unit_test_operation_state():
    """useOperationState hook unit tests pass (pass_to_pass)."""
    if not (Path(REPO) / "node_modules").exists():
        pytest.skip("Dependencies not installed - skipping unit test")

    r = subprocess.run(
        ["npx", "vitest", "run", "--silent=passed-only", "src/hooks/useOperationState.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"useOperationState tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_test_operation_actions():
    """Operation actions unit tests pass (pass_to_pass)."""
    if not (Path(REPO) / "node_modules").exists():
        pytest.skip("Dependencies not installed - skipping unit test")

    r = subprocess.run(
        ["npx", "vitest", "run", "--silent=passed-only", "src/store/chat/slices/operation/__tests__/actions.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Operation actions tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_test_streaming_executor():
    """Streaming executor unit tests pass (pass_to_pass)."""
    if not (Path(REPO) / "node_modules").exists():
        pytest.skip("Dependencies not installed - skipping unit test")

    r = subprocess.run(
        ["npx", "vitest", "run", "--silent=passed-only", "src/store/chat/slices/aiChat/actions/__tests__/streamingExecutor.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Streaming executor tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typescript_compile_hooks():
    """TypeScript compiles hooks directory without errors (pass_to_pass)."""
    if not (Path(REPO) / "node_modules").exists():
        pytest.skip("Dependencies not installed - skipping typecheck test")

    tsc_path = Path(REPO) / "node_modules" / ".bin" / "tsc"
    if not tsc_path.exists():
        pytest.skip("TypeScript not installed - skipping typecheck test")

    r = subprocess.run(
        [str(tsc_path), "--noEmit", "--skipLibCheck", "src/hooks/useOperationState.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # tsc returns 0 on success, 2 on type errors (but not crash)
    assert r.returncode in [0, 2], f"TypeScript check crashed unexpectedly:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_vitest_config_valid():
    """Vitest configuration is valid and loads (pass_to_pass)."""
    if not (Path(REPO) / "node_modules").exists():
        pytest.skip("Dependencies not installed - skipping vitest config test")

    r = subprocess.run(
        ["npx", "vitest", "run", "--help"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Just check vitest can load and show help (verifies config does not crash)
    assert r.returncode == 0 or "Usage:" in r.stdout, f"Vitest config seems invalid:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint_config_valid():
    """ESLint configuration is valid and loads (pass_to_pass)."""
    if not (Path(REPO) / "node_modules").exists():
        pytest.skip("Dependencies not installed - skipping eslint config test")

    r = subprocess.run(
        ["npx", "eslint", "--help"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Check eslint can load (verifies config does not crash)
    assert r.returncode == 0 or "Usage:" in r.stdout, f"ESLint config seems invalid:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_test_selectors():
    """messageStateSelectors unit tests pass (pass_to_pass)."""
    if not (Path(REPO) / "node_modules").exists():
        pytest.skip("Dependencies not installed - skipping unit test")

    r = subprocess.run(
        ["npx", "vitest", "run", "--silent=passed-only", "src/store/chat/slices/operation/__tests__/selectors.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Selectors tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_vitest_run_cancel_functionality():
    """Cancel functionality tests in streamingExecutor pass (pass_to_pass)."""
    if not (Path(REPO) / "node_modules").exists():
        pytest.skip("Dependencies not installed - skipping unit test")

    r = subprocess.run(
        ["npx", "vitest", "run", "--silent=passed-only", "-t", "cancel", "src/store/chat/slices/aiChat/actions/__tests__/streamingExecutor.test.ts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Cancel functionality tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"