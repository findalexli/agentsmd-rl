"""
Task: opencode-effectify-file-watcher
Repo: anomalyco/opencode @ d4694d058cc590b0f05261a04460034d2fa8541d
PR:   17827

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
PACKAGE = f"{REPO}/packages/opencode"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    # Run TypeScript compiler in noEmit mode to check for syntax/type errors
    r = subprocess.run(
        ["bun", "run", "tsc", "--noEmit", "--skipLibCheck"],
        cwd=PACKAGE,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_filewatcher_service_class_exists():
    """FileWatcherService class must exist with proper Effect Service structure."""
    watcher_ts = Path(f"{PACKAGE}/src/file/watcher.ts").read_text()

    # Must have FileWatcherService class (not just FileWatcher namespace)
    assert "export class FileWatcherService" in watcher_ts, "Missing FileWatcherService class export"

    # Must extend ServiceMap.Service
    assert "extends ServiceMap.Service<FileWatcherService" in watcher_ts, "FileWatcherService must extend ServiceMap.Service"

    # Must have static layer
    assert "static readonly layer" in watcher_ts, "FileWatcherService must have static readonly layer"

    # Must use Layer.effect
    assert "Layer.effect(" in watcher_ts, "FileWatcherService.layer must use Layer.effect"

    # Must use Effect.gen for composition
    assert "Effect.gen(function* ()" in watcher_ts, "FileWatcherService must use Effect.gen"


# [pr_diff] fail_to_pass
def test_filewatcher_uses_instance_context():
    """FileWatcherService must use InstanceContext instead of Instance.* globals."""
    watcher_ts = Path(f"{PACKAGE}/src/file/watcher.ts").read_text()

    # Must import InstanceContext
    assert "InstanceContext" in watcher_ts, "Must import InstanceContext from @/effect/instances"

    # Must yield* InstanceContext (inside Effect.gen)
    assert "yield* InstanceContext" in watcher_ts, "Must use yield* InstanceContext to get instance info"

    # Should NOT directly use Instance.directory or Instance.project inside Effect.gen
    # (This is a soft check - we verify the positive case above)


# [pr_diff] fail_to_pass
def test_filewatcher_uses_effect_finalizer():
    """FileWatcherService must use Effect.addFinalizer for cleanup."""
    watcher_ts = Path(f"{PACKAGE}/src/file/watcher.ts").read_text()

    # Must use Effect.addFinalizer for cleanup
    assert "Effect.addFinalizer" in watcher_ts, "Must use Effect.addFinalizer for subscription cleanup"


# [pr_diff] fail_to_pass
def test_filewatcher_uses_instance_bind():
    """FileWatcherService must use Instance.bind for native callbacks."""
    watcher_ts = Path(f"{PACKAGE}/src/file/watcher.ts").read_text()

    # Must use Instance.bind for the native watcher callback
    assert "Instance.bind(" in watcher_ts, "Must use Instance.bind for native @parcel/watcher callback"


# [pr_diff] fail_to_pass
def test_instances_ts_updated():
    """instances.ts must include FileWatcherService in union and layers."""
    instances_ts = Path(f"{PACKAGE}/src/effect/instances.ts").read_text()

    # Must import FileWatcherService
    assert "FileWatcherService" in instances_ts, "Must import FileWatcherService in instances.ts"

    # Must include in InstanceServices union
    assert "FileWatcherService" in instances_ts.split("InstanceServices")[1], \
        "FileWatcherService must be in InstanceServices union type"

    # Must have Layer.fresh(FileWatcherService.layer)
    assert "Layer.fresh(FileWatcherService.layer)" in instances_ts, \
        "Must add Layer.fresh(FileWatcherService.layer) to lookup()"


# [pr_diff] fail_to_pass
def test_bootstrap_updated():
    """bootstrap.ts must call FileWatcherService via runPromiseInstance."""
    bootstrap_ts = Path(f"{PACKAGE}/src/project/bootstrap.ts").read_text()

    # Must import FileWatcherService
    assert "FileWatcherService" in bootstrap_ts, "Must import FileWatcherService in bootstrap.ts"

    # Must call via runPromiseInstance
    assert "runPromiseInstance(FileWatcherService.use" in bootstrap_ts or \
           "FileWatcherService.use((service) => service.init())" in bootstrap_ts, \
        "Must call FileWatcherService via runPromiseInstance"

    # Must NOT call old FileWatcher.init()
    assert "FileWatcher.init()" not in bootstrap_ts, "Must not call legacy FileWatcher.init()"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression tests using actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """TypeScript type checking passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "run", "typecheck"],
        cwd=PACKAGE,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_file_ignore():
    """File ignore tests pass - file module related (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/file/ignore.test.ts", "--timeout", "30000"],
        cwd=PACKAGE,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, f"File ignore tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_project_state():
    """Project state tests pass - Instance.state related (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/project/state.test.ts", "--timeout", "30000"],
        cwd=PACKAGE,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Project state tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_permission_service():
    """Permission service tests pass - Effect service pattern related (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/permission/next.test.ts", "--timeout", "30000"],
        cwd=PACKAGE,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Permission service tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_effect_zod():
    """Effect-zod integration tests pass - Effect patterns related (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/util/effect-zod.test.ts", "--timeout", "30000"],
        cwd=PACKAGE,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Effect-zod tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_util_timeout():
    """Timeout util tests pass - async utilities related (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/util/timeout.test.ts", "--timeout", "30000"],
        cwd=PACKAGE,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Timeout util tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """FileWatcherService layer has real implementation, not just a stub."""
    watcher_ts = Path(f"{PACKAGE}/src/file/watcher.ts").read_text()

    # Extract the layer content (rough approximation)
    layer_start = watcher_ts.find("static readonly layer")
    assert layer_start != -1, "Must have static layer"

    # The layer should have meaningful content (not just a stub init)
    layer_section = watcher_ts[layer_start:layer_start + 2000]

    # Should have real subscription logic, not just return FileWatcherService.of({ init })
    assert "subscribe" in layer_section, "Layer must have subscription logic"
    assert "Effect.addFinalizer" in layer_section, "Layer must have cleanup logic"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — documentation update checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass - The AGENTS.md update is part of the PR diff
def test_agents_md_documents_instance_services():
    """AGENTS.md must document the Instance-scoped Effect services pattern."""
    agents_md = Path(f"{PACKAGE}/AGENTS.md").read_text()

    # Must have Instance-scoped Effect services section
    assert "Instance-scoped Effect services" in agents_md or \
           "instance-scoped" in agents_md.lower(), \
        "AGENTS.md must document Instance-scoped Effect services pattern"

    # Must mention LayerMap or Instances
    assert "LayerMap" in agents_md or "Instances" in agents_md, \
        "AGENTS.md must mention LayerMap/Instances for service lifecycle"


# [pr_diff] fail_to_pass
def test_agents_md_documents_instance_bind():
    """AGENTS.md must document Instance.bind for native callbacks."""
    agents_md = Path(f"{PACKAGE}/AGENTS.md").read_text()

    # Must have Instance.bind documentation
    assert "Instance.bind" in agents_md, \
        "AGENTS.md must document Instance.bind pattern for native callbacks"

    # Must explain when to use it (native addons)
    assert "native" in agents_md.lower() or "callback" in agents_md.lower(), \
        "AGENTS.md must explain Instance.bind is for native/C++ callbacks"


# [pr_diff] fail_to_pass
def test_agents_md_documents_effect_callback():
    """AGENTS.md must document Effect.callback pattern."""
    agents_md = Path(f"{PACKAGE}/AGENTS.md").read_text()

    # Must mention Effect.callback (not just Effect.async)
    assert "Effect.callback" in agents_md, \
        "AGENTS.md must document Effect.callback for async operations"


# [agent_config] pass_to_pass - AGENTS.md:37 @ base_commit
def test_no_wildcard_imports():
    """Code should not use wildcard imports (per AGENTS.md Effect guide)."""
    watcher_ts = Path(f"{PACKAGE}/src/file/watcher.ts").read_text()

    # No wildcard imports
    assert "* from" not in watcher_ts, "Should not use wildcard imports"
    assert "* as " not in watcher_ts or "import * as" in watcher_ts, "Check import style"


# [agent_config] pass_to_pass - AGENTS.md:30 @ base_commit
def test_uses_effect_gen():
    """Service uses Effect.gen for composition (per AGENTS.md)."""
    watcher_ts = Path(f"{PACKAGE}/src/file/watcher.ts").read_text()

    # Must use Effect.gen not just Promise chains
    assert "Effect.gen(function* ()" in watcher_ts, "Must use Effect.gen for composition"
