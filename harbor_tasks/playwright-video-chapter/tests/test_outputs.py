"""Test outputs for playwright-video-chapter task.

This validates both code changes (video-chapter feature implementation)
and config/documentation updates (SKILL.md, video-recording.md, getting-started-cli.md).
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")
VIDEO_TS = REPO / "packages/playwright-core/src/tools/backend/video.ts"
COMMANDS_TS = REPO / "packages/playwright-core/src/tools/cli-daemon/commands.ts"
SKILL_MD = REPO / "packages/playwright-core/src/tools/cli-client/skill/SKILL.md"
VIDEO_RECORDING_MD = REPO / "packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md"
GETTING_STARTED_MD = REPO / "docs/src/getting-started-cli.md"


def _read_file(path: Path) -> str:
    """Read file content."""
    if not path.exists():
        return ""
    return path.read_text()


# ============================================================================
# CODE BEHAVIOR TESTS (fail_to_pass)
# ============================================================================

def test_video_chapter_tool_exists():
    """[f2p] video.ts must contain the videoChapter tool definition."""
    content = _read_file(VIDEO_TS)
    assert "const videoChapter = defineTool" in content, "videoChapter tool definition missing"
    assert "browser_video_chapter" in content, "browser_video_chapter tool name missing"
    assert "tab.page.overlay.chapter" in content, "overlay.chapter() call missing"
    assert "Chapter title" in content, "Chapter title param missing"
    assert "duration" in content, "duration param missing"


def test_video_chapter_command_exists():
    """[f2p] commands.ts must contain the video-chapter CLI command."""
    content = _read_file(COMMANDS_TS)
    assert "const videoChapter = declareCommand" in content, "videoChapter command definition missing"
    assert "name: 'video-chapter'" in content, "video-chapter command name missing"
    assert "Add a chapter marker to the video recording" in content, "video-chapter description missing"
    assert "browser_video_chapter" in content, "browser_video_chapter tool reference missing"


def test_video_chapter_in_commands_array():
    """[f2p] commandsArray must include videoChapter."""
    content = _read_file(COMMANDS_TS)
    # Find the commandsArray and check videoChapter is in it
    # The array should have: videoStart, videoStop, videoChapter, devtoolsShow
    assert "videoChapter," in content, "videoChapter not added to commandsArray"
    # Verify ordering: videoStop, then videoChapter
    vstop_pos = content.find("videoStop,")
    vchapter_pos = content.find("videoChapter,")
    devtools_pos = content.find("devtoolsShow,")
    assert vstop_pos > 0, "videoStop not in commandsArray"
    assert vchapter_pos > 0, "videoChapter not in commandsArray"
    assert devtools_pos > 0, "devtoolsShow not in commandsArray"
    assert vstop_pos < vchapter_pos < devtools_pos, "videoChapter should be between videoStop and devtoolsShow"


def test_video_ts_variable_renames():
    """[f2p] video.ts should rename startVideo/stopVideo to videoStart/videoStop."""
    content = _read_file(VIDEO_TS)
    # Variables should be renamed
    assert "const videoStart = defineTool" in content, "videoStart variable definition missing"
    assert "const videoStop = defineTool" in content, "videoStop variable definition missing"
    # Old names should not exist (except in export default)
    assert "const startVideo = defineTool" not in content, "Old startVideo variable still present"
    assert "const stopVideo = defineTool" not in content, "Old stopVideo variable still present"


def test_video_ts_exports_updated():
    """[f2p] video.ts export default should include all three tools."""
    content = _read_file(VIDEO_TS)
    export_section = content[content.find("export default"):]
    assert "videoStart," in export_section, "videoStart missing from exports"
    assert "videoStop," in export_section, "videoStop missing from exports"
    assert "videoChapter," in export_section, "videoChapter missing from exports"


# ============================================================================
# CONFIG/DOCUMENTATION UPDATE TESTS (fail_to_pass)
# ============================================================================

def test_skill_md_has_video_chapter():
    """[f2p][config_edit] SKILL.md must document the video-chapter command."""
    content = _read_file(SKILL_MD)
    assert "video-chapter" in content, "SKILL.md missing video-chapter command"
    # Should have the full example with options
    assert "--description=" in content, "SKILL.md missing --description option example"
    assert "--duration=" in content, "SKILL.md missing --duration option example"


def test_video_recording_md_has_chapter_examples():
    """[f2p][config_edit] video-recording.md must have chapter marker examples."""
    content = _read_file(VIDEO_RECORDING_MD)
    # Should mention chapter markers
    assert "chapter" in content.lower(), "video-recording.md missing chapter references"
    # Should have at least one example with --description
    assert "--description" in content, "video-recording.md missing --description examples"
    # Should have at least 2 chapter examples ("Getting Started" and "Filling Form")
    chapter_count = content.count('playwright-cli video-chapter')
    assert chapter_count >= 2, f"Expected at least 2 video-chapter examples, found {chapter_count}"


def test_getting_started_cli_md_updated():
    """[f2p][config_edit] getting-started-cli.md must include video-chapter in CLI reference."""
    content = _read_file(GETTING_STARTED_MD)
    assert "video-chapter" in content, "getting-started-cli.md missing video-chapter command"
    assert "add chapter marker" in content.lower() or "chapter marker" in content.lower(), \
        "getting-started-cli.md missing chapter marker description"


# ============================================================================
# SYNTAX/PASS-TO-PASS TESTS
# ============================================================================

def test_typescript_syntax_valid():
    """[p2p] TypeScript files should have valid syntax (basic checks)."""
    # Check for obvious syntax errors like mismatched braces
    for path in [VIDEO_TS, COMMANDS_TS]:
        content = _read_file(path)
        if not content:
            continue
        # Basic brace matching
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, f"{path.name}: mismatched braces"
        open_parens = content.count('(')
        close_parens = content.count(')')
        assert open_parens == close_parens, f"{path.name}: mismatched parentheses"


def test_skill_md_structure_valid():
    """[p2p] SKILL.md should have valid frontmatter structure."""
    content = _read_file(SKILL_MD)
    assert content.startswith("---"), "SKILL.md missing frontmatter start"
    assert "name:" in content, "SKILL.md missing name in frontmatter"
    assert "description:" in content, "SKILL.md missing description in frontmatter"


def test_commands_ts_declare_command_usage():
    """[p2p] videoChapter command should properly use declareCommand API."""
    content = _read_file(COMMANDS_TS)
    # Find videoChapter definition
    idx = content.find("const videoChapter = declareCommand")
    assert idx > 0, "videoChapter declaration not found"
    section = content[idx:idx+1000]
    # Should have required fields
    assert "name:" in section, "videoChapter missing name field"
    assert "description:" in section, "videoChapter missing description field"
    assert "category:" in section, "videoChapter missing category field"
    assert "toolName:" in section, "videoChapter missing toolName field"
    assert "toolParams:" in section, "videoChapter missing toolParams field"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_snippets_npm():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_pip():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -r utils/doclint/linting-code-snippets/python/requirements.txt'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_mvn():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'mvn package'], cwd=os.path.join(REPO, 'utils/doclint/linting-code-snippets/java'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_node():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/doclint/linting-code-snippets/cli.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npx():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright install --with-deps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm_2():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_verify_clean_tree():
    """pass_to_pass | CI job 'docs & lint' → step 'Verify clean tree'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ -n $(git status -s) ]]; then\n  echo "ERROR: tree is dirty after npm run build:"\n  git diff\n  exit 1\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify clean tree' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_audit_prod_npm_dependencies():
    """pass_to_pass | CI job 'docs & lint' → step 'Audit prod NPM dependencies'"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/check_audit.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Audit prod NPM dependencies' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")