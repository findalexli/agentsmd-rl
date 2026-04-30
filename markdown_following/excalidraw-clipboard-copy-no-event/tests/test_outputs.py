"""Tests for clipboard.ts fix - behavioral verification.

These tests verify the fix by:
1. Behavioral execution with mocked browser APIs to verify fallback works
2. Structural analysis of control flow via Node.js brace-counting
3. Using prettier for syntax validation

The bug: copyTextToSystemClipboard returns early when no clipboardEvent is provided,
preventing the navigator.clipboard.writeText() fallback from executing.
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(os.environ.get("REPO_PATH", "/workspace/excalidraw"))
CLIPBOARD_TS = REPO / "packages" / "excalidraw" / "clipboard.ts"
BUTTON_SCSS = REPO / "packages" / "excalidraw" / "components" / "FilledButton.scss"


def _run_node(script: str) -> subprocess.CompletedProcess:
    """Write script to temp file and run with Node.js."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", delete=False
    ) as f:
        f.write(script)
        f.flush()
        try:
            return subprocess.run(
                ["node", f.name],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(REPO),
            )
        finally:
            Path(f.name).unlink(missing_ok=True)


def _flow_control_script() -> str:
    """Node.js script: structural flow-control analysis with brace-counting."""
    return (
        "const fs = require('fs');\n"
        "const content = fs.readFileSync('"
        + str(CLIPBOARD_TS).replace("\\", "\\\\")
        + "', 'utf8');\n"
        + r"""
const funcMatch = content.match(/export const copyTextToSystemClipboard = async[\s\S]*?^};/m);
if (!funcMatch) { console.error('FUNC_NOT_FOUND'); process.exit(1); }
const funcBody = funcMatch[0];

// === Check 1: No unconditional return in try block ===
const tryStart = funcBody.indexOf('try {');
if (tryStart === -1) { console.error('NO_TRY_BLOCK'); process.exit(1); }

// Brace-counting to find try body
let depth = 0;
let tryBodyStart = -1;
let tryBodyEnd = -1;
for (let i = tryStart; i < funcBody.length; i++) {
    if (funcBody[i] === '{') {
        if (depth === 0) tryBodyStart = i + 1;
        depth++;
    }
    if (funcBody[i] === '}') {
        depth--;
        if (depth === 0) { tryBodyEnd = i; break; }
    }
}
const tryBody = funcBody.substring(tryBodyStart, tryBodyEnd);

// Find if (clipboardEvent) { ... } using brace counting
const ifIdx = tryBody.indexOf('if (clipboardEvent)');
if (ifIdx === -1) { console.error('NO_IF_CLIPBOARDEVENT'); process.exit(1); }
const ifBraceStart = tryBody.indexOf('{', ifIdx);
depth = 0;
let ifBodyEnd = -1;
for (let i = ifBraceStart; i < tryBody.length; i++) {
    if (tryBody[i] === '{') depth++;
    if (tryBody[i] === '}') {
        depth--;
        if (depth === 0) { ifBodyEnd = i; break; }
    }
}

// Text after the if block within tryBody — check for stray return
const afterIf = tryBody.substring(ifBodyEnd + 1).trim();
const hasUnconditionalReturn = /^return\s*;/.test(afterIf);

if (hasUnconditionalReturn) {
    console.log('HAS_UNCONDITIONAL_RETURN');
} else {
    console.log('NO_UNCONDITIONAL_RETURN');
}

// === Check 2: Return after navigator.clipboard.writeText ===
const writeTextReturn = /await\s+navigator\.clipboard\.writeText\([^)]*\)\s*;[\s\S]*?return\s*;/;
if (writeTextReturn.test(funcBody)) {
    console.log('HAS_RETURN_AFTER_WRITETEXT');
} else {
    console.log('MISSING_RETURN_AFTER_WRITETEXT');
}

if (hasUnconditionalReturn || !writeTextReturn.test(funcBody)) {
    process.exit(1);
}
"""
    )


def _behavioral_script() -> str:
    """Node.js script: extract function, strip types, mock globals, execute."""
    return (
        "const fs = require('fs');\n"
        "const path = require('path');\n"
        "const os = require('os');\n"
        "const content = fs.readFileSync('"
        + str(CLIPBOARD_TS).replace("\\", "\\\\")
        + "', 'utf8');\n"
        + r"""
const funcMatch = content.match(/export const copyTextToSystemClipboard = async[\s\S]*?^};/m);
if (!funcMatch) { console.error('FUNC_NOT_FOUND'); process.exit(1); }

let func = funcMatch[0];

// Strip TypeScript type annotations to make valid JavaScript
func = func.replace('export const', 'const');
func = func.replace(/<\s*\n?\s*MimeType[\s\S]*?>\s*\(/s, '(');
func = func.replace(/text\s*:\s*string[^,]*,/s, 'text,');
func = func.replace(/clipboardEvent\??\s*:\s*ClipboardEvent[^,)]*,?/s, 'clipboardEvent,');
func = func.replace(/error\s*:\s*any/g, 'error');

const testCode = `
const MIME_TYPES = { text: 'text/plain' };
let _writeTextCalled = false;
let _writeTextValue = null;
const probablySupportsClipboardWriteText = true;
const navigator = {
  clipboard: { writeText: async (val) => { _writeTextCalled = true; _writeTextValue = val; } }
};
const copyTextViaExecCommand = () => true;

${func}

(async () => {
  try {
    await copyTextToSystemClipboard("hello world", null);
    if (_writeTextCalled) console.log('WRITETEXT_CALLED');
    else { console.log('WRITETEXT_NOT_CALLED'); process.exit(1); }
    if (_writeTextValue === 'hello world') console.log('CORRECT_VALUE');
    else { console.log('WRONG_VALUE:' + _writeTextValue); process.exit(1); }
  } catch(e) {
    console.error('EXEC_ERROR:' + e.message);
    process.exit(1);
  }
})();
`;

const tmpFile = path.join(os.tmpdir(), '_behavioral_test_' + process.pid + '.js');
fs.writeFileSync(tmpFile, testCode);

const { execSync } = require('child_process');
try {
    const output = execSync('node ' + tmpFile, { encoding: 'utf8', timeout: 10000 });
    process.stdout.write(output);
} catch(e) {
    process.stderr.write(e.stderr || e.message || 'unknown error');
    process.exit(1);
} finally {
    try { fs.unlinkSync(tmpFile); } catch(x) {}
}
"""
    )


def test_clipboard_flow_control():
    """Test that return is correctly scoped inside if(clipboardEvent), not at try-block level.

    Uses brace-counting analysis to verify:
    - No unconditional return between if(clipboardEvent) block and catch
    - A return exists after navigator.clipboard.writeText succeeds
    """
    r = _run_node(_flow_control_script())
    assert r.returncode == 0, f"Flow control check failed: {r.stderr}"
    assert "NO_UNCONDITIONAL_RETURN" in r.stdout, \
        "Unconditional return found between if(clipboardEvent) and catch"
    assert "HAS_RETURN_AFTER_WRITETEXT" in r.stdout, \
        "Missing return after navigator.clipboard.writeText"


def test_plain_text_const():
    """Test that plainTextEntry is declared as const, not let."""
    content = CLIPBOARD_TS.read_text()
    func_match = re.search(
        r'export const copyTextToSystemClipboard = async[\s\S]*?^};',
        content,
        re.MULTILINE,
    )
    assert func_match, "copyTextToSystemClipboard function not found"

    func_body = func_match.group(0)
    assert re.search(r'\bconst\s+plainTextEntry\b', func_body), \
        "plainTextEntry should be declared as const"
    assert not re.search(r'\blet\s+plainTextEntry\b', func_body), \
        "plainTextEntry should not be declared as let"


def test_no_redundant_undefined():
    """Test that plainTextEntry is not set to undefined after writeText."""
    content = CLIPBOARD_TS.read_text()
    func_match = re.search(
        r'export const copyTextToSystemClipboard = async[\s\S]*?^};',
        content,
        re.MULTILINE,
    )
    assert func_match, "copyTextToSystemClipboard function not found"

    func_body = func_match.group(0)
    assert "plainTextEntry = undefined" not in func_body, \
        "plainTextEntry should not be set to undefined - use return instead"
    assert "plainTextEntry = void 0" not in func_body, \
        "plainTextEntry should not be nullified"


def test_scss_success_color():
    """Test that FilledButton.scss includes background-color for success state."""
    content = BUTTON_SCSS.read_text()

    pattern = r'&\.ExcButton--status-loading,\s*&\.ExcButton--status-success\s*\{[^}]*background-color:\s*var\(--color-success\)'
    assert re.search(pattern, content, re.DOTALL), \
        "FilledButton.scss should have background-color: var(--color-success) for loading/success states"


def test_clipboard_fallback_behavior():
    """Behavioral test: when clipboardEvent is null, the function must call writeText.

    Extracts the function from clipboard.ts, strips TypeScript annotations,
    mocks browser APIs (navigator.clipboard, etc.), executes with null clipboardEvent,
    and verifies that navigator.clipboard.writeText is called with the correct value.
    """
    r = _run_node(_behavioral_script())
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}"
    assert "WRITETEXT_CALLED" in r.stdout, \
        "writeText was not called when clipboardEvent is null"
    assert "CORRECT_VALUE" in r.stdout, \
        "writeText was called with incorrect value"


# =============================================================================
# Pass-to-Pass Tests - Repo CI/CD Checks
# These ensure the fix doesn't break existing functionality
# =============================================================================


def test_repo_clipboard_ts_syntax():
    """Repo's clipboard.ts has valid TypeScript syntax (pass_to_pass).

    Uses prettier --parser typescript to validate the file can be parsed.
    """
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "typescript", str(CLIPBOARD_TS)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, "clipboard.ts has TypeScript syntax errors"


def test_repo_clipboard_test_ts_syntax():
    """Repo's clipboard.test.ts has valid TypeScript syntax (pass_to_pass).

    Uses prettier --parser typescript to validate test file syntax.
    """
    test_file = REPO / "packages" / "excalidraw" / "clipboard.test.ts"
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "typescript", str(test_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, "clipboard.test.ts has TypeScript syntax errors"


def test_repo_filledbutton_scss_syntax():
    """Repo's FilledButton.scss has valid SCSS syntax (pass_to_pass).

    Uses prettier --parser scss to validate the file can be parsed.
    """
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "scss", str(BUTTON_SCSS)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, "FilledButton.scss has SCSS syntax errors"


def test_repo_charts_test_syntax():
    """Repo's charts.test.ts has valid TypeScript syntax (pass_to_pass).

    Uses prettier --parser typescript to validate the test file syntax.
    """
    test_file = REPO / "packages" / "excalidraw" / "charts.test.ts"
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "typescript", str(test_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, "charts.test.ts has TypeScript syntax errors"


def test_repo_utils_test_syntax():
    """Repo's utils.test.ts has valid TypeScript syntax (pass_to_pass).

    Uses prettier --parser typescript to validate the test file syntax.
    """
    test_file = REPO / "packages" / "common" / "src" / "utils.test.ts"
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "typescript", str(test_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, "utils.test.ts has TypeScript syntax errors"


def test_repo_constants_ts_syntax():
    """Repo's constants.ts has valid TypeScript syntax (pass_to_pass).

    The constants.ts file must be syntactically valid TypeScript.
    Uses prettier to validate without requiring full type check.
    """
    constants_file = REPO / "packages" / "common" / "src" / "constants.ts"
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "typescript", str(constants_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, "constants.ts has TypeScript syntax errors"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
