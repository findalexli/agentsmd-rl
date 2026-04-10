"""
Task: nextjs-otel-span-route-fallback
Repo: vercel/next.js @ 3003e17b102699bffca325257ae7be53fda69052
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

_ROUTE_EVAL_JS = textwrap.dedent(r"""
const fs = require("fs");
const filePath = process.argv[2];
const mode = process.argv[3] || "fallback";
const src = fs.readFileSync(filePath, "utf8");
const lines = src.split("\n");

function stripTS(line) {
    return line.trim()
        .replace(/(const|let|var)\s+(\w+)\s*:\s*[^=;]+\s*=/g, "$1 $2 =")
        .replace(/\bas\s+[\w|&\s<>,[\]]+/g, "")
        .replace(/(\)|\w)!(?=[.\s;|?&,\n])/g, "$1")
        .replace(/\s*\/\/.*$/, "");
}

let getIdx = -1;
for (let i = 0; i < lines.length; i++) {
    if (/rootSpanAttributes\s*\.?\s*get\s*\(\s*['"]next\.route/.test(lines[i])) {
        getIdx = i;
        break;
    }
}
if (getIdx === -1) {
    console.error("no rootSpanAttributes.get('next.route') found");
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
    console.error("could not extract route computation");
    process.exit(1);
}

let code = block.join("\n").replace(/\b(const|var)\s+route\b/g, "let route");
code += "\nreturn typeof route !== \"undefined\" ? route : undefined;";

const rootSpanAttributes = new Map();
if (mode === "present") {
    rootSpanAttributes.set("next.route", "/expected/dynamic/route");
}
const normalizedSrcPage = "/app/[param]/page";
const srcPage = "/api/test-handler";

try {
    const fn = new Function("rootSpanAttributes", "normalizedSrcPage", "srcPage", code);
    const result = fn(rootSpanAttributes, normalizedSrcPage, srcPage);

    if (mode === "present") {
        if (result === "/expected/dynamic/route") process.exit(0);
        console.error("expected /expected/dynamic/route, got " + JSON.stringify(result));
        process.exit(1);
    }

    if (!result || (typeof result === "string" && result.trim() === "")) {
        console.error("route is empty/falsy: " + JSON.stringify(result));
        process.exit(1);
    }
    if (typeof result === "string" && result.startsWith("/")) {
        process.exit(0);
    }
    console.error("route is not a valid path: " + JSON.stringify(result));
    process.exit(1);
} catch (e) {
    console.error("eval error: " + e.message);
    process.exit(1);
}
""")


def _eval_route(filepath: str, mode: str = "fallback") -> subprocess.CompletedProcess:
    js_path = "/tmp/_test_route_eval.js"
    Path(js_path).write_text(_ROUTE_EVAL_JS)
    return subprocess.run(
        ["node", js_path, filepath, mode],
        capture_output=True, text=True, timeout=10,
    )


# [pr_diff] fail_to_pass
def test_app_page_route_fallback():
    r = _eval_route(APP_PAGE, "fallback")
    assert r.returncode == 0, "app-page.ts route fallback failed: " + str(r.stderr)


# [pr_diff] fail_to_pass
def test_app_route_route_fallback():
    r = _eval_route(APP_ROUTE, "fallback")
    assert r.returncode == 0, "app-route.ts route fallback failed: " + str(r.stderr)


# [pr_diff] fail_to_pass
def test_pages_api_route_fallback():
    r = _eval_route(PAGES_API, "fallback")
    assert r.returncode == 0, "pages-api.ts route fallback failed: " + str(r.stderr)


# [pr_diff] fail_to_pass
def test_pages_handler_route_fallback():
    r = _eval_route(PAGES_HANDLER, "fallback")
    assert r.returncode == 0, "pages-handler.ts route fallback failed: " + str(r.stderr)


# [pr_diff] fail_to_pass
def test_wrapped_by_server_detection():
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


# [pr_diff] fail_to_pass
def test_parent_span_propagation():
    for filepath in ALL_FILES:
        src = Path(filepath).read_text()
        lines = src.split("\n")
        name = Path(filepath).name
        route_idx = None
        for i, line in enumerate(lines):
            # Check for rootSpanAttributes.get with either quote type
            pattern1 = 'rootSpanAttributes.get("next.route")'
            pattern2 = "rootSpanAttributes.get('next.route')"
            if pattern1 in line or pattern2 in line:
                route_idx = i
                break
        assert route_idx is not None, "{}: no rootSpanAttributes.get found".format(name)
        parent_set_idx = None
        for i in range(route_idx, min(route_idx + 25, len(lines))):
            if "parentSpan" in lines[i] and "setAttribute" in lines[i] and "http.route" in lines[i]:
                parent_set_idx = i
                break
        assert parent_set_idx is not None, "{}: parentSpan.setAttribute not found".format(name)
        for i in range(route_idx + 1, parent_set_idx):
            assert not re.search(r"if\s*\(\s*route\s*\)", lines[i]), "{}: gated by if (route)".format(name)


# [pr_diff] pass_to_pass
def test_route_uses_next_route_when_present():
    for filepath in ALL_FILES:
        r = _eval_route(filepath, "present")
        msg = "{}: did not use next.route: {}".format(Path(filepath).name, r.stderr)
        assert r.returncode == 0, msg


# [static] pass_to_pass
def test_span_logic_not_stubbed():
    for filepath in ALL_FILES:
        src = Path(filepath).read_text()
        name = Path(filepath).name
        assert "setAttributes" in src, "{}: missing setAttributes".format(name)
        assert "updateName" in src, "{}: missing updateName".format(name)


# [static] pass_to_pass
def test_repo_typescript_parse():
    for filepath in ALL_FILES:
        src = Path(filepath).read_text()
        name = Path(filepath).name
        assert src.count("{") == src.count("}"), "{}: unbalanced braces".format(name)
        assert src.count("(") == src.count(")"), "{}: unbalanced parens".format(name)
        assert len(src.strip()) > 0, "{}: file empty".format(name)
        assert "export" in src or "import" in src, "{}: missing keywords".format(name)


# [static] pass_to_pass
def test_repo_otel_parent_span_structure():
    for filepath in ALL_FILES:
        src = Path(filepath).read_text()
        name = Path(filepath).name
        assert "parentSpan" in src, "{}: missing parentSpan".format(name)
        assert "setAttribute" in src, "{}: missing setAttribute".format(name)
        assert "rootSpanAttributes.get('next.route')" in src or 'rootSpanAttributes.get("next.route")' in src, "{}: missing rootSpanAttributes.get".format(name)


# [static] pass_to_pass
def test_repo_pages_handler_structure():
    src = Path(PAGES_HANDLER).read_text()
    assert "activeSpan" in src, "missing activeSpan"
    assert "getTracer" in src, "missing getTracer"
    assert "handleResponse" in src, "missing handleResponse"


# [repo_tests] pass_to_pass
def test_repo_tsc_syntax_check():
    for filepath in ALL_FILES:
        r = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ES2020",
             "--module", "commonjs", "--ignoreConfig", filepath],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        stderr_lines = r.stderr.strip().split("\n") if r.stderr else []
        syntax_errors = [l for l in stderr_lines if "error TS" in l and "TS5107" not in l]
        assert len(syntax_errors) == 0, "Syntax errors in {}".format(Path(filepath).name)


# [repo_tests] pass_to_pass
def test_repo_git_status_clean():
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, "git status failed: {}".format(r.stderr)
    assert r.stdout.strip() == "", "Repo has uncommitted changes: {}".format(r.stdout)
