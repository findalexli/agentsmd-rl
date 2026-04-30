// Imports the new layout/server config modules from the cloned opencode repo
// and exercises their schemas. The test harness invokes this file via
// `bun run`. Output: JSON describing each check's result, written to
// /tmp/schema_results.json.

import { writeFileSync } from "fs"

const REPO = "/workspace/opencode/packages/opencode/src/config"

type Result = {
  id: string
  ok: boolean
  detail: string
}

const results: Result[] = []

function record(id: string, ok: boolean, detail: string = "") {
  results.push({ id, ok, detail })
}

async function loadModule(path: string): Promise<any> {
  return await import(path)
}

let layoutMod: any = null
let serverMod: any = null

try {
  layoutMod = await loadModule(`${REPO}/layout.ts`)
  record("layout_module_imports", true)
} catch (e: any) {
  record("layout_module_imports", false, String(e?.message ?? e))
}

try {
  serverMod = await loadModule(`${REPO}/server.ts`)
  record("server_module_imports", true)
} catch (e: any) {
  record("server_module_imports", false, String(e?.message ?? e))
}

// --- Layout schema behavior ---
if (layoutMod) {
  const ConfigLayout = layoutMod.ConfigLayout
  if (!ConfigLayout) {
    record("layout_namespace_export", false, "ConfigLayout namespace export missing")
  } else {
    record("layout_namespace_export", true)

    const Layout = ConfigLayout.Layout
    if (!Layout) {
      record("layout_schema_present", false, "ConfigLayout.Layout missing")
    } else {
      record("layout_schema_present", true)

      const zodSchema = Layout.zod
      if (!zodSchema || typeof zodSchema.parse !== "function") {
        record("layout_zod_accessor", false, "Layout.zod is not a zod schema")
      } else {
        record("layout_zod_accessor", true)

        // Auto valid
        try {
          const v = zodSchema.parse("auto")
          record("layout_accepts_auto", v === "auto", `parsed=${JSON.stringify(v)}`)
        } catch (e: any) {
          record("layout_accepts_auto", false, String(e?.message ?? e))
        }
        // Stretch valid
        try {
          const v = zodSchema.parse("stretch")
          record("layout_accepts_stretch", v === "stretch", `parsed=${JSON.stringify(v)}`)
        } catch (e: any) {
          record("layout_accepts_stretch", false, String(e?.message ?? e))
        }
        // Invalid value rejected
        try {
          zodSchema.parse("compact")
          record("layout_rejects_invalid", false, "expected throw, got success")
        } catch {
          record("layout_rejects_invalid", true)
        }
        try {
          zodSchema.parse("")
          record("layout_rejects_empty", false, "expected throw, got success")
        } catch {
          record("layout_rejects_empty", true)
        }
      }
    }
  }
}

// --- Server schema behavior ---
if (serverMod) {
  const ConfigServer = serverMod.ConfigServer
  if (!ConfigServer) {
    record("server_namespace_export", false, "ConfigServer namespace export missing")
  } else {
    record("server_namespace_export", true)

    const Server = ConfigServer.Server
    if (!Server) {
      record("server_schema_present", false, "ConfigServer.Server missing")
    } else {
      record("server_schema_present", true)

      const zodSchema = Server.zod
      if (!zodSchema || typeof zodSchema.parse !== "function") {
        record("server_zod_accessor", false, "Server.zod is not a zod schema")
      } else {
        record("server_zod_accessor", true)

        // Empty config (all optional)
        try {
          zodSchema.parse({})
          record("server_accepts_empty", true)
        } catch (e: any) {
          record("server_accepts_empty", false, String(e?.message ?? e))
        }
        // Full valid config
        try {
          const v = zodSchema.parse({
            port: 3000,
            hostname: "localhost",
            mdns: true,
            mdnsDomain: "opencode.local",
            cors: ["https://example.com"],
          })
          const ok = v.port === 3000 && v.hostname === "localhost" && v.mdns === true
          record("server_accepts_full", ok, `parsed=${JSON.stringify(v)}`)
        } catch (e: any) {
          record("server_accepts_full", false, String(e?.message ?? e))
        }
        // Reject negative port (positive int constraint)
        try {
          zodSchema.parse({ port: -1 })
          record("server_rejects_negative_port", false, "expected throw")
        } catch {
          record("server_rejects_negative_port", true)
        }
        // Reject zero port
        try {
          zodSchema.parse({ port: 0 })
          record("server_rejects_zero_port", false, "expected throw")
        } catch {
          record("server_rejects_zero_port", true)
        }
        // Reject non-integer port
        try {
          zodSchema.parse({ port: 3.5 })
          record("server_rejects_float_port", false, "expected throw")
        } catch {
          record("server_rejects_float_port", true)
        }
        // Reject non-string hostname
        try {
          zodSchema.parse({ hostname: 123 })
          record("server_rejects_bad_hostname", false, "expected throw")
        } catch {
          record("server_rejects_bad_hostname", true)
        }
        // Reject cors not an array
        try {
          zodSchema.parse({ cors: "not-array" })
          record("server_rejects_bad_cors", false, "expected throw")
        } catch {
          record("server_rejects_bad_cors", true)
        }
      }
    }
  }
}

// --- config.ts re-exports ---
try {
  // Importing config.ts pulls in the entire config service. Skip that;
  // instead read the file and confirm it references the new modules.
  const fs = await import("fs/promises")
  const src = await fs.readFile(`${REPO}/config.ts`, "utf8")

  // Accept "./server" or "./server.ts"; allow `import type` is not relevant here.
  const importsServer = /import\s*\{\s*ConfigServer\s*\}\s*from\s*["']\.\/server(?:\.ts)?["']/.test(src)
  record("config_imports_configserver", importsServer)

  const importsLayout = /import\s*\{\s*ConfigLayout\s*\}\s*from\s*["']\.\/layout(?:\.ts)?["']/.test(src)
  record("config_imports_configlayout", importsLayout)

  // After the migration, config.ts's Server/Layout exports should be
  // re-exports backed by the new module's .zod accessor rather than
  // freshly-built zod schemas. Allow an optional type annotation.
  const reexportsServerZod = /export\s+const\s+Server(?:\s*:\s*[^=\n]+)?\s*=\s*ConfigServer\.Server\.zod/.test(src)
  record("config_reexports_server_via_zod", reexportsServerZod)

  const reexportsLayoutZod = /export\s+const\s+Layout(?:\s*:\s*[^=\n]+)?\s*=\s*ConfigLayout\.Layout\.zod/.test(src)
  record("config_reexports_layout_via_zod", reexportsLayoutZod)

  // The legacy inline `z.enum(["auto", "stretch"])` for Layout must be gone.
  const hasOldLayoutEnum = /z\.enum\(\s*\[\s*["']auto["']\s*,\s*["']stretch["']\s*\]\s*\)/.test(src)
  record("config_no_inline_layout_enum", !hasOldLayoutEnum)
} catch (e: any) {
  record("config_imports_configserver", false, String(e?.message ?? e))
  record("config_imports_configlayout", false, String(e?.message ?? e))
  record("config_reexports_server_via_zod", false, String(e?.message ?? e))
  record("config_reexports_layout_via_zod", false, String(e?.message ?? e))
  record("config_no_inline_layout_enum", false, String(e?.message ?? e))
}

writeFileSync("/tmp/schema_results.json", JSON.stringify(results, null, 2))
console.log(JSON.stringify(results, null, 2))
