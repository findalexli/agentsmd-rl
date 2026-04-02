"""
Task: nextjs-otel-span-route-fallback
Repo: vercel/next.js @ 3003e17b102699bffca325257ae7be53fda69052

When Next.js handler exports are invoked directly (without base-server),
OpenTelemetry span names must include the route, not just the HTTP method.
The fix adds a fallback to normalizedSrcPage/srcPage when rootSpanAttributes
lacks 'next.route', and gates the activeSpan path in pages-handler.ts.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/next.js"

APP_PAGE = f"{REPO}/packages/next/src/build/templates/app-page.ts"
APP_ROUTE = f"{REPO}/packages/next/src/build/templates/app-route.ts"
PAGES_API = f"{REPO}/packages/next/src/build/templates/pages-api.ts"
PAGES_HANDLER = f"{REPO}/packages/next/src/server/route-modules/pages/pages-handler.ts"

ALL_FILES = [APP_PAGE, APP_ROUTE, PAGES_API, PAGES_HANDLER]

# Node.js evaluator: extracts the route-computation expression from a TS
# template, strips type annotations, and evals it with mocked dependencies.
# Accepts any valid fallback pattern: ||, ??, ternary, if/else, etc.
_ROUTE_EVAL_JS = textwrap.dedent(r"""
    const fs = require('fs');
    const filePath = process.argv[2];
    const mode = process.argv[3] || 'fallback';
    const src = fs.readFileSync(filePath, 'utf8');
    const lines = src.split('\n');

    function stripTS(line) {
        return line.trim()
            .replace(/(const|let|var)\s+(\w+)\s*:\s*[^=;]+\s*=/g, '$1 $2 =')
            .replace(/\bas\s+[\w|&\s<>,[\]]+/g, '')
            .replace(/(\)|\w)!(?=[.\s;|?&,\n])/g, '$1')
            .replace(/\s*\/\/.*$/, '');
    }

    let getIdx = -1;
    for (let i = 0; i < lines.length; i++) {
        if (/rootSpanAttributes\s*\.?\s*get\s*\(\s*['"]next\.route/.test(lines[i])) {
            getIdx = i;
            break;
        }
    }
    if (getIdx === -1) {
        console.error('no rootSpanAttributes.get("next.route") found');
        process.exit(1);
    }

    let block = [];
    let routeAssignIdx = -1;
    for (let i = getIdx; i < Math.min(getIdx + 10, lines.length); i++) {
        block.push(stripTS(lines[i]));
        if (/\broute\s*=/.test(lines[i])) {
            routeAssignIdx = i;
            break;
        }
    }

    if (routeAssignIdx >= 0) {
        for (let i = routeAssignIdx + 1; i < Math.min(routeAssignIdx + 8, lines.length); i++) {
            const trimmed = lines[i].trim();
            if (/if\s*\(\s*!route\s*\)\s*route\s*=/.test(trimmed)) {
                block.push(stripTS(lines[i]));
                break;
            }
            if (/if\s*\(\s*!route\s*\)\s*\{?\s*$/.test(trimmed)) {
                block.push(stripTS(lines[i]));
                for (let j = i + 1; j < Math.min(i + 4, lines.length); j++) {
                    block.push(stripTS(lines[j]));
                    if (/route\s*=/.test(lines[j])) break;
                }
                break;
            }
            if (/^\s*route\s*=/.test(trimmed) && !/const|let|var/.test(trimmed)) {
                block.push(stripTS(lines[i]));
                break;
            }
        }
    }

    if (block.length === 0) {
        console.error('could not extract route computation');
        process.exit(1);
    }

    let code = block.join('\n').replace(/\b(const|var)\s+route\b/g, 'let route');
    code += '\nreturn typeof route !== "undefined" ? route : undefined;';

    const rootSpanAttributes = new Map();
    if (mode === 'present') {
        rootSpanAttributes.set('next.route', '/expected/dynamic/route');
    }
    const normalizedSrcPage = '/app/[param]/page';
    const srcPage = '/api/test-handler';

    try {
        const fn = new Function('rootSpanAttributes', 'normalizedSrcPage', 'srcPage', code);
        const result = fn(rootSpanAttributes, normalizedSrcPage, srcPage);

        if (mode === 'present') {
            if (result === '/expected/dynamic/route') process.exit(0);
            console.error('expected /expected/dynamic/route, got ' + JSON.stringify(result));
            process.exit(1);
        }

        if (!result || (typeof result === 'string' && result.trim() === '')) {
            console.error('route is empty/falsy: ' + JSON.stringify(result));
            process.exit(1);
        }
        if (typeof result === 'string' && result.startsWith('/')) {
            process.exit(0);
        }
        console.error('route is not a valid path: ' + JSON.stringify(result));
        process.exit(1);
    } catch (e) {
        console.error('eval error: ' + e.message);
        process.exit(1);
    }
""")


def _eval_route(filepath: str, mode: str = "fallback") -> subprocess.CompletedProcess:
    """Evaluate the route-computation expression from a TS template file."""
    js_path = "/tmp/_test_route_eval.js"
    Path(js_path).write_text(_ROUTE_EVAL_JS)
    return subprocess.run(
        ["node", js_path, filepath, mode],
        capture_output=True, text=True, timeout=10,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — route fallback behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_app_page_route_fallback():
    """app-page.ts: route falls back to page identifier when next.route absent."""
    r = _eval_route(APP_PAGE, "fallback")
    assert r.returncode == 0, f"app-page.ts route fallback failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_app_route_route_fallback():
    """app-route.ts: route falls back to page identifier when next.route absent."""
    r = _eval_route(APP_ROUTE, "fallback")
    assert r.returncode == 0, f"app-route.ts route fallback failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_pages_api_route_fallback():
    """pages-api.ts: route falls back to page identifier when next.route absent."""
    r = _eval_route(PAGES_API, "fallback")
    assert r.returncode == 0, f"pages-api.ts route fallback failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_pages_handler_route_fallback():
    """pages-handler.ts: route falls back to page identifier when next.route absent."""
    r = _eval_route(PAGES_HANDLER, "fallback")
    assert r.returncode == 0, f"pages-handler.ts route fallback failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_wrapped_by_server_detection():
    """pages-handler.ts: activeSpan path is gated by server-wrapper detection."""
    src = Path(PAGES_HANDLER).read_text()
    has_bare = bool(re.search(r"if\s*\(\s*activeSpan\s*\)\s*\{", src))
    has_wrapped = bool(
        re.search(r"isWrapped|wrappedByNextServer|isWrappedByNextServer|baseServerSpan", src, re.I)
    )
    has_combined = bool(
        re.search(r"if\s*\([^)]*activeSpan[^)]*&&|if\s*\([^)]*&&[^)]*activeSpan", src)
    )
    assert not has_bare or has_wrapped or has_combined, (
        "pages-handler.ts has bare if(activeSpan) without wrapped-by-server detection"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — parentSpan propagation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_parent_span_propagation():
    """All 4 files: parentSpan http.route is set unconditionally (not gated by route truthiness)."""
    for filepath in ALL_FILES:
        src = Path(filepath).read_text()
        lines = src.split('\n')
        name = Path(filepath).name

        # Find rootSpanAttributes.get('next.route')
        route_idx = None
        for i, line in enumerate(lines):
            if re.search(r"rootSpanAttributes\s*\.?\s*get\s*\(\s*['\"]next\.route", line):
                route_idx = i
                break
        assert route_idx is not None, f"{name}: no rootSpanAttributes.get('next.route') found"

        # Find parentSpan.setAttribute('http.route') within next 25 lines
        parent_set_idx = None
        for i in range(route_idx, min(route_idx + 25, len(lines))):
            if re.search(r"parentSpan\s*\.\s*setAttribute\s*\(\s*['\"]http\.route", lines[i]):
                parent_set_idx = i
                break
        assert parent_set_idx is not None, (
            f"{name}: parentSpan.setAttribute('http.route') not found near route logic"
        )

        # Verify no 'if (route)' between route assignment and parentSpan —
        # the base commit gates propagation inside if(route){...}, the fix
        # makes it unconditional by using a fallback value.
        for i in range(route_idx + 1, parent_set_idx):
            assert not re.search(r'if\s*\(\s*route\s*\)', lines[i]), (
                f"{name}: parentSpan propagation gated by 'if (route)' at line {i+1}"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_route_uses_next_route_when_present():
    """All 4 files use next.route value when rootSpanAttributes has it."""
    for filepath in ALL_FILES:
        r = _eval_route(filepath, "present")
        assert r.returncode == 0, (
            f"{Path(filepath).name}: didn't use next.route when present:\n{r.stderr}"
        )


# [static] pass_to_pass
def test_span_logic_not_stubbed():
    """All 4 files contain real span logic (setAttributes + updateName)."""
    for filepath in ALL_FILES:
        src = Path(filepath).read_text()
        name = Path(filepath).name
        assert "setAttributes" in src, f"{name}: missing setAttributes (stubbed?)"
        assert "updateName" in src, f"{name}: missing updateName (stubbed?)"
