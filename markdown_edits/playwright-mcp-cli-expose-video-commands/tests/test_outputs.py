"""Tests for playwright-mcp-cli-expose-video-commands task.

This task adds the video-chapter CLI command and MCP tool.
Tests verify:
1. The videoChapter tool is properly defined in backend/video.ts
2. The CLI command is registered in cli-daemon/commands.ts
3. SKILL.md documents the new video-chapter command
4. video-recording.md shows chapter marker examples
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")
BACKEND_VIDEO = REPO / "packages/playwright-core/src/tools/backend/video.ts"
CLI_COMMANDS = REPO / "packages/playwright-core/src/tools/cli-daemon/commands.ts"
SKILL_MD = REPO / "packages/playwright-core/src/tools/cli-client/skill/SKILL.md"
VIDEO_RECORDING_MD = REPO / "packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md"
GETTING_STARTED_MD = REPO / "docs/src/getting-started-cli.md"


def _read_file(path: Path) -> str:
    """Read file content, return empty string if file doesn't exist."""
    if not path.exists():
        return ""
    return path.read_text()


def _run_in_repo(cmd: list[str], timeout: int = 60, cwd: str = None) -> subprocess.CompletedProcess:
    """Run a command in the repo directory."""
    workdir = cwd or str(REPO)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=workdir,
    )


# ============================================================================
# CODE BEHAVIOR TESTS (Fail-to-Pass)
# ============================================================================

def test_video_chapter_tool_defined():
    """FAIL_TO_PASS: videoChapter tool must be defined in backend/video.ts

    The PR adds a new `videoChapter` tool that:
    - Has schema name 'browser_video_chapter'
    - Accepts title (required), description and duration (optional)
    - Calls tab.page.overlay.chapter() in the handler
    """
    content = _read_file(BACKEND_VIDEO)
    assert content, f"File not found: {BACKEND_VIDEO}"

    # Check for videoChapter constant definition
    assert "const videoChapter = defineTool" in content, \
        "videoChapter tool must be defined with defineTool"

    # Check for the tool schema name
    assert "name: 'browser_video_chapter'" in content, \
        "Tool must have schema name 'browser_video_chapter'"

    # Check for title parameter
    assert "title: z.string()" in content, \
        "Tool must accept title parameter"

    # Check for optional description parameter
    assert "description: z.string().optional()" in content, \
        "Tool must accept optional description parameter"

    # Check for optional duration parameter
    assert "duration: z.number().optional()" in content, \
        "Tool must accept optional duration parameter"

    # Check the handler calls overlay.chapter
    assert "tab.page.overlay.chapter(params.title" in content, \
        "Handler must call tab.page.overlay.chapter() with title"

    # Check for the response text
    assert "Chapter '" in content and "added." in content, \
        "Handler must add response text confirming chapter was added"

    # Check it's exported
    assert "videoChapter," in content or "videoChapter" in content.split("export default")[1], \
        "videoChapter must be exported in the default array"


def test_video_chapter_cli_command_registered():
    """FAIL_TO_PASS: video-chapter CLI command must be registered in commands.ts

    The PR adds a new 'video-chapter' CLI command with:
    - name: 'video-chapter'
    - category: 'devtools'
    - Required 'title' arg
    - Optional --description and --duration options
    """
    content = _read_file(CLI_COMMANDS)
    assert content, f"File not found: {CLI_COMMANDS}"

    # Check for videoChapter command definition
    assert "const videoChapter = declareCommand" in content, \
        "videoChapter command must be declared with declareCommand"

    # Check command name
    assert "name: 'video-chapter'" in content, \
        "Command must have name 'video-chapter'"

    # Check category
    assert "category: 'devtools'" in content, \
        "Command must be in 'devtools' category"

    # Check for title arg
    assert "title: z.string()" in content, \
        "Command must accept title argument"

    # Check for description option
    assert "description: z.string().optional()" in content, \
        "Command must accept --description option"

    # Check for duration option
    assert "duration: numberArg.optional()" in content, \
        "Command must accept --duration option"

    # Check tool mapping
    assert "toolName: 'browser_video_chapter'" in content, \
        "Command must map to 'browser_video_chapter' tool"

    # Check it's in the commands array
    assert "videoChapter," in content.split("commandsArray: AnyCommandSchema[]")[1] or \
           "videoChapter" in content.split("commandsArray")[1].split("];")[0], \
        "videoChapter must be added to commandsArray"


def test_typescript_compiles():
    """FAIL_TO_PASS: TypeScript must compile without errors after the changes.

    Run tsc to verify the modified files have no type errors.
    """
    result = _run_in_repo(
        ["npx", "tsc", "--noEmit", "-p", "packages/playwright-core/tsconfig.json"],
        timeout=120
    )

    # TypeScript may exit 0 even with errors in some configs, check stderr too
    error_text = result.stderr + result.stdout

    # Filter out errors that are not related to our files
    lines = error_text.split('\n')
    relevant_errors = []
    for line in lines:
        if 'error TS' in line:
            # Only count errors in our modified files
            if any(f in line for f in ['video.ts', 'commands.ts']):
                relevant_errors.append(line)

    assert len(relevant_errors) == 0, \
        f"TypeScript errors in modified files: {relevant_errors}"


# ============================================================================
# CONFIG/DOCUMENTATION UPDATE TESTS (Fail-to-Pass for agentmd-edit)
# ============================================================================

def test_skill_md_documents_video_chapter():
    """FAIL_TO_PASS: SKILL.md must document the video-chapter command.

    The SKILL.md is the primary agent instruction file. It must include
    an example of the video-chapter command in the DevTools section.
    """
    content = _read_file(SKILL_MD)
    assert content, f"File not found: {SKILL_MD}"

    # Check for video-chapter in the DevTools examples
    assert "video-chapter" in content, \
        "SKILL.md must document the 'video-chapter' command"

    # Check for the example with --description option
    assert "--description=" in content or "--description" in content, \
        "SKILL.md example should show --description option"

    # Check for the example with --duration option
    assert "--duration=" in content or "--duration" in content, \
        "SKILL.md example should show --duration option"


def test_video_recording_md_has_chapter_examples():
    """FAIL_TO_PASS: video-recording.md must show chapter marker examples.

    The video-recording.md reference guide must demonstrate how to use
    chapter markers during video recording workflows.
    """
    content = _read_file(VIDEO_RECORDING_MD)
    assert content, f"File not found: {VIDEO_RECORDING_MD}"

    # Check for chapter marker examples
    assert "video-chapter" in content, \
        "video-recording.md must show video-chapter examples"

    # Check for multiple chapter markers (showing workflow usage)
    chapter_count = content.count("video-chapter")
    assert chapter_count >= 2, \
        f"video-recording.md should show multiple chapter markers (found {chapter_count})"

    # Check for descriptive chapter examples
    assert "--description=" in content or "--description" in content, \
        "Examples should use --description option"

    # Check for duration option in examples
    assert "--duration=" in content or "--duration" in content, \
        "Examples should use --duration option"


def test_getting_started_cli_documents_video_chapter():
    """FAIL_TO_PASS: getting-started-cli.md must list video-chapter command.

    The main CLI documentation must include the video-chapter command
    in the command reference section.
    """
    content = _read_file(GETTING_STARTED_MD)
    assert content, f"File not found: {GETTING_STARTED_MD}"

    # Check for video-chapter in the command list
    assert "video-chapter" in content, \
        "getting-started-cli.md must list 'video-chapter' command"

    # Check that it's documented as taking a title argument
    chapter_line = [l for l in content.split('\n') if 'video-chapter' in l]
    if chapter_line:
        assert "<title>" in chapter_line[0] or "title" in chapter_line[0].lower(), \
            "Command documentation should show title argument"


# ============================================================================
# PASS_TO_PASS TESTS (Repo CI/CD compatibility)
# ============================================================================

def test_npm_run_lint_syntax_only():
    """PASS_TO_PASS: npm run lint-packages should pass on syntax.

    This is a pass-to-pass test that ensures the existing linting
    infrastructure still works after our changes.
    """
    result = _run_in_repo(
        ["npm", "run", "lint-packages"],
        timeout=120
    )

    # This may fail for unrelated reasons, but should not fail
    # due to syntax errors in our modified files
    error_text = result.stderr + result.stdout

    # Check for specific syntax/parse errors in our files
    if "video.ts" in error_text or "commands.ts" in error_text:
        # Extract relevant error context
        lines = error_text.split('\n')
        for i, line in enumerate(lines):
            if 'video.ts' in line or 'commands.ts' in line:
                context = lines[max(0, i-2):min(len(lines), i+3)]
                assert False, f"Lint error in modified files: {' '.join(context)}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
