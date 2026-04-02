"""
Task: opencode-file-appfilesystem-migration
Repo: anomalyco/opencode @ 608607256716d953bdaaa3142efe6cc99da6baf0
PR:   #19458

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
PKG = f"{REPO}/packages/opencode"
FILE_SRC = f"{PKG}/src/file/index.ts"
FS_SRC = f"{PKG}/src/filesystem/index.ts"


def _run_bun_script(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp TS file inside the package src dir and run it with bun."""
    import hashlib

    name = hashlib.md5(script.encode()).hexdigest()[:8]
    script_path = Path(f"{PKG}/src/_harbor_test_{name}.ts")
    try:
        script_path.write_text(script)
        return subprocess.run(
            ["bun", "run", str(script_path)],
            cwd=PKG,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified TypeScript files must parse without errors."""
    r = subprocess.run(
        [
            "node",
            "-e",
            f"""
const ts = require('typescript');
for (const f of ['{FILE_SRC}', '{FS_SRC}']) {{
    const src = require('fs').readFileSync(f, 'utf8');
    ts.createSourceFile(f, src, ts.ScriptTarget.Latest, true);
}}
console.log('OK');
""",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"TypeScript syntax error:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_exists_safe():
    """AppFileSystem.existsSafe returns true for existing files, false for missing."""
    r = _run_bun_script(
        """
import { AppFileSystem } from "@/filesystem"
import { Effect } from "effect"
import * as fs from "fs"

fs.writeFileSync("/tmp/_harbor_exists_target", "hello")

const program = Effect.gen(function*() {
  const appFs = yield* AppFileSystem.Service
  if (typeof appFs.existsSafe !== "function")
    throw new Error("existsSafe is not a function on AppFileSystem.Service")

  const yes = yield* appFs.existsSafe("/tmp/_harbor_exists_target")
  if (yes !== true) throw new Error("existsSafe(existing) should be true, got: " + yes)

  const no = yield* appFs.existsSafe("/nonexistent_harbor_" + Date.now())
  if (no !== false) throw new Error("existsSafe(missing) should be false, got: " + no)

  // Also test with a directory
  fs.mkdirSync("/tmp/_harbor_exists_dir", { recursive: true })
  const dir = yield* appFs.existsSafe("/tmp/_harbor_exists_dir")
  if (dir !== true) throw new Error("existsSafe(dir) should be true, got: " + dir)
})

await Effect.runPromise(program.pipe(Effect.provide(AppFileSystem.defaultLayer)))
console.log("existsSafe OK")
"""
    )
    assert r.returncode == 0, f"existsSafe test failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_read_directory_entries():
    """AppFileSystem.readDirectoryEntries returns DirEntry[] with correct name and type."""
    r = _run_bun_script(
        """
import { AppFileSystem } from "@/filesystem"
import { Effect } from "effect"
import * as fs from "fs"

fs.mkdirSync("/tmp/_harbor_readdir_test/sub_dir", { recursive: true })
fs.writeFileSync("/tmp/_harbor_readdir_test/alpha.txt", "a")
fs.writeFileSync("/tmp/_harbor_readdir_test/beta.log", "b")

const program = Effect.gen(function*() {
  const appFs = yield* AppFileSystem.Service
  if (typeof appFs.readDirectoryEntries !== "function")
    throw new Error("readDirectoryEntries is not a function on AppFileSystem.Service")

  const entries = yield* appFs.readDirectoryEntries("/tmp/_harbor_readdir_test")
  if (!Array.isArray(entries)) throw new Error("must return array, got: " + typeof entries)
  if (entries.length < 3) throw new Error("expected >=3 entries, got: " + entries.length)

  const byName = new Map(entries.map((e: any) => [e.name, e]))

  const alpha = byName.get("alpha.txt")
  if (!alpha) throw new Error("missing alpha.txt in entries")
  if (alpha.type !== "file") throw new Error("alpha.txt type should be 'file', got: " + alpha.type)

  const sub = byName.get("sub_dir")
  if (!sub) throw new Error("missing sub_dir in entries")
  if (sub.type !== "directory") throw new Error("sub_dir type should be 'directory', got: " + sub.type)

  const beta = byName.get("beta.log")
  if (!beta) throw new Error("missing beta.log in entries")
  if (beta.type !== "file") throw new Error("beta.log type should be 'file', got: " + beta.type)
})

await Effect.runPromise(program.pipe(Effect.provide(AppFileSystem.defaultLayer)))
console.log("readDirectoryEntries OK")
"""
    )
    assert r.returncode == 0, f"readDirectoryEntries test failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_default_layer_exported():
    """File namespace exports defaultLayer that composes with AppFileSystem."""
    r = _run_bun_script(
        """
import { File } from "@/file"

if (!("defaultLayer" in File)) throw new Error("File.defaultLayer not found in File namespace")
if (!File.defaultLayer) throw new Error("File.defaultLayer is falsy")
if (typeof (File.defaultLayer as any).pipe !== "function")
  throw new Error("File.defaultLayer does not look like an Effect Layer (no pipe method)")
console.log("File.defaultLayer OK")
"""
    )
    assert r.returncode == 0, f"File.defaultLayer test failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_read_no_raw_filesystem_calls():
    """read method must not use raw Filesystem.exists/readText/readBytes — should use AppFileSystem."""
    src = Path(FILE_SRC).read_text()
    read_start = src.find("const read = Effect.fn")
    assert read_start != -1, "read function not found in file/index.ts"

    list_start = src.find("const list = Effect.fn", read_start)
    read_section = src[read_start:list_start] if list_start > 0 else src[read_start : read_start + 2000]

    # read must not call raw Filesystem helpers (these should go through AppFileSystem)
    for raw_call in ["Filesystem.exists", "Filesystem.readText", "Filesystem.readBytes"]:
        assert raw_call not in read_section, (
            f"read method still uses raw {raw_call} instead of AppFileSystem"
        )


# [pr_diff] fail_to_pass
def test_list_no_raw_readdir():
    """list method must not use raw fs.promises.readdir — should use AppFileSystem."""
    src = Path(FILE_SRC).read_text()
    list_start = src.find("const list = Effect.fn")
    assert list_start != -1, "list function not found in file/index.ts"

    list_section = src[list_start : list_start + 2000]
    assert "fs.promises.readdir" not in list_section, (
        "list method still uses raw fs.promises.readdir instead of AppFileSystem"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_typecheck():
    """Full TypeScript type checking must pass after changes."""
    r = subprocess.run(
        ["bun", "run", "typecheck"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"bun typecheck failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — layer composition
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_appfilesystem_used_in_file_layer():
    """File.layer must yield AppFileSystem.Service for dependency injection."""
    src = Path(FILE_SRC).read_text()
    layer_start = src.find("export const layer = Layer.effect")
    assert layer_start != -1, "File.layer definition not found in file/index.ts"
    # The AppFileSystem.Service yield should be within the layer's Effect.gen block
    layer_section = src[layer_start : layer_start + 500]
    assert "AppFileSystem.Service" in layer_section or "AppFileSystem" in layer_section, (
        "File.layer must yield AppFileSystem.Service — the File service should depend on AppFileSystem"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — packages/opencode/AGENTS.md:21 @ 608607256716
def test_new_methods_traced_with_effect_fn():
    """New filesystem methods (existsSafe, readDirectoryEntries) must use Effect.fn for tracing."""
    src = Path(FS_SRC).read_text()
    traced = re.findall(
        r'Effect\.fn\(\s*"[A-Za-z]+\.(existsSafe|readDirectoryEntries|safeExists|listEntries)',
        src,
    )
    assert len(traced) >= 2, (
        f"Both new filesystem methods (existsSafe, readDirectoryEntries) must use Effect.fn for tracing, "
        f"found only {len(traced)}: {traced}"
    )
