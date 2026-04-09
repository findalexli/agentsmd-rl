"""
Task: playwright-kill-all-command
Repo: microsoft/playwright @ 8710e613f8297cebe33c4f6a745999ab4e4907aa
PR:   39116

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a node script in the repo directory."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_kill_all_command_registered():
    """kill-all command is declared with declareCommand and registered in commandsArray."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright/src/mcp/terminal/commands.ts', 'utf-8');
const hasDeclaration = /const\\s+killAll\\s*=\\s*declareCommand/.test(content);
if (!hasDeclaration) { console.error('killAll not declared with declareCommand'); process.exit(1); }
const hasName = /name:\\s*'kill-all'/.test(content);
if (!hasName) { console.error('kill-all name not found'); process.exit(1); }
const afterArray = content.split('commandsArray')[1] || '';
if (!afterArray.includes('killAll')) { console.error('killAll not in commandsArray'); process.exit(1); }
console.log('OK');
""")
    assert r.returncode == 0, f"kill-all command not properly declared/registered: {r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_kill_all_daemons_implemented():
    """killAllDaemons function exists with platform-specific process killing logic."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf-8');
if (!content.includes('killAllDaemons')) { console.error('killAllDaemons missing'); process.exit(1); }
if (!content.includes('run-mcp-server')) { console.error('daemon pattern missing'); process.exit(1); }
if (!content.includes('--daemon-session')) { console.error('session pattern missing'); process.exit(1); }
if (!content.includes('SIGKILL')) { console.error('SIGKILL missing'); process.exit(1); }
if (!content.includes('win32')) { console.error('platform check missing'); process.exit(1); }
if (!content.includes('execSync')) { console.error('execSync missing'); process.exit(1); }
console.log('OK');
""")
    assert r.returncode == 0, f"killAllDaemons implementation incomplete: {r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_kill_all_routed():
    """program.ts routes kill-all command to the handler at both entry points."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf-8');
// Top-level routing
const hasTopLevel = content.includes("commandName === 'kill-all'");
if (!hasTopLevel) { console.error('top-level routing missing'); process.exit(1); }
// Subcommand routing
const hasSubcommand = content.includes("subcommand === 'kill-all'");
if (!hasSubcommand) { console.error('subcommand routing missing'); process.exit(1); }
console.log('OK');
""")
    assert r.returncode == 0, f"kill-all routing missing: {r.stderr}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — config/documentation update tests
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:29-30
def test_skill_md_documents_kill_all():
    """SKILL.md documents the kill-all command in the Sessions section."""
    skill_md = Path(f"{REPO}/packages/playwright/src/skill/SKILL.md")
    content = skill_md.read_text()
    assert "kill-all" in content, "SKILL.md should document the kill-all command"
    # Verify it appears with context about daemon/zombie processes
    lines = content.split("\n")
    kill_all_lines = [i for i, l in enumerate(lines) if "kill-all" in l]
    assert len(kill_all_lines) > 0, "kill-all should appear in SKILL.md"
    for idx in kill_all_lines:
        context = "\n".join(lines[max(0, idx - 3):idx + 3])
        if "daemon" in context.lower() or "zombie" in context.lower():
            return
    assert False, "kill-all should be documented with daemon/zombie context"


# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:29-30
def test_session_management_documents_kill_all():
    """session-management.md references kill-all with usage guidance for zombie processes."""
    ref_md = Path(f"{REPO}/packages/playwright/src/skill/references/session-management.md")
    content = ref_md.read_text()
    assert "kill-all" in content, "session-management.md should reference kill-all"
    assert "zombie" in content.lower() or "unresponsive" in content.lower() or "stale" in content.lower(), \
        "Should explain when to use kill-all (zombie/unresponsive/stale processes)"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_commands_file_valid():
    """commands.ts is syntactically balanced (brace matching)."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright/src/mcp/terminal/commands.ts', 'utf-8');
let depth = 0;
for (const ch of content) {
  if (ch === '{') depth++;
  if (ch === '}') depth--;
  if (depth < 0) { process.exit(1); }
}
if (depth !== 0) { process.exit(1); }
console.log('OK');
""")
    assert r.returncode == 0, "commands.ts has unbalanced braces"


# [repo_tests] pass_to_pass — CI/CD checks
# These tests verify the repo's own lint/build passes on both base and fixed commits

def test_repo_lint_packages():
    """Repo's workspace package consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\\n{r.stderr[-500:]}"


def test_repo_build():
    """Repo's build completes successfully (pass_to_pass)."""
    # First install dependencies (needed in fresh containers)
    install = subprocess.run(
        ["npm", "install"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert install.returncode == 0, f"npm install failed: {install.stderr[-500:]}"

    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"build failed:\\n{r.stderr[-500:]}"


def test_repo_commands_syntax():
    """commands.ts has valid Node.js syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "packages/playwright/src/mcp/terminal/commands.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"commands.ts syntax error: {r.stderr}"


def test_repo_program_syntax():
    """program.ts has valid Node.js syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "packages/playwright/src/mcp/terminal/program.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"program.ts syntax error: {r.stderr}"
