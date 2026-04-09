"""
Task: nextjs-turbopack-build-all-command
Repo: next.js @ 46761a321042e8ac1863f4cfc8d73d527956e181
PR:   90543

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — JSON validity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_root_package_json_valid():
    """Root package.json must be valid JSON with build script preserved."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    assert "scripts" in pkg, "package.json missing 'scripts'"
    assert "build" in pkg["scripts"], "Existing 'build' script must be preserved"


# [static] pass_to_pass
def test_next_swc_package_json_valid():
    """packages/next-swc/package.json must be valid JSON with scripts."""
    pkg = json.loads(Path(f"{REPO}/packages/next-swc/package.json").read_text())
    assert "scripts" in pkg, "next-swc package.json missing 'scripts'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_all_script_via_node():
    """Node parses root package.json and finds build-all with build-native-auto."""
    result = subprocess.run(
        ["node", "-e",
         "const p=require('./package.json');"
         "const s=p.scripts['build-all']||'';"
         "if(!s.includes('build-native-auto'))"
         "{console.error('build-all missing or wrong:',s);process.exit(1);}"
         "console.log(JSON.stringify({script:s}));"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert result.returncode == 0, f"build-all script check failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert "build-native-auto" in data["script"]


# [pr_diff] fail_to_pass
def test_next_swc_build_native_auto():
    """next-swc package.json has build-native-auto running maybe-build-native."""
    result = subprocess.run(
        ["node", "-e",
         "const p=require('./packages/next-swc/package.json');"
         "const s=p.scripts['build-native-auto']||'';"
         "if(!s.includes('maybe-build-native'))"
         "{console.error('build-native-auto wrong:',s);process.exit(1);}"
         "console.log(JSON.stringify({script:s}));"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert result.returncode == 0, f"build-native-auto check failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert "maybe-build-native" in data["script"]


# [pr_diff] fail_to_pass
def test_turbo_config_task_renamed():
    """Turbo config must have build-native-auto task."""
    turbo_path = Path(f"{REPO}/packages/next-swc/turbo.jsonc")
    if not turbo_path.exists():
        turbo_path = Path(f"{REPO}/packages/next-swc/turbo.json")
    content = turbo_path.read_text()
    # Strip JSONC comments (preserving // inside strings like URLs)
    stripped = re.sub(
        r'"(?:[^"\\]|\\.)*"|//.*$',
        lambda m: m.group() if m.group().startswith('"') else "",
        content,
        flags=re.MULTILINE,
    )
    # Strip trailing commas before } or ]
    stripped = re.sub(r",(\s*[}\]])", r"\1", stripped)
    data = json.loads(stripped)
    tasks = data.get("tasks", {})
    assert "build-native-auto" in tasks, (
        f"Turbo config missing 'build-native-auto' task. Found: {list(tasks.keys())}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — AGENTS.md config update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_documents_build_all():
    """AGENTS.md must reference 'pnpm build-all' for full JS+Rust builds."""
    agents_path = Path(f"{REPO}/AGENTS.md")
    content = agents_path.read_text()
    assert "pnpm build-all" in content, (
        "AGENTS.md should document 'pnpm build-all' command"
    )
    # Must appear in multiple contexts (build commands, bootstrap, rebuild sections)
    lines_with_build_all = [l for l in content.split("\n") if "build-all" in l]
    assert len(lines_with_build_all) >= 3, (
        f"AGENTS.md should reference 'build-all' in at least 3 contexts. "
        f"Found {len(lines_with_build_all)} references."
    )


# [pr_diff] fail_to_pass
def test_agents_md_build_js_clarification():
    """AGENTS.md must no longer describe 'pnpm build' as building everything."""
    agents_path = Path(f"{REPO}/AGENTS.md")
    content = agents_path.read_text()
    # The old "# Build everything" comment above "pnpm build" must be updated
    assert "# Build everything\npnpm build" not in content, (
        "AGENTS.md should no longer describe 'pnpm build' as 'Build everything'"
    )
    # "build-all" should be associated with Rust or comprehensive builds
    build_all_lines = [l for l in content.split("\n") if "build-all" in l.lower()]
    has_rust_or_all = any(
        "rust" in l.lower() or "all" in l.lower() for l in build_all_lines
    )
    assert has_rust_or_all, (
        "AGENTS.md should associate 'build-all' with Rust or comprehensive builds"
    )
