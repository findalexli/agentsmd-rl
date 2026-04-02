/**
 * Behavioral test: force-replacing a plugin preserves JSONC comments.
 * Exits 0 on PASS, 1 on FAIL.
 */
import fs from "fs/promises"
import path from "path"
import os from "os"
import { parse as parseJsonc } from "jsonc-parser"
import { createPlugTask, type PlugDeps, type PlugCtx } from "../../src/cli/cmd/plug"

async function main() {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "jsonc-force-"))

  const p = path.join(tmp, "plugin")
  await fs.mkdir(p, { recursive: true })
  await fs.writeFile(
    path.join(p, "package.json"),
    JSON.stringify({ name: "acme", version: "1.0.0", "oc-plugin": ["server"] }, null, 2),
  )

  const cfg = path.join(tmp, ".opencode")
  await fs.mkdir(cfg, { recursive: true })
  const serverPath = path.join(cfg, "opencode.jsonc")

  await fs.writeFile(
    serverPath,
    `{
  "plugin": [
    // keep this note
    "acme@1.0.0"
  ]
}
`,
  )

  const deps: PlugDeps = {
    spinner: () => ({ start() {}, stop() {} }),
    log: { error() {}, info() {}, success() {} },
    resolve: async () => p,
    readText: (file: string) => fs.readFile(file, "utf8"),
    write: (file: string, text: string) => fs.writeFile(file, text),
    exists: async (file: string) => {
      try {
        await fs.access(file)
        return true
      } catch {
        return false
      }
    },
    files: (dir: string, name: "opencode" | "tui") => [path.join(dir, `${name}.jsonc`)],
    global: path.join(tmp, "global"),
  }

  const ctx: PlugCtx = { vcs: "git", worktree: tmp, directory: tmp }
  const run = createPlugTask({ mod: "acme@2.0.0", force: true }, deps)
  const ok = await run(ctx)

  if (!ok) {
    console.error("FAIL: createPlugTask returned false")
    process.exit(1)
  }

  const text = await fs.readFile(serverPath, "utf8")

  if (!text.includes("// keep this note")) {
    console.error("FAIL: comment was stripped during force replace")
    process.exit(1)
  }

  const json = parseJsonc(text) as { plugin?: unknown[] }
  if (!json.plugin?.includes("acme@2.0.0")) {
    console.error("FAIL: plugin was not updated to acme@2.0.0 — got: " + JSON.stringify(json.plugin))
    process.exit(1)
  }
  if (json.plugin?.includes("acme@1.0.0")) {
    console.error("FAIL: old plugin version still present")
    process.exit(1)
  }

  await fs.rm(tmp, { recursive: true, force: true })
  console.log("PASS")
}

main().catch((e) => {
  console.error("FAIL:", e.message || e)
  process.exit(1)
})
