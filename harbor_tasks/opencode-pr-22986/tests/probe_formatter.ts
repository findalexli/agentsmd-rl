// Imports the agent's new formatter.ts module and exercises ConfigFormatter.Info.
// Fails (non-zero exit) if the module is missing, lacks `ConfigFormatter` namespace,
// lacks `Info` schema, or the schema doesn't behave like a record-of-formatter-entries.

import { ConfigFormatter } from "/workspace/opencode/packages/opencode/src/config/formatter"

if (typeof ConfigFormatter !== "object" || ConfigFormatter === null) {
  console.error("ConfigFormatter namespace missing from formatter.ts")
  process.exit(1)
}

const Info = (ConfigFormatter as { Info?: { safeParse: (x: unknown) => { success: boolean } } }).Info
if (!Info || typeof Info.safeParse !== "function") {
  console.error("ConfigFormatter.Info missing or not a zod schema")
  process.exit(1)
}

// `false` is valid (disable formatters)
let r = Info.safeParse(false)
if (!r.success) {
  console.error("Info.safeParse(false) should succeed")
  process.exit(1)
}

// Record of formatter entries should validate
r = Info.safeParse({
  prettier: {
    command: ["prettier", "--write", "$FILE"],
    extensions: [".ts", ".tsx"],
    environment: { NODE_ENV: "production" },
  },
  ruff: { disabled: true },
})
if (!r.success) {
  console.error("valid record should parse:", JSON.stringify((r as { error?: unknown }).error))
  process.exit(1)
}

// command must be a string array, not a string
r = Info.safeParse({ broken: { command: "not-an-array" } })
if (r.success) {
  console.error("non-array command should be rejected")
  process.exit(1)
}

// extensions must be a string array, not a string
r = Info.safeParse({ broken: { extensions: ".ts" } })
if (r.success) {
  console.error("non-array extensions should be rejected")
  process.exit(1)
}

// environment values must be strings
r = Info.safeParse({ broken: { environment: { KEY: 42 } } })
if (r.success) {
  console.error("non-string environment value should be rejected")
  process.exit(1)
}

// `true` is not a valid root value (only `false` or a record)
r = Info.safeParse(true)
if (r.success) {
  console.error("Info.safeParse(true) should fail")
  process.exit(1)
}

console.log("FORMATTER_OK")
