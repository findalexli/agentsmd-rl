#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier

cat > /workspace/effect/packages/effect/test/Schema/SchemaAST/probe.test.ts <<'PROBE'
import { describe, it } from "@effect/vitest"
import { deepStrictEqual } from "@effect/vitest/utils"
import * as S from "effect/Schema"
import * as AST from "effect/SchemaAST"

describe("probe getPropertySignatures Transformation", () => {
  it("handles optionalWith default without crashing", () => {
    const schema = S.Struct({
      a: S.String,
      b: S.optionalWith(S.Number, { default: () => 0 })
    })
    const sigs = AST.getPropertySignatures(schema.ast)
    deepStrictEqual(sigs.length, 2)
    deepStrictEqual(sigs[0].name, "a")
    deepStrictEqual(sigs[1].name, "b")
  })

  it("handles optionalWith as Option without crashing", () => {
    const schema = S.Struct({
      a: S.String,
      b: S.optionalWith(S.Number, { as: "Option" })
    })
    const sigs = AST.getPropertySignatures(schema.ast)
    deepStrictEqual(sigs.length, 2)
    deepStrictEqual(sigs[0].name, "a")
    deepStrictEqual(sigs[1].name, "b")
  })

  it("handles optionalWith nullable without crashing", () => {
    const schema = S.Struct({
      x: S.String,
      y: S.optionalWith(S.Number, { nullable: true, default: () => 0 })
    })
    const sigs = AST.getPropertySignatures(schema.ast)
    deepStrictEqual(sigs.length, 2)
    deepStrictEqual(sigs.map((s) => s.name as string).sort(), ["x", "y"])
  })

  it("handles a single-key Transformation Struct", () => {
    const schema = S.Struct({
      only: S.optionalWith(S.String, { default: () => "" })
    })
    const sigs = AST.getPropertySignatures(schema.ast)
    deepStrictEqual(sigs.length, 1)
    deepStrictEqual(sigs[0].name, "only")
  })

  it("does NOT regress non-Transformation Struct", () => {
    const schema = S.Struct({ p: S.String, q: S.Number })
    const sigs = AST.getPropertySignatures(schema.ast)
    deepStrictEqual(sigs.length, 2)
    deepStrictEqual(sigs[0].name, "p")
    deepStrictEqual(sigs[1].name, "q")
  })
})
PROBE

cd /tests
python3 -m pytest test_outputs.py -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest_report.json \
    --ctrf /logs/verifier/ctrf.json
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: $PYTEST_RC"
echo "reward: $(cat /logs/verifier/reward.txt)"
