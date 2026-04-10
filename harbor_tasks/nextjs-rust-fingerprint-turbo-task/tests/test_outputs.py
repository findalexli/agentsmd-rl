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
    """Strip // comments and trailing commas from JSONC, then parse as JSON.

    Only removes // comments that are preceded by whitespace (to avoid
    matching URLs like https://...).
    """
    # Remove // comments only when preceded by whitespace or start of line
    text = re.sub(r"(^|\s)//.*$", "", text, flags=re.MULTILINE)
    # Remove trailing commas before } or ]
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) - syntax / compilation checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_turbo_json_valid_syntax():
    """turbo.json must parse as valid JSON via Python json.tool."""
    turbo_path = Path(f"{REPO}/turbo.json")
    assert turbo_path.exists(), "turbo.json does not exist"

    # Use subprocess to validate JSON (real CI command pattern)
    r = subprocess.run(
        ["python3", "-m", "json.tool", str(turbo_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"turbo.json is not valid JSON:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_turbo_jsonc_valid_syntax():
    """packages/next-swc/turbo.jsonc must parse as valid JSONC."""
    # Use Python to validate JSONC (strip comments, trailing commas, then parse)
    # This is equivalent to what the CI would do when reading the config
    turbo_path = Path(f"{REPO}/packages/next-swc/turbo.jsonc")
    assert turbo_path.exists(), "turbo.jsonc does not exist"

    # Use subprocess with Python script for true command execution
    script = """
import re
import json
import sys

with open(sys.argv[1], "r") as f:
    content = f.read()

# Remove // comments (only when preceded by whitespace or start of line)
content = re.sub(r\"(^|\\s)//.*$\", \"\", content, flags=re.MULTILINE)
# Remove trailing commas before } or ]
content = re.sub(r\",(\\s*[}\\]])\", r\"\\1\", content)

try:
    data = json.loads(content)
    if \"tasks\" not in data:
        print(\"Missing tasks key\", file=sys.stderr)
        sys.exit(1)
    print(\"OK\")
except json.JSONDecodeError as e:
    print(f\"Parse error: {e}\", file=sys.stderr)
    sys.exit(1)
"""
    r = subprocess.run(
        ["python3", "-c", script, str(turbo_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"turbo.jsonc is not valid JSONC:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_next_swc_package_json_valid():
    """packages/next-swc/package.json must be valid JSON with required scripts via node."""
    pkg_path = Path(f"{REPO}/packages/next-swc/package.json")
    assert pkg_path.exists(), "package.json does not exist"

    # Use node subprocess to validate and check required fields
    node_script = """
const fs = require(\"fs\");
const file = process.argv[1];
const data = JSON.parse(fs.readFileSync(file, \"utf8\"));
const scripts = data.scripts || {};
const required = [\"build-native\", \"rust-check-fmt\"];
const missing = required.filter(s => !scripts[s]);
if (missing.length > 0) {
    console.error(\"Missing scripts:\", missing.join(\" \"));
    process.exit(1);
}
console.log(\"OK\");
"""
    r = subprocess.run(
        ["node", "-e", node_script, str(pkg_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"package.json validation failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_root_package_json_valid():
    """package.json must be valid JSON with required scripts."""
    pkg_path = Path(f"{REPO}/package.json")
    assert pkg_path.exists(), "package.json does not exist"

    # Use node subprocess to validate
    node_script = """
const fs = require(\"fs\");
const file = process.argv[1];
const data = JSON.parse(fs.readFileSync(file, \"utf8\"));
const scripts = data.scripts || {};
const required = [\"build\", \"lint\"];
const missing = required.filter(s => !scripts[s]);
if (missing.length > 0) {
    console.error(\"Missing scripts:\", missing.join(\" \"));
    process.exit(1);
}
console.log(\"OK\");
"""
    r = subprocess.run(
        ["node", "-e", node_script, str(pkg_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"package.json validation failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_rust_fingerprint_script_valid():
    """scripts/rust-fingerprint.js must have valid Node.js syntax."""
    script_path = Path(f"{REPO}/scripts/rust-fingerprint.js")
    assert script_path.exists(), "scripts/rust-fingerprint.js does not exist"

    # Use node --check to validate syntax (same as node --check in CI)
    r = subprocess.run(
        ["node", "--check", str(script_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"rust-fingerprint.js has syntax errors:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
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
    stdout_text = r.stdout.decode()
    assert "skipping" in stdout_text.lower(), (
        f"Expected skipping message, got: {stdout_text}"
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
    script_value = scripts["rust-fingerprint"]
    assert "rust-fingerprint" in script_value, (
        f"rust-fingerprint script value unexpected: {script_value}"
    )
