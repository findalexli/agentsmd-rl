import { Rpc, RpcGroup } from "@effect/rpc"
import { assert, describe, it } from "@effect/vitest"
import { Cause, Exit, Schema } from "effect"

const roundTrip = (rpc: any, defect: unknown): unknown => {
  const schema = Rpc.exitSchema(rpc)
  const enc = Schema.encodeSync(schema)
  const dec = Schema.decodeSync(schema)
  const round = dec(enc(Exit.die(defect)))
  if (!Exit.isFailure(round)) {
    throw new Error("expected Failure exit")
  }
  return Cause.squash((round as Exit.Failure<any, any>).cause)
}

describe("custom defect schema", () => {
  it("Schema.Unknown preserves arbitrary object fields", () => {
    const rpc: any = (Rpc.make as any)("preservesObject", {
      success: Schema.String,
      defect: Schema.Unknown
    })
    const original = { message: "boom", stack: "Error: boom\n  at h.ts:1", code: 42, kind: "auth" }
    assert.deepStrictEqual(roundTrip(rpc, original), original)
  })

  it("Schema.Unknown preserves a primitive number defect", () => {
    const rpc: any = (Rpc.make as any)("preservesNumber", {
      defect: Schema.Unknown
    })
    assert.deepStrictEqual(roundTrip(rpc, 12345), 12345)
  })

  it("Schema.Unknown preserves a nested object defect", () => {
    const rpc: any = (Rpc.make as any)("preservesNested", {
      defect: Schema.Unknown
    })
    const original = { outer: { inner: { code: 7, tags: ["a", "b"] } }, ok: false }
    assert.deepStrictEqual(roundTrip(rpc, original), original)
  })

  it("setSuccess preserves the defect schema across Proto chain", () => {
    const base: any = (Rpc.make as any)("chain1", {
      defect: Schema.Unknown
    })
    const chained: any = base.setSuccess(Schema.Number)
    const original = { code: 99, detail: "after-setSuccess" }
    assert.deepStrictEqual(roundTrip(chained, original), original)
  })

  it("setError preserves the defect schema across Proto chain", () => {
    const base: any = (Rpc.make as any)("chain2", {
      defect: Schema.Unknown
    })
    const chained: any = base.setError(Schema.String)
    const original = { code: 7, msg: "after-setError" }
    assert.deepStrictEqual(roundTrip(chained, original), original)
  })

  it("RpcGroup retains custom defect schema for grouped rpcs", () => {
    const Group = RpcGroup.make(
      (Rpc.make as any)("Op", {
        success: Schema.String,
        defect: Schema.Unknown
      })
    )
    const rpc: any = (Group as any).requests.get("Op")
    assert.isDefined(rpc)
    const original = { tag: "from-group", code: 1 }
    assert.deepStrictEqual(roundTrip(rpc, original), original)
  })
})
