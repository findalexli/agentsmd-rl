"""Behavioral tests for the opencode composer e2e probe/driver utility."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/opencode")
MODULE = REPO / "packages/app/src/testing/session-composer.ts"
STATE_FILE = REPO / "packages/app/src/pages/session/composer/session-composer-state.ts"
DOCK_FILE = REPO / "packages/app/src/pages/session/composer/session-todo-dock.tsx"
REGION_FILE = REPO / "packages/app/src/pages/session/composer/session-composer-region.tsx"
SPEC_FILE = REPO / "packages/app/e2e/session/session-composer-dock.spec.ts"
AGENTS_FILE = REPO / "packages/app/e2e/AGENTS.md"


def run_bun(snippet: str, *, timeout: int = 30) -> str:
    """Execute a bun TypeScript snippet and return its stdout (stripped).

    The snippet may import the new module via the absolute path
    /workspace/opencode/packages/app/src/testing/session-composer.ts.
    """
    r = subprocess.run(
        ["bun", "-e", snippet],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
    )
    if r.returncode != 0:
        raise AssertionError(
            f"bun snippet failed (exit {r.returncode}):\n"
            f"--- stdout ---\n{r.stdout}\n--- stderr ---\n{r.stderr}"
        )
    return r.stdout.strip()


# ---------------------------------------------------------------------------
# Module-level behavior: composer-event constant
# ---------------------------------------------------------------------------


def test_module_file_exists():
    """The new test-only module is at packages/app/src/testing/session-composer.ts."""
    assert MODULE.is_file(), f"missing module file: {MODULE}"


def test_composer_event_constant():
    """composerEvent must be the literal 'opencode:e2e:composer'."""
    out = run_bun(
        f"""
const m = await import("{MODULE}")
console.log(JSON.stringify({{ event: m.composerEvent, t: typeof m.composerEvent }}))
"""
    )
    data = json.loads(out)
    assert data == {"event": "opencode:e2e:composer", "t": "string"}, data


# ---------------------------------------------------------------------------
# composerEnabled() behavior
# ---------------------------------------------------------------------------


def test_enabled_returns_false_without_window():
    """composerEnabled() returns false when window is undefined."""
    out = run_bun(
        f"""
// Bun's default global has no `window`; ensure it stays undefined.
delete (globalThis as any).window
const m = await import("{MODULE}")
console.log(JSON.stringify({{ enabled: m.composerEnabled() }}))
"""
    )
    assert json.loads(out) == {"enabled": False}


def test_enabled_returns_false_when_flag_missing():
    """composerEnabled() returns false when the namespace exists but enabled is missing."""
    out = run_bun(
        f"""
;(globalThis as any).window = {{ __opencode_e2e: {{ composer: {{}} }} }}
const m = await import("{MODULE}")
console.log(JSON.stringify({{ enabled: m.composerEnabled() }}))
"""
    )
    assert json.loads(out) == {"enabled": False}


def test_enabled_returns_false_when_flag_falsy():
    """composerEnabled() must require strict-true; falsy values do not count."""
    out = run_bun(
        f"""
const results: Record<string, boolean> = {{}}
const m = await import("{MODULE}")
;(globalThis as any).window = {{ __opencode_e2e: {{ composer: {{ enabled: false }} }} }}
results.boolFalse = m.composerEnabled()
;(globalThis as any).window = {{ __opencode_e2e: {{ composer: {{ enabled: 0 }} }} }}
results.zero = m.composerEnabled()
;(globalThis as any).window = {{ __opencode_e2e: {{ composer: {{ enabled: "true" }} }} }}
results.stringTrue = m.composerEnabled()
;(globalThis as any).window = {{ __opencode_e2e: {{ composer: {{ enabled: 1 }} }} }}
results.numericOne = m.composerEnabled()
console.log(JSON.stringify(results))
"""
    )
    data = json.loads(out)
    assert data == {
        "boolFalse": False,
        "zero": False,
        "stringTrue": False,
        "numericOne": False,
    }, data


def test_enabled_returns_true_when_flag_true():
    """composerEnabled() returns true when window.__opencode_e2e.composer.enabled === true."""
    out = run_bun(
        f"""
;(globalThis as any).window = {{ __opencode_e2e: {{ composer: {{ enabled: true }} }} }}
const m = await import("{MODULE}")
console.log(JSON.stringify({{ enabled: m.composerEnabled() }}))
"""
    )
    assert json.loads(out) == {"enabled": True}


# ---------------------------------------------------------------------------
# composerDriver() behavior
# ---------------------------------------------------------------------------


def test_driver_undefined_when_no_session_id():
    """composerDriver() with no sessionID returns undefined."""
    out = run_bun(
        f"""
;(globalThis as any).window = {{ __opencode_e2e: {{ composer: {{ enabled: true, sessions: {{
  s1: {{ driver: {{ live: true, todos: [] }} }}
}} }} }} }}
const m = await import("{MODULE}")
console.log(JSON.stringify({{ result: m.composerDriver() === undefined }}))
"""
    )
    assert json.loads(out) == {"result": True}


def test_driver_undefined_when_disabled():
    """composerDriver() returns undefined when composerEnabled() is false."""
    out = run_bun(
        f"""
;(globalThis as any).window = {{ __opencode_e2e: {{ composer: {{ enabled: false, sessions: {{
  s1: {{ driver: {{ live: true, todos: [] }} }}
}} }} }} }}
const m = await import("{MODULE}")
console.log(JSON.stringify({{ result: m.composerDriver("s1") === undefined }}))
"""
    )
    assert json.loads(out) == {"result": True}


def test_driver_undefined_when_no_driver_set():
    """composerDriver(id) returns undefined when no driver has been set for that session."""
    out = run_bun(
        f"""
;(globalThis as any).window = {{ __opencode_e2e: {{ composer: {{ enabled: true, sessions: {{ s1: {{}} }} }} }} }}
const m = await import("{MODULE}")
console.log(JSON.stringify({{ result: m.composerDriver("s1") === undefined }}))
"""
    )
    assert json.loads(out) == {"result": True}


def test_driver_returns_clone_of_state():
    """composerDriver(id) returns a fresh object with cloned todo entries."""
    out = run_bun(
        f"""
const todos = [
  {{ content: "first", status: "pending", priority: "high" }},
  {{ content: "second", status: "in_progress", priority: "medium" }},
]
const driver = {{ live: true, todos }}
;(globalThis as any).window = {{
  __opencode_e2e: {{
    composer: {{
      enabled: true,
      sessions: {{ s1: {{ driver }} }},
    }},
  }},
}}
const m = await import("{MODULE}")
const got = m.composerDriver("s1")
console.log(JSON.stringify({{
  shape: got,
  isCloneObj: got !== driver,
  isCloneArr: got.todos !== todos,
  itemsCloned: got.todos.every((t: any, i: number) => t !== todos[i]),
}}))
"""
    )
    data = json.loads(out)
    assert data["shape"] == {
        "live": True,
        "todos": [
            {"content": "first", "status": "pending", "priority": "high"},
            {"content": "second", "status": "in_progress", "priority": "medium"},
        ],
    }, data["shape"]
    assert data["isCloneObj"] is True
    assert data["isCloneArr"] is True
    assert data["itemsCloned"] is True


def test_driver_clone_isolates_caller_mutation():
    """Mutating the returned driver value must not affect the underlying state."""
    out = run_bun(
        f"""
const todos = [{{ content: "a", status: "pending", priority: "low" }}]
const driver = {{ live: false, todos }}
;(globalThis as any).window = {{
  __opencode_e2e: {{ composer: {{ enabled: true, sessions: {{ s1: {{ driver }} }} }} }},
}}
const m = await import("{MODULE}")
const got = m.composerDriver("s1")!
got.todos!.push({{ content: "x", status: "completed", priority: "high" }})
got.todos![0].content = "changed"
console.log(JSON.stringify({{
  underlyingLen: todos.length,
  underlyingFirst: todos[0].content,
}}))
"""
    )
    assert json.loads(out) == {"underlyingLen": 1, "underlyingFirst": "a"}


def test_driver_handles_missing_todos_field():
    """A driver state without todos should still return cleanly with todos undefined."""
    out = run_bun(
        f"""
;(globalThis as any).window = {{
  __opencode_e2e: {{ composer: {{ enabled: true, sessions: {{ s1: {{ driver: {{ live: true }} }} }} }} }},
}}
const m = await import("{MODULE}")
const got = m.composerDriver("s1")
console.log(JSON.stringify({{ live: got?.live, todosUndefined: got?.todos === undefined }}))
"""
    )
    assert json.loads(out) == {"live": True, "todosUndefined": True}


# ---------------------------------------------------------------------------
# composerProbe() behavior
# ---------------------------------------------------------------------------


def test_probe_set_writes_state():
    """composerProbe(id).set(s) writes s under window.__opencode_e2e.composer.sessions[id].probe."""
    out = run_bun(
        f"""
const win: any = {{ __opencode_e2e: {{ composer: {{ enabled: true, sessions: {{}} }} }} }}
;(globalThis as any).window = win
const m = await import("{MODULE}")
m.composerProbe("s1").set({{
  mounted: true,
  collapsed: false,
  hidden: false,
  count: 2,
  states: ["pending", "in_progress"],
}})
console.log(JSON.stringify(win.__opencode_e2e.composer.sessions.s1.probe))
"""
    )
    assert json.loads(out) == {
        "mounted": True,
        "collapsed": False,
        "hidden": False,
        "count": 2,
        "states": ["pending", "in_progress"],
    }


def test_probe_set_clones_states_array():
    """composerProbe(id).set(s) must clone s.states; mutating the original must not affect the stored probe."""
    out = run_bun(
        f"""
const win: any = {{ __opencode_e2e: {{ composer: {{ enabled: true, sessions: {{}} }} }} }}
;(globalThis as any).window = win
const m = await import("{MODULE}")
const states = ["pending", "in_progress"]
m.composerProbe("s1").set({{
  mounted: true, collapsed: false, hidden: false, count: 2, states,
}})
states.push("completed")
states[0] = "cancelled"
console.log(JSON.stringify(win.__opencode_e2e.composer.sessions.s1.probe.states))
"""
    )
    # If states array were not cloned, the stored value would be ["cancelled", "in_progress", "completed"]
    assert json.loads(out) == ["pending", "in_progress"]


def test_probe_set_preserves_existing_driver():
    """Setting probe must NOT erase a previously-set driver for the same session."""
    out = run_bun(
        f"""
const win: any = {{ __opencode_e2e: {{ composer: {{
  enabled: true,
  sessions: {{ s1: {{ driver: {{ live: true, todos: [{{ content: "x", status: "pending", priority: "low" }}] }} }} }},
}} }} }}
;(globalThis as any).window = win
const m = await import("{MODULE}")
m.composerProbe("s1").set({{
  mounted: true, collapsed: false, hidden: false, count: 0, states: [],
}})
const cell = win.__opencode_e2e.composer.sessions.s1
console.log(JSON.stringify({{
  hasDriver: cell.driver?.live === true,
  driverTodoLen: cell.driver?.todos?.length ?? -1,
  hasProbe: cell.probe?.mounted === true,
}}))
"""
    )
    assert json.loads(out) == {"hasDriver": True, "driverTodoLen": 1, "hasProbe": True}


def test_probe_set_no_op_without_session_id():
    """composerProbe() with no sessionID — calling .set must not throw and not write anything."""
    out = run_bun(
        f"""
const win: any = {{ __opencode_e2e: {{ composer: {{ enabled: true, sessions: {{}} }} }} }}
;(globalThis as any).window = win
const m = await import("{MODULE}")
m.composerProbe().set({{
  mounted: true, collapsed: false, hidden: false, count: 0, states: [],
}})
console.log(JSON.stringify({{ keys: Object.keys(win.__opencode_e2e.composer.sessions) }}))
"""
    )
    assert json.loads(out) == {"keys": []}


def test_probe_set_no_op_when_disabled():
    """composerProbe(id).set must be a no-op when composerEnabled() is false."""
    out = run_bun(
        f"""
const win: any = {{ __opencode_e2e: {{ composer: {{ enabled: false, sessions: {{}} }} }} }}
;(globalThis as any).window = win
const m = await import("{MODULE}")
m.composerProbe("s1").set({{
  mounted: true, collapsed: false, hidden: false, count: 0, states: [],
}})
console.log(JSON.stringify({{ keys: Object.keys(win.__opencode_e2e.composer.sessions) }}))
"""
    )
    assert json.loads(out) == {"keys": []}


def test_probe_drop_writes_unmounted_state():
    """drop() writes mounted=false, hidden=true, count=0, empty states."""
    out = run_bun(
        f"""
const win: any = {{ __opencode_e2e: {{ composer: {{ enabled: true, sessions: {{}} }} }} }}
;(globalThis as any).window = win
const m = await import("{MODULE}")
const probe = m.composerProbe("s1")
probe.set({{ mounted: true, collapsed: true, hidden: false, count: 3, states: ["a","b","c"] }})
probe.drop()
console.log(JSON.stringify(win.__opencode_e2e.composer.sessions.s1.probe))
"""
    )
    assert json.loads(out) == {
        "mounted": False,
        "collapsed": False,
        "hidden": True,
        "count": 0,
        "states": [],
    }


# ---------------------------------------------------------------------------
# Integration: the composer state and todo dock plug into the new module.
# ---------------------------------------------------------------------------
#
# These check that the integration files actually consume the new symbols, by
# parsing them with bun (which reports SyntaxError on a malformed file) and by
# verifying the import edges. We can't render SolidJS without the full
# workspace install, but the integration files unambiguously must import the
# new symbols for the e2e flow to work end-to-end.


def test_state_file_imports_driver_and_event():
    """session-composer-state.ts must import composerDriver, composerEnabled, and composerEvent."""
    text = STATE_FILE.read_text()
    # A specific import line from the new testing module.
    pattern = re.compile(
        r'from\s+["\']@/testing/session-composer["\']'
    )
    assert pattern.search(text), "session-composer-state.ts is not importing from @/testing/session-composer"
    for sym in ("composerDriver", "composerEnabled", "composerEvent"):
        assert sym in text, f"session-composer-state.ts must reference {sym}"


def test_state_file_uses_event_listener():
    """state file must subscribe to the composerEvent CustomEvent on window."""
    text = STATE_FILE.read_text()
    assert "addEventListener" in text and "composerEvent" in text, (
        "state file must register a window event listener for composerEvent"
    )
    assert "removeEventListener" in text, "state file must remove its listener on cleanup"


def test_state_file_uses_create_store_for_driver_state():
    """SolidJS guidance: prefer createStore over multiple createSignal for related state.

    Base state file already uses createStore once (for the responding/closing/etc.
    store). After adding the driver overlay, there must be at least one MORE
    createStore call body, since the overlay groups related signals (`on`,
    `live`, `todos`).
    """
    text = STATE_FILE.read_text()
    # Count createStore call sites (excluding the import line).
    call_sites = re.findall(r"\bcreateStore\s*\(", text)
    assert len(call_sites) >= 2, (
        f"state file must use createStore for the driver overlay too; "
        f"found {len(call_sites)} call site(s) — gold has 2."
    )


def test_dock_file_imports_probe():
    """session-todo-dock.tsx must import composerProbe and composerEnabled."""
    text = DOCK_FILE.read_text()
    pattern = re.compile(r'from\s+["\']@/testing/session-composer["\']')
    assert pattern.search(text), "session-todo-dock.tsx must import from @/testing/session-composer"
    for sym in ("composerEnabled", "composerProbe"):
        assert sym in text, f"session-todo-dock.tsx must reference {sym}"


def test_dock_file_accepts_session_id_prop():
    """The dock component must accept an optional sessionID prop."""
    text = DOCK_FILE.read_text()
    # Look for sessionID typed as string-or-undefined in the props block.
    assert re.search(r"sessionID\??\s*:\s*string", text), (
        "session-todo-dock.tsx must declare a sessionID prop"
    )


def test_region_passes_session_id_to_dock():
    """session-composer-region.tsx must wire route.params.id into <SessionTodoDock sessionID={...} />."""
    text = REGION_FILE.read_text()
    assert "sessionID" in text, "region must pass sessionID to SessionTodoDock"


# ---------------------------------------------------------------------------
# Spec rewrite + AGENTS.md doc updates (the test-driver / new rules pieces).
# ---------------------------------------------------------------------------


def test_spec_imports_composer_event():
    """The rewritten spec must import composerEvent from the new module."""
    text = SPEC_FILE.read_text()
    assert "composerEvent" in text, "spec must reference composerEvent"
    assert "src/testing/session-composer" in text, (
        "spec must import from ../../src/testing/session-composer"
    )


def test_spec_drops_seedSessionTodos_import():
    """The rewritten spec no longer pulls in seedSessionTodos / sessionTodoListSelector."""
    text = SPEC_FILE.read_text()
    # seedSessionTodos was the backend-driven seed used by the flaky version.
    # After the rewrite, the dock test drives via the probe instead.
    bad_imports = re.findall(
        r"^import\s+\{[^}]*\b(seedSessionTodos|sessionTodoDockSelector|sessionTodoListSelector)\b[^}]*\}\s+from\b",
        text,
        flags=re.MULTILINE,
    )
    assert not bad_imports, (
        f"spec still imports stale helpers: {bad_imports} — replace them with probe-based assertions"
    )


def test_spec_uses_probe_to_match_object():
    """The new spec uses expect.poll(...).toMatchObject({ mounted, ... }) on the probe."""
    text = SPEC_FILE.read_text()
    assert "toMatchObject" in text, "spec must assert on probe state via toMatchObject"
    assert "mounted" in text and "states" in text, (
        "spec must inspect probe fields mounted/states"
    )


def test_e2e_agents_doc_has_state_first_section():
    """AGENTS.md must document the new state-first pattern with the three new headings."""
    text = AGENTS_FILE.read_text()
    for heading in ("### Wait on state", "### Add hooks", "### Prefer helpers"):
        assert heading in text, f"AGENTS.md missing '{heading}' subsection"


# ---------------------------------------------------------------------------
# Pass-to-pass: stable repo-state checks unaffected by the patch.
# ---------------------------------------------------------------------------


def test_p2p_repo_root_package_json():
    """Sanity: the bun monorepo root has the expected packageManager."""
    pkg = json.loads((REPO / "package.json").read_text())
    assert pkg.get("packageManager", "").startswith("bun@"), pkg.get("packageManager")


def test_p2p_app_package_unit_test_script_present():
    """The packages/app package keeps its test:unit script (so future runs can use it)."""
    pkg = json.loads((REPO / "packages/app/package.json").read_text())
    assert "test:unit" in pkg.get("scripts", {}), pkg.get("scripts")


def test_p2p_bun_runtime_works():
    """Bun is installed and functional in the env."""
    r = subprocess.run(["bun", "--version"], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, r.stderr
    assert re.match(r"^\d+\.\d+\.\d+", r.stdout.strip()), r.stdout


def test_p2p_unrelated_app_module_parses():
    """An unrelated app source file (selectors.ts) parses cleanly — sanity check that parsing works in this env."""
    target = REPO / "packages/app/e2e/selectors.ts"
    assert target.exists(), target
    r = subprocess.run(
        ["bun", "build", "--no-bundle", "--target", "bun", str(target), "--outdir", "/tmp/out_sel"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    if r.returncode != 0:
        assert "SyntaxError" not in r.stderr, f"selectors.ts failed to parse:\n{r.stderr}"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """fail_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")