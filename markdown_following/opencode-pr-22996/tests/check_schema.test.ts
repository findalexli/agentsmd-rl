import { describe, expect, test } from "bun:test"
import { ConfigParse } from "@/config/parse"
import z from "zod"

describe("ConfigParse.schema", () => {
  test("returns parsed data when it matches the schema", () => {
    const schema = z.object({ x: z.number(), y: z.string() })
    const result = ConfigParse.schema(schema, { x: 42, y: "hi" }, "test:source")
    expect(result).toEqual({ x: 42, y: "hi" })
  })

  test("throws when the data does not match the schema", () => {
    expect(typeof (ConfigParse as any).schema).toBe("function")
    const okSchema = z.object({ x: z.number() })
    expect(ConfigParse.schema(okSchema, { x: 1 }, "test:source")).toEqual({ x: 1 })
    let threw = false
    try {
      ConfigParse.schema(okSchema, { x: "not a number" }, "test:source")
    } catch {
      threw = true
    }
    expect(threw).toBe(true)
  })

  test("accepts an already-parsed object (does not re-parse JSONC)", () => {
    const schema = z.object({ a: z.array(z.number()) })
    const data = { a: [1, 2, 3] }
    const result = ConfigParse.schema(schema, data, "test:source")
    expect(result).toEqual({ a: [1, 2, 3] })
  })

  test("validates a deeply nested object", () => {
    const schema = z.object({
      outer: z.object({
        inner: z.object({
          value: z.boolean(),
        }),
      }),
    })
    const result = ConfigParse.schema(schema, { outer: { inner: { value: true } } }, "test:source")
    expect(result.outer.inner.value).toBe(true)
  })
})
