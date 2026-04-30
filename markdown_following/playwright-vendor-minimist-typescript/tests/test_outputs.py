"""
Task: playwright-vendor-minimist-typescript
Repo: microsoft/playwright @ 4df350b1c81b61ea471ff12767efd8e05f773377
PR:   #39734

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
CLI_DIR = f"{REPO}/packages/playwright-core/src/tools/cli-client"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp .ts script in the cli-client dir and run it with Node."""
    script_path = Path(CLI_DIR) / "_eval_tmp.mts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            [
                "node",
                "--experimental-strip-types",
                "--no-warnings",
                str(script_path),
            ],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — vendored minimist behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_minimist_parses_args():
    """Vendored minimist correctly parses boolean, string, and positional args."""
    result = _run_ts("""
import { minimist } from './minimist.ts';
const args = minimist(
    ['--verbose', '--name', 'alice', '--no-color', 'file.txt'],
    { boolean: ['verbose', 'color'], string: ['name'] }
);
console.log(JSON.stringify(args));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["verbose"] is True, f"Expected verbose=true, got {data.get('verbose')}"
    assert data["color"] is False, f"Expected color=false, got {data.get('color')}"
    assert data["name"] == "alice", f"Expected name='alice', got {data.get('name')}"
    assert "file.txt" in data["_"], f"Expected 'file.txt' in positional args, got {data['_']}"


# [pr_diff] fail_to_pass
def test_minimist_boolean_equals_error():
    """Vendored minimist throws error when boolean option passed with =value."""
    result = _run_ts("""
import { minimist } from './minimist.ts';
try {
    minimist(['--verbose=true'], { boolean: ['verbose'] });
    console.log('NO_ERROR');
} catch (e: any) {
    console.log('ERROR:' + e.message);
}
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    output = result.stdout.strip()
    assert output.startswith("ERROR:"), f"Expected error for --bool=value, got: {output}"
    assert "verbose" in output, f"Error should mention 'verbose': {output}"


# [pr_diff] fail_to_pass
def test_minimist_double_dash():
    """Vendored minimist handles -- separator correctly."""
    result = _run_ts("""
import { minimist } from './minimist.ts';
const args = minimist(
    ['--flag', '--', '--not-a-flag', 'positional'],
    { boolean: ['flag'] }
);
console.log(JSON.stringify(args));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["flag"] is True, f"Expected flag=true, got {data.get('flag')}"
    assert "--not-a-flag" in data["_"], f"Args after -- should be positional: {data['_']}"
    assert "positional" in data["_"], f"'positional' should be in _: {data['_']}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral integration tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_program_imports_vendored():
    """program.ts can import and use the vendored minimist (not npm package)."""
    # First verify minimist.ts exists and exports correctly
    # Note: MinimistArgs is a type-only export, import only the runtime value minimist
    result = _run_ts("""
import { minimist } from './minimist.ts';
const args = minimist(['--test'], { boolean: ['test'] });
if (args.test !== true) {
    console.log('FAILED: minimist export not working');
    process.exit(1);
}
console.log('VENDORED_IMPORT_OK');
""")
    assert result.returncode == 0, f"Vendored minimist failed to import: {result.stderr}"
    assert "VENDORED_IMPORT_OK" in result.stdout, f"Expected VENDORED_IMPORT_OK, got: {result.stdout}"

    # Now verify program.ts imports from local path (structural check still needed)
    content = Path(f"{CLI_DIR}/program.ts").read_text()
    assert "from './minimist'" in content or 'from "./minimist"' in content, \
        "program.ts should import from vendored ./minimist"
    assert "require('minimist')" not in content and 'require("minimist")' not in content, \
        "program.ts should not use require('minimist')"


# [pr_diff] fail_to_pass
def test_types_minimist_removed():
    """@types/minimist dev dependency removed and package.json is valid."""
    # Check package.json doesn't contain @types/minimist
    pkg_path = Path(f"{REPO}/package.json")
    content = pkg_path.read_text()
    assert "@types/minimist" not in content, \
        "package.json should not contain @types/minimist"

    # Verify package.json is valid JSON and has expected structure
    try:
        import json
        pkg = json.loads(content)
        assert "devDependencies" in pkg, "package.json should have devDependencies"
        assert "@types/minimist" not in pkg.get("devDependencies", {}), \
            "@types/minimist should not be in devDependencies object"
    except json.JSONDecodeError as e:
        raise AssertionError(f"package.json is not valid JSON: {e}")


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — DEPS system rule from CLAUDE.md:95
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:95 @ 4df350b1c81b61ea471ff12767efd8e05f773377
def test_deps_list_updated():
    """DEPS.list declares minimist.ts as allowed import per CLAUDE.md DEPS rule."""
    content = Path(f"{CLI_DIR}/DEPS.list").read_text()
    assert "./minimist.ts" in content, "DEPS.list should declare ./minimist.ts"
    assert "[minimist.ts]" in content, "DEPS.list should have [minimist.ts] section"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config file update
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_generated_with_rule():
    """CLAUDE.md includes rule against 'Generated with' in commit messages."""
    content = Path(f"{REPO}/CLAUDE.md").read_text()
    assert "generated with" in content.lower(), \
        "CLAUDE.md should mention not adding 'Generated with' in commit messages"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — existing rules preserved
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:127 @ 4df350b1c81b61ea471ff12767efd8e05f773377
def test_claude_md_commit_rules_intact():
    """CLAUDE.md still has existing commit message and branch naming rules."""
    content = Path(f"{REPO}/CLAUDE.md").read_text()
    assert "co-authored-by" in content.lower(), \
        "CLAUDE.md should still mention Co-Authored-By rule"
    assert "fix-<issue-number>" in content, \
        "CLAUDE.md should still have branch naming convention"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cli_client_files_exist():
    """Repo's cli-client source files exist and are non-empty (pass_to_pass)."""
    # Verify core cli-client files exist and have content
    for fname in ["program.ts", "session.ts", "registry.ts", "cli.ts", "DEPS.list"]:
        fpath = Path(f"{CLI_DIR}/{fname}")
        assert fpath.exists(), f"{fname} should exist in cli-client directory"
        content = fpath.read_text()
        assert len(content) > 0, f"{fname} should not be empty"


# [repo_tests] pass_to_pass
def test_repo_cli_client_typescript_no_syntax_errors():
    """Repo's cli-client TypeScript files have no obvious syntax errors (pass_to_pass)."""
    # Check for basic syntax issues in TypeScript files
    for fname in ["program.ts", "session.ts", "registry.ts", "cli.ts"]:
        fpath = Path(f"{CLI_DIR}/{fname}")
        content = fpath.read_text()

        # Check for balanced braces (basic syntax check)
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, f"{fname} has unbalanced braces"

        # Check for balanced parentheses
        open_parens = content.count("(")
        close_parens = content.count(")")
        assert open_parens == close_parens, f"{fname} has unbalanced parentheses"


# [repo_tests] pass_to_pass
def test_repo_deps_list_valid():
    """Repo's DEPS.list file is valid and parseable (pass_to_pass)."""
    deps_path = Path(f"{CLI_DIR}/DEPS.list")
    content = deps_path.read_text()

    # Verify DEPS.list has valid structure with sections
    assert "[program.ts]" in content, "DEPS.list should have [program.ts] section"
    assert "[session.ts]" in content, "DEPS.list should have [session.ts] section"
    assert "[registry.ts]" in content, "DEPS.list should have [registry.ts] section"

    # Verify strict mode is declared
    assert '"strict"' in content, "DEPS.list should declare strict mode"


# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """Repo's package.json is valid JSON with expected structure (pass_to_pass)."""
    pkg_path = Path(f"{REPO}/package.json")
    content = pkg_path.read_text()

    # Verify valid JSON
    try:
        pkg = json.loads(content)
    except json.JSONDecodeError as e:
        raise AssertionError(f"package.json is not valid JSON: {e}")

    # Verify expected structure
    assert "name" in pkg, "package.json should have name field"
    assert "devDependencies" in pkg, "package.json should have devDependencies"
    assert "@types/node" in pkg.get("devDependencies", {}), "package.json should have @types/node"


# [repo_tests] pass_to_pass - Real CI commands from the repo's CI/CD pipeline
# These tests use subprocess.run() to execute actual commands that CI runs
# CI commands found: npm run eslint, npm run tsc, npm run check-deps, npm run lint-packages


# Module-level cache for build state
_build_cache = {"done": False}


def _ensure_built():
    """Run npm ci and build once, cached across tests."""
    if _build_cache["done"]:
        return

    # Install dependencies
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"

    # Build the project
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm run build failed:\n{r.stderr[-500:]}"

    _build_cache["done"] = True


def test_repo_eslint_cli_client():
    """Repo's ESLint passes on cli-client directory (pass_to_pass).

    CI command: npm run eslint -- --max-warnings=0 packages/playwright-core/src/tools/cli-client/
    """
    _ensure_built()

    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--max-warnings=0", "packages/playwright-core/src/tools/cli-client/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_typescript_compile():
    """Repo's TypeScript compiler passes (pass_to_pass).

    CI command: npm run tsc
    """
    _ensure_built()

    r = subprocess.run(
        ["npm", "run", "tsc"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}"


def test_repo_check_deps():
    """Repo's DEPS.list check passes (pass_to_pass).

    CI command: npm run check-deps
    """
    _ensure_built()

    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # check-deps outputs "Disallowed" to stdout when there are issues
    assert "Disallowed" not in r.stdout, f"DEPS.list check found disallowed imports:\n{r.stdout[-500:]}"


def test_repo_lint_packages():
    """Repo's workspace package lint passes (pass_to_pass).

    CI command: npm run lint-packages
    """
    _ensure_built()

    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stderr[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_playwright_driver_npm():
    """pass_to_pass | CI job 'build-playwright-driver' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_playwright_driver_npm_2():
    """pass_to_pass | CI job 'build-playwright-driver' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")