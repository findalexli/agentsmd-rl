"""
Task: playwright-video-chapter-command
Repo: microsoft/playwright @ a8ea6558c5f28f3e7a7d8a39d52c732053eee6a1
PR:   39891

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    files = [
        "packages/playwright-core/src/tools/backend/video.ts",
        "packages/playwright-core/src/tools/cli-daemon/commands.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"File not found: {f}"
        # Use node to check TypeScript syntax via acorn-like parse
        r = subprocess.run(
            ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{p}', 'utf8');
// Strip TypeScript-specific syntax for basic syntax validation
const stripped = src
    .replace(/:\\s*(string|number|boolean|void|any|object)\\b/g, '')
    .replace(/import\\s+type\\s+/g, 'import ')
    .replace(/<[^>]+>/g, '');
try {{
    // Basic brace/paren/bracket balance check
    let depth = {{}};
    const pairs = {{'(': ')', '[': ']', '{{': '}}'}}
    const stack = [];
    for (const ch of stripped) {{
        if ('([{{'.includes(ch)) stack.push(pairs[ch]);
        else if (')]}}'.includes(ch)) {{
            if (stack.length === 0 || stack.pop() !== ch) {{
                process.exit(1);
            }}
        }}
    }}
    if (stack.length !== 0) process.exit(1);
    process.exit(0);
}} catch(e) {{
    process.exit(1);
}}
"""],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Syntax check failed for {{f}}: {{r.stderr}}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (CODE EXECUTION)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_video_chapter_tool_defined():
    """video.ts defines a browser_video_chapter MCP tool with title, description, duration params."""
    code = """
const fs = require('fs');
const content = fs.readFileSync(
    '/workspace/playwright/packages/playwright-core/src/tools/backend/video.ts', 'utf8'
);
const result = {
    hasToolName: /name:\\s*['"]browser_video_chapter['"]/.test(content),
    hasTitleParam: /title:\\s*z\\.string\\(\\)/.test(content),
    hasDescParam: /description:\\s*z\\.string\\(\\)\\.optional\\(\\)/.test(content),
    hasDurationParam: /duration:\\s*z\\.number\\(\\)\\.optional\\(\\)/.test(content),
    hasHandle: /handle:\\s*async/.test(content) && content.includes('overlay.chapter'),
};
console.log(JSON.stringify(result));
if (!result.hasToolName || !result.hasTitleParam || !result.hasDescParam || !result.hasDurationParam || !result.hasHandle)
    process.exit(1);
"""
    r = subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"video_chapter tool not properly defined: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["hasToolName"], "Missing tool name 'browser_video_chapter'"
    assert data["hasTitleParam"], "Missing 'title' z.string() param in inputSchema"
    assert data["hasDescParam"], "Missing optional 'description' param in inputSchema"
    assert data["hasDurationParam"], "Missing optional 'duration' param in inputSchema"
    assert data["hasHandle"], "Missing handle function calling overlay.chapter"


# [pr_diff] fail_to_pass
def test_video_chapter_tool_exported():
    """videoChapter tool is included in the default export array of video.ts."""
    code = """
const fs = require('fs');
const content = fs.readFileSync(
    '/workspace/playwright/packages/playwright-core/src/tools/backend/video.ts', 'utf8'
);
// Find the export default [...] section and check videoChapter is in it
const exportMatch = content.match(/export\\s+default\\s+\\[([^\\]]+)\\]/s);
if (!exportMatch) process.exit(1);
const exports = exportMatch[1];
// Check that a variable referencing the chapter tool is exported
// (could be videoChapter, chapterVideo, etc.)
if (!exports.includes('hapter')) process.exit(1);
console.log('exported');
"""
    r = subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"videoChapter not in default export: {r.stderr}"
    assert "exported" in r.stdout, "videoChapter tool not exported from video.ts"


# [pr_diff] fail_to_pass
def test_video_chapter_command_declared():
    """commands.ts declares a 'video-chapter' CLI command mapping to browser_video_chapter."""
    code = """
const fs = require('fs');
const content = fs.readFileSync(
    '/workspace/playwright/packages/playwright-core/src/tools/cli-daemon/commands.ts', 'utf8'
);
const result = {
    hasCommandName: /name:\\s*['"]video-chapter['"]/.test(content),
    hasToolMapping: /toolName:\\s*['"]browser_video_chapter['"]/.test(content),
    hasTitleArg: /title:\\s*z\\.string\\(\\)/.test(content),
    hasDescOption: content.includes('description') && content.includes('.optional()'),
    hasDurationOption: content.includes('duration') && content.includes('numberArg'),
    hasCategory: /category:\\s*['"]devtools['"]/.test(content),
};
console.log(JSON.stringify(result));
if (!result.hasCommandName || !result.hasToolMapping || !result.hasTitleArg)
    process.exit(1);
"""
    r = subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"video-chapter command not declared: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["hasCommandName"], "Command name 'video-chapter' not found"
    assert data["hasToolMapping"], "toolName 'browser_video_chapter' mapping not found"
    assert data["hasTitleArg"], "Missing 'title' positional arg"


# [pr_diff] fail_to_pass
def test_video_chapter_in_commands_array():
    """videoChapter is registered in the commandsArray in commands.ts."""
    code = """
const fs = require('fs');
const content = fs.readFileSync(
    '/workspace/playwright/packages/playwright-core/src/tools/cli-daemon/commands.ts', 'utf8'
);
// Find commandsArray and check for videoChapter (or similar) between videoStop and devtoolsShow
const arrayMatch = content.match(/const\\s+commandsArray[^=]*=\\s*\\[([\\s\\S]*?)\\];/);
if (!arrayMatch) { console.error('commandsArray not found'); process.exit(1); }
const arrayContent = arrayMatch[1];
// Must contain a reference to the chapter command variable
if (!/\\bvideo[Cc]hapter\\b/.test(arrayContent) && !/\\bchapter[Vv]ideo\\b/.test(arrayContent)) {
    console.error('No chapter command in commandsArray');
    process.exit(1);
}
console.log('registered');
"""
    r = subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"videoChapter not in commandsArray: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — tool export structure validation (CODE EXECUTION)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tool_export_structure():
    """video.ts export array contains exactly videoStart, videoStop, videoChapter in order."""
    code = """
const fs = require('fs');
const content = fs.readFileSync(
    '/workspace/playwright/packages/playwright-core/src/tools/backend/video.ts', 'utf8'
);
// Check the export default array has the expected structure
const exportMatch = content.match(/export\\s+default\\s*\\[\\s*([^\\]]+)\\s*\\]/s);
if (!exportMatch) {
    console.error('No export default found');
    process.exit(1);
}
const exportContent = exportMatch[1];
// Must have exactly 3 items (renamed start/stop plus new chapter)
const items = exportContent.split(',').map(s => s.trim()).filter(s => s.length > 0);
if (items.length !== 3) {
    console.error('Expected 3 exports, got:', items.length);
    process.exit(1);
}
// Check names are present
const hasVideoStart = /videoStart|startVideo/.test(exportContent);
const hasVideoStop = /videoStop|stopVideo/.test(exportContent);
const hasVideoChapter = /videoChapter/.test(exportContent);
if (!hasVideoStart || !hasVideoStop || !hasVideoChapter) {
    console.error('Missing required exports');
    process.exit(1);
}
console.log(JSON.stringify({ items: items.length, ok: true }));
"""
    r = subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Export structure check failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("ok") == True, "Export structure validation failed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .claude/skills/playwright-dev/tools.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/playwright-dev/tools.md:276-279
def test_skill_md_documents_video_chapter():
    """SKILL.md must document the video-chapter CLI command with usage example."""
    skill_md = Path(REPO) / "packages/playwright-core/src/tools/cli-client/skill/SKILL.md"
    content = skill_md.read_text()
    assert "video-chapter" in content, \
        "SKILL.md should document the video-chapter command"
    # Must show usage with arguments, not just mention the name
    assert "--description" in content or "--duration" in content, \
        "SKILL.md should show video-chapter usage with options (--description or --duration)"


# [agent_config] fail_to_pass — .claude/skills/playwright-dev/tools.md:276-279
def test_video_recording_ref_documents_chapters():
    """video-recording.md reference must include chapter command examples."""
    ref_md = Path(REPO) / "packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md"
    content = ref_md.read_text()
    assert "video-chapter" in content, \
        "video-recording.md should include video-chapter command examples"
    # Must show at least one concrete example with a title
    assert 'video-chapter "' in content or "video-chapter '" in content, \
        "video-recording.md should show video-chapter with a title argument"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — documentation update
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_getting_started_cli_documents_video_chapter():
    """getting-started-cli.md must list video-chapter in the DevTools commands section."""
    cli_md = Path(REPO) / "docs/src/getting-started-cli.md"
    content = cli_md.read_text()
    assert "video-chapter" in content, \
        "getting-started-cli.md should list the video-chapter command"


# [pr_diff] fail_to_pass
def test_getting_started_cli_format():
    """getting-started-cli.md shows video-chapter with proper format <title>."""
    cli_md = Path(REPO) / "docs/src/getting-started-cli.md"
    content = cli_md.read_text()
    # Check that it shows the expected format: video-chapter <title>
    assert "video-chapter <title>" in content or 'video-chapter "' in content, \
        "getting-started-cli.md should show video-chapter with title placeholder or example"
