import { Equal, Utils } from "effect"

const cases: Record<string, () => void> = {
  null_vs_null: () =>
    Utils.structuralRegion(() => {
      if (Equal.equals(null, null) !== true) throw new Error("expected true for null vs null")
    }),
  null_vs_object: () =>
    Utils.structuralRegion(() => {
      if (Equal.equals(null, { a: 1 }) !== false) throw new Error("expected false for null vs object")
    }),
  object_vs_null: () =>
    Utils.structuralRegion(() => {
      if (Equal.equals({ a: 1 }, null) !== false) throw new Error("expected false for object vs null")
    }),
  null_vs_string: () =>
    Utils.structuralRegion(() => {
      if (Equal.equals(null, "hello") !== false) throw new Error("expected false for null vs string")
    }),
  null_vs_array: () =>
    Utils.structuralRegion(() => {
      if (Equal.equals(null, [1, 2, 3]) !== false) throw new Error("expected false for null vs array")
    }),
  array_vs_null: () =>
    Utils.structuralRegion(() => {
      if (Equal.equals([1, 2, 3], null) !== false) throw new Error("expected false for array vs null")
    }),
  null_vs_undefined: () =>
    Utils.structuralRegion(() => {
      if (Equal.equals(null, undefined) !== false) throw new Error("expected false for null vs undefined")
    }),
  nested_null_equality: () =>
    Utils.structuralRegion(() => {
      const a = { name: "test", address: { city: "NYC", zip: null } }
      const b = { name: "test", address: { city: "NYC", zip: null } }
      if (Equal.equals(a, b) !== true) throw new Error("expected true for nested null equality")
    }),
  nested_null_vs_nonnull: () =>
    Utils.structuralRegion(() => {
      const a = { name: "test", value: null }
      const b = { name: "test", value: 42 }
      if (Equal.equals(a, b) !== false) throw new Error("expected false for nested null vs nonnull")
    }),
  object_with_null_field_vs_object_with_object_field: () =>
    Utils.structuralRegion(() => {
      const a = { x: null }
      const b = { x: { y: 1 } }
      if (Equal.equals(a, b) !== false) throw new Error("expected false")
    }),
  no_throw_on_pure_null_object_compare: () => {
    let threw = false
    try {
      Utils.structuralRegion(() => {
        Equal.equals(null, { a: 1 })
        Equal.equals({ a: 1 }, null)
        Equal.equals(null, [1])
        Equal.equals([1], null)
      })
    } catch (_e) {
      threw = true
    }
    if (threw) throw new Error("Equal.equals threw when comparing null with object inside structuralRegion")
  }
}

const name = process.argv[2]
const fn = cases[name]
if (!fn) {
  console.error("unknown case:", name)
  process.exit(2)
}
try {
  fn()
  console.log("PASS", name)
  process.exit(0)
} catch (e: any) {
  console.error("FAIL", name, e?.message ?? String(e))
  process.exit(1)
}
