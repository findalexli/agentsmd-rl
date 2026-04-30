"""
Task: next.js-automatically-build-and-clear-native
Repo: vercel/next.js @ def0e3aabfa112ada22ece9297501c52471d34bd
PR:   89819

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"


def test_agents_md_has_rebuild_section():
    """AGENTS.md must contain the Rebuilding Before Running Tests section."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    msg = "AGENTS.md must retain the Rebuilding Before Running Tests section"
    assert "## Rebuilding Before Running Tests" in content, msg


def test_maybe_build_native_skips_in_ci():
    """Running maybe-build-native.mjs with CI=1 must exit 0 and print skip message."""
    script = Path(REPO) / "packages" / "next-swc" / "maybe-build-native.mjs"
    assert script.exists(), f"Script not found: {script}"
    result = subprocess.run(
        ["node", str(script)],
        capture_output=True,
        text=True,
        timeout=15,
        env={"CI": "1", "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/root"},
        cwd=str(Path(REPO) / "packages" / "next-swc"),
    )
    assert result.returncode == 0, f"Script failed rc={result.returncode}"
    assert "Skipping swc-build-native in CI" in result.stdout


def test_maybe_build_native_runs_without_ci():
    """Running maybe-build-native.mjs without CI must not crash."""
    script = Path(REPO) / "packages" / "next-swc" / "maybe-build-native.mjs"
    assert script.exists(), f"Script not found: {script}"
    result = subprocess.run(
        ["node", str(script)],
        capture_output=True,
        text=True,
        timeout=30,
        env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/root"},
        cwd=str(Path(REPO) / "packages" / "next-swc"),
    )
    output = result.stdout + result.stderr
    assert "unhandled" not in output.lower() and "exception" not in output.lower()


def test_maybe_build_native_has_rust_detection():
    """maybe-build-native.mjs must define hasRustChanges and getVersionBumpCommit functions."""
    script = Path(REPO) / "packages" / "next-swc" / "maybe-build-native.mjs"
    assert script.exists(), f"Script not found: {script}"
    content = script.read_text()
    assert "function hasRustChanges" in content, "must define function hasRustChanges"
    assert "function getVersionBumpCommit" in content, "must define function getVersionBumpCommit"


def test_package_json_build_script():
    """packages/next-swc/package.json must have a build script referencing maybe-build-native."""
    pkg = Path(REPO) / "packages" / "next-swc" / "package.json"
    data = json.loads(pkg.read_text())
    scripts = data.get("scripts", {})
    assert "build" in scripts, "package.json must have a build script"
    assert "maybe-build-native" in scripts["build"], "build script must reference maybe-build-native"


def test_turbo_json_build_task():
    """packages/next-swc/turbo.json must define a build task with Rust inputs and CI env."""
    turbo = Path(REPO) / "packages" / "next-swc" / "turbo.json"
    data = json.loads(turbo.read_text())
    tasks = data.get("tasks", {})
    assert "build" in tasks, "turbo.json must define a build task"
    build_task = tasks["build"]
    inputs = build_task.get("inputs", [])
    input_str = " ".join(inputs)
    assert "crates" in input_str, "build task inputs must include crates directory"
    assert "Cargo" in input_str, "build task inputs must include Cargo files"
    assert "CI" in build_task.get("env", []), "build task must include CI in env"


def test_build_native_prettier_pipeline():
    """scripts/build-native.ts must use --stdin-filepath not --write with prettier."""
    script = Path(REPO) / "scripts" / "build-native.ts"
    content = script.read_text()
    assert "--stdin-filepath" in content, (
        "scripts/build-native.ts must use --stdin-filepath for prettier formatting"
    )
    assert "'--write'" not in content, (
        "scripts/build-native.ts must not use '--write' with prettier"
    )
    assert '"--write"' not in content, (
        'scripts/build-native.ts must not use "--write" with prettier'
    )


def test_agents_md_simplified_rebuild():
    """AGENTS.md must unify Rust/Turbopack rebuild instructions under pnpm build."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    assert "pnpm swc-build-native" not in content
    assert "pnpm turbo build build-native" not in content
    lines = content.split(chr(10))
    rebuild_lines = [l for l in lines if "Turbopack" in l and "Rust" in l and "pnpm build" in l]
    assert len(rebuild_lines) >= 1


def test_maybe_build_native_syntax():
    """maybe-build-native.mjs must exist and have valid JavaScript syntax."""
    script = Path(REPO) / "packages" / "next-swc" / "maybe-build-native.mjs"
    if not script.exists():
        raise AssertionError("maybe-build-native.mjs does not exist")
    result = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Syntax error"


def test_repo_package_json_valid():
    """Root package.json must be valid JSON."""
    pkg = Path(REPO) / "package.json"
    json.loads(pkg.read_text())


def test_repo_turbo_json_valid():
    """Root turbo.json must be valid JSON."""
    turbo = Path(REPO) / "turbo.json"
    json.loads(turbo.read_text())


def test_repo_next_swc_package_json_valid():
    """packages/next-swc/package.json must be valid JSON."""
    pkg = Path(REPO) / "packages" / "next-swc" / "package.json"
    json.loads(pkg.read_text())


def test_repo_next_swc_turbo_json_valid():
    """packages/next-swc/turbo.json must be valid JSON."""
    turbo = Path(REPO) / "packages" / "next-swc" / "turbo.json"
    json.loads(turbo.read_text())


def test_repo_validate_externals_doc_syntax():
    """scripts/validate-externals-doc.js must have valid syntax."""
    script = Path(REPO) / "scripts" / "validate-externals-doc.js"
    result = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Syntax error"


def test_repo_build_native_syntax():
    """scripts/build-native.ts must have valid syntax (TypeScript via node --check)."""
    script = Path(REPO) / "scripts" / "build-native.ts"
    result = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Syntax error"


def test_repo_prettier_build_native():
    """scripts/build-native.ts must pass prettier formatting check."""
    script = Path(REPO) / "scripts" / "build-native.ts"
    result = subprocess.run(
        ["npx", "prettier", "--check", str(script)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Prettier check failed"


def test_repo_prettier_validate_externals_doc():
    """scripts/validate-externals-doc.js must pass prettier formatting check."""
    script = Path(REPO) / "scripts" / "validate-externals-doc.js"
    result = subprocess.run(
        ["npx", "prettier", "--check", str(script)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Prettier check failed"


def test_repo_prettier_package_json():
    """Root package.json must pass prettier formatting check."""
    pkg = Path(REPO) / "package.json"
    result = subprocess.run(
        ["npx", "prettier", "--check", str(pkg)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Prettier check failed"


def test_repo_prettier_next_swc_package_json():
    """packages/next-swc/package.json must pass prettier formatting check."""
    pkg = Path(REPO) / "packages" / "next-swc" / "package.json"
    result = subprocess.run(
        ["npx", "prettier", "--check", str(pkg)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Prettier check failed"


def test_repo_prettier_turbo_json():
    """turbo.json files must pass prettier formatting check."""
    root_turbo = Path(REPO) / "turbo.json"
    next_swc_turbo = Path(REPO) / "packages" / "next-swc" / "turbo.json"
    for turbo_file in [root_turbo, next_swc_turbo]:
        result = subprocess.run(
            ["npx", "prettier", "--check", str(turbo_file)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Prettier check failed for {turbo_file}"


def test_repo_prettier_maybe_build_native():
    """packages/next-swc/maybe-build-native.mjs must pass prettier formatting check."""
    script = Path(REPO) / "packages" / "next-swc" / "maybe-build-native.mjs"
    result = subprocess.run(
        ["npx", "prettier", "--check", str(script)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Prettier check failed"


def test_repo_maybe_build_native_syntax_p2p():
    """maybe-build-native.mjs must have valid syntax (checked both before and after patch)."""
    script = Path(REPO) / "packages" / "next-swc" / "maybe-build-native.mjs"
    result = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Syntax error"


def test_repo_build_wasm_syntax():
    """scripts/build-wasm.cjs must have valid syntax."""
    script = Path(REPO) / "scripts" / "build-wasm.cjs"
    result = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Syntax error"


def test_repo_prettier_agents_md():
    """AGENTS.md must pass prettier formatting check."""
    agents_md = Path(REPO) / "AGENTS.md"
    result = subprocess.run(
        ["npx", "prettier", "--check", str(agents_md)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Prettier check failed"


def test_ci_prettier_next_swc():
    """pass_to_pass | CI lint: prettier check on next-swc package files."""
    r = subprocess.run(
        ["bash", "-lc", "npx prettier --check packages/next-swc/package.json packages/next-swc/turbo.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"prettier check failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_pnpm():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm install'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_pnpm_2():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_validate_docs_links_run_link_checker():
    """pass_to_pass | CI job 'validate-docs-links' → step 'Run link checker'"""
    r = subprocess.run(
        ["bash", "-lc", 'node ./.github/actions/validate-docs-links/dist/index.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run link checker' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")