"""
Task: nextjs-turbopack-build-all-script
Repo: vercel/next.js @ 46761a321042e8ac1863f4cfc8d73d527956e181
PR:   90543

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This task verifies:
1. Code changes: build-all script added, build renamed to build-native-auto in turbo.jsonc
2. Config changes: AGENTS.md updated to distinguish pnpm build vs pnpm build-all
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"


def _read_json(path: str) -> dict:
    """Read and parse a JSON file."""
    content = Path(path).read_text()
    return json.loads(content)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI command checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """Root package.json is valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('package.json', 'utf8')); console.log('OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"package.json is not valid JSON:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_next_swc_package_json_valid():
    """packages/next-swc/package.json is valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('packages/next-swc/package.json', 'utf8')); console.log('OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"packages/next-swc/package.json is not valid JSON:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_turbo_jsonc_exists():
    """packages/next-swc/turbo.jsonc exists and is readable (pass_to_pass)."""
    r = subprocess.run(
        ["test", "-r", f"{REPO}/packages/next-swc/turbo.jsonc"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"turbo.jsonc does not exist or is not readable:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build_script_exists():
    """Root package.json has build script (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-p", "require('./package.json').scripts.build"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"build script not found:\n{r.stderr[-500:]}"
    assert "turbo" in r.stdout, f"build script should use turbo: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_agents_md_exists():
    """AGENTS.md exists and is readable (pass_to_pass)."""
    r = subprocess.run(
        ["test", "-r", f"{REPO}/AGENTS.md"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"AGENTS.md not readable:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_json_syntax_valid():
    """Modified JSON files must be syntactically valid."""
    root_pkg = Path(f"{REPO}/package.json")
    next_swc_pkg = Path(f"{REPO}/packages/next-swc/package.json")

    # These should parse without errors
    _read_json(str(root_pkg))
    _read_json(str(next_swc_pkg))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_all_script_exists():
    """Root package.json must have build-all script that includes build-native-auto."""
    pkg = _read_json(f"{REPO}/package.json")
    scripts = pkg.get("scripts", {})

    assert "build-all" in scripts, "build-all script must exist in root package.json"
    build_all = scripts["build-all"]
    assert "build-native-auto" in build_all, \
        f"build-all must reference build-native-auto task, got: {build_all}"


# [pr_diff] fail_to_pass
def test_next_swc_script_renamed():
    """packages/next-swc/package.json build script must be renamed to build-native-auto."""
    pkg = _read_json(f"{REPO}/packages/next-swc/package.json")
    scripts = pkg.get("scripts", {})

    # The old "build" script that runs maybe-build-native.mjs should be renamed
    assert "build" not in scripts or "maybe-build-native" not in scripts.get("build", ""), \
        "Old 'build' script calling maybe-build-native.mjs should not exist"
    assert "build-native-auto" in scripts, \
        "build-native-auto script must exist"
    assert "maybe-build-native" in scripts["build-native-auto"], \
        "build-native-auto should call maybe-build-native.mjs"


# [pr_diff] fail_to_pass
def test_turbo_jsonc_task_renamed():
    """turbo.jsonc must have build-native-auto task instead of build task."""
    turbo_path = Path(f"{REPO}/packages/next-swc/turbo.jsonc")
    assert turbo_path.exists(), "turbo.jsonc must exist (renamed from turbo.json)"

    content = turbo_path.read_text()

    # Should have build-native-auto task with comment explaining it
    assert '"build-native-auto"' in content, \
        "turbo.jsonc must define build-native-auto task"
    assert '"build":' not in content or '"build-native-auto"' in content, \
        "Old 'build' task should be renamed to 'build-native-auto'"

    # Should have the explanatory comment about "auto"
    assert "auto" in content.lower() and "build-all" in content, \
        "turbo.jsonc should have comment explaining build-native-auto is for build-all"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Config update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_documents_build_all():
    """AGENTS.md must document pnpm build-all for building JS + Rust code."""
    agents_md = Path(f"{REPO}/AGENTS.md").read_text()

    # Should mention build-all command
    assert "pnpm build-all" in agents_md, \
        "AGENTS.md should document pnpm build-all command"

    # Should distinguish between build (JS only) and build-all (JS + Rust)
    assert "pnpm build" in agents_md, \
        "AGENTS.md should still document pnpm build"

    # Should explain when to use build-all vs build --filter=next
    # Check for key phrases that indicate the distinction
    js_only_indicators = ["build all JS code", "JS code", "JS and Rust"]
    has_js_only_distinction = any(indicator in agents_md for indicator in js_only_indicators)
    assert has_js_only_distinction, \
        "AGENTS.md should distinguish between 'build' (JS only) and 'build-all' (JS + Rust)"


# [pr_diff] fail_to_pass
def test_agents_md_branch_switch_uses_build_all():
    """AGENTS.md should recommend build-all for branch switches and when editing Turbopack."""
    agents_md = Path(f"{REPO}/AGENTS.md").read_text()

    # After branch switch, should use build-all
    branch_switch_section = agents_md.find("switching branches")
    if branch_switch_section != -1:
        # Look at context after "switching branches"
        context = agents_md[branch_switch_section:branch_switch_section + 500]
        assert "build-all" in context, \
            "AGENTS.md should recommend build-all after switching branches"

    # When editing Turbopack/Rust, should use build-all
    assert "build-all" in agents_md.lower(), \
        "AGENTS.md should reference build-all in the context of Turbopack/Rust builds"
