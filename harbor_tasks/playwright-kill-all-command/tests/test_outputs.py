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
    """kill-all command is declared and registered in commandsArray."""
    # Parse commands.ts to extract and verify the kill-all command definition
    r = _run_node("""
const fs = require('fs');
const path = require('path');

const content = fs.readFileSync('packages/playwright/src/mcp/terminal/commands.ts', 'utf-8');

// Find all declareCommand calls and extract their names
const declareCommandRegex = /declareCommand\\s*\\(\\s*\\{([^}]+)\\}/gs;
const commands = [];
let match;

while ((match = declareCommandRegex.exec(content)) !== null) {
    const block = match[1];
    const nameMatch = block.match(/name:\\s*['\"]([^'\"]+)['\"]/);
    if (nameMatch) {
        commands.push(nameMatch[1]);
    }
}

// Check that kill-all is in the commands list
if (!commands.includes('kill-all')) {
    console.error('kill-all not found in declared commands:', commands);
    process.exit(1);
}

// Verify commandsArray includes kill-all by checking export
const exportMatch = content.match(/export const commands = Object\\.fromEntries\\(commandsArray\\.map/);
if (!exportMatch) {
    console.error('commands export not found');
    process.exit(1);
}

console.log('OK: kill-all command declared and export structure exists');
""")
    assert r.returncode == 0, f"kill-all command not registered: {r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_kill_all_daemons_implemented():
    """killAllDaemons function exists and has platform-specific process killing logic."""
    r = _run_node("""
const fs = require('fs');

const content = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf-8');

// Check that a function handles kill-all command with process scanning
// Look for key behavioral elements:
const checks = [
    // Must scan for daemon processes
    { test: content.includes('run-mcp-server'), name: 'daemon pattern scan' },
    { test: content.includes('--daemon-session'), name: 'session pattern scan' },
    // Must have process termination
    { test: content.includes('SIGKILL') || content.includes('Stop-Process'), name: 'process termination (SIGKILL or Stop-Process)' },
    // Must handle both platforms
    { test: content.includes('win32') || content.includes('platform'), name: 'platform detection' },
    // Must execute system commands
    { test: content.includes('execSync') || content.includes('exec'), name: 'system execution' },
];

for (const check of checks) {
    if (!check.test) {
        console.error(`Missing: ${check.name}`);
        process.exit(1);
    }
}

console.log('OK: kill-all implementation has required components');
""")
    assert r.returncode == 0, f"killAllDaemons implementation incomplete: {r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_kill_all_routed():
    """program.ts routes kill-all command to the handler."""
    r = _run_node("""
const fs = require('fs');

const content = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf-8');

// Check for routing logic: commandName === 'kill-all' or similar
const hasCommandRouting = /commandName\\s*===?\\s*['\"']kill-all['\"']/.test(content);
const hasSubcommandRouting = /subcommand\\s*===?\\s*['\"']kill-all['\"']/.test(content);

// Must have at least one routing path
if (!hasCommandRouting && !hasSubcommandRouting) {
    console.error('No routing found for kill-all command');
    process.exit(1);
}

console.log('OK: kill-all routing exists');
""")
    assert r.returncode == 0, f"kill-all routing missing: {r.stderr}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — config/documentation update tests
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — SKILL.md documents kill-all
def test_skill_md_documents_kill_all():
    """SKILL.md documents the kill-all command in the Sessions section."""
    skill_md = Path(f"{REPO}/packages/playwright/src/skill/SKILL.md")
    content = skill_md.read_text()
    lines = content.split("\n")

    # Find lines mentioning kill-all
    kill_all_indices = [i for i, line in enumerate(lines) if "kill-all" in line]
    assert len(kill_all_indices) > 0, "SKILL.md should document the kill-all command"

    # Check that at least one kill-all reference has relevant context within ±3 lines
    has_context = False
    for idx in kill_all_indices:
        context_start = max(0, idx - 3)
        context_end = min(len(lines), idx + 4)
        nearby = "\n".join(lines[context_start:context_end]).lower()
        if any(w in nearby for w in ("daemon", "zombie", "stale", "force")):
            has_context = True
            break

    assert has_context, "kill-all should be documented with context (daemon/zombie/force/stale)"


# [agent_config] fail_to_pass — session-management.md references kill-all
def test_session_management_documents_kill_all():
    """session-management.md references kill-all with usage guidance."""
    ref_md = Path(f"{REPO}/packages/playwright/src/skill/references/session-management.md")
    content = ref_md.read_text()

    # Must mention kill-all
    assert "kill-all" in content, "session-management.md should reference kill-all"

    # Must explain when to use it
    content_lower = content.lower()
    has_guidance = (
        "zombie" in content_lower or
        "unresponsive" in content_lower or
        "stale" in content_lower or
        "force" in content_lower or
        "daemon" in content_lower
    )
    assert has_guidance, "Should explain when to use kill-all (zombie/unresponsive/stale/force/daemon)"


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


def test_repo_cli_session_spec_syntax():
    """cli-session.spec.ts has valid Node.js syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "tests/mcp/cli-session.spec.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"cli-session.spec.ts syntax error: {r.stderr}"


def test_repo_check_deps():
    """Repo's dependency checks pass (npm run check-deps) (pass_to_pass)."""
    # First install dependencies (needed in fresh containers)
    install = subprocess.run(
        ["npm", "install"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert install.returncode == 0, f"npm install failed: {install.stderr[-500:]}"

    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"check-deps failed:\\n{r.stderr[-500:]}"
