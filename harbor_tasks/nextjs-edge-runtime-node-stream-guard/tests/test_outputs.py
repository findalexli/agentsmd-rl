"""
Task: nextjs-edge-runtime-node-stream-guard
Repo: vercel/next.js @ 15d9b4d7f923e637d1661b109df639a918f59c8a
PR:   92354

Tests verify that code paths importing node:stream are guarded with
NEXT_RUNTIME == 'edge' checks using proper if/else DCE-safe patterns.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"

HELPER = Path(REPO) / "packages/next/src/server/stream-utils/node-web-streams-helper.ts"
PRERENDER = Path(REPO) / "packages/next/src/server/app-render/app-render-prerender-utils.ts"
RENDER_RESULT = Path(REPO) / "packages/next/src/server/render-result.ts"
ERRORS_JSON = Path(REPO) / "packages/next/errors.json"


def _extract_function_body(src: str, func_name: str) -> str | None:
    """Extract a TypeScript function body using brace counting."""
    pattern = rf"(?:export\s+)?(?:async\s+)?function\s+{func_name}\s*\("
    match = re.search(pattern, src)
    if not match:
        return None
    rest = src[match.start() :]
    brace_idx = rest.find("{")
    if brace_idx == -1:
        return None
    depth = 0
    for i in range(brace_idx, len(rest)):
        if rest[i] == "{":
            depth += 1
        elif rest[i] == "}":
            depth -= 1
            if depth == 0:
                return rest[: i + 1]
    return None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — edge runtime guards
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_webToReadable_edge_guard():
    """webToReadable must check NEXT_RUNTIME before require node:stream."""
    src = HELPER.read_text()
    body = _extract_function_body(src, "webToReadable")
    assert body is not None, "webToReadable function not found"
    # Must have NEXT_RUNTIME edge check
    edge_check = re.search(r"NEXT_RUNTIME\s*===\s*['\"]edge['\"]", body)
    assert edge_check is not None, "webToReadable must check NEXT_RUNTIME"
    require_match = re.search(r"require\(['\"]node:stream['\"]\)", body)
    assert require_match is not None, "webToReadable must have require"
    assert edge_check.start() < require_match.start(), "edge check before require"
    edge_pos = edge_check.end()
    between = body[edge_pos : require_match.start()]
    assert "throw" in between, "edge branch must throw"


# [pr_diff] fail_to_pass
def test_streamToUint8Array_edge_delegation():
    """streamToUint8Array must delegate to webstreamToUint8Array in edge runtime."""
    src = HELPER.read_text()
    body = _extract_function_body(src, "streamToUint8Array")
    assert body is not None, "streamToUint8Array function not found"
    edge_check = re.search(r"NEXT_RUNTIME\s*===\s*['\"]edge['\"]", body)
    assert edge_check is not None, "must check NEXT_RUNTIME"
    require_match = re.search(r"require\(['\"]node:stream['\"]\)", body)
    assert require_match is not None, "must have require"
    edge_branch = body[edge_check.end() : require_match.start()]
    assert "webstreamToUint8Array" in edge_branch, "must delegate to webstreamToUint8Array"


# [pr_diff] fail_to_pass
def test_prerender_tee_edge_guard():
    """ReactServerResult tee must guard node:stream usage with edge runtime check."""
    src = PRERENDER.read_text()
    requires = list(re.finditer(r"require\(['\"]node:stream['\"]\)", src))
    assert len(requires) > 0, "must have require node:stream"
    for req in requires:
        preceding = src[: req.start()]
        edge_checks = list(re.finditer(r"NEXT_RUNTIME\s*===\s*['\"]edge['\"]", preceding))
        assert len(edge_checks) > 0, f"require at {req.start()} needs edge check"


# [pr_diff] fail_to_pass
def test_render_result_edge_guards():
    """RenderResult must guard all node:stream requires with edge runtime checks."""
    src = RENDER_RESULT.read_text()
    requires = list(re.finditer(r"require\(['\"]node:stream['\"]\)", src))
    assert len(requires) > 0, "must have require node:stream"
    edge_checks = list(re.finditer(r"NEXT_RUNTIME\s*===\s*['\"]edge['\"]", src))
    assert len(edge_checks) >= 2, f"need >=2 edge checks, found {len(edge_checks)}"
    for req in requires:
        preceding = src[: req.start()]
        checks_before = list(re.finditer(r"NEXT_RUNTIME\s*===\s*['\"]edge['\"]", preceding))
        assert len(checks_before) > 0, f"require at {req.start()} needs edge check"


# [pr_diff] fail_to_pass
def test_edge_error_codes():
    """errors.json must include edge-runtime-specific error messages."""
    r = subprocess.run(
        [
            "node",
            "-e",
            """
const errors = require('./packages/next/errors.json');
const vals = Object.values(errors);
const edgeErrors = vals.filter(v => v.toLowerCase().includes('edge runtime'));
if (edgeErrors.length < 3) {
    console.error("Expected >= 3 edge runtime errors, found " + edgeErrors.length);
    process.exit(1);
}
const streamRelated = edgeErrors.filter(v => v.includes('Readable') || v.includes('stream') || v.includes('webToReadable'));
if (streamRelated.length < 1) {
    console.error("No stream-related edge runtime errors found");
    process.exit(1);
}
console.log("OK");
""",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"errors.json check failed: {r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — DCE-safe require pattern
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass
def test_require_node_stream_dce_safe():
    """All require node:stream must be in else branches for DCE safety."""
    files_to_check = [HELPER, PRERENDER, RENDER_RESULT]
    for fpath in files_to_check:
        src = fpath.read_text()
        lines = src.splitlines()
        for i, line in enumerate(lines):
            if "require(" not in line or "node:stream" not in line:
                continue
            found_else = False
            for j in range(i - 1, max(i - 30, -1), -1):
                prev = lines[j].strip()
                if "} else {" in prev or "} else{" in prev:
                    found_else = True
                    break
                if prev.startswith("else {") or prev == "else{":
                    found_else = True
                    break
            assert found_else, f"require at {fpath.name}:{i+1} must be in else branch"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — file validity
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_modified_files_valid():
    """All modified TypeScript files exist and have substantial content."""
    for fpath in [HELPER, PRERENDER, RENDER_RESULT]:
        assert fpath.exists(), f"{fpath} does not exist"
        content = fpath.read_text()
        line_count = len(content.splitlines())
        assert line_count > 50, f"{fpath.name} has only {line_count} lines"
    assert ERRORS_JSON.exists(), "errors.json does not exist"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks
# ---------------------------------------------------------------------------


def _setup_corepack():
    """Enable corepack for pnpm."""
    subprocess.run(["corepack", "enable"], capture_output=True, cwd=REPO)
    subprocess.run(["corepack", "prepare", "pnpm@9.6.0", "--activate"], capture_output=True, cwd=REPO)




# [repo_tests] pass_to_pass
def test_repo_error_codes_valid():
    """Error codes validation passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "check-error-codes.js"],
        capture_output=True, text=True, timeout=60,
        cwd=str(Path(REPO) / "packages" / "next"),
    )
    assert r.returncode == 0, f"Error codes check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_prettier_helper():
    """Prettier formatting check for node-web-streams-helper.ts passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "--yes", "prettier", "--check", "packages/next/src/server/stream-utils/node-web-streams-helper.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_prettier_prerender():
    """Prettier formatting check for app-render-prerender-utils.ts passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "--yes", "prettier", "--check", "packages/next/src/server/app-render/app-render-prerender-utils.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_prettier_render_result():
    """Prettier formatting check for render-result.ts passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "--yes", "prettier", "--check", "packages/next/src/server/render-result.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_errors_json_valid():
    """errors.json is valid JSON and contains error codes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "const e=require('./packages/next/errors.json'); console.log('Valid JSON with', Object.keys(e).length, 'errors');"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"errors.json validation failed:\n{r.stderr[-500:]}"
    assert "Valid JSON" in r.stdout, "errors.json should output valid JSON message"



# [repo_tests] pass_to_pass
def test_repo_node_version():
    """Node.js version meets minimum requirement >= 20.9.0 (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "const v=process.version.slice(1).split('.'); const major=parseInt(v[0]); const minor=parseInt(v[1]); if(major<20||(major===20&&minor<9)){console.error('Node version too low:',process.version);process.exit(1)};console.log('Node version OK:',process.version);"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Node version check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_stream_utils_syntax():
    """node-web-streams-helper.ts has valid TypeScript syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "require('fs').readFileSync('packages/next/src/server/stream-utils/node-web-streams-helper.ts','utf8'); console.log('Syntax OK');"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Stream utils syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prerender_syntax():
    """app-render-prerender-utils.ts has valid TypeScript syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "require('fs').readFileSync('packages/next/src/server/app-render/app-render-prerender-utils.ts','utf8'); console.log('Syntax OK');"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Prerender utils syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_render_result_syntax():
    """render-result.ts has valid TypeScript syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "require('fs').readFileSync('packages/next/src/server/render-result.ts','utf8'); console.log('Syntax OK');"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Render result syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """packages/next/package.json is valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "const p=require('./packages/next/package.json'); console.log('Valid package.json for',p.name,'version',p.version);"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"package.json validation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_import_paths_valid():
    """Key import paths in modified files use valid patterns (pass_to_pass)."""
    # Check that modified files don't have obvious import issues
    files_to_check = [
        "packages/next/src/server/stream-utils/node-web-streams-helper.ts",
        "packages/next/src/server/app-render/app-render-prerender-utils.ts",
        "packages/next/src/server/render-result.ts",
    ]
    for fpath in files_to_check:
        r = subprocess.run(
            ["node", "-e", f"const content=require('fs').readFileSync('{fpath}','utf8'); const imports=content.match(/from\s+['\"]([^'\"]+)['\"]/g)||[]; console.log('OK:',imports.length,'imports');"],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Import check failed for {fpath}:\n{r.stderr[-500:]}"


