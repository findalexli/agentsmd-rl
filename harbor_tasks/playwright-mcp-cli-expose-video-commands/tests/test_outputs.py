#!/usr/bin/env python3
"""
Test suite for Playwright MCP CLI video command exposure.

This validates:
1. Code changes: New video.ts module exists, capability renamed to 'devtools'
2. Config/documentation update: SKILL.md documents new video commands
"""

import subprocess
import json
from pathlib import Path
import sys

REPO = Path("/workspace/playwright")


def _run_typecheck(file_path: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run TypeScript type checking on a single file."""
    # Use npx tsc --noEmit for type checking
    return subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", str(file_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_node_script(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script and return result."""
    script_path = REPO / "_eval_tmp.js"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", str(script_path)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ============================================================================
# FAIL-TO-PASS TESTS: Code behavior
# ============================================================================

def test_video_module_exists():
    """Video tools module must exist with proper exports."""
    video_ts = REPO / "packages/playwright/src/mcp/browser/tools/video.ts"
    assert video_ts.exists(), "video.ts module must exist"

    content = video_ts.read_text()
    assert "browser_start_video" in content, "Must export browser_start_video tool"
    assert "browser_stop_video" in content, "Must export browser_stop_video tool"
    assert "export default" in content, "Must have default export"


def test_video_capability_is_devtools():
    """Video tools must use 'devtools' capability, not 'tracing'."""
    video_ts = REPO / "packages/playwright/src/mcp/browser/tools/video.ts"
    content = video_ts.read_text()

    # Video tools should use devtools capability
    assert "capability: 'devtools'" in content, "Video tools must use 'devtools' capability"

    # Should NOT use 'tracing' capability
    assert "capability: 'tracing'" not in content, "Video tools must NOT use 'tracing' capability"


def test_tracing_capability_renamed_to_devtools():
    """Tracing tools must have capability renamed from 'tracing' to 'devtools'."""
    tracing_ts = REPO / "packages/playwright/src/mcp/browser/tools/tracing.ts"
    content = tracing_ts.read_text()

    # Tracing should now use devtools capability
    assert "capability: 'devtools'" in content, "Tracing tools must use 'devtools' capability"

    # Should NOT use old 'tracing' capability
    assert "capability: 'tracing'" not in content, "Tracing tools must NOT use old 'tracing' capability"


def test_tools_registry_includes_video():
    """Tools registry must include video tools in correct order."""
    tools_ts = REPO / "packages/playwright/src/mcp/browser/tools.ts"
    content = tools_ts.read_text()

    # Must import video
    assert "import video from './tools/video';" in content, "Must import video module"

    # Must include video in browserTools array (after verify, before wait)
    assert "...video," in content, "Must include video in browserTools array"

    # Check import order: verify, then video, then wait
    verify_pos = content.find("import verify from './tools/verify';")
    video_pos = content.find("import video from './tools/video';")
    wait_pos = content.find("import wait from './tools/wait';")

    assert verify_pos < video_pos < wait_pos, "Imports must be in order: verify, video, wait"


def test_config_dts_has_devtools_capability():
    """Config type definitions must include 'devtools' capability."""
    config_dts = REPO / "packages/playwright/src/mcp/config.d.ts"
    content = config_dts.read_text()

    # Must have devtools in ToolCapability
    assert "'devtools'" in content, "ToolCapability must include 'devtools'"

    # Must NOT have 'tracing' anymore (replaced by devtools)
    assert "'tracing'" not in content, "ToolCapability must NOT include 'tracing' (replaced by devtools)"

    # Must document devtools in capabilities comment
    assert "devtools" in content.lower(), "Must document devtools capability"


def test_browser_context_factory_uses_devtools():
    """BrowserContextFactory must check for 'devtools' capability."""
    factory_ts = REPO / "packages/playwright/src/mcp/browser/browserContextFactory.ts"
    content = factory_ts.read_text()

    # Should check for 'devtools' capability
    assert "capabilities?.includes('devtools')" in content, "Must check for 'devtools' capability"


def test_program_cli_accepts_devtools():
    """CLI program must accept 'devtools' in --caps option."""
    program_ts = REPO / "packages/playwright/src/mcp/program.ts"
    content = program_ts.read_text()

    # Must document devtools in caps help
    assert "possible values: vision, pdf, devtools" in content, "Must document 'devtools' in --caps option"

    # Must handle 'tracing' -> 'devtools' migration
    assert "options.caps?.includes('tracing')" in content, "Must handle legacy 'tracing' capability"
    assert "options.caps.push('devtools')" in content, "Must add 'devtools' when 'tracing' is used"


def test_terminal_commands_include_video():
    """Terminal commands must include video-start and video-stop."""
    commands_ts = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_ts.read_text()

    # Must have videoStart command
    assert "videoStart = declareCommand" in content, "Must declare videoStart command"
    assert "name: 'video-start'" in content, "Must have video-start command name"
    assert "toolName: 'browser_start_video'" in content, "Must map to browser_start_video tool"

    # Must have videoStop command
    assert "videoStop = declareCommand" in content, "Must declare videoStop command"
    assert "name: 'video-stop'" in content, "Must have video-stop command name"
    assert "toolName: 'browser_stop_video'" in content, "Must map to browser_stop_video tool"

    # Both must be in devtools category
    assert "category: 'devtools'" in content, "Video commands must be in devtools category"

    # Must be registered in commandsArray
    assert "videoStart," in content, "videoStart must be in commandsArray"
    assert "videoStop," in content, "videoStop must be in commandsArray"


def test_terminal_program_passes_output_dir():
    """Terminal program must pass outputDir to session.run()."""
    program_ts = REPO / "packages/playwright/src/mcp/terminal/program.ts"
    content = program_ts.read_text()

    # Must pass outputDir in run-mcp-server args
    assert "`--output-dir=${outputDir}`" in content, "Must pass --output-dir to MCP server"

    # Must pass outputDir to session.run
    assert "session.run({ ...args, outputDir })" in content, "Must pass outputDir to session.run"


def test_command_parses_filename_with_output_dir():
    """Command parser must resolve filename against outputDir."""
    command_ts = REPO / "packages/playwright/src/mcp/terminal/command.ts"
    content = command_ts.read_text()

    assert "path.resolve(args.outputDir, args.filename)" in content, \
        "Must resolve filename against outputDir"


def test_run_code_in_correct_order():
    """runCode command must be in correct position (after resize, before navigation)."""
    commands_ts = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_ts.read_text()

    # runCode must be declared before tabs section (moved from devtools to core)
    run_code_pos = content.find("const runCode = declareCommand")
    tabs_section_pos = content.find("// Tabs")

    assert run_code_pos != -1, "runCode command must exist"
    assert tabs_section_pos != -1, "Tabs section must exist"
    assert run_code_pos < tabs_section_pos, "runCode must be declared before Tabs section"

    # runCode must be in commandsArray before navigation section
    assert "runCode," in content, "runCode must be in commandsArray"


# ============================================================================
# FAIL-TO-PASS TESTS: Config/documentation update (SKILL.md)
# ============================================================================

def test_skill_md_documents_video_commands():
    """SKILL.md must document the new video-start and video-stop commands."""
    skill_md = REPO / "packages/playwright/src/mcp/terminal/SKILL.md"
    assert skill_md.exists(), "SKILL.md must exist"

    content = skill_md.read_text()

    # Must document video-start command
    assert "playwright-cli video-start" in content, "SKILL.md must document video-start command"

    # Must document video-stop command
    assert "playwright-cli video-stop" in content, "SKILL.md must document video-stop command"

    # Should be in the DevTools section examples (after tracing-stop)
    devtools_section = content.find("### DevTools")
    assert devtools_section != -1, "Must have DevTools section"

    video_start_pos = content.find("playwright-cli video-start")
    tracing_stop_pos = content.find("playwright-cli tracing-stop")

    assert video_start_pos != -1, "video-start must be documented"
    assert tracing_stop_pos != -1, "tracing-stop must be documented"
    assert video_start_pos > tracing_stop_pos, "video commands must appear after tracing-stop"


def test_skill_md_consistent_formatting():
    """SKILL.md must maintain consistent formatting with other examples."""
    skill_md = REPO / "packages/playwright/src/mcp/terminal/SKILL.md"
    content = skill_md.read_text()

    # Video commands should follow same pattern as other commands (backticks, no extra blank lines)
    lines = content.split("\n")

    # Find video-start line
    video_start_lines = [i for i, line in enumerate(lines) if "playwright-cli video-start" in line]
    assert len(video_start_lines) == 1, "video-start should appear exactly once"

    video_start_line = lines[video_start_lines[0]]
    assert video_start_line.startswith("playwright-cli "), \
        "Video command should be in code block (no extra indentation)"


# ============================================================================
# PASS-TO-PASS TESTS: Code quality
# ============================================================================

def test_video_module_syntax_valid():
    """Video module must have valid TypeScript syntax."""
    video_ts = REPO / "packages/playwright/src/mcp/browser/tools/video.ts"
    result = _run_typecheck(video_ts)
    assert result.returncode == 0, f"TypeScript syntax error: {result.stdout}{result.stderr}"


def test_commands_module_syntax_valid():
    """Commands module must have valid TypeScript syntax."""
    commands_ts = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    result = _run_typecheck(commands_ts)
    assert result.returncode == 0, f"TypeScript syntax error: {result.stdout}{result.stderr}"


def test_no_debug_console_log_in_program():
    """Session class should not have debug console.log statements."""
    program_ts = REPO / "packages/playwright/src/mcp/terminal/program.ts"
    content = program_ts.read_text()

    # Should NOT have console.log(matchingDirs)
    assert "console.log(matchingDirs)" not in content, "Should remove debug console.log statement"


# ============================================================================
# Test runner
# ============================================================================

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
