# refactor: shorten SKILL.md descriptions ~28.5% across all 197 skills

Source: [jaechang-hits/SciAgent-Skills#16](https://github.com/jaechang-hits/SciAgent-Skills/pull/16)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/biostatistics/clinical-decision-support-documents/SKILL.md`
- `skills/biostatistics/degenerate-input-filtering/SKILL.md`
- `skills/biostatistics/hypothesis-generation/SKILL.md`
- `skills/biostatistics/matplotlib-scientific-plotting/SKILL.md`
- `skills/biostatistics/nan-safe-correlation/SKILL.md`
- `skills/biostatistics/pyhealth/SKILL.md`
- `skills/biostatistics/pymc-bayesian-modeling/SKILL.md`
- `skills/biostatistics/scikit-learn-machine-learning/SKILL.md`
- `skills/biostatistics/scikit-survival-analysis/SKILL.md`
- `skills/biostatistics/shap-model-explainability/SKILL.md`
- `skills/biostatistics/statistical-analysis/SKILL.md`
- `skills/biostatistics/statsmodels-statistical-modeling/SKILL.md`
- `skills/cell-biology/cellpose-cell-segmentation/SKILL.md`
- `skills/cell-biology/flowio-flow-cytometry/SKILL.md`
- `skills/cell-biology/histolab-wsi-processing/SKILL.md`
- `skills/cell-biology/imaging-data-commons/SKILL.md`
- `skills/cell-biology/napari-image-viewer/SKILL.md`
- `skills/cell-biology/nnunet-segmentation/SKILL.md`
- `skills/cell-biology/omero-integration/SKILL.md`
- `skills/cell-biology/opencv-bioimage-analysis/SKILL.md`
- `skills/cell-biology/pathml/SKILL.md`
- `skills/cell-biology/pydicom-medical-imaging/SKILL.md`
- `skills/cell-biology/pyimagej-fiji-bridge/SKILL.md`
- `skills/cell-biology/scikit-image-processing/SKILL.md`
- `skills/cell-biology/simpleitk-image-registration/SKILL.md`
- `skills/cell-biology/single-cell-annotation/SKILL.md`
- `skills/cell-biology/trackpy-particle-tracking/SKILL.md`
- `skills/data-visualization/plotly-interactive-plots/SKILL.md`
- `skills/data-visualization/plotly-interactive-visualization/SKILL.md`
- `skills/data-visualization/scientific-visualization/SKILL.md`
- `skills/data-visualization/seaborn-statistical-plots/SKILL.md`
- `skills/data-visualization/seaborn-statistical-visualization/SKILL.md`
- `skills/data-visualization/statistical-significance-annotation/SKILL.md`
- `skills/genomics-bioinformatics/anndata-data-structure/SKILL.md`
- `skills/genomics-bioinformatics/arboreto-grn-inference/SKILL.md`
- `skills/genomics-bioinformatics/archs4-database/SKILL.md`
- `skills/genomics-bioinformatics/bcftools-variant-manipulation/SKILL.md`
- `skills/genomics-bioinformatics/bedtools-genomic-intervals/SKILL.md`
- `skills/genomics-bioinformatics/biopython-molecular-biology/SKILL.md`
- `skills/genomics-bioinformatics/biopython-sequence-analysis/SKILL.md`
- `skills/genomics-bioinformatics/bioservices-multi-database/SKILL.md`
- `skills/genomics-bioinformatics/busco-status-interpretation/SKILL.md`
- `skills/genomics-bioinformatics/bwa-mem2-dna-aligner/SKILL.md`
- `skills/genomics-bioinformatics/cbioportal-database/SKILL.md`
- `skills/genomics-bioinformatics/celltypist-cell-annotation/SKILL.md`
- `skills/genomics-bioinformatics/cellxgene-census/SKILL.md`
- `skills/genomics-bioinformatics/clinpgx-database/SKILL.md`
- `skills/genomics-bioinformatics/clinvar-database/SKILL.md`
- `skills/genomics-bioinformatics/cnvkit-copy-number/SKILL.md`
- `skills/genomics-bioinformatics/cosmic-database/SKILL.md`
- `skills/genomics-bioinformatics/dbsnp-database/SKILL.md`
- `skills/genomics-bioinformatics/deeptools-ngs-analysis/SKILL.md`
- `skills/genomics-bioinformatics/depmap-crispr-essentiality/SKILL.md`
- `skills/genomics-bioinformatics/deseq2-differential-expression/SKILL.md`
- `skills/genomics-bioinformatics/ena-database/SKILL.md`
- `skills/genomics-bioinformatics/encode-database/SKILL.md`
- `skills/genomics-bioinformatics/ensembl-database/SKILL.md`
- `skills/genomics-bioinformatics/etetoolkit/SKILL.md`
- `skills/genomics-bioinformatics/fastp-fastq-preprocessing/SKILL.md`
- `skills/genomics-bioinformatics/featurecounts-rna-counting/SKILL.md`
- `skills/genomics-bioinformatics/gatk-variant-calling/SKILL.md`
- `skills/genomics-bioinformatics/gene-database/SKILL.md`
- `skills/genomics-bioinformatics/geniml/SKILL.md`
- `skills/genomics-bioinformatics/geo-database/SKILL.md`
- `skills/genomics-bioinformatics/gget-genomic-databases/SKILL.md`
- `skills/genomics-bioinformatics/gnomad-database/SKILL.md`
- `skills/genomics-bioinformatics/gseapy-gene-enrichment/SKILL.md`
- `skills/genomics-bioinformatics/gtars/SKILL.md`
- `skills/genomics-bioinformatics/gwas-database/SKILL.md`
- `skills/genomics-bioinformatics/harmony-batch-correction/SKILL.md`
- `skills/genomics-bioinformatics/homer-motif-analysis/SKILL.md`
- `skills/genomics-bioinformatics/jaspar-database/SKILL.md`
- `skills/genomics-bioinformatics/kegg-database/SKILL.md`
- `skills/genomics-bioinformatics/macs3-peak-calling/SKILL.md`
- `skills/genomics-bioinformatics/monarch-database/SKILL.md`
- `skills/genomics-bioinformatics/mouse-phenome-database/SKILL.md`
- `skills/genomics-bioinformatics/multiqc-qc-reports/SKILL.md`
- `skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md`
- `skills/genomics-bioinformatics/popv-cell-annotation/SKILL.md`
- `skills/genomics-bioinformatics/prokka-genome-annotation/SKILL.md`
- `skills/genomics-bioinformatics/pubmed-database/SKILL.md`
- `skills/genomics-bioinformatics/pydeseq2-differential-expression/SKILL.md`
- `skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md`
- `skills/genomics-bioinformatics/quickgo-database/SKILL.md`
- `skills/genomics-bioinformatics/regulomedb-database/SKILL.md`
- `skills/genomics-bioinformatics/remap-database/SKILL.md`
- `skills/genomics-bioinformatics/salmon-rna-quantification/SKILL.md`
- `skills/genomics-bioinformatics/samtools-bam-processing/SKILL.md`
- `skills/genomics-bioinformatics/scanpy-scrna-seq/SKILL.md`
- `skills/genomics-bioinformatics/scikit-bio/SKILL.md`
- `skills/genomics-bioinformatics/scvi-tools-single-cell/SKILL.md`
- `skills/genomics-bioinformatics/single-cell-annotation-guide/SKILL.md`
- `skills/genomics-bioinformatics/snpeff-variant-annotation/SKILL.md`
- `skills/genomics-bioinformatics/star-rna-seq-aligner/SKILL.md`
- `skills/genomics-bioinformatics/ucsc-genome-browser/SKILL.md`
- `skills/genomics-bioinformatics/vcf-variant-filtering/SKILL.md`
- `skills/lab-automation/benchling-integration/SKILL.md`
- `skills/lab-automation/opentrons-integration/SKILL.md`
- `skills/lab-automation/opentrons-protocol-api/SKILL.md`
- `skills/lab-automation/protocolsio-integration/SKILL.md`
- `skills/lab-automation/pylabrobot/SKILL.md`
- `skills/lab-automation/western-blot-quantification/SKILL.md`
- `skills/molecular-biology/plannotate-plasmid-annotation/SKILL.md`
- `skills/molecular-biology/sgrna-design-guide/SKILL.md`
- `skills/molecular-biology/viennarna-structure-prediction/SKILL.md`
- `skills/proteomics-protein-engineering/adaptyv-bio/SKILL.md`
- `skills/proteomics-protein-engineering/esm-protein-language-model/SKILL.md`
- `skills/proteomics-protein-engineering/hmdb-database/SKILL.md`
- `skills/proteomics-protein-engineering/interpro-database/SKILL.md`
- `skills/proteomics-protein-engineering/matchms-spectral-matching/SKILL.md`
- `skills/proteomics-protein-engineering/maxquant-proteomics/SKILL.md`
- `skills/proteomics-protein-engineering/metabolomics-workbench-database/SKILL.md`
- `skills/proteomics-protein-engineering/pride-database/SKILL.md`
- `skills/proteomics-protein-engineering/pyopenms-mass-spectrometry/SKILL.md`
- `skills/proteomics-protein-engineering/uniprot-protein-database/SKILL.md`
- `skills/scientific-computing/aeon/SKILL.md`
- `skills/scientific-computing/astropy-astronomy/SKILL.md`
- `skills/scientific-computing/dask-parallel-computing/SKILL.md`
- `skills/scientific-computing/exploratory-data-analysis/SKILL.md`
- `skills/scientific-computing/geopandas-geospatial/SKILL.md`
- `skills/scientific-computing/hypogenic-hypothesis-generation/SKILL.md`
- `skills/scientific-computing/matlab-scientific-computing/SKILL.md`
- `skills/scientific-computing/networkx-graph-analysis/SKILL.md`
- `skills/scientific-computing/neurokit2/SKILL.md`
- `skills/scientific-computing/neuropixels-analysis/SKILL.md`
- `skills/scientific-computing/nextflow-workflow-engine/SKILL.md`
- `skills/scientific-computing/polars-dataframes/SKILL.md`
- `skills/scientific-computing/pymatgen/SKILL.md`
- `skills/scientific-computing/pymoo/SKILL.md`
- `skills/scientific-computing/simpy-discrete-event-simulation/SKILL.md`
- `skills/scientific-computing/snakemake-workflow-engine/SKILL.md`
- `skills/scientific-computing/spikeinterface-electrophysiology/SKILL.md`
- `skills/scientific-computing/sympy-symbolic-math/SKILL.md`
- `skills/scientific-computing/torch-geometric-graph-neural-networks/SKILL.md`
- `skills/scientific-computing/transformers-bio-nlp/SKILL.md`
- `skills/scientific-computing/umap-learn/SKILL.md`
- `skills/scientific-computing/uspto-database/SKILL.md`
- `skills/scientific-computing/vaex-dataframes/SKILL.md`
- `skills/scientific-computing/zarr-python/SKILL.md`
- `skills/scientific-writing/biorxiv-database/SKILL.md`
- `skills/scientific-writing/cancer-research-figure-guide/SKILL.md`
- `skills/scientific-writing/cell-figure-guide/SKILL.md`
- `skills/scientific-writing/citation-management/SKILL.md`
- `skills/scientific-writing/elife-figure-guide/SKILL.md`
- `skills/scientific-writing/general-figure-guide/SKILL.md`
- `skills/scientific-writing/lancet-figure-guide/SKILL.md`
- `skills/scientific-writing/latex-research-posters/SKILL.md`
- `skills/scientific-writing/literature-review/SKILL.md`
- `skills/scientific-writing/nature-figure-guide/SKILL.md`
- `skills/scientific-writing/nejm-figure-guide/SKILL.md`
- `skills/scientific-writing/openalex-database/SKILL.md`
- `skills/scientific-writing/peer-review-methodology/SKILL.md`
- `skills/scientific-writing/pnas-figure-guide/SKILL.md`
- `skills/scientific-writing/science-figure-guide/SKILL.md`
- `skills/scientific-writing/scientific-brainstorming/SKILL.md`
- `skills/scientific-writing/scientific-critical-thinking/SKILL.md`
- `skills/scientific-writing/scientific-literature-search/SKILL.md`
- `skills/scientific-writing/scientific-manuscript-writing/SKILL.md`
- `skills/scientific-writing/scientific-schematics/SKILL.md`
- `skills/scientific-writing/scientific-slides/SKILL.md`
- `skills/structural-biology-drug-discovery/alphafold-database-access/SKILL.md`
- `skills/structural-biology-drug-discovery/autodock-vina-docking/SKILL.md`
- `skills/structural-biology-drug-discovery/chembl-database-bioactivity/SKILL.md`
- `skills/structural-biology-drug-discovery/clinicaltrials-database-search/SKILL.md`
- `skills/structural-biology-drug-discovery/dailymed-database/SKILL.md`
- `skills/structural-biology-drug-discovery/datamol-cheminformatics/SKILL.md`
- `skills/structural-biology-drug-discovery/ddinter-database/SKILL.md`
- `skills/structural-biology-drug-discovery/deepchem/SKILL.md`
- `skills/structural-biology-drug-discovery/diffdock/SKILL.md`
- `skills/structural-biology-drug-discovery/drugbank-database-access/SKILL.md`
- `skills/structural-biology-drug-discovery/emdb-database/SKILL.md`
- `skills/structural-biology-drug-discovery/fda-database/SKILL.md`
- `skills/structural-biology-drug-discovery/gtopdb-database/SKILL.md`
- `skills/structural-biology-drug-discovery/mdanalysis-trajectory/SKILL.md`
- `skills/structural-biology-drug-discovery/medchem/SKILL.md`
- `skills/structural-biology-drug-discovery/molfeat-molecular-featurization/SKILL.md`
- `skills/structural-biology-drug-discovery/opentargets-database/SKILL.md`
- `skills/structural-biology-drug-discovery/pdb-database/SKILL.md`
- `skills/structural-biology-drug-discovery/pubchem-compound-search/SKILL.md`
- `skills/structural-biology-drug-discovery/pytdc-therapeutics-data-commons/SKILL.md`
- `skills/structural-biology-drug-discovery/rdkit-cheminformatics/SKILL.md`
- `skills/structural-biology-drug-discovery/rowan/SKILL.md`
- `skills/structural-biology-drug-discovery/sar-analysis/SKILL.md`
- `skills/structural-biology-drug-discovery/torchdrug/SKILL.md`
- `skills/structural-biology-drug-discovery/unichem-database/SKILL.md`
- `skills/structural-biology-drug-discovery/zinc-database/SKILL.md`
- `skills/systems-biology-multiomics/brenda-database/SKILL.md`
- `skills/systems-biology-multiomics/cellchat-cell-communication/SKILL.md`
- `skills/systems-biology-multiomics/cobrapy-metabolic-modeling/SKILL.md`
- `skills/systems-biology-multiomics/kegg-pathway-analysis/SKILL.md`
- `skills/systems-biology-multiomics/lamindb-data-management/SKILL.md`
- `skills/systems-biology-multiomics/libsbml-network-modeling/SKILL.md`
- `skills/systems-biology-multiomics/mofaplus-multi-omics/SKILL.md`
- `skills/systems-biology-multiomics/muon-multiomics-singlecell/SKILL.md`
- `skills/systems-biology-multiomics/omics-analysis-guide/SKILL.md`
- `skills/systems-biology-multiomics/reactome-database/SKILL.md`
- `skills/systems-biology-multiomics/string-database-ppi/SKILL.md`

## What to add / change

## Summary

Reduces the system-prompt overhead injected by progressive disclosure. Only frontmatter `name + description` are loaded into the agent's system prompt; this PR shortens the description side without touching body content.

- **197 SKILL.md files** modified (frontmatter `description` only)
- **Aggregate: 83,161 → 59,460 chars (−28.5%)**, ~5,900 fewer tokens of always-loaded prompt
- vs reference repo (K-Dense-AI/scientific-agent-skills): 1.87× → **1.36×** total chars (now in line with skill-count ratio of 1.39×)

### Per-category reduction
| Category | Files | Δ |
|---|---:|---:|
| lab-automation | 6 | −30.7% |
| molecular-biology | 3 | −30.5% |
| cell-biology | 15 | −29.9% |
| biostatistics | 12 | −29.4% |
| structural-biology-drug-discovery | 26 | −29.2% |
| data-visualization | 6 | −29.0% |
| genomics-bioinformatics | 63 | −28.8% |
| proteomics-protein-engineering | 10 | −28.2% |
| scientific-computing | 24 | −28.0% |
| systems-biology-multiomics | 11 | −27.2% |
| scientific-writing | 21 | −25.1% |

### Preserved
- Tool-comparison cross-references ("use X for Y / Z for W")
- Key capability lists
- "Use when ..." routing intent
- YAML formatting style (single-line double-quoted vs folded scalar)
- All `name`, `license`, and body content

### Trimmed
- Redundant adjectives ("comprehensive", "fast", "Python framework for")
- Repeated phrasing and parenthetical re-statements
- Over-detailed enumerations

## Test plan
- [x] `pixi run validate` — 197 entries OK
- [x] `

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
