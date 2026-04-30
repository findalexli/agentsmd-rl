#!/usr/bin/env bash
set -euo pipefail

cd /workspace/protein-design-skills

# Idempotency guard
if grep -qF "| `--max-seqs` | 300 | Max hits to pass through prefilter; reducing this affects" "skills/foldseek/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/foldseek/SKILL.md b/skills/foldseek/SKILL.md
@@ -2,7 +2,7 @@
 name: foldseek
 description: >
   Structure similarity search with Foldseek. Use this skill when:
-  (1) Finding similar structures in PDB/AF2 databases,
+  (1) Finding similar structures in PDB/AFDB databases,
   (2) Structural homology search,
   (3) Database queries by 3D structure,
   (4) Finding remote homologs not detected by sequence,
@@ -29,7 +29,7 @@ tags: [search, structure, database, similarity]
 
 **Note**: Foldseek can run locally or via web server. No GPU required.
 
-### Option 1: Web Server (Quick)
+### Option 1: Web Server (Quick; rate-limited, use sparingly)
 ```bash
 # Upload structure to web server
 curl -X POST "https://search.foldseek.com/api/ticket" \
@@ -73,14 +73,14 @@ def foldseek_search(query_pdb, database, output="results.m8"):
 | `--min-seq-id` | 0.0 | Minimum sequence identity |
 | `-e` | 0.001 | E-value threshold |
 | `--alignment-type` | 2 | 0=3Di, 1=TM, 2=3Di+AA |
-| `--max-seqs` | 300 | Max hits to report |
+| `--max-seqs` | 300 | Max hits to pass through prefilter; reducing this affects sensitivity |
 
 ## Databases
 
 | Database | Description | Size |
 |----------|-------------|------|
 | `pdb100` | PDB clustered at 100% | ~200K structures |
-| `afdb50` | AlphaFold DB at 50% | ~200M structures |
+| `afdb50` | AlphaFold DB at 50% | ~67M structures |
 | `swissprot` | SwissProt structures | ~500K structures |
 | `cath50` | CATH domains | ~50K domains |
 
@@ -120,15 +120,11 @@ Should I use Foldseek?
 │  ├─ By sequence → Use BLAST (uniprot skill)
 │  └─ Both → Run both, compare results
 │
-├─ What do you need?
-│  ├─ Find structural homologs → Foldseek ✓
-│  ├─ Remote homolog detection → Foldseek ✓
-│  ├─ Structural clustering → Foldseek ✓
-│  └─ Functional annotation → Cross-reference with UniProt
-│
-└─ Speed vs sensitivity?
-   ├─ Fast → Use 3Di only mode
-   └─ Sensitive → Use 3Di+AA alignment
+└─ What do you need?
+   ├─ Find structural homologs → Foldseek ✓
+   ├─ Remote homolog detection → Foldseek ✓
+   ├─ Structural clustering → Foldseek ✓
+   └─ Functional annotation → Cross-reference with UniProt
 ```
 
 ## Common use cases
@@ -142,7 +138,7 @@ foldseek easy-search design.pdb pdb100 similar_natural.m8 tmp/
 ### Novelty check
 ```bash
 # Ensure design is novel (low similarity to known)
-foldseek easy-search design.pdb afdb50 novelty.m8 tmp/ --max-seqs 10
+foldseek easy-search design.pdb afdb50 novelty.m8 tmp/
 
 # Novel if: top hit identity < 30%
 ```
@@ -168,7 +164,7 @@ wc -l results.m8  # Number of hits
 
 **No hits**: Lower e-value threshold, try larger database
 **Too many hits**: Increase min-seq-id threshold
-**Slow search**: Use smaller database or 3Di-only mode
+**Slow search**: Use smaller database
 
 ### Error interpretation
 
PATCH

echo "Gold patch applied."
