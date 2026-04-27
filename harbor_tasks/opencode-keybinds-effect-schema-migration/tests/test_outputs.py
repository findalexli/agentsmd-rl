"""Behavioral tests for the keybinds.ts → Effect Schema migration (PR #23227).

The probe rewrites the (agent-edited) keybinds.ts so that bun can import it
from a minimal effect+zod sandbox without depending on the full opencode
workspace install. We then run the consumer surface that tui.ts and
tui-schema.ts exercise — `Keybinds.shape`, `Keybinds.parse(...)`, per-field
`.parse(undefined)` — plus a test that captures the strict-mode behavior
change (unknown keybind keys are accepted at this layer because
KeybindOverride in tui-schema.ts is already strict upstream).
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/opencode")
SANDBOX = Path("/workspace/sandbox")
KEYBINDS = REPO / "packages/opencode/src/config/keybinds.ts"
EFFECT_ZOD_SRC = REPO / "packages/opencode/src/util/effect-zod.ts"

PROBE_TS = r"""
import { promises as fs } from "node:fs"

const KEYBINDS = "__KEYBINDS__"
const EFFECT_ZOD_SRC = "__EFFECT_ZOD_SRC__"
const SANDBOX = "/workspace/sandbox"

// Mirror the two source files into the sandbox where `effect` and `zod`
// resolve, so bun's upward walk for `node_modules` succeeds. The keybinds
// copy rewrites its `@/util/effect-zod` alias to a sibling import; the
// self-reexport is stripped so the sibling lookup is unambiguous.
const effectZodSrc = await fs.readFile(EFFECT_ZOD_SRC, "utf8")
await fs.writeFile(`${SANDBOX}/effect-zod.copy.ts`, effectZodSrc)

const original = await fs.readFile(KEYBINDS, "utf8")
const rewritten = original
  .replace(/from\s+["']@\/util\/effect-zod["']/g, `from "./effect-zod.copy"`)
  .replace(/^export\s+\*\s+as\s+ConfigKeybinds\s+from\s+["']\.\/keybinds["'][^\n]*\n?/m, "")

const COPY = `${SANDBOX}/keybinds.copy.ts`
await fs.writeFile(COPY, rewritten)

const mod = await import(COPY)
const Keybinds = mod.Keybinds

const out: any = {}
out.has_shape = Keybinds && typeof Keybinds === "object" && "shape" in Keybinds
out.shape_keys = out.has_shape ? Object.keys(Keybinds.shape).length : 0
out.shape_keys_sample = out.has_shape ? Object.keys(Keybinds.shape).slice(0, 5) : []

try {
  const parsed = Keybinds.parse({})
  out.parsed_ok = true
  out.leader_default = parsed.leader
  out.editor_open_default = parsed.editor_open
  out.terminal_suspend_default = parsed.terminal_suspend
  out.input_undo_default_via_parse = parsed.input_undo
} catch (e: any) {
  out.parsed_ok = false
  out.parse_error = String(e?.message ?? e).slice(0, 300)
}

try {
  out.input_undo_via_field_parse = Keybinds.shape.input_undo.parse(undefined)
} catch (e: any) {
  out.input_undo_via_field_parse_err = String(e?.message ?? e).slice(0, 300)
}

try {
  const r = Keybinds.parse({ leader: "ctrl+x", _unknown_key_xyz: "blah" })
  out.unknown_key_accepted = true
  out.leader_after_unknown = r.leader
} catch (e: any) {
  out.unknown_key_accepted = false
  out.unknown_key_error = String(e?.message ?? e).slice(0, 300)
}

console.log("PROBE_RESULT:" + JSON.stringify(out))
"""


_probe_cache: dict | None = None


def _run_probe() -> dict:
    global _probe_cache
    if _probe_cache is not None:
        return _probe_cache

    probe_path = "/tmp/probe.ts"
    src = (
        PROBE_TS
        .replace("__KEYBINDS__", str(KEYBINDS))
        .replace("__EFFECT_ZOD_SRC__", str(EFFECT_ZOD_SRC))
    )
    with open(probe_path, "w") as f:
        f.write(src)

    r = subprocess.run(
        ["bun", "run", probe_path],
        cwd=str(SANDBOX),
        capture_output=True,
        text=True,
        timeout=120,
    )
    blob = (r.stdout or "") + "\n" + (r.stderr or "")
    if r.returncode != 0:
        raise AssertionError(
            f"probe exited rc={r.returncode}\n--- stdout/stderr ---\n{blob[-3000:]}"
        )
    for line in blob.splitlines():
        if line.startswith("PROBE_RESULT:"):
            _probe_cache = json.loads(line[len("PROBE_RESULT:"):])
            return _probe_cache
    raise AssertionError(f"probe produced no PROBE_RESULT line:\n{blob[-3000:]}")


# ---------------- pass_to_pass: consumer surface preserved ----------------

def test_keybinds_module_loads():
    """The keybinds module loads without throwing and exposes Keybinds.shape."""
    r = _run_probe()
    assert r["has_shape"] is True, f"Keybinds has no .shape; sample={r}"


def test_keybinds_shape_has_97_fields():
    """Keybinds.shape exposes all 97 keybind fields (consumer iterates this in tui-schema.ts)."""
    r = _run_probe()
    assert r["shape_keys"] == 97, (
        f"expected 97 shape keys, got {r['shape_keys']}; "
        f"first few: {r.get('shape_keys_sample')}"
    )


def test_keybinds_parse_resolves_defaults():
    """Calling Keybinds.parse({}) fills in the documented defaults."""
    r = _run_probe()
    assert r["parsed_ok"] is True, f"parse failed: {r.get('parse_error')}"
    assert r["leader_default"] == "ctrl+x", f"leader={r['leader_default']!r}"
    assert r["editor_open_default"] == "<leader>e", f"editor_open={r['editor_open_default']!r}"
    # On Linux, terminal_suspend default is "ctrl+z" (the win32 override is
    # applied at the call site in tui.ts, not at the schema layer).
    assert r["terminal_suspend_default"] == "ctrl+z", (
        f"terminal_suspend={r['terminal_suspend_default']!r}"
    )


def test_per_field_parse_input_undo():
    """Keybinds.shape.input_undo.parse(undefined) returns the Linux default; tui.ts
    relies on this exact API to seed input_undo before the user override merges in."""
    r = _run_probe()
    err = r.get("input_undo_via_field_parse_err")
    assert err is None, f"per-field parse threw: {err}"
    assert r["input_undo_via_field_parse"] == "ctrl+-,super+z", (
        f"got {r['input_undo_via_field_parse']!r}"
    )


# ---------------- pass_to_pass: existing repo test for the walker ----------------

def test_repo_effect_zod_walker_tests_pass():
    """The existing util/effect-zod.test.ts (the walker the migration depends on)
    keeps passing — guards against regressions in the walker contract that
    the migrated keybinds.ts now relies on. Run from /workspace/sandbox so
    bun does not pick up the package's bunfig.toml (which preloads
    @opentui/solid which we don't install)."""
    test_src = REPO / "packages/opencode/test/util/effect-zod.test.ts"
    util_src = REPO / "packages/opencode/src/util/effect-zod.ts"
    if not test_src.exists() or not util_src.exists():
        import pytest
        pytest.skip("effect-zod test or util file missing at base commit")

    # Copy walker source + test into the sandbox, rewriting the relative
    # import in the test file to point at the local copy.
    util_copy = SANDBOX / "effect-zod.copy.ts"
    util_copy.write_text(util_src.read_text())
    test_dst = SANDBOX / "effect-zod.test.copy.ts"
    rewritten = test_src.read_text().replace(
        '"../../src/util/effect-zod"',
        '"./effect-zod.copy"',
    )
    test_dst.write_text(rewritten)

    r = subprocess.run(
        ["bun", "test", "--timeout", "30000", str(test_dst)],
        cwd=str(SANDBOX),
        capture_output=True,
        text=True,
        timeout=180,
    )
    blob = (r.stdout or "") + "\n" + (r.stderr or "")
    assert r.returncode == 0, (
        f"util/effect-zod.test.ts failed (rc={r.returncode}):\n{blob[-2500:]}"
    )


# ---------------- fail_to_pass: behavioral diff that captures the PR ----------------

def test_unknown_keybind_keys_do_not_throw():
    """Unknown keybind keys must not raise — KeybindOverride in tui-schema.ts is
    already strict, so the schema-level .strict() at this layer was redundant
    and is dropped by the migration. Without that change, parse({foo, unknown})
    throws ZodError."""
    r = _run_probe()
    assert r["unknown_key_accepted"] is True, (
        f"parse with an unknown key threw: {r.get('unknown_key_error')!r}"
    )
    # Even when unknown keys are silently dropped, the known field should still
    # round-trip — verifies the parse actually ran and produced output.
    assert r.get("leader_after_unknown") == "ctrl+x", r
