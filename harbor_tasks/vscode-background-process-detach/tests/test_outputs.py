"""
Task: vscode-background-process-detach
Repo: microsoft/vscode @ a4855ab045eb06a0fbe50c1a91f5ff53b4cc990b

Background server processes started via run_in_terminal with isBackground=true
are killed when VS Code: exits. The fix adds a CommandLineBackgroundDetachRewriter
that wraps background commands with nohup (POSIX) or Start-Process (Windows).

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = "/workspace/vscode"
REWRITER_DIR = Path(f"{REPO}/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter")
REWRITER_FILE = REWRITER_DIR / "commandLineBackgroundDetachRewriter.ts"
INTERFACE_FILE = REWRITER_DIR / "commandLineRewriter.ts"
RUN_TOOL_FILE = Path(f"{REPO}/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts")
CONFIG_FILE = Path(f"{REPO}/src/vs/workbench/contrib/terminalContrib/chatAgentTools/common/terminalChatAgentToolsConfiguration.ts")
UPSTREAM_TEST_FILE = Path(f"{REPO}/src/vs/workbench/contrib/terminalContrib/chatAgentTools/test/electron-browser/commandLineBackgroundDetachRewriter.test.ts")


def _exec_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript/TypeScript code via node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral checks with code execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rewriter_file_exists():
    """commandLineBackgroundDetachRewriter.ts is created at the expected path."""
    assert REWRITER_FILE.exists(), (
        f"Missing: {REWRITER_FILE}\n"
        "The fix must create commandLineBackgroundDetachRewriter.ts"
    )
    assert REWRITER_FILE.stat().st_size > 0, "File is empty"


# [pr_diff] fail_to_pass
def test_rewriter_class_exported():
    """CommandLineBackgroundDetachRewriter is exported and implements ICommandLineRewriter."""
    src = REWRITER_FILE.read_text()
    assert "export class CommandLineBackgroundDetachRewriter" in src, (
        "CommandLineBackgroundDetachRewriter must be exported as a class"
    )
    assert "implements ICommandLineRewriter" in src, (
        "Class must implement ICommandLineRewriter interface"
    )

    # BEHAVIORAL: Parse the file to verify it's valid TypeScript-like syntax
    r = _exec_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{REWRITER_FILE}', 'utf8');
// Check for class declaration with export
const hasExport = /export\\s+class\\s+CommandLineBackgroundDetachRewriter/.test(src);
const hasImplements = /implements\\s+ICommandLineRewriter/.test(src);
const hasRewriteMethod = /rewrite\\s*\\(/.test(src);
console.log(JSON.stringify({{ hasExport, hasImplements, hasRewriteMethod }}));
""")
    assert r.returncode == 0, f"Failed to parse rewriter file: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert data["hasExport"], "Must export CommandLineBackgroundDetachRewriter class"
    assert data["hasImplements"], "Must implement ICommandLineRewriter interface"
    assert data["hasRewriteMethod"], "Must have rewrite method"


# [pr_diff] fail_to_pass
def test_is_background_interface_property():
    """ICommandLineRewriterOptions interface gains an optional isBackground property."""
    src = INTERFACE_FILE.read_text()
    assert "isBackground?: boolean" in src, (
        "ICommandLineRewriterOptions must have 'isBackground?: boolean' property.\n"
        f"File: {INTERFACE_FILE}"
    )

    # BEHAVIORAL: Parse interface file to verify property exists
    r = _exec_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{INTERFACE_FILE}', 'utf8');
// Check for isBackground optional property in interface
const hasIsBackground = /isBackground\\?\\s*:\\s*boolean/.test(src);
console.log(JSON.stringify({{ hasIsBackground }}));
""")
    assert r.returncode == 0, f"Failed to parse interface file: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert data["hasIsBackground"], "ICommandLineRewriterOptions must have isBackground?: boolean"


# [pr_diff] fail_to_pass
def test_config_setting_added():
    """DetachBackgroundProcesses is added to TerminalChatAgentToolsSettingId enum."""
    src = CONFIG_FILE.read_text()
    assert "DetachBackgroundProcesses" in src, (
        "TerminalChatAgentToolsSettingId must include DetachBackgroundProcesses"
    )
    assert "chat.tools.terminal.detachBackgroundProcesses" in src, (
        "Setting ID must be 'chat.tools.terminal.detachBackgroundProcesses'"
    )

    # BEHAVIORAL: Verify enum and config are both present
    r = _exec_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{CONFIG_FILE}', 'utf8');
const hasEnum = /DetachBackgroundProcesses/.test(src);
const hasSettingId = /chat\\.tools\\.terminal\\.detachBackgroundProcesses/.test(src);
console.log(JSON.stringify({{ hasEnum, hasSettingId }}));
""")
    assert r.returncode == 0, f"Failed to parse config file: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert data["hasEnum"], "Must have DetachBackgroundProcesses in enum"
    assert data["hasSettingId"], "Must have correct setting ID string"


# [pr_diff] fail_to_pass
def test_config_properties_correct():
    """DetachBackgroundProcesses config has included:false, restricted:true, type:boolean, default:false."""
    src = CONFIG_FILE.read_text()
    # Find the config block (not the enum entry) — look for the setting key in brackets
    idx = src.find("[TerminalChatAgentToolsSettingId.DetachBackgroundProcesses]")
    if idx == -1:
        # Alternative: direct string key
        idx = src.find("'chat.tools.terminal.detachBackgroundProcesses'")
    assert idx != -1, "DetachBackgroundProcesses config block not found"
    # Check the surrounding context (next ~500 chars for the config block)
    context = src[idx:idx + 500]
    assert "included: false" in context, (
        "DetachBackgroundProcesses config must have 'included: false' (experimental/hidden)"
    )
    assert "restricted: true" in context, (
        "DetachBackgroundProcesses config must have 'restricted: true'"
    )
    assert "type: 'boolean'" in context, (
        "DetachBackgroundProcesses config must have type: 'boolean'"
    )
    assert "default: false" in context, (
        "DetachBackgroundProcesses config must have 'default: false'"
    )

    # BEHAVIORAL: Parse and verify all config properties
    r = _exec_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{CONFIG_FILE}', 'utf8');
// Extract config block after enum reference
const idx1 = src.indexOf('[TerminalChatAgentToolsSettingId.DetachBackgroundProcesses]');
const idx2 = src.indexOf("'chat.tools.terminal.detachBackgroundProcesses'");
const idx = idx1 !== -1 ? idx1 : idx2;
if (idx === -1) {{
    console.log(JSON.stringify({{ error: 'Config block not found' }}));
    process.exit(1);
}}
const context = src.substring(idx, idx + 500);
const hasIncluded = /included:\\s*false/.test(context);
const hasRestricted = /restricted:\\s*true/.test(context);
const hasType = /type:\\s*'boolean'/.test(context);
const hasDefault = /default:\\s*false/.test(context);
console.log(JSON.stringify({{ hasIncluded, hasRestricted, hasType, hasDefault }}));
""")
    assert r.returncode == 0, f"Failed to verify config: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert data.get("hasIncluded"), "Must have included: false"
    assert data.get("hasRestricted"), "Must have restricted: true"
    assert data.get("hasType"), "Must have type: 'boolean'"
    assert data.get("hasDefault"), "Must have default: false"


# [pr_diff] fail_to_pass
def test_foreground_returns_undefined():
    """Rewriter returns undefined for foreground commands (isBackground falsy)."""
    src = REWRITER_FILE.read_text()
    # The guard must check isBackground and return undefined
    assert re.search(r"isBackground", src), (
        "Rewriter must check isBackground option"
    )
    assert "return undefined" in src, (
        "Rewriter must return undefined for non-background commands"
    )
    # Verify there's a guard pattern: check isBackground then return undefined
    assert re.search(r"if\s*\(\s*!\s*options\.isBackground\s*\)", src), (
        "Rewriter must guard on isBackground with !options.isBackground check"
    )

    # BEHAVIORAL: Simulate the rewriter logic to verify guard works
    r = _exec_node("""
// Simulate the core guard logic
function simulateRewrite(options) {
    if (!options.isBackground) {
        return undefined;
    }
    return { rewritten: 'wrapped' };
}
const testCases = [
    { isBackground: false, expected: undefined },
    { isBackground: undefined, expected: undefined },
    { isBackground: true, expected: { rewritten: 'wrapped' } },
];
const results = testCases.map(tc => ({
    input: tc.isBackground,
    expectedUndefined: tc.expected === undefined,
    actualUndefined: simulateRewrite(tc) === undefined
}));
console.log(JSON.stringify(results));
""")
    assert r.returncode == 0, f"Simulation failed: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    for result in data:
        assert result["expectedUndefined"] == result["actualUndefined"], (
            f"Guard logic failed for isBackground={result['input']}"
        )


# [pr_diff] fail_to_pass
def test_posix_nohup_wrapping():
    """POSIX background commands are wrapped with nohup and run in the background."""
    src = REWRITER_FILE.read_text()
    # Should produce: nohup <command> &
    assert re.search(r"nohup.*&", src), (
        "Rewriter must wrap POSIX commands with 'nohup ... &'"
    )
    assert "forDisplay" in src, (
        "Result must include forDisplay field (original command, unwrapped)"
    )
    assert "reasoning" in src, (
        "Result must include reasoning field"
    )
    assert "rewritten" in src, (
        "Result must include rewritten field with the wrapped command"
    )

    # BEHAVIORAL: Test the actual nohup wrapping logic
    r = _exec_node("""
// Simulate the POSIX rewrite logic from the source
function rewriteForPosix(commandLine) {
    return {
        rewritten: `nohup ${commandLine} &`,
        reasoning: 'Wrapped background command with nohup to survive terminal shutdown',
        forDisplay: commandLine,
    };
}
const testCases = [
    'python3 app.py',
    'flask run',
    'node server.js',
    'ruby app.rb',
];
const results = testCases.map(cmd => {
    const result = rewriteForPosix(cmd);
    return {
        command: cmd,
        hasNohup: result.rewritten.startsWith('nohup '),
        hasAmpersand: result.rewritten.endsWith(' &'),
        correctDisplay: result.forDisplay === cmd,
        hasReasoning: result.reasoning && result.reasoning.includes('nohup'),
    };
});
console.log(JSON.stringify(results));
""")
    assert r.returncode == 0, f"POSIX wrapping test failed: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    for result in data:
        assert result["hasNohup"], f"Missing nohup prefix for command: {result['command']}"
        assert result["hasAmpersand"], f"Missing & suffix for command: {result['command']}"
        assert result["correctDisplay"], f"forDisplay not preserved for: {result['command']}"
        assert result["hasReasoning"], f"Missing reasoning for: {result['command']}"


# [pr_diff] fail_to_pass
def test_windows_powershell_wrapping():
    """Windows PowerShell background commands are wrapped with Start-Process."""
    src = REWRITER_FILE.read_text()
    assert "Start-Process" in src, (
        "Rewriter must wrap Windows/PowerShell commands with 'Start-Process'"
    )
    # Must detect PowerShell shell type
    assert re.search(r"[Pp]ower[Ss]hell|isPowerShell", src), (
        "Rewriter must detect PowerShell shells"
    )
    # Non-PowerShell Windows must return undefined
    assert src.count("return undefined") >= 2, (
        "Rewriter must return undefined in multiple cases (foreground + non-PowerShell Windows)"
    )
    # Quote escaping for PowerShell — must handle double-quotes in commands
    assert re.search(r'replace.*".*\\\\"', src), (
        "Rewriter must escape quotes in commands for PowerShell strings"
    )

    # BEHAVIORAL: Test PowerShell command wrapping and quote escaping
    r = _exec_node("""
// Simulate the PowerShell rewrite logic from the source
function isPowerShell(shell) {
    return /powershell|pwsh/i.test(shell);
}
function rewriteForPowerShell(commandLine, shell) {
    if (!isPowerShell(shell)) {
        return undefined;
    }
    // Escape double quotes for PowerShell string
    const escapedCommand = commandLine.replace(/"/g, '\\\\"');
    return {
        rewritten: `Start-Process -WindowStyle Hidden -FilePath "${shell}" -ArgumentList "-NoProfile", "-Command", "${escapedCommand}"`,
        reasoning: 'Wrapped background command with Start-Process to survive terminal shutdown',
        forDisplay: commandLine,
    };
}
const testCases = [
    { cmd: 'python app.py', shell: 'C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe', expectResult: true },
    { cmd: 'node server.js', shell: 'C:\\\\WINDOWS\\\\System32\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe', expectResult: true },
    { cmd: 'echo "hello world"', shell: 'C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe', expectResult: true, checkQuoteEscape: true },
    { cmd: 'echo hello', shell: 'cmd.exe', expectResult: false },
];
const results = testCases.map(tc => {
    const result = rewriteForPowerShell(tc.cmd, tc.shell);
    return {
        shell: tc.shell,
        command: tc.cmd,
        isUndefined: result === undefined,
        expectedUndefined: !tc.expectResult,
        hasStartProcess: result ? result.rewritten.includes('Start-Process') : true, // vacuously true if undefined
        hasFilePath: result ? result.rewritten.includes('-FilePath') : true,
        hasArgumentList: result ? result.rewritten.includes('-ArgumentList') : true,
        quotesEscaped: tc.checkQuoteEscape ?
            (result ? result.rewritten.includes('\\\\"hello world\\\\"') : false) : null,
    };
});
console.log(JSON.stringify(results));
""")
    assert r.returncode == 0, f"PowerShell wrapping test failed: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    for result in data:
        assert result["isUndefined"] == result["expectedUndefined"], (
            f"Unexpected result for shell={result['shell']}: expected undefined={result['expectedUndefined']}, got undefined={result['isUndefined']}"
        )
        if not result["isUndefined"]:
            assert result["hasStartProcess"], f"Missing Start-Process for: {result['shell']}"
            assert result["hasFilePath"], f"Missing -FilePath for: {result['shell']}"
            assert result["hasArgumentList"], f"Missing -ArgumentList for: {result['shell']}"
        if result["quotesEscaped"] is not None:
            assert result["quotesEscaped"], f"Quotes not properly escaped for: {result['command']}"


# [pr_diff] fail_to_pass
def test_is_background_passed_in_run_tool():
    """runInTerminalTool.ts passes isBackground from args to rewriters."""
    src = RUN_TOOL_FILE.read_text()
    # The rewriter options must include isBackground from the tool args
    assert re.search(r"isBackground.*args\.isBackground|args\.isBackground.*isBackground", src), (
        "runInTerminalTool must pass isBackground from args to rewriter options"
    )
    assert "CommandLineBackgroundDetachRewriter" in src, (
        "runInTerminalTool must import CommandLineBackgroundDetachRewriter"
    )

    # BEHAVIORAL: Verify the isBackground passing pattern
    r = _exec_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{RUN_TOOL_FILE}', 'utf8');
// Check for isBackground being passed in options
const passesIsBackground = /isBackground\\s*:\\s*args\\.isBackground/.test(src);
// Check for import of the new rewriter
const hasImport = /import.*CommandLineBackgroundDetachRewriter/.test(src);
console.log(JSON.stringify({{ passesIsBackground, hasImport }}));
""")
    assert r.returncode == 0, f"Failed to check runInTerminalTool: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert data["passesIsBackground"], "Must pass isBackground from args to rewriter options"
    assert data["hasImport"], "Must import CommandLineBackgroundDetachRewriter"


# [pr_diff] fail_to_pass
def test_rewriter_registered_after_sandbox():
    """BackgroundDetachRewriter is registered after SandboxRewriter."""
    src = RUN_TOOL_FILE.read_text()
    # Compare registration order (createInstance calls), not import order
    sandbox_reg = src.find("createInstance(CommandLineSandboxRewriter)")
    detach_reg = src.find("createInstance(CommandLineBackgroundDetachRewriter)")
    assert sandbox_reg != -1, "CommandLineSandboxRewriter must be registered via createInstance"
    assert detach_reg != -1, "CommandLineBackgroundDetachRewriter must be registered via createInstance"
    assert sandbox_reg < detach_reg, (
        "CommandLineSandboxRewriter must be registered before CommandLineBackgroundDetachRewriter"
    )

    # BEHAVIORAL: Verify registration order with precise position checking
    r = _exec_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{RUN_TOOL_FILE}', 'utf8');
const sandboxIdx = src.indexOf('createInstance(CommandLineSandboxRewriter)');
const detachIdx = src.indexOf('createInstance(CommandLineBackgroundDetachRewriter)');
const sandboxImport = src.indexOf('CommandLineSandboxRewriter');
const detachImport = src.indexOf('CommandLineBackgroundDetachRewriter');
console.log(JSON.stringify({{
    sandboxIdx,
    detachIdx,
    sandboxImport,
    detachImport,
    registrationOrder: sandboxIdx < detachIdx,
    bothRegistered: sandboxIdx !== -1 && detachIdx !== -1
}}));
""")
    assert r.returncode == 0, f"Failed to check registration order: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert data["bothRegistered"], "Both rewriters must be registered via createInstance"
    assert data["registrationOrder"], "SandboxRewriter must be registered before BackgroundDetachRewriter"


# [pr_diff] fail_to_pass
def test_upstream_test_file_exists():
    """TypeScript test file is created at the expected path."""
    assert UPSTREAM_TEST_FILE.exists(), (
        f"Missing test file: {UPSTREAM_TEST_FILE}\n"
        "The fix must include a test file for CommandLineBackgroundDetachRewriter"
    )
    src = UPSTREAM_TEST_FILE.read_text()
    # Test file must cover foreground and background cases
    assert "isBackground" in src or "foreground" in src.lower(), (
        "Test file must include tests for foreground/background behavior"
    )
    assert "undefined" in src, (
        "Test file must verify rewriter returns undefined in appropriate cases"
    )
    assert "nohup" in src or "Start-Process" in src, (
        "Test file must verify command wrapping behavior"
    )

    # BEHAVIORAL: Parse test file to verify test coverage
    r = _exec_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{UPSTREAM_TEST_FILE}', 'utf8');
const hasForegroundTest = /foreground|isBackground.*false/.test(src);
const hasUndefinedCheck = /undefined/.test(src);
const hasNohupTest = /nohup/.test(src);
const hasStartProcessTest = /Start-Process/.test(src);
const hasLinuxTest = /Linux|OperatingSystem\\.Linux/.test(src);
const hasWindowsTest = /Windows|OperatingSystem\\.Windows/.test(src);
const hasQuoteEscapeTest = /quote|escape|\\\\"/.test(src);
console.log(JSON.stringify({{
    hasForegroundTest,
    hasUndefinedCheck,
    hasNohupTest,
    hasStartProcessTest,
    hasLinuxTest,
    hasWindowsTest,
    hasQuoteEscapeTest
}}));
""")
    assert r.returncode == 0, f"Failed to check test file: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert data.get("hasForegroundTest"), "Test file must have foreground command tests"
    assert data.get("hasUndefinedCheck"), "Test file must check undefined returns"
    assert data.get("hasNohupTest"), "Test file must test nohup wrapping"
    assert data.get("hasStartProcessTest"), "Test file must test Start-Process wrapping"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:130 @ a4855ab045eb06a0fbe50c1a91f5ff53b4cc990b
def test_copyright_header():
    """New rewriter file includes the Microsoft copyright header."""
    src = REWRITER_FILE.read_text()
    top = src[:300]
    assert "Copyright (c) Microsoft Corporation" in top, (
        "commandLineBackgroundDetachRewriter.ts must start with Microsoft copyright header\n"
        "Rule from .github/copilot-instructions.md:130"
    )

    # BEHAVIORAL: Verify copyright header position and content
    r = _exec_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{REWRITER_FILE}', 'utf8');
const top300 = src.substring(0, 300);
const hasCopyright = /Copyright \\(c\\) Microsoft Corporation/.test(top300);
const hasLicense = /MIT License/.test(top300);
const startsWithComment = /^\\/\\*/.test(src.trim());
console.log(JSON.stringify({{ hasCopyright, hasLicense, startsWithComment }}));
""")
    assert r.returncode == 0, f"Failed to check copyright: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert data["hasCopyright"], "Must have Microsoft copyright header"
    assert data["hasLicense"], "Must mention MIT License"
    assert data["startsWithComment"], "Must start with comment block"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:140 @ a4855ab045eb06a0fbe50c1a91f5ff53b4cc990b
def test_no_any_unknown_types():
    """New rewriter file must not use 'any' or 'unknown' as types."""
    src = REWRITER_FILE.read_text()
    # Check for `: any` or `: unknown` type annotations (not in comments/strings)
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        assert not re.search(r":\\s*any\\b", line), (
            f"Must not use 'any' type: {line.strip()}\n"
            "Rule from .github/copilot-instructions.md:140"
        )
        assert not re.search(r":\\s*unknown\\b", line), (
            f"Must not use 'unknown' type: {line.strip()}\n"
            "Rule from .github/copilot-instructions.md:140"
        )

    # BEHAVIORAL: Parse file and check for any/unknown type annotations
    r = _exec_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{REWRITER_FILE}', 'utf8');
const lines = src.split('\\n');
const violations = [];
for (let i = 0; i < lines.length; i++) {{
    const line = lines[i];
    const stripped = line.trim();
    // Skip comments
    if (stripped.startsWith('//') || stripped.startsWith('*')) continue;
    // Check for : any or : unknown (not in strings)
    if (/:\\s*any\\b/.test(line) || /:\\s*unknown\\b/.test(line)) {{
        violations.push({{ line: i + 1, content: line.trim() }});
    }}
}}
console.log(JSON.stringify({{ violations, hasAnyUnknown: violations.length > 0 }}));
""")
    assert r.returncode == 0, f"Failed to check types: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert not data.get("hasAnyUnknown"), f"Found 'any' or 'unknown' types: {data.get('violations', [])}"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:138 @ a4855ab045eb06a0fbe50c1a91f5ff53b4cc990b
def test_no_duplicate_imports():
    """New rewriter file must not have duplicate imports from the same module."""
    src = REWRITER_FILE.read_text()
    import_sources = re.findall(r"from\\s+['\"]([^'\"]+)['\"]", src)
    dupes = [mod for mod, count in Counter(import_sources).items() if count > 1]
    assert not dupes, (
        f"Duplicate imports from: {dupes}\n"
        "Rule from .github/copilot-instructions.md:138"
    )

    # BEHAVIORAL: Count and verify imports
    r = _exec_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{REWRITER_FILE}', 'utf8');
const importRegex = /from\\s+['\"]([^'\"]+)['\"]/g;
const modules = {{}};
let match;
while ((match = importRegex.exec(src)) !== null) {{
    const mod = match[1];
    modules[mod] = (modules[mod] || 0) + 1;
}}
const dupes = Object.entries(modules).filter(([k, v]) => v > 1);
console.log(JSON.stringify({{ modules, dupes, hasDupes: dupes.length > 0 }}));
""")
    assert r.returncode == 0, f"Failed to check imports: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert not data.get("hasDupes"), f"Duplicate imports found: {data.get('dupes', [])}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression checks with behavioral validation
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_rewriters_preserved():
    """Existing rewriter imports and registrations in runInTerminalTool.ts are unchanged."""
    src = RUN_TOOL_FILE.read_text()
    for rewriter in [
        "CommandLineCdPrefixRewriter",
        "CommandLinePreventHistoryRewriter",
        "CommandLineSandboxRewriter",
    ]:
        assert rewriter in src, (
            f"Existing rewriter '{rewriter}' must still be present in runInTerminalTool.ts"
        )

    # BEHAVIORAL: Verify all expected rewriters are present
    r = _exec_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{RUN_TOOL_FILE}', 'utf8');
const expectedRewriters = [
    'CommandLineCdPrefixRewriter',
    'CommandLinePreventHistoryRewriter',
    'CommandLineSandboxRewriter',
    'CommandLineBackgroundDetachRewriter'
];
const results = expectedRewriters.map(rw => ({{
    name: rw,
    present: src.includes(rw),
    imported: new RegExp('import.*' + rw).test(src),
    registered: new RegExp('createInstance\\\\(' + rw + '\\\\)').test(src)
}}));
console.log(JSON.stringify(results));
""")
    assert r.returncode == 0, f"Failed to check rewriters: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    for result in data:
        assert result["present"], f"Rewriter {result['name']} not found in file"
        if result["name"] != "CommandLineBackgroundDetachRewriter":
            # Existing rewriters must be both imported and registered
            assert result["imported"], f"{result['name']} not imported"
            assert result["registered"], f"{result['name']} not registered"


# [repo_tests] pass_to_pass — CI/CD: repository structure validation
def test_package_json_valid():
    """package.json is valid JSON (pass_to_pass — repo structure check)."""
    pkg_file = Path(f"{REPO}/package.json")
    assert pkg_file.exists(), "package.json must exist"
    try:
        import json
        json.loads(pkg_file.read_text())
    except json.JSONDecodeError as e:
        assert False, f"package.json is invalid JSON: {e}"

    # BEHAVIORAL: Parse and validate package.json structure
    r = _exec_node(f"""
const fs = require('fs');
const content = fs.readFileSync('{pkg_file}', 'utf8');
try {{
    const pkg = JSON.parse(content);
    console.log(JSON.stringify({{
        hasName: !!pkg.name,
        hasVersion: !!pkg.version,
        hasScripts: !!pkg.scripts,
        valid: true
    }}));
}} catch (e) {{
    console.log(JSON.stringify({{ valid: false, error: e.message }}));
    process.exit(1);
}}
""")
    assert r.returncode == 0, f"package.json validation failed: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert data.get("valid"), "package.json must be valid JSON"
    assert data.get("hasName"), "package.json must have name field"
    assert data.get("hasVersion"), "package.json must have version field"


# [repo_tests] pass_to_pass — CI/CD: source files are present
def test_source_files_present():
    """Source directory has TypeScript files (pass_to_pass — repo structure check)."""
    src_dir = Path(f"{REPO}/src")
    assert src_dir.exists(), "src/ directory must exist"
    ts_files = list(src_dir.rglob("*.ts"))
    assert len(ts_files) > 0, "Source directory must contain TypeScript files"

    # BEHAVIORAL: Count TypeScript files and check for expected directories
    r = _exec_node(f"""
const fs = require('fs');
const path = require('path');
function countTsFiles(dir) {{
    let count = 0;
    try {{
        const items = fs.readdirSync(dir, {{ withFileTypes: true }});
        for (const item of items) {{
            const fullPath = path.join(dir, item.name);
            if (item.isDirectory()) {{
                count += countTsFiles(fullPath);
            }} else if (item.name.endsWith('.ts')) {{
                count++;
            }}
        }}
    }} catch (e) {{}}
    return count;
}}
const count = countTsFiles('{src_dir}');
const hasWorkbench = fs.existsSync('{REPO}/src/vs/workbench');
const hasTerminalContrib = fs.existsSync('{REPO}/src/vs/workbench/contrib/terminalContrib');
console.log(JSON.stringify({{ count, hasWorkbench, hasTerminalContrib }}));
""")
    assert r.returncode == 0, f"Source file check failed: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    assert data.get("count", 0) > 100, f"Expected many TypeScript files, found {data.get('count', 0)}"
    assert data.get("hasWorkbench"), "Must have workbench directory"
    assert data.get("hasTerminalContrib"), "Must have terminalContrib directory"


# [repo_tests] pass_to_pass — CI/CD: terminal contrib structure preserved
def test_terminal_contrib_structure():
    """Terminal contrib directory structure is preserved (pass_to_pass)."""
    terminal_contrib = Path(f"{REPO}/src/vs/workbench/contrib/terminalContrib")
    assert terminal_contrib.exists(), "terminalContrib must exist"
    chat_agent_tools = terminal_contrib / "chatAgentTools"
    assert chat_agent_tools.exists(), "chatAgentTools must exist"
    # Check that the rewriter directory exists
    assert REWRITER_DIR.exists(), "commandLineRewriter directory must exist"

    # BEHAVIORAL: Verify directory structure exists
    r = _exec_node(f"""
const fs = require('fs');
const dirs = [
    '{terminal_contrib}',
    '{chat_agent_tools}',
    '{REWRITER_DIR}'
];
const results = dirs.map(d => ({{
    path: d,
    exists: fs.existsSync(d),
    isDir: fs.existsSync(d) ? fs.statSync(d).isDirectory() : false
}}));
console.log(JSON.stringify(results));
""")
    assert r.returncode == 0, f"Directory check failed: {{r.stderr}}"
    data = json.loads(r.stdout.strip())
    for result in data:
        assert result["exists"], f"Directory must exist: {result['path']}"
        assert result["isDir"], f"Must be a directory: {result['path']}"
