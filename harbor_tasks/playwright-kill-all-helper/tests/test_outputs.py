"""
Tests for playwright kill-all CLI command task.

This task tests both:
1. Code changes: Adding kill-all command implementation (behavioral AST tests)
2. Config changes: Updating SKILL.md and session-management.md documentation
"""

import subprocess
import json
from pathlib import Path

REPO = Path("/workspace/playwright")


def _node_eval(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a Node.js script in the repo directory."""
    return subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_kill_all_command_registered():
    """killAll command must be declared and registered in commands.ts (verified via TypeScript AST)."""
    r = _node_eval("""
const ts = require('typescript');
const fs = require('fs');
const source = fs.readFileSync('packages/playwright/src/mcp/terminal/commands.ts', 'utf-8');
const sf = ts.createSourceFile('commands.ts', source, ts.ScriptTarget.Latest, true);

let foundDecl = false;
let declProps = {};
let foundInArray = false;

function visit(node) {
    // Find: const killAll = declareCommand({ ... })
    if (ts.isVariableDeclaration(node) && node.name.getText(sf) === 'killAll') {
        foundDecl = true;
        // Extract properties from the object literal argument
        if (node.initializer && ts.isCallExpression(node.initializer)) {
            const arg = node.initializer.arguments[0];
            if (arg && ts.isObjectLiteralExpression(arg)) {
                for (const prop of arg.properties) {
                    if (ts.isPropertyAssignment(prop)) {
                        const key = prop.name.getText(sf);
                        if (ts.isStringLiteral(prop.initializer)) {
                            declProps[key] = prop.initializer.text;
                        }
                    }
                }
            }
        }
    }
    // Find killAll in the commandsArray
    if (ts.isArrayLiteralExpression(node)) {
        for (const elem of node.elements) {
            if (ts.isIdentifier(elem) && elem.text === 'killAll') {
                foundInArray = true;
            }
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

const result = { foundDecl, declProps, foundInArray };
console.log(JSON.stringify(result));

if (!foundDecl) { console.error('killAll variable declaration not found'); process.exit(1); }
if (declProps.name !== 'kill-all') { console.error('Expected name kill-all, got: ' + declProps.name); process.exit(1); }
if (declProps.category !== 'session') { console.error('Expected category session, got: ' + declProps.category); process.exit(1); }
if (!declProps.description || !declProps.description.includes('Forcefully kill all daemon processes')) {
    console.error('Description mismatch: ' + declProps.description); process.exit(1);
}
if (!foundInArray) { console.error('killAll not found in commandsArray'); process.exit(1); }
console.log('PASS');
""")
    assert r.returncode == 0, f"AST check failed:\n{r.stdout}\n{r.stderr}"
    data = json.loads(r.stdout.strip().split("\n")[0])
    assert data["foundDecl"], "killAll declaration not found in AST"
    assert data["foundInArray"], "killAll not in commandsArray"
    assert data["declProps"]["name"] == "kill-all"
    assert data["declProps"]["category"] == "session"


def test_kill_all_implemented_in_program():
    """killAllDaemons function must be implemented in program.ts with cross-platform support (verified via AST)."""
    r = _node_eval("""
const ts = require('typescript');
const fs = require('fs');
const source = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf-8');
const sf = ts.createSourceFile('program.ts', source, ts.ScriptTarget.Latest, true);

let foundFunc = false;
let foundExecSync = false;
let foundPlatformCheck = false;
let foundRunMcpServer = false;
let foundDaemonSession = false;
let foundKillAllRoute = false;

function visit(node) {
    // killAllDaemons function declaration
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'killAllDaemons') {
        foundFunc = true;
    }
    // execSync import
    if (ts.isImportDeclaration(node)) {
        const text = node.getText(sf);
        if (text.includes('execSync')) foundExecSync = true;
    }
    // Platform check: 'win32'
    if (ts.isStringLiteral(node) && node.text === 'win32') {
        foundPlatformCheck = true;
    }
    // Daemon detection patterns
    if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) {
        const val = node.text || '';
        if (val.includes('run-mcp-server')) foundRunMcpServer = true;
        if (val.includes('daemon-session')) foundDaemonSession = true;
    }
    // Route: subcommand === 'kill-all'
    if (ts.isStringLiteral(node) && node.text === 'kill-all') {
        foundKillAllRoute = true;
    }
    ts.forEachChild(node, visit);
}
visit(sf);

const result = { foundFunc, foundExecSync, foundPlatformCheck, foundRunMcpServer, foundDaemonSession, foundKillAllRoute };
console.log(JSON.stringify(result));

if (!foundFunc) { console.error('killAllDaemons function not found'); process.exit(1); }
if (!foundExecSync) { console.error('execSync not imported'); process.exit(1); }
if (!foundPlatformCheck) { console.error('win32 platform check not found'); process.exit(1); }
if (!foundRunMcpServer) { console.error('run-mcp-server pattern not found'); process.exit(1); }
if (!foundDaemonSession) { console.error('daemon-session pattern not found'); process.exit(1); }
if (!foundKillAllRoute) { console.error('kill-all route not found'); process.exit(1); }
console.log('PASS');
""")
    assert r.returncode == 0, f"AST check failed:\n{r.stdout}\n{r.stderr}"
    data = json.loads(r.stdout.strip().split("\n")[0])
    assert data["foundFunc"], "killAllDaemons function not found"
    assert data["foundExecSync"], "execSync not imported"
    assert data["foundPlatformCheck"], "Platform-specific handling (win32) not found"
    assert data["foundRunMcpServer"], "run-mcp-server detection pattern not found"
    assert data["foundDaemonSession"], "daemon-session detection pattern not found"
    assert data["foundKillAllRoute"], "kill-all subcommand route not found"


def test_skill_md_documents_kill_all():
    """SKILL.md must document the kill-all command in the Sessions section."""
    skill_path = REPO / "packages/playwright/src/skill/SKILL.md"
    content = skill_path.read_text()

    # Check kill-all is documented in the sessions section
    session_section = content.find("### Sessions")
    assert session_section != -1, "Sessions section not found in SKILL.md"

    session_content = content[session_section:session_section + 1500]
    assert "kill-all" in session_content, "kill-all not documented in Sessions section"

    # Check it mentions daemon processes
    assert "daemon" in content.lower() or "zombie" in content.lower() or "stale" in content.lower(), \
        "kill-all documentation should mention daemon/zombie/stale processes"


def test_session_management_md_documents_kill_all():
    """session-management.md reference must document kill-all usage."""
    ref_path = REPO / "packages/playwright/src/skill/references/session-management.md"
    content = ref_path.read_text()

    # Check kill-all is documented
    assert "kill-all" in content, "kill-all not documented in session-management.md"

    # Check it appears with the CLI prefix
    assert "playwright-cli kill-all" in content, "kill-all command example not found"

    # Check it mentions the use case (zombie/stale processes)
    assert any(phrase in content.lower() for phrase in ["zombie", "stale", "unresponsive", "forcefully"]), \
        "kill-all documentation should explain when to use it (zombie/stale/unresponsive processes)"


def test_skill_md_follows_existing_format():
    """SKILL.md kill-all entry must follow the same format as other session commands."""
    skill_path = REPO / "packages/playwright/src/skill/SKILL.md"
    content = skill_path.read_text()

    # Find the Sessions code block
    lines = content.split('\n')
    in_sessions_block = False
    session_commands = []

    for line in lines:
        if 'playwright-cli session-list' in line or 'playwright-cli session-stop' in line:
            in_sessions_block = True
        if in_sessions_block:
            if line.strip().startswith('playwright-cli'):
                session_commands.append(line.strip())
            if line.strip() == '```':
                break

    # Check kill-all follows the same pattern
    kill_all_lines = [cmd for cmd in session_commands if 'kill-all' in cmd]
    assert len(kill_all_lines) > 0, "kill-all not found in session commands block"

    for cmd in kill_all_lines:
        assert cmd.startswith('playwright-cli kill-all'), \
            f"kill-all command format incorrect: {cmd}"


def test_session_management_includes_use_case():
    """session-management.md must include specific use case for kill-all."""
    ref_path = REPO / "packages/playwright/src/skill/references/session-management.md"
    content = ref_path.read_text()

    lines = content.split('\n')

    # Find line with kill-all and check context
    for i, line in enumerate(lines):
        if 'kill-all' in line and 'playwright-cli' in line:
            # Check surrounding context
            context_start = max(0, i - 3)
            context = '\n'.join(lines[context_start:i])

            has_context = any(phrase in context.lower() for phrase in [
                'if', 'when', 'zombie', 'stale', 'unresponsive', 'remain', 'force'
            ])
            assert has_context, "kill-all should have explanatory context about when to use it"
            break
    else:
        assert False, "kill-all command not found in session-management.md"
