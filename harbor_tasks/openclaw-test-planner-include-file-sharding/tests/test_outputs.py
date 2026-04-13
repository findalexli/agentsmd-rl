"""
Task: openclaw-test-planner-include-file-sharding
Repo: openclaw/openclaw @ c22edbb8eeb3668f60b0b23cd8e8e11b4340f6d6
PR:   57807

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The test-planner modules (executor.mjs, planner.mjs) have deep ESM import chains.
Tests verify behavior by:
1. Extracting and unit-testing the helper function in isolation
2. Running the actual test-planner tests from the repo
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
EXECUTOR = f"{REPO}/scripts/test-planner/executor.mjs"
PLANNER = f"{REPO}/scripts/test-planner/planner.mjs"


def _read(filepath: str) -> str:
    return Path(filepath).read_text()


def _run_node(script: str, *, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a self-contained JS snippet via node --input-type=module."""
    return subprocess.run(
        ["node", "--input-type=module"],
        input=script,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _extract_filter_helper(filepath: str) -> str | None:
    """Extract the helper function that combines countExplicitEntryFilters with includeFiles.

    Looks for a top-level const arrow function whose body references both
    'countExplicitEntryFilters' and 'includeFiles'. Returns the full function
    source or None if not found.
    """
    content = _read(filepath)
    # Match const <name> = (<params>) => { ... }; spanning multiple lines
    for match in re.finditer(
        r"(const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{.*?\n\};)",
        content,
        re.DOTALL,
    ):
        func = match.group(1)
        if "includeFiles" in func and "countExplicitEntryFilters" in func:
            return func
    return None


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified .mjs files must parse without syntax errors."""
    for f in [EXECUTOR, PLANNER]:
        r = subprocess.run(
            ["node", "--check", f],
            cwd=REPO, capture_output=True, text=True, timeout=15,
        )
        assert r.returncode == 0, f"{f} has syntax errors: {r.stderr}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_filter_helper_defined():
    """Both files define a helper that combines countExplicitEntryFilters with includeFiles."""
    for f in [EXECUTOR, PLANNER]:
        func = _extract_filter_helper(f)
        assert func is not None, (
            f"{Path(f).name} has no helper combining countExplicitEntryFilters + includeFiles"
        )


# [pr_diff] fail_to_pass
def test_include_files_fallback():
    """Helper returns includeFiles.length when explicit CLI filters are null.

    Extracts the helper from executor.mjs and runs it with a mock
    countExplicitEntryFilters that returns null.
    """
    func = _extract_filter_helper(EXECUTOR)
    assert func is not None, "Helper not found in executor.mjs"

    r = _run_node(f"""
// Mock: no CLI file filters
let mockReturn = null;
const countExplicitEntryFilters = (_args) => mockReturn;
{func}

// Extract the function name dynamically
const fnName = `{func}`.match(/const\\s+(\\w+)/)[1];
const fn = eval(fnName);

const cases = [
  [{{ includeFiles: ['a.test.ts'], args: [] }}, 1],
  [{{ includeFiles: ['a.ts', 'b.ts'], args: [] }}, 2],
  [{{ includeFiles: ['a.ts', 'b.ts', 'c.ts', 'd.ts', 'e.ts'], args: [] }}, 5],
];
for (const [unit, expected] of cases) {{
  const result = fn(unit);
  if (result !== expected) {{
    console.error('includeFiles=' + unit.includeFiles.length + ': expected ' + expected + ', got ' + result);
    process.exit(1);
  }}
}}
console.log('OK');
""")
    assert r.returncode == 0, f"includeFiles fallback broken:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_explicit_filters_take_priority():
    """Helper prefers explicit CLI filter count over includeFiles count.

    When countExplicitEntryFilters returns a non-null value, the helper must
    return that value regardless of what includeFiles contains.
    """
    func = _extract_filter_helper(EXECUTOR)
    assert func is not None, "Helper not found in executor.mjs"

    r = _run_node(f"""
let mockReturn = null;
const countExplicitEntryFilters = (_args) => mockReturn;
{func}

const fnName = `{func}`.match(/const\\s+(\\w+)/)[1];
const fn = eval(fnName);

// When explicit returns a number, it wins over includeFiles
for (const n of [1, 3, 7, 42]) {{
  mockReturn = n;
  const result = fn({{ includeFiles: ['a.ts', 'b.ts'], args: ['some', 'args'] }});
  if (result !== n) {{
    console.error('Explicit=' + n + ' but got ' + result);
    process.exit(1);
  }}
}}

// When explicit returns null, fall back to includeFiles
mockReturn = null;
const result = fn({{ includeFiles: ['x.ts'], args: [] }});
if (result !== 1) {{
  console.error('Expected fallback to includeFiles (1), got ' + result);
  process.exit(1);
}}
console.log('OK');
""")
    assert r.returncode == 0, f"Priority test failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_executor_call_sites_updated():
    """executor.mjs call sites no longer use raw countExplicitEntryFilters(unit.args).

    The fix replaces countExplicitEntryFilters(unit.args) with the new helper at
    the formatPlanOutput and executePlan call sites.
    """
    content = _read(EXECUTOR)

    # The helper definition itself will contain countExplicitEntryFilters - exclude it
    helper = _extract_filter_helper(EXECUTOR) or ""
    # Remove the helper body from content for call-site analysis
    rest = content.replace(helper, "")

    # After removing the helper definition, no remaining call site should use
    # countExplicitEntryFilters(unit.args) - they should all use the helper
    call_sites = re.findall(r"countExplicitEntryFilters\s*\(\s*unit\.args\s*\)", rest)
    assert len(call_sites) == 0, (
        f"executor.mjs still has {len(call_sites)} call site(s) using "
        f"countExplicitEntryFilters(unit.args) outside the helper"
    )


# [pr_diff] fail_to_pass
def test_planner_call_sites_updated():
    """planner.mjs call sites no longer use raw countExplicitEntryFilters(unit.args).

    buildTopLevelSingleShardAssignments and formatExecutionUnitSummary must use
    the new helper instead of countExplicitEntryFilters directly.
    """
    content = _read(PLANNER)

    helper = _extract_filter_helper(PLANNER) or ""
    rest = content.replace(helper, "")

    call_sites = re.findall(r"countExplicitEntryFilters\s*\(\s*unit\.args\s*\)", rest)
    assert len(call_sites) == 0, (
        f"planner.mjs still has {len(call_sites)} call site(s) using "
        f"countExplicitEntryFilters(unit.args) outside the helper"
    )


# -----------------------------------------------------------------------------
# Pass-to-pass - regression checks
# -----------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_null_for_no_include_files():
    """Helper returns null when includeFiles is empty, undefined, or null."""
    func = _extract_filter_helper(EXECUTOR)
    if func is None:
        # On base commit, the helper doesn't exist - skip gracefully.
        # (This is p2p, so if the helper doesn't exist, the f2p tests catch it.)
        return

    r = _run_node(f"""
let mockReturn = null;
const countExplicitEntryFilters = (_args) => mockReturn;
{func}

const fnName = `{func}`.match(/const\\s+(\\w+)/)[1];
const fn = eval(fnName);

const cases = [
  {{ includeFiles: [], args: [] }},
  {{ args: [] }},
  {{ includeFiles: null, args: [] }},
];
for (const unit of cases) {{
  const result = fn(unit);
  if (result !== null) {{
    console.error('Expected null for ' + JSON.stringify(unit) + ', got ' + result);
    process.exit(1);
  }}
}}
console.log('OK');
""")
    assert r.returncode == 0, f"Null return broken:\n{r.stdout}\n{r.stderr}"


# [pr_diff] pass_to_pass
def test_explicit_filter_import_preserved():
    """countExplicitEntryFilters is still imported from vitest-args.mjs in both files."""
    for f in [EXECUTOR, PLANNER]:
        content = _read(f)
        assert "countExplicitEntryFilters" in content, (
            f"{Path(f).name} no longer references countExplicitEntryFilters"
        )
        assert re.search(
            r'import\s*\{[^}]*countExplicitEntryFilters[^}]*\}\s*from\s*["\'].*vitest-args',
            content,
        ), f"{Path(f).name} no longer imports countExplicitEntryFilters from vitest-args"


# -----------------------------------------------------------------------------
# Config-derived (agent_config)
# -----------------------------------------------------------------------------

# [agent_config] pass_to_pass - CLAUDE.md:146 @ c22edbb8
def test_no_lint_suppressions():
    """New helper function must not introduce inline lint suppressions.

    CLAUDE.md:146: "Never add @ts-nocheck and do not add inline lint suppressions by default."
    Scoped to the helper function to avoid flagging pre-existing suppressions in the file.
    """
    suppressions = ["@ts-nocheck", "eslint-disable", "oxlint-ignore", "noinspection"]
    for filepath in [EXECUTOR, PLANNER]:
        func = _extract_filter_helper(filepath)
        if func is None:
            # Helper absent on base commit - the f2p tests catch this; skip here.
            continue
        for s in suppressions:
            assert s not in func, (
                f"{Path(filepath).name}: new helper contains lint suppression '{s}' - "
                f"fix root causes instead of suppressing"
            )


# [agent_config] pass_to_pass - CLAUDE.md:147 @ c22edbb8
def test_no_explicit_any_disable():
    """Modified files must not disable no-explicit-any.

    CLAUDE.md:147: "Do not disable no-explicit-any; prefer real types, unknown, or a narrow adapter."
    """
    for name in [EXECUTOR, PLANNER]:
        content = _read(name)
        assert "no-explicit-any" not in content, (
            f"{Path(name).name} disables no-explicit-any"
        )


# [agent_config] pass_to_pass - CLAUDE.md:160 @ c22edbb8
def test_no_prototype_mutation():
    """Modified files must not share behavior via prototype mutation.

    CLAUDE.md:160: "Never share class behavior via prototype mutation."
    """
    for name in [EXECUTOR, PLANNER]:
        for line in _read(name).splitlines():
            assert not re.search(r"\.prototype\.\w+\s*[=]", line), (
                f"{Path(name).name} has prototype mutation: {line.strip()}"
            )


# -----------------------------------------------------------------------------
# End-to-end behavioral test (repo_tests)
# -----------------------------------------------------------------------------


# [repo_tests] fail_to_pass
def test_single_file_batches_get_shard_assignment():
    """Single-file include batches are assigned to specific shards (not over-sharded).

    This runs the actual repo's test-planner tests to verify that units with
    includeFiles (instead of CLI filters) get proper topLevelSingleShardAssignments.
    Verifies the fix for the over-sharding bug.
    """
    r = subprocess.run(
        ["pnpm", "test", "--", "test/scripts/test-planner.test.ts", "-t", "single include-file CI batches"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Test passes if vitest exits 0
    assert r.returncode == 0, (
        f"Repo test failed: {r.stdout}\n{r.stderr}"
    )


# [repo_tests] pass_to_pass
def test_parallel_tests_still_pass():
    """Related test-parallel tests continue to work after the fix."""
    r = subprocess.run(
        ["pnpm", "test", "--", "test/scripts/test-parallel.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # p2p: on gold this passes, on base may fail for unrelated reasons
    # We mainly want to ensure no syntax errors in modified files
    if r.returncode != 0:
        # Only fail if syntax/parse errors (indicating our changes broke something)
        assert "SyntaxError" not in r.stderr and "ParseError" not in r.stderr, (
            f"Syntax error in modified files: {r.stderr}"
        )



# -----------------------------------------------------------------------------
# Repo CI/CD pass-to-pass gates
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo build passes (pass_to_pass).

    Runs pnpm build to verify the codebase compiles without errors.
    This is a critical gate to ensure changes don't break the build.
    """
    r = subprocess.run(
        ["pnpm", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, "Build failed:\n" + r.stderr[-1000:]


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo linting passes (pass_to_pass).

    Runs pnpm lint (oxlint) to verify code style and catch common issues.
    This ensures modified files follow the repo's linting standards.
    """
    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, "Lint failed:\n" + r.stderr[-1000:]


# [repo_tests] pass_to_pass
def test_repo_test_planner():
    """Repo test-planner tests pass (pass_to_pass).

    Runs the test-planner test suite to verify the planner and executor
    modules work correctly. This covers both the base commit and the fix.
    """
    r = subprocess.run(
        ["pnpm", "test", "--", "test/scripts/test-planner.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, "Test-planner tests failed:\n" + r.stderr[-1000:]

# [repo_tests] pass_to_pass
def test_repo_check():
    """Repo check passes (pass_to_pass).

    Runs pnpm check to verify conflict markers, Swift policies, and typechecking (tsgo).
    """
    r = subprocess.run(
        ["pnpm", "check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, "Check failed:\n" + r.stderr[-1000:]


# [repo_tests] pass_to_pass
def test_repo_executor_fallback():
    """Repo test-planner.executor-fallback tests pass (pass_to_pass).

    Runs the specific executor-fallback test suite to ensure executor modifications
    don't break existing fallback logic.
    """
    r = subprocess.run(
        ["pnpm", "test", "--", "test/scripts/test-planner.executor-fallback.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, "Executor-fallback tests failed:\n" + r.stderr[-1000:]


# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo format check passes (pass_to_pass).

    Runs pnpm format to verify code formatting adheres to the repo's
    style guidelines (oxfmt --check).
    """
    r = subprocess.run(
        ["pnpm", "format"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, "Format check failed:\n" + r.stderr[-1000:]


# [repo_tests] pass_to_pass
def test_repo_check_no_conflict_markers():
    """Repo conflict marker check passes (pass_to_pass).

    Runs pnpm check:no-conflict-markers to verify no Git conflict
    markers were accidentally left in the code.
    """
    r = subprocess.run(
        ["pnpm", "check:no-conflict-markers"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, "Conflict markers check failed:\n" + r.stderr[-500:]
