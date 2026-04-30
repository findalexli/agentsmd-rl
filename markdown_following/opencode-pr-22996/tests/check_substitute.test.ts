import { describe, expect, test } from "bun:test"
import { ConfigVariable } from "@/config/variable"
import { promises as fs } from "fs"
import path from "path"
import os from "os"

describe("ConfigVariable.substitute", () => {
  test("accepts a single options object and substitutes {env:VAR}", async () => {
    process.env.SCAFFOLD_TEST_ENV_A = "WORLD"
    try {
      const result = await ConfigVariable.substitute({
        text: "hello {env:SCAFFOLD_TEST_ENV_A}",
        type: "virtual",
        dir: "/tmp",
        source: "test",
      })
      expect(result).toBe("hello WORLD")
    } finally {
      delete process.env.SCAFFOLD_TEST_ENV_A
    }
  })

  test("missing 'empty' returns empty string for unset env", async () => {
    delete process.env.SCAFFOLD_NEVER_DEFINED_VAR
    const result = await ConfigVariable.substitute({
      text: "x={env:SCAFFOLD_NEVER_DEFINED_VAR}",
      type: "virtual",
      dir: "/tmp",
      source: "test",
      missing: "empty",
    })
    expect(result).toBe("x=")
  })

  test("substitutes {file:relative-path} relative to dir", async () => {
    const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "scaffold-sub-"))
    try {
      await fs.writeFile(path.join(tmp, "secret.txt"), "S3CRET")
      const result = await ConfigVariable.substitute({
        text: '{"key": "{file:secret.txt}"}',
        type: "virtual",
        dir: tmp,
        source: "test",
      })
      expect(result).toBe('{"key": "S3CRET"}')
    } finally {
      await fs.rm(tmp, { recursive: true, force: true })
    }
  })

  test("works for type=path with the path field", async () => {
    process.env.SCAFFOLD_TEST_ENV_B = "VALUE_B"
    try {
      const result = await ConfigVariable.substitute({
        text: "v={env:SCAFFOLD_TEST_ENV_B}",
        type: "path",
        path: "/tmp/dummy.json",
      })
      expect(result).toBe("v=VALUE_B")
    } finally {
      delete process.env.SCAFFOLD_TEST_ENV_B
    }
  })
})
