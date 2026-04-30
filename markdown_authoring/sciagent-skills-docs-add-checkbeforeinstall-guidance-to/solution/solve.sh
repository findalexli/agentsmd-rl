#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sciagent-skills

# Idempotency guard
if grep -qF "- [ ] **Check-before-install**: Prerequisites sections for CLI executables inclu" "CLAUDE.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/bcftools-variant-manipulation/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/bedtools-genomic-intervals/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/biopython-sequence-analysis/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/bwa-mem2-dna-aligner/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/cnvkit-copy-number/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/etetoolkit/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/fastp-fastq-preprocessing/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/featurecounts-rna-counting/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/gatk-variant-calling/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/homer-motif-analysis/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/macs3-peak-calling/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/multiqc-qc-reports/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available (e.g., inside a" "skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/prokka-genome-annotation/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/salmon-rna-quantification/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/samtools-bam-processing/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/snpeff-variant-annotation/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/genomics-bioinformatics/star-rna-seq-aligner/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/scientific-computing/nextflow-workflow-engine/SKILL.md" && grep -qF "> **Check before installing**: The tool may already be available in the current " "skills/scientific-computing/snakemake-workflow-engine/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -275,6 +275,7 @@ Before finalizing any entry, verify:
 - [ ] **URL verification**: spot-check primary URLs against official project. Do NOT invent repository URLs
 - [ ] No verbatim copy-paste from sources (synthesize and attribute)
 - [ ] No promotional or advertising content
+- [ ] **Check-before-install**: Prerequisites sections for CLI executables include a note telling the agent to run `command -v <tool>` first and skip the install commands if the tool is already present (e.g., inside a `pixi` / `conda` env), and to invoke tools via `pixi run <tool>` when inside a pixi project
 - [ ] `registry.yaml` updated with new entry
 - [ ] Cross-cutting tools: secondary categories noted in description field
 - [ ] (migrations) Capability completeness, pitfall migration, narrative use-case disposition, stub detection checks completed
diff --git a/skills/genomics-bioinformatics/bcftools-variant-manipulation/SKILL.md b/skills/genomics-bioinformatics/bcftools-variant-manipulation/SKILL.md
@@ -29,6 +29,8 @@ bcftools is the standard command-line toolkit for processing VCF (Variant Call F
 - **Input requirements**: VCF or BGzipped+tabix-indexed VCF (`.vcf.gz + .vcf.gz.tbi`) for region queries
 - **Companion tools**: `samtools` for BAM processing; `tabix` for VCF indexing
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v bcftools` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run bcftools` rather than bare `bcftools`.
+
 ```bash
 # Bioconda (recommended — installs HTSlib suite)
 conda install -c bioconda bcftools
diff --git a/skills/genomics-bioinformatics/bedtools-genomic-intervals/SKILL.md b/skills/genomics-bioinformatics/bedtools-genomic-intervals/SKILL.md
@@ -29,6 +29,8 @@ bedtools is the standard toolkit for operating on genomic intervals in BED, BAM,
 - **Input requirements**: BED/BAM/GFF/VCF files; FASTA reference for `getfasta`; genome file (chromosome sizes) for `slop`/`flank`/`genomecov`
 - **Sorting**: Most operations require coordinate-sorted input
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v bedtools` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run bedtools` rather than bare `bedtools`.
+
 ```bash
 # Bioconda (recommended)
 conda install -c bioconda bedtools
diff --git a/skills/genomics-bioinformatics/biopython-sequence-analysis/SKILL.md b/skills/genomics-bioinformatics/biopython-sequence-analysis/SKILL.md
@@ -32,6 +32,8 @@ For PCR primer design, restriction enzyme digestion, cloning simulation, protein
 - **NCBI access**: Set `Entrez.email` before any E-utilities call; obtain a free API key at https://www.ncbi.nlm.nih.gov/account/ for 10 req/s (default is 3 req/s)
 - **Local BLAST**: BLAST+ installed separately (`conda install -c bioconda blast`) for offline searches
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v python` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run python` rather than bare `python`.
+
 ```bash
 pip install biopython numpy matplotlib
 conda install -c bioconda blast  # optional, for local BLAST
diff --git a/skills/genomics-bioinformatics/bwa-mem2-dna-aligner/SKILL.md b/skills/genomics-bioinformatics/bwa-mem2-dna-aligner/SKILL.md
@@ -26,6 +26,8 @@ BWA-MEM2 aligns short DNA reads (Illumina, 50–250 bp) to a reference genome us
 - **Reference**: genome FASTA (e.g., GRCh38, hg19, mm10)
 - **RAM**: ~28 GB for human genome index; 6–8 GB for mouse
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v bwa-mem2` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run bwa-mem2` rather than bare `bwa-mem2`.
+
 ```bash
 # Install with conda (recommended)
 conda install -c bioconda bwa-mem2 samtools
diff --git a/skills/genomics-bioinformatics/cnvkit-copy-number/SKILL.md b/skills/genomics-bioinformatics/cnvkit-copy-number/SKILL.md
@@ -28,6 +28,8 @@ CNVkit detects somatic copy number variants (CNVs) from whole-exome sequencing (
 - **Input files**: sorted, indexed BAM files (tumor ± matched normal); BED file of capture targets; reference genome FASTA; access to R with DNAcopy package for CBS
 - **Data requirements**: minimum ~50× mean target coverage for WES; WGS works at 20-30×
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v cnvkit.py` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run cnvkit.py` rather than bare `cnvkit.py`.
+
 ```bash
 # Install CNVkit via conda (recommended — handles R/DNAcopy dependency)
 conda install -c bioconda cnvkit
diff --git a/skills/genomics-bioinformatics/etetoolkit/SKILL.md b/skills/genomics-bioinformatics/etetoolkit/SKILL.md
@@ -27,6 +27,8 @@ ETE Toolkit (ETE3) is a Python framework for phylogenetic tree exploration, mani
 - **Data requirements**: Newick string or tree file; NCBI taxonomy database (downloaded on first use for NCBI module)
 - **Environment**: Python 3.6+; PyQt5 required for `TreeStyle` rendering and interactive GUI; headless rendering requires `xvfb`
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v python` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run python` rather than bare `python`.
+
 ```bash
 pip install ete3 numpy lxml PyQt5
 # For headless rendering on Linux servers:
diff --git a/skills/genomics-bioinformatics/fastp-fastq-preprocessing/SKILL.md b/skills/genomics-bioinformatics/fastp-fastq-preprocessing/SKILL.md
@@ -25,6 +25,8 @@ fastp performs adapter trimming, quality filtering, and QC reporting for Illumin
 - **Software**: fastp (conda or pre-compiled binary)
 - **Input**: raw Illumina FASTQ files (single-end or paired-end, .fastq or .fastq.gz)
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v fastp` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run fastp` rather than bare `fastp`.
+
 ```bash
 # Install with conda
 conda install -c bioconda fastp
diff --git a/skills/genomics-bioinformatics/featurecounts-rna-counting/SKILL.md b/skills/genomics-bioinformatics/featurecounts-rna-counting/SKILL.md
@@ -25,6 +25,8 @@ featureCounts (part of the Subread package) assigns sequencing reads in BAM file
 - **Software**: Subread package (contains `featureCounts`)
 - **Input**: Sorted BAM files from STAR or HISAT2, plus a matching GTF annotation file
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v featureCounts` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run featureCounts` rather than bare `featureCounts`.
+
 ```bash
 # Install with conda (recommended)
 conda install -c bioconda subread
diff --git a/skills/genomics-bioinformatics/gatk-variant-calling/SKILL.md b/skills/genomics-bioinformatics/gatk-variant-calling/SKILL.md
@@ -26,6 +26,8 @@ GATK (Genome Analysis Toolkit) implements the GATK Best Practices workflow for c
 - **Reference files**: genome FASTA + known variants VCF (dbSNP, 1000G, Mills indels)
 - **Input**: duplicate-marked, sorted BAM with `@RG` read group headers (from BWA-MEM2)
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v gatk` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run gatk` rather than bare `gatk`.
+
 ```bash
 # Install GATK4
 wget https://github.com/broadinstitute/gatk/releases/download/4.6.0.0/gatk-4.6.0.0.zip
diff --git a/skills/genomics-bioinformatics/homer-motif-analysis/SKILL.md b/skills/genomics-bioinformatics/homer-motif-analysis/SKILL.md
@@ -29,6 +29,8 @@ HOMER (Hypergeometric Optimization of Motif EnRichment) is a suite of Perl/C++ t
 - **Input**: BED file of peaks (at minimum: chr, start, end columns); ideally summit-centered peaks from MACS3
 - **Python packages** (for parsing/visualization): `pandas`, `matplotlib`, `seaborn`
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v findMotifsGenome.pl` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run findMotifsGenome.pl` rather than bare `findMotifsGenome.pl`.
+
 ```bash
 # Install HOMER via conda (recommended — handles Perl dependencies)
 conda install -c bioconda homer
diff --git a/skills/genomics-bioinformatics/macs3-peak-calling/SKILL.md b/skills/genomics-bioinformatics/macs3-peak-calling/SKILL.md
@@ -26,6 +26,8 @@ MACS3 (Model-based Analysis of ChIP-seq) identifies regions of significant read
 - **Input**: Sorted BAM files (with index) from ChIP-seq or ATAC-seq alignment (e.g., using STAR or Bowtie2)
 - **Optional**: Input/IgG control BAM for background normalization
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v macs3` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run macs3` rather than bare `macs3`.
+
 ```bash
 # Install with pip or conda
 pip install macs3
diff --git a/skills/genomics-bioinformatics/multiqc-qc-reports/SKILL.md b/skills/genomics-bioinformatics/multiqc-qc-reports/SKILL.md
@@ -26,6 +26,8 @@ MultiQC automatically searches directories for QC log files from 150+ bioinforma
 - **Input requirements**: Output files from bioinformatics tools (FastQC `.zip`, samtools `.flagstat`, STAR `Log.final.out`, etc.) — MultiQC finds them automatically
 - **Environment**: Python 3.8+
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v multiqc` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run multiqc` rather than bare `multiqc`.
+
 ```bash
 pip install multiqc
 
diff --git a/skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md b/skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md
@@ -26,20 +26,26 @@ PLINK2 is the high-performance successor to PLINK 1.9, designed for genome-wide
 - **Software**: PLINK2 (pre-compiled binary; no pip/conda package)
 - **Input**: PLINK binary files (.bed/.bim/.fam) or VCF/BGEN from array genotyping or imputation
 
+> **Check before installing**: The tool may already be available (e.g., inside a `pixi` / `conda` env). Always run `command -v plink2` first and skip the install block if it returns a path. When executing tools inside a pixi project, prefer `pixi run <tool>` over plain `<tool>`.
+
 ```bash
-# Download PLINK2 pre-compiled binary (Linux)
-wget https://s3.amazonaws.com/plink2-assets/alpha6/plink2_linux_avx2_20241112.zip
-unzip plink2_linux_avx2_20241112.zip
-chmod +x plink2
-export PATH="$PWD:$PATH"
-
-# macOS
-wget https://s3.amazonaws.com/plink2-assets/alpha6/plink2_mac_20241112.zip
-unzip plink2_mac_20241112.zip
-
-# Verify
-plink2 --version
-# PLINK v2.00a6LM
+# Skip install if already present
+if command -v plink2 >/dev/null 2>&1; then
+    echo "plink2 already installed: $(plink2 --version)"
+else
+    # Download PLINK2 pre-compiled binary (Linux)
+    wget https://s3.amazonaws.com/plink2-assets/alpha6/plink2_linux_avx2_20241112.zip
+    unzip plink2_linux_avx2_20241112.zip
+    chmod +x plink2
+    export PATH="$PWD:$PATH"
+
+    # macOS
+    # wget https://s3.amazonaws.com/plink2-assets/alpha6/plink2_mac_20241112.zip
+    # unzip plink2_mac_20241112.zip
+
+    plink2 --version
+    # PLINK v2.00a6LM
+fi
 
 # Python for downstream analysis
 pip install pandas numpy matplotlib scipy
diff --git a/skills/genomics-bioinformatics/prokka-genome-annotation/SKILL.md b/skills/genomics-bioinformatics/prokka-genome-annotation/SKILL.md
@@ -28,6 +28,8 @@ Prokka is a command-line pipeline for rapid annotation of prokaryotic genomes (b
 - **Input**: assembled genome in FASTA format (complete or draft with multiple contigs)
 - **Environment**: conda strongly recommended to handle the Perl and C dependency stack
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v prokka` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run prokka` rather than bare `prokka`.
+
 ```bash
 # Install Prokka via conda/mamba (recommended)
 conda install -c conda-forge -c bioconda prokka
diff --git a/skills/genomics-bioinformatics/salmon-rna-quantification/SKILL.md b/skills/genomics-bioinformatics/salmon-rna-quantification/SKILL.md
@@ -26,6 +26,8 @@ Salmon quantifies transcript abundance from RNA-seq reads using quasi-mapping 
 - **Reference**: transcriptome FASTA (cDNA sequences, e.g., GENCODE or Ensembl) + genome FASTA for decoy-aware indexing
 - **Python packages**: `pandas` for parsing output; `pydeseq2` for differential expression
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v salmon` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run salmon` rather than bare `salmon`.
+
 ```bash
 # Install with conda (recommended)
 conda install -c bioconda salmon
diff --git a/skills/genomics-bioinformatics/samtools-bam-processing/SKILL.md b/skills/genomics-bioinformatics/samtools-bam-processing/SKILL.md
@@ -30,6 +30,8 @@ samtools is the standard command-line toolkit for processing sequence alignment
 - **Input requirements**: SAM/BAM/CRAM files; CRAM requires FASTA reference
 - **Companion tools**: `samtools faidx` for FASTA indexing; `samtools sort` before `samtools index`
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v samtools` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run samtools` rather than bare `samtools`.
+
 ```bash
 # Bioconda (recommended)
 conda install -c bioconda samtools
diff --git a/skills/genomics-bioinformatics/snpeff-variant-annotation/SKILL.md b/skills/genomics-bioinformatics/snpeff-variant-annotation/SKILL.md
@@ -27,6 +27,8 @@ SnpEff annotates variants in VCF files by predicting their functional consequenc
 - **Python packages** (optional): `cyvcf2`, `pandas`, `matplotlib`, `seaborn` for Python-side parsing and visualization
 - **Reference genome database**: downloaded once per assembly (e.g., `hg38`, `GRCh37`, `mm10`)
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v snpEff` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run snpEff` rather than bare `snpEff`.
+
 ```bash
 # Download SnpEff JAR
 wget https://snpeff.blob.core.windows.net/versions/snpEff_latest_core.zip
diff --git a/skills/genomics-bioinformatics/star-rna-seq-aligner/SKILL.md b/skills/genomics-bioinformatics/star-rna-seq-aligner/SKILL.md
@@ -26,6 +26,8 @@ STAR (Spliced Transcripts Alignment to a Reference) aligns RNA-seq reads to a ge
 - **RAM**: 30–32 GB for human/mouse genome index; 8–16 GB for smaller genomes
 - **Disk**: ~25 GB for human genome index, ~5–10 GB per sample BAM
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v STAR` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run STAR` rather than bare `STAR`.
+
 ```bash
 # Install with conda (recommended)
 conda install -c bioconda star
diff --git a/skills/scientific-computing/nextflow-workflow-engine/SKILL.md b/skills/scientific-computing/nextflow-workflow-engine/SKILL.md
@@ -26,6 +26,8 @@ Nextflow implements a dataflow programming model where **processes** (containeri
 - **Containers**: Docker or Singularity for process isolation (recommended)
 - **Optional**: nf-core tools for community pipeline management
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v nextflow` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run nextflow` rather than bare `nextflow`.
+
 ```bash
 # Install Nextflow (self-contained JAR — no sudo required)
 curl -s https://get.nextflow.io | bash
diff --git a/skills/scientific-computing/snakemake-workflow-engine/SKILL.md b/skills/scientific-computing/snakemake-workflow-engine/SKILL.md
@@ -28,6 +28,8 @@ Snakemake is a Python-based workflow management system that scales analyses from
 - **Environment**: Python 3.11+; conda/mamba recommended for per-rule environments
 - **Data requirements**: Input files, reference files; output paths defined as rules
 
+> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v snakemake` first and skip the install commands below if it returns a path. When running inside a pixi project, invoke the tool via `pixi run snakemake` rather than bare `snakemake`.
+
 ```bash
 # Install via conda (includes optional dependencies)
 conda install -c conda-forge -c bioconda snakemake
PATCH

echo "Gold patch applied."
