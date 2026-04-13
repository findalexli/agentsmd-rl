"""
Task: playwright-chorecli-session-b
Repo: microsoft/playwright @ 605d93d732c5ab752ae314ac47fdd6ad3abc11de
PR:   39156

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
COMMAND_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/command.ts"
COMMANDS_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts"
HELP_GEN_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/helpGenerator.ts"
PROGRAM_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/skill/SKILL.md"
SESSION_MGMT_MD = Path(REPO) / "packages/playwright/src/skill/references/session-management.md"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a JavaScript snippet via Node in the repo directory."""
    tmp = Path(REPO) / "_eval_check.mjs"
    tmp.write_text(script)
    try:
        return subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files have balanced braces."""
    for ts_file in [COMMAND_TS, COMMANDS_TS, HELP_GEN_TS, PROGRAM_TS]:
        content = ts_file.read_text()
        assert content.count("{") == content.count("}"), \
            f"Unbalanced braces in {ts_file.name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node execution
# ---------------------------------------------------------------------------

def test_command_names_renamed():
    """Session commands renamed: session-list -> list, session-close-all -> close-all, session-kill-all -> kill-all."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright/src/mcp/terminal/commands.ts', 'utf8');

// Extract command names from all declareCommand calls
const names = [...src.matchAll(/declareCommand\\(\\{[\\s\\S]*?name:\\s*['\"]([^'\"]+)['\"]/g)].map(m => m[1]);

const required = ['list', 'close-all', 'kill-all'];
const missing = required.filter(c => !names.includes(c));
if (missing.length > 0) {
    console.error(JSON.stringify({ error: 'missing_commands', missing, found: names }));
    process.exit(1);
}

const forbidden = ['session-list', 'session-close-all', 'session-kill-all'];
const present = forbidden.filter(c => names.includes(c));
if (present.length > 0) {
    console.error(JSON.stringify({ error: 'old_commands_still_present', present }));
    process.exit(1);
}

console.log(JSON.stringify({ status: 'ok', commands: names }));
""")
    assert r.returncode == 0, f"Command name check failed: {r.stderr or r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data["status"] == "ok"


def test_category_renamed_to_browsers():
    """Category 'session' renamed to 'browsers' in command.ts type and commands.ts usage."""
    r = _run_node("""
import { readFileSync } from 'fs';
const cmdTs = readFileSync('packages/playwright/src/mcp/terminal/command.ts', 'utf8');
const cmdsTs = readFileSync('packages/playwright/src/mcp/terminal/commands.ts', 'utf8');

// Check Category type union
const typeMatch = cmdTs.match(/type\\s+Category\\s*=\\s*([^;]+)/);
if (!typeMatch) {
    console.error(JSON.stringify({ error: 'category_type_not_found' }));
    process.exit(1);
}
const typeStr = typeMatch[1];
if (!typeStr.includes("'browsers'")) {
    console.error(JSON.stringify({ error: 'browsers_missing_from_type', typeStr }));
    process.exit(1);
}
if (typeStr.includes("'session'")) {
    console.error(JSON.stringify({ error: 'session_still_in_type', typeStr }));
    process.exit(1);
}

// Check category assignments in commands
const cats = [...cmdsTs.matchAll(/category:\\s*['\"]([^'\"]+)['\"]/g)].map(m => m[1]);
if (cats.includes('session')) {
    console.error(JSON.stringify({ error: 'session_category_in_commands' }));
    process.exit(1);
}
if (!cats.includes('browsers')) {
    console.error(JSON.stringify({ error: 'browsers_category_missing' }));
    process.exit(1);
}

console.log(JSON.stringify({ status: 'ok', categories: [...new Set(cats)] }));
""")
    assert r.returncode == 0, f"Category check failed: {r.stderr or r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data["status"] == "ok"
    assert "browsers" in data["categories"]


def test_program_switch_uses_new_names():
    """program.ts switch dispatches 'list', 'close-all', 'kill-all'."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');

const cases = [...src.matchAll(/case\\s+['\"]([^'\"]+)['\"]/g)].map(m => m[1]);

const required = ['list', 'close-all', 'kill-all'];
const missing = required.filter(c => !cases.includes(c));
if (missing.length > 0) {
    console.error(JSON.stringify({ error: 'missing_switch_cases', missing, found: cases }));
    process.exit(1);
}

const forbidden = ['session-list', 'session-close-all', 'session-kill-all'];
const present = forbidden.filter(c => cases.includes(c));
if (present.length > 0) {
    console.error(JSON.stringify({ error: 'old_cases_present', present }));
    process.exit(1);
}

console.log(JSON.stringify({ status: 'ok', cases }));
""")
    assert r.returncode == 0, f"Switch case check failed: {r.stderr or r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data["status"] == "ok"


def test_b_flag_alias():
    """program.ts normalizes -b flag to --session by extracting and executing the normalization code."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');

// Extract the if (args.b) { ... } normalization block
const match = src.match(/if\\s*\\(\\s*args\\.b\\s*\\)\\s*\\{([\\s\\S]*?)\\}/);
if (!match) {
    console.error(JSON.stringify({ error: 'no_b_flag_block' }));
    process.exit(1);
}

// Execute the extracted code against test data
const args = { b: 'testbrowser', _: ['open'] };
const fn = new Function('args', match[1]);
fn(args);

if (args.session !== 'testbrowser') {
    console.error(JSON.stringify({ error: 'session_not_set', args }));
    process.exit(1);
}
if (args.b !== undefined) {
    console.error(JSON.stringify({ error: 'b_not_deleted', args }));
    process.exit(1);
}

console.log(JSON.stringify({ status: 'ok', session: args.session }));
""")
    assert r.returncode == 0, f"-b flag check failed: {r.stderr or r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data["status"] == "ok"
    assert data["session"] == "testbrowser"


def test_user_messages_say_browser():
    """User-facing messages say 'Browser' instead of 'Session' in program.ts."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');

// Old pattern: "Session '" appears in template literals for user messages
// e.g. `Session '${this.name}' is not running.`
if (src.includes("Session '")) {
    console.error(JSON.stringify({ error: 'old_Session_quote_pattern' }));
    process.exit(1);
}

// Must have Browser messages
if (!src.includes("Browser '")) {
    console.error(JSON.stringify({ error: 'no_Browser_messages' }));
    process.exit(1);
}

// List header: 'Sessions:' -> 'Browsers:'
if (src.includes("'Sessions:'")) {
    console.error(JSON.stringify({ error: 'old_Sessions_header' }));
    process.exit(1);
}

console.log(JSON.stringify({ status: 'ok' }));
""")
    assert r.returncode == 0, f"User message check failed: {r.stderr or r.stdout}"


def test_status_markers_open_closed():
    """Status markers use [open]/[closed] instead of [running]/[stopped]."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');

if (!src.includes("'[open]'") || !src.includes("'[closed]'")) {
    console.error(JSON.stringify({ error: 'missing_new_markers' }));
    process.exit(1);
}
if (src.includes("'[running]'") || src.includes("'[stopped]'")) {
    console.error(JSON.stringify({ error: 'old_markers_present' }));
    process.exit(1);
}

console.log(JSON.stringify({ status: 'ok' }));
""")
    assert r.returncode == 0, f"Status marker check failed: {r.stderr or r.stdout}"


def test_session_mgmt_md_heading_updated():
    """session-management.md heading mentions 'Browser'."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright/src/skill/references/session-management.md', 'utf8');
const firstLine = src.trim().split('\\n')[0].toLowerCase();
if (!firstLine.includes('browser')) {
    console.error(JSON.stringify({ error: 'heading_missing_browser', firstLine }));
    process.exit(1);
}
console.log(JSON.stringify({ status: 'ok', firstLine }));
""")
    assert r.returncode == 0, f"Heading check failed: {r.stderr or r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — documentation updates
# ---------------------------------------------------------------------------

def test_skill_md_uses_new_commands():
    """SKILL.md documents -b flag and new command names."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright/src/skill/SKILL.md', 'utf8');

const required = ['-b ', 'playwright-cli list', 'playwright-cli close-all', 'playwright-cli kill-all'];
const missing = required.filter(p => !src.includes(p));
if (missing.length > 0) {
    console.error(JSON.stringify({ error: 'missing_in_skill_md', missing }));
    process.exit(1);
}

const forbidden = ['session-list', 'session-close-all', 'session-kill-all'];
const present = forbidden.filter(p => src.includes(p));
if (present.length > 0) {
    console.error(JSON.stringify({ error: 'old_commands_in_skill_md', present }));
    process.exit(1);
}

console.log(JSON.stringify({ status: 'ok' }));
""")
    assert r.returncode == 0, f"SKILL.md check failed: {r.stderr or r.stdout}"


def test_session_mgmt_md_uses_b_flag():
    """session-management.md uses -b flag and new command names."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright/src/skill/references/session-management.md', 'utf8');

if (!src.includes('-b ')) {
    console.error(JSON.stringify({ error: 'missing_b_flag' }));
    process.exit(1);
}
if (src.includes('--session')) {
    console.error(JSON.stringify({ error: 'old_session_flag' }));
    process.exit(1);
}

const required = ['playwright-cli list', 'close-all', 'kill-all'];
const missing = required.filter(p => !src.includes(p));
if (missing.length > 0) {
    console.error(JSON.stringify({ error: 'missing_commands', missing }));
    process.exit(1);
}

console.log(JSON.stringify({ status: 'ok' }));
""")
    assert r.returncode == 0, f"session-management.md check failed: {r.stderr or r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

def test_program_still_handles_open_close():
    """program.ts must still handle 'open' and 'close' commands."""
    content = PROGRAM_TS.read_text()
    assert "case 'open'" in content, "program.ts must handle 'open' command"
    assert "case 'close'" in content, "program.ts must handle 'close' command"
    assert "case 'delete-data'" in content, "program.ts must handle 'delete-data' command"


def test_modified_typescript_files_have_balanced_braces():
    """Modified TypeScript files have balanced braces (static)."""
    for ts_file in [COMMAND_TS, COMMANDS_TS, HELP_GEN_TS, PROGRAM_TS]:
        content = ts_file.read_text()
        open_count = content.count('{')
        close_count = content.count('}')
        assert open_count == close_count, f"{ts_file.name}: Unbalanced braces ({open_count} open, {close_count} close)"


def test_modified_typescript_files_have_balanced_parentheses():
    """Modified TypeScript files have balanced parentheses (static)."""
    for ts_file in [COMMAND_TS, COMMANDS_TS, HELP_GEN_TS, PROGRAM_TS]:
        content = ts_file.read_text()
        open_count = content.count('(')
        close_count = content.count(')')
        assert open_count == close_count, f"{ts_file.name}: Unbalanced parentheses ({open_count} open, {close_count} close)"


def test_skill_documentation_files_exist():
    """SKILL.md and session-management.md exist and are non-empty (static)."""
    assert SKILL_MD.exists(), 'SKILL.md must exist'
    assert SKILL_MD.stat().st_size > 0, 'SKILL.md must not be empty'
    assert SESSION_MGMT_MD.exists(), 'session-management.md must exist'
    assert SESSION_MGMT_MD.stat().st_size > 0, 'session-management.md must not be empty'


def test_command_ts_has_category_type():
    """command.ts defines Category type (static)."""
    content = COMMAND_TS.read_text()
    assert 'type Category' in content, 'command.ts must define Category type'


def test_commands_ts_has_declare_command():
    """commands.ts uses declareCommand (static)."""
    content = COMMANDS_TS.read_text()
    assert 'declareCommand' in content, 'commands.ts must use declareCommand'


def test_program_ts_has_switch_structure():
    """program.ts has command dispatch switch (static)."""
    content = PROGRAM_TS.read_text()
    assert 'switch(commandName)' in content or 'switch (commandName)' in content, 'program.ts must have command dispatch switch statement'


def test_help_generator_has_categories():
    """helpGenerator.ts defines categories array (static)."""
    content = HELP_GEN_TS.read_text()
    assert 'categories' in content, 'helpGenerator.ts must define categories'


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD validation
# These tests validate the repo's structural integrity passes on both
# the base commit AND after the gold fix is applied.
# ---------------------------------------------------------------------------

def test_repo_npm_run_build():
    """Repo CI check: npm run build succeeds (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"npm run build failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_npm_run_eslint():
    """Repo CI check: npm run eslint passes on terminal files (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "packages/playwright/src/mcp/terminal/*.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_npm_run_check_deps():
    """Repo CI check: npm run check-deps passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"check-deps failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_npm_run_lint_packages():
    """Repo CI check: npm run lint-packages passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_npx_eslint_modified_files():
    """Repo CI check: npx eslint passes on modified terminal files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "--no-cache",
         "packages/playwright/src/mcp/terminal/command.ts",
         "packages/playwright/src/mcp/terminal/commands.ts",
         "packages/playwright/src/mcp/terminal/helpGenerator.ts",
         "packages/playwright/src/mcp/terminal/program.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint on modified files failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
