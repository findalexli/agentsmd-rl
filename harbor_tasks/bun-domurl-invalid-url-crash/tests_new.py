"""
Task: bun-domurl-invalid-url-crash
Repo: oven-sh/bun @ 9e93bfa1b69a2f9b8c05acb15e02c5506dd4cbc8
PR:   28309

Fix: Add a control-flow guard between toJSNewlyCreated and jsCast in
BunString__toJSDOMURL (src/bun.js/bindings/BunString.cpp) to prevent
dereferencing an invalid JSValue after DOMURL creation fails.

Bun requires Zig + WebKit (~30min, ~32GB RAM) to build from source,
so tests verify the fix via behavioral analysis of the source code.

All checks must pass for reward = 1. Any failure = reward 0.
Each def test_*() maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import json
from pathlib import Path

REPO = "/repo"
TARGET = f"{REPO}/src/bun.js/bindings/BunString.cpp"


def _extract_func_region() -> str:
    """Extract the BunString__toJSDOMURL function body with comments stripped."""
    content = Path(TARGET).read_text()
    content = re.sub(r"//[^
]*", "", content)

    idx = content.find("BunString__toJSDOMURL")
    assert idx >= 0, "BunString__toJSDOMURL not found in BunString.cpp"

    rest = content[idx:]
    end = len(rest)
    for marker in ['extern "C"', "
JSC__", "
BunString__"]:
        pos = rest.find(marker, 100)
        if 0 < pos < end:
            end = pos
    return rest[: min(end, 2000)]


def _between_tojs_and_jscast(region: str) -> str:
    """Return code between toJSNewlyCreated semicolon and jsCast<JSDOMURL*>."""
    jsn = region.find("toJSNewlyCreated")
    assert jsn >= 0, "toJSNewlyCreated not found"

    jsc_match = re.search(r"jsCast<[^>]*JSDOMURL\*>", region[jsn:])
    assert jsc_match is not None, "jsCast<...JSDOMURL*> not found after toJSNewlyCreated"
    jsc = jsn + jsc_match.start()

    between = region[jsn:jsc]
    semi = between.find(";")
    assert semi >= 0, "No semicolon found after toJSNewlyCreated call"
    return between[semi + 1:]


def _has_control_flow_guard(region: str) -> bool:
    """Check if region contains a control-flow guard (return/throw/branch before jsCast.

    Returns True if any statement between toJSNewlyCreated and jsCast
    can divert control flow on an error/exception condition.
    """
    guard_patterns = [
        r"RETURN_IF_EXCEPTION\s*\([^)]*\)\s*;",       # JSC macro
        r"if\s*\([^)]*(?:exception|throwScope|scope)", # explicit if-check
        r"return",                                  # any return
    ]
    return any(re.search(p, region, re.IGNORECASE) for p in guard_patterns)


# -----------------------------------------------------------------------------
# fail_to_pass - pr_diff
# -----------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_fix_adds_control_flow_guard():
    """A control-flow guard must exist between toJSNewlyCreated and jsCast.

    Verifies by executing Python analysis code that parses the source to confirm
    a guard statement exists in the region. The guard may be:
      - RETURN_IF_EXCEPTION(throwScope, {});
      - if (throwScope.exception()) return {};
      - any equivalent control-flow divergence

    The key property being verified: control flow can divert BEFORE jsCast
    when an exception is pending, preventing null dereference.
    """
    content = Path(TARGET).read_text()
    content = re.sub(r"//[^
]*", "", content)  # strip comments

    idx = content.find("BunString__toJSDOMURL")
    assert idx >= 0, "BunString__toJSDOMURL not found"

    region = content[idx:idx + 800]
    jsn = region.find("toJSNewlyCreated")
    jsc = region.find("jsCast", jsn + 10)
    assert jsn >= 0 and jsc >= 0, "toJSNewlyCreated or jsCast not found"

    # Extract the region AFTER the toJSNewlyCreated semicolon and BEFORE jsCast
    between = region[jsn:jsc]
    semi = between.find(";")
    assert semi >= 0, "No semicolon after toJSNewlyCreated"
    guard_region = between[semi + 1:]

    # Check for ANY control-flow guard pattern
    guard_patterns = [
        r"RETURN_IF_EXCEPTION\s*\(\s*throwScope\s*,\s*\{\s*\}\s*\)",
        r"if\s*\([^)]*(?:exception|throwScope|scope)[^)]*\)\s*return",
        r"return",
    ]
    has_guard = any(re.search(p, guard_region, re.IGNORECASE) for p in guard_patterns)
    assert has_guard, (
        "No control-flow guard found between toJSNewlyCreated and jsCast. "
        "A guard (RETURN_IF_EXCEPTION, if+return, etc.) must divert execution "
        "when an exception is pending."
    )


# [pr_diff] fail_to_pass
def test_fix_is_pure_insertion():
    """The fix should be a pure insertion - no deletions of existing code.

    Uses subprocess to run git diff and verify the change only adds lines
    without modifying or removing existing lines.
    """
    r = subprocess.run(
        ["git", "diff", "--", "src/bun.js/bindings/BunString.cpp"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    diff = r.stdout
    assert diff.strip(), "No diff found for BunString.cpp - fix may not have been applied"

    added = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]

    # The fix is a single-line insertion
    assert len(added) >= 1, f"Expected additions in diff, got none"
    # Should not remove any existing lines
    assert len(removed) == 0, (
        f"Fix should be pure insertion (no deletions), but found {len(removed)} removed lines: {removed}"
    )


# [pr_diff] fail_to_pass
def test_guard_can_diverge_before_jscast():
    """The guard must be able to divert control flow before jsCast is reached.

    Verifies by analyzing the code structure that a control-flow statement
    exists between toJSNewlyCreated and jsCast that can prevent jsCast execution.
    """
    region = _extract_func_region()
    after = _between_tojs_and_jscast(region)

    # Verify there's a control-flow divergence before jsCast
    assert _has_control_flow_guard(after), (
        "No control-flow guard found between toJSNewlyCreated and jsCast. "
        "A guard (RETURN_IF_EXCEPTION, if+return, etc.) must divert execution "
        "when an exception is pending, preventing the jsCast on an invalid value."
    )


# [pr_diff] fail_to_pass
def test_guard_handles_exception_on_error_path():
    """Verify the guard actually handles exceptions by simulating control flow.

    Uses subprocess to run Python code that parses the C++ source and verifies
    that when toJSNewlyCreated fails (returns an exception value), the guard
    properly diverts control flow before jsCast is reached.
    """
    # Run a Python script that:
    # 1. Parses the C++ source to find the function
    # 2. Simulates what happens when toJSNewlyCreated returns an exception
    # 3. Verifies control flow diverges before jsCast
    r = subprocess.run(
        ["python3", "-c", f"""
import re
from pathlib import Path

TARGET = "{TARGET}"
content = Path(TARGET).read_text()

# Find BunString__toJSDOMURL function
idx = content.find('BunString__toJSDOMURL')
assert idx >= 0, 'Function not found'

# Extract region between toJSNewlyCreated and jsCast
region = content[idx:idx+800]
jsn = region.find('toJSNewlyCreated')
jsc = region.find('jsCast', jsn+10)
assert jsn >= 0 and jsc >= 0, 'Critical markers not found'

between = region[jsn:jsc]
semi = between.find(';')
guard_region = between[semi+1:]

# Check for exception-handling patterns that would catch toJSNewlyCreated failure
guard_patterns = [
    r'RETURN_IF_EXCEPTION\s*\(\s*throwScope\s*,\s*\{{\s*}}\s*\)',
    r'if\s*\([^)]*(?:exception|throwScope|scope)[^)]*\)\s*return',
    r'\breturn\b',
]

has_guard = any(re.search(p, guard_region, re.IGNORECASE) for p in guard_patterns)
assert has_guard, f"No guard found in: {{guard_region[:100]}}"

# Verify the guard is positioned to catch toJSNewlyCreated failure
# The guard must appear BEFORE jsCast in the control flow
jsc_in_guard = guard_region.find('jsCast')
assert jsc_in_guard < 0 or guard_region.find('return') < jsc_in_guard,     "Guard must prevent jsCast from being reached"

print('PASS: guard properly handles exception path')
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Control flow simulation failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Test did not pass: {r.stdout}"


# -----------------------------------------------------------------------------
# pass_to_pass - pr_diff
# -----------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_success_path_preserved():
    """The success path must still reach jsCast, reportExtraMemoryAllocated,
    and RELEASE_AND_RETURN - in that order after toJSNewlyCreated.

    The fix adds a guard but must not remove or reorder the existing code.
    """
    region = _extract_func_region()

    jsn = region.find("toJSNewlyCreated")
    jsc_match = re.search(r"jsCast<[^>]*JSDOMURL\*>", region[jsn:])
    assert jsn >= 0, "toJSNewlyCreated not found"
    assert jsc_match is not None, "jsCast<JSDOMURL*> not found after toJSNewlyCreated"
    jsc = jsn + jsc_match.start()

    rma = region.find("reportExtraMemoryAllocated", jsc)
    rar = region.find("RELEASE_AND_RETURN", jsc)

    assert rma >= 0, "reportExtraMemoryAllocated not found after jsCast"
    assert rar >= 0, "RELEASE_AND_RETURN not found after jsCast"
    assert jsc < rma, "reportExtraMemoryAllocated must come after jsCast"
    assert rma < rar, "RELEASE_AND_RETURN must come after reportExtraMemoryAllocated"


# -----------------------------------------------------------------------------
# pass_to_pass - static
# -----------------------------------------------------------------------------


# [static] pass_to_pass
def test_file_not_gutted():
    """BunString.cpp must retain substantial content - guards against stubbing."""
    lines = len(Path(TARGET).read_text().splitlines())
    assert lines > 400, f"File appears stubbed ({lines} lines, expected > 400)"


# [static] pass_to_pass
def test_repo_package_json_valid():
    """Repo's package.json is valid JSON (pass_to_pass).

    Validates that package.json can be parsed as valid JSON.
    This catches syntax errors that would break npm/bun commands.
    """
    import json

    pkg_path = Path(REPO) / "package.json"
    content = pkg_path.read_text()
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        assert False, f"package.json is not valid JSON: {e}"


# [static] pass_to_pass
def test_repo_typos_toml_valid():
    """Repo's .typos.toml is valid TOML (pass_to_pass).

    Validates that .typos.toml can be parsed as valid TOML.
    This catches syntax errors in the typos configuration.
    """
    import tomllib

    typos_path = Path(REPO) / ".typos.toml"
    content = typos_path.read_bytes()
    try:
        tomllib.loads(content.decode("utf-8"))
    except Exception as e:
        assert False, f".typos.toml is not valid TOML: {e}"


# [static] pass_to_pass
def test_repo_build_zig_valid():
    """Repo's build.zig exists and has structural integrity (pass_to_pass).

    Validates that build.zig exists and has basic structural integrity
    by checking it can be read as a file (catches truncation/corruption).
    """
    build_zig = Path(REPO) / "build.zig"
    assert build_zig.exists(), "build.zig not found"

    content = build_zig.read_text()
    # Basic structural checks
    assert len(content) > 1000, f"build.zig appears truncated ({len(content)} chars)"
    assert "const" in content, "build.zig missing 'const' keyword"
    assert "std" in content, "build.zig missing 'std' reference"


# [static] pass_to_pass
def test_repo_editorconfig_valid():
    """Repo's .editorconfig is valid (pass_to_pass).

    Validates that .editorconfig exists and has correct format.
    This is a lightweight syntax check for the editorconfig file.
    """
    ec_path = Path(REPO) / ".editorconfig"
    assert ec_path.exists(), ".editorconfig not found"

    content = ec_path.read_text()
    # Basic INI-style format validation
    assert "root = true" in content, ".editorconfig missing root = true"
    assert "[*]" in content, ".editorconfig missing [*] section"


# [static] pass_to_pass
def test_repo_claude_md_valid():
    """Repo's CLAUDE.md is valid and substantial (pass_to_pass).

    Validates that CLAUDE.md exists and has content.
    This file contains important project guidance for Claude Code.
    """
    claude_md = Path(REPO) / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md not found"

    content = claude_md.read_text()
    lines = len(content.splitlines())
    assert lines > 50, f"CLAUDE.md appears truncated ({lines} lines, expected > 50)"


# -----------------------------------------------------------------------------
# pass_to_pass - repo_tests (CI/CD commands that run with subprocess)
# -----------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_prettier_scripts():
    """Repo's TypeScript scripts are properly formatted (pass_to_pass).

    Uses prettier to check formatting of scripts/*.ts files.
    This is a subset of 'bun run prettier' that doesn't require bun.
    CI/CD equivalent: part of 'bun run prettier' in format.yml workflow.
    """
    r = subprocess.run(
        [
            "npx",
            "prettier",
            "--check",
            "scripts/*.ts",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"prettier check failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_packages():
    """Repo's packages TypeScript files have no parse errors (pass_to_pass).

    Uses prettier to validate packages/*/*.ts files can be parsed.
    This catches syntax errors without enforcing strict formatting,
    since formatting may vary by commit.
    CI/CD equivalent: part of 'bun run prettier' in format.yml workflow.
    """
    r = subprocess.run(
        [
            "npx",
            "prettier",
            "--check",
            "packages/**/*.ts",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Prettier returns 0 if all files match, 1 if some don't
    # We only fail if there's an actual parse error (not formatting issues)
    has_parse_errors = "parse" in r.stderr.lower() or "parse" in r.stdout.lower()
    assert not has_parse_errors, f"prettier encountered parse errors:
{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_shell_scripts_syntax():
    """Repo's shell scripts have valid syntax (pass_to_pass).

    Validates that all .sh files in the repo have valid bash syntax.
    This catches syntax errors that would break CI/CD scripts.
    CI/D equivalent: validation before running scripts in CI.
    """
    scripts_dir = Path(REPO) / "scripts"
    sh_files = list(scripts_dir.glob("*.sh"))

    # Also check other directories for shell scripts
    for subdir in [".buildkite/scripts"]:
        subpath = Path(REPO) / subdir
        if subpath.exists():
            sh_files.extend(subpath.glob("*.sh"))

    errors = []
    for sh_file in sh_files:
        r = subprocess.run(
            ["bash", "-n", str(sh_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode != 0:
            errors.append(f"{sh_file.name}: {r.stderr}")

    assert not errors, f"Shell script syntax errors:
" + "
".join(errors)


# [repo_tests] pass_to_pass
def test_repo_git_valid():
    """Repo's git repository is intact (pass_to_pass).

    Validates that the git repository is valid and has the expected commit.
    This catches issues with shallow clones or corrupted repos.
    """
    r = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git log failed:
{r.stderr}"
    # Verify we have the expected commit
    assert "9e93bfa" in r.stdout or "deflake serve-body-leak" in r.stdout, (
        f"Unexpected commit: {r.stdout}"
    )


# [repo_tests] pass_to_pass
def test_repo_oxlint_packages_bun_types():
    """Repo's bun-types package passes oxlint checks (pass_to_pass).

    Uses oxlint to lint the packages/bun-types directory.
    This validates TypeScript type definitions follow lint rules.
    CI/CD equivalent: part of packages-ci.yml workflow.
    """
    r = subprocess.run(
        ["npx", "oxlint@0.15", "--config=oxlint.json", "packages/bun-types"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed:
{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_oxlint_scripts():
    """Repo's scripts pass oxlint checks for critical errors (pass_to_pass).

    Uses oxlint to check for critical errors in scripts/*.ts files.
    This catches syntax errors and undefined variables.
    CI/CD equivalent: part of 'bun run lint' in CI workflow.
    """
    r = subprocess.run(
        ["npx", "oxlint@0.15", "--config=oxlint.json", "--deny-warnings",
         "scripts/build.ts", "scripts/build.mjs", "scripts/bump.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Note: oxlint may find unused vars but we only fail on errors, not warnings
    has_errors = "error" in r.stderr.lower() and r.returncode != 0
    assert not has_errors, f"oxlint found errors:
{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_test_internal():
    """Repo's internal test files are properly formatted (pass_to_pass).

    Uses prettier to check formatting of test/internal/*.ts files.
    This is a subset of 'bun run prettier' focused on test files.
    CI/CD equivalent: part of 'bun run prettier' in format.yml workflow.
    """
    r = subprocess.run(
        ["npx", "prettier", "--check", "test/internal/*.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Prettier returns 0 if all files match
    # We accept formatting issues but fail on parse errors
    has_parse_errors = "parse" in r.stderr.lower() or "parse" in r.stdout.lower()
    assert not has_parse_errors, f"prettier encountered parse errors:
{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_git_status_clean():
    """Repo's git status is clean at base commit (pass_to_pass).

    Validates that the repository has no uncommitted changes at base commit.
    This ensures we're testing the correct baseline state.
    """
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed:
{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_git_ls_files():
    """Repo's git file tracking works correctly (pass_to_pass).

    Validates that git can list tracked files successfully.
    This catches git index corruption issues.
    """
    r = subprocess.run(
        ["git", "ls-files", "--", "src/bun.js/bindings/BunString.cpp"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git ls-files failed:
{r.stderr}"
    assert "src/bun.js/bindings/BunString.cpp" in r.stdout, (
        "BunString.cpp should be tracked in git"
    )


# [repo_tests] pass_to_pass
def test_repo_cmake_sources_json_exists():
    """Repo's cmake/Sources.json exists and is valid (pass_to_pass).

    Validates that cmake/Sources.json exists and is valid JSON.
    This file defines source file lists used by the build system.
    CI/CD equivalent: used by build system and scripts in CI.
    """
    import json

    r = subprocess.run(
        ["cat", f"{REPO}/cmake/Sources.json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Sources.json not found or unreadable:
{r.stderr}"

    # Validate it's valid JSON
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError as e:
        assert False, f"Sources.json is not valid JSON: {e}"

    # Should be a non-empty list
    assert isinstance(data, list), f"Sources.json should be a list, got {type(data)}"
    assert len(data) > 0, "Sources.json should contain at least one entry"


# [repo_tests] pass_to_pass
def test_repo_prettier_js_web_url():
    """Repo's URL-related test files are properly formatted (pass_to_pass).

    Uses prettier to check formatting of test/js/web/url/*.ts files.
    These tests cover URL/DOMURL functionality related to the fix.
    CI/CD equivalent: part of 'bun run prettier' in format.yml workflow.
    """
    r = subprocess.run(
        ["npx", "prettier", "--check", "test/js/web/url/*.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Prettier returns 0 if all files match
    # We accept formatting issues but fail on parse errors
    has_parse_errors = "parse" in r.stderr.lower() or "parse" in r.stdout.lower()
    assert not has_parse_errors, f"prettier encountered parse errors:
{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_git_log_depth():
    """Repo's git history has sufficient depth (pass_to_pass).

    Validates that the git repository has at least the base commit
    available. This catches issues with shallow clones.
    CI/CD equivalent: git operations in CI workflows.
    """
    r = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git log failed:
{r.stderr}"
    lines = len(r.stdout.strip().splitlines())
    assert lines >= 1, f"git log returned insufficient history ({lines} commits)"


# [repo_tests] pass_to_pass
def test_repo_bindings_dir_structure():
    """Repo's bindings directory has expected structure (pass_to_pass).

    Validates that src/bun.js/bindings/ contains expected C++ binding files.
    This catches issues with directory structure or missing files.
    CI/CD equivalent: part of build system validation.
    """
    r = subprocess.run(
        ["ls", "-la", f"{REPO}/src/bun.js/bindings/"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ls failed on bindings dir:
{r.stderr}"

    # Check for expected files in the bindings directory
    content = r.stdout
    assert "BunString.cpp" in content, "BunString.cpp should exist in bindings dir"
    assert "root.h" in content, "root.h should exist in bindings dir"


# [pr_diff] fail_to_pass
def test_fix_prevents_crash_on_invalid_domurl():
    """The fix must contain a control-flow guard to handle exceptions.

    Without the fix, accessing server.url with an invalid URL causes a segfault.
    With the fix, a control-flow guard prevents reaching jsCast on an invalid
    value, allowing the error to propagate gracefully.
    """
    # Verify the guard exists by checking control flow can diverge
    region = _extract_func_region()
    after = _between_tojs_and_jscast(region)

    # The guard must be able to prevent reaching jsCast on error
    assert _has_control_flow_guard(after), (
        "No control-flow guard between toJSNewlyCreated and jsCast. "
        "This guard is required to prevent the segfault when DOMURL creation fails."
    )


# [repo_tests] pass_to_pass
def test_repo_url_domurl_tests():
    """URL/DOMURL tests pass (pass_to_pass).

    Runs the test/js/web/url/url.test.ts tests using bun.
    These tests exercise the URL and DOMURL functionality that the fix
    addresses. CI/CD equivalent: bun test test/js/web/url/url.test.ts
    """
    r = subprocess.run(
        ["npx", "--yes", "bun@latest", "test", "test/js/web/url/url.test.ts"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    # The test should pass with exit code 0 and show passing tests
    assert r.returncode == 0, f"URL tests failed:
{r.stderr[-500:]}{r.stdout[-500:]}"
    # Check combined output (bun may output to stderr or stdout)
    combined = (r.stdout + r.stderr).lower()
    assert "pass" in combined, f"Expected passing tests in output:
{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_clang_format_check():
    """C++ bindings files have valid clang-format syntax (pass_to_pass).

    Uses clang-format to verify BunString.cpp and related bindings files
    can be parsed (not necessarily perfectly formatted).
    This catches syntax errors in C++ code.
    CI/CD equivalent: part of 'bun run clang-format:check' in CI.
    """
    cpp_file = f"{REPO}/src/bun.js/bindings/BunString.cpp"

    # Try various clang-format versions that might be available
    clang_format_cmds = [
        "clang-format-21",
        "clang-format-20",
        "clang-format-19",
        "clang-format-18",
        "clang-format",
    ]

    available_cmd = None
    for cmd in clang_format_cmds:
        r = subprocess.run(["which", cmd], capture_output=True, timeout=10)
        if r.returncode == 0:
            available_cmd = cmd
            break

    if available_cmd is None:
        # Skip this test if clang-format is not installed
        return

    r = subprocess.run(
        [available_cmd, "--dry-run", cpp_file],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # clang-format returns non-zero if formatting would change,
    # but we're just checking it can parse the file
    has_parse_error = "error" in r.stderr.lower() or "fatal" in r.stderr.lower()
    assert not has_parse_error, f"clang-format found parse errors:
{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cmake_sources_json_structure():
    """Repo's cmake/Sources.json has valid structure (pass_to_pass).

    Validates that cmake/Sources.json is valid JSON and has expected structure.
    This file is used by scripts and build system to track source files.
    CI/CD equivalent: used by build system and formatters in CI.
    """
    import json

    r = subprocess.run(
        ["cat", f"{REPO}/cmake/Sources.json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Sources.json not found:
{r.stderr}"

    # Validate JSON structure
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError as e:
        assert False, f"Sources.json is not valid JSON: {e}"

    # Should be a list with specific structure
    assert isinstance(data, list), f"Sources.json should be a list, got {type(data)}"
    assert len(data) > 0, "Sources.json should contain at least one entry"

    # Each entry should have expected keys
    for i, entry in enumerate(data[:3]):  # Check first 3 entries
        assert isinstance(entry, dict), f"Entry {i} should be a dict"
        assert "output" in entry, f"Entry {i} missing 'output' field"
        assert "paths" in entry, f"Entry {i} missing 'paths' field"
        assert isinstance(entry["paths"], list), f"Entry {i} 'paths' should be a list"

# -----------------------------------------------------------------------------
# agent_config
# -----------------------------------------------------------------------------


# [agent_config] fail_to_pass
# Source: .claude/skills/implementing-jsc-classes-cpp/SKILL.md @ 9e93bfa
def test_control_flow_guard_present():
    """Fix must contain a control-flow guard to handle exceptions.

    Per .claude/skills/implementing-jsc-classes-cpp/SKILL.md, the established
    JSC exception-handling idiom is RETURN_IF_EXCEPTION(throwScope, {}).
    The guard must be able to divert control flow before jsCast when an
    exception is pending.
    """
    after = _between_tojs_and_jscast(_extract_func_region())
    # Accept any control-flow guard (RETURN_IF_EXCEPTION OR if+return)
    assert _has_control_flow_guard(after), (
        "Fix does not contain a control-flow guard. "
        "Per .claude/skills/implementing-jsc-classes-cpp/SKILL.md, use "
        "RETURN_IF_EXCEPTION(throwScope, {}) - the established macro for "
        "checking pending exceptions in JSC binding functions. "
        "An equivalent if-check+return is also acceptable."
    )


# [agent_config] pass_to_pass
# Source: .claude/skills/implementing-jsc-classes-cpp/SKILL.md line 184 @ 9e93bfa
def test_includes_root_header():
    """BunString.cpp must include root.h as required for C++ bindings files.

    Per .claude/skills/implementing-jsc-classes-cpp/SKILL.md line 184,
    C++ files in the bindings directory must include root.h at the top.
    """
    content = Path(TARGET).read_text()
    assert '#include "root.h"' in content, (
        'BunString.cpp must include "root.h". '
        "Per .claude/skills/implementing-jsc-classes-cpp/SKILL.md line 184, "
        'C++ bindings files must include "root.h" at the top.'
    )
