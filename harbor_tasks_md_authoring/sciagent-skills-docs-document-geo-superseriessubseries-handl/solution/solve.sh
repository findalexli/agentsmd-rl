#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sciagent-skills

# Idempotency guard
if grep -qF "6. **Always resolve SubSeries before analysis**: After loading any GSE, inspect " "skills/genomics-bioinformatics/geo-database/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/genomics-bioinformatics/geo-database/SKILL.md b/skills/genomics-bioinformatics/geo-database/SKILL.md
@@ -229,6 +229,28 @@ print(df.iloc[:3, :3])
 - **GSM** (Sample): A single hybridization or sequencing run
 - **GDS** (Dataset): Curated, normalized subset of a series (fewer than GSE records)
 
+### SuperSeries and SubSeries
+
+Multi-assay or multi-batch submissions (e.g., RNA-seq + ATAC-seq) are organized as a **SuperSeries** GSE that references one or more **SubSeries** GSEs. Each SubSeries holds its own samples, platform, and matrix; the SuperSeries itself has no samples of its own. Both are tagged in `gse.metadata`:
+
+- SuperSeries: `gse.metadata["relation"]` contains entries like `"SuperSeries of: GSExxxx"`
+- SubSeries: `gse.metadata["relation"]` contains `"SubSeries of: GSEyyyy"`
+
+Always resolve SubSeries before pulling an expression matrix — downloading the SuperSeries alone yields metadata but no data.
+
+```python
+import GEOparse
+
+gse = GEOparse.get_GEO("GSE47966", destdir="./geo_data/", silent=True)  # a SuperSeries
+relations = gse.metadata.get("relation", [])
+subseries = [r.split(": ")[1] for r in relations if r.startswith("SuperSeries of")]
+print(f"SubSeries to download: {subseries}")
+
+for acc in subseries:
+    sub = GEOparse.get_GEO(acc, destdir="./geo_data/", silent=True)
+    print(f"  {acc}: {len(sub.gsms)} samples, platforms={list(sub.gpls.keys())}")
+```
+
 ### Soft vs. MiniML Format
 
 GEOparse downloads SOFT-format files (plain text). For XML-based access, use MiniML format via E-utilities. Series Matrix files (tab-delimited) are the most compact format for expression data.
@@ -333,6 +355,8 @@ print(df[["accession", "title", "n_samples"]].head(10).to_string(index=False))
 
 5. **Check platform column names**: GPL annotation table column names vary by platform (e.g., `"Gene Symbol"` vs `"GENE_SYMBOL"` vs `"gene_id"`). Always inspect `gpl.table.columns` before assuming field names.
 
+6. **Always resolve SubSeries before analysis**: After loading any GSE, inspect `gse.metadata.get("relation", [])` for `"SuperSeries of: ..."` entries. If present, iterate every referenced SubSeries accession and download each one — the SuperSeries record itself carries no samples or expression matrices. Skipping this step silently drops the actual data.
+
 ## Common Recipes
 
 ### Recipe: Quick GSE Metadata Peek
@@ -388,6 +412,7 @@ print("First 5:", gsm_ids[:5])
 | Download hangs for large series | Large SOFT file (GB range) | Use FTP Series Matrix download instead of GEOparse for large series |
 | ESearch returns 0 results | Wrong `entry type` or field tag | Switch `gse[entry type]` to `gds[entry type]`; verify query syntax |
 | Numeric sample columns contain `null` | Missing/absent expression values | Fill with `df.fillna(0)` or drop columns with high missingness |
+| GSE has no samples / empty `gse.gsms` | Accession is a SuperSeries | Parse `gse.metadata["relation"]` for `SuperSeries of:` entries and download each SubSeries |
 
 ## Related Skills
 
PATCH

echo "Gold patch applied."
