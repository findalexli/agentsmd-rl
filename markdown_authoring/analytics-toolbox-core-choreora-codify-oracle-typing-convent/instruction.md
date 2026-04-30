# chore(ora): codify Oracle typing convention [sc-548140]

Source: [CartoDB/analytics-toolbox-core#602](https://github.com/CartoDB/analytics-toolbox-core/pull/602)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/oracle.md`

## What to add / change

## Summary

Codifies the Oracle typing convention for v1.0 in `.claude/rules/oracle.md`. Replaces the prior ad-hoc "Use CLOB for large JSON arrays" guidance with a structured convention for SQL-native returns.

Shortcut: https://app.shortcut.com/cartoteam/story/548140/research-about-oracle-typing-and-conventions

## The convention

**SQL-native returns use nested table types + pipelined functions for arrays; object types for structs. CLOB JSON reserved for Gateway HTTP wire and named transit-layer exceptions.**

## Rule sections added/updated

- **Type Mapping table** — primitive scalars, geometry (SRID 4326), arrays (`TABLE OF <type>` PIPELINED), structs (`OBJECT` types), array-of-struct (`TABLE OF <object_type>` PIPELINED), opaque payloads (`CLOB`)
- **Pipelined rule** — mandatory for size-variable returns, non-pipelined for fixed-size
- **Type placement** — per-module `00_types.sql` with `00_` prefix for deploy ordering
- **Naming** — module-prefixed type names (`H3_INDEX_ARRAY`, `QUADBIN_INDEX_ARRAY`, etc.)
- **SRID rule** — explicit 4326 on all `SDO_GEOMETRY` outputs
- **NULL-on-invalid rule** — match Snowflake's native-SQL convention
- **Gateway HTTP boundary** — JSON serialization only at the wire, with named transit-layer exceptions (`INTERNAL_GENERIC_HTTP`, `INTERNAL_CREATE_BUILDER_MAP`)
- **`_JSON` suffix reserved** for future dual-form modules (not used in v1.0)
- **Evolution discipline** for object types (minimal fields, additive changes, avoid renames, version-bu

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
