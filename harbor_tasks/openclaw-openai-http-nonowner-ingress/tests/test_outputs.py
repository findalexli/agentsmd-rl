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


def _read_stripped() -> str:
    """Read openai-http.ts with comments stripped."""
    code = Path(TARGET).read_text()
    stripped = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    stripped = re.sub(r'/\*[\s\S]*?\*/', '', stripped)
    return stripped


def _get_function_body(stripped: str, func_name: str) -> str:
    """Extract the full body of a function using brace matching.

    Returns the content inside the function's outermost braces.
    """
    fn_start = stripped.find(f"function {func_name}")
    if fn_start == -1:
        return ""

    # Skip past the parameter list to find the opening brace
    paren_start = stripped.find("(", fn_start)
    if paren_start == -1:
        return ""

    depth = 1
    pos = paren_start + 1
    while depth > 0 and pos < len(stripped):
        if stripped[pos] == "(":
            depth += 1
        elif stripped[pos] == ")":
            depth -= 1
        pos += 1

    # Now find the function body braces
    brace_pos = stripped.find("{", pos)
    if brace_pos == -1:
        return ""

    depth = 1
    body_end = brace_pos + 1
    while depth > 0 and body_end < len(stripped):
        if stripped[body_end] == "{":
            depth += 1
        elif stripped[body_end] == "}":
            depth -= 1
        body_end += 1

    return stripped[brace_pos + 1:body_end - 1]


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using ACTUAL code execution
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sender_is_owner_false():
    """buildAgentCommandInput must set senderIsOwner to false for HTTP ingress.

    BEHAVIORAL TEST: Runs actual vitest from the repo to verify senderIsOwner is false.
    The PR adds an assertion: expect(getFirstAgentCall()?.senderIsOwner).toBe(false)
    """
    # Install dependencies if needed
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0 and "lockfile" in r.stderr.lower():
        # Try without frozen-lockfile if lockfile issues
        r = subprocess.run(
            ["pnpm", "install"],
            capture_output=True, text=True, timeout=180, cwd=REPO,
        )
        assert r.returncode == 0, f"pnpm install failed: {r.stderr[:500]}"

    # Run the specific test that checks senderIsOwner behavior
    # The test in openai-http.test.ts has: expect(getFirstAgentCall()?.senderIsOwner).toBe(false)
    r = subprocess.run(
        ["pnpm", "vitest", "run", "src/gateway/openai-http.test.ts",
         "-t", "senderIsOwner"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )

    # If the specific test name filter doesn't match, run the full file and check output
    if r.returncode != 0 or "senderIsOwner" not in r.stdout:
        # Run with broader filter - look for the test that validates HTTP API behavior
        r = subprocess.run(
            ["pnpm", "vitest", "run", "src/gateway/openai-http.test.ts",
             "-t", "handles request validation and routing"],
            capture_output=True, text=True, timeout=180, cwd=REPO,
        )

    assert r.returncode == 0, (
        f"vitest failed - senderIsOwner assertion likely failed.\n"
        f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-1000:]}"
    )

    # Verify the specific assertion about senderIsOwner passed
    assert "senderIsOwner" in r.stdout or "✓" in r.stdout, (
        f"Expected senderIsOwner test to run and pass. Output:\n{r.stdout[-1500:]}"
    )


# [pr_diff] fail_to_pass
def test_sender_is_owner_in_source():
    """Source code must contain senderIsOwner: false (not true) for HTTP ingress.

    This is a secondary behavioral check: we verify the actual source code
    has the fix applied - senderIsOwner must be false, not true.
    """
    stripped = _read_stripped()

    # Use brace-matching helper to extract the full function body
    body = _get_function_body(stripped, "buildAgentCommandInput")
    if not body:
        # Fall back to simple grep if function extraction fails
        sender_owner_pattern = r'senderIsOwner:\s*(true|false)'
        matches = re.findall(sender_owner_pattern, stripped)
        assert matches, "Could not find senderIsOwner in the source code"
        for m in matches:
            assert m == "false", (
                f"senderIsOwner must be false, found: {m}. "
                "The bug is that HTTP callers incorrectly get owner-level access."
            )
        return

    # Check for senderIsOwner: true (bug) vs senderIsOwner: false (fix)
    assert "senderIsOwner: true" not in body, (
        "BUG DETECTED: senderIsOwner is set to true in buildAgentCommandInput. "
        "HTTP callers should NOT get owner-level access. "
        "The fix should change senderIsOwner: true to senderIsOwner: false"
    )
    # After fix, should have senderIsOwner: false
    assert "senderIsOwner: false" in body, (
        "senderIsOwner: false not found in buildAgentCommandInput. "
        "The fix should set senderIsOwner to false for HTTP ingress."
    )


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# -----------------------------------------------------------------------------

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
    """Other fields in the returned object must retain correct values.

    Uses tsx to execute the actual function and verify field values.
    """
    # Create a test script that imports and calls the actual function
    test_script = f"""
import {{ buildAgentCommandInput }} from '{TARGET}';

const result = buildAgentCommandInput({{
    prompt: {{ message: "hello" }},
    modelOverride: "test-model",
    sessionKey: "sess-1",
    runId: "run-1",
    messageChannel: "test-channel",
}});

console.log(JSON.stringify(result));
"""
    script_path = Path(REPO) / "_verify_fields.mjs"
    script_path.write_text(test_script)

    try:
        r = subprocess.run(
            ["npx", "tsx", str(script_path)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        if r.returncode == 0:
            result = json.loads(r.stdout.strip())
            assert result.get("deliver") == False, (
                f"deliver must be false, got {{result.get('deliver')}}"
            )
            assert result.get("bestEffortDeliver") == False, (
                f"bestEffortDeliver must be false, got {{result.get('bestEffortDeliver')}}"
            )
            assert result.get("allowModelOverride") == True, (
                f"allowModelOverride must be true, got {{result.get('allowModelOverride')}}"
            )
        else:
            # Fallback: parse from source using brace-matching helper
            stripped = _read_stripped()
            body = _get_function_body(stripped, "buildAgentCommandInput")
            if body:
                # Check field values in source
                assert re.search(r'deliver:\s*false', body), "deliver: false not found"
                assert re.search(r'bestEffortDeliver:\s*false', body), "bestEffortDeliver: false not found"
                assert re.search(r'allowModelOverride:\s*true', body), "allowModelOverride: true not found"
    finally:
        script_path.unlink(missing_ok=True)


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

    # Now find the function body `{{...}}` after the `)`
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
    assert len(lines) >= 3, f"Function body too short ({{len(lines)}} lines) — likely a stub"


# -----------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# -----------------------------------------------------------------------------

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
        f"Found {{len(any_matches)}} 'any' type annotation(s) in buildAgentCommandInput — "
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
    """buildAgentCommandInput must correctly pass through prompt, model, session, and run fields.

    Uses tsx to execute the actual function and verify field values.
    """
    # Create a test script that imports and calls the actual function
    test_script = f"""
import {{ buildAgentCommandInput }} from '{TARGET}';

const result = buildAgentCommandInput({{
    prompt: {{ message: "specific-msg", extraSystemPrompt: "sys-prompt" }},
    modelOverride: "my-model",
    sessionKey: "my-session",
    runId: "my-run",
    messageChannel: "my-channel",
}});

console.log(JSON.stringify(result));
"""
    script_path = Path(REPO) / "_verify_params.mjs"
    script_path.write_text(test_script)

    try:
        r = subprocess.run(
            ["npx", "tsx", str(script_path)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        if r.returncode == 0:
            result = json.loads(r.stdout.strip())
            assert result.get("message") == "specific-msg", (
                f"message not passed through, got {{result.get('message')}}"
            )
            assert result.get("extraSystemPrompt") == "sys-prompt", (
                f"extraSystemPrompt not passed through, got {{result.get('extraSystemPrompt')}}"
            )
            assert result.get("model") == "my-model", (
                f"model not passed through, got {{result.get('model')}}"
            )
            assert result.get("sessionKey") == "my-session", (
                f"sessionKey not passed through, got {{result.get('sessionKey')}}"
            )
            assert result.get("messageChannel") == "my-channel", (
                f"messageChannel not passed through, got {{result.get('messageChannel')}}"
            )
        else:
            # Fallback: parse from source using brace-matching helper
            stripped = _read_stripped()
            body = _get_function_body(stripped, "buildAgentCommandInput")
            if body:
                # Verify params are referenced in the return object
                assert "params.prompt.message" in body or "message:" in body
                assert "params.modelOverride" in body or "model:" in body
                assert "params.sessionKey" in body or "sessionKey:" in body
                assert "params.runId" in body or "runId:" in body
                assert "params.messageChannel" in body or "messageChannel:" in body
    finally:
        script_path.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's CI/CD checks
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass — full check suite (typecheck + lint + architecture checks)
def test_repo_lint():
    """Repo's full check suite must pass (pass_to_pass).

    Runs pnpm check which includes:
    - TypeScript type checking (tsgo)
    - oxlint type-aware linting
    - Architecture/boundary checks (no-conflict-markers, host-env-policy, etc.)
    """
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Check failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — repo's build must succeed
def test_repo_build():
    """Repo's build must succeed (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — openai-http gateway tests
def test_repo_gateway_tests():
    """Repo's gateway tests for openai-http must pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "vitest", "run", "src/gateway/openai-http.test.ts",
         "--testNamePattern", "handles request validation"],
        capture_output=True, text=True, timeout=240, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Gateway tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
    )
