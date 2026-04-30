import { describe, expect, test } from "bun:test"
import { ConfigParse } from "@/config/parse"

describe("ConfigParse.jsonc", () => {
  test("parses standard JSON to a plain object", () => {
    const result = ConfigParse.jsonc('{"a": 1, "b": "hi"}', "test.json")
    expect(result).toEqual({ a: 1, b: "hi" })
  })

  test("allows trailing commas", () => {
    const result = ConfigParse.jsonc('{"a": 1,}', "test.json")
    expect(result).toEqual({ a: 1 })
  })

  test("allows comments", () => {
    const result = ConfigParse.jsonc('// header\n{"a": 1, /* inline */ "b": 2}', "test.json")
    expect(result).toEqual({ a: 1, b: 2 })
  })

  test("throws on invalid JSONC", () => {
    expect(typeof (ConfigParse as any).jsonc).toBe("function")
    expect(ConfigParse.jsonc('{"ok": 1}', "test.json")).toEqual({ ok: 1 })
    let threw = false
    try {
      ConfigParse.jsonc("{this is not json}", "test.json")
    } catch {
      threw = true
    }
    expect(threw).toBe(true)
  })

  test("does not validate against any schema (returns raw unknown shape)", () => {
    const result: unknown = ConfigParse.jsonc('{"unknown_field": [1,2,3]}', "test.json")
    expect(result).toEqual({ unknown_field: [1, 2, 3] })
  })
})
