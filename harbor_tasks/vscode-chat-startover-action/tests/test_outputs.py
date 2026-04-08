"""
Task: vscode-chat-startover-action
Repo: microsoft/vscode @ d7ebb2cc7dcab5b7d7c9bc98ad5b96652dcab650

Fix: Add StartOverAction for first request checkpoint, add isFirstRequest
context key, and hide fork/restore-checkpoint actions on first request.

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/vscode"

CHAT_EDITING_ACTIONS = f"{REPO}/src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts"
CHAT_CONTEXT_KEYS = f"{REPO}/src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts"
CHAT_LIST_RENDERER = f"{REPO}/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts"
CHAT_FORK_ACTIONS = f"{REPO}/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# --- fail_to_pass tests (must fail on base, pass on fix) ---


def test_is_first_request_context_key():
    """isFirstRequest context key must be defined in chatContextKeys.ts with correct RawContextKey name."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

// Must have isFirstRequest export
if (!src.includes('isFirstRequest')) {
    throw new Error('isFirstRequest export not found');
}

// Must use RawContextKey with key name 'chatFirstRequest'
const match = src.match(/isFirstRequest\\s*=\\s*new\\s+RawContextKey.*?['"](\\w+)['"]/);
if (!match) {
    throw new Error('isFirstRequest not defined as RawContextKey');
}
if (match[1] !== 'chatFirstRequest') {
    throw new Error('Expected key chatFirstRequest, got: ' + match[1]);
}
console.log('PASS');
""", CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Context key check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_start_over_action_registered():
    """StartOverAction class must be registered via registerAction2 with correct action ID."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

// Must have the StartOverAction class
if (!src.includes('class StartOverAction extends Action2')) {
    throw new Error('StartOverAction class not found or does not extend Action2');
}

// Must have the correct action ID
if (!src.includes('workbench.action.chat.startOver')) {
    throw new Error('StartOverAction must have id workbench.action.chat.startOver');
}

// Must have registerAction2 wrapping
if (!src.match(/registerAction2\\(class\\s+StartOverAction/)) {
    throw new Error('StartOverAction must be registered via registerAction2');
}

console.log('PASS');
""", CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"StartOverAction registration check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_start_over_action_when_clause():
    """StartOverAction must show only when isFirstRequest is true (not negated)."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

// Find the StartOverAction block
const startOverIdx = src.indexOf('class StartOverAction');
if (startOverIdx === -1) throw new Error('StartOverAction class not found');

// Get text from StartOverAction to the next registerAction2 or end
const afterStartOver = src.substring(startOverIdx);
const nextRegister = afterStartOver.indexOf('registerAction2(class', 10);
const block = nextRegister > 0 ? afterStartOver.substring(0, nextRegister) : afterStartOver;

// Must reference isFirstRequest in when clause (without .negate())
if (!block.includes('isFirstRequest')) {
    throw new Error('StartOverAction menu when clause must reference isFirstRequest');
}

// Must NOT have .negate() on isFirstRequest in this block
// Look for the when clause line
const whenLines = block.split('\\n').filter(l => l.includes('when:') && l.includes('ContextKeyExpr'));
for (const line of whenLines) {
    if (line.includes('isFirstRequest') && line.includes('.negate()')) {
        throw new Error('StartOverAction when clause should NOT negate isFirstRequest');
    }
}

console.log('PASS');
""", CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"StartOverAction when clause check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_start_over_action_run_method():
    """StartOverAction must have a run method that calls setCheckpoint and restoreSnapshotWithConfirmation."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

const startOverIdx = src.indexOf('class StartOverAction');
if (startOverIdx === -1) throw new Error('StartOverAction class not found');

const afterStartOver = src.substring(startOverIdx);
const nextRegister = afterStartOver.indexOf('registerAction2(class', 10);
const block = nextRegister > 0 ? afterStartOver.substring(0, nextRegister) : afterStartOver;

// Must have async run method
if (!block.includes('async run(')) {
    throw new Error('StartOverAction must have async run method');
}

// Must call setCheckpoint
if (!block.includes('setCheckpoint')) {
    throw new Error('StartOverAction.run must call setCheckpoint');
}

// Must call restoreSnapshotWithConfirmation
if (!block.includes('restoreSnapshotWithConfirmation')) {
    throw new Error('StartOverAction.run must call restoreSnapshotWithConfirmation');
}

console.log('PASS');
""", CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"StartOverAction run method check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_first_request_bound_in_renderer():
    """isFirstRequest must be bound in chatListRenderer.ts with first-request detection logic."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

// Must bind isFirstRequest
if (!src.includes('isFirstRequest')) {
    throw new Error('isFirstRequest not referenced in renderer');
}

// Must bind to context key service
if (!src.match(/isFirstRequest.*\\.bindTo/)) {
    throw new Error('isFirstRequest must be bound via bindTo');
}

// Must check if request is first in model (getRequests)
if (!src.includes('getRequests()')) {
    throw new Error('Must check getRequests() to identify first request');
}

// The binding must compare element id with first request id
const bindingMatch = src.match(/isFirstRequest[^;]*\\n?[^;]*set\\([^)]+\\)/);
if (!bindingMatch) {
    throw new Error('isFirstRequest binding with set() not found');
}

console.log('PASS');
""", CHAT_LIST_RENDERER)
    assert r.returncode == 0, f"Renderer binding check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_fork_hidden_on_first_request():
    """Fork action must have isFirstRequest.negate() in its when clause."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

// Must reference isFirstRequest
if (!src.includes('isFirstRequest')) {
    throw new Error('isFirstRequest not referenced in fork actions');
}

// Must negate it (hide fork on first request)
if (!src.includes('isFirstRequest.negate()')) {
    throw new Error('Fork when clause must include isFirstRequest.negate()');
}

console.log('PASS');
""", CHAT_FORK_ACTIONS)
    assert r.returncode == 0, f"Fork hidden check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_restore_checkpoint_hidden_on_first():
    """RestoreCheckpoint action must hide when isFirstRequest is true (negated in when clause)."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

// Find RestoreCheckpointAction block
const restoreIdx = src.indexOf('class RestoreCheckpointAction');
if (restoreIdx === -1) throw new Error('RestoreCheckpointAction class not found');

const afterRestore = src.substring(restoreIdx);
const nextRegister = afterRestore.indexOf('registerAction2(class', 10);
const block = nextRegister > 0 ? afterRestore.substring(0, nextRegister) : afterRestore;

// The when clause must include isFirstRequest.negate()
if (!block.includes('isFirstRequest')) {
    throw new Error('RestoreCheckpoint when clause must reference isFirstRequest');
}
if (!block.includes('isFirstRequest.negate()')) {
    throw new Error('RestoreCheckpoint when clause must include isFirstRequest.negate()');
}

console.log('PASS');
""", CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"RestoreCheckpoint hidden check failed: {r.stderr}"
    assert "PASS" in r.stdout


# --- pass_to_pass tests (should pass on both base and fix) ---


def test_chat_context_keys_structure():
    """ChatContextKeys namespace must have core keys that exist on both base and fix."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

// Core keys that must exist regardless of fix
const requiredKeys = ['isResponse', 'isRequest', 'itemId', 'isPendingRequest'];
for (const key of requiredKeys) {
    if (!src.includes(key)) {
        throw new Error('Missing required context key: ' + key);
    }
}

// Must be a namespace export
if (!src.includes('export namespace ChatContextKeys')) {
    throw new Error('ChatContextKeys namespace not found');
}

console.log('PASS');
""", CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Context keys structure check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_start_over_action_label_and_tooltip():
    """StartOverAction must have proper label and tooltip using localize2."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

const startOverIdx = src.indexOf('class StartOverAction');
if (startOverIdx === -1) throw new Error('StartOverAction class not found');

const afterStartOver = src.substring(startOverIdx);
const nextRegister = afterStartOver.indexOf('registerAction2(class', 10);
const block = nextRegister > 0 ? afterStartOver.substring(0, nextRegister) : afterStartOver;

// Must use localize2 for label
if (!block.includes("localize2('chat.startOver.label'")) {
    throw new Error('StartOverAction must use localize2 for label with key chat.startOver.label');
}

// Must have tooltip with localize2
if (!block.includes("localize2('chat.startOver.tooltip'")) {
    throw new Error('StartOverAction must use localize2 for tooltip with key chat.startOver.tooltip');
}

// Must have f1: false (not in command palette)
if (!block.includes('f1: false')) {
    throw new Error('StartOverAction should have f1: false');
}

console.log('PASS');
""", CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"StartOverAction label/tooltip check failed: {r.stderr}"
    assert "PASS" in r.stdout
