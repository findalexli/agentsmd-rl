"""
Task: vscode-terminal-telemetry-unsandboxed-reason
Repo: microsoft/vscode @ a2d7b9e13bdbe52233ea06b2ca6bc69a81083772
PR:   306330

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = Path("/workspace/vscode")
TELEMETRY_FILE = REPO / "src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/runInTerminalToolTelemetry.ts"
TOOL_FILE = REPO / "src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts"

# Node.js script that uses the TypeScript compiler API to parse a TS file and
# report all occurrences of requestUnsandboxedExecutionReason as structured JSON.
_AST_ANALYSIS_JS = r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(FILEPATH, 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

const TARGET = 'requestUnsandboxedExecutionReason';
const results = { propertySignatures: [], propertyAssignments: [] };

function visit(node) {
    // Property signatures in type literals / interfaces
    if ((ts.isPropertySignature(node) || ts.isPropertyDeclaration(node)) && node.name) {
        const name = node.name.getText(sf);
        if (name === TARGET) {
            const entry = { name, kind: 'signature' };
            if (node.type) {
                entry.typeText = node.type.getText(sf);
                if (ts.isTypeLiteralNode(node.type)) {
                    entry.isTypeLiteral = true;
                    entry.typeMembers = [];
                    for (const member of node.type.members) {
                        if (ts.isPropertySignature(member) && member.name) {
                            entry.typeMembers.push({
                                name: member.name.getText(sf),
                                type: member.type ? member.type.getText(sf) : undefined,
                            });
                        }
                    }
                }
            }
            results.propertySignatures.push(entry);
        }
    }
    // Property assignments in object literals
    if (ts.isPropertyAssignment(node) && node.name) {
        const name = node.name.getText(sf);
        if (name === TARGET) {
            const entry = { name, kind: 'assignment', valueText: node.initializer.getText(sf) };
            if (ts.isPropertyAccessExpression(node.initializer)) {
                entry.objectName = node.initializer.expression.getText(sf);
                entry.propertyName = node.initializer.name.getText(sf);
            }
            results.propertyAssignments.push(entry);
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);
console.log(JSON.stringify(results));
"""


def _run_node(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = REPO / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
        )
    finally:
        script.unlink(missing_ok=True)


_report_cache: dict = {}


def _get_ast_report(file_path: Path) -> dict:
    """Parse a TS file with the TypeScript compiler API and return a structural report."""
    key = str(file_path)
    if key in _report_cache:
        return _report_cache[key]
    js = _AST_ANALYSIS_JS.replace("FILEPATH", json.dumps(str(file_path)))
    r = _run_node(js)
    assert r.returncode == 0, f"AST analysis failed: {r.stderr}"
    report = json.loads(r.stdout.strip())
    _report_cache[key] = report
    return report


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via TypeScript AST parsing
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_state_interface_has_property():
    """State interface declares requestUnsandboxedExecutionReason: string | undefined (AST)."""
    report = _get_ast_report(TELEMETRY_FILE)
    typed_sigs = [s for s in report["propertySignatures"]
                  if s.get("typeText") == "string | undefined"]
    assert len(typed_sigs) >= 1, (
        "requestUnsandboxedExecutionReason: string | undefined not found in any type declaration"
    )


# [pr_diff] fail_to_pass
def test_data_event_type_has_property():
    """requestUnsandboxedExecutionReason: string | undefined in both state param and TelemetryEvent type (AST)."""
    report = _get_ast_report(TELEMETRY_FILE)
    typed_sigs = [s for s in report["propertySignatures"]
                  if s.get("typeText") == "string | undefined"]
    assert len(typed_sigs) >= 2, (
        f"Expected >=2 declarations of requestUnsandboxedExecutionReason: string | undefined, "
        f"found {len(typed_sigs)}"
    )


# [pr_diff] fail_to_pass
def test_classification_has_property():
    """Telemetry classification includes requestUnsandboxedExecutionReason with SystemMetaData/FeatureInsight (AST)."""
    report = _get_ast_report(TELEMETRY_FILE)
    class_sigs = [s for s in report["propertySignatures"] if s.get("isTypeLiteral")]
    assert len(class_sigs) >= 1, (
        "No classification type literal found for requestUnsandboxedExecutionReason"
    )
    members = {m["name"]: m.get("type") for m in class_sigs[0].get("typeMembers", [])}
    assert members.get("classification") == "'SystemMetaData'", (
        f"classification should be 'SystemMetaData', got {members.get('classification')}"
    )
    assert members.get("purpose") == "'FeatureInsight'", (
        f"purpose should be 'FeatureInsight', got {members.get('purpose')}"
    )


# [pr_diff] fail_to_pass
def test_mapping_includes_property():
    """Telemetry data mapping passes state.requestUnsandboxedExecutionReason (AST)."""
    report = _get_ast_report(TELEMETRY_FILE)
    state_assigns = [a for a in report["propertyAssignments"]
                     if a.get("objectName") == "state"
                     and a.get("propertyName") == "requestUnsandboxedExecutionReason"]
    assert len(state_assigns) >= 1, (
        f"No mapping state.requestUnsandboxedExecutionReason found; "
        f"assignments: {[a.get('valueText') for a in report['propertyAssignments']]}"
    )


# [pr_diff] fail_to_pass
def test_tool_passes_property():
    """runInTerminalTool.ts passes args.requestUnsandboxedExecutionReason to telemetry (AST)."""
    report = _get_ast_report(TOOL_FILE)
    args_assigns = [a for a in report["propertyAssignments"]
                    if a.get("objectName") == "args"
                    and a.get("propertyName") == "requestUnsandboxedExecutionReason"]
    assert len(args_assigns) >= 1, (
        f"No args.requestUnsandboxedExecutionReason found; "
        f"assignments: {[a.get('valueText') for a in report['propertyAssignments']]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_properties_preserved():
    """Pre-existing telemetry mappings must still be present after the change."""
    src = TELEMETRY_FILE.read_text()
    for prop in ["isBackground", "isNewSession", "isSandbox"]:
        assert prop in src, f"Pre-existing telemetry property '{prop}' removed"


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
            continue
        assert line[0] == '\t', \
            f"Line uses space indentation instead of tabs: {line!r}"

# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from .github/workflows/*.yml
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes using tsgo native compiler (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsgo", "--project", "src/tsconfig.json", "--noEmit", "--skipLibCheck"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript typecheck (tsgo) failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_monaco_compile_check():
    """Repo's Monaco editor compile check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "monaco-compile-check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Monaco compile check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tsec_compile_check():
    """Repo's tsec security compile check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "tsec-compile-check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"tsec compile check failed:\n{r.stderr[-500:]}"
