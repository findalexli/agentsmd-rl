"""
Task: vscode-terminal-telemetry-unsandboxed-reason
Repo: microsoft/vscode @ a2d7b9e13bdbe52233ea06b2ca6bc69a81083772
PR:   306330

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

# AST-only because: TypeScript source — cannot import/execute without transpilation.
# All checks use regex on source files.

import re
from pathlib import Path

REPO = Path("/workspace/vscode")
TELEMETRY_FILE = REPO / "src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/runInTerminalToolTelemetry.ts"
TOOL_FILE = REPO / "src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_state_interface_has_property():
    """State interface must declare requestUnsandboxedExecutionReason: string | undefined."""
    src = TELEMETRY_FILE.read_text()
    assert re.search(
        r'requestUnsandboxedExecutionReason\s*:\s*string\s*\|\s*undefined\s*;',
        src,
    ), "State interface missing: requestUnsandboxedExecutionReason: string | undefined"


# [pr_diff] fail_to_pass
def test_data_event_type_has_property():
    """requestUnsandboxedExecutionReason: string | undefined must appear in both state param and TelemetryEvent type."""
    src = TELEMETRY_FILE.read_text()
    # The property declaration (string | undefined) must appear in both the logInvoke
    # state parameter and the local TelemetryEvent type alias within that method.
    matches = re.findall(
        r'requestUnsandboxedExecutionReason\s*:\s*string\s*\|\s*undefined',
        src,
    )
    assert len(matches) >= 2, (
        f"requestUnsandboxedExecutionReason: string | undefined should appear in both "
        f"state parameter and TelemetryEvent type (found {len(matches)})"
    )


# [pr_diff] fail_to_pass
def test_classification_has_property():
    """Telemetry event classification must include requestUnsandboxedExecutionReason with SystemMetaData/FeatureInsight."""
    src = TELEMETRY_FILE.read_text()
    assert re.search(
        r"requestUnsandboxedExecutionReason\s*:\s*\{\s*classification\s*:\s*'SystemMetaData'",
        src,
    ), "Telemetry classification missing requestUnsandboxedExecutionReason: { classification: 'SystemMetaData' ... }"
    assert re.search(
        r"requestUnsandboxedExecutionReason\s*:.*purpose\s*:\s*'FeatureInsight'",
        src,
    ), "Telemetry classification for requestUnsandboxedExecutionReason missing purpose: 'FeatureInsight'"


# [pr_diff] fail_to_pass
def test_mapping_includes_property():
    """Telemetry data construction must map requestUnsandboxedExecutionReason from state."""
    src = TELEMETRY_FILE.read_text()
    assert re.search(
        r'requestUnsandboxedExecutionReason\s*:\s*state\.requestUnsandboxedExecutionReason',
        src,
    ), "Telemetry data mapping missing: requestUnsandboxedExecutionReason: state.requestUnsandboxedExecutionReason"


# [pr_diff] fail_to_pass
def test_tool_passes_property():
    """runInTerminalTool.ts must pass requestUnsandboxedExecutionReason when reporting telemetry."""
    src = TOOL_FILE.read_text()
    assert re.search(
        r'requestUnsandboxedExecutionReason\s*:\s*args\.requestUnsandboxedExecutionReason',
        src,
    ), "Tool missing: requestUnsandboxedExecutionReason: args.requestUnsandboxedExecutionReason"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_properties_preserved():
    """Pre-existing telemetry mappings must still be present after the change."""
    src = TELEMETRY_FILE.read_text()
    assert re.search(r'isBackground\s*:\s*state\.isBackground', src), \
        "isBackground mapping removed"
    assert re.search(r'isNewSession\s*:\s*state\.isNewSession', src), \
        "isNewSession mapping removed"
    assert re.search(r'isSandbox\s*:\s*state\.isSandboxWrapped', src), \
        "isSandbox mapping removed"


# [static] pass_to_pass
def test_files_have_copyright_header():
    """Both modified files must retain the Microsoft copyright header."""
    for path in [TELEMETRY_FILE, TOOL_FILE]:
        header = path.read_text()[:300]
        assert 'Copyright' in header and 'Microsoft' in header, \
            f"Microsoft copyright header missing from {path.name}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:107 @ a2d7b9e13bdbe52233ea06b2ca6bc69a81083772
def test_property_indented_with_tabs():
    """New property lines must use tab indentation, not spaces (copilot-instructions.md:107)."""
    src = TELEMETRY_FILE.read_text()
    lines = [l for l in src.splitlines() if 'requestUnsandboxedExecutionReason' in l]
    assert lines, "requestUnsandboxedExecutionReason not found in telemetry file"
    for line in lines:
        if not line or not line[0].isspace():
            continue  # unindented line — no issue
        assert line[0] == '\t', \
            f"Line uses space indentation instead of tabs: {line!r}"
