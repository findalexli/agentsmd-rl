"""
Task: vscode-chat-copy-final-response
Repo: microsoft/vscode @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
PR:   306184

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import pytest
import subprocess
import json
import re
from pathlib import Path

REPO = Path("/workspace/vscode")
CHATMODEL_SRC = REPO / "src/vs/workbench/contrib/chat/common/model/chatModel.ts"
CHATMODEL_TEST = REPO / "src/vs/workbench/contrib/chat/test/common/model/chatModel.test.ts"
COPY_ACTIONS_SRC = REPO / "src/vs/workbench/contrib/chat/browser/actions/chatCopyActions.ts"
LIST_WIDGET_SRC = REPO / "src/vs/workbench/contrib/chat/browser/widget/chatListWidget.ts"
APPROVAL_TEST = REPO / "src/vs/workbench/contrib/chat/test/browser/agentSessions/agentSessionApprovalModel.test.ts"
CONTROLLER_TEST = REPO / "src/vs/workbench/contrib/chat/test/browser/agentSessions/localAgentSessionsController.test.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = REPO / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
        )
    finally:
        script.unlink(missing_ok=True)


def _extract_method_body(content: str, method_sig: str, max_chars: int = 3000) -> str:
    """Extract a method body by matching braces from its signature."""
    idx = content.find(method_sig)
    assert idx != -1, f"Method signature '{method_sig}' not found"
    brace_start = content.find("{", idx)
    assert brace_start != -1, f"No opening brace after '{method_sig}'"
    depth = 0
    for i in range(brace_start, min(brace_start + max_chars, len(content))):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                return content[idx : i + 1]
    return content[idx : brace_start + max_chars]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral: algorithm correctness via Node.js
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_getFinalResponse_algorithm():
    """getFinalResponse correctly extracts the last contiguous markdown block from response parts."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const src = readFileSync('src/vs/workbench/contrib/chat/common/model/chatModel.ts', 'utf-8');

// Find getFinalResponse method IMPLEMENTATION (not interface declaration)
// The interface has 'getFinalResponse(): string;' while implementation has 'getFinalResponse(): string {'
const sig = 'getFinalResponse(): string {';
const sigIdx = src.indexOf(sig);
if (sigIdx === -1) {
    process.stderr.write('getFinalResponse method not found in source');
    process.exit(1);
}

// Extract method body by brace matching
let bi = src.indexOf('{', sigIdx);
let depth = 0, ei = -1;
for (let i = bi; i < src.length; i++) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') { depth--; if (depth === 0) { ei = i; break; } }
}
if (ei === -1) { process.stderr.write('Unmatched braces'); process.exit(1); }

let body = src.substring(bi + 1, ei);

// Remove TS type annotations (e.g. ": string[]")
body = body.replace(/:\s*string\[\]/g, '');

// Build a standalone function using a Proxy to mock 'this' context.
// The Proxy returns the input parts array for any property containing "part"
// and returns a mock function for method calls (like inlineRefToRepr).
const fnCode = [
    'const self = new Proxy({}, {',
    '  get(_, prop) {',
    '    if (typeof prop === "string" && (prop.includes("Part") || prop.includes("part") || prop.includes("_resp"))) return inputParts;',
    '    return function() {',
    '      const p = arguments[0];',
    '      if (p && p.inlineReference !== undefined) return typeof p.inlineReference === "string" ? p.inlineReference : String(p.inlineReference);',
    '      return "";',
    '    };',
    '  }',
    '});',
    'return (function() {',
    body,
    '}).call(self);',
].join('\n');

let testFn;
try {
    testFn = new Function('inputParts', fnCode);
} catch (e) {
    process.stderr.write('Failed to create function from extracted body: ' + e.message);
    process.exit(1);
}

function runTest(name, parts, check) {
    try {
        const r = testFn(parts);
        return { test: name, pass: check(r), got: r };
    } catch (e) {
        return { test: name, pass: false, got: 'ERROR: ' + e.message };
    }
}

const results = [
    // Test 1: Last markdown after tool call
    runTest('after_tool_call', [
        { kind: 'markdownContent', content: { value: 'Early text' } },
        { kind: 'externalToolInvocationUpdate' },
        { kind: 'markdownContent', content: { value: 'Final text' } },
    ], r => r === 'Final text'),

    // Test 2: Skip trailing empty markdown and tool calls
    runTest('skip_trailing_empty', [
        { kind: 'markdownContent', content: { value: 'Before' } },
        { kind: 'externalToolInvocationUpdate' },
        { kind: 'markdownContent', content: { value: 'Answer: 42' } },
        { kind: 'externalToolInvocationUpdate' },
        { kind: 'markdownContent', content: { value: '' } },
    ], r => r === 'Answer: 42'),

    // Test 3: Only tool calls -> empty string
    runTest('no_markdown', [
        { kind: 'externalToolInvocationUpdate' },
    ], r => r === ''),

    // Test 4: All markdown, no tool calls -> joined
    runTest('all_markdown', [
        { kind: 'markdownContent', content: { value: 'Hello ' } },
        { kind: 'markdownContent', content: { value: 'World' } },
    ], r => r === 'Hello World'),

    // Test 5: Inline references included
    runTest('inline_ref', [
        { kind: 'externalToolInvocationUpdate' },
        { kind: 'markdownContent', content: { value: 'See ' } },
        { kind: 'inlineReference', inlineReference: 'https://example.com/' },
        { kind: 'markdownContent', content: { value: ' for details.' } },
    ], r => r.includes('See ') && r.includes('for details.')),
];

console.log(JSON.stringify(results));
""")
    assert r.returncode == 0, f"Node.js execution failed:\nstderr: {r.stderr}"
    output = r.stdout.strip()
    assert output, f"No output from Node.js script. stderr: {r.stderr}"
    results = json.loads(output)
    for t in results:
        assert t["pass"], (
            f"getFinalResponse scenario '{t['test']}' failed: got '{t['got']}'"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — interface declaration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interface_has_getFinalResponse():
    """IResponse interface declares getFinalResponse(): string."""
    content = CHATMODEL_SRC.read_text()
    iface_match = re.search(
        r"export\s+interface\s+IResponse\s*\{(.*?)\n\}",
        content,
        re.DOTALL,
    )
    assert iface_match, "IResponse interface not found in chatModel.ts"
    iface_body = iface_match.group(1)
    assert "getFinalResponse()" in iface_body, (
        "IResponse interface is missing getFinalResponse() declaration"
    )
    assert "string" in iface_body.split("getFinalResponse()")[1].split("\n")[0], (
        "getFinalResponse() should return string"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — action registration & overlay
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_action_registered_and_functional():
    """CopyFinalResponseAction is registered, calls getFinalResponse, writes to clipboard, gated by isResponse."""
    content = COPY_ACTIONS_SRC.read_text()
    assert "CopyFinalResponseAction" in content, (
        "CopyFinalResponseAction not found in chatCopyActions.ts"
    )
    assert "registerAction2" in content, (
        "CopyFinalResponseAction must be registered via registerAction2"
    )
    idx = content.find("CopyFinalResponseAction")
    action_block = content[idx : idx + 1500]
    assert "getFinalResponse()" in action_block, (
        "CopyFinalResponseAction must call getFinalResponse() on the response"
    )
    assert "clipboardService" in action_block.lower() or "writeText" in action_block, (
        "CopyFinalResponseAction must write to the clipboard"
    )
    assert "isResponse" in action_block, (
        "CopyFinalResponseAction must be gated by ChatContextKeys.isResponse"
    )


# [pr_diff] fail_to_pass
def test_context_key_in_overlay():
    """isResponse context key is added to createOverlay() in chatListWidget.ts."""
    content = LIST_WIDGET_SRC.read_text()
    overlay_idx = content.find("createOverlay")
    assert overlay_idx != -1, "createOverlay() call not found in chatListWidget.ts"
    window = content[overlay_idx : overlay_idx + 500]
    assert "isResponse.key" in window, (
        "ChatContextKeys.isResponse.key must be inside the createOverlay() call"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — unit tests & mocks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_unit_tests_added():
    """chatModel.test.ts contains getFinalResponse unit tests covering multiple scenarios."""
    content = CHATMODEL_TEST.read_text()
    assert "getFinalResponse" in content, (
        "chatModel.test.ts must have tests for getFinalResponse"
    )
    test_patterns = ["tool call", "empty", "inline"]
    matches = sum(1 for p in test_patterns if p.lower() in content.lower())
    assert matches >= 2, (
        f"Expected at least 2 distinct getFinalResponse test scenarios, found {matches}"
    )


# [pr_diff] fail_to_pass
def test_mocks_updated():
    """Mock IResponse objects include getFinalResponse in agent session test files."""
    found = 0
    for test_file in [APPROVAL_TEST, CONTROLLER_TEST]:
        if test_file.exists() and "getFinalResponse" in test_file.read_text():
            found += 1
    assert found >= 1, (
        "At least one mock response in agentSessions test files must include getFinalResponse"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_original_interface_preserved():
    """IResponse still declares getMarkdown() and toString() (not broken by changes)."""
    content = CHATMODEL_SRC.read_text()
    iface_match = re.search(
        r"export\s+interface\s+IResponse\s*\{(.*?)\n\}",
        content,
        re.DOTALL,
    )
    assert iface_match, "IResponse interface not found"
    iface_body = iface_match.group(1)
    assert "getMarkdown()" in iface_body, "IResponse.getMarkdown() was removed"
    assert "toString()" in iface_body, "IResponse.toString() was removed"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_eslint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_hygiene():
    """Repo's hygiene check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "hygiene"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Hygiene check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_valid_layers():
    """Repo's valid-layers-check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "valid-layers-check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Valid layers check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_define_class_fields():
    """Repo's define-class-fields-check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "define-class-fields-check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Define class fields check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_monaco_compile():
    """Repo's Monaco editor compile check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "monaco-compile-check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Monaco compile check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_vscode_dts_compile():
    """Repo's VS Code dts compile check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "vscode-dts-compile-check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"VS Code dts compile check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_tsec_compile():
    """Repo's tsec compile check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "tsec-compile-check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Tsec compile check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_check_cyclic_deps():
    """Repo's cyclic dependencies check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "check-cyclic-dependencies"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Cyclic dependencies check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_build_scripts():
    """Repo's build scripts tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "test-build-scripts"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Build scripts tests failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_stylelint():
    """Repo's Stylelint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "stylelint"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Stylelint failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_compile():
    """Repo compiles successfully (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "compile"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Compile failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
@pytest.mark.skip(reason="npm install fails in Docker")
def test_repo_core_ci():
    """Repo's core CI passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "core-ci"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Core CI failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# ---------------------------------------------------------------------------
# Agent config checks
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:99 @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
def test_action_label_title_case():
    """Copy Final Response action label uses title-case capitalization."""
    content = COPY_ACTIONS_SRC.read_text()
    assert "Copy Final Response" in content, (
        "Action label should be 'Copy Final Response' (title case) — "
        "required by .github/copilot-instructions.md:99"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:140 @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
def test_no_any_in_getFinalResponse():
    """getFinalResponse body does not use 'any' or 'unknown' types."""
    content = CHATMODEL_SRC.read_text()
    body = _extract_method_body(content, "getFinalResponse(): string {")
    assert ": any" not in body, (
        "getFinalResponse uses ': any' — forbidden by .github/copilot-instructions.md:140"
    )
    assert ": unknown" not in body, (
        "getFinalResponse uses ': unknown' — forbidden by .github/copilot-instructions.md:140"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:132 @ 94c7bf8213beb59e3181fdb61992a032fc65e9a2
def test_action_label_localized():
    """CopyFinalResponseAction label uses localize/localize2 (not a raw string)."""
    content = COPY_ACTIONS_SRC.read_text()
    idx = content.find("CopyFinalResponseAction")
    assert idx != -1, "CopyFinalResponseAction not found"
    action_block = content[idx : idx + 600]
    assert "localize" in action_block, (
        "Action label must be localized using localize/localize2 — "
        "required by .github/copilot-instructions.md:132"
    )
