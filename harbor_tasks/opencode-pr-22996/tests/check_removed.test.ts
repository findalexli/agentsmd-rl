import { describe, expect, test } from "bun:test"
import { ConfigParse } from "@/config/parse"

describe("Old combined APIs are removed", () => {
  test("ConfigParse.parse no longer exists", () => {
    expect((ConfigParse as any).parse).toBeUndefined()
  })

  test("ConfigParse.load no longer exists", () => {
    expect((ConfigParse as any).load).toBeUndefined()
  })

  test("ConfigParse exposes only jsonc and schema as parse-related functions", () => {
    expect(typeof (ConfigParse as any).jsonc).toBe("function")
    expect(typeof (ConfigParse as any).schema).toBe("function")
  })
})
