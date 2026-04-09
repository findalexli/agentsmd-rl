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
    result = _run_ts("""
import { minimist, MinimistArgs } from './minimist.ts';
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
