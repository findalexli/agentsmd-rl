"""
Task: nextjs-edge-als-test-timeout-race
Repo: vercel/next.js @ 9f181bd11af5f532c529a6f168fe40505f0a4d75
PR:   91643

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/next.js"
TEST_FILE = Path(REPO) / "test/e2e/edge-async-local-storage/index.test.ts"
TEST_DIR = Path(REPO) / "test/e2e/edge-async-local-storage"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_single_fixture_executes_correctly():
    """Single ALS fixture file exists and returns {id: <req-id>} when invoked."""
    fixture = _find_fixture("single")
    assert fixture is not None, "No single fixture file found under pages/api/ or app/api/"

    _assert_handler_responses(fixture, [
        ("test-42", '(j) => j.id === "test-42"'),
        ("req-999", '(j) => j.id === "req-999"'),
        ("hello-world", '(j) => j.id === "hello-world"'),
    ])


# [pr_diff] fail_to_pass
def test_multiple_fixture_executes_correctly():
    """Multiple ALS fixture file exists and returns {id, nestedId} with nested ALS."""
    fixture = _find_fixture("multiple")
    assert fixture is not None, "No multiple fixture file found under pages/api/ or app/api/"

    _assert_handler_responses(fixture, [
        ("abc-1", '(j) => j.id === "abc-1" && typeof j.nestedId === "string" && j.nestedId.includes("nested")'),
        ("xyz-2", '(j) => j.id === "xyz-2" && typeof j.nestedId === "string" && j.nestedId.includes("nested")'),
        ("req-0", '(j) => j.id === "req-0" && typeof j.nestedId === "string" && j.nestedId.includes("nested")'),
    ])


# [pr_diff] fail_to_pass
def test_no_per_test_instance_creation():
    """createNext must not be called inside it/test body (the core race condition bug)."""
    code = TEST_FILE.read_text()

    # If createNext isn't used at all, the fix uses an alternative — pass
    if "createNext" not in code:
        return

    # Verify createNext is NOT inside a test callback using brace-depth tracking
    result = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const code = fs.readFileSync('{TEST_FILE}', 'utf8');
const lines = code.split('\\n');
let inTestBody = false, braceDepth = 0, testEntryDepth = -1;
for (let i = 0; i < lines.length; i++) {{
    const line = lines[i];
    if (!inTestBody && /\\b(it|test)\\s*[.(]/.test(line)) {{
        inTestBody = true;
        testEntryDepth = braceDepth;
    }}
    for (const ch of line) {{
        if (ch === '{{') braceDepth++;
        if (ch === '}}') braceDepth--;
    }}
    if (inTestBody && braceDepth <= testEntryDepth) inTestBody = false;
    if (inTestBody && line.includes('createNext')) {{
        console.error('createNext inside test body at line ' + (i+1));
        process.exit(1);
    }}
}}
"""],
        capture_output=True, timeout=10,
    )
    assert result.returncode == 0, "createNext is still called inside a test body (race condition not fixed)"


# [pr_diff] fail_to_pass
def test_no_inline_route_code():
    """Route handler code must not be inlined as template strings in the test file."""
    code = TEST_FILE.read_text()

    for match in re.findall(r"`([^`]*)`", code, re.DOTALL):
        if len(match) > 50:
            has_export = re.search(r"export\s+(default|const\s+config)", match)
            has_handler = re.search(r"function\s+handler", match)
            assert not (has_export or has_handler), \
                "Test file still contains inline route code as template strings"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_uses_fetchViaHTTP():
    """Test must still use fetchViaHTTP from next-test-utils."""
    code = TEST_FILE.read_text()
    assert "fetchViaHTTP" in code, "fetchViaHTTP usage was removed"


# [pr_diff] pass_to_pass
def test_concurrent_requests_with_req_id():
    """Test must still send concurrent requests with req-id headers via Promise.all."""
    code = TEST_FILE.read_text()
    assert "req-id" in code, "req-id header pattern was removed"
    assert "Promise.all" in code, "Promise.all concurrent request pattern was removed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:207-221 @ 9f181bd
def test_uses_nexttestsetup():
    """Must use nextTestSetup() API (not createNext) per AGENTS.md:207-221."""
    code = TEST_FILE.read_text()
    assert "nextTestSetup" in code, \
        "Test does not use nextTestSetup — AGENTS.md:207-221 requires it over createNext"


# [agent_config] fail_to_pass — AGENTS.md:207-221 @ 9f181bd
def test_uses_fixture_directory():
    """Must use fixture directory reference (not inline files object) per AGENTS.md:207-221."""
    code = TEST_FILE.read_text()
    uses_dir_ref = bool(re.search(r"__dirname|import\.meta|path\.(join|resolve)", code))
    uses_inline_files = bool(re.search(r"files\s*:\s*\{", code))

    assert uses_dir_ref or not uses_inline_files, \
        "Uses inline files object instead of fixture directory reference (AGENTS.md:207-221)"


# [agent_config] pass_to_pass — AGENTS.md:194-205 @ 9f181bd
def test_no_deprecated_check_function():
    """Must not use deprecated check() function per AGENTS.md:194-205."""
    code = TEST_FILE.read_text()
    assert not re.search(r"\bcheck\s*\(", code), \
        "Uses deprecated check() function (AGENTS.md:194-205)"


# [agent_config] pass_to_pass — AGENTS.md:180-192 @ 9f181bd
def test_no_settimeout_waiting():
    """Must not use setTimeout for waiting — use retry() instead per AGENTS.md:180-192."""
    code = TEST_FILE.read_text()
    bad_patterns = [
        r"new\s+Promise\s*\(\s*\(?[^)]*\)?\s*=>\s*setTimeout",
        r"await\s+new\s+Promise[^)]*setTimeout",
    ]
    for pat in bad_patterns:
        assert not re.search(pat, code), \
            "Uses setTimeout for waiting instead of retry() (AGENTS.md:180-192)"


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Test file must have real structure: describe, it/test, fetchViaHTTP/expect, 15+ lines."""
    code = TEST_FILE.read_text()
    meaningful = [l for l in code.split("\n") if l.strip() and not l.strip().startswith("//")]
    assert len(meaningful) >= 15, f"Only {len(meaningful)} meaningful lines — likely a stub"
    assert re.search(r"\bdescribe\s*\(", code), "Missing describe block"
    assert re.search(r"\b(it|test)\s*[.(]", code), "Missing it/test calls"
    assert re.search(r"fetchViaHTTP|\bexpect\s*\(", code), "Missing fetchViaHTTP or expect"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_fixture(name: str) -> str | None:
    """Find a fixture file at common Next.js locations."""
    for ext in ("js", "ts", "jsx", "tsx", "mjs"):
        p = TEST_DIR / "pages" / "api" / f"{name}.{ext}"
        if p.exists():
            return str(p)
    for ext in ("js", "ts", "mjs"):
        p = TEST_DIR / "app" / "api" / name / f"route.{ext}"
        if p.exists():
            return str(p)
    return None


def _assert_handler_responses(fixture_path: str, cases: list[tuple[str, str]]):
    """Execute an edge handler via Node.js VM and validate responses for multiple request IDs."""
    checks = []
    for req_id, validator in cases:
        checks.append(
            f'    handler({{ headers: {{ get: (n) => n === "req-id" ? "{req_id}" : null }} }})'
            f'        .then(r => r.json())'
            f'        .then(j => {{ const ok = ({validator})(j);'
            f'            if (!ok) throw new Error("Failed for req-id={req_id}: " + JSON.stringify(j)); }})'
        )

    script = f"""
const vm = require('vm');
const fs = require('fs');
const {{ AsyncLocalStorage }} = require('async_hooks');

let code = fs.readFileSync('{fixture_path}', 'utf8');
code = code.replace(/^export\\s+default\\s+/m, '__exports.default = ');
code = code.replace(/^export\\s+(const|let|var|function|async\\s+function|class)\\s+/gm, '$1 ');
code = code.replace(/^import\\s+.*$/gm, '');

const __exports = {{}};
const sandbox = {{
    AsyncLocalStorage,
    Response: globalThis.Response,
    fetch: async () => ({{ text: async () => '', ok: true }}),
    console, __exports, setTimeout, clearTimeout, Promise, require,
}};

vm.runInNewContext(code, sandbox, {{ timeout: 5000 }});
const handler = __exports.default;
if (typeof handler !== 'function') {{
    console.error('No default export function found');
    process.exit(1);
}}

Promise.all([
{_join_comma(checks)}
]).then(() => process.exit(0)).catch((e) => {{ console.error(e.message); process.exit(1); }});
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, timeout=15)
    assert result.returncode == 0, f"Handler execution failed:\n{result.stderr.decode()}"


def _join_comma(items: list[str]) -> str:
    return ",\n".join(items)
