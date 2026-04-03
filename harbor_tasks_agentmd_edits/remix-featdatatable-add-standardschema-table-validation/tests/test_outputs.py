"""
Task: remix-featdatatable-add-standardschema-table-validation
Repo: remix-run/remix @ 89db125c56d3b0d637a283ac9122c6cb8f5542c3
PR:   11067

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/remix"

TABLE_TS = f"{REPO}/packages/data-table/src/lib/table.ts"
DATABASE_TS = f"{REPO}/packages/data-table/src/lib/database.ts"
INDEX_TS = f"{REPO}/packages/data-table/src/index.ts"
AGENTS_MD = f"{REPO}/AGENTS.md"
README_MD = f"{REPO}/packages/data-table/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must be valid (no obvious syntax errors)."""
    for path in [TABLE_TS, DATABASE_TS, INDEX_TS]:
        src = Path(path).read_text()
        assert len(src.strip()) > 0, f"{path} is empty"
        assert src.count("{") == src.count("}"), f"{path} has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_table_standard_schema_property():
    """createTable must attach a ~standard property to the table object via defineProperty."""
    src = Path(TABLE_TS).read_text()

    # createTable must use Object.defineProperty to set '~standard' on the table
    # (the base already has ~standard in timestampSchema, but NOT on the table object itself)
    assert re.search(
        r"Object\.defineProperty\s*\(\s*table\s*,\s*['\"]~standard['\"]", src
    ), (
        "createTable must use Object.defineProperty to attach '~standard' to the table object"
    )

    # The Table type must declare ~standard in its type definition
    assert re.search(r"['\"]~standard['\"]:\s*Schema", src), (
        "Table type must include '~standard': Schema in its type definition"
    )


# [pr_diff] fail_to_pass
def test_table_validate_partial_row_input_function():
    """table.ts must have a validatePartialRowInput helper that powers both ~standard and writes."""
    src = Path(TABLE_TS).read_text()

    # Must define validatePartialRowInput as the shared validation core
    # This is the internal function that both ~standard.validate and validatePartialRow call
    assert re.search(r"function\s+validatePartialRowInput", src), (
        "table.ts must define a validatePartialRowInput function as shared validation core"
    )

    # validatePartialRowInput must accept table name, columns, and value params
    match = re.search(
        r"function\s+validatePartialRowInput[^{]*\{([\s\S]*?)(?=\nfunction\s|\nexport\s+function\s|\Z)",
        src,
    )
    assert match, "validatePartialRowInput function body not found"
    body = match.group(1)

    # Must handle non-object input
    assert "object" in body or "Array.isArray" in body, (
        "validatePartialRowInput must guard against non-object input"
    )

    # Must use parseSafe for column-level validation
    assert "parseSafe" in body, (
        "validatePartialRowInput must use parseSafe to validate individual column values"
    )


# [pr_diff] fail_to_pass
def test_validate_partial_row_exported():
    """validatePartialRow must be exported from table.ts as a public API."""
    src = Path(TABLE_TS).read_text()

    # Must have an exported validatePartialRow function
    assert re.search(r"export\s+function\s+validatePartialRow", src), (
        "validatePartialRow must be exported from table.ts"
    )


# [pr_diff] fail_to_pass
def test_write_path_uses_shared_validator():
    """database.ts must import validatePartialRow from table.ts for write validation."""
    src = Path(DATABASE_TS).read_text()

    # Must import validatePartialRow from table.ts
    assert re.search(r"import.*validatePartialRow.*from\s+['\"]\.\/table", src, re.DOTALL), (
        "database.ts must import validatePartialRow from './table'"
    )

    # Must call validatePartialRow (shared validation, not inline reimplementation)
    assert re.search(r"validatePartialRow\s*\(", src), (
        "database.ts must call validatePartialRow for write validation"
    )


# [pr_diff] fail_to_pass
def test_dataschemma_type_removed_from_exports():
    """DataSchema type must NOT be re-exported from data-table's public index.ts."""
    src = Path(INDEX_TS).read_text()

    # DataSchema was previously exported; it must now be removed
    # Check that DataSchema does not appear in any export statement
    export_lines = [line for line in src.splitlines() if "export" in line]
    for line in export_lines:
        assert "DataSchema" not in line, (
            "DataSchema must not be re-exported from index.ts — "
            "consumers should import Schema from data-schema directly"
        )


# [pr_diff] fail_to_pass
def test_timestamp_schema_uses_create_schema():
    """timestampSchema must use createSchema from data-schema instead of inline ~standard."""
    src = Path(TABLE_TS).read_text()

    # Must import createSchema from data-schema
    assert re.search(r"import.*createSchema.*from\s+['\"]@remix-run/data-schema['\"]", src, re.DOTALL), (
        "table.ts must import createSchema from @remix-run/data-schema"
    )

    # timestampSchema function must call createSchema
    # Find the timestampSchema function body
    match = re.search(r"function\s+timestampSchema\s*\([^)]*\)[^{]*\{([\s\S]*?)\n\}", src)
    assert match, "timestampSchema function not found"
    body = match.group(1)
    assert "createSchema" in body, (
        "timestampSchema must use createSchema instead of inline ~standard object"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/doc update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must mention "cross-package" — this phrase is unique to the new rule
    # (the base AGENTS.md has "re-exporting" but in a different context about src/lib)
    assert "cross-package" in content_lower, (
        "AGENTS.md must document a cross-package boundary rule"
    )

    # Must convey the rule: avoid re-exporting from other packages
    # Check for the concept of avoiding/not re-exporting across packages
    has_avoid_reexport = "avoid" in content_lower and "re-export" in content_lower
    has_no_reexport = ("don't" in content_lower or "do not" in content_lower or "avoid" in content_lower) and "re-export" in content_lower
    has_import_directly = "import" in content_lower and "directly" in content_lower
    assert has_avoid_reexport or has_no_reexport or has_import_directly, (
        "AGENTS.md must state that re-exporting from other packages should be avoided"
    )


# [config_edit] fail_to_pass

    # Must have a section about data validation
    assert "data validation" in content_lower or "validation" in content_lower.split("##")[1:] != [], (
        "README must have a section about data validation"
    )

    # Must mention Standard Schema
    assert "standard schema" in content_lower, (
        "README must mention Standard Schema compatibility"
    )

    # Must mention parseSafe or parse from data-schema (showing how to use table as schema)
    assert "parsesafe" in content_lower or "parse(" in content_lower, (
        "README must show how to use parseSafe/parse with tables"
    )

    # Must explain key validation semantics
    assert "partial" in content_lower, (
        "README must explain that partial objects are accepted"
    )
    assert "unknown" in content_lower, (
        "README must explain that unknown columns are rejected"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_table_still_exports_core_api():
    """Core table API (createTable, hasMany, etc.) must remain exported."""
    src = Path(TABLE_TS).read_text()
    assert re.search(r"export\s+function\s+createTable", src), (
        "createTable must still be exported"
    )
    assert re.search(r"export\s+function\s+hasMany", src), (
        "hasMany must still be exported"
    )
    assert re.search(r"export\s+function\s+hasOne", src), (
        "hasOne must still be exported"
    )
    assert re.search(r"export\s+function\s+belongsTo", src), (
        "belongsTo must still be exported"
    )
