#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sciagent-skills

# Idempotency guard
if grep -qF "description: \"Guidelines for clinical decision support (CDS) documents: biomarke" "skills/biostatistics/clinical-decision-support-documents/SKILL.md" && grep -qF "description: \"Filter degenerate, uninformative inputs before statistical tests: " "skills/biostatistics/degenerate-input-filtering/SKILL.md" && grep -qF "description: \"Structured hypothesis formulation: turn observations into testable" "skills/biostatistics/hypothesis-generation/SKILL.md" && grep -qF "description: \"Low-level Python plotting for scientific figures: publication-qual" "skills/biostatistics/matplotlib-scientific-plotting/SKILL.md" && grep -qF "description: \"Per-feature NaN-safe Spearman/Pearson correlation across many feat" "skills/biostatistics/nan-safe-correlation/SKILL.md" && grep -qF "description: \"Python library for healthcare ML on EHR data: process MIMIC-III/IV" "skills/biostatistics/pyhealth/SKILL.md" && grep -qF "description: \"Bayesian modeling with PyMC 5: priors, likelihood, NUTS/ADVI sampl" "skills/biostatistics/pymc-bayesian-modeling/SKILL.md" && grep -qF "description: \"Classical ML in Python: classification, regression, clustering, di" "skills/biostatistics/scikit-learn-machine-learning/SKILL.md" && grep -qF "description: \"Time-to-event modeling with scikit-survival: Cox PH (elastic net)," "skills/biostatistics/scikit-survival-analysis/SKILL.md" && grep -qF "Model interpretability via SHAP (Shapley values from game theory)." "skills/biostatistics/shap-model-explainability/SKILL.md" && grep -qF "Guided statistical analysis: test choice, assumption checks, effect" "skills/biostatistics/statistical-analysis/SKILL.md" && grep -qF "description: \"Python statistical modeling: regression (OLS, WLS, GLM), discrete " "skills/biostatistics/statsmodels-statistical-modeling/SKILL.md" && grep -qF "description: \"DL cell/nucleus segmentation for fluorescence and brightfield micr" "skills/cell-biology/cellpose-cell-segmentation/SKILL.md" && grep -qF "description: \"Parse/write FCS (Flow Cytometry) files v2.0-3.1. Events as NumPy, " "skills/cell-biology/flowio-flow-cytometry/SKILL.md" && grep -qF "description: \"WSI processing for digital pathology. Tissue detection, tile extra" "skills/cell-biology/histolab-wsi-processing/SKILL.md" && grep -qF "description: \"Query NCI Imaging Data Commons (IDC) for cancer radiology and path" "skills/cell-biology/imaging-data-commons/SKILL.md" && grep -qF "description: \"Interactive viewer for microscopy. Displays 2D/3D/4D arrays as Ima" "skills/cell-biology/napari-image-viewer/SKILL.md" && grep -qF "description: \"Medical image segmentation with nnU-Net's self-configuring framewo" "skills/cell-biology/nnunet-segmentation/SKILL.md" && grep -qF "description: \"Open-source bio-image data management. Use the omero-py client to " "skills/cell-biology/omero-integration/SKILL.md" && grep -qF "description: \"Computer vision for bio-image preprocessing, feature detection, re" "skills/cell-biology/opencv-bioimage-analysis/SKILL.md" && grep -qF "description: \"Computational pathology toolkit for whole-slide images (WSIs): loa" "skills/cell-biology/pathml/SKILL.md" && grep -qF "description: \"Pure Python DICOM for medical imaging (CT, MRI, X-ray, ultrasound)" "skills/cell-biology/pydicom-medical-imaging/SKILL.md" && grep -qF "description: \"Python bridge to ImageJ2/Fiji for macros, plugins (Bio-Formats, Tr" "skills/cell-biology/pyimagej-fiji-bridge/SKILL.md" && grep -qF "description: \"Python image processing for microscopy and bioimage analysis. Read" "skills/cell-biology/scikit-image-processing/SKILL.md" && grep -qF "description: \"Register, segment, filter, resample 3D medical images (MRI, CT, mi" "skills/cell-biology/simpleitk-image-registration/SKILL.md" && grep -qF "description: \"Guide to annotating cell types in scRNA-seq. Covers manual marker-" "skills/cell-biology/single-cell-annotation/SKILL.md" && grep -qF "description: \"Python library for single-particle tracking (SPT) in video microsc" "skills/cell-biology/trackpy-particle-tracking/SKILL.md" && grep -qF "description: \"Interactive scientific visualization with Plotly. Two APIs: plotly" "skills/data-visualization/plotly-interactive-plots/SKILL.md" && grep -qF "description: \"Interactive visualization with Plotly. 40+ chart types (scatter, l" "skills/data-visualization/plotly-interactive-visualization/SKILL.md" && grep -qF "description: \"Guide for choosing and creating scientific visualizations for publ" "skills/data-visualization/scientific-visualization/SKILL.md" && grep -qF "description: \"Statistical visualization on matplotlib with native pandas support" "skills/data-visualization/seaborn-statistical-plots/SKILL.md" && grep -qF "description: \"Statistical visualization on matplotlib + pandas. Distributions (h" "skills/data-visualization/seaborn-statistical-visualization/SKILL.md" && grep -qF "description: \"Guide for annotating statistical significance (p-value asterisks) " "skills/data-visualization/statistical-significance-annotation/SKILL.md" && grep -qF "description: \"Annotated matrices for single-cell genomics. Stores X with obs/var" "skills/genomics-bioinformatics/anndata-data-structure/SKILL.md" && grep -qF "description: \"GRN inference from expression via GRNBoost2 (gradient boosting) or" "skills/genomics-bioinformatics/arboreto-grn-inference/SKILL.md" && grep -qF "description: \"Query ARCHS4 REST API for uniformly processed RNA-seq expression, " "skills/genomics-bioinformatics/archs4-database/SKILL.md" && grep -qF "description: \"CLI for VCF/BCF: filter, merge, annotate, query, normalize, comput" "skills/genomics-bioinformatics/bcftools-variant-manipulation/SKILL.md" && grep -qF "description: \"Genomic interval ops on BED/BAM/GFF/VCF. Find overlaps, merge inte" "skills/genomics-bioinformatics/bedtools-genomic-intervals/SKILL.md" && grep -qF "description: \"Molecular biology toolkit: sequence manipulation, FASTA/GenBank/PD" "skills/genomics-bioinformatics/biopython-molecular-biology/SKILL.md" && grep -qF "description: \"Biopython sequence analysis: parse FASTA/FASTQ/GenBank/GFF (SeqIO)" "skills/genomics-bioinformatics/biopython-sequence-analysis/SKILL.md" && grep -qF "pathways, ChEMBL/ChEBI/PubChem, BLAST, cross-database ID mapping, GO annotations" "skills/genomics-bioinformatics/bioservices-multi-database/SKILL.md" && grep -qF "description: \"Guide to interpreting BUSCO completeness statuses: why Duplicated " "skills/genomics-bioinformatics/busco-status-interpretation/SKILL.md" && grep -qF "description: \"Fast short-read DNA aligner for WGS/WES/ChIP-seq. 2\u00d7 faster BWA-ME" "skills/genomics-bioinformatics/bwa-mem2-dna-aligner/SKILL.md" && grep -qF "description: \"Cancer genomics (TCGA et al.) via cBioPortal REST API. Retrieve so" "skills/genomics-bioinformatics/cbioportal-database/SKILL.md" && grep -qF "description: \"Automated scRNA-seq cell type annotation via pre-trained logistic " "skills/genomics-bioinformatics/celltypist-cell-annotation/SKILL.md" && grep -qF "description: \"Query CELLxGENE Census (61M+ cells). Search by cell type/tissue/di" "skills/genomics-bioinformatics/cellxgene-census/SKILL.md" && grep -qF "description: \"Query PharmGKB REST API for drug-gene interactions, clinical annot" "skills/genomics-bioinformatics/clinpgx-database/SKILL.md" && grep -qF "description: \"Query NCBI ClinVar via E-utilities for variant clinical significan" "skills/genomics-bioinformatics/clinvar-database/SKILL.md" && grep -qF "description: \"Detect somatic CNVs from WES/WGS/targeted BAMs (CNVkit v0.9.x). Bi" "skills/genomics-bioinformatics/cnvkit-copy-number/SKILL.md" && grep -qF "description: \"Query COSMIC for cancer somatic mutations, gene census, mutational" "skills/genomics-bioinformatics/cosmic-database/SKILL.md" && grep -qF "description: \"Query NCBI dbSNP for SNP records by rsID, gene, or region via E-ut" "skills/genomics-bioinformatics/dbsnp-database/SKILL.md" && grep -qF "description: \"NGS CLI for ChIP/RNA/ATAC-seq. BAM\u2192bigWig with RPGC/CPM/RPKM, samp" "skills/genomics-bioinformatics/deeptools-ngs-analysis/SKILL.md" && grep -qF "description: \"DepMap CRISPR gene effect (Chronos) analysis: sign convention for " "skills/genomics-bioinformatics/depmap-crispr-essentiality/SKILL.md" && grep -qF "description: \"Bulk RNA-seq DE with R/Bioconductor DESeq2. Negative binomial GLM," "skills/genomics-bioinformatics/deseq2-differential-expression/SKILL.md" && grep -qF "description: \"ENA REST API for sequences, reads, assemblies, and annotations. Po" "skills/genomics-bioinformatics/ena-database/SKILL.md" && grep -qF "description: \"ENCODE Portal REST API for regulatory genomics: TF ChIP-seq, ATAC-" "skills/genomics-bioinformatics/encode-database/SKILL.md" && grep -qF "description: \"Ensembl REST API for gene/transcript/variant annotations in 300+ s" "skills/genomics-bioinformatics/ensembl-database/SKILL.md" && grep -qF "description: \"ETE Toolkit (ETE3): Python phylogenetic tree analysis and visualiz" "skills/genomics-bioinformatics/etetoolkit/SKILL.md" && grep -qF "description: \"All-in-one FASTQ QC and adapter trimming. Auto-detects Illumina ad" "skills/genomics-bioinformatics/fastp-fastq-preprocessing/SKILL.md" && grep -qF "description: \"Counts RNA-seq reads overlapping GTF gene features. Takes sorted S" "skills/genomics-bioinformatics/featurecounts-rna-counting/SKILL.md" && grep -qF "description: \"GATK Best Practices for germline SNP/indel calling from WGS/WES BA" "skills/genomics-bioinformatics/gatk-variant-calling/SKILL.md" && grep -qF "description: \"NCBI Gene via E-utilities: curated records across 1M+ taxa. Offici" "skills/genomics-bioinformatics/gene-database/SKILL.md" && grep -qF "description: \"Python library for genomic interval ML. Train/apply region2vec emb" "skills/genomics-bioinformatics/geniml/SKILL.md" && grep -qF "description: \"NCBI GEO access via GEOparse and E-utilities. Search by keyword/or" "skills/genomics-bioinformatics/geo-database/SKILL.md" && grep -qF "description: \"Unified CLI/Python interface to 20+ genomic databases. Gene lookup" "skills/genomics-bioinformatics/gget-genomic-databases/SKILL.md" && grep -qF "description: \"gnomAD v4 population variant frequencies via GraphQL API. Allele c" "skills/genomics-bioinformatics/gnomad-database/SKILL.md" && grep -qF "description: \"GSEA and over-representation analysis (ORA) for RNA-seq and proteo" "skills/genomics-bioinformatics/gseapy-gene-enrichment/SKILL.md" && grep -qF "description: \"Rust-backed Python library for fast genomic token arithmetic and B" "skills/genomics-bioinformatics/gtars/SKILL.md" && grep -qF "description: \"NHGRI-EBI GWAS Catalog REST API for SNP-trait associations from pu" "skills/genomics-bioinformatics/gwas-database/SKILL.md" && grep -qF "description: \"Harmony batch correction for scRNA-seq and other omics. Removes ba" "skills/genomics-bioinformatics/harmony-batch-correction/SKILL.md" && grep -qF "description: \"De novo and known TF motif enrichment in ChIP-seq/ATAC-seq peaks v" "skills/genomics-bioinformatics/homer-motif-analysis/SKILL.md" && grep -qF "description: \"JASPAR 2024 TF binding profiles via REST API and pyJASPAR. Retriev" "skills/genomics-bioinformatics/jaspar-database/SKILL.md" && grep -qF "description: \"KEGG REST API (academic only). Pathways, genes, compounds, enzymes" "skills/genomics-bioinformatics/kegg-database/SKILL.md" && grep -qF "description: \"Poisson-model peak caller for ChIP-seq/ATAC-seq BAMs. MACS3 callpe" "skills/genomics-bioinformatics/macs3-peak-calling/SKILL.md" && grep -qF "description: \"Monarch Initiative knowledge graph REST API for disease-gene-pheno" "skills/genomics-bioinformatics/monarch-database/SKILL.md" && grep -qF "description: \"Retrieve quantitative phenotypes across inbred mouse strains from " "skills/genomics-bioinformatics/mouse-phenome-database/SKILL.md" && grep -qF "description: \"Aggregates QC from 150+ bioinformatics tools into one interactive " "skills/genomics-bioinformatics/multiqc-qc-reports/SKILL.md" && grep -qF "description: \"GWAS and population genetics tool. Processes PLINK (.bed/.bim/.fam" "skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md" && grep -qF "description: \"Consensus cell type annotation: runs 10+ algorithms (KNN-Harmony/B" "skills/genomics-bioinformatics/popv-cell-annotation/SKILL.md" && grep -qF "description: \"Annotate prokaryotic genomes (bacteria, archaea, viruses) via Prok" "skills/genomics-bioinformatics/prokka-genome-annotation/SKILL.md" && grep -qF "citation matching, systematic review strategies. Use for biomedical" "skills/genomics-bioinformatics/pubmed-database/SKILL.md" && grep -qF "description: \"Bulk RNA-seq DE with PyDESeq2: load counts, normalize, fit negativ" "skills/genomics-bioinformatics/pydeseq2-differential-expression/SKILL.md" && grep -qF "description: \"Read/write SAM/BAM/CRAM, VCF/BCF, FASTA/FASTQ. Region queries, pil" "skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md" && grep -qF "description: \"Query EBI QuickGO REST API for GO terms and protein annotations. F" "skills/genomics-bioinformatics/quickgo-database/SKILL.md" && grep -qF "description: \"Query RegulomeDB v2 REST API to score variants for regulatory func" "skills/genomics-bioinformatics/regulomedb-database/SKILL.md" && grep -qF "description: \"Query ReMap 2022 TF ChIP-seq peak database via REST API and BED do" "skills/genomics-bioinformatics/remap-database/SKILL.md" && grep -qF "description: \"Ultra-fast RNA-seq transcript/gene quantification via quasi-mappin" "skills/genomics-bioinformatics/salmon-rna-quantification/SKILL.md" && grep -qF "description: \"CLI toolkit for SAM/BAM/CRAM: sort, index, convert, filter, QC ali" "skills/genomics-bioinformatics/samtools-bam-processing/SKILL.md" && grep -qF "description: \"scRNA-seq with Scanpy: QC, normalization, HVG selection, PCA, neig" "skills/genomics-bioinformatics/scanpy-scrna-seq/SKILL.md" && grep -qF "(Shannon, Faith PD, Bray-Curtis, UniFrac), ordination (PCoA, CCA, RDA)," "skills/genomics-bioinformatics/scikit-bio/SKILL.md" && grep -qF "description: \"Deep generative models for single-cell omics: probabilistic batch " "skills/genomics-bioinformatics/scvi-tools-single-cell/SKILL.md" && grep -qF "description: \"Decision framework for manual marker-based, automated (CellTypist)" "skills/genomics-bioinformatics/single-cell-annotation-guide/SKILL.md" && grep -qF "description: \"Annotate and filter VCF variants with SnpEff and SnpSift. SnpEff p" "skills/genomics-bioinformatics/snpeff-variant-annotation/SKILL.md" && grep -qF "description: \"Splice-aware RNA-seq aligner producing sorted BAM and splice junct" "skills/genomics-bioinformatics/star-rna-seq-aligner/SKILL.md" && grep -qF "description: \"Query UCSC Genome Browser REST API for DNA sequences, tracks, gene" "skills/genomics-bioinformatics/ucsc-genome-browser/SKILL.md" && grep -qF "description: \"Guide to quality filtering raw VCF files before computing summary " "skills/genomics-bioinformatics/vcf-variant-filtering/SKILL.md" && grep -qF "description: \"Benchling R&D Python SDK: CRUD on registry entities (DNA, RNA, pro" "skills/lab-automation/benchling-integration/SKILL.md" && grep -qF "description: \"Opentrons Protocol API v2 for OT-2/Flex: Python protocols for pipe" "skills/lab-automation/opentrons-integration/SKILL.md" && grep -qF "description: \"Python API v2 for Opentrons OT-2/Flex liquid handlers: protocols a" "skills/lab-automation/opentrons-protocol-api/SKILL.md" && grep -qF "description: \"protocols.io REST API: search and fetch wet-lab, bioinformatics, a" "skills/lab-automation/protocolsio-integration/SKILL.md" && grep -qF "description: \"Hardware-agnostic Python liquid-handler library: portable scripts " "skills/lab-automation/pylabrobot/SKILL.md" && grep -qF "description: \"Quantitative Western blot analysis: band detection, two-step norma" "skills/lab-automation/western-blot-quantification/SKILL.md" && grep -qF "description: \"Auto-annotate plasmids with features (promoters, terminators, resi" "skills/molecular-biology/plannotate-plasmid-annotation/SKILL.md" && grep -qF "description: \"Decision guide for finding/designing sgRNAs via three tiers: (1) v" "skills/molecular-biology/sgrna-design-guide/SKILL.md" && grep -qF "description: \"Predict RNA secondary structure, MFE folding, base-pair probabilit" "skills/molecular-biology/viennarna-structure-prediction/SKILL.md" && grep -qF "description: \"API + Python SDK for ordering cell-free protein expression and bin" "skills/proteomics-protein-engineering/adaptyv-bio/SKILL.md" && grep -qF "description: \"Protein language models (ESM3, ESM C) for sequence generation, str" "skills/proteomics-protein-engineering/esm-protein-language-model/SKILL.md" && grep -qF "description: \"Parse HMDB (Human Metabolome Database) local XML for metabolite in" "skills/proteomics-protein-engineering/hmdb-database/SKILL.md" && grep -qF "description: \"Query InterPro REST API for protein domain architecture, family cl" "skills/proteomics-protein-engineering/interpro-database/SKILL.md" && grep -qF "description: MS spectral matching and metabolite ID with matchms. Import spectra" "skills/proteomics-protein-engineering/matchms-spectral-matching/SKILL.md" && grep -qF "description: \"MaxQuant + Perseus proteomics pipeline: run MaxQuant for LFQ and S" "skills/proteomics-protein-engineering/maxquant-proteomics/SKILL.md" && grep -qF "description: \"Query Metabolomics Workbench REST API (4,200+ NIH studies) for met" "skills/proteomics-protein-engineering/metabolomics-workbench-database/SKILL.md" && grep -qF "description: \"Search PRIDE Archive REST API for proteomics datasets, peptide IDs" "skills/proteomics-protein-engineering/pride-database/SKILL.md" && grep -qF "description: MS data processing with PyOpenMS for LC-MS/MS proteomics and metabo" "skills/proteomics-protein-engineering/pyopenms-mass-spectrometry/SKILL.md" && grep -qF "description: \"Query UniProt REST API: search by gene/protein name, fetch FASTA, " "skills/proteomics-protein-engineering/uniprot-protein-database/SKILL.md" && grep -qF "description: \"scikit-learn compatible Python toolkit for time series ML: classif" "skills/scientific-computing/aeon/SKILL.md" && grep -qF "description: \"Core Python library for astronomy/astrophysics: units with dimensi" "skills/scientific-computing/astropy-astronomy/SKILL.md" && grep -qF "description: \"Parallel/distributed computing for larger-than-RAM data. Component" "skills/scientific-computing/dask-parallel-computing/SKILL.md" && grep -qF "omics), quality assessment, report generation, format detection across 200+" "skills/scientific-computing/exploratory-data-analysis/SKILL.md" && grep -qF "basemaps). Use for spatial joins, overlays, CRS transforms, area/distance, maps." "skills/scientific-computing/geopandas-geospatial/SKILL.md" && grep -qF "description: \"LLM-driven hypothesis generation/testing on tabular data. Three me" "skills/scientific-computing/hypogenic-hypothesis-generation/SKILL.md" && grep -qF "description: \"MATLAB/GNU Octave numerical computing: matrices, linear algebra, O" "skills/scientific-computing/matlab-scientific-computing/SKILL.md" && grep -qF "description: \"Graph and network analysis toolkit. Four graph types (directed, un" "skills/scientific-computing/networkx-graph-analysis/SKILL.md" && grep -qF "description: \"Python toolkit for neurophysiological signal processing: ECG (HR, " "skills/scientific-computing/neurokit2/SKILL.md" && grep -qF "description: \"Pipeline for Neuropixels extracellular electrophysiology: probe ge" "skills/scientific-computing/neuropixels-analysis/SKILL.md" && grep -qF "description: \"Dataflow workflow engine for scalable bioinformatics pipelines. De" "skills/scientific-computing/nextflow-workflow-engine/SKILL.md" && grep -qF "pushdown. Reads CSV, Parquet, JSON, Excel, DBs, cloud. Larger-than-RAM: Dask; GP" "skills/scientific-computing/polars-dataframes/SKILL.md" && grep -qF "description: \"Python Materials Genomics library for structure analysis, thermody" "skills/scientific-computing/pymatgen/SKILL.md" && grep -qF "description: \"Python framework for single- and multi-objective optimization with" "skills/scientific-computing/pymoo/SKILL.md" && grep -qF "description: \"Process-based discrete-event simulation. Model queues, shared reso" "skills/scientific-computing/simpy-discrete-event-simulation/SKILL.md" && grep -qF "description: \"Python-based workflow manager for reproducible, scalable pipelines" "skills/scientific-computing/snakemake-workflow-engine/SKILL.md" && grep -qF "description: \"Unified Python framework for extracellular electrophysiology. Load" "skills/scientific-computing/spikeinterface-electrophysiology/SKILL.md" && grep -qF "description: \"Symbolic math in Python: exact algebra, calculus (derivatives, int" "skills/scientific-computing/sympy-symbolic-math/SKILL.md" && grep -qF "description: \"PyTorch Geometric (PyG) for graph neural networks: node/graph clas" "skills/scientific-computing/torch-geometric-graph-neural-networks/SKILL.md" && grep -qF "description: \"HuggingFace Transformers with biomedical LMs (BioBERT, PubMedBERT," "skills/scientific-computing/transformers-bio-nlp/SKILL.md" && grep -qF "(temporal/batch). 15+ distance metrics, custom Numba metrics, precomputed distan" "skills/scientific-computing/umap-learn/SKILL.md" && grep -qF "description: \"Access USPTO patent data via PatentsView REST API and Google Paten" "skills/scientific-computing/uspto-database/SKILL.md" && grep -qF "GCS, Azure). Built-in ML transformers (scaling, PCA, K-means). In-memory: polars" "skills/scientific-computing/vaex-dataframes/SKILL.md" && grep -qF "description: \"Chunked N-D arrays with compression and cloud storage. NumPy-style" "skills/scientific-computing/zarr-python/SKILL.md" && grep -qF "description: \"Query bioRxiv/medRxiv preprints via REST API. Search by DOI, categ" "skills/scientific-writing/biorxiv-database/SKILL.md" && grep -qF "description: \"Cancer Research (AACR) figures: resolution (300-1200 DPI), formats" "skills/scientific-writing/cancer-research-figure-guide/SKILL.md" && grep -qF "description: \"Cell (Cell Press) figure preparation: resolution (300-1000 DPI), f" "skills/scientific-writing/cell-figure-guide/SKILL.md" && grep -qF "description: \"Selecting a reference manager and applying citation styles. Compar" "skills/scientific-writing/citation-management/SKILL.md" && grep -qF "description: \"eLife figure preparation: file formats (TIFF/EPS/PDF), striking im" "skills/scientific-writing/elife-figure-guide/SKILL.md" && grep -qF "description: \"Universal QA checklist for generated scientific plots: overlapping" "skills/scientific-writing/general-figure-guide/SKILL.md" && grep -qF "description: \"The Lancet figure preparation: resolution (300+ DPI at 120%), pref" "skills/scientific-writing/lancet-figure-guide/SKILL.md" && grep -qF "description: \"Research posters in LaTeX using beamerposter, tikzposter, or bapos" "skills/scientific-writing/latex-research-posters/SKILL.md" && grep -qF "description: \"Conducting systematic, scoping, and narrative literature reviews. " "skills/scientific-writing/literature-review/SKILL.md" && grep -qF "description: \"Nature figure preparation: resolution (300+ DPI), formats (AI/EPS/" "skills/scientific-writing/nature-figure-guide/SKILL.md" && grep -qF "description: \"NEJM figure preparation: resolution (300-1200 DPI), editable vecto" "skills/scientific-writing/nejm-figure-guide/SKILL.md" && grep -qF "description: \"Query OpenAlex REST API for 250M+ scholarly works, authors, instit" "skills/scientific-writing/openalex-database/SKILL.md" && grep -qF "description: \"Structured peer review of manuscripts and grants. 7-stage evaluati" "skills/scientific-writing/peer-review-methodology/SKILL.md" && grep -qF "description: \"PNAS figure preparation: resolution (300-1000 PPI), formats (TIFF/" "skills/scientific-writing/pnas-figure-guide/SKILL.md" && grep -qF "description: \"Science (AAAS) figure preparation: resolution (150-300+ DPI), form" "skills/scientific-writing/science-figure-guide/SKILL.md" && grep -qF "description: \"Structured ideation methods: SCAMPER, Six Thinking Hats, Morpholog" "skills/scientific-writing/scientific-brainstorming/SKILL.md" && grep -qF "description: \"Evaluating scientific evidence and claims. Covers study design hie" "skills/scientific-writing/scientific-critical-thinking/SKILL.md" && grep -qF "description: \"Systematic strategies for searching scientific literature across P" "skills/scientific-writing/scientific-literature-search/SKILL.md" && grep -qF "description: \"Scientific manuscript writing: IMRAD, citation styles (APA/AMA/Van" "skills/scientific-writing/scientific-manuscript-writing/SKILL.md" && grep -qF "description: \"Designing scientific schematics, diagrams, and graphical abstracts" "skills/scientific-writing/scientific-schematics/SKILL.md" && grep -qF "description: \"Scientific presentations for conferences, seminars, thesis defense" "skills/scientific-writing/scientific-slides/SKILL.md" && grep -qF "analyze pLDDT/PAE, bulk-fetch proteomes via Google Cloud. For experimental struc" "skills/structural-biology-drug-discovery/alphafold-database-access/SKILL.md" && grep -qF "description: \"Molecular docking with AutoDock Vina (Python API). Receptor/ligand" "skills/structural-biology-drug-discovery/autodock-vina-docking/SKILL.md" && grep -qF "description: Query ChEMBL via Python SDK. Search compounds by structure/properti" "skills/structural-biology-drug-discovery/chembl-database-bioactivity/SKILL.md" && grep -qF "description: Query ClinicalTrials.gov API v2 for trial data. Search by condition" "skills/structural-biology-drug-discovery/clinicaltrials-database-search/SKILL.md" && grep -qF "description: \"Query FDA drug labels (DailyMed) via REST API. Search structured p" "skills/structural-biology-drug-discovery/dailymed-database/SKILL.md" && grep -qF "Pythonic RDKit wrapper with sensible defaults for drug discovery. SMILES parsing" "skills/structural-biology-drug-discovery/datamol-cheminformatics/SKILL.md" && grep -qF "description: \"Query DDInter drug-drug interactions via REST API (1.7M+ interacti" "skills/structural-biology-drug-discovery/ddinter-database/SKILL.md" && grep -qF "description: \"Deep learning for drug discovery. 60+ models (GCN, GAT, AttentiveF" "skills/structural-biology-drug-discovery/deepchem/SKILL.md" && grep -qF "description: \"Diffusion-based docking that predicts protein-ligand poses without" "skills/structural-biology-drug-discovery/diffdock/SKILL.md" && grep -qF "description: \"Parse local DrugBank XML for drug info, interactions, targets, and" "skills/structural-biology-drug-discovery/drugbank-database-access/SKILL.md" && grep -qF "description: \"Search EMDB cryo-EM density maps, fitted atomic models, and metada" "skills/structural-biology-drug-discovery/emdb-database/SKILL.md" && grep -qF "description: \"Query openFDA REST API for adverse events (FAERS), labeling, produ" "skills/structural-biology-drug-discovery/fda-database/SKILL.md" && grep -qF "description: \"Query IUPHAR/BPS Guide to Pharmacology (GtoPdb) REST API for recep" "skills/structural-biology-drug-discovery/gtopdb-database/SKILL.md" && grep -qF "description: \"Analyze MD trajectories from GROMACS, AMBER, NAMD, CHARMM, LAMMPS." "skills/structural-biology-drug-discovery/mdanalysis-trajectory/SKILL.md" && grep -qF "composition query language. Built on RDKit/datamol. For hit-to-lead filtering, l" "skills/structural-biology-drug-discovery/medchem/SKILL.md" && grep -qF "description: Molecular featurization hub (100+ featurizers) for ML. SMILES to fi" "skills/structural-biology-drug-discovery/molfeat-molecular-featurization/SKILL.md" && grep -qF "description: \"Query Open Targets GraphQL API for target-disease associations, ev" "skills/structural-biology-drug-discovery/opentargets-database/SKILL.md" && grep -qF "description: \"Query RCSB PDB (200K+ structures) via rcsb-api SDK. Text/attribute" "skills/structural-biology-drug-discovery/pdb-database/SKILL.md" && grep -qF "description: \"Query PubChem (110M+ compounds) via PubChemPy/PUG-REST. Search by " "skills/structural-biology-drug-discovery/pubchem-compound-search/SKILL.md" && grep -qF "toxicity, DTI, DDI with scaffold/cold splits, standardized metrics, molecular or" "skills/structural-biology-drug-discovery/pytdc-therapeutics-data-commons/SKILL.md" && grep -qF "description: \"Cheminformatics toolkit for molecular analysis and virtual screeni" "skills/structural-biology-drug-discovery/rdkit-cheminformatics/SKILL.md" && grep -qF "description: \"Cloud quantum chemistry platform with Python SDK. Run geometry opt" "skills/structural-biology-drug-discovery/rowan/SKILL.md" && grep -qF "description: \"Structure-Activity Relationship (SAR) analysis with RDKit: scaffol" "skills/structural-biology-drug-discovery/sar-analysis/SKILL.md" && grep -qF "description: \"PyTorch-based ML platform for drug discovery: graph molecular repr" "skills/structural-biology-drug-discovery/torchdrug/SKILL.md" && grep -qF "description: \"Cross-reference compound IDs across 50+ databases (ChEMBL, DrugBan" "skills/structural-biology-drug-discovery/unichem-database/SKILL.md" && grep -qF "description: \"Query ZINC15/ZINC22 virtual compound libraries (1.4B compounds, 75" "skills/structural-biology-drug-discovery/zinc-database/SKILL.md" && grep -qF "description: \"BRENDA Enzyme DB SOAP/REST queries: kinetic parameters (Km, Vmax, " "skills/systems-biology-multiomics/brenda-database/SKILL.md" && grep -qF "description: \"Infer and visualize intercellular communication from scRNA-seq wit" "skills/systems-biology-multiomics/cellchat-cell-communication/SKILL.md" && grep -qF "description: \"Constraint-based (COBRA) analysis of genome-scale metabolic models" "skills/systems-biology-multiomics/cobrapy-metabolic-modeling/SKILL.md" && grep -qF "description: \"Guide to KEGG pathway enrichment for DEG results. Covers ORA vs GS" "skills/systems-biology-multiomics/kegg-pathway-analysis/SKILL.md" && grep -qF "description: \"Open-source FAIR biology data framework. Version artifacts (AnnDat" "skills/systems-biology-multiomics/lamindb-data-management/SKILL.md" && grep -qF "description: \"Build, read, validate, modify SBML biological network models via t" "skills/systems-biology-multiomics/libsbml-network-modeling/SKILL.md" && grep -qF "description: \"Multi-Omics Factor Analysis v2 (MOFA+) with mofapy2. Jointly decom" "skills/systems-biology-multiomics/mofaplus-multi-omics/SKILL.md" && grep -qF "description: \"Multi-modal single-cell analysis with muon/MuData. Joint RNA+ATAC " "skills/systems-biology-multiomics/muon-multiomics-singlecell/SKILL.md" && grep -qF "description: \"Decision guide for omics analysis (transcriptomics, proteomics) us" "skills/systems-biology-multiomics/omics-analysis-guide/SKILL.md" && grep -qF "description: \"Query Reactome pathways via REST: pathway queries, entity lookup, " "skills/systems-biology-multiomics/reactome-database/SKILL.md" && grep -qF "description: Query STRING REST API for PPIs (59M proteins, 20B interactions, 500" "skills/systems-biology-multiomics/string-database-ppi/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/biostatistics/clinical-decision-support-documents/SKILL.md b/skills/biostatistics/clinical-decision-support-documents/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: clinical-decision-support-documents
-description: "Guidelines for generating clinical decision support (CDS) documents: patient cohort analyses (biomarker-stratified outcomes) and treatment recommendation reports (GRADE-graded evidence). Covers document structure, executive summary design, evidence grading (GRADE 1A–2C), statistical reporting (HR, CI, survival), and biomarker integration. Use when creating pharmaceutical research documents, clinical guidelines, or regulatory submissions."
+description: "Guidelines for clinical decision support (CDS) documents: biomarker-stratified cohort analyses and GRADE-graded treatment reports. Covers structure, executive summaries, evidence grading (1A–2C), stats (HR, CI, survival), and biomarker integration. Use for pharma research docs, clinical guidelines, regulatory submissions."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/biostatistics/degenerate-input-filtering/SKILL.md b/skills/biostatistics/degenerate-input-filtering/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: degenerate-input-filtering
-description: "Mandatory filtering of degenerate and uninformative data points before statistical tests. Covers single-sequence alignments, empty files, constant-value features, zero-variance inputs, and all-NaN columns. For NaN-aware correlation computation, see the nan-safe-correlation skill. For broader statistical testing guidance, see the statistical-analysis skill."
+description: "Filter degenerate, uninformative inputs before statistical tests: single-sequence alignments, empty files, constant features, zero-variance inputs, all-NaN columns. See nan-safe-correlation for NaN-aware correlation; statistical-analysis for test guidance."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/biostatistics/hypothesis-generation/SKILL.md b/skills/biostatistics/hypothesis-generation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: hypothesis-generation
-description: "Structured hypothesis formulation from observations. Use when you have experimental observations or data and need to formulate testable hypotheses with predictions, propose mechanisms, and design experiments to test them. Follows scientific method framework. For open-ended ideation use scientific-brainstorming; for automated LLM-driven hypothesis testing on datasets use hypogenic."
+description: "Structured hypothesis formulation: turn observations into testable hypotheses with predictions, propose mechanisms, design experiments. Follows the scientific method. Use scientific-brainstorming for open ideation; hypogenic for automated LLM hypothesis testing on datasets."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/biostatistics/matplotlib-scientific-plotting/SKILL.md b/skills/biostatistics/matplotlib-scientific-plotting/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "matplotlib-scientific-plotting"
-description: "Low-level Python plotting library for full customization of scientific figures. Use for publication-quality plots (line, scatter, bar, heatmap, contour, 3D), multi-panel subplot layouts, and fine-grained control over every visual element. Export to PNG/PDF/SVG. For quick statistical plots use seaborn; for interactive plots use plotly."
+description: "Low-level Python plotting for scientific figures: publication-quality line, scatter, bar, heatmap, contour, 3D; multi-panel layouts; fine control of every element. PNG/PDF/SVG export. Use seaborn for quick stats, plotly for interactive."
 license: "PSF-based"
 ---
 
diff --git a/skills/biostatistics/nan-safe-correlation/SKILL.md b/skills/biostatistics/nan-safe-correlation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: nan-safe-correlation
-description: "Per-feature NaN-safe Spearman/Pearson correlation computation. Use when computing correlations across many features (genes, proteins, variants) with missing values. Covers why bulk matrix shortcuts fail with missing data, correct pairwise deletion, degenerate input filtering, and performance optimization for large datasets. For general statistical test selection use statistical-analysis; for model explainability use shap-model-explainability."
+description: "Per-feature NaN-safe Spearman/Pearson correlation across many features (genes, proteins, variants) with missing values. Covers why bulk matrix shortcuts fail, correct pairwise deletion, degenerate input filtering, and large-dataset performance. Use statistical-analysis for test choice; shap-model-explainability for interpretability."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/biostatistics/pyhealth/SKILL.md b/skills/biostatistics/pyhealth/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pyhealth"
-description: "PyHealth is a Python library for healthcare machine learning. Build clinical prediction models from EHR (Electronic Health Record) data: process MIMIC-III/IV, eICU, and OMOP-CDM datasets, encode medical codes (ICD, ATC, NDC), construct patient-level datasets, and train models (Transformer, RETAIN, GRASP, MedBERT) for tasks including mortality prediction, drug recommendation, readmission, and diagnosis prediction. Alternatives: FIDDLE (EHR preprocessing only), clinical-longformer (NLP on clinical notes only), ehr-ml (EHR embedding only)."
+description: "Python library for healthcare ML on EHR data: process MIMIC-III/IV, eICU, OMOP-CDM; encode medical codes (ICD, ATC, NDC); build patient-level datasets; train Transformer, RETAIN, GRASP, MedBERT for mortality, drug recommendation, readmission, diagnosis prediction. Alternatives: FIDDLE (preprocessing), clinical-longformer (clinical NLP), ehr-ml (embeddings)."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/biostatistics/pymc-bayesian-modeling/SKILL.md b/skills/biostatistics/pymc-bayesian-modeling/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pymc-bayesian-modeling"
-description: "Bayesian modeling with PyMC 5. 8-step workflow: define model, set priors, define likelihood, sample (NUTS/ADVI), diagnose (R-hat, ESS, divergences), interpret posteriors, compare models (LOO/WAIC), predict. Hierarchical, logistic, GP model variants. Prior/posterior predictive checks."
+description: "Bayesian modeling with PyMC 5: priors, likelihood, NUTS/ADVI sampling, diagnostics (R-hat, ESS), LOO/WAIC comparison, prediction. Hierarchical, logistic, GP variants; predictive checks."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/biostatistics/scikit-learn-machine-learning/SKILL.md b/skills/biostatistics/scikit-learn-machine-learning/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "scikit-learn-machine-learning"
-description: "Classical machine learning in Python. Use for classification, regression, clustering, dimensionality reduction, model evaluation, hyperparameter tuning, and preprocessing pipelines. Covers linear models, tree ensembles, SVMs, K-Means, PCA, t-SNE. For deep learning use PyTorch/TensorFlow; for gradient boosting at scale use XGBoost/LightGBM."
+description: "Classical ML in Python: classification, regression, clustering, dim reduction, evaluation, tuning, preprocessing pipelines. Linear models, tree ensembles, SVMs, K-Means, PCA, t-SNE. Use PyTorch/TF for deep learning; XGBoost/LightGBM for scale."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/biostatistics/scikit-survival-analysis/SKILL.md b/skills/biostatistics/scikit-survival-analysis/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scikit-survival-analysis
-description: "Survival analysis and time-to-event modeling with scikit-survival. Cox proportional hazards (standard/elastic net), Random Survival Forests, Gradient Boosting, SVMs for censored data. C-index (Harrell/Uno), Brier score, time-dependent AUC evaluation. Kaplan-Meier, Nelson-Aalen, competing risks. scikit-learn Pipeline/GridSearchCV compatible. For frequentist regression use statsmodels; for Bayesian survival use pymc; for simpler parametric models use lifelines."
+description: "Time-to-event modeling with scikit-survival: Cox PH (elastic net), Random Survival Forests, Boosting, SVMs for censored data. C-index, Brier, time-dependent AUC; Kaplan-Meier, Nelson-Aalen, competing risks. Pipeline/GridSearchCV compatible. Use statsmodels for frequentist, pymc for Bayesian, lifelines for parametric."
 license: GPL-3.0
 ---
 
diff --git a/skills/biostatistics/shap-model-explainability/SKILL.md b/skills/biostatistics/shap-model-explainability/SKILL.md
@@ -1,13 +1,12 @@
 ---
 name: shap-model-explainability
 description: >-
-  Model interpretability using SHAP (SHapley Additive exPlanations) based on
-  Shapley values from game theory. Covers explainer selection (Tree, Deep,
-  Linear, Kernel, Gradient, Permutation), computing feature attributions,
-  and visualization (waterfall, beeswarm, bar, scatter, force, heatmap).
-  Use when explaining ML model predictions, computing feature importance,
-  debugging model behavior, analyzing fairness/bias, or comparing models.
-  Works with tree-based, deep learning, linear, and black-box models.
+  Model interpretability via SHAP (Shapley values from game theory).
+  Covers explainer choice (Tree, Deep, Linear, Kernel, Gradient,
+  Permutation), feature attribution, and plots (waterfall, beeswarm,
+  bar, scatter, force, heatmap). Use to explain ML predictions, rank
+  features, debug models, audit fairness, or compare models. Works
+  with tree, deep, linear, and black-box models.
 license: MIT
 ---
 
diff --git a/skills/biostatistics/statistical-analysis/SKILL.md b/skills/biostatistics/statistical-analysis/SKILL.md
@@ -1,11 +1,11 @@
 ---
 name: statistical-analysis
 description: >-
-  Guided statistical analysis: test selection, assumption checking, effect sizes, power analysis, and APA reporting.
-  Use when choosing appropriate tests for your data, verifying assumptions, calculating effect sizes,
-  or formatting results for publication. Covers frequentist (t-test, ANOVA, chi-square, regression, correlation,
-  survival, count models, agreement/reliability) and Bayesian alternatives.
-  For implementing specific models use statsmodels or pymc-bayesian-modeling.
+  Guided statistical analysis: test choice, assumption checks, effect
+  sizes, power, APA reporting. Pick tests, verify assumptions, or
+  format results for publication. Covers frequentist (t-test, ANOVA,
+  chi-square, regression, correlation, survival, count, reliability)
+  and Bayesian. Use statsmodels or pymc-bayesian-modeling to fit.
 license: CC-BY-4.0
 ---
 
diff --git a/skills/biostatistics/statsmodels-statistical-modeling/SKILL.md b/skills/biostatistics/statsmodels-statistical-modeling/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "statsmodels-statistical-modeling"
-description: "Statistical modeling library for Python. Use for regression (OLS, WLS, GLM), discrete outcomes (Logit, Poisson, NegBin), time series (ARIMA, SARIMAX, VAR), and rigorous inference with detailed diagnostics, coefficient tables, and hypothesis tests. For ML-focused classification/regression use scikit-learn; for guided test selection use statistical-analysis."
+description: "Python statistical modeling: regression (OLS, WLS, GLM), discrete (Logit, Poisson, NegBin), time series (ARIMA, SARIMAX, VAR), with rigorous inference, diagnostics, and hypothesis tests. Use scikit-learn for ML; statistical-analysis for test choice."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/cell-biology/cellpose-cell-segmentation/SKILL.md b/skills/cell-biology/cellpose-cell-segmentation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "cellpose-cell-segmentation"
-description: "Deep learning cell and nucleus segmentation from fluorescence and brightfield microscopy images. Uses pre-trained models (cyto3, nuclei, tissuenet) and a generalist flow-based algorithm that segments cells without requiring retraining on new image types. Outputs label masks for downstream morphology measurement and tracking. Use scikit-image watershed for rule-based segmentation; use Cellpose when deep learning generalization across staining conditions is needed."
+description: "DL cell/nucleus segmentation for fluorescence and brightfield microscopy. Pre-trained models (cyto3, nuclei, tissuenet) and a generalist flow-based algorithm segment cells without retraining. Outputs label masks for morphology and tracking. Use scikit-image watershed for rule-based; Cellpose when DL generalization across staining is needed."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/cell-biology/flowio-flow-cytometry/SKILL.md b/skills/cell-biology/flowio-flow-cytometry/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: flowio-flow-cytometry
-description: "Parse and create FCS (Flow Cytometry Standard) files v2.0-3.1. Read event data as NumPy arrays, extract channel metadata, handle multi-dataset files, export to CSV/FCS. For advanced gating and compensation use FlowKit."
+description: "Parse/write FCS (Flow Cytometry) files v2.0-3.1. Events as NumPy, channel metadata, multi-dataset files, CSV/FCS export. Use FlowKit for gating/compensation."
 license: BSD-3-Clause
 ---
 
diff --git a/skills/cell-biology/histolab-wsi-processing/SKILL.md b/skills/cell-biology/histolab-wsi-processing/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "histolab-wsi-processing"
-description: "Whole slide image processing for digital pathology. Tissue detection, tile extraction (random, grid, score-based), filter pipelines for H&E/IHC preprocessing. Use for dataset preparation, tile-based deep learning, and slide quality assessment. For advanced spatial proteomics or multiplexed imaging use pathml."
+description: "WSI processing for digital pathology. Tissue detection, tile extraction (random, grid, score-based), filter pipelines for H&E/IHC. For dataset prep, tile-based DL, slide QC. Use pathml for multiplexed imaging."
 license: Apache-2.0
 ---
 
diff --git a/skills/cell-biology/imaging-data-commons/SKILL.md b/skills/cell-biology/imaging-data-commons/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "imaging-data-commons"
-description: "Query NCI Imaging Data Commons (IDC) for cancer radiology and pathology imaging datasets hosted on Google Cloud. Search DICOM collections by modality, anatomical site, cancer type, or collection name. Download images via Google Cloud Storage or IDAT tool. 50TB+ of publicly accessible DICOM images. Requires Google Cloud account for large downloads; small queries work without billing. For local DICOM processing use pydicom-medical-imaging; for whole-slide pathology use histolab."
+description: "Query NCI Imaging Data Commons (IDC) for cancer radiology and pathology datasets on Google Cloud. Search DICOM by modality, anatomical site, or cancer type; download via GCS or IDAT. 50TB+ public DICOM. GCS account needed for large downloads; metadata queries free. Use pydicom-medical-imaging for local DICOM; histolab for WSI."
 license: "CC0-1.0"
 ---
 
diff --git a/skills/cell-biology/napari-image-viewer/SKILL.md b/skills/cell-biology/napari-image-viewer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "napari-image-viewer"
-description: "Interactive multi-dimensional image viewer for scientific microscopy data. Napari displays 2D/3D/4D arrays as Image, Labels, Points, Shapes, and Tracks layers; supports real-time annotation, plugin-based analysis, and headless screenshot export. Core visualization tool for bioimage analysis workflows. Use ImageJ/FIJI for macro-based processing; use napari for Python-native interactive visualization and plugin-based deep learning segmentation review."
+description: "Interactive viewer for microscopy. Displays 2D/3D/4D arrays as Image, Labels, Points, Shapes, Tracks layers; supports annotation, plugin analysis, headless screenshots. Core visualization for Python bioimage workflows. Use ImageJ/FIJI for macro processing; napari for Python-native interactive visualization and DL segmentation review."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/cell-biology/nnunet-segmentation/SKILL.md b/skills/cell-biology/nnunet-segmentation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "nnunet-segmentation"
-description: "Train and deploy automated medical image segmentation models using nnU-Net's self-configuring framework that auto-selects optimal architecture, preprocessing, and training for any modality. Supports CT, MRI, microscopy, and ultrasound with 2D, 3D full-res, 3D low-res, and cascade configurations. Pipeline: convert dataset → plan and preprocess → train (5-fold cross-validation) → find best configuration → predict → ensemble. Use when classical segmentation fails and annotated training data is available."
+description: "Medical image segmentation with nnU-Net's self-configuring framework — auto-selects architecture, preprocessing, training for any modality. CT, MRI, microscopy, ultrasound in 2D, 3D full-res, 3D low-res, cascade. Pipeline: convert → plan/preprocess → train (5-fold CV) → best config → predict → ensemble. Use when classical segmentation fails and annotated data exists."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/cell-biology/omero-integration/SKILL.md b/skills/cell-biology/omero-integration/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "omero-integration"
-description: "OMERO is an open-source platform for biological image data management. Use the omero-py Python client to connect to an OMERO server, search and retrieve images as numpy arrays, annotate images with tags and key-value pairs, manage ROIs, and integrate OMERO image data into downstream analysis pipelines — all programmatically without the OMERO desktop GUI."
+description: "Open-source bio-image data management. Use the omero-py client to connect to an OMERO server, retrieve images as numpy arrays, annotate with tags and key-value pairs, manage ROIs, and feed image data into Python analysis pipelines — programmatically, no GUI."
 license: "GPL-2.0"
 ---
 
diff --git a/skills/cell-biology/opencv-bioimage-analysis/SKILL.md b/skills/cell-biology/opencv-bioimage-analysis/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "opencv-bioimage-analysis"
-description: "Computer vision library for bio-image preprocessing, feature detection, and real-time microscopy analysis. Performs color space conversion, morphological operations, contour/blob detection, template matching, and optical flow on fluorescence and brightfield images. 10-100× faster than pure Python implementations using optimized C++ kernels. Use scikit-image for scientific morphometry and regionprops; use OpenCV for real-time processing, video, and classical feature extraction pipelines."
+description: "Computer vision for bio-image preprocessing, feature detection, real-time microscopy. Color conversion, morphology, contour/blob detection, template matching, optical flow on fluorescence/brightfield. 10-100× faster than pure Python via C++. Use scikit-image for scientific morphometry/regionprops; OpenCV for real-time, video, classical feature extraction."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/cell-biology/pathml/SKILL.md b/skills/cell-biology/pathml/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pathml"
-description: "PathML is an open-source toolkit for computational pathology. Use it to process whole-slide images (WSIs): load slides, extract tiles, apply stain normalization and nuclear segmentation preprocessing, extract features, and train machine learning models. Supports H&E and multiplex imaging. Ideal for building end-to-end digital pathology pipelines from raw WSI files to quantitative outputs."
+description: "Computational pathology toolkit for whole-slide images (WSIs): load slides, extract tiles, stain normalization, nuclear segmentation, feature extraction, and ML training. Supports H&E and multiplex. For end-to-end pipelines from raw WSIs to quantitative outputs."
 license: "GPL-2.0"
 ---
 
diff --git a/skills/cell-biology/pydicom-medical-imaging/SKILL.md b/skills/cell-biology/pydicom-medical-imaging/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pydicom-medical-imaging"
-description: "Pure Python DICOM library for medical imaging (CT, MRI, X-ray, ultrasound). Read/write DICOM files, extract pixel data as NumPy arrays, access/modify metadata tags, apply windowing (VOI LUT), anonymize PHI, build DICOM from scratch, process series into 3D volumes. For whole-slide pathology images use histolab; for NIfTI neuroimaging use nibabel."
+description: "Pure Python DICOM for medical imaging (CT, MRI, X-ray, ultrasound). Read/write DICOM, pixels as NumPy, edit tags, windowing (VOI LUT), PHI anonymization, build DICOM, series→3D volumes. Use histolab for WSI pathology; nibabel for NIfTI."
 license: MIT
 ---
 
diff --git a/skills/cell-biology/pyimagej-fiji-bridge/SKILL.md b/skills/cell-biology/pyimagej-fiji-bridge/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pyimagej-fiji-bridge"
-description: "Python bridge to ImageJ2/Fiji enabling macro execution, plugin calls (Bio-Formats, TrackMate, Analyze Particles), bidirectional NumPy↔ImagePlus/ImgLib2 data exchange, and ImageJ Ops from Python. Use for automating Fiji-specific workflows headlessly from Python scripts. Use scikit-image instead for pure Python pipelines that do not require Fiji plugins; use napari for interactive visualization."
+description: "Python bridge to ImageJ2/Fiji for macros, plugins (Bio-Formats, TrackMate, Analyze Particles), NumPy↔ImagePlus/ImgLib2 exchange, and ImageJ Ops. Automates Fiji headlessly from Python. Use scikit-image for pure Python without Fiji plugins; napari for visualization."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/cell-biology/scikit-image-processing/SKILL.md b/skills/cell-biology/scikit-image-processing/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "scikit-image-processing"
-description: "Python image processing library for scientific microscopy and bioimage analysis. Read/write multi-format images, apply filters (Gaussian, median, LoG), segment objects (thresholding, watershed, active contours), measure region properties (area, intensity, shape), and detect features. Part of the SciPy ecosystem; integrates with NumPy arrays. Use OpenCV instead for real-time video processing; use CellPose for deep-learning cell segmentation; use napari for interactive visualization."
+description: "Python image processing for microscopy and bioimage analysis. Read/write images, filter (Gaussian, median, LoG), segment (thresholding, watershed, active contours), measure region properties, detect features. SciPy/NumPy ecosystem. Use OpenCV for real-time video; CellPose for DL cell segmentation; napari for visualization."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/cell-biology/simpleitk-image-registration/SKILL.md b/skills/cell-biology/simpleitk-image-registration/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "simpleitk-image-registration"
-description: "Register, segment, filter, and resample 3D medical images (MRI, CT, microscopy) using SimpleITK's Python API with support for DICOM, NIfTI, and multi-modal image analysis. Provides rigid/affine/deformable registration, threshold and region-growing segmentation, Gaussian and morphological filtering, label statistics, and format conversion. Use when aligning volumetric images across timepoints or modalities, automating segmentation of fluorescence microscopy, or converting DICOM series to NIfTI for analysis pipelines."
+description: "Register, segment, filter, resample 3D medical images (MRI, CT, microscopy) via SimpleITK Python; DICOM, NIfTI, multi-modal. Rigid/affine/deformable registration, threshold/region-growing segmentation, Gaussian/morph filtering, label stats, format conversion. Use to align volumes across timepoints/modalities, segment fluorescence, or convert DICOM→NIfTI."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/cell-biology/single-cell-annotation/SKILL.md b/skills/cell-biology/single-cell-annotation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: single-cell-annotation
-description: "Guide to annotating cell types in single-cell RNA-seq data. Covers manual marker-based, automated (CellTypist, scAnnotate), and reference-based (scArches, Azimuth, SingleR) approaches with decision framework for tool selection. Includes key marker genes for blood/immune, epithelial, and stromal lineages, validation checklist, and common pitfalls. Cross-references: scanpy-scrna-seq for preprocessing, celltypist-cell-annotation for automated classification, scvi-tools-single-cell for deep-learning-based label transfer."
+description: "Guide to annotating cell types in scRNA-seq. Covers manual marker-based, automated (CellTypist, scAnnotate), and reference-based (scArches, Azimuth, SingleR) approaches with a decision framework. Markers for blood/immune, epithelial, stromal lineages; validation and pitfalls. See scanpy-scrna-seq (prep), celltypist-cell-annotation (auto), scvi-tools (DL transfer)."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/cell-biology/trackpy-particle-tracking/SKILL.md b/skills/cell-biology/trackpy-particle-tracking/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "trackpy-particle-tracking"
-description: "Python library for tracking particles (fluorescent spots, colloids, vesicles, cells) in video microscopy using the Crocker-Grier algorithm. Core modules: locate particles in single frames, batch-process image sequences, link positions into trajectories, filter short-lived tracks, and compute mean squared displacement (MSD) for diffusion analysis. Supports 2D and 3D tracking with subpixel accuracy. Integrates with pims for reading TIF stacks, AVI, and image series. Use when you need quantitative single-particle tracking (SPT) from fluorescence or brightfield video and downstream diffusion coefficient extraction."
+description: "Python library for single-particle tracking (SPT) in video microscopy via the Crocker-Grier algorithm. Locate particles (fluorescent spots, colloids, vesicles, cells) per frame, link into trajectories, filter short tracks, and compute MSD for diffusion analysis. 2D/3D with subpixel accuracy; reads TIF stacks, AVI, image series via pims. Use for quantitative SPT and diffusion coefficient extraction from fluorescence or brightfield video."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/data-visualization/plotly-interactive-plots/SKILL.md b/skills/data-visualization/plotly-interactive-plots/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "plotly-interactive-plots"
-description: "Interactive scientific visualization with Plotly. Two-layer API: plotly.express (px) for one-liner DataFrame plots and plotly.graph_objects (go) for full trace-level control. 40+ chart types with hover, zoom, pan, and animation. Exports to interactive HTML or static PNG/SVG/PDF via kaleido. Use for interactive web figures, volcano plots with gene hover info, dose-response dashboards, gene expression heatmaps, and 3D molecular visualizations. Use seaborn for statistical summaries with automatic aggregation; use matplotlib for fine-grained publication figures; use plotly for interactive or web-embedded output."
+description: "Interactive scientific visualization with Plotly. Two APIs: plotly.express (px) for one-liner DataFrame plots, plotly.graph_objects (go) for trace-level control. 40+ chart types with hover, zoom, pan, animation. Exports HTML or static PNG/SVG/PDF via kaleido. Use for volcano plots with gene hover, dose-response dashboards, expression heatmaps, 3D molecular views. Use seaborn for stats; matplotlib for publication figures."
 license: "MIT"
 ---
 
diff --git a/skills/data-visualization/plotly-interactive-visualization/SKILL.md b/skills/data-visualization/plotly-interactive-visualization/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: plotly-interactive-visualization
-description: "Interactive visualization with Plotly. 40+ chart types (scatter, line, bar, heatmap, 3D, statistical, geographic) with hover, zoom, and pan. Use for exploratory analysis, dashboards, and presentations. Two APIs: Plotly Express (quick, DataFrame-oriented) and Graph Objects (fine-grained control). For static publication figures use matplotlib; for statistical grammar use seaborn."
+description: "Interactive visualization with Plotly. 40+ chart types (scatter, line, heatmap, 3D, geographic) with hover, zoom, pan. Two APIs: Plotly Express (DataFrame) and Graph Objects (fine control). For static publication figures use matplotlib; for statistical grammar use seaborn."
 license: MIT
 ---
 
diff --git a/skills/data-visualization/scientific-visualization/SKILL.md b/skills/data-visualization/scientific-visualization/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "scientific-visualization"
-description: "Guide for choosing and creating scientific visualizations for publications and presentations. Covers selecting chart types for different data structures, color theory for accessibility and print, figure composition, journal-specific formatting requirements (Nature, Cell, ACS), and common pitfalls that undermine scientific credibility. Consult this guide when deciding how to visualize your data or preparing figures for submission."
+description: "Guide for choosing and creating scientific visualizations for publications and talks. Covers chart-type selection by data structure, color theory for accessibility/print, figure composition, journal formatting (Nature, Cell, ACS), and common pitfalls. Consult when visualizing data or preparing submission figures."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/data-visualization/seaborn-statistical-plots/SKILL.md b/skills/data-visualization/seaborn-statistical-plots/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "seaborn-statistical-plots"
-description: "Statistical visualization library built on matplotlib with native pandas DataFrame support. Automatic aggregation, confidence intervals, and grouping for distribution plots (histplot, kdeplot), categorical comparisons (boxplot, violinplot, stripplot), relational plots (scatterplot, lineplot), regression plots (regplot, lmplot), matrix plots (heatmap, clustermap), and multi-variable grids (pairplot, jointplot, FacetGrid). Use seaborn for statistical summaries with minimal code; use matplotlib for fine-grained figure control; use plotly for interactive HTML output."
+description: "Statistical visualization on matplotlib with native pandas support. Auto aggregation, CIs, grouping for distributions (histplot, kdeplot), categorical (boxplot, violinplot), relational (scatterplot, lineplot), regression (regplot, lmplot), matrix (heatmap, clustermap), grids (pairplot, FacetGrid). Use for quick statistical summaries; matplotlib for fine control; plotly for interactive HTML."
 license: BSD-3-Clause
 ---
 
diff --git a/skills/data-visualization/seaborn-statistical-visualization/SKILL.md b/skills/data-visualization/seaborn-statistical-visualization/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: seaborn-statistical-visualization
-description: "Statistical visualization built on matplotlib with pandas integration. Distribution plots (histplot, kdeplot, violinplot, boxplot), relational plots (scatterplot, lineplot), categorical comparisons, regression, correlation heatmaps. Automatic aggregation and CI. For interactive plots use plotly; for low-level control use matplotlib."
+description: "Statistical visualization on matplotlib + pandas. Distributions (histplot, kdeplot, violin, box), relational (scatter, line), categorical, regression, correlation heatmaps. Auto aggregation/CIs. Use plotly for interactive; matplotlib for low-level."
 license: BSD-3-Clause
 ---
 
diff --git a/skills/data-visualization/statistical-significance-annotation/SKILL.md b/skills/data-visualization/statistical-significance-annotation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "statistical-significance-annotation"
-description: "Guide for annotating statistical significance (p-value asterisk notation) on comparison plots. Covers standard notation conventions (ns, *, **, ***, ****), when to annotate, matplotlib bracket+asterisk implementation, and integration with seaborn box/violin/bar plots. Use when generating publication-ready comparison figures that need significance markers to support statistical claims made in the analysis."
+description: "Guide for annotating statistical significance (p-value asterisks) on comparison plots. Covers standard notation (ns, *, **, ***, ****), matplotlib bracket+asterisk implementation, and use with seaborn box/violin/bar plots. Use when preparing publication-ready figures with significance markers."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/anndata-data-structure/SKILL.md b/skills/genomics-bioinformatics/anndata-data-structure/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: anndata-data-structure
-description: "Annotated data matrices for single-cell genomics. AnnData stores expression data (X) with observation metadata (obs), variable metadata (var), layers, embeddings (obsm/varm), graphs (obsp/varp), and unstructured data (uns). Use for .h5ad/.zarr file handling, dataset concatenation, and scverse ecosystem integration. For analysis workflows use scanpy; for probabilistic models use scvi-tools."
+description: "Annotated matrices for single-cell genomics. Stores X with obs/var metadata, layers, embeddings (obsm/varm), graphs (obsp/varp), uns. Use for .h5ad/.zarr I/O, concatenation, scverse integration. For analysis use scanpy; for probabilistic models use scvi-tools."
 license: BSD-3-Clause
 ---
 
diff --git a/skills/genomics-bioinformatics/arboreto-grn-inference/SKILL.md b/skills/genomics-bioinformatics/arboreto-grn-inference/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "arboreto-grn-inference"
-description: "Gene regulatory network inference from expression data using GRNBoost2 (gradient boosting) or GENIE3 (Random Forest). Load expression matrix, optionally filter by transcription factors, infer TF-target-importance links, filter and save network. Dask-parallelized for single-cell scale. Core component of the SCENIC pipeline."
+description: "GRN inference from expression via GRNBoost2 (gradient boosting) or GENIE3 (Random Forest). Load matrix, filter by TFs, infer TF-target-importance links, save network. Dask-parallelized to single-cell scale. Core SCENIC component."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/genomics-bioinformatics/archs4-database/SKILL.md b/skills/genomics-bioinformatics/archs4-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "archs4-database"
-description: "Query uniformly processed RNA-seq gene expression profiles, tissue-specific expression patterns, and co-expression networks from the ARCHS4 database REST API. Retrieve z-score normalized expression across 1M+ human and mouse samples, find co-expressed genes, search samples by metadata, and download HDF5 expression matrices. For variant-level population genetics use gnomad-database; for pathway enrichment from gene lists use gget-genomic-databases (Enrichr)."
+description: "Query ARCHS4 REST API for uniformly processed RNA-seq expression, tissue patterns, co-expression across 1M+ human/mouse samples. Retrieve z-scores, co-expressed genes, samples by metadata, HDF5 matrices. For variant population genetics use gnomad-database; for pathway enrichment use gget-genomic-databases (Enrichr)."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/bcftools-variant-manipulation/SKILL.md b/skills/genomics-bioinformatics/bcftools-variant-manipulation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "bcftools-variant-manipulation"
-description: "Command-line toolkit for VCF/BCF variant file manipulation. Filter, merge, annotate, query, normalize, and compute statistics on variant call files. Essential for post-variant-calling pipelines: quality filtering, multi-sample merging, rsID annotation, and genotype extraction. Companion to samtools in the HTSlib ecosystem. Use GATK instead for complex indel realignment during variant calling; use VCFtools instead for population genetics statistics."
+description: "CLI for VCF/BCF: filter, merge, annotate, query, normalize, compute stats. Core post-variant-calling: quality filtering, multi-sample merging, rsID annotation, genotype extraction. Samtools companion in HTSlib. Use GATK for complex indel realignment during calling; use VCFtools for population genetics stats."
 license: "MIT"
 ---
 
diff --git a/skills/genomics-bioinformatics/bedtools-genomic-intervals/SKILL.md b/skills/genomics-bioinformatics/bedtools-genomic-intervals/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "bedtools-genomic-intervals"
-description: "Toolkit for genomic interval operations on BED, BAM, GFF, VCF files. Find overlapping regions, merge adjacent intervals, calculate coverage depth, extract FASTA sequences, find nearest features, and manipulate interval coordinates. Essential for ChIP-seq peak annotation, target region filtering, and genome arithmetic. Use tabix instead for indexed single-region queries; use deeptools for normalized bigWig coverage."
+description: "Genomic interval ops on BED/BAM/GFF/VCF. Find overlaps, merge intervals, compute coverage, extract FASTA, find nearest features. Core for ChIP-seq peak annotation, region filtering, genome arithmetic. Use tabix for indexed single-region queries; use deeptools for normalized bigWig coverage."
 license: "GPL-2.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/biopython-molecular-biology/SKILL.md b/skills/genomics-bioinformatics/biopython-molecular-biology/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "biopython-molecular-biology"
-description: "Computational molecular biology toolkit for sequence manipulation, file I/O (FASTA/GenBank/PDB), NCBI database access (Entrez), BLAST automation, pairwise/multiple sequence alignment, protein structure analysis (Bio.PDB), and phylogenetic tree construction. Use for batch sequence processing, custom bioinformatics pipelines, format conversion, and programmatic PubMed/GenBank queries. For quick gene lookups use gget; for multi-service REST APIs use bioservices."
+description: "Molecular biology toolkit: sequence manipulation, FASTA/GenBank/PDB I/O, NCBI Entrez, BLAST automation, pairwise/MSA alignment, Bio.PDB, phylogenetic trees. Use for batch processing, custom pipelines, format conversion, PubMed/GenBank queries. For quick gene lookups use gget; for multi-service REST APIs use bioservices."
 license: "Biopython License (BSD-like)"
 ---
 
diff --git a/skills/genomics-bioinformatics/biopython-sequence-analysis/SKILL.md b/skills/genomics-bioinformatics/biopython-sequence-analysis/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "biopython-sequence-analysis"
-description: "Biopython toolkit for sequence analysis workflows: parse FASTA/FASTQ/GenBank/GFF with SeqIO, query NCBI databases via Entrez (esearch/efetch/elink), run remote and local BLAST with result parsing, perform pairwise and multiple sequence alignment (PairwiseAligner, MUSCLE/ClustalW), and build/visualize phylogenetic trees (Phylo module). Use for gene family studies, phylogenomics, comparative genomics, and programmatic NCBI pipelines. For PCR design, restriction digestion, and cloning workflows use biopython-molecular-biology; for SAM/BAM alignments use pysam."
+description: "Biopython sequence analysis: parse FASTA/FASTQ/GenBank/GFF (SeqIO), NCBI Entrez (esearch/efetch/elink), remote/local BLAST, pairwise/MSA alignment (PairwiseAligner, MUSCLE/ClustalW), phylogenetic trees (Phylo). Use for gene family studies, phylogenomics, comparative genomics, NCBI pipelines. For PCR/restriction/cloning use biopython-molecular-biology; for SAM/BAM use pysam."
 license: "Biopython License (BSD-like)"
 ---
 
diff --git a/skills/genomics-bioinformatics/bioservices-multi-database/SKILL.md b/skills/genomics-bioinformatics/bioservices-multi-database/SKILL.md
@@ -1,11 +1,10 @@
 ---
 name: bioservices-multi-database
 description: >
-  Unified Python interface to 40+ bioinformatics web services via bioservices library. Query
-  UniProt proteins, KEGG pathways, ChEMBL/ChEBI/PubChem compounds, run BLAST searches, map
-  identifiers across databases, retrieve GO annotations, and find protein-protein interactions.
-  For single-database deep queries use dedicated tools (gget for Ensembl, pubchempy for PubChem);
-  bioservices excels at cross-database integration workflows.
+  Unified Python interface to 40+ bioinformatics web services: UniProt proteins, KEGG
+  pathways, ChEMBL/ChEBI/PubChem, BLAST, cross-database ID mapping, GO annotations, PPI.
+  For deep single-DB queries use dedicated tools (gget for Ensembl, pubchempy for
+  PubChem); bioservices excels at cross-database workflows.
 license: GPLv3
 ---
 
diff --git a/skills/genomics-bioinformatics/busco-status-interpretation/SKILL.md b/skills/genomics-bioinformatics/busco-status-interpretation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: busco-status-interpretation
-description: "Guide to correctly interpreting BUSCO (Benchmarking Universal Single-Copy Orthologs) completeness statuses. Covers why Duplicated BUSCOs count as complete, how to parse BUSCO output files, how to compute and compare completeness across proteomes and genomes, and common counting mistakes. Relevant when running genome or proteome quality assessments with BUSCO, comparing assemblies, or reporting completeness statistics. See also: prokka-genome-annotation for annotation workflows that feed into BUSCO assessment."
+description: "Guide to interpreting BUSCO completeness statuses: why Duplicated BUSCOs count as complete, parsing output files, computing/comparing completeness across proteomes/genomes, common counting mistakes. Use when running BUSCO QC, comparing assemblies, or reporting completeness. See also: prokka-genome-annotation for annotation workflows feeding BUSCO."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/genomics-bioinformatics/bwa-mem2-dna-aligner/SKILL.md b/skills/genomics-bioinformatics/bwa-mem2-dna-aligner/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "bwa-mem2-dna-aligner"
-description: "Fast short-read DNA aligner for whole-genome, whole-exome, and ChIP-seq alignment to a reference genome. BWA-MEM2 is the 2× faster successor to BWA-MEM; outputs SAM/BAM with read group headers required by GATK. Produces primary alignments with supplementary records for chimeric reads. Use STAR instead for RNA-seq splice-aware alignment; use Bowtie2 as an alternative with comparable accuracy."
+description: "Fast short-read DNA aligner for WGS/WES/ChIP-seq. 2× faster BWA-MEM successor; outputs SAM/BAM with read group headers for GATK. Primary plus supplementary records for chimeric reads. Use STAR for RNA-seq splice-aware alignment; Bowtie2 is a comparable alternative."
 license: "MIT"
 ---
 
diff --git a/skills/genomics-bioinformatics/cbioportal-database/SKILL.md b/skills/genomics-bioinformatics/cbioportal-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "cbioportal-database"
-description: "Access TCGA and other cancer genomics datasets via cBioPortal REST API. Retrieve somatic mutations, copy number alterations, gene expression profiles, and clinical data (survival, stage, treatment) for thousands of cancer studies. Use for tumor mutation burden analysis, oncoprint queries, and survival analysis. For population variant frequencies use gnomad-database; for drug-gene interactions use dgidb-database."
+description: "Cancer genomics (TCGA et al.) via cBioPortal REST API. Retrieve somatic mutations, CNAs, expression, clinical data (survival/stage/treatment) across thousands of studies. Use for TMB, oncoprints, survival analysis. For population frequencies use gnomad-database; for drug-gene interactions use dgidb-database."
 license: "AGPL-3.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/celltypist-cell-annotation/SKILL.md b/skills/genomics-bioinformatics/celltypist-cell-annotation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "celltypist-cell-annotation"
-description: "Automated cell type annotation for scRNA-seq data using pre-trained logistic regression models. CellTypist ships 45+ models covering immune cells, gut, lung, brain, fetal tissues, and cancer microenvironments. Inputs a normalized AnnData; outputs per-cell predicted labels, majority-vote cluster labels, and confidence scores. Use when you want fast, reproducible, reference-model-backed annotation without manual marker inspection."
+description: "Automated scRNA-seq cell type annotation via pre-trained logistic regression. 45+ models: immune, gut, lung, brain, fetal, cancer microenvironments. Input normalized AnnData; outputs per-cell labels, majority-vote cluster labels, confidence scores. Use for fast, reference-backed annotation without manual marker inspection."
 license: "MIT"
 ---
 
diff --git a/skills/genomics-bioinformatics/cellxgene-census/SKILL.md b/skills/genomics-bioinformatics/cellxgene-census/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: cellxgene-census
-description: "Query CELLxGENE Census (61M+ cells) programmatically. Search by cell type, tissue, disease, organism. Get expression matrices as AnnData, stream large queries out-of-core, train PyTorch models on single-cell data. For analyzing your own data use scanpy; for annotated data manipulation use anndata."
+description: "Query CELLxGENE Census (61M+ cells). Search by cell type/tissue/disease/organism; get AnnData, stream out-of-core, train PyTorch models. For your own data use scanpy; for annotated data use anndata."
 license: MIT
 ---
 
diff --git a/skills/genomics-bioinformatics/clinpgx-database/SKILL.md b/skills/genomics-bioinformatics/clinpgx-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "clinpgx-database"
-description: "Query PharmGKB (Clinical Pharmacogenomics) database via REST API for drug-gene interactions, clinical annotations, dosing guidelines (CPIC, DPWG), variant-drug associations, and pharmacogenomic pathways. Search by gene, drug, rsID, or pathway. No authentication required. For somatic cancer pharmacogenomics use cosmic-database or opentargets-database; for drug structures use chembl-database-bioactivity."
+description: "Query PharmGKB REST API for drug-gene interactions, clinical annotations, CPIC/DPWG guidelines, variant-drug associations, PGx pathways. Search by gene/drug/rsID/pathway; no auth. For somatic cancer PGx use cosmic-database or opentargets-database; for drug structures use chembl-database-bioactivity."
 license: "CC-BY-SA-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/clinvar-database/SKILL.md b/skills/genomics-bioinformatics/clinvar-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "clinvar-database"
-description: "Query NCBI ClinVar via E-utilities REST API for clinical significance, pathogenicity classifications, and disease associations of genetic variants. Search by gene, rsID, condition, or review status. Returns structured variant records: ClinSig, submitter data, conditions, HGVS expressions. For GWAS associations use gwas-database; for variant consequence prediction use Ensembl VEP."
+description: "Query NCBI ClinVar via E-utilities for variant clinical significance, pathogenicity, disease associations. Search by gene/rsID/condition/review status; returns ClinSig, submitter data, conditions, HGVS. For GWAS use gwas-database; for variant consequence prediction use Ensembl VEP."
 license: "CC0-1.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/cnvkit-copy-number/SKILL.md b/skills/genomics-bioinformatics/cnvkit-copy-number/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "cnvkit-copy-number"
-description: "Detect somatic copy number variants (CNVs) from WES, WGS, or targeted sequencing BAM files with CNVkit v0.9.x. Pipeline: calculate bin-level coverage in target/antitarget regions, normalize against a reference, segment copy ratios with CBS or HMM, call amplifications and deletions, generate scatter/diagram plots, estimate tumor purity and ploidy, and export to VCF/SEG. Both CLI and Python API (cnvlib) shown. Use GATK CNV instead for deep WGS with population-scale controls; use CNVkit for targeted or exome sequencing where antitarget bins are critical."
+description: "Detect somatic CNVs from WES/WGS/targeted BAMs (CNVkit v0.9.x). Bin coverage in target/antitarget regions, normalize vs reference, segment with CBS/HMM, call amps/dels, scatter/diagram plots, purity/ploidy, VCF/SEG export. CLI plus Python API (cnvlib). Use GATK CNV for deep WGS with population controls; use CNVkit for targeted/exome where antitarget bins matter."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/cosmic-database/SKILL.md b/skills/genomics-bioinformatics/cosmic-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "cosmic-database"
-description: "Query COSMIC (Catalogue Of Somatic Mutations In Cancer) for cancer somatic mutations, gene census data, mutational signatures, drug resistance variants, and cancer gene annotations. REST API v3.1 supports gene/sample/variant queries. Free registration required. For germline clinical variants use clinvar-database; for drug-target data use opentargets-database or chembl-database-bioactivity."
+description: "Query COSMIC for cancer somatic mutations, gene census, mutational signatures, drug resistance variants. REST API v3.1 supports gene/sample/variant queries; free registration. For germline use clinvar-database; for drug-target data use opentargets-database or chembl-database-bioactivity."
 license: "CC-BY-NC-SA-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/dbsnp-database/SKILL.md b/skills/genomics-bioinformatics/dbsnp-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "dbsnp-database"
-description: "Query NCBI dbSNP for SNP records by rsID, gene, or genomic region via E-utilities (esearch, efetch, epost) and NCBI Variation Services REST API. Retrieve allele data, minor allele frequency, variant class (SNV, indel, MNV), clinical significance links, and cross-database IDs (ClinVar, dbVar, 1000G). Free access; 3 req/sec without API key, 10 req/sec with key. For clinical pathogenicity classifications use clinvar-database; for population frequencies use gnomad-database."
+description: "Query NCBI dbSNP for SNP records by rsID, gene, or region via E-utilities and Variation Services REST API. Retrieve alleles, MAF, variant class (SNV/indel/MNV), clinical links, cross-DB IDs (ClinVar, dbVar, 1000G). Free; 3 req/sec (10 with key). For clinical pathogenicity use clinvar-database; for population frequencies use gnomad-database."
 license: "CC0-1.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/deeptools-ngs-analysis/SKILL.md b/skills/genomics-bioinformatics/deeptools-ngs-analysis/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: deeptools-ngs-analysis
-description: "NGS analysis CLI toolkit for ChIP-seq, RNA-seq, ATAC-seq. BAM→bigWig conversion with normalization (RPGC, CPM, RPKM), sample correlation/PCA, heatmaps and profile plots around genomic features, enrichment fingerprints. For alignment use STAR/BWA; for peak calling use MACS2."
+description: "NGS CLI for ChIP/RNA/ATAC-seq. BAM→bigWig with RPGC/CPM/RPKM, sample correlation/PCA, heatmaps/profiles around features, fingerprints. For alignment use STAR/BWA; for peak calling use MACS2."
 license: BSD-3-Clause
 ---
 
diff --git a/skills/genomics-bioinformatics/depmap-crispr-essentiality/SKILL.md b/skills/genomics-bioinformatics/depmap-crispr-essentiality/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: depmap-crispr-essentiality
-description: "Guide to DepMap CRISPR gene effect (Chronos) data analysis. Covers the critical sign convention for essentiality interpretation, per-gene NaN-safe Spearman correlation computation, and data loading/alignment patterns. For general NaN-safe correlation techniques see nan-safe-correlation. For upstream data quality filtering see degenerate-input-filtering."
+description: "DepMap CRISPR gene effect (Chronos) analysis: sign convention for essentiality, per-gene NaN-safe Spearman correlation, data loading/alignment. For general NaN-safe correlation see nan-safe-correlation; for quality filtering see degenerate-input-filtering."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/genomics-bioinformatics/deseq2-differential-expression/SKILL.md b/skills/genomics-bioinformatics/deseq2-differential-expression/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "deseq2-differential-expression"
-description: "Differential expression analysis for bulk RNA-seq using R/Bioconductor DESeq2. Negative binomial GLM with empirical Bayes shrinkage, Wald and LRT tests, multi-factor designs, interaction terms, Salmon tximeta import, apeglm LFC shrinkage, MA/volcano/heatmap visualization. The R gold standard for DE analysis with native Bioconductor integration. Use pydeseq2-differential-expression for Python-based pipelines; use edgeR for TMM normalization."
+description: "Bulk RNA-seq DE with R/Bioconductor DESeq2. Negative binomial GLM, empirical Bayes shrinkage, Wald/LRT tests, multi-factor designs, Salmon tximeta import, apeglm LFC shrinkage, MA/volcano/heatmap viz. R gold standard. Use pydeseq2-differential-expression for Python; use edgeR for TMM normalization."
 license: "LGPL-3.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/ena-database/SKILL.md b/skills/genomics-bioinformatics/ena-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: ena-database
-description: "European Nucleotide Archive (ENA) REST API access for genomic sequences, raw reads, assemblies, and annotations. Portal API search with query syntax, Browser API retrieval (XML/FASTA/EMBL), file reports for FASTQ/BAM download URLs, taxonomy queries, cross-references. For multi-database Python queries prefer bioservices; for NCBI-specific queries use pubmed-database or Biopython Entrez."
+description: "ENA REST API for sequences, reads, assemblies, and annotations. Portal API search, Browser API retrieval (XML/FASTA/EMBL), file reports for FASTQ/BAM URLs, taxonomy, cross-refs. For multi-DB Python use bioservices; for NCBI-only use pubmed-database or Biopython Entrez."
 license: Unknown
 ---
 
diff --git a/skills/genomics-bioinformatics/encode-database/SKILL.md b/skills/genomics-bioinformatics/encode-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "encode-database"
-description: "Query the ENCODE Portal REST API for regulatory genomics data: TF ChIP-seq experiments, ATAC-seq/DNase-seq accessibility peaks, histone mark tracks, and RNA-seq datasets across 1000+ cell types and tissues. Search experiments by assay, biosample, or target protein; download BED/bigWig files; retrieve candidate cis-regulatory elements (cCREs) from ENCODE SCREEN by genomic region or gene. Use for finding regulatory tracks to annotate variants, identifying open chromatin in a cell type of interest, and downloading peak files for ChIP-seq or ATAC-seq analysis. For regulatory variant scoring use regulomedb-database; for GWAS associations use gwas-database."
+description: "ENCODE Portal REST API for regulatory genomics: TF ChIP-seq, ATAC-seq/DNase-seq peaks, histone marks, and RNA-seq across 1000+ cell types. Search experiments by assay/biosample/target; download BED/bigWig; retrieve SCREEN cCREs by region or gene. Use to annotate variants with regulatory tracks, find open chromatin in a cell type, or fetch peak files for ChIP/ATAC analysis. For regulatory variant scoring use regulomedb-database; for GWAS associations use gwas-database."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/ensembl-database/SKILL.md b/skills/genomics-bioinformatics/ensembl-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "ensembl-database"
-description: "Query Ensembl REST API for gene/transcript/variant annotations across 300+ species. Retrieve gene info by symbol/ID, sequence, cross-references (HGNC, RefSeq, UniProt), variants, regulatory features, comparative genomics. For bulk local access use pyensembl; for pathway lookups use kegg-database or reactome-database."
+description: "Ensembl REST API for gene/transcript/variant annotations in 300+ species. Gene info by symbol/ID, sequence, cross-refs (HGNC, RefSeq, UniProt), regulatory features. For bulk local use pyensembl; for pathways use kegg-database."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/etetoolkit/SKILL.md b/skills/genomics-bioinformatics/etetoolkit/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "etetoolkit"
-description: "ETE Toolkit (ETE3) is a Python environment for phylogenetic tree analysis, manipulation, and visualization. Parse Newick/NHX/PhyloXML trees, traverse and annotate nodes, render publication-quality figures with TreeStyle/NodeStyle, integrate NCBI taxonomy for taxon-aware operations, and run PhyloTree workflows for comparative genomics. Use for building species trees, gene family evolution analysis, and annotated tree figures."
+description: "ETE Toolkit (ETE3): Python phylogenetic tree analysis and visualization. Parse Newick/NHX/PhyloXML, traverse/annotate nodes, render figures with TreeStyle/NodeStyle, integrate NCBI taxonomy, run PhyloTree comparative genomics. Use for species trees, gene family evolution, annotated tree figures."
 license: "GPL-3.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/fastp-fastq-preprocessing/SKILL.md b/skills/genomics-bioinformatics/fastp-fastq-preprocessing/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "fastp-fastq-preprocessing"
-description: "All-in-one FASTQ quality control and adapter trimming tool. Automatically detects and removes Illumina adapters, filters low-quality reads, corrects paired-end overlaps, and generates HTML+JSON QC reports in a single fast pass. 3-10× faster than Trim Galore/Trimmomatic. Use as the first step before STAR, BWA-MEM2, or Salmon alignment in any NGS pipeline."
+description: "All-in-one FASTQ QC and adapter trimming. Auto-detects Illumina adapters, filters low-quality reads, corrects paired-end overlaps, emits HTML+JSON QC in one pass. 3-10x faster than Trim Galore/Trimmomatic. First step before STAR, BWA-MEM2, or Salmon."
 license: "MIT"
 ---
 
diff --git a/skills/genomics-bioinformatics/featurecounts-rna-counting/SKILL.md b/skills/genomics-bioinformatics/featurecounts-rna-counting/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "featurecounts-rna-counting"
-description: "Counts aligned RNA-seq reads overlapping gene features in a GTF annotation. Takes sorted BAM files from STAR alignment and a GTF file; outputs a tab-delimited count matrix per gene across all samples. Handles strandedness (0=unstranded, 1=stranded, 2=reverse-stranded), paired-end, and multi-sample batch counting in a single command. Use Salmon instead for alignment-free quantification; use featureCounts when STAR BAMs already exist and a gene-level count matrix is needed."
+description: "Counts RNA-seq reads overlapping GTF gene features. Takes sorted STAR BAMs plus GTF; outputs a per-gene tab-delimited matrix across samples. Handles strandedness (0/1/2), paired-end, multi-sample batch counting in one command, and outputs assignment statistics. Use Salmon for alignment-free quantification; use featureCounts when STAR BAMs already exist."
 license: "GPL-3.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/gatk-variant-calling/SKILL.md b/skills/genomics-bioinformatics/gatk-variant-calling/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "gatk-variant-calling"
-description: "GATK Best Practices pipeline for germline SNP and indel variant calling from WGS/WES BAM files. Runs HaplotypeCaller in GVCF mode per sample, consolidates with GenomicsDBImport, joint-genotypes with GenotypeGVCFs, and applies VQSR or hard filters. Requires BWA-MEM2-aligned, markdup, and BQSR-processed BAMs. Use DeepVariant instead for a faster deep-learning alternative; GATK is the ENCODE/NIH standard for research and clinical genomics."
+description: "GATK Best Practices for germline SNP/indel calling from WGS/WES BAMs. Per-sample HaplotypeCaller GVCFs, GenomicsDBImport, GenotypeGVCFs joint calling, VQSR or hard filters. Requires BWA-MEM2-aligned, markdup, BQSR BAMs. Use DeepVariant for a faster DL alternative; GATK is the NIH/ENCODE standard."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/genomics-bioinformatics/gene-database/SKILL.md b/skills/genomics-bioinformatics/gene-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "gene-database"
-description: "Query NCBI Gene via E-utilities for curated gene records across 1M+ taxa. Retrieve official gene symbols, aliases, RefSeq accessions, summary descriptions, genomic coordinates, GO annotations, and interaction data. Use for gene ID resolution, cross-species queries, and gene function summaries. For sequence retrieval use Ensembl; for expression data use geo-database."
+description: "NCBI Gene via E-utilities: curated records across 1M+ taxa. Official symbols, aliases, RefSeq IDs, summaries, coordinates, GO, interactions. Use for gene ID resolution and cross-species function queries. For sequences use Ensembl; for expression use geo-database."
 license: "CC0-1.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/geniml/SKILL.md b/skills/genomics-bioinformatics/geniml/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "geniml"
-description: "Geniml is a Python library for genomic interval machine learning. Train and apply region2vec embeddings to convert BED file regions into numeric vectors, load and index genomic interval datasets for ML pipelines, search embedding spaces with BEDSpace, and evaluate embedding quality. Use for chromatin accessibility clustering, regulatory element classification, cross-sample region comparison, and building ML models on genomic intervals."
+description: "Python library for genomic interval ML. Train/apply region2vec embeddings turning BED regions into vectors, index interval datasets for ML, search embedding space with BEDSpace, and evaluate embedding quality. Use for chromatin accessibility clustering, regulatory element classification, and cross-sample region comparison."
 license: "BSD-2-Clause"
 ---
 
diff --git a/skills/genomics-bioinformatics/geo-database/SKILL.md b/skills/genomics-bioinformatics/geo-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "geo-database"
-description: "Query NCBI Gene Expression Omnibus (GEO) for gene expression datasets and sample metadata via GEOparse Python library and E-utilities. Search datasets by keyword/organism/platform, download GSE series matrices, parse GPL platform annotations, extract GSM sample metadata, and load expression matrices into pandas. For single-cell data use cellxgene-census; for programmatic multi-DB access use gget-genomic-databases."
+description: "NCBI GEO access via GEOparse and E-utilities. Search by keyword/organism/platform, download GSE series matrices, parse GPL annotations, extract GSM metadata, load expression matrices into pandas. For single-cell use cellxgene-census; for multi-DB access use gget-genomic-databases."
 license: "MIT"
 ---
 
diff --git a/skills/genomics-bioinformatics/gget-genomic-databases/SKILL.md b/skills/genomics-bioinformatics/gget-genomic-databases/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: gget-genomic-databases
-description: "Unified CLI/Python interface to 20+ genomic databases. Use for quick gene lookups (Ensembl search/info/seq), BLAST/BLAT sequence alignment, AlphaFold structure prediction, enrichment analysis (Enrichr), disease/drug associations (OpenTargets), single-cell data (CELLxGENE), cancer genomics (cBioPortal/COSMIC), and expression correlation (ARCHS4). Covers genomics, proteomics, and disease domains. For batch processing or advanced BLAST use biopython; for multi-database Python SDK workflows use bioservices."
+description: "Unified CLI/Python interface to 20+ genomic databases. Gene lookups (Ensembl search/info/seq), BLAST/BLAT, AlphaFold, Enrichr enrichment, OpenTargets disease/drug, CELLxGENE single-cell, cBioPortal/COSMIC cancer, ARCHS4 expression. Spans genomics, proteomics, disease. For batch/advanced BLAST use biopython; for multi-DB Python SDK use bioservices."
 license: BSD-2-Clause
 ---
 
diff --git a/skills/genomics-bioinformatics/gnomad-database/SKILL.md b/skills/genomics-bioinformatics/gnomad-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "gnomad-database"
-description: "Query gnomAD v4 population variant frequencies via GraphQL API. Retrieve allele counts and frequencies stratified by ancestry group (AFR, AMR, EAS, NFE, SAS, FIN, ASJ, MID), gene-level constraint metrics (pLI, LOEUF, missense z-score), and read depth coverage. Identify variants with low population frequency or under evolutionary constraint. For clinical pathogenicity classifications use clinvar-database; for GWAS associations use gwas-database."
+description: "gnomAD v4 population variant frequencies via GraphQL API. Allele counts and frequencies stratified by ancestry (AFR, AMR, EAS, NFE, SAS, FIN, ASJ, MID), gene-level constraint (pLI, LOEUF, missense z), and coverage. Identify rare or constrained variants. For clinical pathogenicity use clinvar-database; for GWAS use gwas-database."
 license: "ODbL-1.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/gseapy-gene-enrichment/SKILL.md b/skills/genomics-bioinformatics/gseapy-gene-enrichment/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "gseapy-gene-enrichment"
-description: "Gene set enrichment analysis (GSEA) and over-representation analysis (ORA) for RNA-seq and proteomics data. Wraps Enrichr API for ORA against MSigDB, KEGG, GO, and 200+ gene set databases; implements preranked GSEA for ranked gene lists from differential expression. Outputs enrichment tables and GSEA running-score plots. Use after DESeq2 or edgeR for pathway-level interpretation of differential expression results."
+description: "GSEA and over-representation analysis (ORA) for RNA-seq and proteomics. Wraps Enrichr for ORA against MSigDB, KEGG, GO, and 200+ databases; runs preranked GSEA on ranked DE gene lists. Outputs enrichment tables and running-score plots. Use after DESeq2 or edgeR for pathway-level interpretation."
 license: "MIT"
 ---
 
diff --git a/skills/genomics-bioinformatics/gtars/SKILL.md b/skills/genomics-bioinformatics/gtars/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "gtars"
-description: "GTARS is a Rust-backed Python library for fast genomic token arithmetic and BED file processing. Perform high-performance BED file I/O, genomic interval set operations (intersect, merge, complement, subtract), tokenization of genomic regions against a universe, and universe construction. Use for preprocessing large BED file collections, building token vocabularies for ML pipelines, and computing interval statistics at scale."
+description: "Rust-backed Python library for fast genomic token arithmetic and BED processing. High-performance BED I/O, interval set ops (intersect, merge, complement, subtract), region tokenization against a universe, universe construction. Use for preprocessing large BED collections and ML token vocabularies."
 license: "MIT"
 ---
 
diff --git a/skills/genomics-bioinformatics/gwas-database/SKILL.md b/skills/genomics-bioinformatics/gwas-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: gwas-database
-description: "NHGRI-EBI GWAS Catalog REST API for SNP-trait associations from published genome-wide association studies. Query studies, associations, variants, traits, genes, and summary statistics. Build polygenic risk score candidates, analyze variant pleiotropy, download summary statistics for Manhattan plots. No authentication required."
+description: "NHGRI-EBI GWAS Catalog REST API for SNP-trait associations from published GWAS. Query studies, associations, variants, traits, genes, summary stats. Build PRS candidates, analyze pleiotropy, fetch stats for Manhattan plots. No auth."
 license: Apache-2.0
 ---
 
diff --git a/skills/genomics-bioinformatics/harmony-batch-correction/SKILL.md b/skills/genomics-bioinformatics/harmony-batch-correction/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "harmony-batch-correction"
-description: "Batch correction for single-cell RNA-seq (and other omics) with Harmony. Removes technical batch effects from PCA embeddings while preserving biological variation. Use after PCA, before UMAP/neighbors. Fast and scalable to millions of cells. Python (harmonypy, scanpy integration) and R (Seurat) APIs."
+description: "Harmony batch correction for scRNA-seq and other omics. Removes batch effects from PCA embeddings while preserving biology. Run after PCA, before UMAP. Scales to millions of cells. Python (harmonypy, scanpy) and R (Seurat)."
 license: "MIT"
 ---
 
diff --git a/skills/genomics-bioinformatics/homer-motif-analysis/SKILL.md b/skills/genomics-bioinformatics/homer-motif-analysis/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "homer-motif-analysis"
-description: "De novo motif discovery and known TF motif enrichment in ChIP-seq and ATAC-seq peak sets using HOMER. findMotifsGenome.pl searches for over-represented sequence patterns against a background; annotatePeaks.pl assigns genomic context (TSS distance, gene, repeat). Use after MACS3 peak calling to identify which transcription factors are enriched in your peaks, annotate peaks with nearest genes, and validate ChIP-seq quality by checking the target TF's own motif."
+description: "De novo and known TF motif enrichment in ChIP-seq/ATAC-seq peaks via HOMER. findMotifsGenome.pl finds over-represented patterns vs background; annotatePeaks.pl assigns context (TSS distance, gene, repeat). Use after MACS3 to identify enriched TFs, annotate peaks with nearest genes, and validate ChIP-seq via the target motif."
 license: "GPL-3.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/jaspar-database/SKILL.md b/skills/genomics-bioinformatics/jaspar-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "jaspar-database"
-description: "Query the JASPAR 2024 TF binding profile database via REST API and pyJASPAR. Retrieve position frequency matrices (PFMs) and position weight matrices (PWMs) by TF name, JASPAR ID, species, or structural class. Scan DNA sequences for transcription factor binding sites (TFBS). Browse profiles by taxon (Homo sapiens, Mus musculus) or TF family (bHLH, zinc finger). Use for motif enrichment input, TFBS scanning, and regulatory sequence analysis. For ChIP-seq peak-based motif discovery use homer-motif-analysis; for regulatory variant scoring use regulomedb-database."
+description: "JASPAR 2024 TF binding profiles via REST API and pyJASPAR. Retrieve PFMs/PWMs by TF name, JASPAR ID, species, or structural class. Scan DNA for TFBS; browse by taxon (human, mouse) or TF family (bHLH, zinc finger). Use for motif enrichment input, TFBS scanning, and regulatory sequence analysis. For ChIP-seq peak motif discovery use homer-motif-analysis; for regulatory variant scoring use regulomedb-database."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/kegg-database/SKILL.md b/skills/genomics-bioinformatics/kegg-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: kegg-database
-description: "Direct REST API access to KEGG (academic use only). Query pathways, genes, compounds, enzymes, diseases, drugs. Seven operations: info, list, find, get, conv, link, ddi. ID conversion (NCBI, UniProt, PubChem). For Python workflows with multiple databases, prefer bioservices."
+description: "KEGG REST API (academic only). Pathways, genes, compounds, enzymes, diseases, drugs via 7 ops (info/list/find/get/conv/link/ddi). ID conversion (NCBI/UniProt/PubChem). Use bioservices for multi-DB Python."
 license: Non-academic use of KEGG requires a commercial license
 ---
 
diff --git a/skills/genomics-bioinformatics/macs3-peak-calling/SKILL.md b/skills/genomics-bioinformatics/macs3-peak-calling/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "macs3-peak-calling"
-description: "Calls narrow and broad peaks from ChIP-seq and ATAC-seq BAM files using a Poisson model. MACS3 callpeak identifies enriched genomic regions (transcription factor binding sites or histone marks) against an input/IgG control; outputs BED narrowPeak/broadPeak files for downstream motif analysis, annotation, and differential binding. Use narrow peaks for TF ChIP-seq and ATAC-seq; use broad peaks for H3K27me3, H3K9me3, and other broad histone marks."
+description: "Poisson-model peak caller for ChIP-seq/ATAC-seq BAMs. MACS3 callpeak finds enriched regions (TF sites or histone marks) vs input/IgG; outputs BED narrowPeak/broadPeak for motif analysis, annotation, and differential binding. Use narrow peaks for TF ChIP-seq and ATAC-seq; broad for H3K27me3, H3K9me3, and other broad marks."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/genomics-bioinformatics/monarch-database/SKILL.md b/skills/genomics-bioinformatics/monarch-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "monarch-database"
-description: "Query disease-gene-phenotype associations, entity details, and cross-species orthology from the Monarch Initiative knowledge graph REST API. Retrieve MONDO disease-to-gene and disease-to-phenotype mappings, HP phenotype profiles, and cross-species phenotype comparisons. Use for rare disease gene prioritization, phenotype-based candidate gene ranking, and building disease-phenotype networks. For GWAS associations use gwas-database; for clinical pathogenicity use clinvar-database."
+description: "Monarch Initiative knowledge graph REST API for disease-gene-phenotype associations and cross-species orthology. MONDO disease-to-gene/phenotype, HP phenotype profiles, cross-species comparisons. Use for rare disease gene prioritization and phenotype-based candidate ranking. For GWAS use gwas-database; for clinical pathogenicity use clinvar-database."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/genomics-bioinformatics/mouse-phenome-database/SKILL.md b/skills/genomics-bioinformatics/mouse-phenome-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "mouse-phenome-database"
-description: "Retrieve quantitative phenotype measurements across inbred mouse strains from the Mouse Phenome Database (MPD) for metabolic, behavioral, and physiological traits. Query strain means and raw individual measurements for body weight, glucose, blood pressure, behavioral assays, and 40+ additional procedures. Use for QTL analysis support, cross-strain phenotype comparison, and identifying mouse models for metabolic or behavioral traits. For mouse gene-disease-phenotype associations use monarch-database; for mouse genome annotations use ensembl-database."
+description: "Retrieve quantitative phenotypes across inbred mouse strains from MPD: metabolic, behavioral, physiological traits. Query strain means and raw measurements for body weight, glucose, blood pressure, behavioral assays, 40+ procedures. Use for QTL support, cross-strain comparison, mouse model selection. Use monarch-database for gene-disease associations; ensembl-database for genome annotations."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/multiqc-qc-reports/SKILL.md b/skills/genomics-bioinformatics/multiqc-qc-reports/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "multiqc-qc-reports"
-description: "Aggregates QC outputs from 150+ bioinformatics tools into a single interactive HTML report. Scans directories for FastQC, samtools, STAR, HISAT2, Trim Galore, featureCounts, Kallisto, Salmon, Picard, and GATK logs; merges statistics across samples with interactive plots. Essential for NGS pipeline QC review. Use FastQC directly instead for single-sample initial assessment; MultiQC is for multi-sample pipeline-wide reporting."
+description: "Aggregates QC from 150+ bioinformatics tools into one interactive HTML report. Scans FastQC, samtools, STAR, HISAT2, Trim Galore, featureCounts, Kallisto, Salmon, Picard, GATK logs; merges per-sample stats with plots. For NGS pipeline-wide QC. Use FastQC directly for single-sample; MultiQC for multi-sample reporting."
 license: "GPL-3.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md b/skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "plink2-gwas-analysis"
-description: "Genome-wide association study (GWAS) and population genetics analysis tool. Processes PLINK (.bed/.bim/.fam), VCF, and BGEN files; performs QC (MAF, HWE, missingness), identity-by-descent estimation, principal component analysis, and linear/logistic regression GWAS. Outputs Manhattan-plot-ready summary statistics. Use regenie or SAIGE instead for very large biobanks (>100k samples) with mixed models."
+description: "GWAS and population genetics tool. Processes PLINK (.bed/.bim/.fam), VCF, and BGEN; runs QC (MAF, HWE, missingness), IBD estimation, PCA, and linear/logistic regression GWAS. Outputs Manhattan-ready summary stats. Use regenie or SAIGE for biobanks (>100k samples) needing mixed models."
 license: "GPL-3.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/popv-cell-annotation/SKILL.md b/skills/genomics-bioinformatics/popv-cell-annotation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "popv-cell-annotation"
-description: "Consensus cell type annotation by running 10+ algorithms (KNN-Harmony, KNN-BBKNN, KNN-Scanorama, KNN-scVI, CellTypist, ONCLASS, Random Forest, SCANVI, SVM, XGBoost) on a labeled reference and transferring labels to a query dataset via majority voting. popV produces per-method labels, an overall consensus prediction, and an agreement score quantifying confidence across methods. Use when single-method annotation is insufficient or when you need ensemble uncertainty estimates for novel cell states."
+description: "Consensus cell type annotation: runs 10+ algorithms (KNN-Harmony/BBKNN/Scanorama/scVI, CellTypist, ONCLASS, Random Forest, SCANVI, SVM, XGBoost) on a labeled reference and transfers labels via majority voting. Outputs per-method labels, consensus, agreement score. Use when single-method annotation is insufficient or you need ensemble uncertainty for novel states."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/genomics-bioinformatics/prokka-genome-annotation/SKILL.md b/skills/genomics-bioinformatics/prokka-genome-annotation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "prokka-genome-annotation"
-description: "Annotate prokaryotic genome assemblies (bacteria, archaea, viruses) with Prokka's BLAST/HMM-based pipeline. Identifies CDS, rRNA, tRNA, tmRNA, and signal peptides against Pfam, TIGRFAMs, and RefSeq databases. Produces GFF3, GenBank, protein FASTA, and TSV outputs. Use PGAP instead when submitting to NCBI GenBank; use Bakta for faster annotation with NCBI-compatible outputs on modern assemblies."
+description: "Annotate prokaryotic genomes (bacteria, archaea, viruses) via Prokka's BLAST/HMM pipeline. Identifies CDS, rRNA, tRNA, tmRNA, signal peptides against Pfam, TIGRFAMs, RefSeq. Outputs GFF3, GenBank, FASTA, TSV. Use PGAP for NCBI GenBank submission; Bakta for faster NCBI-compatible annotation."
 license: "GPL-3.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/pubmed-database/SKILL.md b/skills/genomics-bioinformatics/pubmed-database/SKILL.md
@@ -1,13 +1,11 @@
 ---
 name: pubmed-database
 description: >-
-  Programmatic access to PubMed biomedical literature via NCBI E-utilities
-  REST API. Covers advanced Boolean/MeSH query construction, field-tagged
-  searching, E-utilities endpoints (ESearch, EFetch, ESummary, EPost,
-  ELink), history server for batch processing, citation matching, and
-  systematic review search strategies. Use when searching biomedical
-  literature, building automated literature pipelines, or conducting
-  systematic reviews.
+  Programmatic PubMed access via NCBI E-utilities REST API. Covers
+  Boolean/MeSH queries, field-tagged search, endpoints (ESearch,
+  EFetch, ESummary, EPost, ELink), history server for batches,
+  citation matching, systematic review strategies. Use for biomedical
+  literature search or automated pipelines.
 license: CC-BY-4.0
 ---
 
diff --git a/skills/genomics-bioinformatics/pydeseq2-differential-expression/SKILL.md b/skills/genomics-bioinformatics/pydeseq2-differential-expression/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pydeseq2-differential-expression"
-description: "Bulk RNA-seq differential expression analysis with PyDESeq2. Load count matrices, normalize, fit negative binomial models, Wald test with BH-FDR correction, LFC shrinkage, volcano/MA plots. Use for two-group comparisons, multi-factor designs with batch correction, and multiple contrast testing."
+description: "Bulk RNA-seq DE with PyDESeq2: load counts, normalize, fit negative binomial models, Wald test (BH-FDR), LFC shrinkage, volcano/MA plots. Use for two-group comparisons, multi-factor designs with batch correction, multiple contrasts."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md b/skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: pysam-genomic-files
-description: "Read/write SAM/BAM/CRAM alignments, VCF/BCF variants, FASTA/FASTQ sequences. Region queries, coverage/pileup analysis, variant filtering, read group extraction. Python wrapper for htslib with samtools/bcftools CLI access. For alignment pipelines use STAR/BWA; for variant calling use GATK/DeepVariant."
+description: "Read/write SAM/BAM/CRAM, VCF/BCF, FASTA/FASTQ. Region queries, pileup, variant filtering, read groups. Python htslib wrapper exposing samtools/bcftools CLI. Use STAR/BWA for alignment; GATK/DeepVariant for variant calling."
 license: MIT
 ---
 
diff --git a/skills/genomics-bioinformatics/quickgo-database/SKILL.md b/skills/genomics-bioinformatics/quickgo-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "quickgo-database"
-description: "Query the EBI QuickGO REST API for Gene Ontology terms and protein GO annotations. Fetch GO term metadata by ID, search terms by keyword, retrieve ancestor/descendant hierarchies, and download GO annotations filtered by taxon ID, evidence code, and GO aspect. Use for GO term resolution, ontology traversal, and annotation-set retrieval before enrichment analysis. For enrichment analysis itself use gseapy-gene-enrichment; for protein function annotations use uniprot-protein-database."
+description: "Query EBI QuickGO REST API for GO terms and protein annotations. Fetch term metadata by ID, search by keyword, walk ancestor/descendant hierarchies, download annotations filtered by taxon, evidence code, aspect. Use for GO resolution, ontology traversal, annotation retrieval before enrichment. Use gseapy-gene-enrichment for enrichment; uniprot-protein-database for proteins."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/regulomedb-database/SKILL.md b/skills/genomics-bioinformatics/regulomedb-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "regulomedb-database"
-description: "Query RegulomeDB v2 REST API to score genetic variants for regulatory function and retrieve overlapping regulatory evidence (TF binding sites, histone marks, DNase-seq peaks, eQTLs, motifs). Score a single rsID or genomic position, batch-score variant lists, search regions for all regulatory variants, and retrieve full annotation details. Scores range from 1a (strongest: eQTL + TF + DNase + motif) to 7 (no known regulatory function). Use for GWAS hit prioritization, regulatory variant annotation, and cis-regulatory element discovery. For clinical pathogenicity use clinvar-database; for GWAS associations use gwas-database."
+description: "Query RegulomeDB v2 REST API to score variants for regulatory function and retrieve overlapping evidence (TF binding, histone marks, DNase peaks, eQTLs, motifs). Score single rsID/position, batch lists, region searches, and full annotations. Scores range 1a (strongest: eQTL+TF+DNase+motif) to 7 (none). Use for GWAS hit prioritization, regulatory variant annotation, cis-regulatory discovery. Use clinvar-database for pathogenicity; gwas-database for trait associations."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/remap-database/SKILL.md b/skills/genomics-bioinformatics/remap-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "remap-database"
-description: "Query the ReMap 2022 TF ChIP-seq binding peak database via REST API and BED file downloads. Retrieve all TF binding peaks overlapping a genomic region (chr:start-end), find TF peaks near a gene by name, list TFs available for a species, filter peaks by regulatory biotype (promoter, enhancer), and download peak BED files for a TF-cell type pair. Use for TF co-occupancy analysis, regulatory region annotation, and building TF binding atlases. For JASPAR motif matrices use jaspar-database; for ENCODE regulatory tracks use encode-database."
+description: "Query ReMap 2022 TF ChIP-seq peak database via REST API and BED downloads. Retrieve TF peaks overlapping a region (chr:start-end), peaks near a gene, TFs by species, peaks filtered by biotype (promoter, enhancer), and BED files for a TF-cell type pair. Use for TF co-occupancy, regulatory annotation, and TF binding atlases. Use jaspar-database for PWM motifs; encode-database for ENCODE tracks."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/salmon-rna-quantification/SKILL.md b/skills/genomics-bioinformatics/salmon-rna-quantification/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "salmon-rna-quantification"
-description: "Ultra-fast RNA-seq transcript and gene-level quantification using quasi-mapping (no BAM required). Builds a k-mer index from a transcriptome FASTA, then quantifies reads in minutes. Outputs transcript-level TPM/count tables (quant.sf) with optional GC-bias and sequence-bias correction. Integrates directly with tximeta/tximport for DESeq2 or edgeR. Use STAR instead when a genome-aligned BAM is required for variant calling or visualization."
+description: "Ultra-fast RNA-seq transcript/gene quantification via quasi-mapping (no BAM). Builds a k-mer index from transcriptome FASTA, quantifies in minutes. Outputs TPM/count tables (quant.sf) with optional GC- and sequence-bias correction. Integrates with tximeta/tximport for DESeq2/edgeR. Use STAR when a genome-aligned BAM is needed."
 license: "GPL-3.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/samtools-bam-processing/SKILL.md b/skills/genomics-bioinformatics/samtools-bam-processing/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "samtools-bam-processing"
-description: "Command-line toolkit for SAM/BAM/CRAM alignment file manipulation. Sort, index, convert, filter, and QC sequencing alignments. Core commands: view (filter/convert), sort, index, flagstat, stats, depth, markdup, merge. Required for all NGS pipelines between alignment and variant calling or peak calling. Use pysam for Python-native BAM access; use deeptools for normalized coverage tracks."
+description: "CLI toolkit for SAM/BAM/CRAM: sort, index, convert, filter, QC alignments. Core commands: view, sort, index, flagstat, stats, depth, markdup, merge. Required between alignment and variant/peak calling. Use pysam for Python-native BAM access; deeptools for normalized coverage tracks."
 license: "MIT"
 ---
 
diff --git a/skills/genomics-bioinformatics/scanpy-scrna-seq/SKILL.md b/skills/genomics-bioinformatics/scanpy-scrna-seq/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "scanpy-scrna-seq"
-description: "Single-cell RNA-seq analysis with Scanpy. QC filtering, normalization, HVG selection, PCA, neighborhood graph, UMAP/t-SNE, Leiden clustering, marker gene identification, cell type annotation, and trajectory inference. Use for standard scRNA-seq exploratory workflows."
+description: "scRNA-seq with Scanpy: QC, normalization, HVG selection, PCA, neighborhood graph, UMAP/t-SNE, Leiden clustering, markers, cell annotation, trajectory inference. Standard scRNA-seq exploration."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/scikit-bio/SKILL.md b/skills/genomics-bioinformatics/scikit-bio/SKILL.md
@@ -1,13 +1,11 @@
 ---
 name: scikit-bio
 description: >-
-  Python library for biological data analysis covering sequence manipulation
-  (DNA, RNA, protein), pairwise/multiple alignment, phylogenetic tree
-  construction (NJ, UPGMA), diversity metrics (alpha: Shannon, Faith PD;
-  beta: Bray-Curtis, UniFrac), ordination (PCoA, CCA, RDA), statistical
-  testing (PERMANOVA, ANOSIM, Mantel), and biological file I/O (FASTA,
-  FASTQ, Newick, BIOM). Use for microbiome analysis, community ecology,
-  phylogenetics, or biological sequence processing.
+  Python library for biology: sequence manipulation (DNA/RNA/protein),
+  pairwise/multiple alignment, phylogenetic trees (NJ, UPGMA), diversity
+  (Shannon, Faith PD, Bray-Curtis, UniFrac), ordination (PCoA, CCA, RDA),
+  stats (PERMANOVA, ANOSIM, Mantel), file I/O (FASTA, FASTQ, Newick,
+  BIOM). Use for microbiome, community ecology, or phylogenetics.
 license: BSD-3-Clause
 ---
 
diff --git a/skills/genomics-bioinformatics/scvi-tools-single-cell/SKILL.md b/skills/genomics-bioinformatics/scvi-tools-single-cell/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "scvi-tools-single-cell"
-description: "Deep generative models for single-cell omics. Probabilistic batch correction (scVI), semi-supervised annotation (scANVI), CITE-seq RNA+protein modeling (totalVI), transfer learning to new datasets (scARCHES), and differential expression with uncertainty quantification. Unified setup→train→extract API on AnnData. Use harmony-batch-correction for fast linear batch correction without deep learning; use muon for multi-modal MuData workflows; use scVI for probabilistic, deep learning-based integration with uncertainty quantification."
+description: "Deep generative models for single-cell omics: probabilistic batch correction (scVI), semi-supervised annotation (scANVI), CITE-seq RNA+protein (totalVI), transfer learning (scARCHES), and DE with uncertainty. Unified setup→train→extract API on AnnData. Use harmony-batch-correction for fast linear correction without deep learning; muon for multi-modal MuData workflows."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/genomics-bioinformatics/single-cell-annotation-guide/SKILL.md b/skills/genomics-bioinformatics/single-cell-annotation-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "single-cell-annotation-guide"
-description: "Decision framework for choosing between manual marker-based, automated (CellTypist), and reference-based (popV) cell type annotation strategies in single-cell RNA-seq analysis. Covers a three-tier strategy: Tier 1 (manual canonical markers), Tier 2 (CellTypist pre-trained models), and Tier 3 (popV ensemble label transfer). Use when planning or troubleshooting cell type annotation in any scRNA-seq project."
+description: "Decision framework for manual marker-based, automated (CellTypist), and reference-based (popV) cell type annotation in scRNA-seq. Three-tier strategy: Tier 1 manual markers, Tier 2 CellTypist, Tier 3 popV ensemble transfer. Use when planning or troubleshooting annotation."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/snpeff-variant-annotation/SKILL.md b/skills/genomics-bioinformatics/snpeff-variant-annotation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "snpeff-variant-annotation"
-description: "Annotate and filter genetic variants in VCF files using SnpEff and SnpSift. SnpEff predicts functional effects (HIGH/MODERATE/LOW/MODIFIER impact), gene names, transcript IDs, amino acid changes, and HGVS notation; SnpSift filters annotated VCFs and adds ClinVar/dbSNP annotations. Java-based command-line tools with Python subprocess integration. Use ANNOVAR for alternative multi-database annotation; use Ensembl VEP for web-based or REST API annotation; use SnpEff for fast command-line annotation with pre-built genome databases."
+description: "Annotate and filter VCF variants with SnpEff and SnpSift. SnpEff predicts functional effects (HIGH/MODERATE/LOW/MODIFIER), genes, transcripts, AA changes, HGVS; SnpSift filters and adds ClinVar/dbSNP. Java CLI with Python subprocess integration. Use ANNOVAR for multi-database annotation; Ensembl VEP for REST API; SnpEff for fast CLI with pre-built genomes."
 license: "MIT"
 ---
 
diff --git a/skills/genomics-bioinformatics/star-rna-seq-aligner/SKILL.md b/skills/genomics-bioinformatics/star-rna-seq-aligner/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "star-rna-seq-aligner"
-description: "Splice-aware RNA-seq read aligner producing sorted BAM files and splice junction tables. Performs genome index generation and two-pass alignment for improved junction detection. Outputs coordinate-sorted BAM, splice junctions (SJ.out.tab), alignment statistics (Log.final.out), and optional gene count tables. Use Salmon instead for ultra-fast pseudoalignment; use STAR when you need a genome-aligned BAM for downstream tools (variant calling, visualization, ENCODE pipelines)."
+description: "Splice-aware RNA-seq aligner producing sorted BAM and splice junction tables. Builds genome index, runs two-pass alignment for better junctions. Outputs sorted BAM, junctions (SJ.out.tab), stats (Log.final.out), optional gene counts. Use Salmon for fast pseudoalignment; STAR when a BAM is needed for variant calling, IGV, or ENCODE pipelines."
 license: "MIT"
 ---
 
diff --git a/skills/genomics-bioinformatics/ucsc-genome-browser/SKILL.md b/skills/genomics-bioinformatics/ucsc-genome-browser/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "ucsc-genome-browser"
-description: "Query the UCSC Genome Browser REST API for DNA sequences, track annotations, gene models, and conservation scores across 100+ genome assemblies. Retrieve sequence for any genomic region, list or fetch BED/bigWig track data, get chromosome sizes, query RefSeq/GENCODE gene structures, and access PhyloP/PhastCons conservation scores. Use for programmatic access to UCSC annotations; use Ensembl REST API instead for Ensembl-native gene IDs and VEP variant annotation."
+description: "Query UCSC Genome Browser REST API for DNA sequences, tracks, gene models, and conservation across 100+ assemblies. Retrieve sequence by region, list/fetch BED/bigWig tracks, chromosome sizes, RefSeq/GENCODE gene structures, PhyloP/PhastCons scores. Use for UCSC annotations; Ensembl REST API for Ensembl gene IDs and VEP variant annotation."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/genomics-bioinformatics/vcf-variant-filtering/SKILL.md b/skills/genomics-bioinformatics/vcf-variant-filtering/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: vcf-variant-filtering
-description: "Guide to mandatory quality filtering of raw/unfiltered VCF files before computing summary statistics such as Ts/Tv ratio, variant counts, or allele frequency distributions. Covers detection of raw VCFs via FILTER column and QUAL distribution inspection, QUAL-based filtering with bcftools, interpretation of Ts/Tv ratios, and when NOT to filter. Essential reading before any variant-level QC task. Cross-references: bcftools-variant-manipulation for advanced filtering expressions, gatk-variant-calling for upstream caller configuration, samtools-bam-processing for alignment QC prior to variant calling."
+description: "Guide to quality filtering raw VCF files before computing summary stats (Ts/Tv ratio, variant counts, AF distributions). Covers detecting raw VCFs via FILTER column and QUAL inspection, QUAL-based filtering with bcftools, Ts/Tv interpretation, and when NOT to filter. Read before any variant-level QC task. See bcftools-variant-manipulation for advanced filters, gatk-variant-calling for caller config, samtools-bam-processing for upstream alignment QC."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/lab-automation/benchling-integration/SKILL.md b/skills/lab-automation/benchling-integration/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: benchling-integration
-description: "Benchling R&D platform Python SDK. CRUD operations on registry entities (DNA, RNA, proteins, custom entities), inventory management (containers, boxes, transfers), electronic lab notebook entries, workflow automation. Requires Benchling account and API key. For local sequence analysis use biopython; for chemical databases use pubchem."
+description: "Benchling R&D Python SDK: CRUD on registry entities (DNA, RNA, proteins, custom), inventory, ELN, workflow automation. Needs Benchling account and API key. Use biopython for local sequence analysis; pubchem for chemical DBs."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/lab-automation/opentrons-integration/SKILL.md b/skills/lab-automation/opentrons-integration/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: opentrons-integration
-description: "Opentrons Protocol API v2 for OT-2 and Flex liquid handling robots. Write Python protocols for automated pipetting, serial dilutions, PCR setup, plate replication. Control hardware modules (thermocycler, heater-shaker, magnetic, temperature). For multi-vendor lab automation use pylabrobot."
+description: "Opentrons Protocol API v2 for OT-2/Flex: Python protocols for pipetting, serial dilutions, PCR, plate replication; control thermocycler, heater-shaker, magnetic, temperature modules. Use pylabrobot for multi-vendor."
 license: Apache-2.0
 ---
 
diff --git a/skills/lab-automation/opentrons-protocol-api/SKILL.md b/skills/lab-automation/opentrons-protocol-api/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "opentrons-protocol-api"
-description: "Python API v2 for programming Opentrons OT-2 and Flex liquid handling robots. Write protocols as Python files with metadata and a run() function; control pipettes, labware, and hardware modules (thermocycler, heater-shaker, magnetic, temperature). Simulate locally with opentrons_simulate, then upload to the robot app. Use PyLabRobot instead for hardware-agnostic scripts that run on Hamilton, Tecan, or other vendors."
+description: "Python API v2 for Opentrons OT-2/Flex liquid handlers: protocols as Python files with metadata and run(); control pipettes, labware, and modules (thermocycler, heater-shaker, magnetic, temperature). Simulate via opentrons_simulate then upload. Use PyLabRobot for vendor-agnostic scripts (Hamilton, Tecan)."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/lab-automation/protocolsio-integration/SKILL.md b/skills/lab-automation/protocolsio-integration/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "protocolsio-integration"
-description: "Access protocols.io public library via REST API. Search and retrieve experimental protocols (wet-lab, bioinformatics, clinical) by keyword, DOI, or category. Download step-by-step protocol content including reagents, materials, equipment, and timing. Free public access; authentication needed for private protocols or publishing. Use alongside opentrons-integration or benchling-integration to programmatically execute downloaded protocols."
+description: "protocols.io REST API: search and fetch wet-lab, bioinformatics, and clinical protocols by keyword, DOI, or category, with steps, reagents, materials, equipment, timing. Public access free; auth needed for private or publishing. Pair with opentrons-integration or benchling-integration to execute."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/lab-automation/pylabrobot/SKILL.md b/skills/lab-automation/pylabrobot/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pylabrobot"
-description: "PyLabRobot is a hardware-agnostic Python library for liquid handling robots. Use it to write portable automation scripts that run on Hamilton STAR, Tecan Freedom EVO, Opentrons OT-2, or a simulation backend — without vendor lock-in. Ideal for protocol automation, method development, plate reformatting, serial dilutions, and integrating liquid handlers into larger Python-based lab workflows."
+description: "Hardware-agnostic Python liquid-handler library: portable scripts run on Hamilton STAR, Tecan Freedom EVO, Opentrons OT-2, or a simulator without vendor lock-in. For protocol automation, method dev, plate reformatting, serial dilutions, and Python lab workflows."
 license: "MIT"
 ---
 
diff --git a/skills/lab-automation/western-blot-quantification/SKILL.md b/skills/lab-automation/western-blot-quantification/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: western-blot-quantification
-description: "Guide to quantitative Western blot analysis covering band detection, two-step normalization, fold change calculation, statistical aggregation across biological replicates, and publication-ready visualization. Consult when analyzing blot images with multiple conditions and repetitions, choosing normalization strategies, or preparing densitometry figures for publication."
+description: "Quantitative Western blot analysis: band detection, two-step normalization, fold change, replicate aggregation, publication-ready figures. Use for multi-condition, multi-replicate blots, picking a normalization strategy, or preparing densitometry figures."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/molecular-biology/plannotate-plasmid-annotation/SKILL.md b/skills/molecular-biology/plannotate-plasmid-annotation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "plannotate-plasmid-annotation"
-description: "Automatically annotate plasmid sequences with functional features (promoters, terminators, resistance genes, origins of replication, tags, fluorescent proteins) using BLAST-based detection against curated databases (Addgene, fpbase, SnapGene). Accepts FASTA or raw sequence; outputs annotated GenBank files, interactive HTML maps, and CSV feature tables. Handles circular topology correctly. Use for verifying synthetic plasmid construction, preparing Addgene submissions, sharing plasmid maps, or batch-annotating a cloning library."
+description: "Auto-annotate plasmids with features (promoters, terminators, resistance, origins, tags, fluorescent proteins) via BLAST against curated DBs (Addgene, fpbase, SnapGene). FASTA or raw sequence in; annotated GenBank, interactive HTML maps, CSV tables out. Handles circular topology. Use to verify synthetic constructs, prep Addgene submissions, share maps, or batch-annotate cloning libraries."
 license: "GPL-3.0"
 ---
 
diff --git a/skills/molecular-biology/sgrna-design-guide/SKILL.md b/skills/molecular-biology/sgrna-design-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "sgrna-design-guide"
-description: "Decision guide for finding or designing sgRNAs using a three-tiered strategy: (1) validated sequences from Addgene or literature, (2) pre-computed designs from the Broad Institute CRISPick database, (3) de novo design with CRISPOR/Benchling as a last resort. Covers PAM requirements for SpCas9, SaCas9, AsCas12a, and enAsCas12a; sgRNA quality metrics; application-specific targeting rules for knockout, CRISPRa, CRISPRi, base editing, and prime editing; and computational filtering criteria. Use when planning any CRISPR experiment and unsure which sgRNA source or design approach to use."
+description: "Decision guide for finding/designing sgRNAs via three tiers: (1) validated from Addgene/literature, (2) pre-computed from Broad CRISPick, (3) de novo via CRISPOR/Benchling as last resort. Covers PAM rules (SpCas9, SaCas9, AsCas12a, enAsCas12a), quality metrics, and targeting rules for knockout, CRISPRa/i, base and prime editing. Use when planning CRISPR and unsure which sgRNA source to pick."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/molecular-biology/viennarna-structure-prediction/SKILL.md b/skills/molecular-biology/viennarna-structure-prediction/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "viennarna-structure-prediction"
-description: "Predict RNA secondary structure, minimum free energy (MFE) folding, base pair probabilities, and RNA-RNA interactions using ViennaRNA Python bindings. Pipeline: load sequence → compute MFE structure → calculate partition function and base pair probability matrix → visualize dot-bracket notation → assess RNA-RNA duplex formation. Use for siRNA/sgRNA targeting, ribozyme design, and RNA accessibility analysis. Use mfold or RNAfold CLI directly for batch command-line use without Python."
+description: "Predict RNA secondary structure, MFE folding, base-pair probabilities, RNA-RNA interactions via ViennaRNA Python bindings. Pipeline: sequence → MFE → partition function and pair-probability matrix → dot-bracket → duplex. Use for siRNA/sgRNA targeting, ribozyme design, RNA accessibility. Use RNAfold CLI for batch use without Python."
 license: "MIT"
 ---
 
diff --git a/skills/proteomics-protein-engineering/adaptyv-bio/SKILL.md b/skills/proteomics-protein-engineering/adaptyv-bio/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "adaptyv-bio"
-description: "Adaptyv Bio provides an API and Python SDK for ordering and managing cell-free protein expression and binding assay experiments. Use it to submit protein sequences for expression (scale 10–100 µg), characterize binding affinity (KD) against target proteins, track experiment status, and retrieve results — all programmatically without wet-lab setup. Designed for protein engineers, ML-guided directed evolution, and antibody/nanobody optimization workflows. Requires an Adaptyv Bio account and API key."
+description: "API + Python SDK for ordering cell-free protein expression and binding assays. Submit sequences for expression (10–100 µg), measure binding affinity (KD) against targets, track status, and retrieve results programmatically — no wet-lab setup. Built for ML-guided directed evolution and antibody/nanobody optimization. Requires Adaptyv account and API key."
 license: "MIT"
 ---
 
diff --git a/skills/proteomics-protein-engineering/esm-protein-language-model/SKILL.md b/skills/proteomics-protein-engineering/esm-protein-language-model/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: esm-protein-language-model
-description: "Protein language models (ESM3, ESM C) for sequence generation, structure prediction, inverse folding, and protein embeddings. Use when designing novel proteins, extracting sequence representations for downstream ML, or predicting structure from sequence. Local GPU or EvolutionaryScale Forge cloud API. For traditional structure prediction use AlphaFold; for small-molecule cheminformatics use RDKit."
+description: "Protein language models (ESM3, ESM C) for sequence generation, structure prediction, inverse folding, and embeddings. Design novel proteins, extract ML features, or fold sequences. Local GPU or EvolutionaryScale Forge API. Use AlphaFold for traditional folding; RDKit for small molecules."
 license: MIT
 ---
 
diff --git a/skills/proteomics-protein-engineering/hmdb-database/SKILL.md b/skills/proteomics-protein-engineering/hmdb-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "hmdb-database"
-description: "Parse and query the Human Metabolome Database (HMDB) local XML for metabolite information, chemical properties, biological context, disease associations, spectral data, and cross-database mapping. No public REST API — primary access via downloaded XML (~6 GB). For drug-focused queries use drugbank-database-access; for live compound lookups use pubchem-compound-search."
+description: "Parse HMDB (Human Metabolome Database) local XML for metabolite info, chemical properties, biological context, disease links, spectra, and cross-DB mapping. No REST API — uses ~6 GB XML download. Use drugbank-database-access for drugs; pubchem-compound-search for live lookups."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/proteomics-protein-engineering/interpro-database/SKILL.md b/skills/proteomics-protein-engineering/interpro-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "interpro-database"
-description: "Query the InterPro REST API for protein domain architecture, family classification, and member database integration. Search InterPro entries by name or accession, retrieve all domains in a protein (domain architecture), list proteins in a family, get taxonomic distribution, and link to PDB structures. Integrates Pfam, PANTHER, PIRSF, PRINTS, PROSITE, SMART, CDD, and NCBIfam into a unified hierarchy. For protein sequence and Swiss-Prot annotations use uniprot-protein-database; for experimental 3D structures use pdb-database."
+description: "Query InterPro REST API for protein domain architecture, family classification, and member-DB integration. Search entries, retrieve a protein's domains, list family members, get taxonomic distribution, link to PDB. Unifies Pfam, PANTHER, PIRSF, PRINTS, PROSITE, SMART, CDD, NCBIfam. Use uniprot-protein-database for sequences; pdb-database for 3D structures."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/proteomics-protein-engineering/matchms-spectral-matching/SKILL.md b/skills/proteomics-protein-engineering/matchms-spectral-matching/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: matchms-spectral-matching
-description: Mass spectrometry spectral matching and metabolite identification with matchms. Use for importing spectra (mzML, MGF, MSP, JSON), filtering/normalizing peaks, computing spectral similarity (cosine, modified cosine, fingerprint), building reproducible processing pipelines, and identifying unknown metabolites from spectral libraries. For full LC-MS/MS proteomics pipelines, use pyopenms instead.
+description: MS spectral matching and metabolite ID with matchms. Import spectra (mzML, MGF, MSP, JSON), filter/normalize peaks, score similarity (cosine, modified cosine, fingerprint), build reproducible pipelines, identify unknowns vs spectral libraries. Use pyopenms for full LC-MS/MS proteomics.
 license: Apache-2.0
 ---
 
diff --git a/skills/proteomics-protein-engineering/maxquant-proteomics/SKILL.md b/skills/proteomics-protein-engineering/maxquant-proteomics/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "maxquant-proteomics"
-description: "MaxQuant + Perseus proteomics pipeline: configure and run MaxQuant for label-free quantification (LFQ) and SILAC; parse proteinGroups.txt in Python; filter contaminants/reverse decoys; log2-transform and median-normalize LFQ intensities; impute MNAR missing values; t-test with FDR correction; volcano plot; GO/pathway enrichment. Use Proteome Discoverer for Thermo instrument-native processing; FragPipe/MSFragger for GPU-accelerated database search."
+description: "MaxQuant + Perseus proteomics pipeline: run MaxQuant for LFQ and SILAC; parse proteinGroups.txt in Python; filter contaminants/decoys; log2 + median-normalize; impute MNAR; t-test with FDR; volcano plot; GO/pathway enrichment. Use Proteome Discoverer for Thermo-native processing; FragPipe/MSFragger for GPU-accelerated DB search."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/proteomics-protein-engineering/metabolomics-workbench-database/SKILL.md b/skills/proteomics-protein-engineering/metabolomics-workbench-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "metabolomics-workbench-database"
-description: "Query Metabolomics Workbench REST API (4,200+ studies, NIH-funded) for metabolite identification, study discovery, RefMet name standardization, MS m/z precursor ion searches, MetStat study filtering, and gene/protein annotations. For local metabolite XML parsing use hmdb-database; for compound property lookups use pubchem-compound-search."
+description: "Query Metabolomics Workbench REST API (4,200+ NIH studies) for metabolite ID, study discovery, RefMet standardization, m/z precursor searches, MetStat filtering, gene/protein annotations. Use hmdb-database for local XML; pubchem-compound-search for compounds."
 license: "Unknown"
 ---
 
diff --git a/skills/proteomics-protein-engineering/pride-database/SKILL.md b/skills/proteomics-protein-engineering/pride-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pride-database"
-description: "Search and retrieve proteomics datasets, peptide identifications, and mass spectrometry raw data files from the PRIDE Archive REST API. Find experiments by organism, tissue, disease, or instrument; download RAW/mzML files; retrieve peptide and PSM identifications; access protein-level evidence. For protein domain architecture use interpro-database; for protein sequences and annotations use uniprot-protein-database."
+description: "Search PRIDE Archive REST API for proteomics datasets, peptide IDs, and MS raw files. Find experiments by organism, tissue, disease, or instrument; download RAW/mzML; retrieve peptide/PSM IDs and protein-level evidence. Use interpro-database for domains; uniprot-protein-database for sequences."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/proteomics-protein-engineering/pyopenms-mass-spectrometry/SKILL.md b/skills/proteomics-protein-engineering/pyopenms-mass-spectrometry/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: pyopenms-mass-spectrometry
-description: Mass spectrometry data processing with PyOpenMS. Use for LC-MS/MS proteomics and metabolomics workflows — mzML/mzXML file I/O, signal processing (smoothing, peak picking, centroiding), feature detection and linking across samples, peptide/protein identification with FDR control, untargeted metabolomics pipelines. For simple spectral matching and metabolite ID, use matchms instead.
+description: MS data processing with PyOpenMS for LC-MS/MS proteomics and metabolomics — mzML/mzXML I/O, signal processing (smoothing, peak picking, centroiding), feature detection/linking, peptide/protein ID with FDR, untargeted metabolomics. Use matchms for simple spectral matching.
 license: BSD-3-Clause
 ---
 
diff --git a/skills/proteomics-protein-engineering/uniprot-protein-database/SKILL.md b/skills/proteomics-protein-engineering/uniprot-protein-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uniprot-protein-database
-description: "Query UniProt protein database via REST API. Search by gene/protein name, retrieve FASTA sequences, map IDs across databases (Ensembl, PDB, RefSeq), access Swiss-Prot annotations. For unified multi-database access use bioservices; for protein structure use alphafold-database."
+description: "Query UniProt REST API: search by gene/protein name, fetch FASTA, map IDs (Ensembl, PDB, RefSeq), access Swiss-Prot annotations. Use bioservices for multi-DB access; alphafold-database for structures."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/scientific-computing/aeon/SKILL.md b/skills/scientific-computing/aeon/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "aeon"
-description: "aeon is a scikit-learn compatible Python toolkit for time series machine learning and data mining. Classify, cluster, regress, segment, and transform time series using 30+ algorithms including ROCKET, InceptionTime, KNN-DTW, HIVE-COTE, and WEASEL. Supports panel (multi-instance), multivariate, and unequal-length time series. Designed as the maintained successor to sktime. Alternatives: sktime (older, larger ecosystem), tslearn (less algorithms), catch22 (feature extraction only)."
+description: "scikit-learn compatible Python toolkit for time series ML: classify, cluster, regress, segment, transform with 30+ algorithms (ROCKET, InceptionTime, KNN-DTW, HIVE-COTE, WEASEL). Handles panel, multivariate, and unequal-length series. Maintained successor to sktime. Alternatives: sktime (larger ecosystem), tslearn (fewer algorithms), catch22 (features only)."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/scientific-computing/astropy-astronomy/SKILL.md b/skills/scientific-computing/astropy-astronomy/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: astropy-astronomy
-description: "Core Python library for astronomy and astrophysics. Units & quantities with dimensional analysis, celestial coordinate transformations (ICRS/Galactic/AltAz/FK5), FITS file handling, table operations (FITS/HDF5/VOTable/CSV), cosmological calculations (Planck18, distance/age/volume), precise time handling (UTC/TAI/TT/TDB, Julian dates, barycentric corrections), WCS pixel-world mapping, model fitting, image visualization. For general data tables use pandas/polars; for radio astronomy interferometry use CASA."
+description: "Core Python library for astronomy/astrophysics: units with dimensional analysis, celestial coordinate transforms (ICRS/Galactic/AltAz/FK5), FITS I/O, tables (FITS/HDF5/VOTable/CSV), cosmology (Planck18, distance/age), precise time (UTC/TAI/TT/TDB, Julian, barycentric), WCS pixel-world mapping, model fitting. For general tables use pandas/polars; for radio interferometry use CASA."
 license: BSD-3-Clause
 ---
 
diff --git a/skills/scientific-computing/dask-parallel-computing/SKILL.md b/skills/scientific-computing/dask-parallel-computing/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: dask-parallel-computing
-description: "Distributed and parallel computing for larger-than-RAM datasets. Five components: DataFrames (parallel pandas), Arrays (parallel NumPy), Bags (unstructured data), Futures (task-based parallelism), Schedulers (threads/processes/distributed). Scales from laptops to HPC clusters. For in-memory speed on single machine use polars; for out-of-core analytics without cluster use vaex."
+description: "Parallel/distributed computing for larger-than-RAM data. Components: DataFrames (parallel pandas), Arrays (parallel NumPy), Bags, Futures, Schedulers. Scales laptop to HPC cluster. For single-machine speed use polars; for out-of-core without cluster use vaex."
 license: BSD-3-Clause
 ---
 
diff --git a/skills/scientific-computing/exploratory-data-analysis/SKILL.md b/skills/scientific-computing/exploratory-data-analysis/SKILL.md
@@ -1,12 +1,11 @@
 ---
 name: exploratory-data-analysis
 description: >-
-  Methodology for performing exploratory data analysis on scientific data files.
-  Covers decision frameworks for choosing analysis approaches based on data type
-  (tabular, sequence, image, spectral, structural, omics), quality assessment,
-  report generation, and format detection across 200+ scientific file formats.
-  Use when a user provides a data file for initial exploration or asks what
-  analysis is appropriate before running a pipeline.
+  Methodology for exploratory data analysis on scientific files. Decision
+  frameworks by data type (tabular, sequence, image, spectral, structural,
+  omics), quality assessment, report generation, format detection across 200+
+  formats. Use when given a data file for initial exploration or to pick an
+  analysis before a pipeline.
 license: CC-BY-4.0
 ---
 
diff --git a/skills/scientific-computing/geopandas-geospatial/SKILL.md b/skills/scientific-computing/geopandas-geospatial/SKILL.md
@@ -1,14 +1,11 @@
 ---
 name: geopandas-geospatial
 description: >-
-  Python library for geospatial vector data analysis extending pandas with
-  spatial operations. Covers reading/writing spatial formats (Shapefile,
-  GeoJSON, GeoPackage, Parquet, PostGIS), coordinate reference systems,
-  geometric operations (buffer, simplify, centroid, affine transforms),
-  spatial analysis (joins, overlays, dissolve, clipping, distance), and
-  visualization (choropleth, interactive maps, basemaps). Use when working
-  with geographic data for spatial joins, overlay operations, coordinate
-  transformations, area/distance calculations, or map creation.
+  Geospatial vector analysis extending pandas. Read/write spatial formats
+  (Shapefile, GeoJSON, GeoPackage, Parquet, PostGIS), CRS handling, geometric
+  ops (buffer, simplify, centroid, affine), spatial analysis (joins, overlays,
+  dissolve, clipping, distance), visualization (choropleth, interactive maps,
+  basemaps). Use for spatial joins, overlays, CRS transforms, area/distance, maps.
 license: BSD-3-Clause
 ---
 
diff --git a/skills/scientific-computing/hypogenic-hypothesis-generation/SKILL.md b/skills/scientific-computing/hypogenic-hypothesis-generation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "hypogenic-hypothesis-generation"
-description: "LLM-driven hypothesis generation and testing on tabular datasets. Three methods: HypoGeniC (data-driven), HypoRefine (literature+data synergy), Union (mechanistic combination). Iterative refinement, Redis caching, multi-hypothesis inference. For manual hypothesis formulation use hypothesis-generation knowhow; for creative ideation use scientific-brainstorming."
+description: "LLM-driven hypothesis generation/testing on tabular data. Three methods: HypoGeniC (data-driven), HypoRefine (literature+data), Union. Iterative refinement, Redis caching, multi-hypothesis inference. Manual: hypothesis-generation; ideation: scientific-brainstorming."
 license: "MIT"
 ---
 
diff --git a/skills/scientific-computing/matlab-scientific-computing/SKILL.md b/skills/scientific-computing/matlab-scientific-computing/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: matlab-scientific-computing
-description: "MATLAB/GNU Octave numerical computing for matrix operations, linear algebra, differential equations, signal processing, optimization, statistics, and scientific visualization. Code examples in MATLAB syntax (runs on both MATLAB and Octave). For Python-based scientific computing use numpy/scipy; for statistical modeling use statsmodels."
+description: "MATLAB/GNU Octave numerical computing: matrices, linear algebra, ODEs, signal processing, optimization, statistics, scientific visualization. MATLAB-syntax examples run on both. For Python use numpy/scipy; for statistical modeling use statsmodels."
 license: "GPL-3.0 (GNU Octave); MATLAB requires commercial license"
 ---
 
diff --git a/skills/scientific-computing/networkx-graph-analysis/SKILL.md b/skills/scientific-computing/networkx-graph-analysis/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "networkx-graph-analysis"
-description: "Graph and network analysis toolkit: create, manipulate, and analyze complex networks. Four graph types (directed, undirected, multi-edge), centrality measures, shortest paths, community detection, graph generators, I/O (GraphML, GML, edge list, pandas, NumPy), visualization with matplotlib. For large-scale graphs (100K+ nodes) use igraph or graph-tool; for graph neural networks use PyG."
+description: "Graph and network analysis toolkit. Four graph types (directed, undirected, multi-edge), centrality, shortest paths, community detection, generators, I/O (GraphML, GML, edge list), matplotlib viz. For large graphs (100K+ nodes) use igraph or graph-tool; for GNNs use PyG."
 license: BSD-3-Clause
 ---
 
diff --git a/skills/scientific-computing/neurokit2/SKILL.md b/skills/scientific-computing/neurokit2/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "neurokit2"
-description: "NeuroKit2 is a Python toolkit for neurophysiological signal processing. Process ECG (heart rate, HRV, R-peak detection), EEG (complexity, power spectral density), EMG (muscle activation onset), EDA/GSR (skin conductance, SCR decomposition), PPG (photoplethysmography), and RSP (respiration) signals. Simulate synthetic signals for testing. Alternatives: BioSPPy (older, less maintained), MNE (EEG/MEG specialist), heartpy (ECG only), scipy.signal (raw DSP without biosignal abstraction)."
+description: "Python toolkit for neurophysiological signal processing: ECG (HR, HRV, R-peaks), EEG (complexity, PSD), EMG (activation onset), EDA/GSR (SCR decomposition), PPG, and RSP. Includes synthetic signal simulation. Alternatives: BioSPPy (less maintained), MNE (EEG/MEG specialist), heartpy (ECG only), scipy.signal (raw DSP)."
 license: "MIT"
 ---
 
diff --git a/skills/scientific-computing/neuropixels-analysis/SKILL.md b/skills/scientific-computing/neuropixels-analysis/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "neuropixels-analysis"
-description: "Pipeline for analyzing Neuropixels extracellular electrophysiology recordings. Covers probe geometry loading (ProbeInterface), spike sorting with Kilosort via SpikeInterface, quality metrics computation, unit curation (ISI violations, firing rate, signal-to-noise), and post-sort analysis (PSTH, tuning curves, population decoding) using pandas and matplotlib. Designed for acute and chronic Neuropixels 1.0/2.0/Ultra recordings from rodent and primate experiments."
+description: "Pipeline for Neuropixels extracellular electrophysiology: probe geometry (ProbeInterface), Kilosort sorting via SpikeInterface, quality metrics, unit curation (ISI, firing rate, SNR), post-sort analysis (PSTH, tuning curves, population decoding). Supports Neuropixels 1.0/2.0/Ultra in rodent/primate experiments."
 license: "MIT"
 ---
 
diff --git a/skills/scientific-computing/nextflow-workflow-engine/SKILL.md b/skills/scientific-computing/nextflow-workflow-engine/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "nextflow-workflow-engine"
-description: "Dataflow-based scientific workflow engine for scalable bioinformatics pipelines. Nextflow defines processes (containerized tasks) connected by channels (data queues); supports local, HPC (SLURM/SGE), cloud (AWS/GCP/Azure), and Kubernetes execution with a single config change. Powers the nf-core community pipeline library. Use Snakemake instead for rule-based workflows with Python integration; use Nextflow for containerized, cloud-native, and nf-core-based pipelines."
+description: "Dataflow workflow engine for scalable bioinformatics pipelines. Defines processes (containerized tasks) connected by channels; runs local, HPC (SLURM/SGE), cloud (AWS/GCP/Azure), or Kubernetes via a single config change. Powers nf-core. Use Snakemake for rule-based Python workflows; use Nextflow for containerized, cloud-native, and nf-core pipelines."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/scientific-computing/polars-dataframes/SKILL.md b/skills/scientific-computing/polars-dataframes/SKILL.md
@@ -1,11 +1,10 @@
 ---
 name: polars-dataframes
 description: >-
-  Fast in-memory DataFrame library with lazy evaluation, parallel execution, and Apache Arrow backend.
-  Use when processing tabular data that fits in RAM (1–100 GB) and pandas is too slow.
-  Expression-based API for select, filter, group_by, joins, pivots, and window functions.
-  Lazy mode enables query optimization (predicate/projection pushdown). Reads CSV, Parquet, JSON, Excel, databases, cloud storage.
-  For larger-than-RAM data use Dask; for GPU acceleration use cuDF.
+  Fast in-memory DataFrame with lazy evaluation, parallel execution, Arrow backend.
+  Use for tabular data in RAM (1–100 GB) when pandas is too slow. Expression API:
+  select, filter, group_by, joins, pivots, window. Lazy mode enables predicate/projection
+  pushdown. Reads CSV, Parquet, JSON, Excel, DBs, cloud. Larger-than-RAM: Dask; GPU: cuDF.
 license: MIT
 ---
 
diff --git a/skills/scientific-computing/pymatgen/SKILL.md b/skills/scientific-computing/pymatgen/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pymatgen"
-description: "pymatgen (Python Materials Genomics) is a materials science Python library for structure analysis, thermodynamics, and electronic property calculation. Parse and create crystal structures (CIF, POSCAR, CIF), query the Materials Project database for DFT-computed properties, analyze phase diagrams and pourbaix diagrams, compute X-ray diffraction patterns, and generate DFT input files for VASP, Quantum ESPRESSO, and CP2K. Alternatives: ASE (Atomic Simulation Environment) for MD/geometry; AFLOW for high-throughput; OVITO for visualization."
+description: "Python Materials Genomics library for structure analysis, thermodynamics, and electronic properties. Parse/create crystal structures (CIF, POSCAR), query Materials Project for DFT-computed properties, analyze phase and Pourbaix diagrams, compute XRD patterns, generate DFT inputs for VASP, Quantum ESPRESSO, CP2K. Alternatives: ASE (MD/geometry), AFLOW (high-throughput), OVITO (visualization)."
 license: "MIT"
 ---
 
diff --git a/skills/scientific-computing/pymoo/SKILL.md b/skills/scientific-computing/pymoo/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pymoo"
-description: "pymoo is a Python framework for single- and multi-objective optimization using evolutionary algorithms. Define problems as vectorized objective functions and constraints, then solve with NSGA-II, NSGA-III, MOEA/D, genetic algorithms, or differential evolution. Analyze Pareto fronts, visualize trade-off surfaces, and customize operators and callbacks. Ideal for engineering design, hyperparameter search, process optimization, and any problem with multiple conflicting objectives. Alternatives: scipy.optimize (single-objective, gradient-based), platypus (fewer algorithms), jMetalPy (Java-based, more algorithms)."
+description: "Python framework for single- and multi-objective optimization with evolutionary algorithms. Define vectorized objectives and constraints; solve with NSGA-II, NSGA-III, MOEA/D, GAs, or differential evolution. Analyze Pareto fronts, visualize trade-offs, customize operators and callbacks. For engineering design, hyperparameter search, and conflicting objectives. Alternatives: scipy.optimize (single-objective, gradient), platypus, jMetalPy (Java)."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/scientific-computing/simpy-discrete-event-simulation/SKILL.md b/skills/scientific-computing/simpy-discrete-event-simulation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: simpy-discrete-event-simulation
-description: "Process-based discrete-event simulation framework. Model systems with queues, shared resources, and time-based events: manufacturing lines, service operations, network traffic, logistics. Processes are Python generators that yield events. Resource types include capacity-limited (Resource, PriorityResource, PreemptiveResource), bulk material (Container), and object storage (Store, FilterStore). For continuous simulation use SciPy ODE solvers; for agent-based modeling use Mesa."
+description: "Process-based discrete-event simulation. Model queues, shared resources, timed events: manufacturing, service ops, network traffic, logistics. Processes are Python generators yielding events. Resources: capacity-limited (Resource/Priority/Preemptive), bulk (Container), objects (Store, FilterStore). For continuous use SciPy ODEs; for agent-based use Mesa."
 license: MIT
 ---
 
diff --git a/skills/scientific-computing/snakemake-workflow-engine/SKILL.md b/skills/scientific-computing/snakemake-workflow-engine/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "snakemake-workflow-engine"
-description: "Python-based workflow management system for reproducible, scalable pipelines. Define rules with file-based dependencies; Snakemake automatically determines the execution order and parallelism. Supports local, SLURM, LSF, AWS, and Google Cloud execution via profiles; per-rule conda/Singularity environments. Use for bioinformatics NGS pipelines, ML training workflows, and any multi-step file-processing analysis. Use Nextflow instead for Groovy-based dataflow pipelines or when nf-core ecosystem integration is required."
+description: "Python-based workflow manager for reproducible, scalable pipelines. Define rules with file-based dependencies; Snakemake resolves execution order and parallelism. Runs local, SLURM, LSF, AWS, GCP via profiles; per-rule conda/Singularity envs. For NGS pipelines, ML training, and multi-step file processing. Use Nextflow for Groovy dataflow or nf-core integration."
 license: "MIT"
 ---
 
diff --git a/skills/scientific-computing/spikeinterface-electrophysiology/SKILL.md b/skills/scientific-computing/spikeinterface-electrophysiology/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "spikeinterface-electrophysiology"
-description: "Unified Python framework for extracellular electrophysiology. Load recordings from 20+ formats (SpikeGLX, OpenEphys, NWB, Intan, Maxwell, Blackrock), preprocess signals, run 10+ spike sorters (Kilosort4, SpykingCircus2, Tridesclous, MountainSort5) with a single API, compute quality metrics (SNR, ISI violations, firing rate, amplitude cutoff), compare sorter outputs, and export to NWB or Phy. Use for format-agnostic and multi-sorter workflows. For a Neuropixels-specific Kilosort4 pipeline with PSTH and population decoding, use neuropixels-analysis instead."
+description: "Unified Python framework for extracellular electrophysiology. Load 20+ formats (SpikeGLX, OpenEphys, NWB, Intan, Maxwell, Blackrock), preprocess, run 10+ sorters (Kilosort4, SpykingCircus2, Tridesclous, MountainSort5) via one API, compute quality metrics (SNR, ISI, firing rate), compare sorters, export NWB/Phy. For format-agnostic multi-sorter workflows. For Neuropixels-specific PSTH/decoding use neuropixels."
 license: "MIT"
 ---
 
diff --git a/skills/scientific-computing/sympy-symbolic-math/SKILL.md b/skills/scientific-computing/sympy-symbolic-math/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: sympy-symbolic-math
-description: "Symbolic mathematics in Python: exact algebra, calculus (derivatives, integrals, limits), equation solving, symbolic matrices, differential equations, code generation (lambdify, C/Fortran). Use when exact symbolic results are needed, not numerical approximations. For numerical computing use numpy/scipy; for statistical modeling use statsmodels."
+description: "Symbolic math in Python: exact algebra, calculus (derivatives, integrals, limits), equation solving, symbolic matrices, ODEs, code gen (lambdify, C/Fortran). Use for exact symbolic results. For numerical use numpy/scipy; for stats use statsmodels."
 license: BSD-3-Clause
 ---
 
diff --git a/skills/scientific-computing/torch-geometric-graph-neural-networks/SKILL.md b/skills/scientific-computing/torch-geometric-graph-neural-networks/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: torch-geometric-graph-neural-networks
-description: "PyTorch Geometric (PyG) for graph neural networks. Node classification, graph classification, link prediction with GCN, GAT, GraphSAGE, GIN layers. Message passing framework, mini-batch processing, heterogeneous graphs, neighbor sampling for large-scale learning, model explainability. Supports molecular property prediction (QM9, MoleculeNet), social networks, knowledge graphs, 3D point clouds. For non-graph deep learning use PyTorch directly; for traditional graph algorithms use NetworkX."
+description: "PyTorch Geometric (PyG) for graph neural networks: node/graph classification, link prediction with GCN, GAT, GraphSAGE, GIN. Message passing, mini-batches, heterogeneous graphs, neighbor sampling, explainability. Supports molecules (QM9, MoleculeNet), social/knowledge graphs, 3D point clouds. For non-graph DL use PyTorch; for classical graph algorithms use NetworkX."
 license: MIT
 ---
 
diff --git a/skills/scientific-computing/transformers-bio-nlp/SKILL.md b/skills/scientific-computing/transformers-bio-nlp/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "transformers-bio-nlp"
-description: "Use HuggingFace Transformers with biomedical language models for scientific NLP tasks. Load BioBERT, PubMedBERT, BioGPT, and BioMedLM for named entity recognition (genes, diseases, chemicals), relation extraction, question answering on biomedical literature, text classification, and abstract summarization. Covers model loading, tokenization of biomedical text, inference pipelines, and fine-tuning on domain-specific datasets. Alternatives: spaCy with en_core_sci_lg (rule-based NER), Stanza (Stanford NLP, biomedical models), NLTK (classical NLP)."
+description: "HuggingFace Transformers with biomedical LMs (BioBERT, PubMedBERT, BioGPT, BioMedLM) for scientific NLP: NER (genes, diseases, chemicals), relation extraction, QA, text classification, abstract summarization. Covers loading, biomedical tokenization, inference pipelines, fine-tuning. Alternatives: spaCy en_core_sci_lg (rule-based NER), Stanza (biomedical models), NLTK."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/scientific-computing/umap-learn/SKILL.md b/skills/scientific-computing/umap-learn/SKILL.md
@@ -1,14 +1,12 @@
 ---
 name: umap-learn
 description: >-
-  UMAP dimensionality reduction for visualization, clustering preprocessing, and feature
+  UMAP dimensionality reduction for visualization, clustering prep, and feature
   engineering. Fast nonlinear manifold learning preserving local and global structure.
-  Standard UMAP (fit/transform, scikit-learn compatible), supervised/semi-supervised
-  with labels, Parametric UMAP (neural network encoder/decoder, TensorFlow), DensMAP
-  (density preservation), AlignedUMAP (temporal/batch datasets). Supports 15+ distance
-  metrics, custom Numba metrics, precomputed distances. Use for 2D/3D visualization,
-  HDBSCAN clustering prep, ML feature pipelines. For linear reduction use PCA; for
-  neighborhood graphs without embedding use scikit-learn NearestNeighbors.
+  Standard UMAP (fit/transform, sklearn-compatible), supervised/semi-supervised,
+  Parametric UMAP (NN encoder/decoder, TensorFlow), DensMAP (density), AlignedUMAP
+  (temporal/batch). 15+ distance metrics, custom Numba metrics, precomputed distances.
+  For linear reduction use PCA; for neighborhood graphs use sklearn NearestNeighbors.
 license: BSD-3-Clause
 ---
 
diff --git a/skills/scientific-computing/uspto-database/SKILL.md b/skills/scientific-computing/uspto-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "uspto-database"
-description: "Access US Patent and Trademark Office (USPTO) patent data via the PatentsView REST API and Google Patents Public Data (BigQuery). Use it to search patents by inventor, assignee, CPC classification, or keywords; download full patent metadata and claims; analyze patent portfolios; and track technology trends. Ideal for IP landscape analysis, competitor monitoring, prior art searches, and technology forecasting in life sciences and biotech."
+description: "Access USPTO patent data via PatentsView REST API and Google Patents Public Data (BigQuery). Search by inventor, assignee, CPC, or keywords; download metadata and claims; analyze portfolios; track tech trends. For IP landscape analysis, competitor monitoring, prior art search, and tech forecasting in life sciences and biotech."
 license: "CC0-1.0"
 ---
 
diff --git a/skills/scientific-computing/vaex-dataframes/SKILL.md b/skills/scientific-computing/vaex-dataframes/SKILL.md
@@ -1,11 +1,10 @@
 ---
 name: vaex-dataframes
 description: >-
-  Out-of-core DataFrame library for billion-row datasets using lazy evaluation and memory-mapped files.
-  Use when data exceeds available RAM (10 GB to terabytes) and needs fast aggregation, filtering,
-  virtual columns, and visualization without loading into memory. Supports HDF5, Apache Arrow, Parquet,
-  CSV I/O with cloud storage (S3, GCS, Azure). Built-in ML transformers (scaling, encoding, PCA, K-means)
-  with scikit-learn bridge. For in-memory speed use polars; for distributed computing use dask.
+  Out-of-core DataFrame for billion-row data via lazy evaluation and memory-mapped files.
+  Use when data exceeds RAM (10 GB–TB) for fast aggregation, filtering, virtual columns,
+  and visualization without loading. Supports HDF5, Arrow, Parquet, CSV with cloud (S3,
+  GCS, Azure). Built-in ML transformers (scaling, PCA, K-means). In-memory: polars; distributed: dask.
 license: MIT
 ---
 
diff --git a/skills/scientific-computing/zarr-python/SKILL.md b/skills/scientific-computing/zarr-python/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: zarr-python
-description: "Chunked N-D arrays with compression and cloud storage. Create, read, write large arrays with NumPy-style indexing. Storage backends (local, S3, GCS, ZIP, memory). Dask/Xarray integration for parallel and labeled computation. For data management/lineage use lamindb; for labeled multi-dim arrays use xarray directly."
+description: "Chunked N-D arrays with compression and cloud storage. NumPy-style indexing. Backends: local, S3, GCS, ZIP, memory. Dask/Xarray integration for parallel and labeled computation. For lineage use lamindb; for labeled arrays use xarray."
 license: MIT
 ---
 
diff --git a/skills/scientific-writing/biorxiv-database/SKILL.md b/skills/scientific-writing/biorxiv-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "biorxiv-database"
-description: "Query bioRxiv and medRxiv preprint servers via REST API for biology and health science preprints. Search by DOI, category, or date range. Retrieve metadata (title, abstract, authors, category, DOI, version history) and download full-text PDFs. No authentication required. For peer-reviewed biomedical literature use pubmed-database; for broader scholarly search use openalex-database."
+description: "Query bioRxiv/medRxiv preprints via REST API. Search by DOI, category, or date range; retrieve metadata (title, abstract, authors, category, DOI, version history) and PDFs. No auth. For peer-reviewed biomedical use pubmed-database; broader scholarly search use openalex-database."
 license: "CC0-1.0"
 ---
 
diff --git a/skills/scientific-writing/cancer-research-figure-guide/SKILL.md b/skills/scientific-writing/cancer-research-figure-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: cancer-research-figure-guide
-description: "Figure and image preparation guide for Cancer Research (AACR). Covers resolution (300-1200 DPI), file formats (EPS, TIFF, AI), hierarchical panel labeling (Ai, Aii, Bi), figure/table limits, and legend requirements including replicate counts."
+description: "Cancer Research (AACR) figures: resolution (300-1200 DPI), formats (EPS/TIFF/AI), hierarchical panel labels (Ai, Aii, Bi), figure/table limits, legend requirements with replicate counts."
 license: CC-BY-4.0
 compatibility: Python 3.10+, Pillow, Matplotlib
 metadata:
diff --git a/skills/scientific-writing/cell-figure-guide/SKILL.md b/skills/scientific-writing/cell-figure-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: cell-figure-guide
-description: "Figure and image preparation guide for Cell (Cell Press) journal. Covers resolution (300-1000 DPI by type), file formats (TIFF, PDF), RGB color mode, Avenir/Arial fonts, uppercase panel labels, and strict image manipulation policies."
+description: "Cell (Cell Press) figure preparation: resolution (300-1000 DPI), formats (TIFF/PDF), RGB color, Avenir/Arial fonts, uppercase panel labels, strict image manipulation policies."
 license: CC-BY-4.0
 compatibility: Python 3.10+, Pillow, Matplotlib
 metadata:
diff --git a/skills/scientific-writing/citation-management/SKILL.md b/skills/scientific-writing/citation-management/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "citation-management"
-description: "Guide for selecting a reference manager, organizing citations, and applying citation styles in scientific writing. Covers Zotero, Mendeley, EndNote, and Paperpile comparison; APA, Vancouver, ACS, and Nature citation styles; DOI management; citation tracking; and integration with Word, Google Docs, and LaTeX. Use when setting up a reference workflow, switching tools, or troubleshooting citation formatting."
+description: "Selecting a reference manager and applying citation styles. Compares Zotero, Mendeley, EndNote, Paperpile; covers APA/Vancouver/ACS/Nature styles, DOI management, citation tracking, and Word/Google Docs/LaTeX integration. Use when setting up a reference workflow or fixing citation formatting."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/scientific-writing/elife-figure-guide/SKILL.md b/skills/scientific-writing/elife-figure-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: elife-figure-guide
-description: "Figure and image preparation guide for eLife. Covers file formats (TIFF, EPS, PDF), striking image requirements (1800x900 px), figure supplement naming conventions, and routine image screening policy where selective enhancement is treated as misconduct."
+description: "eLife figure preparation: file formats (TIFF/EPS/PDF), striking image requirements (1800x900 px), figure supplement naming, and image screening policy treating selective enhancement as misconduct."
 license: CC-BY-4.0
 compatibility: Python 3.10+, Pillow, Matplotlib
 metadata:
diff --git a/skills/scientific-writing/general-figure-guide/SKILL.md b/skills/scientific-writing/general-figure-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: general-figure-guide
-description: "General scientific figure quality checklist for generated plots. Covers visual inspection for overlapping labels, clipped text, missing axes/legends, empty plot areas, overcrowded data, and resolution/format best practices across journals."
+description: "Universal QA checklist for generated scientific plots: overlapping labels, clipped text, missing axes/legends, overcrowded data, and cross-journal resolution/format guidance."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/scientific-writing/lancet-figure-guide/SKILL.md b/skills/scientific-writing/lancet-figure-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: lancet-figure-guide
-description: "Figure and image preparation guide for The Lancet. Covers resolution (300+ DPI at 120% size), file formats (PowerPoint, Word, SVG preferred), column widths (75/154 mm), Times New Roman font, and Lancet in-house redraw policy."
+description: "The Lancet figure preparation: resolution (300+ DPI at 120%), preferred editable formats (PowerPoint/Word/SVG), column widths (75/154 mm), Times New Roman, in-house redraw policy."
 license: CC-BY-4.0
 compatibility: Python 3.10+, Pillow, Matplotlib
 metadata:
diff --git a/skills/scientific-writing/latex-research-posters/SKILL.md b/skills/scientific-writing/latex-research-posters/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: latex-research-posters
-description: "Create professional research posters in LaTeX using beamerposter, tikzposter, or baposter. Layout design, typography, color schemes, figure integration, accessibility, and quality control for conference presentations. Includes ready-to-use templates. For programmatic figure generation use matplotlib-scientific-plotting or plotly-interactive-visualization."
+description: "Research posters in LaTeX using beamerposter, tikzposter, or baposter. Layout, typography, color schemes, figure integration, accessibility, and QA for conferences. Includes templates. For figure generation use matplotlib-scientific-plotting or plotly-interactive-visualization."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/scientific-writing/literature-review/SKILL.md b/skills/scientific-writing/literature-review/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "literature-review"
-description: "Guide for conducting systematic, scoping, and narrative literature reviews. Covers PRISMA and PRISMA-ScR protocols, structured search strategy design (Boolean operators, MeSH terms), database selection (PubMed, Scopus, Web of Science, Embase), title/abstract/full-text screening, data extraction templates, evidence synthesis (narrative, meta-analysis, thematic), and reporting standards. Use when planning or executing a formal literature review."
+description: "Conducting systematic, scoping, and narrative literature reviews. Covers PRISMA/PRISMA-ScR protocols, search strategy (Boolean, MeSH), database selection (PubMed, Scopus, Web of Science, Embase), screening, data extraction, evidence synthesis (narrative, meta-analysis, thematic), and reporting. Use when planning or executing a formal literature review."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/scientific-writing/nature-figure-guide/SKILL.md b/skills/scientific-writing/nature-figure-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: nature-figure-guide
-description: "Figure and image preparation guide for Nature journal. Covers resolution (300+ DPI), file formats (AI, EPS, TIFF), RGB color mode, Helvetica/Arial fonts, lowercase panel labels, and image integrity requirements."
+description: "Nature figure preparation: resolution (300+ DPI), formats (AI/EPS/TIFF), RGB color, Helvetica/Arial fonts, lowercase panel labels, image integrity requirements."
 license: CC-BY-4.0
 compatibility: Python 3.10+, Pillow, Matplotlib
 metadata:
diff --git a/skills/scientific-writing/nejm-figure-guide/SKILL.md b/skills/scientific-writing/nejm-figure-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: nejm-figure-guide
-description: "Figure and image preparation guide for the New England Journal of Medicine (NEJM). Covers resolution (300-1200 DPI), editable vector formats (AI, EPS, SVG), in-house medical illustration policy, and strict image integrity requirements."
+description: "NEJM figure preparation: resolution (300-1200 DPI), editable vector formats (AI/EPS/SVG), in-house medical illustration policy, and strict image integrity requirements."
 license: CC-BY-4.0
 compatibility: Python 3.10+, Pillow, Matplotlib
 metadata:
diff --git a/skills/scientific-writing/openalex-database/SKILL.md b/skills/scientific-writing/openalex-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "openalex-database"
-description: "Query OpenAlex REST API for scholarly literature — 250M+ works, authors, institutions, journals, and concepts. Search by title/abstract keywords, author, DOI, ORCID, or OpenAlex ID. Filter by year, open access status, citation count, or field. Retrieve citations, references, and author disambiguation. Free, no authentication required. For PubMed biomedical search use pubmed-database; for bioRxiv preprints use biorxiv-database."
+description: "Query OpenAlex REST API for 250M+ scholarly works, authors, institutions, journals, concepts. Search by keyword, author, DOI, ORCID, or ID; filter by year, OA, citations, field; retrieve citations, references, author disambiguation. Free, no auth. For PubMed use pubmed-database; preprints use biorxiv-database."
 license: "CC0-1.0"
 ---
 
diff --git a/skills/scientific-writing/peer-review-methodology/SKILL.md b/skills/scientific-writing/peer-review-methodology/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: peer-review-methodology
-description: "Structured peer review of scientific manuscripts and grants. 7-stage evaluation: initial assessment, section-by-section review, statistical rigor, reproducibility, figure integrity, ethics, and writing quality. Covers CONSORT/STROBE/PRISMA compliance, review report structure (summary, major/minor comments, questions). For evaluating evidence quality use scientific-critical-thinking; for quantitative scoring use scholar-evaluation."
+description: "Structured peer review of manuscripts and grants. 7-stage evaluation: initial assessment, section review, statistical rigor, reproducibility, figure integrity, ethics, writing. Covers CONSORT/STROBE/PRISMA and report structure. For evidence quality see scientific-critical-thinking; scoring see scholar-evaluation."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/scientific-writing/pnas-figure-guide/SKILL.md b/skills/scientific-writing/pnas-figure-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: pnas-figure-guide
-description: "Figure and image preparation guide for PNAS. Covers resolution (300-1000 PPI by type), file formats (TIFF, EPS, PDF), strict RGB-only color mode, Arial/Helvetica fonts, italicized uppercase panel labels, and automated image screening."
+description: "PNAS figure preparation: resolution (300-1000 PPI), formats (TIFF/EPS/PDF), strict RGB-only color, Arial/Helvetica fonts, italicized uppercase panel labels, automated image screening."
 license: CC-BY-4.0
 compatibility: Python 3.10+, Pillow, Matplotlib
 metadata:
diff --git a/skills/scientific-writing/science-figure-guide/SKILL.md b/skills/scientific-writing/science-figure-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: science-figure-guide
-description: "Figure and image preparation guide for Science (AAAS) journal. Covers resolution (150-300+ DPI), file formats (PDF, EPS, TIFF), RGB color mode, Myriad/Helvetica fonts, and strict image manipulation policies including gamma adjustment disclosure."
+description: "Science (AAAS) figure preparation: resolution (150-300+ DPI), formats (PDF/EPS/TIFF), RGB color, Myriad/Helvetica fonts, strict image manipulation policies including gamma adjustment disclosure."
 license: CC-BY-4.0
 compatibility: Python 3.10+, Pillow, Matplotlib
 metadata:
diff --git a/skills/scientific-writing/scientific-brainstorming/SKILL.md b/skills/scientific-writing/scientific-brainstorming/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "scientific-brainstorming"
-description: "Structured ideation methods for scientific research: SCAMPER, Six Thinking Hats, Morphological Analysis, TRIZ, Biomimicry, and 4 more techniques. Decision framework for choosing methods by challenge type (stuck, improving existing, systematic exploration, contradiction resolution). Use when generating research ideas, exploring interdisciplinary connections, or challenging assumptions."
+description: "Structured ideation methods: SCAMPER, Six Thinking Hats, Morphological Analysis, TRIZ, Biomimicry, plus more. Decision framework for picking methods by challenge type (stuck, improving, systematic exploration, contradiction). Use when generating research ideas or exploring interdisciplinary connections."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/scientific-writing/scientific-critical-thinking/SKILL.md b/skills/scientific-writing/scientific-critical-thinking/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "scientific-critical-thinking"
-description: "Guide for evaluating scientific evidence and claims. Covers study design hierarchy (RCT to expert opinion), effect size interpretation (OR, RR, NNT, Cohen's d), confounding identification, p-value limitations vs clinical significance, GRADE evidence quality assessment, reproducibility, and bias types (selection, information, confounding, reporting). Use when reading a paper, evaluating a preprint, or assessing claims in a literature review."
+description: "Evaluating scientific evidence and claims. Covers study design hierarchy (RCT to expert opinion), effect sizes (OR, RR, NNT, Cohen's d), confounding, p-value vs clinical significance, GRADE quality assessment, reproducibility, and bias types (selection, information, confounding, reporting). Use when reading a paper or assessing claims."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/scientific-writing/scientific-literature-search/SKILL.md b/skills/scientific-writing/scientific-literature-search/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scientific-literature-search
-description: "Systematic strategies for searching, retrieving, and analyzing scientific literature across PubMed, arXiv, Google Scholar, and AI-assisted tools. Covers the PICO framework for clinical question formulation, three-tiered search strategy (database-specific, AI-assisted, content extraction), PubMed field tags and MeSH vocabulary, boolean query construction, and full-text extraction workflows. Consult this guide when planning a literature search, constructing database queries, or deciding which search tier to use for a given research question."
+description: "Systematic strategies for searching scientific literature across PubMed, arXiv, Google Scholar, and AI-assisted tools. Covers PICO framework for clinical questions, three-tiered search (database-specific, AI-assisted, content extraction), PubMed field tags and MeSH, boolean query construction, and full-text extraction. Use when planning a literature search or choosing a search tier."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/scientific-writing/scientific-manuscript-writing/SKILL.md b/skills/scientific-writing/scientific-manuscript-writing/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "scientific-manuscript-writing"
-description: "Scientific manuscript writing knowledge: IMRAD structure, citation styles (APA/AMA/Vancouver/IEEE), figures and tables best practices, reporting guidelines (CONSORT/STROBE/PRISMA/ARRIVE), writing principles (clarity/conciseness/accuracy), field-specific terminology, venue-specific style adaptation. For LaTeX report formatting see companion assets."
+description: "Scientific manuscript writing: IMRAD, citation styles (APA/AMA/Vancouver/IEEE), figures/tables, reporting guidelines (CONSORT/STROBE/PRISMA/ARRIVE), writing principles (clarity/conciseness/accuracy), venue-specific style. For LaTeX see companion assets."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/scientific-writing/scientific-schematics/SKILL.md b/skills/scientific-writing/scientific-schematics/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "scientific-schematics"
-description: "Guide for designing and creating scientific schematics, diagrams, and graphical abstracts. Covers tool selection (BioRender, Inkscape, Affinity Designer, PowerPoint), design principles for biological pathway diagrams, molecular mechanism schematics, experimental workflow diagrams, and graphical abstracts for journal submissions. Includes composition rules, icon sourcing, color usage for biological entities, and accessibility considerations. Use when planning or creating a scientific figure that is primarily illustrative rather than data-driven."
+description: "Designing scientific schematics, diagrams, and graphical abstracts. Covers tool selection (BioRender, Inkscape, Affinity, PowerPoint), design principles for pathway diagrams, mechanism schematics, experimental workflows, and journal graphical abstracts. Includes composition, icon sourcing, color for biological entities, and accessibility. Use when creating illustrative (not data-driven) scientific figures."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/scientific-writing/scientific-slides/SKILL.md b/skills/scientific-writing/scientific-slides/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scientific-slides
-description: "Create effective scientific presentations for conferences, seminars, thesis defenses, and grant pitches. Slide design principles, talk structure, timing, data visualization for slides, quality assurance. Works with PowerPoint and LaTeX Beamer. For poster creation use latex-research-posters."
+description: "Scientific presentations for conferences, seminars, thesis defenses, and grant pitches. Slide design, talk structure, timing, data viz for slides, QA. PowerPoint and LaTeX Beamer. For posters use latex-research-posters."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/structural-biology-drug-discovery/alphafold-database-access/SKILL.md b/skills/structural-biology-drug-discovery/alphafold-database-access/SKILL.md
@@ -1,10 +1,9 @@
 ---
 name: alphafold-database-access
 description: >
-  Access AlphaFold DB's 200M+ AI-predicted protein structures. Retrieve structures by UniProt ID,
-  download PDB/mmCIF files, analyze confidence metrics (pLDDT, PAE), bulk-download proteomes via
-  Google Cloud. For experimental structures use PDB directly; for structure prediction use
-  ColabFold or ESMFold.
+  Access AlphaFold DB's 200M+ predicted structures by UniProt ID. Download PDB/mmCIF,
+  analyze pLDDT/PAE, bulk-fetch proteomes via Google Cloud. For experimental structures
+  use PDB; for prediction use ColabFold or ESMFold.
 license: CC-BY-4.0
 ---
 
diff --git a/skills/structural-biology-drug-discovery/autodock-vina-docking/SKILL.md b/skills/structural-biology-drug-discovery/autodock-vina-docking/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "autodock-vina-docking"
-description: "Molecular docking with AutoDock Vina via Python API. Receptor/ligand preparation (Meeko + RDKit), grid box setup, docking execution, pose extraction, binding energy analysis, and batch virtual screening. Use for protein-ligand docking and hit identification."
+description: "Molecular docking with AutoDock Vina (Python API). Receptor/ligand prep (Meeko + RDKit), grid box, docking, pose and binding energy analysis, and batch virtual screening."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/chembl-database-bioactivity/SKILL.md b/skills/structural-biology-drug-discovery/chembl-database-bioactivity/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: chembl-database-bioactivity
-description: Query ChEMBL bioactive molecules and drug discovery data using the Python SDK. Search compounds by structure/properties, retrieve bioactivity data (IC50, Ki, EC50), find inhibitors for targets, perform SAR studies, and access drug mechanism/indication data for medicinal chemistry research.
+description: Query ChEMBL via Python SDK. Search compounds by structure/properties, retrieve bioactivity (IC50, Ki, EC50), find target inhibitors, run SAR, access drug mechanism/indication data.
 license: CC-BY-SA-3.0
 ---
 
diff --git a/skills/structural-biology-drug-discovery/clinicaltrials-database-search/SKILL.md b/skills/structural-biology-drug-discovery/clinicaltrials-database-search/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: clinicaltrials-database-search
-description: Query ClinicalTrials.gov API v2 for clinical study data. Search trials by condition, drug/intervention, location, sponsor, or phase. Retrieve detailed study information by NCT ID. Filter by recruitment status, paginate large result sets, export to CSV. For clinical research, patient matching, drug development tracking, and trial portfolio analysis.
+description: Query ClinicalTrials.gov API v2 for trial data. Search by condition, drug/intervention, location, sponsor, or phase; fetch details by NCT ID; filter by status; paginate; export CSV. For clinical research, patient matching, and trial portfolio analysis.
 license: CC-BY-4.0
 ---
 
diff --git a/skills/structural-biology-drug-discovery/dailymed-database/SKILL.md b/skills/structural-biology-drug-discovery/dailymed-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "dailymed-database"
-description: "Query FDA-approved drug labeling from DailyMed (NLM) via REST API. Search structured product labels (SPLs) by drug name, NDC code, set ID, or RxCUI. Retrieve indications, contraindications, dosage, warnings, adverse reactions, and packaging information. No authentication required. For adverse event reports use fda-database; for drug-drug interactions use ddinter-database."
+description: "Query FDA drug labels (DailyMed) via REST API. Search structured product labels (SPLs) by name, NDC, set ID, or RxCUI; get indications, dosage, warnings, adverse reactions, packaging. No auth. For adverse events use fda-database; for DDIs use ddinter-database."
 license: "CC0-1.0"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/datamol-cheminformatics/SKILL.md b/skills/structural-biology-drug-discovery/datamol-cheminformatics/SKILL.md
@@ -1,13 +1,11 @@
 ---
 name: datamol-cheminformatics
 description: >-
-  Pythonic wrapper around RDKit with simplified interface and sensible defaults
-  for drug discovery cheminformatics. Use for SMILES parsing, molecular
-  standardization, descriptor computation, fingerprints, similarity search,
-  clustering, diversity selection, scaffold analysis, BRICS/RECAP fragmentation,
-  3D conformer generation, and molecular visualization. Returns native
-  rdkit.Chem.Mol objects. Prefer datamol over raw RDKit for standard workflows;
-  use RDKit directly for advanced control or custom parameters.
+  Pythonic RDKit wrapper with sensible defaults for drug discovery. SMILES parsing,
+  standardization, descriptors, fingerprints, similarity, clustering, diversity
+  selection, scaffold analysis, BRICS/RECAP fragmentation, 3D conformers, and
+  visualization. Returns native rdkit.Chem.Mol. Prefer datamol for standard
+  workflows; use RDKit directly for advanced control.
 license: Apache-2.0
 ---
 
diff --git a/skills/structural-biology-drug-discovery/ddinter-database/SKILL.md b/skills/structural-biology-drug-discovery/ddinter-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "ddinter-database"
-description: "Query drug-drug interaction (DDI) data from DDInter via REST API. Search interactions by drug name or ID, retrieve severity levels (major/moderate/minor), interaction mechanisms, and clinical recommendations for drug pairs. Covers 1.7M+ interactions across 2,400+ drugs. No authentication required. For FDA drug labeling use dailymed-database; for pharmacogenomics use clinpgx-database."
+description: "Query DDInter drug-drug interactions via REST API (1.7M+ interactions, 2,400+ drugs). Search by drug name/ID for severity (major/moderate/minor), mechanisms, and clinical recommendations. No auth. For FDA labeling use dailymed-database; for pharmacogenomics use clinpgx-database."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/deepchem/SKILL.md b/skills/structural-biology-drug-discovery/deepchem/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: deepchem
-description: "Deep learning framework for drug discovery and materials science. 60+ models (GCN, GAT, AttentiveFP, MPNN, DMPNN, ChemBERTa, GROVER), 50+ molecular featurizers, MoleculeNet benchmarks, hyperparameter optimization, transfer learning. Unified load-featurize-split-train-evaluate API. For fingerprint-only cheminformatics use rdkit-cheminformatics; for featurization hub without training use molfeat-molecular-featurization."
+description: "Deep learning for drug discovery. 60+ models (GCN, GAT, AttentiveFP, MPNN, ChemBERTa, GROVER), 50+ featurizers, MoleculeNet benchmarks, HPO, transfer learning. Unified load-featurize-split-train-evaluate API. For fingerprints use rdkit-cheminformatics; for featurization-only use molfeat."
 license: MIT
 ---
 
diff --git a/skills/structural-biology-drug-discovery/diffdock/SKILL.md b/skills/structural-biology-drug-discovery/diffdock/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "diffdock"
-description: "DiffDock is a diffusion-based molecular docking tool that predicts protein-ligand binding poses without requiring a predefined binding site. Use it when the binding site is unknown, when traditional docking fails, or when exploring multiple binding modes. Pipeline: prepare protein (PDB) and ligand (SMILES/SDF) inputs → run DiffDock inference → analyze confidence-ranked poses → visualize in PyMOL or NGLview."
+description: "Diffusion-based docking that predicts protein-ligand poses without a predefined site. Use for blind docking, when traditional docking fails, or exploring multiple binding modes. Pipeline: prep protein (PDB) and ligand (SMILES/SDF), run inference, analyze confidence-ranked poses."
 license: "MIT"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/drugbank-database-access/SKILL.md b/skills/structural-biology-drug-discovery/drugbank-database-access/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "drugbank-database-access"
-description: "Parse and query DrugBank local XML database for drug information, interactions, targets, and chemical properties. Search drugs by ID/name/CAS, extract drug-drug interactions with severity, map targets/enzymes/transporters, compute molecular similarity from SMILES. Primary access via local XML (downloaded); REST API available but rate-limited (3,000/month dev tier). For live bioactivity queries use chembl-database-bioactivity; for compound property lookups use pubchem-compound-search."
+description: "Parse local DrugBank XML for drug info, interactions, targets, and properties. Search by ID/name/CAS, extract DDIs with severity, map targets/enzymes/transporters, compute SMILES similarity. Primary via local XML; REST API rate-limited (3k/month dev). For live bioactivity use chembl-database-bioactivity; for compound properties use pubchem-compound-search."
 license: "Unknown"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/emdb-database/SKILL.md b/skills/structural-biology-drug-discovery/emdb-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "emdb-database"
-description: "Search and retrieve cryo-EM density maps, fitted atomic models, and metadata from the Electron Microscopy Data Bank (EMDB) REST API. Query by keyword, resolution, method, or organism; fetch entry details, map download URLs, associated PDB models, and publications. No authentication required. For experimental atomic coordinates use pdb-database; for AlphaFold predicted structures use alphafold-database-access."
+description: "Search EMDB cryo-EM density maps, fitted atomic models, and metadata via REST API. Query by keyword, resolution, method, or organism; fetch entries, map URLs, linked PDB models, and publications. No auth. For atomic coordinates use pdb-database; for AlphaFold predictions use alphafold-database-access."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/fda-database/SKILL.md b/skills/structural-biology-drug-discovery/fda-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "fda-database"
-description: "Query openFDA REST API for drug adverse event reports (FAERS), drug labeling, product information, recalls, and enforcement actions. Search by drug name, active ingredient, adverse event term (MedDRA), or NDC code. No API key needed for 1000 req/day; free key for 120,000 req/day. For clinical trial data use clinicaltrials-database-search; for drug structures use drugbank-database-access or chembl-database-bioactivity."
+description: "Query openFDA REST API for adverse events (FAERS), labeling, product info, recalls, enforcement. Search by drug name, ingredient, MedDRA, or NDC. 1k req/day no key; 120k with free key. For trials use clinicaltrials-database-search; for structures use drugbank-database-access or chembl-database-bioactivity."
 license: "CC0-1.0"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/gtopdb-database/SKILL.md b/skills/structural-biology-drug-discovery/gtopdb-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "gtopdb-database"
-description: "Query the IUPHAR/BPS Guide to Pharmacology (GtoPdb) REST API for receptor-ligand interaction data, target pharmacology, and quantitative affinity metrics. Retrieve pKi/pIC50/pEC50 values, ligand classifications (approved drugs, biologics, natural products), target families (GPCRs, ion channels, nuclear receptors, kinases), and selectivity profiles across the pharmacological target space."
+description: "Query IUPHAR/BPS Guide to Pharmacology (GtoPdb) REST API for receptor-ligand interactions and affinity (pKi/pIC50/pEC50). Get ligand classes (drugs, biologics, natural products), target families (GPCRs, ion channels, nuclear receptors, kinases), selectivity profiles."
 license: "ODbL-1.0"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/mdanalysis-trajectory/SKILL.md b/skills/structural-biology-drug-discovery/mdanalysis-trajectory/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "mdanalysis-trajectory"
-description: "Python library for analyzing molecular dynamics (MD) trajectories from GROMACS, AMBER, NAMD, CHARMM, and LAMMPS. Reads topology and trajectory files into Universe objects; supports RMSD, RMSF, radius of gyration, contact maps, hydrogen bond analysis, PCA, and custom distance/angle calculations across millions of frames. Use for structural analysis after MD simulations; use OpenMM or GROMACS directly for running simulations."
+description: "Analyze MD trajectories from GROMACS, AMBER, NAMD, CHARMM, LAMMPS. Reads topology/trajectory into Universe objects; supports RMSD, RMSF, radius of gyration, contact maps, H-bonds, PCA, and custom distance/angle calculations. Use for post-simulation structural analysis; use OpenMM/GROMACS for running simulations."
 license: "GPL-2.0"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/medchem/SKILL.md b/skills/structural-biology-drug-discovery/medchem/SKILL.md
@@ -1,13 +1,11 @@
 ---
 name: medchem
 description: >-
-  Medicinal chemistry filters for drug discovery compound triage. Drug-likeness rules
-  (Lipinski Ro5, Veber, Oprea, CNS, leadlike, REOS, Golden Triangle, Rule of Three),
-  structural alerts (PAINS, NIBR, Lilly Demerits, Common Alerts), chemical group detection
-  (hinge binders, Michael acceptors), molecular complexity metrics, property constraints,
-  and a query language for composing filter logic. Built on RDKit and datamol. Use for
-  hit-to-lead filtering, library design, and ADMET pre-screening. For molecular I/O and
-  descriptors use rdkit-cheminformatics or datamol-cheminformatics instead.
+  Medicinal chemistry filters for compound triage. Drug-likeness rules (Lipinski Ro5,
+  Veber, Oprea, CNS, leadlike, REOS, Golden Triangle, Ro3), structural alerts (PAINS,
+  NIBR, Lilly Demerits), chemical group detectors, complexity metrics, and filter
+  composition query language. Built on RDKit/datamol. For hit-to-lead filtering, library
+  design, ADMET pre-screening. For molecular I/O use rdkit-cheminformatics or datamol.
 license: Apache-2.0
 ---
 
diff --git a/skills/structural-biology-drug-discovery/molfeat-molecular-featurization/SKILL.md b/skills/structural-biology-drug-discovery/molfeat-molecular-featurization/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: molfeat-molecular-featurization
-description: Molecular featurization hub (100+ featurizers) for ML. Convert SMILES to numerical representations via fingerprints (ECFP, MACCS, MAP4), descriptors (RDKit 2D, Mordred), pretrained models (ChemBERTa, GIN, Graphormer), and pharmacophore features. Scikit-learn compatible transformers with parallelization, caching, and state persistence. For QSAR, virtual screening, similarity search, and deep learning on molecules.
+description: Molecular featurization hub (100+ featurizers) for ML. SMILES to fingerprints (ECFP, MACCS, MAP4), descriptors (RDKit 2D, Mordred), pretrained embeddings (ChemBERTa, GIN, Graphormer), pharmacophores. Scikit-learn compatible with parallelization/caching. For QSAR, virtual screening, similarity, and molecular DL.
 license: Apache-2.0
 ---
 
diff --git a/skills/structural-biology-drug-discovery/opentargets-database/SKILL.md b/skills/structural-biology-drug-discovery/opentargets-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "opentargets-database"
-description: "Query Open Targets Platform GraphQL API for target-disease associations, evidence scores, drug-target links, and safety data. Search targets by gene symbol, diseases by EFO ID, retrieve evidence scores from 20+ data sources, drug mechanisms, and tractability assessments. For ChEMBL bioactivity use chembl-database-bioactivity; for clinical trials use clinicaltrials-database-search."
+description: "Query Open Targets GraphQL API for target-disease associations, evidence, drug links, safety. Search targets by gene, diseases by EFO ID; scores from 20+ sources, drug mechanisms, tractability. For ChEMBL use chembl-database-bioactivity; for trials use clinicaltrials-database-search."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/pdb-database/SKILL.md b/skills/structural-biology-drug-discovery/pdb-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pdb-database"
-description: "Query RCSB PDB (200K+ experimental structures) via rcsb-api Python SDK. Text, attribute, sequence, and structure similarity search. Fetch metadata via Schema or GraphQL. Download PDB/mmCIF coordinate files. For AlphaFold predicted structures use alphafold-database-access."
+description: "Query RCSB PDB (200K+ structures) via rcsb-api SDK. Text/attribute/sequence/3D similarity search; metadata via GraphQL; download PDB/mmCIF. For AlphaFold predictions use alphafold-database-access."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/pubchem-compound-search/SKILL.md b/skills/structural-biology-drug-discovery/pubchem-compound-search/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "pubchem-compound-search"
-description: "Query PubChem database (110M+ compounds) via PubChemPy and PUG-REST API. Search compounds by name/CID/SMILES, retrieve molecular properties (MW, LogP, TPSA), perform similarity and substructure searches, access bioactivity data. For local cheminformatics computation use rdkit; for multi-database queries use bioservices."
+description: "Query PubChem (110M+ compounds) via PubChemPy/PUG-REST. Search by name/CID/SMILES, get properties (MW, LogP, TPSA), similarity/substructure search, bioactivity. For local cheminformatics use rdkit; for multi-DB queries use bioservices."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/pytdc-therapeutics-data-commons/SKILL.md b/skills/structural-biology-drug-discovery/pytdc-therapeutics-data-commons/SKILL.md
@@ -1,12 +1,10 @@
 ---
 name: pytdc-therapeutics-data-commons
 description: >
-  Therapeutics Data Commons (TDC) — AI-ready drug discovery dataset platform.
-  Access curated ADME, toxicity, DTI, DDI datasets with scaffold/cold splits,
-  standardized evaluation metrics, molecular oracles for optimization, and
-  ADMET benchmark groups. Use for therapeutic ML model training, benchmarking,
-  and molecular property prediction. For chemical database queries use
-  chembl-database-bioactivity; for molecular featurization use molfeat.
+  Therapeutics Data Commons (TDC) AI-ready drug discovery datasets. Curated ADME,
+  toxicity, DTI, DDI with scaffold/cold splits, standardized metrics, molecular oracles,
+  and ADMET benchmarks for therapeutic ML and property prediction. For chemical database
+  queries use chembl-database-bioactivity; for featurization use molfeat.
 license: MIT
 ---
 
diff --git a/skills/structural-biology-drug-discovery/rdkit-cheminformatics/SKILL.md b/skills/structural-biology-drug-discovery/rdkit-cheminformatics/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "rdkit-cheminformatics"
-description: "Cheminformatics toolkit for molecular analysis and virtual screening. Use for SMILES/SDF parsing, molecular descriptor calculation (MW, LogP, TPSA), fingerprint generation (Morgan/ECFP, MACCS, RDKit), Tanimoto similarity search, substructure filtering with SMARTS, drug-likeness assessment (Lipinski Ro5), chemical reaction enumeration, 2D/3D coordinate generation, and compound library profiling. For simpler high-level API, use datamol. Use RDKit when you need fine-grained control over sanitization, custom fingerprints, SMARTS queries, or reaction SMARTS."
+description: "Cheminformatics toolkit for molecular analysis and virtual screening: SMILES/SDF parsing, descriptors (MW, LogP, TPSA), fingerprints (Morgan/ECFP, MACCS), Tanimoto similarity, SMARTS substructure filtering, Lipinski drug-likeness, reaction enumeration, 2D/3D coordinates. For simpler API use datamol; use RDKit for fine-grained sanitization, custom fingerprints, or SMARTS/reaction control."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/rowan/SKILL.md b/skills/structural-biology-drug-discovery/rowan/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "rowan"
-description: "Rowan is a cloud-based computational chemistry platform providing quantum chemistry calculations via a Python SDK. Use it to run geometry optimization, conformer generation, torsional scans, and energy minimization with DFT or semiempirical methods, and retrieve molecular properties (dipole moment, partial charges, frontier orbital energies) — without managing local quantum chemistry software or HPC clusters."
+description: "Cloud quantum chemistry platform with Python SDK. Run geometry optimization, conformer generation, torsional scans, and energy minimization (DFT/semiempirical), and retrieve properties (dipole, partial charges, frontier orbitals) — no local QC software or HPC needed."
 license: "Proprietary"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/sar-analysis/SKILL.md b/skills/structural-biology-drug-discovery/sar-analysis/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: sar-analysis
-description: "Guide for performing Structure-Activity Relationship (SAR) analysis using RDKit. Covers core scaffold identification via Maximum Common Substructure (MCS), R-group decomposition, molecular alignment for visualization, activity heatmap generation, and interpretive SAR text output. For general cheminformatics operations, see rdkit-cheminformatics. For bioactivity data retrieval, see chembl-database-bioactivity."
+description: "Structure-Activity Relationship (SAR) analysis with RDKit: scaffold detection via MCS, R-group decomposition, aligned visualization, activity heatmaps, interpretive SAR output. For general cheminformatics see rdkit-cheminformatics; for bioactivity see chembl-database-bioactivity."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/structural-biology-drug-discovery/torchdrug/SKILL.md b/skills/structural-biology-drug-discovery/torchdrug/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "torchdrug"
-description: "TorchDrug is a PyTorch-based machine learning platform for drug discovery. Use it for graph-based molecular representation learning, molecular property prediction (ADMET, activity), retrosynthesis prediction, drug-target interaction (DTI) modeling, and pretraining on large molecular datasets. Provides GNN layers (GraphConv, GAT, MPNN), pretrained models, and benchmark datasets in a unified PyTorch-compatible API."
+description: "PyTorch-based ML platform for drug discovery: graph molecular representation learning, property prediction (ADMET, activity), retrosynthesis, drug-target interaction (DTI), and pretraining on large molecular datasets. Provides GNN layers (GraphConv, GAT, MPNN), pretrained models, and benchmark datasets."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/unichem-database/SKILL.md b/skills/structural-biology-drug-discovery/unichem-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "unichem-database"
-description: "Cross-reference chemical compound identifiers across 50+ databases (ChEMBL, DrugBank, PubChem, ChEBI, PDB, KEGG) using the UniChem REST API. Resolve InChIKeys to database-specific IDs, find all sources for a compound, discover related compounds by structural connectivity, and batch-translate compound lists between naming systems. No authentication required."
+description: "Cross-reference compound IDs across 50+ databases (ChEMBL, DrugBank, PubChem, ChEBI, PDB, KEGG) via UniChem REST API. Resolve InChIKeys to source IDs, find structurally related compounds by connectivity, batch-translate between naming systems. No auth required."
 license: "Apache-2.0"
 ---
 
diff --git a/skills/structural-biology-drug-discovery/zinc-database/SKILL.md b/skills/structural-biology-drug-discovery/zinc-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "zinc-database"
-description: "Query ZINC15/ZINC22 virtual compound libraries for drug discovery. Search purchasable lead-like, fragment-like, and drug-like compounds by molecular weight, logP, reactivity class, or SMILES similarity. Download 3D compound sets for docking, retrieve SMILES for in-silico screening. ZINC20 contains 1.4B compounds; purchasable subset is 750M. For bioactivity data use chembl-database-bioactivity; for approved drugs use drugbank-database-access."
+description: "Query ZINC15/ZINC22 virtual compound libraries (1.4B compounds, 750M purchasable). Search lead/fragment/drug-like compounds by MW, logP, reactivity, or SMILES similarity; download 3D sets for docking. For bioactivity use chembl-database-bioactivity; for approved drugs use drugbank-database-access."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/systems-biology-multiomics/brenda-database/SKILL.md b/skills/systems-biology-multiomics/brenda-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "brenda-database"
-description: "Query BRENDA Enzyme Database for kinetic parameters (Km, Vmax, kcat, Ki), enzyme classifications, substrate specificity, inhibitors, cofactors, and organism-specific enzyme data via SOAP/REST API. 80,000+ enzyme entries, 7M+ kinetic values. Requires free academic registration. For metabolic pathway modeling use cobrapy-metabolic-modeling; for metabolite structures use hmdb-database."
+description: "BRENDA Enzyme DB SOAP/REST queries: kinetic parameters (Km, Vmax, kcat, Ki), EC classes, substrate specificity, inhibitors, cofactors, organism data. 80K+ enzymes, 7M+ values. Free academic registration. For metabolic modeling use cobrapy-metabolic-modeling; metabolites use hmdb-database."
 license: "CC-BY-4.0"
 ---
 
diff --git a/skills/systems-biology-multiomics/cellchat-cell-communication/SKILL.md b/skills/systems-biology-multiomics/cellchat-cell-communication/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "cellchat-cell-communication"
-description: "Infer, analyze, and visualize intercellular communication from scRNA-seq data using CellChat (R). Pipeline: create CellChat object from Seurat or count matrix → subset CellChatDB ligand-receptor database → identify over-expressed genes per cell group → infer communication probabilities → compute pathway-level signaling → analyze network centrality (senders, receivers, influencers) → visualize with chord diagrams, heatmaps, and bubble plots → compare across conditions. Human and mouse supported. Use liana for a pure-Python equivalent."
+description: "Infer and visualize intercellular communication from scRNA-seq with CellChat (R). Build CellChat from Seurat/counts → subset CellChatDB ligand-receptor pairs → over-expressed genes per group → communication probabilities → pathway signaling → network centrality (senders/receivers/influencers) → chord/heatmap/bubble plots → cross-condition compare. Human, mouse. Use liana for pure-Python."
 license: "MIT"
 ---
 
diff --git a/skills/systems-biology-multiomics/cobrapy-metabolic-modeling/SKILL.md b/skills/systems-biology-multiomics/cobrapy-metabolic-modeling/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: cobrapy-metabolic-modeling
-description: "Constraint-based reconstruction and analysis (COBRA) of genome-scale metabolic models. FBA, FVA, gene/reaction knockouts, flux sampling, production envelopes, gapfilling, and media optimization. Use for metabolic engineering strain design, essential gene identification, and flux distribution analysis. For kinetic modeling use tellurium; for pathway visualization use Escher."
+description: "Constraint-based (COBRA) analysis of genome-scale metabolic models: FBA, FVA, knockouts, flux sampling, production envelopes, gapfilling, media optimization. Use for strain design, essential gene ID, flux analysis. For kinetic modeling use tellurium; for visualization use Escher."
 license: GPL-2.0
 ---
 
diff --git a/skills/systems-biology-multiomics/kegg-pathway-analysis/SKILL.md b/skills/systems-biology-multiomics/kegg-pathway-analysis/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: kegg-pathway-analysis
-description: "Guide to KEGG pathway enrichment analysis for differential expression results. Covers over-representation analysis (ORA) vs gene set enrichment analysis (GSEA), mandatory directionality splitting, KEGG organism codes, API failure handling with offline fallbacks, cross-condition pathway comparisons, and answer-first reporting. Consult this when running pathway enrichment with clusterProfiler or gseapy on DEG results."
+description: "Guide to KEGG pathway enrichment for DEG results. Covers ORA vs GSEA, mandatory directionality splitting, KEGG organism codes, API failure handling with offline fallbacks, cross-condition comparisons, and answer-first reporting. Consult when running enrichment with clusterProfiler or gseapy."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/systems-biology-multiomics/lamindb-data-management/SKILL.md b/skills/systems-biology-multiomics/lamindb-data-management/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: lamindb-data-management
-description: "Open-source data framework for biology: queryable, traceable, FAIR data management. Version artifacts (AnnData, DataFrame, Zarr), track computational lineage, validate with biological ontologies (Bionty), query across datasets. Integrates with Nextflow, Snakemake, W&B, scVI-tools. For single-cell analysis use scanpy; for ontology-only lookups use bionty directly."
+description: "Open-source FAIR biology data framework. Version artifacts (AnnData, DataFrame, Zarr), track lineage, validate via ontologies (Bionty), query datasets. Integrates with Nextflow, Snakemake, W&B, scVI. For scRNA-seq use scanpy; for ontology lookups use bionty."
 license: Apache-2.0
 ---
 
diff --git a/skills/systems-biology-multiomics/libsbml-network-modeling/SKILL.md b/skills/systems-biology-multiomics/libsbml-network-modeling/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "libsbml-network-modeling"
-description: "Build, read, validate, and modify SBML biological network models using libSBML Python API. Supports all SBML Levels (1–3), reactions with kinetic laws, species/compartments, rules (assignment/rate/algebraic), the FBC extension for flux balance analysis models, and model conversion utilities. Integrates with COBRApy, Tellurium/RoadRunner, and COPASI for simulation. Use when programmatically constructing ODE-based or constraint-based metabolic/signaling models in the standard SBML format."
+description: "Build, read, validate, modify SBML biological network models via the libSBML Python API. SBML Levels 1–3, reactions/kinetic laws, species, rules, FBC extension for flux balance, conversion. Interoperates with COBRApy, Tellurium/RoadRunner, COPASI. Use when programmatically constructing ODE or constraint-based metabolic/signaling models in SBML."
 license: "LGPL-2.1"
 ---
 
diff --git a/skills/systems-biology-multiomics/mofaplus-multi-omics/SKILL.md b/skills/systems-biology-multiomics/mofaplus-multi-omics/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "mofaplus-multi-omics"
-description: "Multi-Omics Factor Analysis v2 (MOFA+) with mofapy2. Jointly decompose multiple omics layers (scRNA-seq, ATAC-seq, proteomics, methylation) into latent factors that capture major sources of biological variation. Supports multi-group designs (patients, conditions). Pipeline: prepare AnnData views → create MOFA object → train → inspect variance explained → correlate factors with metadata → visualize and cluster → enrichment of top loadings."
+description: "Multi-Omics Factor Analysis v2 (MOFA+) with mofapy2. Jointly decompose omics layers (scRNA, ATAC, proteomics, methylation) into latent factors capturing major variation. Multi-group designs. AnnData views → MOFA object → train → variance explained → correlate factors with metadata → visualize/cluster → enrich top loadings."
 license: "LGPL-3.0"
 ---
 
diff --git a/skills/systems-biology-multiomics/muon-multiomics-singlecell/SKILL.md b/skills/systems-biology-multiomics/muon-multiomics-singlecell/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: "muon-multiomics-singlecell"
-description: "Multi-modal single-cell analysis with muon and MuData. Joint RNA+ATAC (10x Multiome), CITE-seq (RNA+protein), and other multi-omics combinations. MuData container holds modality-specific AnnData objects with shared obs. Weighted Nearest Neighbor (WNN) graph for joint embedding, per-modality preprocessing, cross-modal factor analysis with MOFA. Use scanpy-scrna-seq for single-modality RNA analysis; use muon when combining two or more omics modalities from the same cells."
+description: "Multi-modal single-cell analysis with muon/MuData. Joint RNA+ATAC (10x Multiome), CITE-seq (RNA+protein), other multi-omics. MuData holds per-modality AnnData with shared obs. WNN joint embedding, per-modality preprocessing, MOFA factor analysis. Use scanpy-scrna-seq for single-modality RNA; use muon when combining 2+ omics from the same cells."
 license: "BSD-3-Clause"
 ---
 
diff --git a/skills/systems-biology-multiomics/omics-analysis-guide/SKILL.md b/skills/systems-biology-multiomics/omics-analysis-guide/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: omics-analysis-guide
-description: "Comprehensive decision guide for analyzing omics data (transcriptomics, proteomics) using a three-tiered approach: validated pipelines first, standard workflows second, custom analysis last. Covers quality control strategies, normalization method selection, missing value imputation, statistical test selection based on data properties, and result visualization. Consult this guide when planning a bulk RNA-seq or proteomics differential analysis to choose the right tools, tests, and preprocessing steps."
+description: "Decision guide for omics analysis (transcriptomics, proteomics) using a three-tiered approach: validated pipelines first, standard workflows second, custom last. Covers QC, normalization choice, missing value imputation, statistical test selection by data properties, and visualization. Consult when planning bulk RNA-seq or proteomics differential analysis."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/systems-biology-multiomics/reactome-database/SKILL.md b/skills/systems-biology-multiomics/reactome-database/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: reactome-database
-description: "Query Reactome pathway database via REST API. Pathway queries, entity retrieval, keyword search, gene list enrichment analysis, pathway hierarchy, cross-references. Content Service (pathway data) and Analysis Service (enrichment). For Python wrapper use reactome2py. For KEGG pathways use kegg-database; for protein interactions use string-database-ppi."
+description: "Query Reactome pathways via REST: pathway queries, entity lookup, keyword search, gene list enrichment, hierarchy, cross-refs. Content + Analysis services. Python wrapper: reactome2py. For KEGG use kegg-database; for PPIs use string-database-ppi."
 license: CC-BY-4.0
 ---
 
diff --git a/skills/systems-biology-multiomics/string-database-ppi/SKILL.md b/skills/systems-biology-multiomics/string-database-ppi/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: string-database-ppi
-description: Query STRING REST API for protein-protein interactions (59M proteins, 20B interactions, 5000+ species). Retrieve interaction networks, perform GO/KEGG enrichment analysis, discover interaction partners, test PPI enrichment significance, generate network visualizations, and analyze protein homology for systems biology and pathway analysis.
+description: Query STRING REST API for PPIs (59M proteins, 20B interactions, 5000+ species). Retrieve networks, run GO/KEGG enrichment, find partners, test PPI significance, visualize networks, analyze homology. For chemical interactions use chembl-database-bioactivity; pathways use kegg-database.
 license: CC-BY-4.0
 ---
 
PATCH

echo "Gold patch applied."
