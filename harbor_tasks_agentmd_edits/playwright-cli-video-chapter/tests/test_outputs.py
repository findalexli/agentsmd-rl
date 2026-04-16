#!/usr/bin/env python3
"""
Tests for playwright-cli video-chapter command.

This task requires BOTH:
1. Implementing the video-chapter CLI command and MCP tool (code)
2. Updating SKILL.md documentation to include the new command (config)
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")

# Path constants
SKILL_MD = REPO / "packages/playwright-core/src/tools/cli-client/skill/SKILL.md"
VIDEO_RECORDING_MD = REPO / "packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md"
COMMANDS_TS = REPO / "packages/playwright-core/src/tools/cli-daemon/commands.ts"
VIDEO_TS = REPO / "packages/playwright-core/src/tools/backend/video.ts"
CLI_DOCS = REPO / "docs/src/getting-started-cli.md"


def _run_pytest(test_func_name: str) -> tuple[bool, str]:
    """Helper to run a specific test and return result."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"""
import sys
sys.path.insert(0, '/tests')
from test_outputs import {test_func_name}
try:
    {test_func_name}()
    print("PASS")
except AssertionError as e:
    print(f"FAIL: {{e}}")
except Exception as e:
    print(f"ERROR: {{e}}")
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO),
        )
        output = result.stdout.strip() + result.stderr.strip()
        return "PASS" in output, output
    except Exception as e:
        return False, str(e)


# ============================================================================
# CATEGORY 1: CODE BEHAVIOR TESTS
# ============================================================================

def test_video_chapter_command_defined():
    """
    The videoChapter command must be defined in commands.ts.
    This is the primary functional change - adding CLI command registration.
    """
    assert COMMANDS_TS.exists(), f"commands.ts not found at {COMMANDS_TS}"
    content = COMMANDS_TS.read_text()

    # Check for videoChapter command definition
    assert "const videoChapter = declareCommand" in content, \
        "videoChapter command not defined in commands.ts"
    assert "name: 'video-chapter'" in content, \
        "video-chapter command name not found"
    assert "browser_video_chapter" in content, \
        "browser_video_chapter tool name not found"

    # Check that it's added to the commands array
    assert "videoChapter," in content or "videoChapter" in content.split("commandsArray")[1], \
        "videoChapter not added to commands array"


def test_video_chapter_tool_defined():
    """
    The browser_video_chapter MCP tool must be defined in video.ts.
    This registers the backend tool that the CLI command calls.
    """
    assert VIDEO_TS.exists(), f"video.ts not found at {VIDEO_TS}"
    content = VIDEO_TS.read_text()

    # Check for videoChapter tool definition
    assert "const videoChapter = defineTool" in content, \
        "videoChapter tool not defined in video.ts"
    assert "name: 'browser_video_chapter'" in content, \
        "browser_video_chapter tool name not found"
    assert "tab.page.overlay.chapter" in content, \
        "overlay.chapter API call not found"

    # Check schema includes expected parameters
    assert "title" in content, "title parameter not in schema"
    assert "description" in content, "description parameter not in schema"
    assert "duration" in content, "duration parameter not in schema"


def test_video_chapter_exported():
    """
    The videoChapter tool must be exported from video.ts.
    """
    assert VIDEO_TS.exists(), f"video.ts not found at {VIDEO_TS}"
    content = VIDEO_TS.read_text()

    # Check export array includes videoChapter
    export_section = content.split("export default")[1] if "export default" in content else ""
    assert "videoChapter" in export_section, \
        "videoChapter not in default export array"


def test_video_tools_renamed():
    """
    The existing video tools should be renamed from camelCase startVideo/stopVideo
    to videoStart/videoStop for consistency.
    """
    assert VIDEO_TS.exists(), f"video.ts not found at {VIDEO_TS}"
    content = VIDEO_TS.read_text()

    # New naming convention
    assert "const videoStart = defineTool" in content, \
        "videoStart naming not found (should be renamed from startVideo)"
    assert "const videoStop = defineTool" in content, \
        "videoStop naming not found (should be renamed from stopVideo)"


# ============================================================================
# CATEGORY 2: CONFIG/DOCUMENTATION UPDATE TESTS (REQUIRED for AgentMD-Edit)
# ============================================================================

def test_skill_md_documents_video_chapter():
    """
    SKILL.md must document the video-chapter command.
    This is a required config edit - the skill documentation must be updated.

    Origin: agent_config - SKILL.md is a Tier 1 agent instruction file.
    The SKILL.md has a DevTools section that lists all available commands.
    """
    assert SKILL_MD.exists(), f"SKILL.md not found at {SKILL_MD}"
    content = SKILL_MD.read_text()

    # Must include video-chapter command example
    assert "video-chapter" in content, \
        "SKILL.md does not document video-chapter command"

    # Should show usage with title argument
    assert "playwright-cli video-chapter" in content, \
        "SKILL.md missing video-chapter command example"

    # Should show options (description and duration)
    assert "--description" in content or 'description=' in content, \
        "SKILL.md missing --description option documentation"


def test_video_recording_md_documents_chapters():
    """
    video-recording.md must document chapter markers.
    This is a detailed reference guide that should show how to use chapters.

    Origin: pr_diff - The PR adds chapter examples to this reference doc.
    """
    assert VIDEO_RECORDING_MD.exists(), f"video-recording.md not found at {VIDEO_RECORDING_MD}"
    content = VIDEO_RECORDING_MD.read_text()

    # Must include chapter marker examples
    assert "video-chapter" in content, \
        "video-recording.md does not show video-chapter usage"

    # Should show chapter marker for section transitions
    chapter_count = content.count("video-chapter")
    assert chapter_count >= 2, \
        f"video-recording.md should show at least 2 chapter examples, found {chapter_count}"

    # Should document the chapter card functionality
    assert "chapter" in content.lower(), \
        "video-recording.md should mention 'chapter' concept"


def test_cli_docs_lists_video_chapter():
    """
    The CLI getting started docs should list the video-chapter command.

    Origin: pr_diff - The PR updates the command summary table.
    """
    assert CLI_DOCS.exists(), f"getting-started-cli.md not found at {CLI_DOCS}"
    content = CLI_DOCS.read_text()

    # Must include video-chapter in command list
    assert "video-chapter" in content, \
        "getting-started-cli.md does not list video-chapter command"


# ============================================================================
# CATEGORY 3: COMPILATION/SYNTAX CHECKS
# ============================================================================

def test_typescript_compiles():
    """
    The modified TypeScript files must compile without errors.

    Origin: static - TypeScript syntax validation.
    """
    # Run tsc check on the modified files
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck",
         "packages/playwright-core/src/tools/backend/video.ts",
         "packages/playwright-core/src/tools/cli-daemon/commands.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Allow it to pass if tsc isn't available, but fail on actual errors
    if result.returncode != 0:
        stderr_lower = result.stderr.lower()
        stdout_lower = result.stdout.lower()
        # Only fail on actual type/syntax errors, not on missing config
        if "error" in stderr_lower or "error" in stdout_lower:
            # Filter out module resolution errors which are common in partial builds
            actual_errors = [
                line for line in (result.stdout + result.stderr).split("\n")
                if "error" in line.lower() and "ts" in line.lower()
            ]
            if actual_errors:
                assert False, f"TypeScript errors found: {actual_errors[:5]}"


# ============================================================================
# MAIN: Run all tests and write reward
# ============================================================================

def main():
    tests = [
        # Code behavior tests (fail_to_pass)
        ("video_chapter_command_defined", test_video_chapter_command_defined, "fail_to_pass"),
        ("video_chapter_tool_defined", test_video_chapter_tool_defined, "fail_to_pass"),
        ("video_chapter_exported", test_video_chapter_exported, "fail_to_pass"),
        ("video_tools_renamed", test_video_tools_renamed, "fail_to_pass"),

        # Config/documentation tests (fail_to_pass - config edit required)
        ("skill_md_documents_video_chapter", test_skill_md_documents_video_chapter, "fail_to_pass"),
        ("video_recording_md_documents_chapters", test_video_recording_md_documents_chapters, "fail_to_pass"),
        ("cli_docs_lists_video_chapter", test_cli_docs_lists_video_chapter, "fail_to_pass"),

        # Compilation check (pass_to_pass)
        ("typescript_compiles", test_typescript_compiles, "pass_to_pass"),
    ]

    passed = 0
    failed = 0
    results = []

    for test_id, test_func, test_type in tests:
        try:
            test_func()
            results.append((test_id, "PASS", test_type))
            passed += 1
        except AssertionError as e:
            results.append((test_id, "FAIL", str(e)))
            failed += 1
        except Exception as e:
            results.append((test_id, "ERROR", str(e)))
            failed += 1

    # Print results
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    for test_id, status, detail in results:
        status_symbol = "✓" if status == "PASS" else "✗"
        print(f"  {status_symbol} {test_id}: {status}")
        if status != "PASS":
            print(f"      {detail[:100]}")

    # Binary reward: all must pass
    reward = 1 if failed == 0 else 0

    # Write reward
    Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
    Path("/logs/verifier/reward.txt").write_text(str(reward))

    print(f"\nReward: {reward}")
    return reward


if __name__ == "__main__":
    sys.exit(main())
