"""
Task: nextjs-edge-als-test-timeout-race
Repo: vercel/next.js @ 9f181bd11af5f532c529a6f168fe40505f0a4d75
PR:   91643

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
import json
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

    # Execute handler with mocked request and verify it returns correct id
    # Convert ES module syntax to CommonJS for Node.js execution
    code = f"""
const AsyncLocalStorage = require('async_hooks').AsyncLocalStorage;
global.AsyncLocalStorage = AsyncLocalStorage;
global.Response = class Response {{
  constructor(body) {{ this.body = JSON.stringify(body); }}
  json() {{ return Promise.resolve(JSON.parse(this.body)); }}
  static json(body) {{ return new Response(body); }}
}};
global.fetch = async () => ({{ text: async () => 'ok' }});

const fs = require('fs');
let code = fs.readFileSync('{fixture}', 'utf8');
// Strip export const config line and convert export default to exports.default
code = code.replace(/export const config = .*/g, '');
code = code.replace(/export default /, 'exports.default = ');
const vm = require('vm');
const exports = {{}};
const context = {{ AsyncLocalStorage, Response: global.Response, fetch: global.fetch, console, exports, require }};
vm.createContext(context);
vm.runInContext(code, context);

const handler = context.exports.default;
const mockRequest = {{ headers: {{ get: (k) => k === 'req-id' ? 'test-req-42' : null }} }};
handler(mockRequest).then(r => r.json()).then(j => {{
    if (j.id === 'test-req-42') {{ console.log('PASS'); }} else {{ console.log('FAIL: got', JSON.stringify(j)); process.exit(1); }}
}}).catch(e => {{ console.error(e); process.exit(1); }});
"""
    r = subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0 and "PASS" in r.stdout, f"Single fixture failed: {r.stderr or r.stdout}"


# [pr_diff] fail_to_pass
def test_multiple_fixture_executes_correctly():
    """Multiple ALS fixture file exists and returns {id, nestedId} with nested ALS."""
    fixture = _find_fixture("multiple")
    assert fixture is not None, "No multiple fixture file found under pages/api/ or app/api/"

    # Execute handler with mocked request and verify it returns correct id and nestedId
    # Convert ES module syntax to CommonJS for Node.js execution
    code = f"""
const AsyncLocalStorage = require('async_hooks').AsyncLocalStorage;
global.AsyncLocalStorage = AsyncLocalStorage;
global.Response = class Response {{
  constructor(body) {{ this.body = JSON.stringify(body); }}
  json() {{ return Promise.resolve(JSON.parse(this.body)); }}
  static json(body) {{ return new Response(body); }}
}};
global.fetch = async () => ({{ text: async () => 'ok' }});

const fs = require('fs');
let code = fs.readFileSync('{fixture}', 'utf8');
// Strip export const config line and convert export default to exports.default
code = code.replace(/export const config = .*/g, '');
code = code.replace(/export default /, 'exports.default = ');
const vm = require('vm');
const exports = {{}};
const context = {{ AsyncLocalStorage, Response: global.Response, fetch: global.fetch, console, exports, require }};
vm.createContext(context);
vm.runInContext(code, context);

const handler = context.exports.default;
const mockRequest = {{ headers: {{ get: (k) => k === 'req-id' ? 'test-req-99' : null }} }};
handler(mockRequest).then(r => r.json()).then(j => {{
    const expectedNested = 'nested-test-req-99';
    if (j.id === 'test-req-99' && j.nestedId === expectedNested) {{
        console.log('PASS');
    }} else {{
        console.log('FAIL: got', JSON.stringify(j));
        process.exit(1);
    }}
}}).catch(e => {{ console.error(e); process.exit(1); }});
"""
    r = subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0 and "PASS" in r.stdout, f"Multiple fixture failed: {r.stderr or r.stdout}"


# [pr_diff] fail_to_pass
def test_no_per_test_instance_creation():
    """createNext must not be called inside it/test body (the core race condition bug)."""
    code = TEST_FILE.read_text()

    # If createNext isn't used at all, the fix uses an alternative — pass
    if "createNext" not in code:
        return

    # Use TypeScript-aware AST detection via Node.js
    ast_script = f"""
const fs = require('fs');
const ts = require('typescript');
const code = fs.readFileSync('{TEST_FILE}', 'utf8');
const source = ts.createSourceFile('test.ts', code, ts.ScriptTarget.Latest, true);

let inTestBody = false;
let foundBad = false;

function visit(node) {{
    // Check if this is an it() or test() call
    if (ts.isCallExpression(node) &&
        ts.isIdentifier(node.expression) &&
        (node.expression.text === 'it' || node.expression.text === 'test')) {{
        // Check arguments for a function (the test body)
        for (const arg of node.arguments) {{
            if (ts.isArrowFunction(arg) || ts.isFunctionExpression(arg)) {{
                // Visit the function body looking for createNext
                ts.forEachChild(arg.body, function visitBody(n) {{
                    if (ts.isCallExpression(n) &&
                        ts.isIdentifier(n.expression) &&
                        n.expression.text === 'createNext') {{
                        console.error('ERROR: createNext found inside ' + node.expression.text + ' body');
                        foundBad = true;
                    }}
                    ts.forEachChild(n, visitBody);
                }});
            }}
        }}
    }}
    ts.forEachChild(node, visit);
}}

visit(source);
process.exit(foundBad ? 1 : 0);
"""
    # First try with typescript parser, fall back to regex if ts not available
    result = subprocess.run(
        ["node", "-e", ast_script],
        capture_output=True, text=True, timeout=30,
    )

    # If typescript isn't available, use a simpler brace-depth approach
    if "Error: Cannot find module 'typescript'" in result.stderr:
        result = subprocess.run(
            ["node", "-e", f"""
const code = require('fs').readFileSync('{TEST_FILE}', 'utf8');
const lines = code.split('\\n');
let braceDepth = 0, inTest = false, testDepth = 0;
for (let i = 0; i < lines.length; i++) {{
    const line = lines[i];
    const testMatch = line.match(/\\b(it|test)\\s*[\\(\\.]/);
    if (testMatch && !inTest) {{
        inTest = true;
        testDepth = braceDepth;
    }}
    for (const ch of line) {{
        if (ch === '{{') braceDepth++;
        if (ch === '}}') braceDepth--;
    }}
    if (inTest && braceDepth <= testDepth) {{
        inTest = false;
    }}
    if (inTest && line.includes('createNext')) {{
        console.error('createNext at line ' + (i+1));
        process.exit(1);
    }}
}}
"""],
            capture_output=True, text=True, timeout=10,
        )

    assert result.returncode == 0, f"createNext is called inside a test body (race condition not fixed): {result.stderr}"


# [pr_diff] fail_to_pass
def test_no_inline_route_code():
    """Route handler code must not be inlined as template strings in the test file."""
    code = TEST_FILE.read_text()

    # Look for template strings that contain route handler patterns
    for match in re.findall(r"`([^`]*)`", code, re.DOTALL):
        if len(match) > 50:
            # Check for export patterns that indicate inline route code
            has_export_config = "export const config" in match
            has_export_default = "export default" in match and "async function" in match
            has_async_handler = re.search(r"export\s+(default\s+)?async\s+function\s+handler", match)

            assert not (has_export_config or has_export_default or has_async_handler), \
                f"Test file still contains inline route code as template strings: {match[:100]}..."


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
# Repo CI/CD pass_to_pass tests (p2p_enrichment)
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass
def test_test_file_valid_syntax():
    """Repo test file has valid TypeScript syntax (pass_to_pass)."""
    code = TEST_FILE.read_text()
    # Use Node.js to parse TypeScript (swc/acorn can handle it)
    script = f"""
const fs = require('fs');
const code = fs.readFileSync('{TEST_FILE}', 'utf8');
// Basic syntax validation: balanced braces and parentheses
let depth = 0;
let inString = false;
let stringChar = '';
for (let i = 0; i < code.length; i++) {{
    const ch = code[i];
    const prev = code[i-1];
    if (inString) {{
        if (ch === stringChar && prev !== '\\\\') inString = false;
    }} else if (ch === '"' || ch === "'" || ch === '`') {{
        inString = true;
        stringChar = ch;
    }} else if (ch === '{{' || ch === '(' || ch === '[') depth++;
    else if (ch === '}}' || ch === ')' || ch === ']') depth--;
}}
if (depth !== 0) {{
    console.error('Unbalanced braces/parens');
    process.exit(1);
}}
// Try parsing as module - this will catch most syntax errors
try {{
    new Function('return ' + code.replace(/export /g, '').replace(/import /g, '/*import*/ '));
}} catch(e) {{
    // Expected for module code, but not for basic syntax errors
    if (e.message.includes('Unexpected') && e.message.includes('token')) {{
        console.error('Syntax error:', e.message);
        process.exit(1);
    }}
}}
console.log('PASS');
"""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0 and "PASS" in r.stdout, f"Test file syntax validation failed: {r.stderr or r.stdout}"


# [repo_ci] pass_to_pass
def test_fixture_files_valid_syntax():
    """Repo fixture files have valid JavaScript syntax (pass_to_pass)."""
    for name in ["single", "multiple"]:
        fixture = _find_fixture(name)
        if fixture is None:
            continue  # May not exist on base commit

        # Validate syntax with node --check
        r = subprocess.run(
            ["node", "--check", fixture],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Fixture {name} has syntax errors: {r.stderr}"


# [repo_ci] pass_to_pass
def test_no_broken_imports():
    """Repo test file imports are resolvable (pass_to_pass)."""
    code = TEST_FILE.read_text()
    # Check that imports reference existing paths
    import_pattern = r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]"
    all_imports = list(re.finditer(import_pattern, code))
    assert len(all_imports) >= 1, "Test file must have at least one import statement"
    for match in all_imports:
        import_path = match.group(1)
        # Skip external packages (no slash or starts with non-relative)
        if not import_path.startswith('.') and not import_path.startswith('/'):
            continue
        # Resolve relative to test file
        base = TEST_FILE.parent
        if import_path.startswith('.'):
            resolved = base / (import_path + '.ts')
            if not resolved.exists():
                resolved = base / import_path / 'index.ts'
            # Check if it's in test/lib or similar
            if not resolved.exists():
                # These are likely provided by the test harness
                if 'e2e-utils' not in import_path and 'next-test-utils' not in import_path:
                    assert False, f"Import not resolvable: {import_path}"


# [repo_ci] pass_to_pass
def test_repo_e2e_utils_import():
    """Repo test file imports from e2e-utils (pass_to_pass)."""
    code = TEST_FILE.read_text()
    # Both base (createNext) and gold (nextTestSetup) use e2e-utils
    assert "from 'e2e-utils'" in code or 'from "e2e-utils"' in code, \
        "Test file must import from e2e-utils"


# [repo_ci] pass_to_pass
def test_repo_next_test_utils_import():
    """Repo test file imports fetchViaHTTP from next-test-utils (pass_to_pass)."""
    code = TEST_FILE.read_text()
    # Both base and gold use fetchViaHTTP from next-test-utils
    assert "from 'next-test-utils'" in code or 'from "next-test-utils"' in code, \
        "Test file must import from next-test-utils"
    assert "fetchViaHTTP" in code, \
        "Test file must use fetchViaHTTP from next-test-utils"


# [repo_ci] pass_to_pass
def test_repo_describe_block():
    """Repo test file has a describe block (pass_to_pass)."""
    code = TEST_FILE.read_text()
    assert re.search(r"\bdescribe\s*\(", code), \
        "Test file must have a describe block"


# [repo_ci] pass_to_pass
def test_repo_it_test_pattern():
    """Repo test file has it/test calls (pass_to_pass)."""
    code = TEST_FILE.read_text()
    # Check for it() or test() calls - both base and gold use it()
    assert re.search(r"\b(it|test)\s*[\(\.]", code), \
        "Test file must have it() or test() calls"


# [repo_ci] pass_to_pass
def test_repo_als_pattern():
    """Repo test or fixture files reference AsyncLocalStorage pattern (pass_to_pass)."""
    found = False
    test_code = TEST_FILE.read_text()
    if "AsyncLocalStorage" in test_code:
        found = True
    if not found:
        for name in ["single", "multiple"]:
            fixture = _find_fixture(name)
            if fixture:
                fixture_code = Path(fixture).read_text()
                if "AsyncLocalStorage" in fixture_code:
                    found = True
                    break
    assert found, "AsyncLocalStorage pattern not found in test or fixture files"


# [repo_ci] pass_to_pass
def test_repo_req_id_pattern():
    """Repo test file uses req-id header pattern (pass_to_pass)."""
    code = TEST_FILE.read_text()
    # Both base and gold use req-id headers
    assert "req-id" in code, \
        "Test file must use req-id header pattern"


# [repo_ci] pass_to_pass
def test_repo_promise_all_pattern():
    """Repo test file uses Promise.all for concurrent requests (pass_to_pass)."""
    code = TEST_FILE.read_text()
    # Both base and gold use Promise.all for concurrent requests
    assert "Promise.all" in code, \
        "Test file must use Promise.all for concurrent requests"


# [repo_ci] pass_to_pass
def test_repo_edge_runtime_pattern():
    """Repo test or fixture files reference edge runtime config (pass_to_pass)."""
    found = False
    test_code = TEST_FILE.read_text()
    if "runtime: 'edge'" in test_code or 'runtime: "edge"' in test_code:
        found = True
    if not found:
        for name in ["single", "multiple"]:
            fixture = _find_fixture(name)
            if fixture:
                fixture_code = Path(fixture).read_text()
                if "runtime: 'edge'" in fixture_code or 'runtime: "edge"' in fixture_code:
                    found = True
                    break
    assert found, "Edge runtime config not found in test or fixture files"


# [repo_ci] pass_to_pass
def test_repo_no_commonjs():
    """Repo test file does not use CommonJS require/module.exports (pass_to_pass)."""
    code = TEST_FILE.read_text()
    # Next.js tests should use ES modules, not CommonJS
    assert "require(" not in code or "import " in code, \
        "Test file should prefer ES modules over CommonJS"


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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_thank_you__build_pnpm():
    """pass_to_pass | CI job 'thank you, build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm install'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_thank_you__build_pnpm_2():
    """pass_to_pass | CI job 'thank you, build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")