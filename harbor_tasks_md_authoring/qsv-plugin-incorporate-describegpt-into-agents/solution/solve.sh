#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qsv

# Idempotency guard
if grep -qF "See `skills/csv-wrangling/SKILL.md` for the full tool selection matrix and pipel" ".claude/skills/agents/data-analyst.md" && grep -qF "Generate AI-powered documentation for a tabular data file using `describegpt`. P" ".claude/skills/commands/data-describe.md" && grep -qF "10. **Document**: Run `qsv_describegpt` with `all: true` to generate a Data Dict" ".claude/skills/commands/data-profile.md" && grep -qF "| Document dataset | `describegpt` | \u2014 | AI-generated Data Dictionary, Descripti" ".claude/skills/skills/csv-wrangling/SKILL.md" && grep -qF "| **Documentation** | Dataset described? | `describegpt --all` | No Data Diction" ".claude/skills/skills/data-quality/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/agents/data-analyst.md b/.claude/skills/agents/data-analyst.md
@@ -14,6 +14,7 @@ allowed-tools:
   - mcp__qsv__qsv_to_parquet
   - mcp__qsv__qsv_joinp
   - mcp__qsv__qsv_sample
+  - mcp__qsv__qsv_describegpt
   - mcp__qsv__qsv_command
   - mcp__qsv__qsv_search_tools
   - mcp__qsv__qsv_list_files
@@ -56,10 +57,11 @@ Skip this if the user provides absolute file paths or if you're unsure of the wo
 5. **Explore**: Use `qsv_frequency` for distributions, `qsv_slice` for row samples, `qsv_search` for filtering.
 6. **Query**: Use `qsv_sqlp` for SQL-based analysis. **Before writing SQL**, read `.stats.csv` for column types, cardinality, nullcount, min/max ranges, and sort order; run `qsv_frequency` on columns you'll GROUP BY or filter on. Use this data to write precise WHERE clauses, skip unnecessary COALESCE on zero-null columns, and avoid GROUP BY on high-cardinality columns. For CSV > 10MB, convert to Parquet first with `qsv_to_parquet`, then use `read_parquet('file.parquet')` as the table source.
 7. **Report**: Summarize findings clearly with tables, key metrics, and observations.
+8. **Document**: Run `qsv_describegpt` with `all: true` to generate a Data Dictionary, Description, and Tags. Output defaults to `<filestem>.describegpt.md`. Uses the connected LLM automatically via MCP sampling — no API key needed.
 
 ## Analysis Capabilities
 
-See `skills/csv-wrangling/SKILL.md` for the full tool selection matrix and pipeline patterns. Key analysis tools: `qsv_stats`/`qsv_moarstats` (column statistics), `qsv_frequency` (distributions), `qsv_sqlp` (SQL aggregation, joins, window functions), `qsv_search` (regex filtering), `qsv_sample` (random sampling).
+See `skills/csv-wrangling/SKILL.md` for the full tool selection matrix and pipeline patterns. Key analysis tools: `qsv_stats`/`qsv_moarstats` (column statistics), `qsv_frequency` (distributions), `qsv_sqlp` (SQL aggregation, joins, window functions), `qsv_search` (regex filtering), `qsv_sample` (random sampling), `qsv_describegpt` (AI-powered Data Dictionary, Description & Tags).
 
 ## Guidelines
 
diff --git a/.claude/skills/commands/data-describe.md b/.claude/skills/commands/data-describe.md
@@ -0,0 +1,56 @@
+---
+allowed-tools:
+  - mcp__qsv__qsv_sniff
+  - mcp__qsv__qsv_index
+  - mcp__qsv__qsv_stats
+  - mcp__qsv__qsv_headers
+  - mcp__qsv__qsv_count
+  - mcp__qsv__qsv_describegpt
+  - mcp__qsv__qsv_get_working_dir
+  - mcp__qsv__qsv_set_working_dir
+argument-hint: "<file> [--dictionary|--description|--tags|--all]"
+description: Generate AI-powered Data Dictionary, Description, and Tags for a CSV/TSV/Excel file
+---
+
+# Data Describe
+
+Generate AI-powered documentation for a tabular data file using `describegpt`. Produces a Data Dictionary (column labels, descriptions, types), a natural-language Description of the dataset, and semantic Tags — all via the connected LLM (no API key needed in MCP mode).
+
+## Cowork Setup
+
+If running in Claude Code or Cowork, first call `qsv_get_working_dir` to check qsv's current working directory. If it differs from your workspace root (the directory where relative paths should resolve), call `qsv_set_working_dir` to sync it.
+
+## Steps
+
+1. **Index**: Run `qsv_index` on the file for fast random access.
+
+2. **Profile**: Run `qsv_stats` with `cardinality: true, stats_jsonl: true` to generate the stats cache. describegpt reads this cache for column metadata, so it must exist first.
+
+3. **Describe**: Run `qsv_describegpt` with the requested options (recommend `all: true` for comprehensive output). At least one inference option (`dictionary`, `description`, `tags`, or `all`) is required. Output defaults to `<filestem>.describegpt.md`.
+
+4. **Present**: Display the generated Data Dictionary table, Description, and Tags to the user.
+
+## Options
+
+| Option | Effect |
+|--------|--------|
+| `--all` (recommended) | Generate Dictionary + Description + Tags in one pass |
+| `--dictionary` | Data Dictionary only — column labels, descriptions, types |
+| `--description` | Natural-language dataset Description only |
+| `--tags` | Semantic Tags only |
+| `--format` | Output format: `Markdown` (default), `JSON`, `TSV`, `TOON` |
+| `--language` | Generate output in a non-English language (e.g. `Spanish`, `French`) |
+| `--addl-cols-list` | Enrich the dictionary with extra columns (e.g. `"everything"`, `"moar!"`) |
+| `--tag-vocab` | Constrain tags to a controlled vocabulary (comma-separated) |
+| `--num-tags` | Number of tags to generate (default: 5) |
+| `--num-examples` | Number of example values per column in the dictionary |
+| `--enum-threshold` | Max cardinality to treat a column as an enum in the dictionary |
+
+## Notes
+
+- No API key needed in MCP mode — uses the connected LLM automatically via MCP sampling
+- The stats cache must exist first for best results (step 2 creates it)
+- Output defaults to `<filestem>.describegpt.md`
+- For Excel/JSONL files, the MCP server auto-converts to CSV first
+- Use `--format JSON` when you need machine-readable output for downstream processing
+- Use `--language` to generate documentation in the user's preferred language
diff --git a/.claude/skills/commands/data-profile.md b/.claude/skills/commands/data-profile.md
@@ -9,6 +9,7 @@ allowed-tools:
   - mcp__qsv__qsv_frequency
   - mcp__qsv__qsv_slice
   - mcp__qsv__qsv_command
+  - mcp__qsv__qsv_describegpt
   - mcp__qsv__qsv_sqlp
   - mcp__qsv__qsv_get_working_dir
   - mcp__qsv__qsv_set_working_dir
@@ -44,6 +45,8 @@ If running in Claude Code or Cowork, first call `qsv_get_working_dir` to check q
 
 9. **Preview data**: Run `qsv_slice` with `len: 5` to show the first 5 rows as a sample.
 
+10. **Document**: Run `qsv_describegpt` with `all: true` to generate a Data Dictionary, Description, and Tags. Output defaults to `<filestem>.describegpt.md`. This step leverages the stats cache created in step 5. Uses the connected LLM via MCP sampling — no API key needed.
+
 ## Quality Dimensions
 
 When profiling, assess these five dimensions:
@@ -146,6 +149,7 @@ Present a summary with:
 - **Column overview**: table with name, type, nulls, cardinality, min, max, mean (where applicable)
 - **Key observations**: unique identifiers, high-null columns, type mismatches, notable distributions
 - **Data quality flags**: any issues found (high sparsity, mixed types, ragged rows)
+- **Data Dictionary, Description & Tags** (optional): AI-generated documentation from describegpt (step 10)
 
 ### Quality Report Checklist
 
@@ -160,6 +164,7 @@ Present a summary with:
 - [ ] **Schema violations** if schema provided (validity)
 - [ ] **Encoding and delimiter** detected (consistency)
 - [ ] **PII/PHI patterns** detected via searchset (privacy)
+- [ ] **Data Dictionary** generated with column labels, descriptions, and types (describegpt)
 
 ## Common Data Quality Fixes
 
diff --git a/.claude/skills/skills/csv-wrangling/SKILL.md b/.claude/skills/skills/csv-wrangling/SKILL.md
@@ -12,6 +12,7 @@ Always follow this sequence when processing CSV data:
 5. **Transform** - select, sort, dedup, rename, replace, search, sqlp, etc.
 6. **Validate** - `validate` (against JSON Schema), `stats` (verify results)
 7. **Export** - `tojsonl`, `table`, `qsv_to_parquet`
+8. **Document** - `describegpt --all` (AI-generated Data Dictionary, Description & Tags)
 
 ## Tool Selection Matrix
 
@@ -29,6 +30,7 @@ Always follow this sequence when processing CSV data:
 | Reshape long->wide | `pivotp` | `sqlp` | Complex pivots |
 | Concatenate files | `cat rows` | `cat rowskey` | Different column orders |
 | Sample rows | `sample` | `slice` | `slice` for positional ranges |
+| Document dataset | `describegpt` | — | AI-generated Data Dictionary, Description & Tags |
 
 ## qsv Selection Syntax
 
@@ -64,6 +66,11 @@ For CSV > 10MB, convert to Parquet before SQL queries: `sniff -> index -> stats
 index (both files) -> stats (both) -> joinp -> select (keep needed columns) -> sort
 ```
 
+### Profile and Document
+```
+sniff -> index -> stats --cardinality --stats-jsonl -> describegpt --all
+```
+
 ### Convert and Export
 ```
 excel (to CSV) -> index -> stats -> select -> tojsonl / qsv_to_parquet
diff --git a/.claude/skills/skills/data-quality/SKILL.md b/.claude/skills/skills/data-quality/SKILL.md
@@ -11,6 +11,7 @@ For the full step-by-step profiling workflow, use the `/data-profile` command. T
 | **Validity** | Correct formats/types? | `stats` — `type`; `validate schema.json` | String type on numeric column |
 | **Consistency** | Uniform formats? | `frequency` — case variants; `sniff` — encoding | Same value in different cases |
 | **Accuracy** | Plausible values? | `stats` — min/max/stddev | Values > 3 stddev from mean |
+| **Documentation** | Dataset described? | `describegpt --all` | No Data Dictionary or Description |
 
 ## Remediation Decision Tree
 
PATCH

echo "Gold patch applied."
