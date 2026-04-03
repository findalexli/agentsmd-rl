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
from collections import Counter
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


# [pr_diff] fail_to_pass
def test_foreground_returns_undefined():
    """Rewriter returns undefined for foreground commands (isBackground falsy)."""
    # AST-only because: TypeScript requires full compilation to execute
    src = REWRITER_FILE.read_text()
    # The guard must check isBackground and return undefined
    assert re.search(r"isBackground", src), (
        "Rewriter must check isBackground option"
    )
    assert "return undefined" in src, (
        "Rewriter must return undefined for non-background commands"
    )
    # Verify there's a guard pattern: check isBackground then return undefined
    assert re.search(r"isBackground.*?return undefined", src, re.DOTALL), (
        "Rewriter must guard on isBackground before returning undefined"
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
    assert "rewritten" in src, (
        "Result must include rewritten field with the wrapped command"
    )


# [pr_diff] fail_to_pass
def test_windows_powershell_wrapping():
    """Windows PowerShell background commands are wrapped with Start-Process."""
    # AST-only because: TypeScript requires full compilation to execute
    src = REWRITER_FILE.read_text()
    assert "Start-Process" in src, (
        "Rewriter must wrap Windows/PowerShell commands with 'Start-Process'"
    )
    # Must detect PowerShell shell type
    assert re.search(r"[Pp]ower[Ss]hell", src), (
        "Rewriter must detect PowerShell shells"
    )
    # Non-PowerShell Windows must return undefined
    assert src.count("return undefined") >= 2, (
        "Rewriter must return undefined in multiple cases (foreground + non-PowerShell Windows)"
    )
    # Quote escaping for PowerShell — must handle double-quotes in commands
    assert re.search(r'replace.*".*\\', src), (
        "Rewriter must escape quotes in commands for PowerShell strings"
    )


# [pr_diff] fail_to_pass
def test_is_background_passed_in_run_tool():
    """runInTerminalTool.ts passes isBackground from args to rewriters."""
    # AST-only because: TypeScript requires full compilation to execute
    src = RUN_TOOL_FILE.read_text()
    # The rewriter options must include isBackground from the tool args
    assert re.search(r"isBackground.*args\.isBackground|args\.isBackground.*isBackground", src), (
        "runInTerminalTool must pass isBackground from args to rewriter options"
    )
    assert "CommandLineBackgroundDetachRewriter" in src, (
        "runInTerminalTool must import CommandLineBackgroundDetachRewriter"
    )


# [pr_diff] fail_to_pass
def test_rewriter_registered_after_sandbox():
    """BackgroundDetachRewriter is registered after SandboxRewriter."""
    # AST-only because: TypeScript requires full compilation to execute
    src = RUN_TOOL_FILE.read_text()
    # Compare registration order (createInstance calls), not import order
    sandbox_reg = src.find("createInstance(CommandLineSandboxRewriter)")
    detach_reg = src.find("createInstance(CommandLineBackgroundDetachRewriter)")
    assert sandbox_reg != -1, "CommandLineSandboxRewriter must be registered via createInstance"
    assert detach_reg != -1, "CommandLineBackgroundDetachRewriter must be registered via createInstance"
    assert sandbox_reg < detach_reg, (
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


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:130 @ a4855ab045eb06a0fbe50c1a91f5ff53b4cc990b
def test_copyright_header():
    """New rewriter file includes the Microsoft copyright header."""
    # AST-only because: TypeScript requires full compilation to execute
    src = REWRITER_FILE.read_text()
    top = src[:300]
    assert "Copyright (c) Microsoft Corporation" in top, (
        "commandLineBackgroundDetachRewriter.ts must start with Microsoft copyright header\n"
        "Rule from .github/copilot-instructions.md:130"
    )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:140 @ a4855ab045eb06a0fbe50c1a91f5ff53b4cc990b
def test_no_any_unknown_types():
    """New rewriter file must not use 'any' or 'unknown' as types."""
    # AST-only because: TypeScript requires full compilation to execute
    src = REWRITER_FILE.read_text()
    # Check for `: any` or `: unknown` type annotations (not in comments/strings)
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        assert not re.search(r":\s*any\b", line), (
            f"Must not use 'any' type: {line.strip()}\n"
            "Rule from .github/copilot-instructions.md:140"
        )
        assert not re.search(r":\s*unknown\b", line), (
            f"Must not use 'unknown' type: {line.strip()}\n"
            "Rule from .github/copilot-instructions.md:140"
        )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:138 @ a4855ab045eb06a0fbe50c1a91f5ff53b4cc990b
def test_no_duplicate_imports():
    """New rewriter file must not have duplicate imports from the same module."""
    # AST-only because: TypeScript requires full compilation to execute
    src = REWRITER_FILE.read_text()
    import_sources = re.findall(r"from\s+['\"]([^'\"]+)['\"]", src)
    dupes = [mod for mod, count in Counter(import_sources).items() if count > 1]
    assert not dupes, (
        f"Duplicate imports from: {dupes}\n"
        "Rule from .github/copilot-instructions.md:138"
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
