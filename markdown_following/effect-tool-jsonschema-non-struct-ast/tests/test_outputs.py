"""Behavioral and pass-to-pass tests for effect-ts/effect PR #6094.

The PR removes a defensive `props.length === 0` short-circuit in
`Tool.getJsonSchemaFromSchemaAst`. With the check in place, any AST whose
`AST.getPropertySignatures` returns 0 properties (e.g. a primitive
`Schema.Number`) is incorrectly mapped to a placeholder empty-object schema.
After the fix, `JsonSchema.fromAST` is invoked unconditionally and produces
the correct JSON schema for the input AST.
"""

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/effect")
AI_PKG = REPO / "packages" / "ai" / "ai"

REPRO_TS = textwrap.dedent("""\
    import * as Schema from "effect/Schema"
    import * as Tool from "@effect/ai/Tool"

    const out: Record<string, unknown> = {}

    // 1. Primitive (non-struct) AST
    out.numberSchema = Tool.getJsonSchemaFromSchemaAst(Schema.Number.ast as any)

    // 2. String primitive
    out.stringSchema = Tool.getJsonSchemaFromSchemaAst(Schema.String.ast as any)

    // 3. Boolean primitive
    out.boolSchema = Tool.getJsonSchemaFromSchemaAst(Schema.Boolean.ast as any)

    // 4. Struct with optionalWith default (issue #6085 reproducer)
    const StructWithDefault = Schema.Struct({
      name: Schema.String,
      count: Schema.optionalWith(Schema.Number, { default: () => 10 }),
    })
    out.structDefault = Tool.getJsonSchemaFromSchemaAst(StructWithDefault.ast as any)

    // 5. Plain struct (sanity — should still work either way)
    const PlainStruct = Schema.Struct({ a: Schema.String, b: Schema.Number })
    out.plainStruct = Tool.getJsonSchemaFromSchemaAst(PlainStruct.ast as any)

    process.stdout.write("===JSON===" + JSON.stringify(out) + "===END===\\n")
""")


def _run_repro() -> dict:
    target = AI_PKG / "_pr6094_repro.ts"
    target.write_text(REPRO_TS)
    try:
        r = subprocess.run(
            ["tsx", "_pr6094_repro.ts"],
            cwd=str(AI_PKG),
            capture_output=True,
            text=True,
            timeout=120,
        )
    finally:
        try:
            target.unlink()
        except FileNotFoundError:
            pass
    assert r.returncode == 0, (
        f"tsx repro script failed (rc={r.returncode}).\n"
        f"stdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-1000:]}"
    )
    marker_start = r.stdout.find("===JSON===")
    marker_end = r.stdout.find("===END===")
    assert marker_start != -1 and marker_end != -1, (
        f"missing markers in tsx output:\n{r.stdout}"
    )
    payload = r.stdout[marker_start + len("===JSON==="):marker_end]
    return json.loads(payload)


# ---------------------------------------------------------------------------
# Fail-to-pass: behavior change introduced by the PR
# ---------------------------------------------------------------------------

def test_number_ast_returns_number_schema():
    """Schema.Number.ast must produce a `type: number` schema, not a
    placeholder empty-object schema."""
    out = _run_repro()
    s = out["numberSchema"]
    assert isinstance(s, dict), f"unexpected type: {type(s).__name__}"
    placeholder = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }
    assert s != placeholder, (
        "Tool.getJsonSchemaFromSchemaAst still returns the empty-object "
        "placeholder for primitive ASTs; the defensive short-circuit was "
        f"not removed. Got: {s!r}"
    )
    assert s.get("type") == "number", (
        f"expected JSON Schema with type=number for Schema.Number.ast, got: {s!r}"
    )


def test_string_ast_returns_string_schema():
    """Schema.String.ast must produce a `type: string` schema."""
    out = _run_repro()
    s = out["stringSchema"]
    assert isinstance(s, dict)
    assert s.get("type") == "string", (
        f"expected type=string for Schema.String.ast, got: {s!r}"
    )


def test_boolean_ast_returns_boolean_schema():
    """Schema.Boolean.ast must produce a `type: boolean` schema."""
    out = _run_repro()
    s = out["boolSchema"]
    assert isinstance(s, dict)
    assert s.get("type") == "boolean", (
        f"expected type=boolean for Schema.Boolean.ast, got: {s!r}"
    )


def test_struct_with_default_still_works():
    """Sanity: Schema.Struct with optionalWith({default}) keeps producing
    a proper object schema (no regression for struct ASTs)."""
    out = _run_repro()
    s = out["structDefault"]
    assert isinstance(s, dict)
    assert s.get("type") == "object", f"expected object schema, got: {s!r}"
    props = s.get("properties") or {}
    assert "name" in props, f"missing 'name' in properties: {s!r}"
    assert "count" in props, f"missing 'count' in properties: {s!r}"
    required = s.get("required") or []
    assert "name" in required, f"'name' should be required: {s!r}"
    # 'count' has a default -> not in required
    assert "count" not in required, f"'count' must NOT be required: {s!r}"


def test_plain_struct_still_works():
    """Sanity: regular structs continue to produce object schemas with
    both fields present and required."""
    out = _run_repro()
    s = out["plainStruct"]
    assert isinstance(s, dict)
    assert s.get("type") == "object"
    props = s.get("properties") or {}
    assert set(props.keys()) >= {"a", "b"}, f"missing fields: {s!r}"
    required = set(s.get("required") or [])
    assert {"a", "b"} <= required, f"both fields should be required: {s!r}"


# ---------------------------------------------------------------------------
# Agent-config: AGENTS.md "All pull requests must include a changeset"
# ---------------------------------------------------------------------------

def test_changeset_added_for_change():
    """AGENTS.md mandates a changeset entry for every PR. After the agent's
    edit the .changeset/ directory must contain a new markdown entry beyond
    the empty README.md baseline of the base commit."""
    changeset_dir = REPO / ".changeset"
    assert changeset_dir.is_dir(), f".changeset/ missing at {changeset_dir}"
    md_files = [
        p for p in changeset_dir.iterdir()
        if p.suffix == ".md" and p.name.lower() != "readme.md"
    ]
    assert len(md_files) >= 1, (
        f"expected at least one new changeset *.md file in {changeset_dir} "
        f"per AGENTS.md, found: {[p.name for p in changeset_dir.iterdir()]}"
    )
    # The file must reference @effect/ai (the package being changed)
    has_ai = any("@effect/ai" in p.read_text() for p in md_files)
    assert has_ai, (
        "no changeset references @effect/ai package; per AGENTS.md the "
        "changeset must describe the change to the affected package."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: existing repo tests for the affected file
# ---------------------------------------------------------------------------

def test_repo_tool_tests_pass():
    """The existing @effect/ai Tool test suite must still pass."""
    r = subprocess.run(
        ["pnpm", "--filter=@effect/ai", "test", "run", "Tool.test.ts"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"@effect/ai Tool tests failed (rc={r.returncode}).\n"
        f"stdout tail:\n{r.stdout[-1500:]}\nstderr tail:\n{r.stderr[-500:]}"
    )
