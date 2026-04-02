"""
Task: vscode-background-process-detach
Repo: microsoft/vscode @ a4855ab045eb06a0fbe50c1a91f5ff53b4cc990b

Background server processes started via run_in_terminal with isBackground=true
are killed when VS Code exits. The fix adds a CommandLineBackgroundDetachRewriter
that wraps background commands with nohup (POSIX) or Start-Process (Windows).

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
REWRITER_DIR = Path(f"{REPO}/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter")
REWRITER_FILE = REWRITER_DIR / "commandLineBackgroundDetachRewriter.ts"
INTERFACE_FILE = REWRITER_DIR / "commandLineRewriter.ts"
RUN_TOOL_FILE = Path(f"{REPO}/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts")
CONFIG_FILE = Path(f"{REPO}/src/vs/workbench/contrib/terminalContrib/chatAgentTools/common/terminalChatAgentToolsConfiguration.ts")
UPSTREAM_TEST_FILE = Path(f"{REPO}/src/vs/workbench/contrib/terminalContrib/chatAgentTools/test/electron-browser/commandLineBackgroundDetachRewriter.test.ts")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural + behavioral checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rewriter_file_exists():
    """commandLineBackgroundDetachRewriter.ts is created at the expected path."""
    # AST-only because: TypeScript requires full compilation to execute
    assert REWRITER_FILE.exists(), (
        f"Missing: {REWRITER_FILE}\n"
        "The fix must create commandLineBackgroundDetachRewriter.ts"
    )
    assert REWRITER_FILE.stat().st_size > 0, "File is empty"


# [pr_diff] fail_to_pass
def test_rewriter_class_exported():
    """CommandLineBackgroundDetachRewriter is exported and implements ICommandLineRewriter."""
    # AST-only because: TypeScript requires full compilation to execute
    src = REWRITER_FILE.read_text()
    assert "export class CommandLineBackgroundDetachRewriter" in src, (
        "CommandLineBackgroundDetachRewriter must be exported as a class"
    )
    assert "implements ICommandLineRewriter" in src, (
        "Class must implement ICommandLineRewriter interface"
    )


# [pr_diff] fail_to_pass
def test_is_background_interface_property():
    """ICommandLineRewriterOptions interface gains an optional isBackground property."""
    # AST-only because: TypeScript requires full compilation to execute
    src = INTERFACE_FILE.read_text()
    assert "isBackground?: boolean" in src, (
        "ICommandLineRewriterOptions must have 'isBackground?: boolean' property.\n"
        f"File: {INTERFACE_FILE}"
    )


# [pr_diff] fail_to_pass
def test_config_setting_added():
    """DetachBackgroundProcesses is added to TerminalChatAgentToolsSettingId enum."""
    # AST-only because: TypeScript requires full compilation to execute
    src = CONFIG_FILE.read_text()
    assert "DetachBackgroundProcesses" in src, (
        "TerminalChatAgentToolsSettingId must include DetachBackgroundProcesses"
    )
    assert "chat.tools.terminal.detachBackgroundProcesses" in src, (
        "Setting ID must be 'chat.tools.terminal.detachBackgroundProcesses'"
    )


# [pr_diff] fail_to_pass
def test_config_properties_correct():
    """DetachBackgroundProcesses config has included:false, restricted:true, type:boolean, default:false."""
    # AST-only because: TypeScript requires full compilation to execute
    src = CONFIG_FILE.read_text()
    # Find the block around DetachBackgroundProcesses
    idx = src.find("DetachBackgroundProcesses")
    assert idx != -1, "DetachBackgroundProcesses not found in config file"
    # Check the surrounding context (next ~400 chars)
    context = src[idx:idx + 400]
    assert "included: false" in context, (
        "DetachBackgroundProcesses config must have 'included: false' (experimental/hidden)"
    )
    assert "restricted: true" in context, (
        "DetachBackgroundProcesses config must have 'restricted: true'"
    )
    assert "type: 'boolean'" in context, (
        "DetachBackgroundProcesses config must have 'type: 'boolean''"
    )
    assert "default: false" in context, (
        "DetachBackgroundProcesses config must have 'default: false'"
    )


# [pr_diff] fail_to_pass
def test_foreground_returns_undefined():
    """Rewriter returns undefined for foreground commands (isBackground falsy)."""
    # AST-only because: TypeScript requires full compilation to execute
    src = REWRITER_FILE.read_text()
    # The guard: if (!options.isBackground) { return undefined; }
    assert re.search(r"if\s*\(!options\.isBackground\)", src), (
        "Rewriter must guard with 'if (!options.isBackground)' to return undefined for foreground commands"
    )
    assert "return undefined" in src, (
        "Rewriter must return undefined for non-background commands"
    )


# [pr_diff] fail_to_pass
def test_posix_nohup_wrapping():
    """POSIX background commands are wrapped with nohup and run in the background."""
    # AST-only because: TypeScript requires full compilation to execute
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


# [pr_diff] fail_to_pass
def test_windows_powershell_wrapping():
    """Windows PowerShell background commands are wrapped with Start-Process."""
    # AST-only because: TypeScript requires full compilation to execute
    src = REWRITER_FILE.read_text()
    assert "Start-Process" in src, (
        "Rewriter must wrap Windows/PowerShell commands with 'Start-Process'"
    )
    assert "isPowerShell" in src, (
        "Rewriter must call isPowerShell() to detect PowerShell shells"
    )
    # Non-PowerShell Windows returns undefined (isPowerShell check + return undefined)
    assert re.search(r"isPowerShell.*\n.*return undefined|return undefined.*\n.*isPowerShell", src, re.DOTALL), (
        "Rewriter must return undefined for non-PowerShell Windows shells"
    )
    # Quote escaping for PowerShell
    assert re.search(r'replace\(/"/g.*\\\\"|replace.*".*\\\\"', src), (
        "Rewriter must escape double-quotes in commands for PowerShell strings"
    )


# [pr_diff] fail_to_pass
def test_is_background_passed_in_run_tool():
    """runInTerminalTool.ts passes isBackground from args to rewriters."""
    # AST-only because: TypeScript requires full compilation to execute
    src = RUN_TOOL_FILE.read_text()
    assert "isBackground: args.isBackground" in src, (
        "runInTerminalTool must pass 'isBackground: args.isBackground' to rewriter options"
    )
    assert "CommandLineBackgroundDetachRewriter" in src, (
        "runInTerminalTool must import CommandLineBackgroundDetachRewriter"
    )


# [pr_diff] fail_to_pass
def test_rewriter_registered_after_sandbox():
    """BackgroundDetachRewriter is registered after SandboxRewriter with ordering comment."""
    # AST-only because: TypeScript requires full compilation to execute
    src = RUN_TOOL_FILE.read_text()
    # The comment explaining ordering constraint
    assert re.search(r"BackgroundDetachRewriter.*must come after.*SandboxRewriter|after.*SandboxRewriter.*BackgroundDetachRewriter", src, re.IGNORECASE), (
        "Must have comment explaining BackgroundDetachRewriter must come after SandboxRewriter"
    )
    # SandboxRewriter must appear before BackgroundDetachRewriter in registration
    sandbox_idx = src.find("CommandLineSandboxRewriter")
    detach_idx = src.find("CommandLineBackgroundDetachRewriter")
    assert sandbox_idx < detach_idx, (
        "CommandLineSandboxRewriter must be registered before CommandLineBackgroundDetachRewriter"
    )


# [pr_diff] fail_to_pass
def test_upstream_test_file_exists():
    """TypeScript test file is created at the expected path."""
    # AST-only because: TypeScript requires full compilation to execute
    assert UPSTREAM_TEST_FILE.exists(), (
        f"Missing test file: {UPSTREAM_TEST_FILE}\n"
        "The fix must include a test file for CommandLineBackgroundDetachRewriter"
    )
    src = UPSTREAM_TEST_FILE.read_text()
    # Test file must have tests for foreground and disabled-setting cases
    assert "foreground" in src.lower() or "isBackground" in src, (
        "Test file must include tests for foreground commands returning undefined"
    )
    assert "undefined" in src, (
        "Test file must verify rewriter returns undefined in appropriate cases"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:32 @ a4855ab045eb06a0fbe50c1a91f5ff53b4cc990b
def test_copyright_header():
    """New rewriter file includes the Microsoft copyright header."""
    # AST-only because: TypeScript requires full compilation to execute
    src = REWRITER_FILE.read_text()
    # Copyright header must be near the top
    top = src[:300]
    assert "Copyright (c) Microsoft Corporation" in top, (
        "commandLineBackgroundDetachRewriter.ts must start with Microsoft copyright header\n"
        "Rule from .github/copilot-instructions.md:32"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_rewriters_preserved():
    """Existing rewriter imports and registrations in runInTerminalTool.ts are unchanged."""
    # AST-only because: TypeScript requires full compilation to execute
    src = RUN_TOOL_FILE.read_text()
    for rewriter in [
        "CommandLineCdPrefixRewriter",
        "CommandLinePreventHistoryRewriter",
        "CommandLineSandboxRewriter",
    ]:
        assert rewriter in src, (
            f"Existing rewriter '{rewriter}' must still be present in runInTerminalTool.ts"
        )
