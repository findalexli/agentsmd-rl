"""
Task: next.js-turbopack-move-turbopack-out-of
Repo: vercel/next.js @ e2ef94e2efb4d0067d62ce492dba5568ad1379d9
PR:   90543

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/next.js"


def _run_node_json_extract(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Node.js code that outputs JSON and return parsed result."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_package_json_valid():
    """Root package.json must be valid JSON."""
    r = subprocess.run(
        ["node", "-e", f"JSON.parse(require('fs').readFileSync('{REPO}/package.json', 'utf8')); console.log('VALID')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"package.json is invalid: {r.stderr}"
    assert "VALID" in r.stdout


# [static] pass_to_pass
def test_next_swc_package_json_valid():
    """packages/next-swc/package.json must be valid JSON."""
    r = subprocess.run(
        ["node", "-e", f"JSON.parse(require('fs').readFileSync('{REPO}/packages/next-swc/package.json', 'utf8')); console.log('VALID')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"packages/next-swc/package.json is invalid: {r.stderr}"
    assert "VALID" in r.stdout


# [static] pass_to_pass
def test_turbo_jsonc_valid():
    """turbo.jsonc must exist and be valid JSONC (or JSON)."""
    turbo_path = Path(REPO) / "packages" / "next-swc" / "turbo.jsonc"
    assert turbo_path.exists(), "turbo.jsonc does not exist (should be renamed from turbo.json)"

    # Try to parse as JSON (JSONC is a superset, basic JSONC without comments should parse)
    # For JSONC with comments, we'd need a special parser, but let's check structure
    content = turbo_path.read_text()
    assert '"$schema"' in content, "turbo.jsonc missing schema declaration"
    assert '"tasks"' in content, "turbo.jsonc missing tasks section"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_all_script_exists():
    """Root package.json must have build-all script that runs both build and build-native-auto."""
    code = """
import { readFileSync } from 'fs';
const pkg = JSON.parse(readFileSync('./package.json', 'utf8'));
const buildAll = pkg.scripts?.['build-all'];
if (!buildAll) {
    console.log(JSON.stringify({error: 'build-all script not found'}));
    process.exit(1);
}
const hasBuild = buildAll.includes('build');
const hasNativeAuto = buildAll.includes('build-native-auto');
console.log(JSON.stringify({buildAll, hasBuild, hasNativeAuto}));
"""
    r = _run_node_json_extract(code)
    assert r.returncode == 0, f"Failed to check build-all script: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, data.get("error")
    assert data.get("hasBuild") is True, "build-all script must include 'build'"
    assert data.get("hasNativeAuto") is True, "build-all script must include 'build-native-auto'"


# [pr_diff] fail_to_pass
def test_next_swc_build_native_auto_script():
    """packages/next-swc/package.json must have build-native-auto script instead of build."""
    code = """
import { readFileSync } from 'fs';
const pkg = JSON.parse(readFileSync('./packages/next-swc/package.json', 'utf8'));
const scripts = pkg.scripts || {};
const hasBuildNativeAuto = 'build-native-auto' in scripts;
const hasBuild = 'build' in scripts;
const buildNativeAutoValue = scripts['build-native-auto'];
console.log(JSON.stringify({hasBuildNativeAuto, hasBuild, buildNativeAutoValue}));
"""
    r = _run_node_json_extract(code)
    assert r.returncode == 0, f"Failed to check next-swc scripts: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("hasBuildNativeAuto") is True, "build-native-auto script not found"
    assert data.get("hasBuild") is False, "build script should not exist (should be renamed to build-native-auto)"
    assert "maybe-build-native.mjs" in data.get("buildNativeAutoValue", ""), "build-native-auto should run maybe-build-native.mjs"


# [pr_diff] fail_to_pass
def test_turbo_jsonc_task_renamed():
    """turbo.jsonc must have build-native-auto task instead of build task."""
    import re

    turbo_path = Path(REPO) / "packages" / "next-swc" / "turbo.jsonc"
    content = turbo_path.read_text()

    # Check for build-native-auto task
    has_build_native_auto = '"build-native-auto"' in content

    # The old "build" task at the top level should be gone (or at least renamed)
    # We look for the pattern where build is directly under tasks
    build_task_pattern = r'"tasks":\s*\{[^}]*"build":\s*\{'
    has_old_build_task = re.search(build_task_pattern, content, re.DOTALL)

    assert has_build_native_auto, "turbo.jsonc missing build-native-auto task"
    assert has_old_build_task is None, "turbo.jsonc still has old 'build' task (should be renamed to build-native-auto)"


# [pr_diff] fail_to_pass
def test_turbo_jsonc_has_comment():
    """turbo.jsonc must include explanatory comment about build-native-auto."""
    turbo_path = Path(REPO) / "packages" / "next-swc" / "turbo.jsonc"
    content = turbo_path.read_text()

    # Check for comment explaining the purpose
    has_auto_comment = '"auto"' in content and "build-all" in content
    has_explanatory = "up-to-date precompiled version" in content or "checks to see" in content

    assert has_auto_comment or has_explanatory, "turbo.jsonc missing explanatory comment about build-native-auto"


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — structural checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_agents_md_documents_build_all():
    """AGENTS.md must document the build-all command."""
    agents_path = Path(REPO) / "AGENTS.md"
    content = agents_path.read_text()

    assert "pnpm build-all" in content, "AGENTS.md missing documentation for pnpm build-all"
    assert "Build all JS and Rust code" in content or "pnpm build-all" in content, "AGENTS.md should explain build-all purpose"


# [static] pass_to_pass
def test_agents_md_build_command_documentation():
    """AGENTS.md should document pnpm build as building JS code only."""
    agents_path = Path(REPO) / "AGENTS.md"
    content = agents_path.read_text()

    # After the fix, "Build all JS code" or "Build all JS" should describe pnpm build
    assert "Build all JS" in content, "AGENTS.md should document pnpm build as JS-only build"
