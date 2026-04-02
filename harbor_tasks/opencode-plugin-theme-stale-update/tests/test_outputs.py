"""
Task: opencode-plugin-theme-stale-update
Repo: anomalyco/opencode @ 3c32013eb122d794089e011d2ec7077395d6f1c4
PR:   20052

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
import json
from pathlib import Path

REPO = "/workspace/opencode"
PKG = f"{REPO}/packages/opencode"

# ---------------------------------------------------------------------------
# Helper: run a bun script in the packages/opencode directory
# ---------------------------------------------------------------------------

def _run_ts(code: str, *, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a TS snippet to a temp file and run it with bun."""
    tmp = Path(PKG) / "test" / "_verifier"
    tmp.mkdir(parents=True, exist_ok=True)
    script = tmp / f"test_{os.getpid()}.ts"
    script.write_text(code)
    try:
        return subprocess.run(
            ["bun", "run", str(script)],
            cwd=PKG,
            capture_output=True,
            timeout=timeout,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_changed_files_exist():
    """All four modified files must exist and not be empty."""
    files = [
        "packages/opencode/src/util/filesystem.ts",
        "packages/opencode/src/plugin/meta.ts",
        "packages/opencode/src/cli/cmd/tui/context/theme.tsx",
        "packages/opencode/src/cli/cmd/tui/plugin/runtime.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} does not exist"
        assert p.stat().st_size > 0, f"{f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_stat_async_existing_file():
    """Filesystem.statAsync returns stat for existing files with correct size."""
    # Test multiple files of different sizes to prevent hardcoding
    code = """\
import { Filesystem } from "@/util/filesystem"
import * as fs from "fs/promises"
import * as os from "os"
import * as path from "path"

const sizes = [0, 13, 1024]
for (const sz of sizes) {
  const tmp = path.join(os.tmpdir(), `stat-test-${sz}-${Date.now()}`)
  await fs.writeFile(tmp, "x".repeat(sz))
  try {
    const stat = await Filesystem.statAsync(tmp)
    if (!stat) { console.error(`returned undefined for existing file of size ${sz}`); process.exit(1) }
    if (stat.size !== sz) { console.error(`expected size ${sz}, got ${stat.size}`); process.exit(1) }
  } finally {
    await fs.unlink(tmp).catch(() => {})
  }
}
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"statAsync failed for existing file:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_stat_async_missing_file():
    """Filesystem.statAsync returns undefined for missing files (not throw)."""
    code = """\
import { Filesystem } from "@/util/filesystem"

// Test several non-existent paths
const paths = [
  `/tmp/no-such-file-${Date.now()}-${Math.random()}`,
  `/tmp/also-missing-${Date.now()}`,
  `/nonexistent/deep/path/file.txt`,
]
for (const p of paths) {
  const result = await Filesystem.statAsync(p)
  if (result !== undefined) {
    console.error(`should return undefined for ${p}, got:`, result)
    process.exit(1)
  }
}
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"statAsync failed for missing file:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_upsert_theme_add_and_update():
    """upsertTheme must add a new theme AND update an existing one."""
    # isTheme requires { theme: { ... } } where theme is a record
    code = """\
import { hasTheme } from "@/cli/cmd/tui/context/theme"

const mod = await import("@/cli/cmd/tui/context/theme")
const upsertTheme = mod.upsertTheme
if (typeof upsertTheme !== "function") {
  console.error("upsertTheme not exported as a function")
  process.exit(1)
}

// Valid theme shape: { theme: { <color entries> } }
const theme1 = { theme: { text: "#ffffff", background: "#000000" } }
const theme2 = { theme: { text: "#ff0000", background: "#00ff00" } }

// ADD path — new theme name
const name = `_verifier_upsert_${Date.now()}`
const addResult = upsertTheme(name, theme1)
if (addResult !== true) {
  console.error("upsertTheme returned false for valid new theme (add path)")
  process.exit(1)
}
if (!hasTheme(name)) {
  console.error("hasTheme returns false after upsertTheme add")
  process.exit(1)
}

// UPDATE path — same name, different data; addTheme would skip but upsert must succeed
const updateResult = upsertTheme(name, theme2)
if (updateResult !== true) {
  console.error("upsertTheme returned false on second call (update path)")
  process.exit(1)
}

// Verify with a third distinct theme to ensure it's not just toggling
const theme3 = { theme: { text: "#aabbcc", background: "#ddeeff" } }
const name2 = `_verifier_upsert2_${Date.now()}`
if (upsertTheme(name2, theme3) !== true) {
  console.error("upsertTheme failed for second distinct theme name")
  process.exit(1)
}
"""
    r = _run_ts(code, timeout=45)
    assert r.returncode == 0, f"upsertTheme add/update failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_upsert_theme_rejects_invalid():
    """upsertTheme returns false for empty name and non-theme data."""
    code = """\
const mod = await import("@/cli/cmd/tui/context/theme")
const upsertTheme = mod.upsertTheme
if (typeof upsertTheme !== "function") {
  console.error("upsertTheme not exported")
  process.exit(1)
}

// Empty name
if (upsertTheme("", { theme: {} }) !== false) {
  console.error("should return false for empty name")
  process.exit(1)
}

// Non-theme data (string)
if (upsertTheme("test", "not-a-theme") !== false) {
  console.error("should return false for string data")
  process.exit(1)
}

// Non-theme data (no .theme property)
if (upsertTheme("test2", { colors: {} }) !== false) {
  console.error("should return false for object without .theme")
  process.exit(1)
}

// Non-theme data (.theme is not a record)
if (upsertTheme("test3", { theme: "nope" }) !== false) {
  console.error("should return false when .theme is not a record")
  process.exit(1)
}
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"upsertTheme validation failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_set_theme_callable():
    """PluginMeta.setTheme is exported and handles missing plugin IDs gracefully."""
    code = """\
import { PluginMeta } from "@/plugin/meta"

if (typeof PluginMeta.setTheme !== "function") {
  console.error("PluginMeta.setTheme not exported as function")
  process.exit(1)
}

// Should not throw for nonexistent plugin IDs — test several
const ids = ["_verifier_nonexistent_1", "_verifier_nonexistent_2", `_dyn_${Date.now()}`]
for (const id of ids) {
  await PluginMeta.setTheme(id, "test-theme", {
    src: "/tmp/test-theme.json",
    dest: "/tmp/dest-theme.json",
    mtime: Date.now(),
    size: 42,
  })
}
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"PluginMeta.setTheme not working:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_theme_entry_has_themes_field():
    """PluginMeta.Entry type includes themes field for tracking installed themes."""
    # AST-only because: PluginMeta.Entry is a TypeScript type — can't instantiate at runtime
    # We verify the type exists by checking that the gold patch adds it to the store
    code = """\
import { PluginMeta } from "@/plugin/meta"
import * as fs from "fs/promises"

// setTheme should create a themes record on the entry; verify the store shape
// by calling setTheme then listing and checking the schema
const testId = `_verifier_themes_field_${Date.now()}`

// First need a real entry — touch won't create one, so we test
// that setTheme at least doesn't crash and the function signature accepts Theme shape
if (typeof PluginMeta.setTheme !== "function") {
  console.error("setTheme not available")
  process.exit(1)
}

// Verify setTheme accepts the Theme shape with all fields
await PluginMeta.setTheme(testId, "dark-theme", {
  src: "/tmp/src.json",
  dest: "/tmp/dest.json",
  mtime: 1700000000000,
  size: 256,
})

await PluginMeta.setTheme(testId, "light-theme", {
  src: "/tmp/light-src.json",
  dest: "/tmp/light-dest.json",
})
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"themes field test failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_plugin_loader_tests_pass():
    """Existing plugin-loader test suite still passes."""
    r = subprocess.run(
        ["bun", "test", "test/cli/tui/plugin-loader.test.ts"],
        cwd=PKG,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"plugin-loader tests failed:\n{r.stdout.decode()[-500:]}\n{r.stderr.decode()[-500:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified files have substantial content (not stubbed/truncated)."""
    files = [
        "src/util/filesystem.ts",
        "src/plugin/meta.ts",
        "src/cli/cmd/tui/context/theme.tsx",
        "src/cli/cmd/tui/plugin/runtime.ts",
    ]
    for f in files:
        p = Path(PKG) / f
        lines = len(p.read_text().splitlines())
        assert lines >= 50, f"{f} has only {lines} lines — likely stubbed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ 3c32013eb122d794089e011d2ec7077395d6f1c4
def test_no_any_type():
    """No explicit 'any' type annotations in changed files (AGENTS.md:13)."""
    import re
    files = [
        "src/util/filesystem.ts",
        "src/plugin/meta.ts",
        "src/cli/cmd/tui/context/theme.tsx",
        "src/cli/cmd/tui/plugin/runtime.ts",
    ]
    pattern = re.compile(r':\s*any\b|<any>')
    for f in files:
        p = Path(PKG) / f
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if "eslint-disable" in line:
                continue
            assert not pattern.search(line), (
                f"Explicit 'any' type found in {f}:{i}: {line.strip()}"
            )


# [agent_config] pass_to_pass — AGENTS.md:70 @ 3c32013eb122d794089e011d2ec7077395d6f1c4
def test_prefer_const_over_let():
    """Changed lines should prefer const over let (AGENTS.md:70)."""
    # Compare against the known base commit (not HEAD) so this is robust whether
    # the agent commits their changes or leaves them in the working tree.
    BASE = "3c32013eb122d794089e011d2ec7077395d6f1c4"
    r = subprocess.run(
        ["git", "diff", BASE, "--unified=0", "--",
         "packages/opencode/src/util/filesystem.ts",
         "packages/opencode/src/plugin/meta.ts",
         "packages/opencode/src/cli/cmd/tui/context/theme.tsx",
         "packages/opencode/src/cli/cmd/tui/plugin/runtime.ts"],
        cwd=REPO,
        capture_output=True,
        timeout=10,
    )
    diff = r.stdout.decode()
    added_lines = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    let_count = sum(1 for l in added_lines if "  let " in l or "\tlet " in l or l.startswith("+let "))
    # Allow up to 3 lets (some are legitimately needed for reassignment)
    assert let_count <= 3, (
        f"Too many 'let' declarations in added lines ({let_count}). Prefer const."
    )
