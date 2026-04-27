import { describe, expect, test } from "bun:test"
import { MessageV2 } from "../src/session/message-v2"
import { SessionPrompt } from "../src/session/prompt"

describe("structured-output-effect-schema-migration", () => {
  test("OutputFormatText is a Schema.Class with constructible instances", () => {
    expect(typeof (MessageV2 as any).OutputFormatText).toBe("function")
    const inst: any = new (MessageV2 as any).OutputFormatText({ type: "text" })
    expect(inst.type).toBe("text")
  })

  test("OutputFormatJsonSchema is a Schema.Class with constructible instances", () => {
    expect(typeof (MessageV2 as any).OutputFormatJsonSchema).toBe("function")
    const inst: any = new (MessageV2 as any).OutputFormatJsonSchema({
      type: "json_schema",
      schema: { type: "object" },
      retryCount: 3,
    })
    expect(inst.type).toBe("json_schema")
    expect(inst.retryCount).toBe(3)
  })

  test("OutputFormatText exposes a Zod-compatible .zod accessor", () => {
    const z = (MessageV2 as any).OutputFormatText.zod
    expect(z).toBeDefined()
    expect(typeof z.safeParse).toBe("function")
    const ok = z.safeParse({ type: "text" })
    expect(ok.success).toBe(true)
    const bad = z.safeParse({ type: "json_schema" })
    expect(bad.success).toBe(false)
  })

  test("OutputFormatJsonSchema .zod parses with retryCount default of 2", () => {
    const z = (MessageV2 as any).OutputFormatJsonSchema.zod
    const ok = z.safeParse({ type: "json_schema", schema: { type: "object" } })
    expect(ok.success).toBe(true)
    if (ok.success) expect(ok.data.retryCount).toBe(2)

    const custom = z.safeParse({ type: "json_schema", schema: { type: "object" }, retryCount: 7 })
    expect(custom.success).toBe(true)
    if (custom.success) expect(custom.data.retryCount).toBe(7)
  })

  test("OutputFormatJsonSchema .zod rejects negative retryCount and missing schema", () => {
    const z = (MessageV2 as any).OutputFormatJsonSchema.zod
    expect(z.safeParse({ type: "json_schema", schema: {}, retryCount: -1 }).success).toBe(false)
    expect(z.safeParse({ type: "json_schema" }).success).toBe(false)
  })

  test("Format exposes a Zod-compatible .zod accessor that handles the union", () => {
    const z = (MessageV2 as any).Format.zod
    expect(z).toBeDefined()
    expect(typeof z.safeParse).toBe("function")

    expect(z.safeParse({ type: "text" }).success).toBe(true)
    expect(z.safeParse({ type: "json_schema", schema: { type: "object" } }).success).toBe(true)
    expect(z.safeParse({ type: "invalid" }).success).toBe(false)
  })

  test("Format itself is no longer a direct Zod schema (no .safeParse on Format)", () => {
    expect((MessageV2 as any).Format.safeParse).toBeUndefined()
  })

  test("PromptInput accepts format via the migrated .zod accessor", () => {
    // PromptInput's `format` field used to be `MessageV2.Format.optional()`. After
    // the migration, callers must reach into `.zod.optional()`. If prompt.ts was
    // not updated, importing SessionPrompt would have thrown at module load.
    const ok = (SessionPrompt as any).PromptInput.safeParse({
      sessionID: "ses_01HXYZ0000000000000000000000",
      parts: [],
      format: { type: "text" },
    })
    expect(ok.success).toBe(true)

    const okJson = (SessionPrompt as any).PromptInput.safeParse({
      sessionID: "ses_01HXYZ0000000000000000000000",
      parts: [],
      format: { type: "json_schema", schema: { type: "object" } },
    })
    expect(okJson.success).toBe(true)

    const badFormat = (SessionPrompt as any).PromptInput.safeParse({
      sessionID: "ses_01HXYZ0000000000000000000000",
      parts: [],
      format: { type: "bogus" },
    })
    expect(badFormat.success).toBe(false)
  })
})
