"""
Task: vscode-terminal-markdown-escape-fix
Repo: microsoft/vscode @ 891f5f2f96fe5161122912af25d8b3af708cbd1b
PR:   306535

Fix: Remove unnecessary markdown escaping in terminal invocation messages.
escapeMarkdownSyntaxTokens() was redundantly pre-escaping displayCommand before
passing it into MarkdownString via a localize template; the backtick code spans
already handle special characters correctly.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

CI-derived pass-to-pass gates:
- test_repo_eslint: Repo's ESLint checks pass
- test_repo_hygiene: Repo's hygiene checks pass
- test_repo_test_node: Repo's Node.js unit tests pass
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TARGET = Path(
    f"{REPO}/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts"
)


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file present + import structure intact
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists_and_has_imports():
    """Target file must exist and contain its htmlContent.js import."""
    assert TARGET.exists(), f"Target file not found: {TARGET}"
    content = TARGET.read_text()
    assert "htmlContent.js" in content, "htmlContent.js import missing from file"
    assert "MarkdownString" in content, "MarkdownString no longer present in file"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral changes via code execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_invocation_message_no_double_escape():
    """Simulate the invocation message pipeline: commands with markdown-special
    characters (underscores, asterisks) must NOT be double-escaped.

    Base: escapeMarkdownSyntaxTokens is called on displayCommand, so a command
    like 'npm_run_script' becomes 'npm\\_run\\_script' inside the code span.
    Fix: displayCommand is passed directly, so underscores render cleanly.
    """
    r = _run_node(r"""
import { readFileSync } from 'fs';

// escapeMarkdownSyntaxTokens from src/vs/base/common/htmlContent.ts:
//   text.replace(/[\\`*_{}[\]()#+\-!~]/g, '\\$&')
// Escapes markdown syntax chars with a preceding backslash.
function escapeMarkdownSyntaxTokens(text) {
    return text.replace(/[\\`*_{}\[\]()#+\-!~]/g, '\\$&');
}

// 2. Read the target file and find the invocation message section
const target = readFileSync(
    'src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts',
    'utf8'
);

// 3. Check which variable is used in the localize calls for invocation messages
const invocationLines = target.split('\n').filter(
    l => l.includes('localize(') && l.includes('runInTerminal.invocation')
);
const usesEscapedVar = invocationLines.some(l => l.includes('escapedDisplayCommand'));

// 4. Simulate the pipeline with a test command containing markdown chars
const testCommand = 'npm_run_my_script --flag=test_value';
const processed = usesEscapedVar
    ? escapeMarkdownSyntaxTokens(testCommand)
    : testCommand;

// 5. Construct the message like VS Code does: Running `{0}`
const message = `Running \`${processed}\``;

// 6. Check for double-escaping
if (message.includes('\\_') || message.includes('\\-')) {
    console.log('FAIL: Double-escaped markdown chars found: ' + message);
    process.exit(1);
}
if (!message.includes('npm_run_my_script')) {
    console.log('FAIL: Command not found in message: ' + message);
    process.exit(1);
}
console.log('PASS: Command renders cleanly: ' + message);
""")
    assert r.returncode == 0, (
        f"Invocation message double-escapes markdown characters:\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_escape_function_not_in_scope():
    """escapeMarkdownSyntaxTokens must not be imported or referenced in the target file.

    Base: the import line includes escapeMarkdownSyntaxTokens, and it's called.
    Fix: the import is removed and no references remain.

    Uses Node.js to parse the file and extract all import bindings from htmlContent.js.
    """
    r = _run_node(r"""
import { readFileSync } from 'fs';

const target = readFileSync(
    'src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts',
    'utf8'
);

// Find import lines from htmlContent.js
const importLines = target.split('\n').filter(
    l => l.includes('htmlContent.js') && l.trimStart().startsWith('import')
);

if (importLines.length === 0) {
    console.error('FAIL: No htmlContent.js import found at all');
    process.exit(1);
}

// Check each import line for the escape function
for (const line of importLines) {
    // Extract the import specifiers between { and }
    const specMatch = line.match(/\{([^}]+)\}/);
    if (specMatch) {
        const specifiers = specMatch[1].split(',').map(s => s.trim().replace(/^type\s+/, ''));
        if (specifiers.includes('escapeMarkdownSyntaxTokens')) {
            console.log('FAIL: escapeMarkdownSyntaxTokens is still imported: ' + line.trim());
            process.exit(1);
        }
    }
}

// Also verify no references to the function or its variable remain
const nonImportLines = target.split('\n').filter(
    l => !l.trimStart().startsWith('import')
);
const bodyText = nonImportLines.join('\n');
if (bodyText.includes('escapeMarkdownSyntaxTokens')) {
    console.log('FAIL: escapeMarkdownSyntaxTokens still referenced in file body');
    process.exit(1);
}
if (bodyText.includes('escapedDisplayCommand')) {
    console.log('FAIL: escapedDisplayCommand variable still present in file body');
    process.exit(1);
}

console.log('PASS: escapeMarkdownSyntaxTokens not imported or referenced');
""")
    assert r.returncode == 0, (
        f"escapeMarkdownSyntaxTokens still in scope:\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_all_localize_calls_use_display_command():
    """All 4 localize invocation calls must pass displayCommand (not escapedDisplayCommand).

    Uses Node.js to parse the target file, find all 4 localize calls for invocation
    messages, and verify each uses the correct variable.
    """
    r = _run_node(r"""
import { readFileSync } from 'fs';

const target = readFileSync(
    'src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts',
    'utf8'
);

const requiredKeys = [
    'runInTerminal.invocation.sandbox.background',
    'runInTerminal.invocation.sandbox',
    'runInTerminal.invocation.background',
    'runInTerminal.invocation',
];

// For each key, the final argument to the localize call must be 'displayCommand'
// (a bare identifier, not 'escapedDisplayCommand')
const errors = [];
for (const key of requiredKeys) {
    // Find lines containing this localize key
    // Use exact key match to avoid 'runInTerminal.invocation' matching the longer keys
    const keyPattern = `'${key}'`;
    const matchingLines = target.split('\n').filter(
        l => l.includes('localize(') && l.includes(keyPattern)
    );

    if (matchingLines.length === 0) {
        errors.push(`Localize call for '${key}' not found`);
        continue;
    }

    for (const line of matchingLines) {
        if (line.includes('escapedDisplayCommand')) {
            errors.push(`'${key}' still uses escapedDisplayCommand: ${line.trim()}`);
        } else if (!line.includes('displayCommand')) {
            errors.push(`'${key}' does not pass displayCommand: ${line.trim()}`);
        }
    }
}

if (errors.length > 0) {
    console.log('FAIL:\n' + errors.join('\n'));
    process.exit(1);
}
console.log('PASS: All 4 localize calls use displayCommand directly');
""")
    assert r.returncode == 0, (
        f"Localize calls not using displayCommand directly:\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: localization structure unchanged
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_localize_keys_preserved():
    """All 4 runInTerminal invocation localize message keys must still be present.

    The fix only removes the escape step; the message structure is unchanged.
    """
    content = TARGET.read_text()
    required_keys = [
        "runInTerminal.invocation.sandbox.background",
        "runInTerminal.invocation.sandbox",
        "runInTerminal.invocation.background",
        "runInTerminal.invocation",
    ]
    for key in required_keys:
        assert key in content, f"Required localize key missing: '{key}'"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rule from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:139 @ 891f5f2f96fe5161122912af25d8b3af708cbd1b
def test_no_blank_line_left_in_import_block():
    """No blank line left behind from import removal; import block must be compact.

    Rule: "When removing an import, do not leave behind blank lines where the
    import was. Ensure the surrounding code remains compact."
    (.github/copilot-instructions.md line 139)

    Concretely: the area between the 'event.js' import and the 'lifecycle.js'
    import must contain no blank lines.
    """
    lines = TARGET.read_text().splitlines()
    # Find the import block landmarks
    event_idx = next(
        (i for i, l in enumerate(lines) if "from '../../../../../../base/common/event.js'" in l),
        None,
    )
    lifecycle_idx = next(
        (i for i, l in enumerate(lines) if "from '../../../../../../base/common/lifecycle.js'" in l),
        None,
    )
    assert event_idx is not None, "event.js import not found"
    assert lifecycle_idx is not None, "lifecycle.js import not found"
    assert lifecycle_idx > event_idx, "Unexpected file structure"

    between = lines[event_idx + 1 : lifecycle_idx]
    blank_lines = [l for l in between if l.strip() == ""]
    assert len(blank_lines) == 0, (
        f"Blank line(s) found in import block between event.js and lifecycle.js: "
        f"{len(blank_lines)} blank line(s)"
    )


# ---------------------------------------------------------------------------
# CI-derived pass-to-pass gates — repo's CI/CD checks must pass
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass
def test_repo_eslint():
    """Repo ESLint checks pass (pass_to_pass).

    Verifies that the codebase passes the repository's ESLint configuration.
    This is a standard CI check from the VS Code repo's CI pipeline.
    """
    r = subprocess.run(
        ["npx", "eslint", "--no-error-on-unmatched-pattern", "src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_hygiene():
    """Repo's hygiene checks pass (pass_to_pass).

    Verifies that the codebase passes the repository's hygiene checks
    (copyright headers, file permissions, etc.).
    This is a standard CI check from the VS Code repo's CI pipeline.
    """
    r = subprocess.run(
        ["node", "build/hygiene.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Hygiene check failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_test_node():
    """Repo's Node.js unit tests pass (pass_to_pass).

    Verifies that the repository's Node.js unit tests pass.
    This is a standard CI check from the VS Code repo's CI pipeline.
    """
    r = subprocess.run(
        ["npm", "run", "test-node"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Node.js tests failed:\n{r.stderr[-500:]}"

