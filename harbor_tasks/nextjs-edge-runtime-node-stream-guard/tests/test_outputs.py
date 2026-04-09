"""
Task: nextjs-edge-runtime-node-stream-guard
Repo: vercel/next.js @ 15d9b4d7f923e637d1661b109df639a918f59c8a
PR:   92354

Tests verify that code paths importing node:stream are guarded with
NEXT_RUNTIME === 'edge' checks using proper if/else DCE-safe patterns.
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
    """webToReadable must check NEXT_RUNTIME === 'edge' before require('node:stream')."""
    src = HELPER.read_text()
    body = _extract_function_body(src, "webToReadable")
    assert body is not None, "webToReadable function not found in node-web-streams-helper.ts"

    # Must have NEXT_RUNTIME edge check
    edge_check = re.search(r"NEXT_RUNTIME\s*===\s*['\"]edge['\"]", body)
    assert edge_check is not None, (
        "webToReadable must check process.env.NEXT_RUNTIME === 'edge'"
    )

    # The edge check must come BEFORE the first require('node:stream')
    require_match = re.search(r"require\(['\"]node:stream['\"]\)", body)
    assert require_match is not None, (
        "webToReadable must still have require('node:stream') for non-edge runtime"
    )
    assert edge_check.start() < require_match.start(), (
        "NEXT_RUNTIME === 'edge' check must appear before require('node:stream')"
    )

    # The edge branch must throw an error (not silently skip)
    edge_pos = edge_check.end()
    between = body[edge_pos : require_match.start()]
    assert "throw" in between, (
        "The edge runtime branch must throw an error when node:stream is unavailable"
    )


# [pr_diff] fail_to_pass
def test_streamToUint8Array_edge_delegation():
    """streamToUint8Array must delegate to webstreamToUint8Array in edge runtime."""
    src = HELPER.read_text()
    body = _extract_function_body(src, "streamToUint8Array")
    assert body is not None, "streamToUint8Array function not found"

    edge_check = re.search(r"NEXT_RUNTIME\s*===\s*['\"]edge['\"]", body)
    assert edge_check is not None, (
        "streamToUint8Array must check process.env.NEXT_RUNTIME === 'edge'"
    )

    # In the edge branch (between the edge check and require), should call webstreamToUint8Array
    require_match = re.search(r"require\(['\"]node:stream['\"]\)", body)
    assert require_match is not None, (
        "streamToUint8Array must still have require('node:stream') for non-edge runtime"
    )
    edge_branch = body[edge_check.end() : require_match.start()]
    assert "webstreamToUint8Array" in edge_branch, (
        "Edge runtime branch must delegate to webstreamToUint8Array"
    )


# [pr_diff] fail_to_pass
def test_prerender_tee_edge_guard():
    """ReactServerResult tee must guard node:stream usage with edge runtime check."""
    src = PRERENDER.read_text()

    # Find all require('node:stream') positions
    requires = list(re.finditer(r"require\(['\"]node:stream['\"]\)", src))
    assert len(requires) > 0, "app-render-prerender-utils.ts must have require('node:stream')"

    # Each require must be preceded by a NEXT_RUNTIME edge check
    for req in requires:
        preceding = src[: req.start()]
        edge_checks = list(re.finditer(r"NEXT_RUNTIME\s*===\s*['\"]edge['\"]", preceding))
        assert len(edge_checks) > 0, (
            f"require('node:stream') at offset {req.start()} in "
            "app-render-prerender-utils.ts must be preceded by a "
            "NEXT_RUNTIME === 'edge' check"
        )


# [pr_diff] fail_to_pass
def test_render_result_edge_guards():
    """RenderResult must guard all node:stream requires with edge runtime checks."""
    src = RENDER_RESULT.read_text()

    requires = list(re.finditer(r"require\(['\"]node:stream['\"]\)", src))
    assert len(requires) > 0, "render-result.ts must have require('node:stream')"

    edge_checks = list(re.finditer(r"NEXT_RUNTIME\s*===\s*['\"]edge['\"]", src))

    # The PR adds 2 edge guards (toReadableStream and tee each have a
    # code path with require('node:stream'))
    assert len(edge_checks) >= 2, (
        f"render-result.ts must have at least 2 NEXT_RUNTIME === 'edge' checks, "
        f"found {len(edge_checks)}"
    )

    # Each require must be preceded by an edge check
    for req in requires:
        preceding = src[: req.start()]
        checks_before = list(
            re.finditer(r"NEXT_RUNTIME\s*===\s*['\"]edge['\"]", preceding)
        )
        assert len(checks_before) > 0, (
            f"require('node:stream') at offset {req.start()} in render-result.ts "
            "must be preceded by a NEXT_RUNTIME === 'edge' check"
        )


# [pr_diff] fail_to_pass
def test_edge_error_codes():
    """errors.json must include edge-runtime-specific error messages for stream operations."""
    r = subprocess.run(
        [
            "node",
            "-e",
            """
const errors = require('./packages/next/errors.json');
const vals = Object.values(errors);
// At least 3 error messages must mention 'edge runtime' (for the 3 guarded code paths)
const edgeErrors = vals.filter(v => v.toLowerCase().includes('edge runtime'));
if (edgeErrors.length < 3) {
    console.error('Expected >= 3 edge runtime errors, found ' + edgeErrors.length);
    console.error('Found:', JSON.stringify(edgeErrors));
    process.exit(1);
}
// At least one must relate to streams/Readable
const streamRelated = edgeErrors.filter(v =>
    v.includes('Readable') || v.includes('stream') || v.includes('webToReadable')
);
if (streamRelated.length < 1) {
    console.error('No stream-related edge runtime errors found');
    process.exit(1);
}
console.log('Found', edgeErrors.length, 'edge runtime error codes');
""",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"errors.json missing edge runtime error codes:\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — DCE-safe require pattern
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — AGENTS.md:404 @ 15d9b4d7f923e637d1661b109df639a918f59c8a
def test_require_node_stream_dce_safe():
    """All require('node:stream') must be in else branches of if/else for DCE safety.

    Per AGENTS.md line 404: 'Keep require() behind compile-time if/else
    branches for DCE (avoid early-return/throw patterns).'
    """
    files_to_check = [HELPER, PRERENDER, RENDER_RESULT]

    for fpath in files_to_check:
        src = fpath.read_text()
        lines = src.splitlines()

        for i, line in enumerate(lines):
            if "require(" not in line or "node:stream" not in line:
                continue

            # Look backwards for the nearest enclosing else branch
            found_else = False
            for j in range(i - 1, max(i - 30, -1), -1):
                prev = lines[j].strip()
                if "} else {" in prev or "} else{" in prev:
                    found_else = True
                    break
                if prev.startswith("else {") or prev == "else{":
                    found_else = True
                    break
            assert found_else, (
                f"require('node:stream') at {fpath.name}:{i + 1} must be inside "
                f"an else branch (if/else pattern) for DCE safety per AGENTS.md"
            )


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
        assert line_count > 50, (
            f"{fpath.name} has only {line_count} lines, expected >50"
        )
    assert ERRORS_JSON.exists(), "errors.json does not exist"
