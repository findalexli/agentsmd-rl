#!/usr/bin/env bash
set -euo pipefail

cd /workspace/analytics-toolbox-core

# Idempotency guard
if grep -qF "Individual test modules (`test_*.py`) must not use `sys.path.insert(...)` or `fr" ".claude/rules/oracle.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/oracle.md b/.claude/rules/oracle.md
@@ -47,20 +47,118 @@ make remove drop-schema=1      # Drop entire schema (destructive)
 
 - Pure SQL functions: `CREATE OR REPLACE FUNCTION ... RETURN ... IS BEGIN ... END;` with `/` terminator
 - PL/SQL blocks with loops for complex functions (KRING, TOCHILDREN, POLYFILL)
-- No SQL BOOLEAN — use `NUMBER` (1/0) for boolean returns
-- Use `CLOB` instead of `VARCHAR2(32767)` for functions producing large JSON arrays
+- Pipelined functions (`RETURN <type> PIPELINED`, `PIPE ROW(...)`) for size-variable array/struct-array returns
+- No SQL BOOLEAN — use `NUMBER(1)` (1/0) for boolean returns; callers use `= 1`
 - `AUTHID CURRENT_USER` (invoker rights) for all procedures
-- Error codes in `-20100` to `-20199` range for data module errors
 
-## Oracle Type Mapping
+## Oracle Type Mapping (v1.0)
 
-| Generic | Oracle | Notes |
-|---------|--------|-------|
-| quadbin index | `NUMBER` | 38-digit precision, safe for 64-bit |
-| h3 index | `VARCHAR2(15)` | Hex string representation |
-| geometry | `SDO_GEOMETRY` | Native spatial type |
-| boolean | `NUMBER` | 1/0 (no SQL BOOLEAN) |
-| JSON struct/array | `VARCHAR2` or `CLOB` | `CLOB` for large results |
+### SQL-native types (consumer-facing functions)
+
+| Generic shape | Oracle type | Notes |
+|---|---|---|
+| scalar INT / FLOAT | `NUMBER` | 38-digit decimal; holds 64-bit ints and floats exactly |
+| scalar BOOL | `NUMBER(1)` (1/0) | no SQL BOOLEAN; callers use `= 1` |
+| scalar STRING | `VARCHAR2` | direct |
+| scalar GEOMETRY / GEOGRAPHY | `SDO_GEOMETRY` with explicit SRID 4326 | matches BQ/SF implicit WGS84 |
+| `ARRAY<primitive>` | `TABLE OF <type>` PIPELINED | consume via `TABLE(func(...))` |
+| `STRUCT<...>` | `OBJECT` type with named fields | access via `t.field_name` |
+| `ARRAY<STRUCT<...>>` | `TABLE OF <object_type>` PIPELINED | consume via `TABLE(func(...))` |
+| unbounded opaque payload | `CLOB` | Gateway transit and named exceptions only |
+
+**Module-specific types**:
+- quadbin index: `NUMBER` (38-digit precision, safe for 64-bit)
+- h3 index: `VARCHAR2(16)` (hex string representation)
+
+### Pipelined rule
+
+Functions whose output size depends on input parameters MUST be pipelined. Fixed-size returns (e.g. `QUADBIN_TOZXY` returning one triple) are non-pipelined scalar-of-object returns.
+
+### Type placement
+
+Types are declared in the same SQL file as the function that uses them, before the function body. Keeps a single point of edit per function and removes the need to track cross-file dependencies.
+
+Shared types (used by multiple functions in a module) go in a dedicated `00_<type_name>.sql` file — the `00_` prefix ensures alphabetical deploy ordering (types before functions that consume them). Module-scoped; promote to `clouds/oracle/libraries/types/` only if a genuine cross-cutting pattern emerges.
+
+### Idempotent type deployment
+
+`CREATE OR REPLACE TYPE` fails with `ORA-02303` when another type depends on the one being replaced (e.g. a `TABLE OF CELL` collection depends on `CELL`). For redeployable type files, drop with `FORCE` in reverse-dependency order first, then create:
+
+```sql
+-- Reset types idempotently. FORCE cascades to invalidate dependent
+-- objects, which are recompiled when recreated later in the deploy.
+BEGIN
+    EXECUTE IMMEDIATE 'DROP TYPE <SCHEMA>.LDS_H3_ISOLINE_CELLS FORCE';
+EXCEPTION WHEN OTHERS THEN NULL;
+END;
+/
+BEGIN
+    EXECUTE IMMEDIATE 'DROP TYPE <SCHEMA>.LDS_H3_ISOLINE_CELL FORCE';
+EXCEPTION WHEN OTHERS THEN NULL;
+END;
+/
+
+CREATE TYPE <SCHEMA>.LDS_H3_ISOLINE_CELL AS OBJECT (...);
+/
+CREATE TYPE <SCHEMA>.LDS_H3_ISOLINE_CELLS AS TABLE OF <SCHEMA>.LDS_H3_ISOLINE_CELL;
+/
+```
+
+The `BEGIN … EXCEPTION WHEN OTHERS THEN NULL; END;` pattern is Oracle's idiom for "DROP IF EXISTS" (no native syntax). Handles fresh deploy (type doesn't exist → caught), redeploy (type exists with dependents → cascade via FORCE), and partial state (one of the types missing) uniformly.
+
+### Naming
+
+Module-prefixed type names: `H3_INDEX_ARRAY`, `H3_DISTANCE_PAIR`, `QUADBIN_INDEX_ARRAY`, `QUADBIN_ZXY`, etc. Avoids schema-wide collisions and documents ownership.
+
+### SRID rule
+
+All `SDO_GEOMETRY` outputs set SRID 4326 explicitly in the constructor. Input-accepting functions document the WGS84 assumption (no auto-transform in v1.0).
+
+### NULL-on-invalid rule
+
+Functions return NULL (not raise) for invalid-but-type-correct inputs (e.g. `TOPARENT(idx, -1)` → `NULL`, not `ORA-20001`). Matches Snowflake's native-SQL convention. BigQuery throws only because its UDFs run in JavaScript; Oracle PL/SQL follows Snowflake.
+
+### Gateway HTTP boundary
+
+Data exits Oracle as JSON only at the Gateway HTTP wire. Collections serialize to JSON CLOB there; SQL-native Oracle callers never see raw JSON. `INTERNAL_GENERIC_HTTP`, `INTERNAL_CREATE_BUILDER_MAP`, and similar transit-layer functions are explicit exceptions — their job *is* the transit.
+
+### `_JSON` suffix reserved
+
+If a module needs both a nested-table primary AND an explicit CLOB JSON variant for a non-Gateway JSON consumer, the JSON variant takes the `_JSON` suffix (e.g. `H3_TOCHILDREN_JSON`). No function in v1.0 needs this.
+
+### Evolution discipline
+
+Object types and nested tables are harder to evolve than JSON:
+- Keep object types minimal — only the fields needed now
+- Prefer additive changes (`ALTER TYPE ADD ATTRIBUTE`) over replacement
+- Avoid renames (rename = drop + create + cascade)
+- Breaking type changes bump the module's major version
+
+### Canonical consumer idiom
+
+```sql
+-- Array of primitives
+SELECT COLUMN_VALUE AS h3
+FROM TABLE(CARTO.H3_TOCHILDREN('85283473fffffff', 10));
+
+-- Array of struct
+SELECT p.h3_index, p.distance
+FROM TABLE(CARTO.H3_KRING_DISTANCES('85283473fffffff', 2)) p;
+
+-- Fixed-size struct
+WITH t AS (SELECT CARTO.QUADBIN_TOZXY(q) AS zxy FROM DUAL)
+SELECT zxy.z, zxy.x, zxy.y FROM t;
+```
+
+## Oracle Test Patterns
+
+Test files use the shared helpers:
+
+```python
+from test_utils import run_query, drop_table
+```
+
+Individual test modules (`test_*.py`) must not use `sys.path.insert(...)` or `from run_query import run_query`. These patterns are bootstrap-level infrastructure and belong only in `__init__.py` package initializers — specifically `clouds/oracle/modules/test/__init__.py` (the pytest root) and `clouds/oracle/common/test_utils/__init__.py` (the shared helpers). Test modules should only import from `test_utils`.
 
 ## Oracle Native H3 Functions
 
@@ -71,15 +169,15 @@ These return `RAW(8)` — use `RAWTOHEX`/`HEXTORAW` to bridge to `VARCHAR2` hex
 
 ## Dynamic SQL in Procedures
 
-Use Q-literal multiline strings with `REPLACE`-based named placeholders:
+Use string concatenation (`||`) for dynamic SQL — consistent with Redshift, Snowflake, BigQuery, and Postgres patterns in this repo.
+
+For data values, prefer bind variables (`EXECUTE IMMEDIATE ... USING`) over concatenation — avoids escaping and injection issues. Identifier interpolation (table/schema names in DDL) still requires concatenation since DDL can't bind names.
 
 ```sql
-v_sql := q'[
-    SELECT * FROM #INPUT_TABLE# WHERE #CONDITION#
-]';
-v_sql := REPLACE(v_sql, '#INPUT_TABLE#', p_input_table);
-v_sql := REPLACE(v_sql, '#CONDITION#', v_condition);
-EXECUTE IMMEDIATE v_sql;
+-- Identifier concatenated; data values bound
+v_sql := 'CREATE TABLE ' || p_output_table || ' AS
+    SELECT :val AS label FROM DUAL';
+EXECUTE IMMEDIATE v_sql USING p_value;
 ```
 
-Preferred over `UTL_LMS.FORMAT_MESSAGE` (limited to 5 args).
+Avoid `REPLACE`-based placeholder patterns (e.g. `#INPUT_TABLE#`): collisions with interpolated data that contain the placeholder sentinel cause silent corruption.
PATCH

echo "Gold patch applied."
