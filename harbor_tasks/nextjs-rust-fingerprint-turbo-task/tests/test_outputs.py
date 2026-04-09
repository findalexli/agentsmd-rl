"""
Task: nextjs-rust-fingerprint-turbo-task
Repo: next.js @ 8a241bb504bf167d191b96e914b7785156510038
PR:   92167

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/next.js"


def _parse_jsonc(text: str) -> dict:
    """Strip // comments and trailing commas from JSONC, then parse as JSON."""
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        # Remove single-line // comments (not inside strings — works for turbo config)
        stripped = re.sub(r"//.*$", "", line)
        cleaned.append(stripped)
    text = "\n".join(cleaned)
    # Remove trailing commas before } or ]
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_turbo_json_valid_syntax():
    """turbo.json must parse as valid JSON."""
    turbo_path = Path(f"{REPO}/turbo.json")
    content = turbo_path.read_text()
    data = json.loads(content)
    assert "tasks" in data, "turbo.json missing 'tasks' key"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rust_fingerprint_writes_stamp():
    """rust-fingerprint.js writes TURBO_HASH to target/.rust-fingerprint stamp file."""
    script = Path(f"{REPO}/scripts/rust-fingerprint.js")
    assert script.exists(), "scripts/rust-fingerprint.js does not exist"

    # Use a temp dir to avoid polluting the repo
    with tempfile.TemporaryDirectory() as tmp:
        # Create a wrapper that overrides __dirname resolution
        # by running from a dir structure that mimics the repo
        repo_tmp = Path(tmp) / "repo"
        repo_tmp.mkdir()
        scripts_dir = repo_tmp / "scripts"
        scripts_dir.mkdir()
        # Copy the script
        shutil.copy2(script, scripts_dir / "rust-fingerprint.js")

        for test_hash in ["abc123hash", "xyz789different"]:
            env = os.environ.copy()
            env["TURBO_HASH"] = test_hash
            r = subprocess.run(
                ["node", str(scripts_dir / "rust-fingerprint.js")],
                capture_output=True,
                timeout=10,
                env=env,
            )
            assert r.returncode == 0, f"Script failed: {r.stderr.decode()}"

            stamp = repo_tmp / "target" / ".rust-fingerprint"
            assert stamp.exists(), f"Stamp file not created for hash {test_hash}"
            assert stamp.read_text() == test_hash, (
                f"Stamp content mismatch: expected {test_hash!r}, got {stamp.read_text()!r}"
            )


# [pr_diff] fail_to_pass
def test_rust_fingerprint_skips_without_turbo_hash():
    """rust-fingerprint.js exits 0 and skips when TURBO_HASH is not set."""
    script = Path(f"{REPO}/scripts/rust-fingerprint.js")
    assert script.exists(), "scripts/rust-fingerprint.js does not exist"

    env = os.environ.copy()
    env.pop("TURBO_HASH", None)
    r = subprocess.run(
        ["node", str(script)],
        capture_output=True,
        timeout=10,
        env=env,
    )
    assert r.returncode == 0, f"Script failed: {r.stderr.decode()}"
    assert "skipping" in r.stdout.decode().lower(), (
        f"Expected 'skipping' message, got: {r.stdout.decode()}"
    )


# [pr_diff] fail_to_pass
def test_turbo_jsonc_has_fingerprint_task():
    """turbo.jsonc defines a rust-fingerprint task with Rust source inputs."""
    turbo_path = Path(f"{REPO}/packages/next-swc/turbo.jsonc")
    data = _parse_jsonc(turbo_path.read_text())
    tasks = data.get("tasks", {})

    assert "rust-fingerprint" in tasks, (
        f"rust-fingerprint task not found in turbo.jsonc. Tasks: {list(tasks.keys())}"
    )

    fp_task = tasks["rust-fingerprint"]
    inputs = fp_task.get("inputs", [])

    # Must include key Rust source globs
    assert any("crates/**" in i for i in inputs), (
        f"rust-fingerprint inputs missing crates glob: {inputs}"
    )
    assert any(".cargo/**" in i for i in inputs), (
        f"rust-fingerprint inputs missing .cargo glob: {inputs}"
    )
    assert any("Cargo.lock" in i for i in inputs), (
        f"rust-fingerprint inputs missing Cargo.lock: {inputs}"
    )

    # Must produce the stamp file as output
    outputs = fp_task.get("outputs", [])
    assert any(".rust-fingerprint" in o for o in outputs), (
        f"rust-fingerprint outputs missing stamp file: {outputs}"
    )


# [pr_diff] fail_to_pass
def test_build_tasks_depend_on_fingerprint():
    """Rust build tasks must depend on rust-fingerprint, not duplicate globs."""
    turbo_path = Path(f"{REPO}/packages/next-swc/turbo.jsonc")
    data = _parse_jsonc(turbo_path.read_text())
    tasks = data.get("tasks", {})

    # These tasks should all depend on rust-fingerprint
    expected_dependents = [
        "build-native",
        "build-native-auto",
        "build-native-release",
        "build-wasm",
        "build-native-wasi",
        "rust-check-clippy",
        "rust-check-fmt",
        "test-cargo-unit",
    ]

    missing = []
    for task_name in expected_dependents:
        if task_name not in tasks:
            continue
        deps = tasks[task_name].get("dependsOn", [])
        if "rust-fingerprint" not in deps:
            missing.append(task_name)

    assert not missing, (
        f"Tasks missing dependsOn rust-fingerprint: {missing}"
    )


# [pr_diff] fail_to_pass
def test_build_tasks_use_stamp_not_globs():
    """Build tasks must use the stamp file input, not the old duplicated Rust globs."""
    turbo_path = Path(f"{REPO}/packages/next-swc/turbo.jsonc")
    data = _parse_jsonc(turbo_path.read_text())
    tasks = data.get("tasks", {})

    # Tasks that should reference the stamp, not raw Rust globs
    refactored_tasks = [
        "build-native",
        "build-native-auto",
        "build-native-release",
        "build-native-release-with-assertions",
        "build-native-no-plugin",
        "build-native-no-plugin-release",
        "build-wasm",
        "build-native-wasi",
        "cache-build-native",
    ]

    for task_name in refactored_tasks:
        if task_name not in tasks:
            continue
        inputs = tasks[task_name].get("inputs", [])
        # Should NOT contain the old duplicated .cargo/** or crates/** globs
        for inp in inputs:
            assert ".cargo/**" not in inp, (
                f"Task {task_name!r} still has old .cargo/** glob in inputs"
            )
        has_old_crates_glob = any(
            "crates/**" in i and "!" not in i for i in inputs
        )
        assert not has_old_crates_glob, (
            f"Task {task_name!r} still has old crates/** glob in inputs: {inputs}"
        )


# [pr_diff] fail_to_pass
def test_sccache_passthrough_env():
    """turbo.json must have SCCACHE_* and RUSTC_WRAPPER in globalPassThroughEnv."""
    turbo_path = Path(f"{REPO}/turbo.json")
    data = json.loads(turbo_path.read_text())

    pass_through = data.get("globalPassThroughEnv", [])
    assert any("SCCACHE" in e for e in pass_through), (
        f"globalPassThroughEnv missing SCCACHE entry: {pass_through}"
    )
    assert "RUSTC_WRAPPER" in pass_through, (
        f"globalPassThroughEnv missing RUSTC_WRAPPER: {pass_through}"
    )


# [pr_diff] fail_to_pass
def test_ci_in_global_env():
    """turbo.json globalEnv must include CI."""
    turbo_path = Path(f"{REPO}/turbo.json")
    data = json.loads(turbo_path.read_text())

    global_env = data.get("globalEnv", [])
    assert "CI" in global_env, (
        f"globalEnv missing CI: {global_env}"
    )


# [pr_diff] fail_to_pass
def test_package_json_fingerprint_script():
    """packages/next-swc/package.json must define a rust-fingerprint script."""
    pkg_path = Path(f"{REPO}/packages/next-swc/package.json")
    data = json.loads(pkg_path.read_text())

    scripts = data.get("scripts", {})
    assert "rust-fingerprint" in scripts, (
        f"rust-fingerprint script not in package.json scripts: {list(scripts.keys())}"
    )
    # The script should invoke the fingerprint JS file
    assert "rust-fingerprint" in scripts["rust-fingerprint"], (
        f"rust-fingerprint script value unexpected: {scripts['rust-fingerprint']}"
    )
