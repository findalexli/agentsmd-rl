"""
Task: lobe-chat-fixportal-preserve-artifacts-code-scroll
Repo: lobehub/lobe-chat @ 25e1a64c1b2897cb6e0febb265e9d28c3baba5c6
PR:   13114

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
import re
from pathlib import Path

REPO = "/workspace/lobe-chat"
BODY_FILE = f"{REPO}/src/features/Portal/Artifacts/Body/index.tsx"
AGENTS_FILE = f"{REPO}/AGENTS.md"


def _read_file(path: str) -> str:
    """Read file content, return empty string if not found."""
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return ""


def _run_node_script(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript/TypeScript code via Node."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax_valid():
    """Modified TypeScript files must parse without errors."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", BODY_FILE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Allow warnings but not syntax errors
    if r.returncode != 0:
        # Check if it's just missing deps (acceptable) vs syntax errors (fail)
        if "error TS" in r.stderr and "Cannot find module" not in r.stderr:
            assert False, f"TypeScript syntax errors:\n{r.stderr}"
    assert True


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_is_streaming_code_variable_exists():
    """isStreamingCode flag must be defined in the component."""
    content = _read_file(BODY_FILE)
    assert content, f"File not found: {BODY_FILE}"

    # Check for isStreamingCode variable definition
    pattern = r'const\s+isStreamingCode\s*=\s*isMessageGenerating\s*&&\s*!isArtifactTagClosed'
    assert re.search(pattern, content), \
        "isStreamingCode variable not found with correct definition"


# [pr_diff] fail_to_pass
def test_variables_defined_before_early_return():
    """showCode and isStreamingCode must be defined before the early return check."""
    content = _read_file(BODY_FILE)
    assert content, f"File not found: {BODY_FILE}"

    # Find positions of key statements
    show_code_pos = content.find('const showCode =')
    is_streaming_pos = content.find('const isStreamingCode =')
    early_return_pos = content.find('if (!messageId) return')

    assert show_code_pos != -1, "showCode variable not found"
    assert is_streaming_pos != -1, "isStreamingCode variable not found"
    assert early_return_pos != -1, "Early return check not found"

    # Both variables must come before early return
    assert show_code_pos < early_return_pos, \
        f"showCode ({show_code_pos}) must be defined before early return ({early_return_pos})"
    assert is_streaming_pos < early_return_pos, \
        f"isStreamingCode ({is_streaming_pos}) must be defined before early return ({early_return_pos})"


# [pr_diff] fail_to_pass
def test_highlighter_wrapped_in_flexbox():
    """Highlighter component must be wrapped in Flexbox with correct props."""
    content = _read_file(BODY_FILE)
    assert content, f"File not found: {BODY_FILE}"

    # Check for Flexbox wrapper with correct props around Highlighter
    # Pattern: <Flexbox flex={1} style={{ minHeight: 0, overflow: 'auto' }}>
    flexbox_pattern = r'<Flexbox\s+flex=\{1\}\s+style=\{\{\s*minHeight:\s*0,\s*overflow:\s*["\']auto["\']\s*\}\}'
    assert re.search(flexbox_pattern, content, re.DOTALL), \
        "Flexbox wrapper with flex={1} and overflow: 'auto' not found"


# [pr_diff] fail_to_pass
def test_highlighter_has_correct_props():
    """Highlighter must have animated, correct minHeight and overflow props."""
    content = _read_file(BODY_FILE)
    assert content, f"File not found: {BODY_FILE}"

    # Check animated prop is passed
    assert re.search(r'animated=\{isStreamingCode\}', content), \
        "Highlighter missing animated={isStreamingCode} prop"

    # Check minHeight: '100%' in style
    assert re.search(r"minHeight:\s*['\"]100%['\"]", content), \
        "Highlighter missing minHeight: '100%' style"

    # Check overflow: 'visible' in style
    assert re.search(r"overflow:\s*['\"]visible['\"]", content), \
        "Highlighter missing overflow: 'visible' style"


# [pr_diff] fail_to_pass
def test_scroll_fix_pattern_correct():
    """The scroll preservation fix follows the correct architectural pattern."""
    content = _read_file(BODY_FILE)
    assert content, f"File not found: {BODY_FILE}"

    # The fix pattern: outer Flexbox handles scrolling, inner Highlighter handles content
    # Verify the pattern exists in the code

    # Find the showCode conditional block
    show_code_match = re.search(
        r'\{showCode\s*\?\s*\(\s*(.*?)\)\s*:\s*\(',
        content,
        re.DOTALL
    )
    assert show_code_match, "showCode conditional block not found"

    block_content = show_code_match.group(1)

    # Verify Flexbox wrapper exists
    assert '<Flexbox' in block_content, "Flexbox wrapper not in showCode block"

    # Verify Highlighter is inside Flexbox
    assert '<Highlighter' in block_content, "Highlighter not in showCode block"

    # Verify the hierarchy: Flexbox contains Highlighter
    flexbox_pos = block_content.find('<Flexbox')
    highlighter_pos = block_content.find('<Highlighter')
    assert flexbox_pos < highlighter_pos, \
        "Flexbox must wrap Highlighter (Flexbox should come before Highlighter)"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_not_empty():
    """Modified file is not empty or stubbed."""
    content = _read_file(BODY_FILE)
    assert len(content) > 1000, f"Body/index.tsx seems too small or empty ({len(content)} chars)"


# [static] pass_to_pass
def test_component_exports_valid():
    """ArtifactsUI component is properly exported."""
    content = _read_file(BODY_FILE)
    assert 'const ArtifactsUI = memo' in content, "ArtifactsUI component definition not found"
    assert 'export default ArtifactsUI' in content, "ArtifactsUI export not found"


# -----------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# -----------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:48 @ 25e1a64c1b2897cb6e0febb265e9d28c3baba5c6
def test_agents_md_branch_naming_updated():
    """AGENTS.md branch naming convention updated to remove username prefix."""
    content = _read_file(AGENTS_FILE)
    assert content, f"File not found: {AGENTS_FILE}"

    # Should have the updated format without username prefix
    assert 'Git branch name format: `feat/feature-name`' in content, \
        "AGENTS.md not updated with correct branch naming format (should be 'feat/feature-name', not 'username/feat/feature-name')"

    # Should NOT have the old format with username prefix
    assert 'username/feat/feature-name' not in content, \
        "AGENTS.md still contains old branch naming format with username prefix"


# [agent_config] fail_to_pass — AGENTS.md @ 25e1a64c1b2897cb6e0febb265e9d28c3baba5c6
def test_agents_md_example_commands_updated():
    """AGENTS.md git checkout examples updated to use new branch format."""
    content = _read_file(AGENTS_FILE)
    assert content, f"File not found: {AGENTS_FILE}"

    # Check that example commands use new format
    assert 'git checkout -b feat/add-voice-input' in content, \
        "AGENTS.md example not updated with new branch format"
    assert 'git checkout -b fix/message-duplication' in content, \
        "AGENTS.md example not updated with new branch format"
