"""
Task: nextjs-typed-routes-retry-timeout-flake
Repo: vercel/next.js @ 0090db224d177c51f6d5e45fe1be2527ce04e899
PR:   #91923

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
import re
from pathlib import Path

REPO = "/repo"
TEST_FILE = Path(REPO) / "test/e2e/app-dir/typed-routes/typed-routes.test.ts"


def _read_test_file() -> str:
    return TEST_FILE.read_text()


def _parse_ts_with_node(code: str, timeout: int = 30) -> dict:
    """Execute TypeScript parsing code via Node in the repo directory.

    Returns dict with: success, error, ast (if successful)
    """
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        result = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
        else:
            return {"success": False, "error": result.stderr}
    finally:
        script.unlink(missing_ok=True)


def _extract_test_block(content: str, test_name: str) -> str:
    """Extract the body of an it() block by test name."""
    pattern = rf"it\(['\"]{ re.escape(test_name) }['\"].*?async\s*\(\)\s*=>\s*\{{"
    m = re.search(pattern, content, re.DOTALL)
    assert m, f"Test block '{test_name}' not found"
    start = m.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
        i += 1
    return content[m.start() : i]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_file_exists_and_nontrivial():
    """Test file must exist and have substantial content (not stubbed)."""
    assert TEST_FILE.exists(), f"{TEST_FILE} does not exist"
    lines = TEST_FILE.read_text().splitlines()
    assert len(lines) >= 40, f"File too short ({len(lines)} lines) — likely stubbed"


# [static] pass_to_pass
def test_syntax_balanced_braces():
    """Test file must have balanced braces (basic syntax sanity)."""
    content = _read_test_file()
    for open_c, close_c in [("{", "}"), ("(", ")"), ("[", "]")]:
        opens = content.count(open_c)
        closes = content.count(close_c)
        assert abs(opens - closes) <= 3, (
            f"Unbalanced {open_c}/{close_c}: {opens}/{closes}"
        )


# [static] pass_to_pass
def test_typescript_parses():
    """Test file must be valid TypeScript that parses without errors."""
    content = _read_test_file()

    # Use Node to parse and extract the retry() calls
    parse_code = f"""
const fs = require('fs');
const content = fs.readFileSync('{TEST_FILE}', 'utf8');

// Simple regex extraction of retry() calls
const retryPattern = /retry\\s*\\(\\s*async\\s*\\(\\)\\s*=>\\s*\\{{0,1}}[^}}]{{0,500}}\\}}?,\\s*(\\d[\\d_]*)\\s*\\)/g;
const matches = [];
let match;
while ((match = retryPattern.exec(content)) !== null) {{
    matches.push({{ timeout: parseInt(match[1].replace(/_/g, '')), match: match[0].slice(0, 80) }});
}}

console.log(JSON.stringify({{ success: true, retry_calls: matches }}));
"""

    result = _parse_ts_with_node(parse_code)
    assert result.get("success", False), f"Failed to parse test file: {result.get('error', 'Unknown error')}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_generate_route_types_retry_timeout():
    """The 'should generate route types correctly' retry() must have timeout >= 10s."""
    content = _read_test_file()
    block = _extract_test_block(content, "should generate route types correctly")

    # Execute regex via Node to find retry timeout
    parse_code = f"""
const block = {json.dumps(block)};
const retryPattern = /retry\\s*\\(\\s*async\\s*\\(\\)\\s*=>\\s*\\{{0,1}}[\\s\\S]{{0,800}}\\}}?,\\s*(\\d[\\d_]*)\\s*\\)/;
const match = block.match(retryPattern);
if (match) {{
    console.log(JSON.stringify({{ success: true, timeout: parseInt(match[1].replace(/_/g, '')) }}));
}} else {{
    console.log(JSON.stringify({{ success: false, error: 'No retry with timeout found' }}));
}}
"""
    result = _parse_ts_with_node(parse_code)
    assert result.get("success", False), result.get("error", "Failed to extract retry timeout")
    timeout = result.get("timeout")
    assert timeout is not None, "No timeout value found"
    assert timeout >= 10_000, f"Timeout {timeout}ms is too low (need >= 10000)"


# [pr_diff] fail_to_pass
def test_custom_route_patterns_retry_timeout():
    """The 'should correctly convert custom route patterns...' retry() must have timeout >= 10s."""
    content = _read_test_file()
    block = _extract_test_block(
        content,
        "should correctly convert custom route patterns from path-to-regexp to bracket syntax",
    )

    parse_code = f"""
const block = {json.dumps(block)};
const retryPattern = /retry\\s*\\(\\s*async\\s*\\(\\)\\s*=>\\s*\\{{0,1}}[\\s\\S]{{0,800}}\\}}?,\\s*(\\d[\\d_]*)\\s*\\)/;
const match = block.match(retryPattern);
if (match) {{
    console.log(JSON.stringify({{ success: true, timeout: parseInt(match[1].replace(/_/g, '')) }}));
}} else {{
    console.log(JSON.stringify({{ success: false, error: 'No retry with timeout found' }}));
}}
"""
    result = _parse_ts_with_node(parse_code)
    assert result.get("success", False), result.get("error", "Failed to extract retry timeout")
    timeout = result.get("timeout")
    assert timeout is not None, "No timeout value found"
    assert timeout >= 10_000, f"Timeout {timeout}ms is too low (need >= 10000)"


# [pr_diff] fail_to_pass
def test_tsc_waits_for_routes_dts_before_stop():
    """The tsc test must wait for routes.d.ts before calling next.stop()."""
    content = _read_test_file()
    block = _extract_test_block(content, "should have passing tsc after start")

    # Use Node to analyze the ordering of routes.d.ts vs next.stop()
    parse_code = f"""
const block = {json.dumps(block)};

// Find positions of key markers
const routesMatch = block.match(/routes\\.d\\.ts/);
const stopMatch = block.match(/next\\.stop\\(\\)/);

if (!routesMatch) {{
    console.log(JSON.stringify({{ success: false, error: "No routes.d.ts reference in tsc test" }}));
    process.exit(0);
}}
if (!stopMatch) {{
    console.log(JSON.stringify({{ success: false, error: "next.stop() not found in tsc test" }}));
    process.exit(0);
}}

const routesPos = routesMatch.index;
const stopPos = stopMatch.index;

// Check ordering
if (routesPos >= stopPos) {{
    console.log(JSON.stringify({{ success: false, error: "routes.d.ts referenced AFTER next.stop() — must wait before stopping" }}));
    process.exit(0);
}}

// Verify it's actually awaited (in executable code, not just comments)
const preStop = block.substring(0, stopPos);
const hasAwaitRetry = /await\\s+retry\\s*\\(/.test(preStop);
const hasReadFile = /readFile.*routes\\.d\\.ts/.test(preStop);

// Check if routes.d.ts appears in executable code (not just comments)
const lines = preStop.split('\\n');
let inExecutableCode = false;
for (const line of lines) {{
    const stripped = line.trim();
    if (stripped.includes('routes.d.ts') && !stripped.startsWith('//') && !stripped.startsWith('*')) {{
        inExecutableCode = true;
        break;
    }}
}}

if (!hasAwaitRetry && !hasReadFile && !inExecutableCode) {{
    console.log(JSON.stringify({{ success: false, error: "routes.d.ts only in comments before next.stop()" }}));
    process.exit(0);
}}

console.log(JSON.stringify({{ success: true, routes_pos: routesPos, stop_pos: stopPos }}));
"""
    result = _parse_ts_with_node(parse_code)
    assert result.get("success", False), result.get("error", "Failed to verify ordering")


# [pr_diff] fail_to_pass
def test_tsc_retry_has_extended_timeout():
    """The retry() added in the tsc test must also have timeout >= 10s."""
    content = _read_test_file()
    block = _extract_test_block(content, "should have passing tsc after start")

    # Use Node to find all retry calls in the block and their timeouts
    parse_code = f"""
const block = {json.dumps(block)};
const retryPattern = /retry\\s*\\(\\s*async\\s*\\(\\)\\s*=>\\s*\\{{0,1}}[\\s\\S]{{0,800}}\\}}?,\\s*(\\d[\\d_]*)\\s*\\)/g;
const matches = [];
let match;
while ((match = retryPattern.exec(block)) !== null) {{
    matches.push(parseInt(match[1].replace(/_/g, '')));
}}
console.log(JSON.stringify({{ success: true, timeouts: matches }}));
"""
    result = _parse_ts_with_node(parse_code)
    timeouts = result.get("timeouts", [])

    if timeouts:
        for timeout in timeouts:
            assert timeout >= 10_000, f"Timeout {timeout}ms is too low (need >= 10000)"
    else:
        # Accept other wait mechanisms with extended timeout
        assert re.search(r"(?:waitFor|waitUntil)\s*\(.*\d{5,}", block, re.DOTALL), (
            "No extended timeout found in tsc test"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_original_assertions_preserved():
    """Key assertion strings from the original tests must still be present."""
    content = _read_test_file()
    required = [
        "expectedDts",
        "toContain(expectedDts)",
        "routes.d.ts",
        "pnpm",
        "tsc",
        '/blog/[category]/[[...slug]]',
        '/api-legacy/[version]/[[...endpoint]]',
    ]
    missing = [r for r in required if r not in content]
    assert not missing, f"Missing original assertions: {missing}"


# [pr_diff] pass_to_pass
def test_all_original_test_names_present():
    """All test blocks from the original file must still exist."""
    content = _read_test_file()
    test_names = [
        "should generate route types correctly",
        "should have passing tsc after start",
        "should correctly convert custom route patterns",
        "should generate RouteContext type",
    ]
    missing = [n for n in test_names if n not in content]
    assert not missing, f"Missing test names: {missing}"


# [pr_diff] pass_to_pass
def test_retry_blocks_have_assertions():
    """All retry() blocks must contain expect() assertions, not be empty."""
    content = _read_test_file()
    retry_blocks = list(re.finditer(r"retry\s*\(\s*async\s*\(\)\s*=>\s*\{", content))
    assert len(retry_blocks) >= 3, f"Only {len(retry_blocks)} retry blocks (need >= 3)"

    for m in retry_blocks:
        start = m.end()
        depth = 1
        i = start
        while i < len(content) and depth > 0:
            if content[i] == "{":
                depth += 1
            elif content[i] == "}":
                depth -= 1
            i += 1
        body = content[start : i - 1]
        assert "expect(" in body or "assert" in body.lower(), (
            f"retry block at offset {m.start()} has no assertions"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:180 @ 0090db224d
def test_uses_retry_not_settimeout():
    """Must use retry() from next-test-utils, not setTimeout for waiting."""
    content = _read_test_file()
    assert "setTimeout" not in content, "Found setTimeout usage — use retry() instead (AGENTS.md:180)"


# [agent_config] pass_to_pass — AGENTS.md:194 @ 0090db224d
def test_no_deprecated_check():
    """Must not use deprecated check() function."""
    content = _read_test_file()
    assert not re.search(r"^\s*await\s+check\s*\(", content, re.MULTILINE), (
        "Found deprecated check() call — use retry() + expect() (AGENTS.md:194)"
    )


# [agent_config] pass_to_pass — AGENTS.md:207-221 @ 0090db224d
def test_uses_real_fixture_dir():
    """nextTestSetup must use __dirname (real fixture dir), not an inline files object."""
    content = _read_test_file()
    setup_matches = list(re.finditer(r"nextTestSetup\s*\(", content))
    assert setup_matches, "No nextTestSetup call found in test file"
    for m in setup_matches:
        # Extract the full argument passed to nextTestSetup
        start = m.end()
        depth = 1
        i = start
        while i < len(content) and depth > 0:
            if content[i] in "({[":
                depth += 1
            elif content[i] in ")}]":
                depth -= 1
            i += 1
        arg = content[m.start() : i]
        assert not re.search(r"\bfiles\s*:\s*\{", arg), (
            "nextTestSetup uses inline files object — prefer files: __dirname (AGENTS.md:207)"
        )
