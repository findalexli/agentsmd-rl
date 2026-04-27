"""Behavioral tests for the Zod-to-Effect-Schema migration."""
import os
import subprocess
import tempfile

REPO = "/workspace/opencode/packages/opencode"


def run_bun(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Write `code` to a temp .ts file inside REPO and execute it via bun.

    The file lives inside REPO so tsconfig path-mappings (`@/util/*` ->
    `./src/*`) resolve, and so node_modules walks find effect/zod.
    """
    fd, path = tempfile.mkstemp(suffix=".ts", dir=REPO)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        return subprocess.run(
            ["bun", "run", path],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass


def assert_ok(r: subprocess.CompletedProcess) -> None:
    if r.returncode != 0 or "OK" not in r.stdout:
        raise AssertionError(
            f"bun script failed (rc={r.returncode})\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
        )


# ---------- f2p: ConsoleState ----------


def test_console_state_zod_parse_valid():
    """`ConsoleState.zod.safeParse` accepts a well-formed payload (f2p)."""
    code = """
import { ConsoleState } from "@/config/console-state"
const r = ConsoleState.zod.safeParse({
  consoleManagedProviders: ["anthropic", "openai"],
  switchableOrgCount: 2,
})
if (!r.success) { console.error("fail-valid", JSON.stringify(r.error)); process.exit(1) }
if (r.data.consoleManagedProviders.length !== 2) { console.error("wrong-len"); process.exit(1) }
if (r.data.switchableOrgCount !== 2) { console.error("wrong-count"); process.exit(1) }
console.log("OK")
"""
    assert_ok(run_bun(code))


def test_console_state_zod_rejects_invalid():
    """`ConsoleState.zod.safeParse` rejects payloads that violate the shape (f2p)."""
    code = """
import { ConsoleState } from "@/config/console-state"
const bad1 = ConsoleState.zod.safeParse({ consoleManagedProviders: "nope", switchableOrgCount: 1 })
if (bad1.success) { console.error("string-passed-as-array"); process.exit(1) }
const bad2 = ConsoleState.zod.safeParse({ consoleManagedProviders: [], switchableOrgCount: "x" })
if (bad2.success) { console.error("string-passed-as-number"); process.exit(1) }
const bad3 = ConsoleState.zod.safeParse({ switchableOrgCount: 1 })
if (bad3.success) { console.error("missing-required-field"); process.exit(1) }
console.log("OK")
"""
    assert_ok(run_bun(code))


def test_console_state_make_constructs_instance():
    """`ConsoleState.make({...})` builds an instance — Schema.Class semantics (f2p)."""
    code = """
import { ConsoleState, emptyConsoleState } from "@/config/console-state"
if (typeof (ConsoleState as any).make !== "function") { console.error("no-make"); process.exit(1) }
const v = (ConsoleState as any).make({
  consoleManagedProviders: ["x"],
  switchableOrgCount: 7,
})
if (v.switchableOrgCount !== 7) { console.error("make-wrong-count"); process.exit(1) }
if (emptyConsoleState.consoleManagedProviders.length !== 0) { console.error("empty-not-empty"); process.exit(1) }
if (emptyConsoleState.switchableOrgCount !== 0) { console.error("empty-count-wrong"); process.exit(1) }
console.log("OK")
"""
    assert_ok(run_bun(code))


# ---------- f2p: ConfigSkills ----------


def test_skills_zod_parse_valid():
    """`ConfigSkills.Info.zod.safeParse` accepts well-formed skill config (f2p)."""
    code = """
import { ConfigSkills } from "@/config/skills"
const r1 = ConfigSkills.Info.zod.safeParse({ paths: ["/a", "/b"], urls: ["https://x.example/.well-known/skills/"] })
if (!r1.success) { console.error("fail-valid", JSON.stringify(r1.error)); process.exit(1) }
const r2 = ConfigSkills.Info.zod.safeParse({})
if (!r2.success) { console.error("empty-rejected"); process.exit(1) }
const r3 = ConfigSkills.Info.zod.safeParse({ paths: ["only-paths"] })
if (!r3.success) { console.error("paths-only-rejected"); process.exit(1) }
console.log("OK")
"""
    assert_ok(run_bun(code))


def test_skills_zod_rejects_invalid():
    """`ConfigSkills.Info.zod.safeParse` rejects bad shapes (f2p)."""
    code = """
import { ConfigSkills } from "@/config/skills"
const bad1 = ConfigSkills.Info.zod.safeParse({ paths: "not-array" })
if (bad1.success) { console.error("string-as-array"); process.exit(1) }
const bad2 = ConfigSkills.Info.zod.safeParse({ urls: [42] })
if (bad2.success) { console.error("number-as-string"); process.exit(1) }
console.log("OK")
"""
    assert_ok(run_bun(code))


# ---------- f2p: ConfigFormatter ----------


def test_formatter_zod_parse_boolean():
    """`ConfigFormatter.Info.zod.safeParse` accepts a boolean (union member) (f2p)."""
    code = """
import { ConfigFormatter } from "@/config/formatter"
const r1 = ConfigFormatter.Info.zod.safeParse(true)
if (!r1.success) { console.error("true-rejected", JSON.stringify(r1.error)); process.exit(1) }
const r2 = ConfigFormatter.Info.zod.safeParse(false)
if (!r2.success) { console.error("false-rejected"); process.exit(1) }
console.log("OK")
"""
    assert_ok(run_bun(code))


def test_formatter_zod_parse_record_of_entries():
    """`ConfigFormatter.Info.zod.safeParse` accepts a record-of-Entry (other union member) (f2p)."""
    code = """
import { ConfigFormatter } from "@/config/formatter"
const cfg = {
  prettier: {
    command: ["prettier", "--write", "$FILE"],
    extensions: [".ts", ".tsx"],
    environment: { NODE_ENV: "production" },
    disabled: false,
  },
  ruff: { command: ["ruff", "format"] },
}
const r = ConfigFormatter.Info.zod.safeParse(cfg)
if (!r.success) { console.error("rec-rejected", JSON.stringify(r.error)); process.exit(1) }
console.log("OK")
"""
    assert_ok(run_bun(code))


def test_formatter_entry_zod_validates():
    """`ConfigFormatter.Entry` exposes a `.zod` accessor that validates (f2p)."""
    code = """
import { ConfigFormatter } from "@/config/formatter"
const r1 = ConfigFormatter.Entry.zod.safeParse({ command: ["x"], extensions: [".ts"] })
if (!r1.success) { console.error("entry-valid-rejected", JSON.stringify(r1.error)); process.exit(1) }
const r2 = ConfigFormatter.Entry.zod.safeParse({ command: "not-array" })
if (r2.success) { console.error("entry-bad-accepted"); process.exit(1) }
console.log("OK")
"""
    assert_ok(run_bun(code))


# ---------- f2p: consumers updated ----------


def test_config_consumers_use_zod_accessor():
    """`config.ts` calls `.zod.optional()` on the migrated schemas; on base it
    still calls `.optional()` directly. The migrated schemas are Effect Schema
    values that don't expose Zod's `.optional()`, so the consumer must reach
    through `.zod` (matching the existing `ConfigLSP.Info.zod.optional()`
    pattern in the same file)."""
    import re
    p = os.path.join(REPO, "src/config/config.ts")
    with open(p) as f:
        src = f.read()
    # Whitespace-tolerant: allow newlines/spaces between `.zod` and `.optional()`.
    assert re.search(r"ConfigSkills\.Info\.zod\s*\.optional\s*\(\s*\)", src), (
        "config.ts must call .zod.optional() on ConfigSkills.Info "
        "(it is now an Effect Schema, not a Zod schema)."
    )
    assert re.search(r"ConfigFormatter\.Info\.zod\s*\.optional\s*\(\s*\)", src), (
        "config.ts must call .zod.optional() on ConfigFormatter.Info."
    )
    # And the bare `ConfigSkills.Info.optional()` (no `.zod`) must be gone —
    # otherwise the migration is incomplete.
    assert not re.search(r"ConfigSkills\.Info\.optional\s*\(\s*\)", src), (
        "config.ts still calls ConfigSkills.Info.optional() directly; this "
        "no longer compiles against the migrated Effect Schema."
    )
    assert not re.search(r"ConfigFormatter\.Info\.optional\s*\(\s*\)", src), (
        "config.ts still calls ConfigFormatter.Info.optional() directly."
    )


def test_experimental_route_uses_zod_accessor():
    """The experimental route resolver must consume `ConsoleState.zod` after migration."""
    import re
    p = os.path.join(REPO, "src/server/routes/instance/experimental.ts")
    with open(p) as f:
        src = f.read()
    assert re.search(r"resolver\s*\(\s*ConsoleState\.zod\s*\)", src), (
        "experimental.ts must pass ConsoleState.zod to resolver() "
        "(ConsoleState itself is now an Effect Schema, not a Zod schema)."
    )


# ---------- p2p: existing repo tests still pass on the base module ----------


def test_repo_effect_zod_unit_tests():
    """The repo's own `effect-zod` unit tests must still pass (pass_to_pass).

    They live at `test/util/effect-zod.test.ts` and exercise the conversion
    walker that the new schemas rely on. They depend on `bun:test` (built-in)
    and only use effect+zod, both of which are present in the minimal install.
    """
    r = subprocess.run(
        ["bun", "test", "test/util/effect-zod.test.ts", "--timeout", "30000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"effect-zod tests failed (rc={r.returncode})\n"
        f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )
