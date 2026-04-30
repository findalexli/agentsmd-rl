#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qsv

# Idempotency guard
if grep -qF "4. **Inspect** - `slice --len 5` (preview rows), `frequency --frequency-jsonl` (" ".claude/skills/skills/csv-wrangling/SKILL.md" && grep -qF "| Row lengths | `fixlengths` | Pads short rows to match longest row; compare cou" ".claude/skills/skills/data-quality/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/skills/csv-wrangling/SKILL.md b/.claude/skills/skills/csv-wrangling/SKILL.md
@@ -8,10 +8,10 @@ Always follow this sequence when processing CSV data:
 1. **Discover** - `sniff` (detect format, encoding, delimiter) -> `headers` -> `count`
 2. **Index** - `index` (enables fast random access for subsequent commands)
 3. **Profile** - `stats --cardinality --stats-jsonl` (creates cache used by smart commands)
-4. **Inspect** - `slice --len 5` (preview rows), `frequency` (value distributions)
+4. **Inspect** - `slice --len 5` (preview rows), `frequency --frequency-jsonl` (value distributions with cache for reuse)
 5. **Transform** - select, sort, dedup, apply, rename, search, etc.
 6. **Validate** - `validate` (against JSON Schema), `stats` (verify results)
-7. **Export** - `to` (Parquet, XLSX, etc.), `tojsonl`, `table`
+7. **Export** - `to` (XLSX, ODS, etc.), `tojsonl`, `table`
 
 ## Tool Selection Matrix
 
@@ -22,10 +22,10 @@ Always follow this sequence when processing CSV data:
 | Sort data | `sort` | `sqlp` | Need ORDER BY with LIMIT |
 | Remove duplicates | `dedup` | `sqlp` | Need GROUP BY dedup |
 | Join two files | `joinp` | `join` | `join` for memory-constrained |
-| Aggregate/GROUP BY | `sqlp` | `frequency` | `frequency` for simple counts |
+| Aggregate/GROUP BY | `sqlp` | `frequency` | `frequency` for simple counts; `--frequency-jsonl` creates cache |
 | Column stats | `stats` | `moarstats` | `moarstats` for extended stats |
 | Find/replace | `apply operations` | `sqlp` | `sqlp` for conditional replace |
-| Reshape wide->long | `melt` | `sqlp` | Complex reshaping |
+| Reshape wide->long | `transpose --long` | - | DuckDB UNPIVOT (external) for complex reshaping |
 | Reshape long->wide | `pivotp` | `sqlp` | Complex pivots |
 | Concatenate files | `cat rows` | `cat rowskey` | Different column orders |
 | Sample rows | `sample` | `slice` | `slice` for positional ranges |
@@ -64,7 +64,7 @@ index (both files) -> stats (both) -> joinp -> select (keep needed columns) -> s
 
 ### Convert and Export
 ```
-excel (to CSV) -> index -> stats -> select -> to parquet/xlsx
+excel (to CSV) -> index -> stats -> select -> to ods/xlsx
 ```
 
 ## Delimiter Handling
diff --git a/.claude/skills/skills/data-quality/SKILL.md b/.claude/skills/skills/data-quality/SKILL.md
@@ -45,7 +45,7 @@
 | Case consistency | `frequency` | "NYC" vs "nyc" vs "Nyc" as separate values |
 | Encoding | `sniff` | Non-UTF-8 encoding detected |
 | Delimiters | `sniff` | Unexpected delimiter or quoting |
-| Row lengths | `fixlengths --count` | Rows with wrong number of fields |
+| Row lengths | `fixlengths` | Pads short rows to match longest row; compare count before/after to detect ragged rows |
 
 **Red flag**: Frequency shows same value in different cases/formats.
 
@@ -70,7 +70,7 @@
 4. stats --cardinality --stats-jsonl -> Full statistical profile
 5. frequency       -> Value distribution for categorical columns
 6. validate        -> Schema validation (if schema available)
-7. fixlengths --count -> Check for ragged rows
+7. fixlengths      -> Pad short rows to uniform length (compare count before/after to detect ragged rows)
 ```
 
 ## Quality Report Checklist
@@ -97,5 +97,5 @@ After profiling, report on:
 | Ragged rows | `fixlengths` |
 | Unsafe column names | `safenames` |
 | Wrong encoding | `input` (normalizes to UTF-8) |
-| Empty value replacement | `apply emptyreplace "N/A" col` |
+| Empty values | `apply emptyreplace col --replacement "N/A"` |
 | Invalid rows | `validate schema.json` + filter |
PATCH

echo "Gold patch applied."
