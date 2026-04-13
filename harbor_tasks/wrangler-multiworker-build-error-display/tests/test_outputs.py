"""
Task: wrangler-multiworker-build-error-display
Repo: cloudflare/workers-sdk @ d927ee342cd98932556c3671d7f2f01f30bcf954
PR:   13136

Tests verify that DevEnv.handleErrorEvent properly handles BundlerController
errors (displaying build failures instead of silently re-emitting them) and
that BundlerController no longer double-logs errors before emitErrorEvent.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/workers-sdk"
DEVENV_TS = f"{REPO}/packages/wrangler/src/api/startDevWorker/DevEnv.ts"
BUNDLER_TS = f"{REPO}/packages/wrangler/src/api/startDevWorker/BundlerController.ts"


def _run_node(script: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Write a JS analysis script to a temp file and execute via node."""
    fd, path = tempfile.mkstemp(suffix=".mjs")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(script)
        return subprocess.run(
            ["node", path],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_devenv_handles_bundler_errors():
    """DevEnv.handleErrorEvent must have a dedicated branch for BundlerController
    errors that handles them inline, rather than falling through to re-emit."""
    r = _run_node(f'''
import {{ readFileSync }} from "node:fs";

const src = readFileSync("{DEVENV_TS}", "utf8");

// Find the handleErrorEvent method body
const methodMatch = src.match(/handleErrorEvent\\s*\\(.*?\\)\\s*(?::\\s*\\w+)?\\s*{{/);
if (!methodMatch) {{
    console.error("FAIL: handleErrorEvent method not found in DevEnv.ts");
    process.exit(1);
}}
const methodStart = methodMatch.index + methodMatch[0].length;

// Extract method body (balance braces)
let depth = 1, i = methodStart;
while (depth > 0 && i < src.length) {{
    if (src[i] === "{{") depth++;
    else if (src[i] === "}}") depth--;
    i++;
}}
const body = src.slice(methodStart, i - 1);

// Must have a branch that checks for BundlerController
const hasBundlerBranch = /event\\.source\\s*===?\\s*["']BundlerController["']/.test(body);
if (!hasBundlerBranch) {{
    console.error("FAIL: no branch for BundlerController in handleErrorEvent");
    process.exit(1);
}}

// The BundlerController branch must NOT be empty — it must do something
// Extract the BundlerController branch body
const branchMatch = body.match(/event\\.source\\s*===?\\s*["']BundlerController["']\\s*\\)/);
if (branchMatch) {{
    const branchStart = body.indexOf("{{", branchMatch.index + branchMatch[0].length);
    if (branchStart >= 0) {{
        let bd = 1, bi = branchStart + 1;
        while (bd > 0 && bi < body.length) {{
            if (body[bi] === "{{") bd++;
            else if (body[bi] === "}}") bd--;
            bi++;
        }}
        const branchBody = body.slice(branchStart + 1, bi - 1).trim();
        if (branchBody.length < 10) {{
            console.error("FAIL: BundlerController branch is empty/stub");
            process.exit(1);
        }}
    }}
}}

console.log("PASS");
''')
    assert r.returncode == 0, f"BundlerController handling missing:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_devenv_formats_esbuild_failures():
    """DevEnv must import and use build failure formatting utilities
    (logBuildFailure or equivalent) to display esbuild errors from BundlerController,
    rather than just re-emitting them as unknowable errors."""
    src = Path(DEVENV_TS).read_text()

    # Must import build-failure detection utilities
    has_build_failure_import = bool(re.search(
        r'from\s+["\'].*build-failures["\']|'
        r'from\s+["\'].*deployment-bundle/build-failures["\']',
        src,
    ))
    assert has_build_failure_import, (
        "DevEnv.ts must import build failure utilities from deployment-bundle/build-failures"
    )

    # Must import logBuildFailure (or equivalent formatting function)
    has_log_import = bool(re.search(
        r'\blogBuildFailure\b|\blogBuildWarnings\b|\bformatBuildFailure\b',
        src,
    ))
    assert has_log_import, (
        "DevEnv.ts must import a build failure formatting function (logBuildFailure)"
    )

    # The formatting function must actually be called in the file body (not just imported)
    # Find it being used with arguments (not in an import statement)
    lines = src.split("\n")
    non_import_usage = any(
        re.search(r'\blogBuildFailure\s*\(|\blogBuildWarnings\s*\(|\bformatBuildFailure\s*\(', line)
        for line in lines
        if not line.strip().startswith("import")
    )
    assert non_import_usage, (
        "Build failure formatter must be called in handleErrorEvent, not just imported"
    )


# [pr_diff] fail_to_pass
def test_devenv_handles_non_esbuild_bundler_errors():
    """DevEnv must handle non-esbuild BundlerController errors gracefully
    by logging the error message, not falling through to re-emit."""
    r = _run_node(f'''
import {{ readFileSync }} from "node:fs";

const src = readFileSync("{DEVENV_TS}", "utf8");

// Find handleErrorEvent method
const methodMatch = src.match(/handleErrorEvent\\s*\\(.*?\\)\\s*(?::\\s*\\w+)?\\s*{{/);
if (!methodMatch) {{
    console.error("FAIL: handleErrorEvent not found");
    process.exit(1);
}}
const start = methodMatch.index + methodMatch[0].length;
let depth = 1, i = start;
while (depth > 0 && i < src.length) {{
    if (src[i] === "{{") depth++;
    else if (src[i] === "}}") depth--;
    i++;
}}
const body = src.slice(start, i - 1);

// Find the BundlerController branch
const bundlerIdx = body.search(/event\\.source\\s*===?\\s*["']BundlerController["']/);
if (bundlerIdx < 0) {{
    console.error("FAIL: no BundlerController branch");
    process.exit(1);
}}

// After the BundlerController check, there should be both:
// 1. A build-failure-specific path (isBuildFailure or similar)
// 2. A fallback/else path for non-esbuild errors
const afterBundler = body.slice(bundlerIdx);

const hasEsbuildPath = /isBuildFailure|BuildFailure|errors.*warnings/.test(afterBundler);
// The fallback should log the error message (logger.error, console.error, or similar)
// and NOT re-emit it
const hasFallback = /else\\s*{{[^}}]*(?:logger\\.error|console\\.error|logError|log\\()/.test(afterBundler)
    || /else\\s*{{[^}}]*event\\.cause\\.message/.test(afterBundler);

if (!hasEsbuildPath) {{
    console.error("FAIL: no esbuild-specific handling in BundlerController branch");
    process.exit(1);
}}
if (!hasFallback) {{
    console.error("FAIL: no fallback for non-esbuild BundlerController errors");
    process.exit(1);
}}

console.log("PASS");
''')
    assert r.returncode == 0, f"Non-esbuild error handling missing:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_bundler_no_duplicate_error_logging():
    """BundlerController must not call logger.error() immediately before
    emitErrorEvent(). Errors should be logged centrally by DevEnv, not
    double-logged by both BundlerController and DevEnv."""
    r = _run_node(f'''
import {{ readFileSync }} from "node:fs";

const src = readFileSync("{BUNDLER_TS}", "utf8");
const lines = src.split("\\n");

let violations = [];

for (let i = 0; i < lines.length; i++) {{
    const trimmed = lines[i].trim();
    // Check if this line calls emitErrorEvent
    if (/this\\.emitErrorEvent\\s*\\(/.test(trimmed) || /emitErrorEvent\\s*\\(/.test(trimmed)) {{
        // Look back up to 5 lines for a logger.error call in the same block
        for (let j = Math.max(0, i - 5); j < i; j++) {{
            const prev = lines[j].trim();
            if (/logger\\.error\\s*\\(/.test(prev)) {{
                violations.push(`line ${{j + 1}}: logger.error before emitErrorEvent at line ${{i + 1}}`);
            }}
        }}
    }}
}}

if (violations.length > 0) {{
    console.error("FAIL: found " + violations.length + " logger.error calls before emitErrorEvent:");
    violations.forEach(v => console.error("  " + v));
    process.exit(1);
}}

console.log("PASS: no duplicate logging found");
''')
    assert r.returncode == 0, f"Duplicate logging found:\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + structural
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_devenv_preserves_existing_error_handlers():
    """Existing error handling for MiniflareCoreError, ProxyController,
    and ConfigController/ParseError must still be present."""
    src = Path(DEVENV_TS).read_text()

    assert "MiniflareCoreError" in src, "MiniflareCoreError handling removed"
    assert "isUserError" in src, "MiniflareCoreError.isUserError() check removed"
    assert "ProxyController" in src, "ProxyController error handling removed"
    assert "ParseError" in src, "ConfigController ParseError handling removed"
    assert "ConfigController" in src, "ConfigController source check removed"


# [agent_config] pass_to_pass — AGENTS.md:186 @ d927ee342cd98932556c3671d7f2f01f30bcf954
def test_no_console_in_modified_files():
    """No console.* calls in wrangler source — must use logger singleton.
    Rule: AGENTS.md line 186 and packages/wrangler/AGENTS.md line 25."""
    for filepath in [DEVENV_TS, BUNDLER_TS]:
        src = Path(filepath).read_text()
        for i, line in enumerate(src.split("\n"), 1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
                continue
            # Skip import lines
            if stripped.startswith("import"):
                continue
            match = re.search(r'\bconsole\.(log|error|warn|info|debug)\s*\(', stripped)
            assert not match, (
                f"{Path(filepath).name}:{i} uses console.{match.group(1)}() — "
                f"must use logger singleton (AGENTS.md rule)"
            )


# [static] pass_to_pass
def test_devenv_not_stub():
    """The handleErrorEvent method must have meaningful logic (multiple branches),
    not a stub or passthrough."""
    src = Path(DEVENV_TS).read_text()

    # Find handleErrorEvent method
    match = re.search(r'handleErrorEvent\s*\(', src)
    assert match, "handleErrorEvent method not found"

    # Count the number of conditional branches (if/else if)
    method_start = match.start()
    # Get a reasonable chunk of the method
    chunk = src[method_start:method_start + 2000]
    branch_count = len(re.findall(r'\belse\s+if\b|\bif\s*\(', chunk))
    assert branch_count >= 3, (
        f"handleErrorEvent has only {branch_count} branches — "
        f"expected at least 3 (MiniflareCoreError, ProxyController, ConfigController, ...)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands
# ---------------------------------------------------------------------------


def _setup_repo():
    """Install pnpm, dependencies, and build the repo."""
    # Install pnpm if not available
    subprocess.run(["npm", "install", "-g", "pnpm"], check=True, capture_output=True)
    # Install dependencies
    subprocess.run(["pnpm", "install", "--frozen-lockfile"], cwd=REPO, check=True, capture_output=True, timeout=300)
    # Build the workspace
    subprocess.run(["pnpm", "run", "build"], cwd=REPO, check=True, capture_output=True, timeout=600)


# [repo_tests] pass_to_pass
def test_repo_lint_modified_files():
    """Repo's linter (oxlint) passes on modified files (pass_to_pass)."""
    _setup_repo()
    r = subprocess.run(
        ["npx", "oxlint", "--deny-warnings", "--type-aware",
         f"{REPO}/packages/wrangler/src/api/startDevWorker/DevEnv.ts",
         f"{REPO}/packages/wrangler/src/api/startDevWorker/BundlerController.ts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck_wrangler():
    """Wrangler package TypeScript typecheck passes (pass_to_pass)."""
    _setup_repo()
    r = subprocess.run(
        ["pnpm", "--filter", "wrangler", "run", "check:type"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_format_modified_files():
    """Repo's formatter (oxfmt) check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxfmt", "--check",
         f"{REPO}/packages/wrangler/src/api/startDevWorker/DevEnv.ts",
         f"{REPO}/packages/wrangler/src/api/startDevWorker/BundlerController.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests_bundler_controller():
    """BundleController unit tests pass (pass_to_pass). Tests the bundler logic
    that was modified to remove duplicate error logging."""
    _setup_repo()
    r = subprocess.run(
        ["pnpm", "vitest", "run",
         "src/__tests__/api/startDevWorker/BundleController.test.ts",
         "--reporter=verbose"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/wrangler",
    )
    assert r.returncode == 0, f"BundleController tests failed:\n{r.stderr[-500:]}"
