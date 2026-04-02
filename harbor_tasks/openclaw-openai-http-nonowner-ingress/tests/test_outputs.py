"""
Task: openclaw-openai-http-nonowner-ingress
Repo: openclaw/openclaw @ c6f2db1506873e053bda30f99dea736a1b0e3ba2
PR:   57769

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = f"{REPO}/src/gateway/openai-http.ts"


def _node_eval(script: str, timeout: int = 15) -> str:
    """Run a JS snippet via node and return stripped stdout."""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, timeout=timeout, cwd=REPO,
    )
    return r.stdout.decode().strip()


def _extract_and_call(params_json: str) -> dict:
    """Extract buildAgentCommandInput from source, call it with given params, return result object."""
    js = f"""
    const fs = require('fs');
    let code = fs.readFileSync({json.dumps(TARGET)}, 'utf8');

    // Strip comments
    code = code.replace(/\\/\\/.*$/gm, '');
    code = code.replace(/\\/\\*[\\s\\S]*?\\*\\//g, '');

    // Strip TS-isms to make it executable JS
    code = code.replace(/\\bas\\s+const\\b/g, '');
    code = code.replace(/^import\\b.*$/gm, '');
    code = code.replace(/^export\\s+/gm, '');

    // Find function
    const fnStart = code.indexOf('function buildAgentCommandInput');
    if (fnStart === -1) {{ console.log(JSON.stringify({{error: 'NO_FUNCTION'}})); process.exit(0); }}

    // Skip past params
    let pd = 0, pp = fnStart;
    for (let i = fnStart; i < code.length; i++) {{
        if (code[i] === '(') pd++;
        if (code[i] === ')') {{ pd--; if (pd === 0) {{ pp = i + 1; break; }} }}
    }}

    // Extract param name
    const paramStr = code.slice(code.indexOf('(', fnStart) + 1, pp - 1);
    const paramName = paramStr.split(':')[0].split(',')[0].trim();

    // Find body via brace matching
    let bd = 0, bs = -1, be = -1;
    for (let i = pp; i < code.length; i++) {{
        if (code[i] === '{{') {{ if (bd === 0) bs = i; bd++; }}
        if (code[i] === '}}') {{ bd--; if (bd === 0) {{ be = i; break; }} }}
    }}

    if (bs === -1 || be === -1) {{ console.log(JSON.stringify({{error: 'PARSE_ERROR'}})); process.exit(0); }}

    let body = code.slice(bs + 1, be);
    // Remove TS type annotations from declarations
    body = body.replace(/:\\s*[A-Z]\\w*(?:<[^>]*>)?(\\s*[=;,)])/g, '$1');

    const funcCode = 'function testFunc(' + paramName + ') {{' + body + '}}';
    try {{
        const fn = new Function('return (' + funcCode + ')')();
        const result = fn({params_json});
        console.log(JSON.stringify(result));
    }} catch(e) {{
        console.log(JSON.stringify({{error: 'EXEC_ERROR', message: e.message}}));
    }}
    """
    out = _node_eval(js)
    return json.loads(out)


def _read_stripped() -> str:
    """Read openai-http.ts with comments stripped."""
    code = Path(TARGET).read_text()
    stripped = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    stripped = re.sub(r'/\*[\s\S]*?\*/', '', stripped)
    return stripped


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ts_syntax():
    """openai-http.ts must parse without syntax errors."""
    assert Path(TARGET).exists(), f"{TARGET} does not exist"
    # Use node to check that the file is parseable as a module
    r = subprocess.run(
        ["node", "--check", "--input-type=module"],
        input=Path(TARGET).read_bytes(),
        capture_output=True, timeout=10,
    )
    # node --check on ESM TS will fail on type annotations, so fall back to
    # a regex-based brace balance check if node rejects it (expected for .ts)
    if r.returncode != 0:
        code = Path(TARGET).read_text()
        # Basic balance check: braces, parens, brackets
        for open_c, close_c in [("{", "}"), ("(", ")"), ("[", "]")]:
            depth = 0
            for ch in code:
                if ch == open_c:
                    depth += 1
                elif ch == close_c:
                    depth -= 1
                assert depth >= 0, f"Unbalanced '{close_c}' in {TARGET}"
            assert depth == 0, f"Unclosed '{open_c}' in {TARGET}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sender_is_owner_false():
    """buildAgentCommandInput must set senderIsOwner to false for HTTP ingress."""
    result = _extract_and_call(json.dumps({
        "prompt": {"message": "hello"},
        "modelOverride": "test-model",
        "sessionKey": "sess-1",
        "runId": "run-1",
        "messageChannel": "test-channel",
    }))
    assert "error" not in result, f"Execution failed: {result}"
    assert "senderIsOwner" in result, "senderIsOwner field missing from return object"
    assert result["senderIsOwner"] is False, (
        f"senderIsOwner must be false, got {result['senderIsOwner']}"
    )


# [pr_diff] fail_to_pass
def test_sender_is_owner_false_varied_inputs():
    """senderIsOwner must be false regardless of input parameters."""
    test_cases = [
        {"prompt": {"message": "hi"}, "modelOverride": "gpt-4", "sessionKey": "s1", "runId": "r1", "messageChannel": "ch-1"},
        {"prompt": {"message": "test", "extraSystemPrompt": "sys"}, "modelOverride": "claude", "sessionKey": "s2", "runId": "r2", "messageChannel": "ch-2"},
        {"prompt": {"message": ""}, "sessionKey": "s3", "runId": "r3", "messageChannel": ""},
    ]
    for i, params in enumerate(test_cases):
        result = _extract_and_call(json.dumps(params))
        assert "error" not in result, f"Case {i}: execution failed: {result}"
        assert result["senderIsOwner"] is False, (
            f"Case {i}: senderIsOwner must be false, got {result['senderIsOwner']}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_build_agent_command_input_exists():
    """buildAgentCommandInput function must not be deleted or renamed."""
    stripped = _read_stripped()
    assert "function buildAgentCommandInput" in stripped, (
        "buildAgentCommandInput function not found in openai-http.ts"
    )


# [pr_diff] pass_to_pass
def test_handle_openai_http_request_exported():
    """handleOpenAiHttpRequest must still be exported."""
    stripped = _read_stripped()
    assert re.search(r'export\b.*handleOpenAiHttpRequest', stripped), (
        "handleOpenAiHttpRequest export not found in openai-http.ts"
    )


# [pr_diff] pass_to_pass
def test_adjacent_fields_preserved():
    """deliver, bestEffortDeliver, and allowModelOverride must retain original values."""
    result = _extract_and_call(json.dumps({
        "prompt": {"message": "hello"},
        "modelOverride": "test-model",
        "sessionKey": "sess-1",
        "runId": "run-1",
        "messageChannel": "test-channel",
    }))
    assert "error" not in result, f"Execution failed: {result}"
    assert result.get("deliver") is False, (
        f"deliver must be false, got {result.get('deliver')}"
    )
    assert result.get("bestEffortDeliver") is False, (
        f"bestEffortDeliver must be false, got {result.get('bestEffortDeliver')}"
    )
    assert result.get("allowModelOverride") is True, (
        f"allowModelOverride must be true, got {result.get('allowModelOverride')}"
    )


# [static] pass_to_pass
def test_not_stub():
    """buildAgentCommandInput must have a non-trivial function body."""
    stripped = _read_stripped()

    fn_start = stripped.find("function buildAgentCommandInput")
    assert fn_start != -1, "Function not found"

    # Skip past the parameter list (match parens to find closing `)`)
    paren_start = stripped.find("(", fn_start)
    depth, pos = 1, paren_start + 1
    while depth > 0 and pos < len(stripped):
        if stripped[pos] == "(":
            depth += 1
        elif stripped[pos] == ")":
            depth -= 1
        pos += 1

    # Now find the function body `{...}` after the `)`
    brace_pos = stripped.find("{", pos)
    assert brace_pos != -1, "Function body brace not found"
    depth, body_end = 1, brace_pos + 1
    while depth > 0 and body_end < len(stripped):
        if stripped[body_end] == "{":
            depth += 1
        elif stripped[body_end] == "}":
            depth -= 1
        body_end += 1

    body = stripped[brace_pos + 1:body_end - 1]
    lines = [l for l in body.split("\n") if l.strip()]
    assert len(lines) >= 3, f"Function body too short ({len(lines)} lines) — likely a stub"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:144 @ c6f2db1506873e053bda30f99dea736a1b0e3ba2
def test_no_any_in_function():
    """buildAgentCommandInput must not use 'any' type annotation."""
    # AST-only because: TypeScript cannot be imported in Python
    stripped = _read_stripped()

    fn_start = stripped.find("function buildAgentCommandInput")
    assert fn_start != -1, "Function not found"

    # Find the end of the entire function (signature + body)
    # Skip past param list first
    paren_start = stripped.find("(", fn_start)
    depth, pos = 1, paren_start + 1
    while depth > 0 and pos < len(stripped):
        if stripped[pos] == "(":
            depth += 1
        elif stripped[pos] == ")":
            depth -= 1
        pos += 1
    # Find body braces
    brace_pos = stripped.find("{", pos)
    depth, body_end = 1, brace_pos + 1
    while depth > 0 and body_end < len(stripped):
        if stripped[body_end] == "{":
            depth += 1
        elif stripped[body_end] == "}":
            depth -= 1
        body_end += 1

    func_text = stripped[fn_start:body_end]
    # Match ': any' or ': any,' or ': any)' or ': any;' type annotations
    any_matches = re.findall(r':\s*\bany\b', func_text)
    assert len(any_matches) == 0, (
        f"Found {len(any_matches)} 'any' type annotation(s) in buildAgentCommandInput — "
        "prefer strict typing per CLAUDE.md"
    )


# [agent_config] pass_to_pass — CLAUDE.md:146 @ c6f2db1506873e053bda30f99dea736a1b0e3ba2
def test_no_ts_nocheck():
    """openai-http.ts must not contain @ts-nocheck, @ts-ignore, or eslint-disable directives."""
    code = Path(TARGET).read_text()
    assert "@ts-nocheck" not in code, (
        "Found @ts-nocheck in openai-http.ts — fix root causes instead (CLAUDE.md)"
    )
    assert "@ts-ignore" not in code, (
        "Found @ts-ignore in openai-http.ts — fix root causes instead (CLAUDE.md)"
    )
    # CLAUDE.md:146 also says no inline lint suppressions by default
    assert "eslint-disable" not in code, (
        "Found eslint-disable in openai-http.ts — fix root causes instead (CLAUDE.md)"
    )


# [pr_diff] pass_to_pass
def test_params_pass_through():
    """buildAgentCommandInput must correctly pass through prompt, model, session, and run fields."""
    result = _extract_and_call(json.dumps({
        "prompt": {"message": "specific-msg", "extraSystemPrompt": "sys-prompt"},
        "modelOverride": "my-model",
        "sessionKey": "my-session",
        "runId": "my-run",
        "messageChannel": "my-channel",
    }))
    assert "error" not in result, f"Execution failed: {result}"
    assert result.get("message") == "specific-msg", (
        f"message not passed through, got {result.get('message')}"
    )
    assert result.get("extraSystemPrompt") == "sys-prompt", (
        f"extraSystemPrompt not passed through, got {result.get('extraSystemPrompt')}"
    )
    assert result.get("model") == "my-model", (
        f"model not passed through, got {result.get('model')}"
    )
    assert result.get("sessionKey") == "my-session", (
        f"sessionKey not passed through, got {result.get('sessionKey')}"
    )
    assert result.get("messageChannel") == "my-channel", (
        f"messageChannel not passed through, got {result.get('messageChannel')}"
    )
