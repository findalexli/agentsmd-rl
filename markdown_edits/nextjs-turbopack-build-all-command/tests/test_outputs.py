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
# Gates (pass_to_pass, static) — JSON validity and structure checks
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


# [static] pass_to_pass — Repo CI/CD config validation
def test_lerna_json_valid():
    """lerna.json is valid JSON with required fields (pass_to_pass)."""
    lerna = json.loads(Path(f"{REPO}/lerna.json").read_text())
    assert "version" in lerna, "lerna.json missing 'version'"
    assert "packages" in lerna, "lerna.json missing 'packages'"
    # lerna uses glob patterns like "packages/*" not literal paths
    assert any("packages/" in p for p in lerna["packages"]), "lerna.json missing packages/* pattern"


# [static] pass_to_pass — Repo CI/CD config validation
def test_turbo_json_valid():
    """Root turbo.json is valid JSON with tasks defined (pass_to_pass)."""
    turbo = json.loads(Path(f"{REPO}/turbo.json").read_text())
    assert "$schema" in turbo, "turbo.json missing '$schema'"
    assert "tasks" in turbo, "turbo.json missing 'tasks'"
    assert "build" in turbo["tasks"], "turbo.json missing 'build' task"


# [static] pass_to_pass — Repo CI/CD config validation
def test_next_package_json_valid():
    """packages/next/package.json is valid JSON with required fields (pass_to_pass)."""
    pkg = json.loads(Path(f"{REPO}/packages/next/package.json").read_text())
    assert "name" in pkg and pkg["name"] == "next", "next package name must be 'next'"
    assert "scripts" in pkg, "next package.json missing 'scripts'"
    assert "build" in pkg["scripts"], "next package.json missing 'build' script"


# [static] pass_to_pass — Monorepo structure validation
def test_packages_directory_structure():
    """Packages directory has expected structure (pass_to_pass)."""
    packages_dir = Path(f"{REPO}/packages")
    assert packages_dir.exists(), "packages/ directory must exist"
    # Core packages should exist
    core_packages = ["next", "next-swc", "create-next-app"]
    for pkg in core_packages:
        pkg_path = packages_dir / pkg / "package.json"
        assert pkg_path.exists(), f"Core package {pkg}/package.json must exist"


# [static] pass_to_pass — Git repository validation
def test_git_repo_valid():
    """Git repository is valid and at expected commit (pass_to_pass)."""
    git_dir = Path(f"{REPO}/.git")
    assert git_dir.exists(), ".git directory must exist"
    # Verify HEAD is at expected commit
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert result.returncode == 0, "git rev-parse must succeed"
    head_commit = result.stdout.strip()
    # The commit should start with the expected base commit (allow for local commits)
    expected_base = "46761a321042e8ac1863f4cfc8d73d527956e181"
    if head_commit.startswith(expected_base[:16]):
        return  # HEAD is at expected commit
    # Allow for one local commit on top (gold solution case) - check HEAD~1
    result = subprocess.run(
        ["git", "rev-parse", "HEAD~1"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    if result.returncode == 0:
        parent_commit = result.stdout.strip()
        if parent_commit.startswith(expected_base[:16]):
            return  # HEAD~1 is at expected commit
    assert False, f"Unexpected HEAD commit: {head_commit[:16]}... expected {expected_base[:16]}... (or one commit on top)"


# [repo_tests] pass_to_pass — Node.js CLI validation
def test_node_version():
    """Node.js version meets minimum requirement (pass_to_pass)."""
    result = subprocess.run(
        ["node", "--version"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, "node --version must succeed"
    version = result.stdout.strip()
    # Node version should be >= 20
    major = int(version.lstrip("v").split(".")[0])
    assert major >= 20, f"Node version {version} must be >= 20"


# [repo_tests] pass_to_pass — Package manager validation
def test_pnpm_version():
    """pnpm is available and at expected version (pass_to_pass)."""
    try:
        result = subprocess.run(
            ["pnpm", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            assert version.startswith("9."), f"pnpm version {version} should be 9.x"
        # If pnpm is not available (returncode != 0), that's OK for this test
        # The Dockerfile doesn't install pnpm, so we skip this check
    except FileNotFoundError:
        # pnpm not installed in Docker image, skip this test
        pass


# [repo_tests] pass_to_pass — CI release script validation
def test_check_is_release_js():
    """CI release check script runs and produces expected output (pass_to_pass)."""
    result = subprocess.run(
        ["node", "scripts/check-is-release.js"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    # Script returns exit 0 for release commits, exit 1 for non-release
    # Both are valid - just verify it produces expected output format
    output = result.stdout + result.stderr
    assert "not publish commit" in output or result.returncode == 0, (
        f"check-is-release.js produced unexpected output: {output}"
    )


# [repo_tests] pass_to_pass — Shell script syntax validation
def test_shell_scripts_syntax():
    """Shell scripts have valid syntax (pass_to_pass)."""
    scripts = [
        "scripts/check-examples.sh",
        "scripts/check-pre-compiled.sh",
    ]
    for script in scripts:
        script_path = Path(f"{REPO}/{script}")
        if script_path.exists():
            result = subprocess.run(
                ["bash", "-n", str(script_path)],
                capture_output=True, text=True, timeout=10,
            )
            assert result.returncode == 0, f"Shell syntax error in {script}: {result.stderr}"


# [repo_tests] pass_to_pass — JSON validation via Python
def test_workspace_package_json_python():
    """Root package.json is valid JSON via Python parser (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", "import json; json.load(open('package.json'))"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert result.returncode == 0, f"package.json Python validation failed: {result.stderr}"


# [repo_tests] pass_to_pass — Node.js can parse package.json
def test_node_parse_package_json():
    """Node.js can parse and evaluate package.json scripts (pass_to_pass)."""
    result = subprocess.run(
        ["node", "-e", "const p=require('./package.json'); console.log(JSON.stringify(Object.keys(p.scripts).slice(0,5)));"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert result.returncode == 0, f"Node.js package.json parse failed: {result.stderr}"
    output = result.stdout.strip()
    assert "build" in output or "new-error" in output, f"Unexpected output from Node: {output}"


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
