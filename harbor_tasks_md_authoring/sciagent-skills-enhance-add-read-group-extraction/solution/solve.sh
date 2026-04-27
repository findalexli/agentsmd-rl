#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sciagent-skills

# Idempotency guard
if grep -qF "description: \"Read/write SAM/BAM/CRAM alignments, VCF/BCF variants, FASTA/FASTQ " "skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md b/skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: pysam-genomic-files
-description: "Read/write SAM/BAM/CRAM alignments, VCF/BCF variants, FASTA/FASTQ sequences. Region queries, coverage/pileup analysis, variant filtering. Python wrapper for htslib with samtools/bcftools CLI access. For alignment pipelines use STAR/BWA; for variant calling use GATK/DeepVariant."
+description: "Read/write SAM/BAM/CRAM alignments, VCF/BCF variants, FASTA/FASTQ sequences. Region queries, coverage/pileup analysis, variant filtering, read group extraction. Python wrapper for htslib with samtools/bcftools CLI access. For alignment pipelines use STAR/BWA; for variant calling use GATK/DeepVariant."
 license: MIT
 ---
 
@@ -177,7 +177,93 @@ with pysam.FastxFile("reads.fastq.gz") as fq:
             break
 ```
 
-### 5. Samtools/Bcftools CLI Access
+### 5. Read Groups and Sample Information
+
+Extract and filter reads by read group (essential for multi-sample BAM files).
+
+```python
+import pysam
+
+bam = pysam.AlignmentFile("multisample.bam", "rb")
+
+# Access read group information from BAM header
+print("Read groups in file:")
+for rg_dict in bam.header.get("RG", []):
+    print(f"  ID: {rg_dict['ID']}, Sample: {rg_dict.get('SM', 'N/A')}, Library: {rg_dict.get('LB', 'N/A')}, Platform: {rg_dict.get('PL', 'N/A')}")
+
+# Get all samples in the BAM (from RG headers)
+samples = set()
+for rg_dict in bam.header.get("RG", []):
+    if "SM" in rg_dict:
+        samples.add(rg_dict["SM"])
+print(f"Samples in BAM: {sorted(samples)}")
+
+bam.close()
+```
+
+
+
+```python
+# Filter reads by read group ID
+def extract_reads_by_rg(bam_path, rg_id, output_path):
+    """Extract all reads from a specific read group.
+
+    WARNING: Uses fetch(until_eof=True), which scans the entire BAM sequentially.
+    Multi-sample BAMs can be tens to hundreds of GB — this may be slow.
+    For large files, prefer region-based filtering:
+        for read in bam.fetch("chr1", start, end): ...
+    Or use the samtools CLI equivalent (faster for one-off extractions):
+        samtools view -b -r <rg_id> input.bam -o output.bam
+    """
+    with pysam.AlignmentFile(bam_path, "rb") as bam_in:
+        with pysam.AlignmentFile(output_path, "wb", header=bam_in.header) as bam_out:
+            for read in bam_in.fetch(until_eof=True):
+                if read.has_tag("RG") and read.get_tag("RG") == rg_id:
+                    bam_out.write(read)
+    pysam.index(output_path)
+    print(f"Extracted reads from RG:{rg_id} → {output_path}")
+
+extract_reads_by_rg("multisample.bam", "SAMPLE_001_LaneA", "sample001_laneA.bam")
+```
+
+```python
+from collections import defaultdict
+import pysam
+
+# Count reads per sample
+def reads_per_sample(bam_path):
+    """Count reads per sample from read group information.
+
+    Two distinct "unknown" cases are tracked separately:
+    - "no_sm_field":  RG header entry exists but is missing the SM (sample name) field.
+    - "undefined_rg": A read carries an RG tag not declared in the BAM header.
+    """
+    counts = defaultdict(int)
+    rg_to_sample = {}
+
+    with pysam.AlignmentFile(bam_path, "rb") as bam:
+        # Build RG → sample mapping from header
+        for rg_dict in bam.header.get("RG", []):
+            rg_id = rg_dict["ID"]
+            # (a) RG header entry lacks SM field
+            rg_to_sample[rg_id] = rg_dict.get("SM", "no_sm_field")
+
+        # Count reads per resolved sample name
+        for read in bam.fetch(until_eof=True):
+            if read.has_tag("RG"):
+                rg_id = read.get_tag("RG")
+                # (b) Read's RG tag is not declared in the header
+                sample = rg_to_sample.get(rg_id, "undefined_rg")
+                counts[sample] += 1
+
+    return dict(counts)
+
+sample_counts = reads_per_sample("multisample.bam")
+for sample, count in sorted(sample_counts.items()):
+    print(f"  {sample}: {count:,} reads")
+```
+
+### 6. Samtools/Bcftools CLI Access
 
 Call samtools and bcftools commands from Python.
 
@@ -396,6 +482,7 @@ for k, v in summary.items():
 | `PileupProxy accessed after iterator finished` | Pileup iterator went out of scope | Store needed data from pileup columns immediately, don't save PileupProxy references |
 | `SamtoolsError` from CLI calls | Invalid arguments or missing input | Wrap in `try/except pysam.SamtoolsError`; check samtools docs for argument syntax |
 | Very slow iteration | Iterating all reads without region query | Use `fetch("chr1", start, end)` for targeted queries; use indexed files |
+| Read group filter returns 0 reads | RG tag missing or wrong ID specified | Verify RG tag exists: `read.has_tag("RG")`; list available RGs from `bam.header.get("RG", [])` |
 
 ## Related Skills
 
PATCH

echo "Gold patch applied."
