"""
Task: lobechat-feat-message-queue-agent-runtime
Repo: lobehub/lobe-chat @ 70091935ba75208eeea880b3e5856342beabd22f
PR:   13343

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/lobe-chat"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script from a temp file in the repo directory."""
    script_path = Path(REPO) / "_eval_tmp.js"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: mergeQueuedMessages
# ---------------------------------------------------------------------------

def test_merge_queues_sorted_and_joined():
    """mergeQueuedMessages sorts messages by createdAt and joins content with \\n\\n."""
    result = _run_node(r"""
const fs = require('fs');
const path = require('path');

const source = fs.readFileSync(
  path.join(__dirname, 'src/store/chat/slices/operation/types.ts'), 'utf-8'
);

if (!source.includes('mergeQueuedMessages')) {
  console.error('Function mergeQueuedMessages not found in source');
  process.exit(1);
}

// Extract the function body between the opening { and closing };
const match = source.match(
  /export const mergeQueuedMessages = \(messages[^)]*\)[^{]*\{([\s\S]*?)\n\};/
);
if (!match) {
  console.error('Could not parse function body');
  process.exit(1);
}

const mergeQueuedMessages = new Function('messages', match[1]);

// Test: sorts by createdAt and joins with \n\n
const msgs = [
  { id: 'c', content: 'third', createdAt: 3000, interruptMode: 'soft' },
  { id: 'a', content: 'first', createdAt: 1000, interruptMode: 'soft' },
  { id: 'b', content: 'second', createdAt: 2000, interruptMode: 'soft' },
];
const merged = mergeQueuedMessages(msgs);
console.log(JSON.stringify(merged));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["content"] == "first\n\nsecond\n\nthird", \
        f"Expected sorted+joined content, got: {data['content']!r}"
    assert data["files"] == [], f"Expected empty files, got: {data['files']!r}"


def test_merge_queues_collects_files():
    """mergeQueuedMessages collects and flattens files from all queued messages."""
    result = _run_node(r"""
const fs = require('fs');
const path = require('path');

const source = fs.readFileSync(
  path.join(__dirname, 'src/store/chat/slices/operation/types.ts'), 'utf-8'
);

if (!source.includes('mergeQueuedMessages')) {
  console.error('Function mergeQueuedMessages not found');
  process.exit(1);
}

const match = source.match(
  /export const mergeQueuedMessages = \(messages[^)]*\)[^{]*\{([\s\S]*?)\n\};/
);
if (!match) {
  console.error('Could not parse function body');
  process.exit(1);
}

const mergeQueuedMessages = new Function('messages', match[1]);

// Test: files from multiple messages are flattened
const msgs = [
  { id: 'a', content: 'msg1', createdAt: 100, files: ['f1', 'f2'], interruptMode: 'soft' },
  { id: 'b', content: 'msg2', createdAt: 200, files: ['f3'], interruptMode: 'soft' },
  { id: 'c', content: 'msg3', createdAt: 300, interruptMode: 'hard' },
];
const merged = mergeQueuedMessages(msgs);
console.log(JSON.stringify(merged));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["files"] == ["f1", "f2", "f3"], \
        f"Expected flattened files, got: {data['files']!r}"
    assert data["content"] == "msg1\n\nmsg2\n\nmsg3", \
        f"Expected joined content, got: {data['content']!r}"


def test_merge_empty_queue_returns_empty():
    """mergeQueuedMessages with empty array returns empty content and files."""
    result = _run_node(r"""
const fs = require('fs');
const path = require('path');

const source = fs.readFileSync(
  path.join(__dirname, 'src/store/chat/slices/operation/types.ts'), 'utf-8'
);

if (!source.includes('mergeQueuedMessages')) {
  console.error('Function mergeQueuedMessages not found');
  process.exit(1);
}

const match = source.match(
  /export const mergeQueuedMessages = \(messages[^)]*\)[^{]*\{([\s\S]*?)\n\};/
);
if (!match) {
  console.error('Could not parse function body');
  process.exit(1);
}

const mergeQueuedMessages = new Function('messages', match[1]);

const merged = mergeQueuedMessages([]);
console.log(JSON.stringify(merged));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["content"] == "", f"Expected empty content, got: {data['content']!r}"
    assert data["files"] == [], f"Expected empty files, got: {data['files']!r}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/instruction file update: SKILL.md
# ---------------------------------------------------------------------------

def test_skill_electron_testing_exists():
    """The electron-testing SKILL.md file must exist at the expected path."""
    skill_path = Path(REPO) / ".agents" / "skills" / "electron-testing" / "SKILL.md"
    assert skill_path.exists(), f"SKILL.md not found at {skill_path}"
    content = skill_path.read_text()
    assert len(content) > 100, "SKILL.md should have substantial content"


def test_skill_has_valid_frontmatter():
    """SKILL.md must have proper YAML frontmatter with name and description."""
    skill_path = Path(REPO) / ".agents" / "skills" / "electron-testing" / "SKILL.md"
    content = skill_path.read_text()

    # Check frontmatter delimiters
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    first_close = content.index("---", 3)
    frontmatter = content[3:first_close].strip()

    assert "name: electron-testing" in frontmatter, \
        "Frontmatter must declare name: electron-testing"
    assert "description:" in frontmatter, \
        "Frontmatter must include a description"


def test_skill_documents_agent_browser_patterns():
    """SKILL.md must document agent-browser CLI usage and CDP connection patterns."""
    skill_path = Path(REPO) / ".agents" / "skills" / "electron-testing" / "SKILL.md"
    content = skill_path.read_text()
    content_lower = content.lower()

    # Must document agent-browser CLI
    assert "agent-browser" in content_lower, \
        "SKILL.md must document agent-browser CLI"
    # Must mention CDP (Chrome DevTools Protocol) connection
    assert "cdp" in content_lower or "remote-debugging" in content_lower, \
        "SKILL.md must document CDP or remote debugging connection"
    # Must include snapshot command pattern
    assert "snapshot" in content_lower, \
        "SKILL.md must document snapshot command for element discovery"
    # Must mention Electron-specific pattern
    assert "electron" in content_lower, \
        "SKILL.md must reference Electron app"


def test_skill_documents_zustand_store_access():
    """SKILL.md must document accessing Zustand store state via window.__LOBE_STORES."""
    skill_path = Path(REPO) / ".agents" / "skills" / "electron-testing" / "SKILL.md"
    content = skill_path.read_text()

    assert "__LOBE_STORES" in content, \
        "SKILL.md must document window.__LOBE_STORES for store access"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

def test_repo_utils_unit_tests():
    """Repo's unit tests for chat utils pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
set -e
export PATH="/root/.bun/bin:$PATH"
apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null
curl -fsSL https://bun.sh/install | bash 2>&1 | tail -3
cd /workspace/lobe-chat
timeout 180 bun install --frozen-lockfile 2>&1 | tail -3
timeout 60 bunx vitest run src/store/chat/utils/ --reporter=basic 2>&1
"""],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Utils unit tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_eslint_operation_types():
    """Repo's ESLint passes on operation slice files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
set -e
export PATH="/root/.bun/bin:$PATH"
apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null
curl -fsSL https://bun.sh/install | bash 2>&1 | tail -3
cd /workspace/lobe-chat
timeout 180 bun install --frozen-lockfile 2>&1 | tail -3
timeout 30 bunx eslint src/store/chat/slices/operation/types.ts --quiet 2>&1
"""],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural checks
# ---------------------------------------------------------------------------

def test_operation_state_includes_queued_messages():
    """The operation initial state must include queuedMessages field."""
    state_path = Path(REPO) / "src/store/chat/slices/operation/initialState.ts"
    content = state_path.read_text()
    assert "queuedMessages" in content, \
        "initialState must include queuedMessages field"


def test_finish_reason_queued_interrupt_defined():
    """The event types must include queued_message_interrupt finish reason."""
    event_path = Path(REPO) / "packages/agent-runtime/src/types/event.ts"
    content = event_path.read_text()
    assert "queued_message_interrupt" in content, \
        "Event types must define queued_message_interrupt finish reason"


def test_repo_eslint_operation_slice():
    """Repo's ESLint passes on operation slice directory (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
set -e
export PATH="/root/.bun/bin:$PATH"
apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null
curl -fsSL https://bun.sh/install | bash 2>&1 | tail -3
cd /workspace/lobe-chat
timeout 180 bun install --frozen-lockfile 2>&1 | tail -3
timeout 30 bunx eslint src/store/chat/slices/operation/ --quiet 2>&1
"""],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_eslint_chat_input():
    """Repo's ESLint passes on ChatInput component (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
set -e
export PATH="/root/.bun/bin:$PATH"
apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null
curl -fsSL https://bun.sh/install | bash 2>&1 | tail -3
cd /workspace/lobe-chat
timeout 180 bun install --frozen-lockfile 2>&1 | tail -3
timeout 30 bunx eslint src/features/Conversation/ChatInput/ --quiet 2>&1
"""],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"
