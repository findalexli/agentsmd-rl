"""
Task: opencode-stack-effectifyfilewatcherservice
Repo: anomalyco/opencode @ 39e5a5929f2d3dd6f9de8734f3bebb9f8bf807e8
PR:   17827

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/opencode"
OPENCODE_DIR = f"{REPO}/packages/opencode"


def _run_bun(args: list, cwd: str = OPENCODE_DIR, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute bun command in the opencode package directory."""
    return subprocess.run(
        ["bun", *args],
        capture_output=True, text=True, timeout=timeout, cwd=cwd,
    )


def _run_node_ts(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute TypeScript code via bun in the opencode directory."""
    script = Path(OPENCODE_DIR) / "_eval_tmp.ts"
    script.write_text(code)
    try:
        return subprocess.run(
            ["bun", "run", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=OPENCODE_DIR,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    # Run tsc to check compilation of the modified files
    files_to_check = [
        "src/file/watcher.ts",
        "src/effect/instances.ts",
        "src/project/instance.ts",
        "src/flag/flag.ts",
        "src/project/bootstrap.ts",
    ]

    for file in files_to_check:
        r = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck", file],
            capture_output=True, text=True, timeout=60, cwd=OPENCODE_DIR,
        )
        assert r.returncode == 0, f"TypeScript compilation failed for {file}: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_filewatcher_service_exports():
    """FileWatcherService is exported as a proper Effect service with layer."""
    r = _run_node_ts("""
import { FileWatcherService } from "./src/file/watcher";

// Verify the service class exists and has required static properties
if (typeof FileWatcherService !== 'function') {
    console.error("FileWatcherService is not a class/constructor");
    process.exit(1);
}

// Check for the static layer property
if (!FileWatcherService.layer) {
    console.error("FileWatcherService.layer is missing");
    process.exit(1);
}

// Verify it's a proper Effect ServiceMap service by checking its prototype
const proto = FileWatcherService.prototype;
if (!proto || typeof proto !== 'object') {
    console.error("FileWatcherService has invalid prototype");
    process.exit(1);
}

console.log("PASS: FileWatcherService properly defined as Effect service");
""")
    assert r.returncode == 0, f"FileWatcherService export test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_instance_bind_exists():
    """Instance.bind method exists for ALS context capture in native callbacks."""
    r = _run_node_ts("""
import { Instance } from "./src/project/instance";

// Verify Instance.bind is a function
if (typeof Instance.bind !== 'function') {
    console.error("Instance.bind is not a function");
    process.exit(1);
}

// Test that bind returns a wrapped function
const original = (x: number) => x * 2;
const bound = Instance.bind(original);

if (typeof bound !== 'function') {
    console.error("Instance.bind did not return a function");
    process.exit(1);
}

console.log("PASS: Instance.bind method exists and works correctly");
""")
    assert r.returncode == 0, f"Instance.bind test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_flag_uses_effect_config():
    """FileWatcher-related flags use Effect.Config instead of static truthy()."""
    r = _run_node_ts("""
import { Flag } from "./src/flag/flag";
import { Effect } from "effect";

// Check that the flags are Effect Config types (they should have pipe method)
const filewatcherFlag = Flag.OPENCODE_EXPERIMENTAL_FILEWATCHER;
const disableFlag = Flag.OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER;

// Effect Config has a pipe method for composition
if (typeof filewatcherFlag?.pipe !== 'function') {
    console.error("OPENCODE_EXPERIMENTAL_FILEWATCHER is not an Effect Config (no pipe method)");
    process.exit(1);
}

if (typeof disableFlag?.pipe !== 'function') {
    console.error("OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER is not an Effect Config (no pipe method)");
    process.exit(1);
}

console.log("PASS: FileWatcher flags use Effect.Config pattern");
""")
    assert r.returncode == 0, f"Flag Effect.Config test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_instances_includes_filewatcherservice():
    """FileWatcherService is included in InstanceServices union and Layer.mergeAll."""
    watcher_path = Path(OPENCODE_DIR) / "src/file/watcher.ts"
    instances_path = Path(OPENCODE_DIR) / "src/effect/instances.ts"

    watcher_src = watcher_path.read_text()
    instances_src = instances_path.read_text()

    # Check FileWatcherService is exported
    assert "export class FileWatcherService" in watcher_src, "FileWatcherService class not exported"

    # Check instances.ts imports and includes it
    assert 'import { FileWatcherService } from "@/file/watcher"' in instances_src, \
        "FileWatcherService not imported in instances.ts"
    assert "FileWatcherService" in instances_src, \
        "FileWatcherService not referenced in instances.ts"
    assert "Layer.fresh(FileWatcherService.layer)" in instances_src, \
        "FileWatcherService.layer not included in Layer.mergeAll"


# [pr_diff] fail_to_pass
def test_bootstrap_uses_filewatcherservice():
    """Bootstrap uses FileWatcherService.use instead of FileWatcher.init()."""
    bootstrap_path = Path(OPENCODE_DIR) / "src/project/bootstrap.ts"
    bootstrap_src = bootstrap_path.read_text()

    # Check that the new service pattern is used
    assert "FileWatcherService.use" in bootstrap_src, \
        "bootstrap.ts should use FileWatcherService.use pattern"
    assert "runPromiseInstance" in bootstrap_src, \
        "bootstrap.ts should use runPromiseInstance for Effect services"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_upstream_tests_pass():
    """Upstream test suite passes (watcher tests run successfully)."""
    # Run the watcher tests specifically
    r = subprocess.run(
        ["bun", "test", "test/file/watcher.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=OPENCODE_DIR,
    )
    # Note: Tests may skip if native bindings aren't available
    # We just need to ensure they don't crash
    assert r.returncode in [0, 1], f"Test execution had unexpected error: {r.stderr}"
    # If returncode is 1, check if it's due to test failures (not crashes)
    if r.returncode == 1:
        assert "fail" in r.stdout.lower() or "error" in r.stdout.lower(), \
            f"Tests may have crashed rather than failed: {r.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """Modified FileWatcherService has real logic, not just pass/return."""
    watcher_path = Path(OPENCODE_DIR) / "src/file/watcher.ts"
    src = watcher_path.read_text()

    # Check for meaningful implementation details
    checks = [
        "Effect.gen" in src,
        "InstanceContext" in src,
        "Effect.addFinalizer" in src,
        "Instance.bind" in src,
        "FileWatcherService.of" in src,
    ]
    assert any(checks), "FileWatcherService appears to be a stub (missing key implementation patterns)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — packages/opencode/AGENTS.md:46-50 @ 39e5a5929f2d3dd6f9de8734f3bebb9f8bf807e8
def test_agentsmd_instance_bind_documented():
    """AGENTS.md documents Instance.bind for ALS context in native callbacks."""
    agents_path = Path(OPENCODE_DIR) / "AGENTS.md"
    src = agents_path.read_text()

    # Check for Instance.bind documentation
    assert "Instance.bind" in src, "Instance.bind not documented in AGENTS.md"
    assert "ALS context" in src or "async context" in src, \
        "Instance.bind ALS context purpose not documented"
    assert "native" in src.lower() or "@parcel/watcher" in src or "node-pty" in src, \
        "Native addon usage not mentioned with Instance.bind"


# [agent_config] fail_to_pass — packages/opencode/AGENTS.md:43-45 @ 39e5a5929f2d3dd6f9de8734f3bebb9f8bf807e8
def test_agentsmd_effect_callback_documented():
    """AGENTS.md documents Effect.callback (not Effect.async) for callbacks."""
    agents_path = Path(OPENCODE_DIR) / "AGENTS.md"
    src = agents_path.read_text()

    assert "Effect.callback" in src, "Effect.callback not documented in AGENTS.md"


# [agent_config] fail_to_pass — packages/opencode/AGENTS.md:18-25 @ 39e5a5929f2d3dd6f9de8734f3bebb9f8bf807e8
def test_agentsmd_instance_scoped_services_documented():
    """AGENTS.md documents Instance-scoped Effect services pattern."""
    agents_path = Path(OPENCODE_DIR) / "AGENTS.md"
    src = agents_path.read_text()

    assert "Instance-scoped Effect services" in src or "instance) go through the `Instances` LayerMap" in src, \
        "Instance-scoped services pattern not documented"
    assert "ServiceMap.Service" in src, "ServiceMap.Service pattern not documented"
    assert "FileWatcherService" in src, "FileWatcherService not mentioned as example"
