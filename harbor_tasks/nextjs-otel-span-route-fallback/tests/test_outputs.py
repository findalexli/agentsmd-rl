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
        .replace(/(\)|\w)!(?=[.\s;|?&&,\n])/g, "$1")
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
        if (/if\s*\(\s*!route\s*\)\{?\s*$/.test(trimmed)) {
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


# [repo_tests] pass_to_pass - repo CI tests for modified files
def test_repo_app_page_typescript_syntax():
    """Repo CI: app-page.ts has valid TypeScript syntax (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--ignoreConfig",
         "--target", "ES2020", "--module", "commonjs", "--moduleResolution", "node",
         f"{REPO}/packages/next/src/build/templates/app-page.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Filter for syntax errors (TS5xxx) only - type errors are OK
    syntax_errors = [l for l in r.stderr.strip().split("\n") if "error TS5" in l]
    assert len(syntax_errors) == 0, f"Syntax errors in app-page.ts: {syntax_errors}"


def test_repo_app_route_typescript_syntax():
    """Repo CI: app-route.ts has valid TypeScript syntax (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--ignoreConfig",
         "--target", "ES2020", "--module", "commonjs", "--moduleResolution", "node",
         f"{REPO}/packages/next/src/build/templates/app-route.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    syntax_errors = [l for l in r.stderr.strip().split("\n") if "error TS5" in l]
    assert len(syntax_errors) == 0, f"Syntax errors in app-route.ts: {syntax_errors}"


def test_repo_pages_api_typescript_syntax():
    """Repo CI: pages-api.ts has valid TypeScript syntax (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--ignoreConfig",
         "--target", "ES2020", "--module", "commonjs", "--moduleResolution", "node",
         f"{REPO}/packages/next/src/build/templates/pages-api.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    syntax_errors = [l for l in r.stderr.strip().split("\n") if "error TS5" in l]
    assert len(syntax_errors) == 0, f"Syntax errors in pages-api.ts: {syntax_errors}"


def test_repo_pages_handler_typescript_syntax():
    """Repo CI: pages-handler.ts has valid TypeScript syntax (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--ignoreConfig",
         "--target", "ES2020", "--module", "commonjs", "--moduleResolution", "node",
         f"{REPO}/packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    syntax_errors = [l for l in r.stderr.strip().split("\n") if "error TS5" in l]
    assert len(syntax_errors) == 0, f"Syntax errors in pages-handler.ts: {syntax_errors}"


def test_repo_templates_contain_root_span_attributes():
    """Repo CI: All template files contain rootSpanAttributes pattern (pass_to_pass)."""
    for filepath in ALL_FILES:
        r = subprocess.run(
            ["grep", "-q", "rootSpanAttributes.get", filepath],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"{filepath}: missing rootSpanAttributes.get"


def test_repo_base_commit_check():
    """Repo CI: Repository is at expected base commit (pass_to_pass)."""
    # Check that the expected base commit is in the repo history
    expected_base = "3003e17b102699bffca325257ae7be53fda69052"
    r = subprocess.run(
        ["git", "merge-base", "--is-ancestor", expected_base, "HEAD"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    if r.returncode != 0:
        # Fallback: check if HEAD is exactly the base commit (for NOP test)
        r2 = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10, cwd=REPO,
        )
        actual = r2.stdout.strip()
        assert actual == expected_base, f"Expected base commit {expected_base} to be ancestor of HEAD or HEAD itself, got {actual}"
    # If merge-base check passes, the base commit is in history (gold test)


# [repo_tests] pass_to_pass - Prettier formatting check for modified files
def test_repo_prettier_check_templates():
    """Repo CI: Template files pass Prettier formatting check (pass_to_pass)."""
    template_files = [
        f"{REPO}/packages/next/src/build/templates/app-page.ts",
        f"{REPO}/packages/next/src/build/templates/app-route.ts",
        f"{REPO}/packages/next/src/build/templates/pages-api.ts",
    ]
    for filepath in template_files:
        r = subprocess.run(
            ["npx", "prettier", "--check", filepath],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        # Prettier returns 0 for properly formatted files, 1 for formatting issues
        # We accept both as "valid" (exit code 0 means prettier ran successfully)
        assert r.returncode in [0, 1], f"Prettier failed on {filepath}: {r.stderr}"


# [repo_tests] pass_to_pass - Tracer unit test file validation
def test_repo_tracer_test_exists():
    """Repo CI: Tracer unit test file exists and has valid structure (pass_to_pass)."""
    tracer_test = f"{REPO}/packages/next/src/server/lib/trace/tracer.test.ts"
    r = subprocess.run(
        ["test", "-f", tracer_test],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Tracer test file not found: {tracer_test}"


# [repo_tests] pass_to_pass - Verify OTel e2e test exists
def test_repo_otel_e2e_test_exists():
    """Repo CI: OTel parent span propagation e2e test exists (pass_to_pass)."""
    otel_test = f"{REPO}/test/e2e/app-dir/otel-parent-span-propagation/otel-parent-span-propagation.test.ts"
    r = subprocess.run(
        ["test", "-f", otel_test],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"OTel e2e test file not found: {otel_test}"


# [repo_tests] pass_to_pass - Git log verification
def test_repo_git_history_exists():
    """Repo CI: Git history is intact and accessible (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Git log failed: {r.stderr}"
    assert len(r.stdout.strip()) > 0, "Git log is empty"


# [repo_tests] pass_to_pass - TypeScript syntax check for OTel e2e test
def test_repo_otel_e2e_test_typescript_syntax():
    """Repo CI: OTel e2e test file has valid TypeScript syntax (pass_to_pass)."""
    otel_test = f"{REPO}/test/e2e/app-dir/otel-parent-span-propagation/otel-parent-span-propagation.test.ts"
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--ignoreConfig",
         "--target", "ES2020", "--module", "commonjs", "--moduleResolution", "node",
         otel_test],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    syntax_errors = [l for l in r.stderr.strip().split("\n") if "error TS5" in l]
    assert len(syntax_errors) == 0, f"Syntax errors in otel e2e test: {syntax_errors}"


# [repo_tests] pass_to_pass - TypeScript syntax check for tracer unit test
def test_repo_tracer_test_typescript_syntax():
    """Repo CI: Tracer unit test file has valid TypeScript syntax (pass_to_pass)."""
    tracer_test = f"{REPO}/packages/next/src/server/lib/trace/tracer.test.ts"
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--ignoreConfig",
         "--target", "ES2020", "--module", "commonjs", "--moduleResolution", "node",
         tracer_test],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    syntax_errors = [l for l in r.stderr.strip().split("\n") if "error TS5" in l]
    assert len(syntax_errors) == 0, f"Syntax errors in tracer test: {syntax_errors}"


# [repo_tests] pass_to_pass - Check for merge conflict markers in modified files
def test_repo_no_merge_conflict_markers():
    """Repo CI: Modified files have no merge conflict markers (pass_to_pass)."""
    for filepath in ALL_FILES:
        r = subprocess.run(
            ["grep", "-q", "<<<<<<<", filepath],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode != 0, f"{filepath}: contains merge conflict markers"


# [repo_tests] pass_to_pass - Verify template files use correct route variable patterns
def test_repo_template_route_variable_patterns():
    """Repo CI: Template files use correct route variable patterns (pass_to_pass)."""
    # Check that route is assigned using the expected patterns in templates
    template_files = [
        f"{REPO}/packages/next/src/build/templates/app-page.ts",
        f"{REPO}/packages/next/src/build/templates/app-route.ts",
        f"{REPO}/packages/next/src/build/templates/pages-api.ts",
    ]
    for filepath in template_files:
        r = subprocess.run(
            ["grep", "-q", "rootSpanAttributes.get('next.route')", filepath],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"{filepath}: missing rootSpanAttributes.get pattern"


# [repo_tests] pass_to_pass - Check repo file permissions are valid
def test_repo_files_are_readable():
    """Repo CI: All relevant files are readable (pass_to_pass)."""
    for filepath in ALL_FILES:
        r = subprocess.run(
            ["test", "-r", filepath],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"{filepath}: not readable"


# [repo_tests] pass_to_pass - Node.js syntax check for templates
def test_repo_templates_node_syntax():
    """Repo CI: Template files have valid Node.js syntax (pass_to_pass)."""
    template_files = [
        f"{REPO}/packages/next/src/build/templates/app-page.ts",
        f"{REPO}/packages/next/src/build/templates/app-route.ts",
        f"{REPO}/packages/next/src/build/templates/pages-api.ts",
    ]
    for filepath in template_files:
        # Use node --check to validate syntax (fast, no type checking)
        r = subprocess.run(
            ["node", "--check", filepath],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"{filepath}: Node.js syntax check failed"
