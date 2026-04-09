"""
Task: vscode-markdown-escape-fix
Repo: microsoft/vscode @ 33250873ecbd4047cd2e29b0f04ae0e7284aa342

Fix: Stop double-escaping markdown syntax in terminal run tool invocation
messages. The MarkdownString constructor already handles escaping, so
calling escapeMarkdownSyntaxTokens first causes double-escaping.

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TARGET = (
    f"{REPO}/src/vs/workbench/contrib/terminalContrib/"
    "chatAgentTools/browser/tools/runInTerminalTool.ts"
)


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


def test_no_double_escape_in_invocation():
    """Invocation messages must not double-escape markdown characters.

    Reads the source file, replicates the exact escapeMarkdownSyntaxTokens
    regex from htmlContent.ts, and verifies the code path does NOT apply it
    before MarkdownString (which would cause visible backslashes for
    underscores, asterisks, etc. in the chat UI).
    """
    r = _run_node(r"""
const fs = require('fs');

const src = fs.readFileSync(
  'src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts',
  'utf8'
);

// Exact regex from src/vs/base/common/htmlContent.ts
function escapeMarkdownSyntaxTokens(text) {
  return text.replace(/[\\`*_{}[\]()#+\-!~]/g, '\\$&');
}

// Test command with markdown-significant characters
const cmd = 'echo "hello_world" | grep *pattern*';

// Detect if the code creates escapedDisplayCommand
// (escapeMarkdownSyntaxTokens applied before MarkdownString -> double escape)
const hasEscapedVar = /const\s+escapedDisplayCommand\s*=\s*escapeMarkdownSyntaxTokens/.test(src);

if (hasEscapedVar) {
  const single = escapeMarkdownSyntaxTokens(cmd);
  const double = escapeMarkdownSyntaxTokens(single);
  console.error('FAIL: Code double-escapes markdown in invocation messages');
  console.error('  Input:         ' + cmd);
  console.error('  Single escape: ' + single);
  console.error('  Double escape: ' + double);
  process.exit(1);
}

// Verify localize calls use displayCommand, not escapedDisplayCommand
const lines = src.split('\n');
let count = 0;
for (const line of lines) {
  if (/localize\(['"]runInTerminal\.invocation/.test(line)) {
    count++;
    if (line.includes('escapedDisplayCommand')) {
      console.error('FAIL: localize still uses escapedDisplayCommand: ' + line.trim());
      process.exit(1);
    }
  }
}

if (count === 0) {
  console.error('FAIL: No runInTerminal.invocation localize calls found');
  process.exit(1);
}

console.log('PASS: ' + count + ' invocation messages use displayCommand directly');
""")
    assert r.returncode == 0, f"Double-escape detected:\n{r.stdout}\n{r.stderr}"


def test_escape_import_removed():
    """escapeMarkdownSyntaxTokens must not be imported (unused after fix)."""
    src = Path(TARGET).read_text()
    assert "escapeMarkdownSyntaxTokens" not in src, \
        "escapeMarkdownSyntaxTokens should be removed from imports"


def test_markdown_string_still_used():
    """MarkdownString must still be used for invocation messages."""
    src = Path(TARGET).read_text()
    assert "new MarkdownString" in src, \
        "MarkdownString should still be used for invocation messages"
