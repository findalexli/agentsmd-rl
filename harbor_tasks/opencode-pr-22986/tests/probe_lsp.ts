// Imports the agent's new lsp.ts module after stubbing out `../lsp/server`,
// so we can exercise ConfigLSP.Info without pulling the heavy lsp/server
// dep tree (which requires a full monorepo bun-install).
//
// Strategy: read the source of lsp.ts, replace the LSPServer import with an
// inline static stub, strip the self-export (which would re-resolve "./lsp"
// from the temp path), write to /tmp, then dynamic-import.
//
// The self-export pattern is verified separately by a content-level test.

import fs from "fs"

const SRC = "/workspace/opencode/packages/opencode/src/config/lsp.ts"

if (!fs.existsSync(SRC)) {
  console.error(`lsp.ts does not exist at ${SRC}`)
  process.exit(1)
}

const original = fs.readFileSync(SRC, "utf-8")

// Stub LSPServer with the actual server IDs from the base commit's
// src/lsp/server.ts. The schema only reads `.id` off each export.
// One-line stub so the regex below only consumes the import line itself
// (we must preserve the trailing newline of the matched line).
const stub =
  'const LSPServer = { ' +
  [
    "deno", "typescript", "vue", "eslint", "oxlint", "biome", "gopls",
    "ruby-lsp", "ty", "pyright", "elixir-ls", "zls", "csharp", "fsharp",
    "sourcekit-lsp", "rust", "clangd", "svelte", "astro",
  ].map((id, i) => `_${i}: { id: ${JSON.stringify(id)} }`).join(", ") +
  " }"

// Match only the import statement up to (but NOT including) any newline,
// so the original line break is preserved.
// Use [ \t] (horizontal whitespace only) so the regex never eats trailing newlines.
const importRegex = /import[ \t]*\*[ \t]*as[ \t]+LSPServer[ \t]+from[ \t]*["']\.\.\/lsp\/server["'][ \t]*;?[ \t]*/
if (!importRegex.test(original)) {
  console.error("LSPServer import not found in lsp.ts (was the import pattern changed?)")
  process.exit(1)
}
let stubbed = original.replace(importRegex, stub)

// Strip the self-export — keeping it would force bun to re-resolve "./lsp"
// from /tmp/, which doesn't exist. Self-export is checked elsewhere.
stubbed = stubbed.replace(
  /^[\t ]*export\s*\*\s*as\s+ConfigLSP\s+from\s*["']\.\/lsp["']\s*;?\s*$/m,
  "// (self-export stripped for runtime test)",
)

// Write the stubbed file under /workspace/ so bun's node_modules walk-up
// finds zod at /workspace/node_modules/zod (installed at image build time).
const tmp = `/workspace/lsp_stubbed_${Date.now()}.ts`
fs.writeFileSync(tmp, stubbed)

const mod = await import(tmp)

const Info = mod.Info as { safeParse: (x: unknown) => { success: boolean; error?: unknown } } | undefined
if (!Info || typeof Info.safeParse !== "function") {
  console.error("Info schema not exported from lsp.ts")
  process.exit(1)
}

// `false` (disable all LSP) should be valid
let r = Info.safeParse(false)
if (!r.success) {
  console.error("Info.safeParse(false) should succeed")
  process.exit(1)
}

// Known LSP server (id matches) without extensions — should pass refinement
r = Info.safeParse({ typescript: { command: ["typescript-language-server", "--stdio"] } })
if (!r.success) {
  console.error("known LSP without extensions should pass:", JSON.stringify(r.error))
  process.exit(1)
}

// Custom LSP id (not in known set) without extensions — refinement should reject
r = Info.safeParse({ "my-custom-lsp": { command: ["foo", "bar"] } })
if (r.success) {
  console.error("custom LSP without extensions must be rejected")
  process.exit(1)
}

// Custom LSP WITH extensions — passes refinement
r = Info.safeParse({ "my-custom-lsp": { command: ["foo"], extensions: [".foo", ".bar"] } })
if (!r.success) {
  console.error("custom LSP with extensions should pass:", JSON.stringify(r.error))
  process.exit(1)
}

// disabled-only entry is valid
r = Info.safeParse({ "any-id": { disabled: true } })
if (!r.success) {
  console.error("disabled-only entry should pass:", JSON.stringify(r.error))
  process.exit(1)
}

// Custom LSP marked disabled (no extensions, no command) — disabled bypasses checks
r = Info.safeParse({ "another-custom": { disabled: true } })
if (!r.success) {
  console.error("disabled custom LSP should pass:", JSON.stringify(r.error))
  process.exit(1)
}

// command must be an array of strings (when not disabled-only branch)
r = Info.safeParse({ typescript: { command: "not-array" } })
if (r.success) {
  console.error("non-array command should be rejected")
  process.exit(1)
}

// `true` is not a valid root value
r = Info.safeParse(true)
if (r.success) {
  console.error("Info.safeParse(true) should fail")
  process.exit(1)
}

fs.unlinkSync(tmp)
console.log("LSP_OK")
