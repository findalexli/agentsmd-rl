/**
 * Behavioral test: adding a plugin preserves JSONC comments.
 * Exits 0 on PASS, 1 on FAIL.
 */
import fs from "fs/promises"
import path from "path"
import os from "os"
import { parse as parseJsonc } from "jsonc-parser"
import { createPlugTask, type PlugDeps, type PlugCtx } from "../../src/cli/cmd/plug"

async function main() {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "jsonc-add-"))

  const p = path.join(tmp, "plugin")
  await fs.mkdir(p, { recursive: true })
  await fs.writeFile(
    path.join(p, "package.json"),
    JSON.stringify({ name: "acme", version: "1.0.0", "oc-plugin": ["server", "tui"] }, null, 2),
  )

  const cfg = path.join(tmp, ".opencode")
  await fs.mkdir(cfg, { recursive: true })

  const serverPath = path.join(cfg, "opencode.jsonc")
  const tuiPath = path.join(cfg, "tui.jsonc")

  await fs.writeFile(
    serverPath,
    `{
  // server head
  "plugin": [
    // server keep
    "seed@1.0.0"
  ],
  // server tail
  "model": "x"
}
`,
  )

  await fs.writeFile(
    tuiPath,
    `{
  // tui head
  "plugin": [
    // tui keep
    "seed@1.0.0"
  ],
  // tui tail
  "theme": "opencode"
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
  const run = createPlugTask({ mod: "acme@1.2.3" }, deps)
  const ok = await run(ctx)

  if (!ok) {
    console.error("FAIL: createPlugTask returned false")
    process.exit(1)
  }

  const serverText = await fs.readFile(serverPath, "utf8")
  const tuiText = await fs.readFile(tuiPath, "utf8")

  const checks: [string, string, string][] = [
    [serverText, "// server head", "server head comment"],
    [serverText, "// server keep", "server inside-array comment"],
    [serverText, "// server tail", "server tail comment"],
    [tuiText, "// tui head", "tui head comment"],
    [tuiText, "// tui keep", "tui inside-array comment"],
    [tuiText, "// tui tail", "tui tail comment"],
  ]
  for (const [text, comment, desc] of checks) {
    if (!text.includes(comment)) {
      console.error(`FAIL: ${desc} was stripped`)
      process.exit(1)
    }
  }

  const serverJson = parseJsonc(serverText) as { plugin?: unknown[] }
  const tuiJson = parseJsonc(tuiText) as { plugin?: unknown[] }

  if (!serverJson.plugin?.includes("seed@1.0.0") || !serverJson.plugin?.includes("acme@1.2.3")) {
    console.error("FAIL: server plugin list incorrect — got: " + JSON.stringify(serverJson.plugin))
    process.exit(1)
  }
  if (!tuiJson.plugin?.includes("seed@1.0.0") || !tuiJson.plugin?.includes("acme@1.2.3")) {
    console.error("FAIL: tui plugin list incorrect — got: " + JSON.stringify(tuiJson.plugin))
    process.exit(1)
  }

  await fs.rm(tmp, { recursive: true, force: true })
  console.log("PASS")
}

main().catch((e) => {
  console.error("FAIL:", e.message || e)
  process.exit(1)
})
