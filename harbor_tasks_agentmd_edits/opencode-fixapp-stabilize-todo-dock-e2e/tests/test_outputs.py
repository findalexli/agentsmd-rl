"""
Task: opencode-fixapp-stabilize-todo-dock-e2e
Repo: anomalyco/opencode @ dcb17c6a678918ce0786640729fcc8cd8adb1746
PR:   17267

Stabilize flaky todo dock e2e tests by adding a composer driver/probe module,
integrating it into the compositor state and todo dock components, and
documenting state-first e2e testing rules in packages/app/e2e/AGENTS.md.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp .mjs script and run it with node."""
    script_path = Path(REPO) / "_eval_tmp.mjs"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ts_syntax():
    """Modified TypeScript files exist and are structurally valid."""
    files = [
        "packages/app/src/pages/session/composer/session-composer-region.tsx",
        "packages/app/src/pages/session/composer/session-composer-state.ts",
        "packages/app/src/pages/session/composer/session-todo-dock.tsx",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 200, f"{f} is unexpectedly short"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_composer_module_runtime():
    """Import session-composer module in Node and verify exports work correctly."""
    r = _run_node("""
const mod = await import('./packages/app/src/testing/session-composer.ts');

// Verify composerEvent constant
if (mod.composerEvent !== "opencode:e2e:composer")
    throw new Error("composerEvent has wrong value: " + mod.composerEvent);

// Verify composerEnabled returns false without window
if (mod.composerEnabled() !== false)
    throw new Error("composerEnabled() should return false in Node (no window)");

// Verify composerDriver returns undefined without window
const driver = mod.composerDriver("test-session");
if (driver !== undefined)
    throw new Error("composerDriver should return undefined without window");

// Verify composerProbe returns object with set and drop methods
const probe = mod.composerProbe("test-session");
if (typeof probe.set !== "function")
    throw new Error("composerProbe must return object with set method");
if (typeof probe.drop !== "function")
    throw new Error("composerProbe must return object with drop method");

// Verify set/drop are safe no-ops without window
probe.set({ mounted: true, collapsed: false, hidden: false, count: 1, states: ["pending"] });
probe.drop();

console.log(JSON.stringify({
    event: mod.composerEvent,
    enabled: mod.composerEnabled(),
    driverUndefined: driver === undefined,
    probeHasSet: typeof probe.set === "function",
    probeHasDrop: typeof probe.drop === "function",
}));
""")
    assert r.returncode == 0, f"Module runtime test failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["event"] == "opencode:e2e:composer"
    assert data["enabled"] is False
    assert data["driverUndefined"] is True
    assert data["probeHasSet"] is True
    assert data["probeHasDrop"] is True


# [pr_diff] fail_to_pass
def test_state_integrates_driver():
    """session-composer-state.ts imports composerDriver, composerEnabled, composerEvent."""
    content = Path(
        f"{REPO}/packages/app/src/pages/session/composer/session-composer-state.ts"
    ).read_text()
    assert "composerDriver" in content, "Must import composerDriver"
    assert "composerEnabled" in content, "Must import composerEnabled"
    assert "composerEvent" in content, "Must import composerEvent"
    assert "testing/session-composer" in content, \
        "Must import from the session-composer testing module"


# [pr_diff] fail_to_pass
def test_todo_dock_accepts_session_id():
    """SessionTodoDock component accepts a sessionID prop."""
    content = Path(
        f"{REPO}/packages/app/src/pages/session/composer/session-todo-dock.tsx"
    ).read_text()
    assert "sessionID" in content, "SessionTodoDock must accept sessionID prop"
    assert "sessionID?" in content or "sessionID:" in content, \
        "sessionID must be declared in the component props type"


# [pr_diff] fail_to_pass
def test_todo_dock_uses_probe():
    """session-todo-dock.tsx imports and uses composerProbe from testing module."""
    content = Path(
        f"{REPO}/packages/app/src/pages/session/composer/session-todo-dock.tsx"
    ).read_text()
    assert "composerProbe" in content, "Must import composerProbe"
    assert "composerEnabled" in content, "Must import composerEnabled"
    assert "testing/session-composer" in content, \
        "Must import from session-composer testing module"


# [pr_diff] fail_to_pass
def test_region_passes_session_id():
    """session-composer-region.tsx passes sessionID prop to SessionTodoDock."""
    content = Path(
        f"{REPO}/packages/app/src/pages/session/composer/session-composer-region.tsx"
    ).read_text()
    assert "sessionID=" in content or "sessionID =" in content, \
        "Must pass sessionID prop to SessionTodoDock"
    assert "params.id" in content, \
        "sessionID should come from route params"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_wait_on_state():
    """AGENTS.md documents wait-on-state rules for e2e tests."""
    content = Path(f"{REPO}/packages/app/e2e/AGENTS.md").read_text()
    lower = content.lower()
    assert "wall-clock" in lower, \
        "AGENTS.md must warn against wall-clock waits"
    assert "observable state" in lower or "expect.poll" in content, \
        "Must recommend polling on observable state or using expect.poll"


# [pr_diff] fail_to_pass
def test_agents_md_add_hooks():
    """AGENTS.md documents rules for adding test-only hooks/probes."""
    content = Path(f"{REPO}/packages/app/e2e/AGENTS.md").read_text()
    lower = content.lower()
    assert "probe" in lower or "driver" in lower, \
        "AGENTS.md must document adding test-only probes or drivers"
    assert "inert" in lower, \
        "Must specify test hooks are inert unless enabled"


# [pr_diff] fail_to_pass
def test_agents_md_prefer_helpers():
    """AGENTS.md documents preference for fluent helpers in e2e tests."""
    content = Path(f"{REPO}/packages/app/e2e/AGENTS.md").read_text()
    lower = content.lower()
    assert "fluent" in lower, \
        "Must recommend fluent helpers"
    assert "intent" in lower or "clarity" in lower, \
        "Must explain when helpers improve clarity or make intent obvious"
