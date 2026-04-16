"""
Task: wrangler-multiworker-build-error-display
Repo: cloudflare/workers-sdk @ d927ee342cd98932556c3671d7f2f01f30bcf954

Behavioral tests verify that DevEnv.handleErrorEvent properly handles BundlerController
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
    """DevEnv.handleErrorEvent must handle BundlerController errors inline
    (not re-emit them). We verify by checking source structure."""
    r = _run_node(f'''
import {{ readFileSync }} from "node:fs";

const src = readFileSync("{DEVENV_TS}", "utf8");

const hasBundlerCheck = /event\\.source.*BundlerController/.test(src);
if (!hasBundlerCheck) {{
    console.error("FAIL: no BundlerController error handling in handleErrorEvent");
    process.exit(1);
}}

const bundlerSection = src.match(/BundlerController[\\s\\S]{{0,800}}/);
if (!bundlerSection) {{
    console.error("FAIL: cannot find BundlerController handling section");
    process.exit(1);
}}

const section = bundlerSection[0];
const hasErrorHandling = /logger\\.(error|log)|logBuildFailure|isBuildFailure/.test(section);
if (!hasErrorHandling) {{
    console.error("FAIL: BundlerController branch lacks error handling logic");
    process.exit(1);
}}

console.log("PASS");
''')
    assert r.returncode == 0, f"BundlerController handling missing:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_devenv_formats_esbuild_failures():
    """DevEnv must format esbuild BuildFailure errors using the build-failures module."""
    r = _run_node(f'''
import {{ readFileSync }} from "node:fs";

const src = readFileSync("{DEVENV_TS}", "utf8");

const hasBuildFailuresImport = /from\\s+["\'].*build-failures["\']/.test(src);
if (!hasBuildFailuresImport) {{
    console.error("FAIL: missing import from build-failures module");
    process.exit(1);
}}

const hasTypeGuard = /isBuildFailure/.test(src);
if (!hasTypeGuard) {{
    console.error("FAIL: missing isBuildFailure type guard usage");
    process.exit(1);
}}

const hasFormatterCall = /logBuildFailure\\s*\\(/.test(src);
if (!hasFormatterCall) {{
    console.error("FAIL: missing logBuildFailure() call for formatting");
    process.exit(1);
}}

console.log("PASS");
''')
    assert r.returncode == 0, f"Build failure formatting missing:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_devenv_handles_non_esbuild_bundler_errors():
    """DevEnv must handle non-esbuild BundlerController errors by logging them."""
    r = _run_node(f'''
import {{ readFileSync }} from "node:fs";

const src = readFileSync("{DEVENV_TS}", "utf8");

const bundlerMatch = src.match(/event\\.source.*BundlerController[\\s\\S]{{0,1000}}/);
if (!bundlerMatch) {{
    console.error("FAIL: no BundlerController handling found");
    process.exit(1);
}}

const section = bundlerMatch[0];

const hasEsbuildPath = /isBuildFailure/.test(section);
if (!hasEsbuildPath) {{
    console.error("FAIL: no isBuildFailure check for esbuild errors");
    process.exit(1);
}}

const hasElseBranch = /else\\s*{{/.test(section);
const hasFallbackLogging = /else[\\s\\S]{{0,300}}logger\\.error/.test(section);

if (!hasElseBranch) {{
    console.error("FAIL: no else branch for non-esbuild errors");
    process.exit(1);
}}

if (!hasFallbackLogging) {{
    console.error("FAIL: no logger.error in non-esbuild error fallback");
    process.exit(1);
}}

console.log("PASS");
''')
    assert r.returncode == 0, f"Non-esbuild error handling missing:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_bundler_no_duplicate_error_logging():
    """BundlerController must not call logger.error() before emitErrorEvent()."""
    r = _run_node(f'''
import {{ readFileSync }} from "node:fs";

const src = readFileSync("{BUNDLER_TS}", "utf8");
const lines = src.split("\\n");

let violations = [];

for (let i = 0; i < lines.length; i++) {{
    const trimmed = lines[i].trim();
    if (/emitErrorEvent\\s*\\(/.test(trimmed)) {{
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


# [agent_config] pass_to_pass
def test_no_console_in_modified_files():
    """No console.* calls in wrangler source — must use logger singleton."""
    for filepath in [DEVENV_TS, BUNDLER_TS]:
        src = Path(filepath).read_text()
        for i, line in enumerate(src.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
                continue
            if stripped.startswith("import"):
                continue
            match = re.search(r'\bconsole\.(log|error|warn|info|debug)\s*\(', stripped)
            assert not match, (
                f"{Path(filepath).name}:{i} uses console.{match.group(1)}() — "
                f"must use logger singleton (AGENTS.md rule)"
            )


# [static] pass_to_pass
def test_devenv_not_stub():
    """The handleErrorEvent method must have meaningful logic (multiple branches)."""
    src = Path(DEVENV_TS).read_text()

    match = re.search(r'handleErrorEvent\s*\(', src)
    assert match, "handleErrorEvent method not found"

    method_start = match.start()
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
    subprocess.run(["npm", "install", "-g", "pnpm"], check=True, capture_output=True)
    subprocess.run(["pnpm", "install", "--frozen-lockfile"], cwd=REPO, check=True, capture_output=True, timeout=300)
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
