"""Behavioral checks for sciagent-skills-refactor-shorten-skillmd-descriptions-285 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sciagent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/clinical-decision-support-documents/SKILL.md')
    assert 'description: "Guidelines for clinical decision support (CDS) documents: biomarker-stratified cohort analyses and GRADE-graded treatment reports. Covers structure, executive summaries, evidence grading' in text, "expected to find: " + 'description: "Guidelines for clinical decision support (CDS) documents: biomarker-stratified cohort analyses and GRADE-graded treatment reports. Covers structure, executive summaries, evidence grading'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/degenerate-input-filtering/SKILL.md')
    assert 'description: "Filter degenerate, uninformative inputs before statistical tests: single-sequence alignments, empty files, constant features, zero-variance inputs, all-NaN columns. See nan-safe-correlat' in text, "expected to find: " + 'description: "Filter degenerate, uninformative inputs before statistical tests: single-sequence alignments, empty files, constant features, zero-variance inputs, all-NaN columns. See nan-safe-correlat'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/hypothesis-generation/SKILL.md')
    assert 'description: "Structured hypothesis formulation: turn observations into testable hypotheses with predictions, propose mechanisms, design experiments. Follows the scientific method. Use scientific-brai' in text, "expected to find: " + 'description: "Structured hypothesis formulation: turn observations into testable hypotheses with predictions, propose mechanisms, design experiments. Follows the scientific method. Use scientific-brai'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/matplotlib-scientific-plotting/SKILL.md')
    assert 'description: "Low-level Python plotting for scientific figures: publication-quality line, scatter, bar, heatmap, contour, 3D; multi-panel layouts; fine control of every element. PNG/PDF/SVG export. Us' in text, "expected to find: " + 'description: "Low-level Python plotting for scientific figures: publication-quality line, scatter, bar, heatmap, contour, 3D; multi-panel layouts; fine control of every element. PNG/PDF/SVG export. Us'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/nan-safe-correlation/SKILL.md')
    assert 'description: "Per-feature NaN-safe Spearman/Pearson correlation across many features (genes, proteins, variants) with missing values. Covers why bulk matrix shortcuts fail, correct pairwise deletion, ' in text, "expected to find: " + 'description: "Per-feature NaN-safe Spearman/Pearson correlation across many features (genes, proteins, variants) with missing values. Covers why bulk matrix shortcuts fail, correct pairwise deletion, '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/pyhealth/SKILL.md')
    assert 'description: "Python library for healthcare ML on EHR data: process MIMIC-III/IV, eICU, OMOP-CDM; encode medical codes (ICD, ATC, NDC); build patient-level datasets; train Transformer, RETAIN, GRASP, ' in text, "expected to find: " + 'description: "Python library for healthcare ML on EHR data: process MIMIC-III/IV, eICU, OMOP-CDM; encode medical codes (ICD, ATC, NDC); build patient-level datasets; train Transformer, RETAIN, GRASP, '[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/pymc-bayesian-modeling/SKILL.md')
    assert 'description: "Bayesian modeling with PyMC 5: priors, likelihood, NUTS/ADVI sampling, diagnostics (R-hat, ESS), LOO/WAIC comparison, prediction. Hierarchical, logistic, GP variants; predictive checks."' in text, "expected to find: " + 'description: "Bayesian modeling with PyMC 5: priors, likelihood, NUTS/ADVI sampling, diagnostics (R-hat, ESS), LOO/WAIC comparison, prediction. Hierarchical, logistic, GP variants; predictive checks."'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/scikit-learn-machine-learning/SKILL.md')
    assert 'description: "Classical ML in Python: classification, regression, clustering, dim reduction, evaluation, tuning, preprocessing pipelines. Linear models, tree ensembles, SVMs, K-Means, PCA, t-SNE. Use ' in text, "expected to find: " + 'description: "Classical ML in Python: classification, regression, clustering, dim reduction, evaluation, tuning, preprocessing pipelines. Linear models, tree ensembles, SVMs, K-Means, PCA, t-SNE. Use '[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/scikit-survival-analysis/SKILL.md')
    assert 'description: "Time-to-event modeling with scikit-survival: Cox PH (elastic net), Random Survival Forests, Boosting, SVMs for censored data. C-index, Brier, time-dependent AUC; Kaplan-Meier, Nelson-Aal' in text, "expected to find: " + 'description: "Time-to-event modeling with scikit-survival: Cox PH (elastic net), Random Survival Forests, Boosting, SVMs for censored data. C-index, Brier, time-dependent AUC; Kaplan-Meier, Nelson-Aal'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/shap-model-explainability/SKILL.md')
    assert 'Model interpretability via SHAP (Shapley values from game theory).' in text, "expected to find: " + 'Model interpretability via SHAP (Shapley values from game theory).'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/shap-model-explainability/SKILL.md')
    assert 'Permutation), feature attribution, and plots (waterfall, beeswarm,' in text, "expected to find: " + 'Permutation), feature attribution, and plots (waterfall, beeswarm,'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/shap-model-explainability/SKILL.md')
    assert 'bar, scatter, force, heatmap). Use to explain ML predictions, rank' in text, "expected to find: " + 'bar, scatter, force, heatmap). Use to explain ML predictions, rank'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/statistical-analysis/SKILL.md')
    assert 'Guided statistical analysis: test choice, assumption checks, effect' in text, "expected to find: " + 'Guided statistical analysis: test choice, assumption checks, effect'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/statistical-analysis/SKILL.md')
    assert 'format results for publication. Covers frequentist (t-test, ANOVA,' in text, "expected to find: " + 'format results for publication. Covers frequentist (t-test, ANOVA,'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/statistical-analysis/SKILL.md')
    assert 'chi-square, regression, correlation, survival, count, reliability)' in text, "expected to find: " + 'chi-square, regression, correlation, survival, count, reliability)'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/biostatistics/statsmodels-statistical-modeling/SKILL.md')
    assert 'description: "Python statistical modeling: regression (OLS, WLS, GLM), discrete (Logit, Poisson, NegBin), time series (ARIMA, SARIMAX, VAR), with rigorous inference, diagnostics, and hypothesis tests.' in text, "expected to find: " + 'description: "Python statistical modeling: regression (OLS, WLS, GLM), discrete (Logit, Poisson, NegBin), time series (ARIMA, SARIMAX, VAR), with rigorous inference, diagnostics, and hypothesis tests.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/cellpose-cell-segmentation/SKILL.md')
    assert 'description: "DL cell/nucleus segmentation for fluorescence and brightfield microscopy. Pre-trained models (cyto3, nuclei, tissuenet) and a generalist flow-based algorithm segment cells without retrai' in text, "expected to find: " + 'description: "DL cell/nucleus segmentation for fluorescence and brightfield microscopy. Pre-trained models (cyto3, nuclei, tissuenet) and a generalist flow-based algorithm segment cells without retrai'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/flowio-flow-cytometry/SKILL.md')
    assert 'description: "Parse/write FCS (Flow Cytometry) files v2.0-3.1. Events as NumPy, channel metadata, multi-dataset files, CSV/FCS export. Use FlowKit for gating/compensation."' in text, "expected to find: " + 'description: "Parse/write FCS (Flow Cytometry) files v2.0-3.1. Events as NumPy, channel metadata, multi-dataset files, CSV/FCS export. Use FlowKit for gating/compensation."'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/histolab-wsi-processing/SKILL.md')
    assert 'description: "WSI processing for digital pathology. Tissue detection, tile extraction (random, grid, score-based), filter pipelines for H&E/IHC. For dataset prep, tile-based DL, slide QC. Use pathml f' in text, "expected to find: " + 'description: "WSI processing for digital pathology. Tissue detection, tile extraction (random, grid, score-based), filter pipelines for H&E/IHC. For dataset prep, tile-based DL, slide QC. Use pathml f'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/imaging-data-commons/SKILL.md')
    assert 'description: "Query NCI Imaging Data Commons (IDC) for cancer radiology and pathology datasets on Google Cloud. Search DICOM by modality, anatomical site, or cancer type; download via GCS or IDAT. 50T' in text, "expected to find: " + 'description: "Query NCI Imaging Data Commons (IDC) for cancer radiology and pathology datasets on Google Cloud. Search DICOM by modality, anatomical site, or cancer type; download via GCS or IDAT. 50T'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/napari-image-viewer/SKILL.md')
    assert 'description: "Interactive viewer for microscopy. Displays 2D/3D/4D arrays as Image, Labels, Points, Shapes, Tracks layers; supports annotation, plugin analysis, headless screenshots. Core visualizatio' in text, "expected to find: " + 'description: "Interactive viewer for microscopy. Displays 2D/3D/4D arrays as Image, Labels, Points, Shapes, Tracks layers; supports annotation, plugin analysis, headless screenshots. Core visualizatio'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/nnunet-segmentation/SKILL.md')
    assert 'description: "Medical image segmentation with nnU-Net\'s self-configuring framework — auto-selects architecture, preprocessing, training for any modality. CT, MRI, microscopy, ultrasound in 2D, 3D full' in text, "expected to find: " + 'description: "Medical image segmentation with nnU-Net\'s self-configuring framework — auto-selects architecture, preprocessing, training for any modality. CT, MRI, microscopy, ultrasound in 2D, 3D full'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/omero-integration/SKILL.md')
    assert 'description: "Open-source bio-image data management. Use the omero-py client to connect to an OMERO server, retrieve images as numpy arrays, annotate with tags and key-value pairs, manage ROIs, and fe' in text, "expected to find: " + 'description: "Open-source bio-image data management. Use the omero-py client to connect to an OMERO server, retrieve images as numpy arrays, annotate with tags and key-value pairs, manage ROIs, and fe'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/opencv-bioimage-analysis/SKILL.md')
    assert 'description: "Computer vision for bio-image preprocessing, feature detection, real-time microscopy. Color conversion, morphology, contour/blob detection, template matching, optical flow on fluorescenc' in text, "expected to find: " + 'description: "Computer vision for bio-image preprocessing, feature detection, real-time microscopy. Color conversion, morphology, contour/blob detection, template matching, optical flow on fluorescenc'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/pathml/SKILL.md')
    assert 'description: "Computational pathology toolkit for whole-slide images (WSIs): load slides, extract tiles, stain normalization, nuclear segmentation, feature extraction, and ML training. Supports H&E an' in text, "expected to find: " + 'description: "Computational pathology toolkit for whole-slide images (WSIs): load slides, extract tiles, stain normalization, nuclear segmentation, feature extraction, and ML training. Supports H&E an'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/pydicom-medical-imaging/SKILL.md')
    assert 'description: "Pure Python DICOM for medical imaging (CT, MRI, X-ray, ultrasound). Read/write DICOM, pixels as NumPy, edit tags, windowing (VOI LUT), PHI anonymization, build DICOM, series→3D volumes. ' in text, "expected to find: " + 'description: "Pure Python DICOM for medical imaging (CT, MRI, X-ray, ultrasound). Read/write DICOM, pixels as NumPy, edit tags, windowing (VOI LUT), PHI anonymization, build DICOM, series→3D volumes. '[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/pyimagej-fiji-bridge/SKILL.md')
    assert 'description: "Python bridge to ImageJ2/Fiji for macros, plugins (Bio-Formats, TrackMate, Analyze Particles), NumPy↔ImagePlus/ImgLib2 exchange, and ImageJ Ops. Automates Fiji headlessly from Python. Us' in text, "expected to find: " + 'description: "Python bridge to ImageJ2/Fiji for macros, plugins (Bio-Formats, TrackMate, Analyze Particles), NumPy↔ImagePlus/ImgLib2 exchange, and ImageJ Ops. Automates Fiji headlessly from Python. Us'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/scikit-image-processing/SKILL.md')
    assert 'description: "Python image processing for microscopy and bioimage analysis. Read/write images, filter (Gaussian, median, LoG), segment (thresholding, watershed, active contours), measure region proper' in text, "expected to find: " + 'description: "Python image processing for microscopy and bioimage analysis. Read/write images, filter (Gaussian, median, LoG), segment (thresholding, watershed, active contours), measure region proper'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/simpleitk-image-registration/SKILL.md')
    assert 'description: "Register, segment, filter, resample 3D medical images (MRI, CT, microscopy) via SimpleITK Python; DICOM, NIfTI, multi-modal. Rigid/affine/deformable registration, threshold/region-growin' in text, "expected to find: " + 'description: "Register, segment, filter, resample 3D medical images (MRI, CT, microscopy) via SimpleITK Python; DICOM, NIfTI, multi-modal. Rigid/affine/deformable registration, threshold/region-growin'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/single-cell-annotation/SKILL.md')
    assert 'description: "Guide to annotating cell types in scRNA-seq. Covers manual marker-based, automated (CellTypist, scAnnotate), and reference-based (scArches, Azimuth, SingleR) approaches with a decision f' in text, "expected to find: " + 'description: "Guide to annotating cell types in scRNA-seq. Covers manual marker-based, automated (CellTypist, scAnnotate), and reference-based (scArches, Azimuth, SingleR) approaches with a decision f'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cell-biology/trackpy-particle-tracking/SKILL.md')
    assert 'description: "Python library for single-particle tracking (SPT) in video microscopy via the Crocker-Grier algorithm. Locate particles (fluorescent spots, colloids, vesicles, cells) per frame, link int' in text, "expected to find: " + 'description: "Python library for single-particle tracking (SPT) in video microscopy via the Crocker-Grier algorithm. Locate particles (fluorescent spots, colloids, vesicles, cells) per frame, link int'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data-visualization/plotly-interactive-plots/SKILL.md')
    assert 'description: "Interactive scientific visualization with Plotly. Two APIs: plotly.express (px) for one-liner DataFrame plots, plotly.graph_objects (go) for trace-level control. 40+ chart types with hov' in text, "expected to find: " + 'description: "Interactive scientific visualization with Plotly. Two APIs: plotly.express (px) for one-liner DataFrame plots, plotly.graph_objects (go) for trace-level control. 40+ chart types with hov'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data-visualization/plotly-interactive-visualization/SKILL.md')
    assert 'description: "Interactive visualization with Plotly. 40+ chart types (scatter, line, heatmap, 3D, geographic) with hover, zoom, pan. Two APIs: Plotly Express (DataFrame) and Graph Objects (fine contro' in text, "expected to find: " + 'description: "Interactive visualization with Plotly. 40+ chart types (scatter, line, heatmap, 3D, geographic) with hover, zoom, pan. Two APIs: Plotly Express (DataFrame) and Graph Objects (fine contro'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data-visualization/scientific-visualization/SKILL.md')
    assert 'description: "Guide for choosing and creating scientific visualizations for publications and talks. Covers chart-type selection by data structure, color theory for accessibility/print, figure composit' in text, "expected to find: " + 'description: "Guide for choosing and creating scientific visualizations for publications and talks. Covers chart-type selection by data structure, color theory for accessibility/print, figure composit'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data-visualization/seaborn-statistical-plots/SKILL.md')
    assert 'description: "Statistical visualization on matplotlib with native pandas support. Auto aggregation, CIs, grouping for distributions (histplot, kdeplot), categorical (boxplot, violinplot), relational (' in text, "expected to find: " + 'description: "Statistical visualization on matplotlib with native pandas support. Auto aggregation, CIs, grouping for distributions (histplot, kdeplot), categorical (boxplot, violinplot), relational ('[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data-visualization/seaborn-statistical-visualization/SKILL.md')
    assert 'description: "Statistical visualization on matplotlib + pandas. Distributions (histplot, kdeplot, violin, box), relational (scatter, line), categorical, regression, correlation heatmaps. Auto aggregat' in text, "expected to find: " + 'description: "Statistical visualization on matplotlib + pandas. Distributions (histplot, kdeplot, violin, box), relational (scatter, line), categorical, regression, correlation heatmaps. Auto aggregat'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data-visualization/statistical-significance-annotation/SKILL.md')
    assert 'description: "Guide for annotating statistical significance (p-value asterisks) on comparison plots. Covers standard notation (ns, *, **, ***, ****), matplotlib bracket+asterisk implementation, and us' in text, "expected to find: " + 'description: "Guide for annotating statistical significance (p-value asterisks) on comparison plots. Covers standard notation (ns, *, **, ***, ****), matplotlib bracket+asterisk implementation, and us'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/anndata-data-structure/SKILL.md')
    assert 'description: "Annotated matrices for single-cell genomics. Stores X with obs/var metadata, layers, embeddings (obsm/varm), graphs (obsp/varp), uns. Use for .h5ad/.zarr I/O, concatenation, scverse inte' in text, "expected to find: " + 'description: "Annotated matrices for single-cell genomics. Stores X with obs/var metadata, layers, embeddings (obsm/varm), graphs (obsp/varp), uns. Use for .h5ad/.zarr I/O, concatenation, scverse inte'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/arboreto-grn-inference/SKILL.md')
    assert 'description: "GRN inference from expression via GRNBoost2 (gradient boosting) or GENIE3 (Random Forest). Load matrix, filter by TFs, infer TF-target-importance links, save network. Dask-parallelized t' in text, "expected to find: " + 'description: "GRN inference from expression via GRNBoost2 (gradient boosting) or GENIE3 (Random Forest). Load matrix, filter by TFs, infer TF-target-importance links, save network. Dask-parallelized t'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/archs4-database/SKILL.md')
    assert 'description: "Query ARCHS4 REST API for uniformly processed RNA-seq expression, tissue patterns, co-expression across 1M+ human/mouse samples. Retrieve z-scores, co-expressed genes, samples by metadat' in text, "expected to find: " + 'description: "Query ARCHS4 REST API for uniformly processed RNA-seq expression, tissue patterns, co-expression across 1M+ human/mouse samples. Retrieve z-scores, co-expressed genes, samples by metadat'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/bcftools-variant-manipulation/SKILL.md')
    assert 'description: "CLI for VCF/BCF: filter, merge, annotate, query, normalize, compute stats. Core post-variant-calling: quality filtering, multi-sample merging, rsID annotation, genotype extraction. Samto' in text, "expected to find: " + 'description: "CLI for VCF/BCF: filter, merge, annotate, query, normalize, compute stats. Core post-variant-calling: quality filtering, multi-sample merging, rsID annotation, genotype extraction. Samto'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/bedtools-genomic-intervals/SKILL.md')
    assert 'description: "Genomic interval ops on BED/BAM/GFF/VCF. Find overlaps, merge intervals, compute coverage, extract FASTA, find nearest features. Core for ChIP-seq peak annotation, region filtering, geno' in text, "expected to find: " + 'description: "Genomic interval ops on BED/BAM/GFF/VCF. Find overlaps, merge intervals, compute coverage, extract FASTA, find nearest features. Core for ChIP-seq peak annotation, region filtering, geno'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/biopython-molecular-biology/SKILL.md')
    assert 'description: "Molecular biology toolkit: sequence manipulation, FASTA/GenBank/PDB I/O, NCBI Entrez, BLAST automation, pairwise/MSA alignment, Bio.PDB, phylogenetic trees. Use for batch processing, cus' in text, "expected to find: " + 'description: "Molecular biology toolkit: sequence manipulation, FASTA/GenBank/PDB I/O, NCBI Entrez, BLAST automation, pairwise/MSA alignment, Bio.PDB, phylogenetic trees. Use for batch processing, cus'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/biopython-sequence-analysis/SKILL.md')
    assert 'description: "Biopython sequence analysis: parse FASTA/FASTQ/GenBank/GFF (SeqIO), NCBI Entrez (esearch/efetch/elink), remote/local BLAST, pairwise/MSA alignment (PairwiseAligner, MUSCLE/ClustalW), phy' in text, "expected to find: " + 'description: "Biopython sequence analysis: parse FASTA/FASTQ/GenBank/GFF (SeqIO), NCBI Entrez (esearch/efetch/elink), remote/local BLAST, pairwise/MSA alignment (PairwiseAligner, MUSCLE/ClustalW), phy'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/bioservices-multi-database/SKILL.md')
    assert 'pathways, ChEMBL/ChEBI/PubChem, BLAST, cross-database ID mapping, GO annotations, PPI.' in text, "expected to find: " + 'pathways, ChEMBL/ChEBI/PubChem, BLAST, cross-database ID mapping, GO annotations, PPI.'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/bioservices-multi-database/SKILL.md')
    assert 'Unified Python interface to 40+ bioinformatics web services: UniProt proteins, KEGG' in text, "expected to find: " + 'Unified Python interface to 40+ bioinformatics web services: UniProt proteins, KEGG'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/bioservices-multi-database/SKILL.md')
    assert 'For deep single-DB queries use dedicated tools (gget for Ensembl, pubchempy for' in text, "expected to find: " + 'For deep single-DB queries use dedicated tools (gget for Ensembl, pubchempy for'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/busco-status-interpretation/SKILL.md')
    assert 'description: "Guide to interpreting BUSCO completeness statuses: why Duplicated BUSCOs count as complete, parsing output files, computing/comparing completeness across proteomes/genomes, common counti' in text, "expected to find: " + 'description: "Guide to interpreting BUSCO completeness statuses: why Duplicated BUSCOs count as complete, parsing output files, computing/comparing completeness across proteomes/genomes, common counti'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/bwa-mem2-dna-aligner/SKILL.md')
    assert 'description: "Fast short-read DNA aligner for WGS/WES/ChIP-seq. 2× faster BWA-MEM successor; outputs SAM/BAM with read group headers for GATK. Primary plus supplementary records for chimeric reads. Us' in text, "expected to find: " + 'description: "Fast short-read DNA aligner for WGS/WES/ChIP-seq. 2× faster BWA-MEM successor; outputs SAM/BAM with read group headers for GATK. Primary plus supplementary records for chimeric reads. Us'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/cbioportal-database/SKILL.md')
    assert 'description: "Cancer genomics (TCGA et al.) via cBioPortal REST API. Retrieve somatic mutations, CNAs, expression, clinical data (survival/stage/treatment) across thousands of studies. Use for TMB, on' in text, "expected to find: " + 'description: "Cancer genomics (TCGA et al.) via cBioPortal REST API. Retrieve somatic mutations, CNAs, expression, clinical data (survival/stage/treatment) across thousands of studies. Use for TMB, on'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/celltypist-cell-annotation/SKILL.md')
    assert 'description: "Automated scRNA-seq cell type annotation via pre-trained logistic regression. 45+ models: immune, gut, lung, brain, fetal, cancer microenvironments. Input normalized AnnData; outputs per' in text, "expected to find: " + 'description: "Automated scRNA-seq cell type annotation via pre-trained logistic regression. 45+ models: immune, gut, lung, brain, fetal, cancer microenvironments. Input normalized AnnData; outputs per'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/cellxgene-census/SKILL.md')
    assert 'description: "Query CELLxGENE Census (61M+ cells). Search by cell type/tissue/disease/organism; get AnnData, stream out-of-core, train PyTorch models. For your own data use scanpy; for annotated data ' in text, "expected to find: " + 'description: "Query CELLxGENE Census (61M+ cells). Search by cell type/tissue/disease/organism; get AnnData, stream out-of-core, train PyTorch models. For your own data use scanpy; for annotated data '[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/clinpgx-database/SKILL.md')
    assert 'description: "Query PharmGKB REST API for drug-gene interactions, clinical annotations, CPIC/DPWG guidelines, variant-drug associations, PGx pathways. Search by gene/drug/rsID/pathway; no auth. For so' in text, "expected to find: " + 'description: "Query PharmGKB REST API for drug-gene interactions, clinical annotations, CPIC/DPWG guidelines, variant-drug associations, PGx pathways. Search by gene/drug/rsID/pathway; no auth. For so'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/clinvar-database/SKILL.md')
    assert 'description: "Query NCBI ClinVar via E-utilities for variant clinical significance, pathogenicity, disease associations. Search by gene/rsID/condition/review status; returns ClinSig, submitter data, c' in text, "expected to find: " + 'description: "Query NCBI ClinVar via E-utilities for variant clinical significance, pathogenicity, disease associations. Search by gene/rsID/condition/review status; returns ClinSig, submitter data, c'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/cnvkit-copy-number/SKILL.md')
    assert 'description: "Detect somatic CNVs from WES/WGS/targeted BAMs (CNVkit v0.9.x). Bin coverage in target/antitarget regions, normalize vs reference, segment with CBS/HMM, call amps/dels, scatter/diagram p' in text, "expected to find: " + 'description: "Detect somatic CNVs from WES/WGS/targeted BAMs (CNVkit v0.9.x). Bin coverage in target/antitarget regions, normalize vs reference, segment with CBS/HMM, call amps/dels, scatter/diagram p'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/cosmic-database/SKILL.md')
    assert 'description: "Query COSMIC for cancer somatic mutations, gene census, mutational signatures, drug resistance variants. REST API v3.1 supports gene/sample/variant queries; free registration. For germli' in text, "expected to find: " + 'description: "Query COSMIC for cancer somatic mutations, gene census, mutational signatures, drug resistance variants. REST API v3.1 supports gene/sample/variant queries; free registration. For germli'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/dbsnp-database/SKILL.md')
    assert 'description: "Query NCBI dbSNP for SNP records by rsID, gene, or region via E-utilities and Variation Services REST API. Retrieve alleles, MAF, variant class (SNV/indel/MNV), clinical links, cross-DB ' in text, "expected to find: " + 'description: "Query NCBI dbSNP for SNP records by rsID, gene, or region via E-utilities and Variation Services REST API. Retrieve alleles, MAF, variant class (SNV/indel/MNV), clinical links, cross-DB '[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/deeptools-ngs-analysis/SKILL.md')
    assert 'description: "NGS CLI for ChIP/RNA/ATAC-seq. BAM→bigWig with RPGC/CPM/RPKM, sample correlation/PCA, heatmaps/profiles around features, fingerprints. For alignment use STAR/BWA; for peak calling use MA' in text, "expected to find: " + 'description: "NGS CLI for ChIP/RNA/ATAC-seq. BAM→bigWig with RPGC/CPM/RPKM, sample correlation/PCA, heatmaps/profiles around features, fingerprints. For alignment use STAR/BWA; for peak calling use MA'[:80]


def test_signal_58():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/depmap-crispr-essentiality/SKILL.md')
    assert 'description: "DepMap CRISPR gene effect (Chronos) analysis: sign convention for essentiality, per-gene NaN-safe Spearman correlation, data loading/alignment. For general NaN-safe correlation see nan-s' in text, "expected to find: " + 'description: "DepMap CRISPR gene effect (Chronos) analysis: sign convention for essentiality, per-gene NaN-safe Spearman correlation, data loading/alignment. For general NaN-safe correlation see nan-s'[:80]


def test_signal_59():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/deseq2-differential-expression/SKILL.md')
    assert 'description: "Bulk RNA-seq DE with R/Bioconductor DESeq2. Negative binomial GLM, empirical Bayes shrinkage, Wald/LRT tests, multi-factor designs, Salmon tximeta import, apeglm LFC shrinkage, MA/volcan' in text, "expected to find: " + 'description: "Bulk RNA-seq DE with R/Bioconductor DESeq2. Negative binomial GLM, empirical Bayes shrinkage, Wald/LRT tests, multi-factor designs, Salmon tximeta import, apeglm LFC shrinkage, MA/volcan'[:80]


def test_signal_60():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/ena-database/SKILL.md')
    assert 'description: "ENA REST API for sequences, reads, assemblies, and annotations. Portal API search, Browser API retrieval (XML/FASTA/EMBL), file reports for FASTQ/BAM URLs, taxonomy, cross-refs. For mult' in text, "expected to find: " + 'description: "ENA REST API for sequences, reads, assemblies, and annotations. Portal API search, Browser API retrieval (XML/FASTA/EMBL), file reports for FASTQ/BAM URLs, taxonomy, cross-refs. For mult'[:80]


def test_signal_61():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/encode-database/SKILL.md')
    assert 'description: "ENCODE Portal REST API for regulatory genomics: TF ChIP-seq, ATAC-seq/DNase-seq peaks, histone marks, and RNA-seq across 1000+ cell types. Search experiments by assay/biosample/target; d' in text, "expected to find: " + 'description: "ENCODE Portal REST API for regulatory genomics: TF ChIP-seq, ATAC-seq/DNase-seq peaks, histone marks, and RNA-seq across 1000+ cell types. Search experiments by assay/biosample/target; d'[:80]


def test_signal_62():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/ensembl-database/SKILL.md')
    assert 'description: "Ensembl REST API for gene/transcript/variant annotations in 300+ species. Gene info by symbol/ID, sequence, cross-refs (HGNC, RefSeq, UniProt), regulatory features. For bulk local use py' in text, "expected to find: " + 'description: "Ensembl REST API for gene/transcript/variant annotations in 300+ species. Gene info by symbol/ID, sequence, cross-refs (HGNC, RefSeq, UniProt), regulatory features. For bulk local use py'[:80]


def test_signal_63():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/etetoolkit/SKILL.md')
    assert 'description: "ETE Toolkit (ETE3): Python phylogenetic tree analysis and visualization. Parse Newick/NHX/PhyloXML, traverse/annotate nodes, render figures with TreeStyle/NodeStyle, integrate NCBI taxon' in text, "expected to find: " + 'description: "ETE Toolkit (ETE3): Python phylogenetic tree analysis and visualization. Parse Newick/NHX/PhyloXML, traverse/annotate nodes, render figures with TreeStyle/NodeStyle, integrate NCBI taxon'[:80]


def test_signal_64():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/fastp-fastq-preprocessing/SKILL.md')
    assert 'description: "All-in-one FASTQ QC and adapter trimming. Auto-detects Illumina adapters, filters low-quality reads, corrects paired-end overlaps, emits HTML+JSON QC in one pass. 3-10x faster than Trim ' in text, "expected to find: " + 'description: "All-in-one FASTQ QC and adapter trimming. Auto-detects Illumina adapters, filters low-quality reads, corrects paired-end overlaps, emits HTML+JSON QC in one pass. 3-10x faster than Trim '[:80]


def test_signal_65():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/featurecounts-rna-counting/SKILL.md')
    assert 'description: "Counts RNA-seq reads overlapping GTF gene features. Takes sorted STAR BAMs plus GTF; outputs a per-gene tab-delimited matrix across samples. Handles strandedness (0/1/2), paired-end, mul' in text, "expected to find: " + 'description: "Counts RNA-seq reads overlapping GTF gene features. Takes sorted STAR BAMs plus GTF; outputs a per-gene tab-delimited matrix across samples. Handles strandedness (0/1/2), paired-end, mul'[:80]


def test_signal_66():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/gatk-variant-calling/SKILL.md')
    assert 'description: "GATK Best Practices for germline SNP/indel calling from WGS/WES BAMs. Per-sample HaplotypeCaller GVCFs, GenomicsDBImport, GenotypeGVCFs joint calling, VQSR or hard filters. Requires BWA-' in text, "expected to find: " + 'description: "GATK Best Practices for germline SNP/indel calling from WGS/WES BAMs. Per-sample HaplotypeCaller GVCFs, GenomicsDBImport, GenotypeGVCFs joint calling, VQSR or hard filters. Requires BWA-'[:80]


def test_signal_67():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/gene-database/SKILL.md')
    assert 'description: "NCBI Gene via E-utilities: curated records across 1M+ taxa. Official symbols, aliases, RefSeq IDs, summaries, coordinates, GO, interactions. Use for gene ID resolution and cross-species ' in text, "expected to find: " + 'description: "NCBI Gene via E-utilities: curated records across 1M+ taxa. Official symbols, aliases, RefSeq IDs, summaries, coordinates, GO, interactions. Use for gene ID resolution and cross-species '[:80]


def test_signal_68():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/geniml/SKILL.md')
    assert 'description: "Python library for genomic interval ML. Train/apply region2vec embeddings turning BED regions into vectors, index interval datasets for ML, search embedding space with BEDSpace, and eval' in text, "expected to find: " + 'description: "Python library for genomic interval ML. Train/apply region2vec embeddings turning BED regions into vectors, index interval datasets for ML, search embedding space with BEDSpace, and eval'[:80]


def test_signal_69():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/geo-database/SKILL.md')
    assert 'description: "NCBI GEO access via GEOparse and E-utilities. Search by keyword/organism/platform, download GSE series matrices, parse GPL annotations, extract GSM metadata, load expression matrices int' in text, "expected to find: " + 'description: "NCBI GEO access via GEOparse and E-utilities. Search by keyword/organism/platform, download GSE series matrices, parse GPL annotations, extract GSM metadata, load expression matrices int'[:80]


def test_signal_70():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/gget-genomic-databases/SKILL.md')
    assert 'description: "Unified CLI/Python interface to 20+ genomic databases. Gene lookups (Ensembl search/info/seq), BLAST/BLAT, AlphaFold, Enrichr enrichment, OpenTargets disease/drug, CELLxGENE single-cell,' in text, "expected to find: " + 'description: "Unified CLI/Python interface to 20+ genomic databases. Gene lookups (Ensembl search/info/seq), BLAST/BLAT, AlphaFold, Enrichr enrichment, OpenTargets disease/drug, CELLxGENE single-cell,'[:80]


def test_signal_71():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/gnomad-database/SKILL.md')
    assert 'description: "gnomAD v4 population variant frequencies via GraphQL API. Allele counts and frequencies stratified by ancestry (AFR, AMR, EAS, NFE, SAS, FIN, ASJ, MID), gene-level constraint (pLI, LOEUF' in text, "expected to find: " + 'description: "gnomAD v4 population variant frequencies via GraphQL API. Allele counts and frequencies stratified by ancestry (AFR, AMR, EAS, NFE, SAS, FIN, ASJ, MID), gene-level constraint (pLI, LOEUF'[:80]


def test_signal_72():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/gseapy-gene-enrichment/SKILL.md')
    assert 'description: "GSEA and over-representation analysis (ORA) for RNA-seq and proteomics. Wraps Enrichr for ORA against MSigDB, KEGG, GO, and 200+ databases; runs preranked GSEA on ranked DE gene lists. O' in text, "expected to find: " + 'description: "GSEA and over-representation analysis (ORA) for RNA-seq and proteomics. Wraps Enrichr for ORA against MSigDB, KEGG, GO, and 200+ databases; runs preranked GSEA on ranked DE gene lists. O'[:80]


def test_signal_73():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/gtars/SKILL.md')
    assert 'description: "Rust-backed Python library for fast genomic token arithmetic and BED processing. High-performance BED I/O, interval set ops (intersect, merge, complement, subtract), region tokenization ' in text, "expected to find: " + 'description: "Rust-backed Python library for fast genomic token arithmetic and BED processing. High-performance BED I/O, interval set ops (intersect, merge, complement, subtract), region tokenization '[:80]


def test_signal_74():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/gwas-database/SKILL.md')
    assert 'description: "NHGRI-EBI GWAS Catalog REST API for SNP-trait associations from published GWAS. Query studies, associations, variants, traits, genes, summary stats. Build PRS candidates, analyze pleiotr' in text, "expected to find: " + 'description: "NHGRI-EBI GWAS Catalog REST API for SNP-trait associations from published GWAS. Query studies, associations, variants, traits, genes, summary stats. Build PRS candidates, analyze pleiotr'[:80]


def test_signal_75():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/harmony-batch-correction/SKILL.md')
    assert 'description: "Harmony batch correction for scRNA-seq and other omics. Removes batch effects from PCA embeddings while preserving biology. Run after PCA, before UMAP. Scales to millions of cells. Pytho' in text, "expected to find: " + 'description: "Harmony batch correction for scRNA-seq and other omics. Removes batch effects from PCA embeddings while preserving biology. Run after PCA, before UMAP. Scales to millions of cells. Pytho'[:80]


def test_signal_76():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/homer-motif-analysis/SKILL.md')
    assert 'description: "De novo and known TF motif enrichment in ChIP-seq/ATAC-seq peaks via HOMER. findMotifsGenome.pl finds over-represented patterns vs background; annotatePeaks.pl assigns context (TSS dista' in text, "expected to find: " + 'description: "De novo and known TF motif enrichment in ChIP-seq/ATAC-seq peaks via HOMER. findMotifsGenome.pl finds over-represented patterns vs background; annotatePeaks.pl assigns context (TSS dista'[:80]


def test_signal_77():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/jaspar-database/SKILL.md')
    assert 'description: "JASPAR 2024 TF binding profiles via REST API and pyJASPAR. Retrieve PFMs/PWMs by TF name, JASPAR ID, species, or structural class. Scan DNA for TFBS; browse by taxon (human, mouse) or TF' in text, "expected to find: " + 'description: "JASPAR 2024 TF binding profiles via REST API and pyJASPAR. Retrieve PFMs/PWMs by TF name, JASPAR ID, species, or structural class. Scan DNA for TFBS; browse by taxon (human, mouse) or TF'[:80]


def test_signal_78():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/kegg-database/SKILL.md')
    assert 'description: "KEGG REST API (academic only). Pathways, genes, compounds, enzymes, diseases, drugs via 7 ops (info/list/find/get/conv/link/ddi). ID conversion (NCBI/UniProt/PubChem). Use bioservices fo' in text, "expected to find: " + 'description: "KEGG REST API (academic only). Pathways, genes, compounds, enzymes, diseases, drugs via 7 ops (info/list/find/get/conv/link/ddi). ID conversion (NCBI/UniProt/PubChem). Use bioservices fo'[:80]


def test_signal_79():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/macs3-peak-calling/SKILL.md')
    assert 'description: "Poisson-model peak caller for ChIP-seq/ATAC-seq BAMs. MACS3 callpeak finds enriched regions (TF sites or histone marks) vs input/IgG; outputs BED narrowPeak/broadPeak for motif analysis,' in text, "expected to find: " + 'description: "Poisson-model peak caller for ChIP-seq/ATAC-seq BAMs. MACS3 callpeak finds enriched regions (TF sites or histone marks) vs input/IgG; outputs BED narrowPeak/broadPeak for motif analysis,'[:80]


def test_signal_80():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/monarch-database/SKILL.md')
    assert 'description: "Monarch Initiative knowledge graph REST API for disease-gene-phenotype associations and cross-species orthology. MONDO disease-to-gene/phenotype, HP phenotype profiles, cross-species com' in text, "expected to find: " + 'description: "Monarch Initiative knowledge graph REST API for disease-gene-phenotype associations and cross-species orthology. MONDO disease-to-gene/phenotype, HP phenotype profiles, cross-species com'[:80]


def test_signal_81():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/mouse-phenome-database/SKILL.md')
    assert 'description: "Retrieve quantitative phenotypes across inbred mouse strains from MPD: metabolic, behavioral, physiological traits. Query strain means and raw measurements for body weight, glucose, bloo' in text, "expected to find: " + 'description: "Retrieve quantitative phenotypes across inbred mouse strains from MPD: metabolic, behavioral, physiological traits. Query strain means and raw measurements for body weight, glucose, bloo'[:80]


def test_signal_82():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/multiqc-qc-reports/SKILL.md')
    assert 'description: "Aggregates QC from 150+ bioinformatics tools into one interactive HTML report. Scans FastQC, samtools, STAR, HISAT2, Trim Galore, featureCounts, Kallisto, Salmon, Picard, GATK logs; merg' in text, "expected to find: " + 'description: "Aggregates QC from 150+ bioinformatics tools into one interactive HTML report. Scans FastQC, samtools, STAR, HISAT2, Trim Galore, featureCounts, Kallisto, Salmon, Picard, GATK logs; merg'[:80]


def test_signal_83():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md')
    assert 'description: "GWAS and population genetics tool. Processes PLINK (.bed/.bim/.fam), VCF, and BGEN; runs QC (MAF, HWE, missingness), IBD estimation, PCA, and linear/logistic regression GWAS. Outputs Man' in text, "expected to find: " + 'description: "GWAS and population genetics tool. Processes PLINK (.bed/.bim/.fam), VCF, and BGEN; runs QC (MAF, HWE, missingness), IBD estimation, PCA, and linear/logistic regression GWAS. Outputs Man'[:80]


def test_signal_84():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/popv-cell-annotation/SKILL.md')
    assert 'description: "Consensus cell type annotation: runs 10+ algorithms (KNN-Harmony/BBKNN/Scanorama/scVI, CellTypist, ONCLASS, Random Forest, SCANVI, SVM, XGBoost) on a labeled reference and transfers labe' in text, "expected to find: " + 'description: "Consensus cell type annotation: runs 10+ algorithms (KNN-Harmony/BBKNN/Scanorama/scVI, CellTypist, ONCLASS, Random Forest, SCANVI, SVM, XGBoost) on a labeled reference and transfers labe'[:80]


def test_signal_85():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/prokka-genome-annotation/SKILL.md')
    assert 'description: "Annotate prokaryotic genomes (bacteria, archaea, viruses) via Prokka\'s BLAST/HMM pipeline. Identifies CDS, rRNA, tRNA, tmRNA, signal peptides against Pfam, TIGRFAMs, RefSeq. Outputs GFF3' in text, "expected to find: " + 'description: "Annotate prokaryotic genomes (bacteria, archaea, viruses) via Prokka\'s BLAST/HMM pipeline. Identifies CDS, rRNA, tRNA, tmRNA, signal peptides against Pfam, TIGRFAMs, RefSeq. Outputs GFF3'[:80]


def test_signal_86():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/pubmed-database/SKILL.md')
    assert 'citation matching, systematic review strategies. Use for biomedical' in text, "expected to find: " + 'citation matching, systematic review strategies. Use for biomedical'[:80]


def test_signal_87():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/pubmed-database/SKILL.md')
    assert 'Programmatic PubMed access via NCBI E-utilities REST API. Covers' in text, "expected to find: " + 'Programmatic PubMed access via NCBI E-utilities REST API. Covers'[:80]


def test_signal_88():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/pubmed-database/SKILL.md')
    assert 'Boolean/MeSH queries, field-tagged search, endpoints (ESearch,' in text, "expected to find: " + 'Boolean/MeSH queries, field-tagged search, endpoints (ESearch,'[:80]


def test_signal_89():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/pydeseq2-differential-expression/SKILL.md')
    assert 'description: "Bulk RNA-seq DE with PyDESeq2: load counts, normalize, fit negative binomial models, Wald test (BH-FDR), LFC shrinkage, volcano/MA plots. Use for two-group comparisons, multi-factor desi' in text, "expected to find: " + 'description: "Bulk RNA-seq DE with PyDESeq2: load counts, normalize, fit negative binomial models, Wald test (BH-FDR), LFC shrinkage, volcano/MA plots. Use for two-group comparisons, multi-factor desi'[:80]


def test_signal_90():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md')
    assert 'description: "Read/write SAM/BAM/CRAM, VCF/BCF, FASTA/FASTQ. Region queries, pileup, variant filtering, read groups. Python htslib wrapper exposing samtools/bcftools CLI. Use STAR/BWA for alignment; G' in text, "expected to find: " + 'description: "Read/write SAM/BAM/CRAM, VCF/BCF, FASTA/FASTQ. Region queries, pileup, variant filtering, read groups. Python htslib wrapper exposing samtools/bcftools CLI. Use STAR/BWA for alignment; G'[:80]


def test_signal_91():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/quickgo-database/SKILL.md')
    assert 'description: "Query EBI QuickGO REST API for GO terms and protein annotations. Fetch term metadata by ID, search by keyword, walk ancestor/descendant hierarchies, download annotations filtered by taxo' in text, "expected to find: " + 'description: "Query EBI QuickGO REST API for GO terms and protein annotations. Fetch term metadata by ID, search by keyword, walk ancestor/descendant hierarchies, download annotations filtered by taxo'[:80]


def test_signal_92():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/regulomedb-database/SKILL.md')
    assert 'description: "Query RegulomeDB v2 REST API to score variants for regulatory function and retrieve overlapping evidence (TF binding, histone marks, DNase peaks, eQTLs, motifs). Score single rsID/positi' in text, "expected to find: " + 'description: "Query RegulomeDB v2 REST API to score variants for regulatory function and retrieve overlapping evidence (TF binding, histone marks, DNase peaks, eQTLs, motifs). Score single rsID/positi'[:80]


def test_signal_93():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/remap-database/SKILL.md')
    assert 'description: "Query ReMap 2022 TF ChIP-seq peak database via REST API and BED downloads. Retrieve TF peaks overlapping a region (chr:start-end), peaks near a gene, TFs by species, peaks filtered by bi' in text, "expected to find: " + 'description: "Query ReMap 2022 TF ChIP-seq peak database via REST API and BED downloads. Retrieve TF peaks overlapping a region (chr:start-end), peaks near a gene, TFs by species, peaks filtered by bi'[:80]


def test_signal_94():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/salmon-rna-quantification/SKILL.md')
    assert 'description: "Ultra-fast RNA-seq transcript/gene quantification via quasi-mapping (no BAM). Builds a k-mer index from transcriptome FASTA, quantifies in minutes. Outputs TPM/count tables (quant.sf) wi' in text, "expected to find: " + 'description: "Ultra-fast RNA-seq transcript/gene quantification via quasi-mapping (no BAM). Builds a k-mer index from transcriptome FASTA, quantifies in minutes. Outputs TPM/count tables (quant.sf) wi'[:80]


def test_signal_95():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/samtools-bam-processing/SKILL.md')
    assert 'description: "CLI toolkit for SAM/BAM/CRAM: sort, index, convert, filter, QC alignments. Core commands: view, sort, index, flagstat, stats, depth, markdup, merge. Required between alignment and varian' in text, "expected to find: " + 'description: "CLI toolkit for SAM/BAM/CRAM: sort, index, convert, filter, QC alignments. Core commands: view, sort, index, flagstat, stats, depth, markdup, merge. Required between alignment and varian'[:80]


def test_signal_96():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/scanpy-scrna-seq/SKILL.md')
    assert 'description: "scRNA-seq with Scanpy: QC, normalization, HVG selection, PCA, neighborhood graph, UMAP/t-SNE, Leiden clustering, markers, cell annotation, trajectory inference. Standard scRNA-seq explor' in text, "expected to find: " + 'description: "scRNA-seq with Scanpy: QC, normalization, HVG selection, PCA, neighborhood graph, UMAP/t-SNE, Leiden clustering, markers, cell annotation, trajectory inference. Standard scRNA-seq explor'[:80]


def test_signal_97():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/scikit-bio/SKILL.md')
    assert '(Shannon, Faith PD, Bray-Curtis, UniFrac), ordination (PCoA, CCA, RDA),' in text, "expected to find: " + '(Shannon, Faith PD, Bray-Curtis, UniFrac), ordination (PCoA, CCA, RDA),'[:80]


def test_signal_98():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/scikit-bio/SKILL.md')
    assert 'pairwise/multiple alignment, phylogenetic trees (NJ, UPGMA), diversity' in text, "expected to find: " + 'pairwise/multiple alignment, phylogenetic trees (NJ, UPGMA), diversity'[:80]


def test_signal_99():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/scikit-bio/SKILL.md')
    assert 'Python library for biology: sequence manipulation (DNA/RNA/protein),' in text, "expected to find: " + 'Python library for biology: sequence manipulation (DNA/RNA/protein),'[:80]


def test_signal_100():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/scvi-tools-single-cell/SKILL.md')
    assert 'description: "Deep generative models for single-cell omics: probabilistic batch correction (scVI), semi-supervised annotation (scANVI), CITE-seq RNA+protein (totalVI), transfer learning (scARCHES), an' in text, "expected to find: " + 'description: "Deep generative models for single-cell omics: probabilistic batch correction (scVI), semi-supervised annotation (scANVI), CITE-seq RNA+protein (totalVI), transfer learning (scARCHES), an'[:80]


def test_signal_101():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/single-cell-annotation-guide/SKILL.md')
    assert 'description: "Decision framework for manual marker-based, automated (CellTypist), and reference-based (popV) cell type annotation in scRNA-seq. Three-tier strategy: Tier 1 manual markers, Tier 2 CellT' in text, "expected to find: " + 'description: "Decision framework for manual marker-based, automated (CellTypist), and reference-based (popV) cell type annotation in scRNA-seq. Three-tier strategy: Tier 1 manual markers, Tier 2 CellT'[:80]


def test_signal_102():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/snpeff-variant-annotation/SKILL.md')
    assert 'description: "Annotate and filter VCF variants with SnpEff and SnpSift. SnpEff predicts functional effects (HIGH/MODERATE/LOW/MODIFIER), genes, transcripts, AA changes, HGVS; SnpSift filters and adds ' in text, "expected to find: " + 'description: "Annotate and filter VCF variants with SnpEff and SnpSift. SnpEff predicts functional effects (HIGH/MODERATE/LOW/MODIFIER), genes, transcripts, AA changes, HGVS; SnpSift filters and adds '[:80]


def test_signal_103():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/star-rna-seq-aligner/SKILL.md')
    assert 'description: "Splice-aware RNA-seq aligner producing sorted BAM and splice junction tables. Builds genome index, runs two-pass alignment for better junctions. Outputs sorted BAM, junctions (SJ.out.tab' in text, "expected to find: " + 'description: "Splice-aware RNA-seq aligner producing sorted BAM and splice junction tables. Builds genome index, runs two-pass alignment for better junctions. Outputs sorted BAM, junctions (SJ.out.tab'[:80]


def test_signal_104():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/ucsc-genome-browser/SKILL.md')
    assert 'description: "Query UCSC Genome Browser REST API for DNA sequences, tracks, gene models, and conservation across 100+ assemblies. Retrieve sequence by region, list/fetch BED/bigWig tracks, chromosome ' in text, "expected to find: " + 'description: "Query UCSC Genome Browser REST API for DNA sequences, tracks, gene models, and conservation across 100+ assemblies. Retrieve sequence by region, list/fetch BED/bigWig tracks, chromosome '[:80]


def test_signal_105():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/vcf-variant-filtering/SKILL.md')
    assert 'description: "Guide to quality filtering raw VCF files before computing summary stats (Ts/Tv ratio, variant counts, AF distributions). Covers detecting raw VCFs via FILTER column and QUAL inspection, ' in text, "expected to find: " + 'description: "Guide to quality filtering raw VCF files before computing summary stats (Ts/Tv ratio, variant counts, AF distributions). Covers detecting raw VCFs via FILTER column and QUAL inspection, '[:80]


def test_signal_106():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lab-automation/benchling-integration/SKILL.md')
    assert 'description: "Benchling R&D Python SDK: CRUD on registry entities (DNA, RNA, proteins, custom), inventory, ELN, workflow automation. Needs Benchling account and API key. Use biopython for local sequen' in text, "expected to find: " + 'description: "Benchling R&D Python SDK: CRUD on registry entities (DNA, RNA, proteins, custom), inventory, ELN, workflow automation. Needs Benchling account and API key. Use biopython for local sequen'[:80]


def test_signal_107():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lab-automation/opentrons-integration/SKILL.md')
    assert 'description: "Opentrons Protocol API v2 for OT-2/Flex: Python protocols for pipetting, serial dilutions, PCR, plate replication; control thermocycler, heater-shaker, magnetic, temperature modules. Use' in text, "expected to find: " + 'description: "Opentrons Protocol API v2 for OT-2/Flex: Python protocols for pipetting, serial dilutions, PCR, plate replication; control thermocycler, heater-shaker, magnetic, temperature modules. Use'[:80]


def test_signal_108():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lab-automation/opentrons-protocol-api/SKILL.md')
    assert 'description: "Python API v2 for Opentrons OT-2/Flex liquid handlers: protocols as Python files with metadata and run(); control pipettes, labware, and modules (thermocycler, heater-shaker, magnetic, t' in text, "expected to find: " + 'description: "Python API v2 for Opentrons OT-2/Flex liquid handlers: protocols as Python files with metadata and run(); control pipettes, labware, and modules (thermocycler, heater-shaker, magnetic, t'[:80]


def test_signal_109():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lab-automation/protocolsio-integration/SKILL.md')
    assert 'description: "protocols.io REST API: search and fetch wet-lab, bioinformatics, and clinical protocols by keyword, DOI, or category, with steps, reagents, materials, equipment, timing. Public access fr' in text, "expected to find: " + 'description: "protocols.io REST API: search and fetch wet-lab, bioinformatics, and clinical protocols by keyword, DOI, or category, with steps, reagents, materials, equipment, timing. Public access fr'[:80]


def test_signal_110():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lab-automation/pylabrobot/SKILL.md')
    assert 'description: "Hardware-agnostic Python liquid-handler library: portable scripts run on Hamilton STAR, Tecan Freedom EVO, Opentrons OT-2, or a simulator without vendor lock-in. For protocol automation,' in text, "expected to find: " + 'description: "Hardware-agnostic Python liquid-handler library: portable scripts run on Hamilton STAR, Tecan Freedom EVO, Opentrons OT-2, or a simulator without vendor lock-in. For protocol automation,'[:80]


def test_signal_111():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lab-automation/western-blot-quantification/SKILL.md')
    assert 'description: "Quantitative Western blot analysis: band detection, two-step normalization, fold change, replicate aggregation, publication-ready figures. Use for multi-condition, multi-replicate blots,' in text, "expected to find: " + 'description: "Quantitative Western blot analysis: band detection, two-step normalization, fold change, replicate aggregation, publication-ready figures. Use for multi-condition, multi-replicate blots,'[:80]


def test_signal_112():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/molecular-biology/plannotate-plasmid-annotation/SKILL.md')
    assert 'description: "Auto-annotate plasmids with features (promoters, terminators, resistance, origins, tags, fluorescent proteins) via BLAST against curated DBs (Addgene, fpbase, SnapGene). FASTA or raw seq' in text, "expected to find: " + 'description: "Auto-annotate plasmids with features (promoters, terminators, resistance, origins, tags, fluorescent proteins) via BLAST against curated DBs (Addgene, fpbase, SnapGene). FASTA or raw seq'[:80]


def test_signal_113():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/molecular-biology/sgrna-design-guide/SKILL.md')
    assert 'description: "Decision guide for finding/designing sgRNAs via three tiers: (1) validated from Addgene/literature, (2) pre-computed from Broad CRISPick, (3) de novo via CRISPOR/Benchling as last resort' in text, "expected to find: " + 'description: "Decision guide for finding/designing sgRNAs via three tiers: (1) validated from Addgene/literature, (2) pre-computed from Broad CRISPick, (3) de novo via CRISPOR/Benchling as last resort'[:80]


def test_signal_114():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/molecular-biology/viennarna-structure-prediction/SKILL.md')
    assert 'description: "Predict RNA secondary structure, MFE folding, base-pair probabilities, RNA-RNA interactions via ViennaRNA Python bindings. Pipeline: sequence → MFE → partition function and pair-probabil' in text, "expected to find: " + 'description: "Predict RNA secondary structure, MFE folding, base-pair probabilities, RNA-RNA interactions via ViennaRNA Python bindings. Pipeline: sequence → MFE → partition function and pair-probabil'[:80]


def test_signal_115():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proteomics-protein-engineering/adaptyv-bio/SKILL.md')
    assert 'description: "API + Python SDK for ordering cell-free protein expression and binding assays. Submit sequences for expression (10–100 µg), measure binding affinity (KD) against targets, track status, a' in text, "expected to find: " + 'description: "API + Python SDK for ordering cell-free protein expression and binding assays. Submit sequences for expression (10–100 µg), measure binding affinity (KD) against targets, track status, a'[:80]


def test_signal_116():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proteomics-protein-engineering/esm-protein-language-model/SKILL.md')
    assert 'description: "Protein language models (ESM3, ESM C) for sequence generation, structure prediction, inverse folding, and embeddings. Design novel proteins, extract ML features, or fold sequences. Local' in text, "expected to find: " + 'description: "Protein language models (ESM3, ESM C) for sequence generation, structure prediction, inverse folding, and embeddings. Design novel proteins, extract ML features, or fold sequences. Local'[:80]


def test_signal_117():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proteomics-protein-engineering/hmdb-database/SKILL.md')
    assert 'description: "Parse HMDB (Human Metabolome Database) local XML for metabolite info, chemical properties, biological context, disease links, spectra, and cross-DB mapping. No REST API — uses ~6 GB XML ' in text, "expected to find: " + 'description: "Parse HMDB (Human Metabolome Database) local XML for metabolite info, chemical properties, biological context, disease links, spectra, and cross-DB mapping. No REST API — uses ~6 GB XML '[:80]


def test_signal_118():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proteomics-protein-engineering/interpro-database/SKILL.md')
    assert 'description: "Query InterPro REST API for protein domain architecture, family classification, and member-DB integration. Search entries, retrieve a protein\'s domains, list family members, get taxonomi' in text, "expected to find: " + 'description: "Query InterPro REST API for protein domain architecture, family classification, and member-DB integration. Search entries, retrieve a protein\'s domains, list family members, get taxonomi'[:80]


def test_signal_119():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proteomics-protein-engineering/matchms-spectral-matching/SKILL.md')
    assert 'description: MS spectral matching and metabolite ID with matchms. Import spectra (mzML, MGF, MSP, JSON), filter/normalize peaks, score similarity (cosine, modified cosine, fingerprint), build reproduc' in text, "expected to find: " + 'description: MS spectral matching and metabolite ID with matchms. Import spectra (mzML, MGF, MSP, JSON), filter/normalize peaks, score similarity (cosine, modified cosine, fingerprint), build reproduc'[:80]


def test_signal_120():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proteomics-protein-engineering/maxquant-proteomics/SKILL.md')
    assert 'description: "MaxQuant + Perseus proteomics pipeline: run MaxQuant for LFQ and SILAC; parse proteinGroups.txt in Python; filter contaminants/decoys; log2 + median-normalize; impute MNAR; t-test with F' in text, "expected to find: " + 'description: "MaxQuant + Perseus proteomics pipeline: run MaxQuant for LFQ and SILAC; parse proteinGroups.txt in Python; filter contaminants/decoys; log2 + median-normalize; impute MNAR; t-test with F'[:80]


def test_signal_121():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proteomics-protein-engineering/metabolomics-workbench-database/SKILL.md')
    assert 'description: "Query Metabolomics Workbench REST API (4,200+ NIH studies) for metabolite ID, study discovery, RefMet standardization, m/z precursor searches, MetStat filtering, gene/protein annotations' in text, "expected to find: " + 'description: "Query Metabolomics Workbench REST API (4,200+ NIH studies) for metabolite ID, study discovery, RefMet standardization, m/z precursor searches, MetStat filtering, gene/protein annotations'[:80]


def test_signal_122():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proteomics-protein-engineering/pride-database/SKILL.md')
    assert 'description: "Search PRIDE Archive REST API for proteomics datasets, peptide IDs, and MS raw files. Find experiments by organism, tissue, disease, or instrument; download RAW/mzML; retrieve peptide/PS' in text, "expected to find: " + 'description: "Search PRIDE Archive REST API for proteomics datasets, peptide IDs, and MS raw files. Find experiments by organism, tissue, disease, or instrument; download RAW/mzML; retrieve peptide/PS'[:80]


def test_signal_123():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proteomics-protein-engineering/pyopenms-mass-spectrometry/SKILL.md')
    assert 'description: MS data processing with PyOpenMS for LC-MS/MS proteomics and metabolomics — mzML/mzXML I/O, signal processing (smoothing, peak picking, centroiding), feature detection/linking, peptide/pr' in text, "expected to find: " + 'description: MS data processing with PyOpenMS for LC-MS/MS proteomics and metabolomics — mzML/mzXML I/O, signal processing (smoothing, peak picking, centroiding), feature detection/linking, peptide/pr'[:80]


def test_signal_124():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/proteomics-protein-engineering/uniprot-protein-database/SKILL.md')
    assert 'description: "Query UniProt REST API: search by gene/protein name, fetch FASTA, map IDs (Ensembl, PDB, RefSeq), access Swiss-Prot annotations. Use bioservices for multi-DB access; alphafold-database f' in text, "expected to find: " + 'description: "Query UniProt REST API: search by gene/protein name, fetch FASTA, map IDs (Ensembl, PDB, RefSeq), access Swiss-Prot annotations. Use bioservices for multi-DB access; alphafold-database f'[:80]


def test_signal_125():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/aeon/SKILL.md')
    assert 'description: "scikit-learn compatible Python toolkit for time series ML: classify, cluster, regress, segment, transform with 30+ algorithms (ROCKET, InceptionTime, KNN-DTW, HIVE-COTE, WEASEL). Handles' in text, "expected to find: " + 'description: "scikit-learn compatible Python toolkit for time series ML: classify, cluster, regress, segment, transform with 30+ algorithms (ROCKET, InceptionTime, KNN-DTW, HIVE-COTE, WEASEL). Handles'[:80]


def test_signal_126():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/astropy-astronomy/SKILL.md')
    assert 'description: "Core Python library for astronomy/astrophysics: units with dimensional analysis, celestial coordinate transforms (ICRS/Galactic/AltAz/FK5), FITS I/O, tables (FITS/HDF5/VOTable/CSV), cosm' in text, "expected to find: " + 'description: "Core Python library for astronomy/astrophysics: units with dimensional analysis, celestial coordinate transforms (ICRS/Galactic/AltAz/FK5), FITS I/O, tables (FITS/HDF5/VOTable/CSV), cosm'[:80]


def test_signal_127():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/dask-parallel-computing/SKILL.md')
    assert 'description: "Parallel/distributed computing for larger-than-RAM data. Components: DataFrames (parallel pandas), Arrays (parallel NumPy), Bags, Futures, Schedulers. Scales laptop to HPC cluster. For s' in text, "expected to find: " + 'description: "Parallel/distributed computing for larger-than-RAM data. Components: DataFrames (parallel pandas), Arrays (parallel NumPy), Bags, Futures, Schedulers. Scales laptop to HPC cluster. For s'[:80]


def test_signal_128():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/exploratory-data-analysis/SKILL.md')
    assert 'omics), quality assessment, report generation, format detection across 200+' in text, "expected to find: " + 'omics), quality assessment, report generation, format detection across 200+'[:80]


def test_signal_129():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/exploratory-data-analysis/SKILL.md')
    assert 'formats. Use when given a data file for initial exploration or to pick an' in text, "expected to find: " + 'formats. Use when given a data file for initial exploration or to pick an'[:80]


def test_signal_130():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/exploratory-data-analysis/SKILL.md')
    assert 'frameworks by data type (tabular, sequence, image, spectral, structural,' in text, "expected to find: " + 'frameworks by data type (tabular, sequence, image, spectral, structural,'[:80]


def test_signal_131():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/geopandas-geospatial/SKILL.md')
    assert 'basemaps). Use for spatial joins, overlays, CRS transforms, area/distance, maps.' in text, "expected to find: " + 'basemaps). Use for spatial joins, overlays, CRS transforms, area/distance, maps.'[:80]


def test_signal_132():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/geopandas-geospatial/SKILL.md')
    assert 'ops (buffer, simplify, centroid, affine), spatial analysis (joins, overlays,' in text, "expected to find: " + 'ops (buffer, simplify, centroid, affine), spatial analysis (joins, overlays,'[:80]


def test_signal_133():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/geopandas-geospatial/SKILL.md')
    assert '(Shapefile, GeoJSON, GeoPackage, Parquet, PostGIS), CRS handling, geometric' in text, "expected to find: " + '(Shapefile, GeoJSON, GeoPackage, Parquet, PostGIS), CRS handling, geometric'[:80]


def test_signal_134():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/hypogenic-hypothesis-generation/SKILL.md')
    assert 'description: "LLM-driven hypothesis generation/testing on tabular data. Three methods: HypoGeniC (data-driven), HypoRefine (literature+data), Union. Iterative refinement, Redis caching, multi-hypothes' in text, "expected to find: " + 'description: "LLM-driven hypothesis generation/testing on tabular data. Three methods: HypoGeniC (data-driven), HypoRefine (literature+data), Union. Iterative refinement, Redis caching, multi-hypothes'[:80]


def test_signal_135():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/matlab-scientific-computing/SKILL.md')
    assert 'description: "MATLAB/GNU Octave numerical computing: matrices, linear algebra, ODEs, signal processing, optimization, statistics, scientific visualization. MATLAB-syntax examples run on both. For Pyth' in text, "expected to find: " + 'description: "MATLAB/GNU Octave numerical computing: matrices, linear algebra, ODEs, signal processing, optimization, statistics, scientific visualization. MATLAB-syntax examples run on both. For Pyth'[:80]


def test_signal_136():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/networkx-graph-analysis/SKILL.md')
    assert 'description: "Graph and network analysis toolkit. Four graph types (directed, undirected, multi-edge), centrality, shortest paths, community detection, generators, I/O (GraphML, GML, edge list), matpl' in text, "expected to find: " + 'description: "Graph and network analysis toolkit. Four graph types (directed, undirected, multi-edge), centrality, shortest paths, community detection, generators, I/O (GraphML, GML, edge list), matpl'[:80]


def test_signal_137():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/neurokit2/SKILL.md')
    assert 'description: "Python toolkit for neurophysiological signal processing: ECG (HR, HRV, R-peaks), EEG (complexity, PSD), EMG (activation onset), EDA/GSR (SCR decomposition), PPG, and RSP. Includes synthe' in text, "expected to find: " + 'description: "Python toolkit for neurophysiological signal processing: ECG (HR, HRV, R-peaks), EEG (complexity, PSD), EMG (activation onset), EDA/GSR (SCR decomposition), PPG, and RSP. Includes synthe'[:80]


def test_signal_138():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/neuropixels-analysis/SKILL.md')
    assert 'description: "Pipeline for Neuropixels extracellular electrophysiology: probe geometry (ProbeInterface), Kilosort sorting via SpikeInterface, quality metrics, unit curation (ISI, firing rate, SNR), po' in text, "expected to find: " + 'description: "Pipeline for Neuropixels extracellular electrophysiology: probe geometry (ProbeInterface), Kilosort sorting via SpikeInterface, quality metrics, unit curation (ISI, firing rate, SNR), po'[:80]


def test_signal_139():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/nextflow-workflow-engine/SKILL.md')
    assert 'description: "Dataflow workflow engine for scalable bioinformatics pipelines. Defines processes (containerized tasks) connected by channels; runs local, HPC (SLURM/SGE), cloud (AWS/GCP/Azure), or Kube' in text, "expected to find: " + 'description: "Dataflow workflow engine for scalable bioinformatics pipelines. Defines processes (containerized tasks) connected by channels; runs local, HPC (SLURM/SGE), cloud (AWS/GCP/Azure), or Kube'[:80]


def test_signal_140():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/polars-dataframes/SKILL.md')
    assert 'pushdown. Reads CSV, Parquet, JSON, Excel, DBs, cloud. Larger-than-RAM: Dask; GPU: cuDF.' in text, "expected to find: " + 'pushdown. Reads CSV, Parquet, JSON, Excel, DBs, cloud. Larger-than-RAM: Dask; GPU: cuDF.'[:80]


def test_signal_141():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/polars-dataframes/SKILL.md')
    assert 'select, filter, group_by, joins, pivots, window. Lazy mode enables predicate/projection' in text, "expected to find: " + 'select, filter, group_by, joins, pivots, window. Lazy mode enables predicate/projection'[:80]


def test_signal_142():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/polars-dataframes/SKILL.md')
    assert 'Fast in-memory DataFrame with lazy evaluation, parallel execution, Arrow backend.' in text, "expected to find: " + 'Fast in-memory DataFrame with lazy evaluation, parallel execution, Arrow backend.'[:80]


def test_signal_143():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/pymatgen/SKILL.md')
    assert 'description: "Python Materials Genomics library for structure analysis, thermodynamics, and electronic properties. Parse/create crystal structures (CIF, POSCAR), query Materials Project for DFT-comput' in text, "expected to find: " + 'description: "Python Materials Genomics library for structure analysis, thermodynamics, and electronic properties. Parse/create crystal structures (CIF, POSCAR), query Materials Project for DFT-comput'[:80]


def test_signal_144():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/pymoo/SKILL.md')
    assert 'description: "Python framework for single- and multi-objective optimization with evolutionary algorithms. Define vectorized objectives and constraints; solve with NSGA-II, NSGA-III, MOEA/D, GAs, or di' in text, "expected to find: " + 'description: "Python framework for single- and multi-objective optimization with evolutionary algorithms. Define vectorized objectives and constraints; solve with NSGA-II, NSGA-III, MOEA/D, GAs, or di'[:80]


def test_signal_145():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/simpy-discrete-event-simulation/SKILL.md')
    assert 'description: "Process-based discrete-event simulation. Model queues, shared resources, timed events: manufacturing, service ops, network traffic, logistics. Processes are Python generators yielding ev' in text, "expected to find: " + 'description: "Process-based discrete-event simulation. Model queues, shared resources, timed events: manufacturing, service ops, network traffic, logistics. Processes are Python generators yielding ev'[:80]


def test_signal_146():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/snakemake-workflow-engine/SKILL.md')
    assert 'description: "Python-based workflow manager for reproducible, scalable pipelines. Define rules with file-based dependencies; Snakemake resolves execution order and parallelism. Runs local, SLURM, LSF,' in text, "expected to find: " + 'description: "Python-based workflow manager for reproducible, scalable pipelines. Define rules with file-based dependencies; Snakemake resolves execution order and parallelism. Runs local, SLURM, LSF,'[:80]


def test_signal_147():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/spikeinterface-electrophysiology/SKILL.md')
    assert 'description: "Unified Python framework for extracellular electrophysiology. Load 20+ formats (SpikeGLX, OpenEphys, NWB, Intan, Maxwell, Blackrock), preprocess, run 10+ sorters (Kilosort4, SpykingCircu' in text, "expected to find: " + 'description: "Unified Python framework for extracellular electrophysiology. Load 20+ formats (SpikeGLX, OpenEphys, NWB, Intan, Maxwell, Blackrock), preprocess, run 10+ sorters (Kilosort4, SpykingCircu'[:80]


def test_signal_148():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/sympy-symbolic-math/SKILL.md')
    assert 'description: "Symbolic math in Python: exact algebra, calculus (derivatives, integrals, limits), equation solving, symbolic matrices, ODEs, code gen (lambdify, C/Fortran). Use for exact symbolic resul' in text, "expected to find: " + 'description: "Symbolic math in Python: exact algebra, calculus (derivatives, integrals, limits), equation solving, symbolic matrices, ODEs, code gen (lambdify, C/Fortran). Use for exact symbolic resul'[:80]


def test_signal_149():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/torch-geometric-graph-neural-networks/SKILL.md')
    assert 'description: "PyTorch Geometric (PyG) for graph neural networks: node/graph classification, link prediction with GCN, GAT, GraphSAGE, GIN. Message passing, mini-batches, heterogeneous graphs, neighbor' in text, "expected to find: " + 'description: "PyTorch Geometric (PyG) for graph neural networks: node/graph classification, link prediction with GCN, GAT, GraphSAGE, GIN. Message passing, mini-batches, heterogeneous graphs, neighbor'[:80]


def test_signal_150():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/transformers-bio-nlp/SKILL.md')
    assert 'description: "HuggingFace Transformers with biomedical LMs (BioBERT, PubMedBERT, BioGPT, BioMedLM) for scientific NLP: NER (genes, diseases, chemicals), relation extraction, QA, text classification, a' in text, "expected to find: " + 'description: "HuggingFace Transformers with biomedical LMs (BioBERT, PubMedBERT, BioGPT, BioMedLM) for scientific NLP: NER (genes, diseases, chemicals), relation extraction, QA, text classification, a'[:80]


def test_signal_151():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/umap-learn/SKILL.md')
    assert '(temporal/batch). 15+ distance metrics, custom Numba metrics, precomputed distances.' in text, "expected to find: " + '(temporal/batch). 15+ distance metrics, custom Numba metrics, precomputed distances.'[:80]


def test_signal_152():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/umap-learn/SKILL.md')
    assert 'For linear reduction use PCA; for neighborhood graphs use sklearn NearestNeighbors.' in text, "expected to find: " + 'For linear reduction use PCA; for neighborhood graphs use sklearn NearestNeighbors.'[:80]


def test_signal_153():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/umap-learn/SKILL.md')
    assert 'Parametric UMAP (NN encoder/decoder, TensorFlow), DensMAP (density), AlignedUMAP' in text, "expected to find: " + 'Parametric UMAP (NN encoder/decoder, TensorFlow), DensMAP (density), AlignedUMAP'[:80]


def test_signal_154():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/uspto-database/SKILL.md')
    assert 'description: "Access USPTO patent data via PatentsView REST API and Google Patents Public Data (BigQuery). Search by inventor, assignee, CPC, or keywords; download metadata and claims; analyze portfol' in text, "expected to find: " + 'description: "Access USPTO patent data via PatentsView REST API and Google Patents Public Data (BigQuery). Search by inventor, assignee, CPC, or keywords; download metadata and claims; analyze portfol'[:80]


def test_signal_155():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/vaex-dataframes/SKILL.md')
    assert 'GCS, Azure). Built-in ML transformers (scaling, PCA, K-means). In-memory: polars; distributed: dask.' in text, "expected to find: " + 'GCS, Azure). Built-in ML transformers (scaling, PCA, K-means). In-memory: polars; distributed: dask.'[:80]


def test_signal_156():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/vaex-dataframes/SKILL.md')
    assert 'Out-of-core DataFrame for billion-row data via lazy evaluation and memory-mapped files.' in text, "expected to find: " + 'Out-of-core DataFrame for billion-row data via lazy evaluation and memory-mapped files.'[:80]


def test_signal_157():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/vaex-dataframes/SKILL.md')
    assert 'Use when data exceeds RAM (10 GB–TB) for fast aggregation, filtering, virtual columns,' in text, "expected to find: " + 'Use when data exceeds RAM (10 GB–TB) for fast aggregation, filtering, virtual columns,'[:80]


def test_signal_158():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/zarr-python/SKILL.md')
    assert 'description: "Chunked N-D arrays with compression and cloud storage. NumPy-style indexing. Backends: local, S3, GCS, ZIP, memory. Dask/Xarray integration for parallel and labeled computation. For line' in text, "expected to find: " + 'description: "Chunked N-D arrays with compression and cloud storage. NumPy-style indexing. Backends: local, S3, GCS, ZIP, memory. Dask/Xarray integration for parallel and labeled computation. For line'[:80]


def test_signal_159():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/biorxiv-database/SKILL.md')
    assert 'description: "Query bioRxiv/medRxiv preprints via REST API. Search by DOI, category, or date range; retrieve metadata (title, abstract, authors, category, DOI, version history) and PDFs. No auth. For ' in text, "expected to find: " + 'description: "Query bioRxiv/medRxiv preprints via REST API. Search by DOI, category, or date range; retrieve metadata (title, abstract, authors, category, DOI, version history) and PDFs. No auth. For '[:80]


def test_signal_160():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/cancer-research-figure-guide/SKILL.md')
    assert 'description: "Cancer Research (AACR) figures: resolution (300-1200 DPI), formats (EPS/TIFF/AI), hierarchical panel labels (Ai, Aii, Bi), figure/table limits, legend requirements with replicate counts.' in text, "expected to find: " + 'description: "Cancer Research (AACR) figures: resolution (300-1200 DPI), formats (EPS/TIFF/AI), hierarchical panel labels (Ai, Aii, Bi), figure/table limits, legend requirements with replicate counts.'[:80]


def test_signal_161():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/cell-figure-guide/SKILL.md')
    assert 'description: "Cell (Cell Press) figure preparation: resolution (300-1000 DPI), formats (TIFF/PDF), RGB color, Avenir/Arial fonts, uppercase panel labels, strict image manipulation policies."' in text, "expected to find: " + 'description: "Cell (Cell Press) figure preparation: resolution (300-1000 DPI), formats (TIFF/PDF), RGB color, Avenir/Arial fonts, uppercase panel labels, strict image manipulation policies."'[:80]


def test_signal_162():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/citation-management/SKILL.md')
    assert 'description: "Selecting a reference manager and applying citation styles. Compares Zotero, Mendeley, EndNote, Paperpile; covers APA/Vancouver/ACS/Nature styles, DOI management, citation tracking, and ' in text, "expected to find: " + 'description: "Selecting a reference manager and applying citation styles. Compares Zotero, Mendeley, EndNote, Paperpile; covers APA/Vancouver/ACS/Nature styles, DOI management, citation tracking, and '[:80]


def test_signal_163():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/elife-figure-guide/SKILL.md')
    assert 'description: "eLife figure preparation: file formats (TIFF/EPS/PDF), striking image requirements (1800x900 px), figure supplement naming, and image screening policy treating selective enhancement as m' in text, "expected to find: " + 'description: "eLife figure preparation: file formats (TIFF/EPS/PDF), striking image requirements (1800x900 px), figure supplement naming, and image screening policy treating selective enhancement as m'[:80]


def test_signal_164():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/general-figure-guide/SKILL.md')
    assert 'description: "Universal QA checklist for generated scientific plots: overlapping labels, clipped text, missing axes/legends, overcrowded data, and cross-journal resolution/format guidance."' in text, "expected to find: " + 'description: "Universal QA checklist for generated scientific plots: overlapping labels, clipped text, missing axes/legends, overcrowded data, and cross-journal resolution/format guidance."'[:80]


def test_signal_165():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/lancet-figure-guide/SKILL.md')
    assert 'description: "The Lancet figure preparation: resolution (300+ DPI at 120%), preferred editable formats (PowerPoint/Word/SVG), column widths (75/154 mm), Times New Roman, in-house redraw policy."' in text, "expected to find: " + 'description: "The Lancet figure preparation: resolution (300+ DPI at 120%), preferred editable formats (PowerPoint/Word/SVG), column widths (75/154 mm), Times New Roman, in-house redraw policy."'[:80]


def test_signal_166():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/latex-research-posters/SKILL.md')
    assert 'description: "Research posters in LaTeX using beamerposter, tikzposter, or baposter. Layout, typography, color schemes, figure integration, accessibility, and QA for conferences. Includes templates. F' in text, "expected to find: " + 'description: "Research posters in LaTeX using beamerposter, tikzposter, or baposter. Layout, typography, color schemes, figure integration, accessibility, and QA for conferences. Includes templates. F'[:80]


def test_signal_167():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/literature-review/SKILL.md')
    assert 'description: "Conducting systematic, scoping, and narrative literature reviews. Covers PRISMA/PRISMA-ScR protocols, search strategy (Boolean, MeSH), database selection (PubMed, Scopus, Web of Science,' in text, "expected to find: " + 'description: "Conducting systematic, scoping, and narrative literature reviews. Covers PRISMA/PRISMA-ScR protocols, search strategy (Boolean, MeSH), database selection (PubMed, Scopus, Web of Science,'[:80]


def test_signal_168():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/nature-figure-guide/SKILL.md')
    assert 'description: "Nature figure preparation: resolution (300+ DPI), formats (AI/EPS/TIFF), RGB color, Helvetica/Arial fonts, lowercase panel labels, image integrity requirements."' in text, "expected to find: " + 'description: "Nature figure preparation: resolution (300+ DPI), formats (AI/EPS/TIFF), RGB color, Helvetica/Arial fonts, lowercase panel labels, image integrity requirements."'[:80]


def test_signal_169():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/nejm-figure-guide/SKILL.md')
    assert 'description: "NEJM figure preparation: resolution (300-1200 DPI), editable vector formats (AI/EPS/SVG), in-house medical illustration policy, and strict image integrity requirements."' in text, "expected to find: " + 'description: "NEJM figure preparation: resolution (300-1200 DPI), editable vector formats (AI/EPS/SVG), in-house medical illustration policy, and strict image integrity requirements."'[:80]


def test_signal_170():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/openalex-database/SKILL.md')
    assert 'description: "Query OpenAlex REST API for 250M+ scholarly works, authors, institutions, journals, concepts. Search by keyword, author, DOI, ORCID, or ID; filter by year, OA, citations, field; retrieve' in text, "expected to find: " + 'description: "Query OpenAlex REST API for 250M+ scholarly works, authors, institutions, journals, concepts. Search by keyword, author, DOI, ORCID, or ID; filter by year, OA, citations, field; retrieve'[:80]


def test_signal_171():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/peer-review-methodology/SKILL.md')
    assert 'description: "Structured peer review of manuscripts and grants. 7-stage evaluation: initial assessment, section review, statistical rigor, reproducibility, figure integrity, ethics, writing. Covers CO' in text, "expected to find: " + 'description: "Structured peer review of manuscripts and grants. 7-stage evaluation: initial assessment, section review, statistical rigor, reproducibility, figure integrity, ethics, writing. Covers CO'[:80]


def test_signal_172():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/pnas-figure-guide/SKILL.md')
    assert 'description: "PNAS figure preparation: resolution (300-1000 PPI), formats (TIFF/EPS/PDF), strict RGB-only color, Arial/Helvetica fonts, italicized uppercase panel labels, automated image screening."' in text, "expected to find: " + 'description: "PNAS figure preparation: resolution (300-1000 PPI), formats (TIFF/EPS/PDF), strict RGB-only color, Arial/Helvetica fonts, italicized uppercase panel labels, automated image screening."'[:80]


def test_signal_173():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/science-figure-guide/SKILL.md')
    assert 'description: "Science (AAAS) figure preparation: resolution (150-300+ DPI), formats (PDF/EPS/TIFF), RGB color, Myriad/Helvetica fonts, strict image manipulation policies including gamma adjustment dis' in text, "expected to find: " + 'description: "Science (AAAS) figure preparation: resolution (150-300+ DPI), formats (PDF/EPS/TIFF), RGB color, Myriad/Helvetica fonts, strict image manipulation policies including gamma adjustment dis'[:80]


def test_signal_174():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/scientific-brainstorming/SKILL.md')
    assert 'description: "Structured ideation methods: SCAMPER, Six Thinking Hats, Morphological Analysis, TRIZ, Biomimicry, plus more. Decision framework for picking methods by challenge type (stuck, improving, ' in text, "expected to find: " + 'description: "Structured ideation methods: SCAMPER, Six Thinking Hats, Morphological Analysis, TRIZ, Biomimicry, plus more. Decision framework for picking methods by challenge type (stuck, improving, '[:80]


def test_signal_175():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/scientific-critical-thinking/SKILL.md')
    assert 'description: "Evaluating scientific evidence and claims. Covers study design hierarchy (RCT to expert opinion), effect sizes (OR, RR, NNT, Cohen\'s d), confounding, p-value vs clinical significance, GR' in text, "expected to find: " + 'description: "Evaluating scientific evidence and claims. Covers study design hierarchy (RCT to expert opinion), effect sizes (OR, RR, NNT, Cohen\'s d), confounding, p-value vs clinical significance, GR'[:80]


def test_signal_176():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/scientific-literature-search/SKILL.md')
    assert 'description: "Systematic strategies for searching scientific literature across PubMed, arXiv, Google Scholar, and AI-assisted tools. Covers PICO framework for clinical questions, three-tiered search (' in text, "expected to find: " + 'description: "Systematic strategies for searching scientific literature across PubMed, arXiv, Google Scholar, and AI-assisted tools. Covers PICO framework for clinical questions, three-tiered search ('[:80]


def test_signal_177():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/scientific-manuscript-writing/SKILL.md')
    assert 'description: "Scientific manuscript writing: IMRAD, citation styles (APA/AMA/Vancouver/IEEE), figures/tables, reporting guidelines (CONSORT/STROBE/PRISMA/ARRIVE), writing principles (clarity/concisene' in text, "expected to find: " + 'description: "Scientific manuscript writing: IMRAD, citation styles (APA/AMA/Vancouver/IEEE), figures/tables, reporting guidelines (CONSORT/STROBE/PRISMA/ARRIVE), writing principles (clarity/concisene'[:80]


def test_signal_178():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/scientific-schematics/SKILL.md')
    assert 'description: "Designing scientific schematics, diagrams, and graphical abstracts. Covers tool selection (BioRender, Inkscape, Affinity, PowerPoint), design principles for pathway diagrams, mechanism s' in text, "expected to find: " + 'description: "Designing scientific schematics, diagrams, and graphical abstracts. Covers tool selection (BioRender, Inkscape, Affinity, PowerPoint), design principles for pathway diagrams, mechanism s'[:80]


def test_signal_179():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-writing/scientific-slides/SKILL.md')
    assert 'description: "Scientific presentations for conferences, seminars, thesis defenses, and grant pitches. Slide design, talk structure, timing, data viz for slides, QA. PowerPoint and LaTeX Beamer. For po' in text, "expected to find: " + 'description: "Scientific presentations for conferences, seminars, thesis defenses, and grant pitches. Slide design, talk structure, timing, data viz for slides, QA. PowerPoint and LaTeX Beamer. For po'[:80]


def test_signal_180():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/alphafold-database-access/SKILL.md')
    assert 'analyze pLDDT/PAE, bulk-fetch proteomes via Google Cloud. For experimental structures' in text, "expected to find: " + 'analyze pLDDT/PAE, bulk-fetch proteomes via Google Cloud. For experimental structures'[:80]


def test_signal_181():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/alphafold-database-access/SKILL.md')
    assert "Access AlphaFold DB's 200M+ predicted structures by UniProt ID. Download PDB/mmCIF," in text, "expected to find: " + "Access AlphaFold DB's 200M+ predicted structures by UniProt ID. Download PDB/mmCIF,"[:80]


def test_signal_182():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/alphafold-database-access/SKILL.md')
    assert 'use PDB; for prediction use ColabFold or ESMFold.' in text, "expected to find: " + 'use PDB; for prediction use ColabFold or ESMFold.'[:80]


def test_signal_183():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/autodock-vina-docking/SKILL.md')
    assert 'description: "Molecular docking with AutoDock Vina (Python API). Receptor/ligand prep (Meeko + RDKit), grid box, docking, pose and binding energy analysis, and batch virtual screening."' in text, "expected to find: " + 'description: "Molecular docking with AutoDock Vina (Python API). Receptor/ligand prep (Meeko + RDKit), grid box, docking, pose and binding energy analysis, and batch virtual screening."'[:80]


def test_signal_184():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/chembl-database-bioactivity/SKILL.md')
    assert 'description: Query ChEMBL via Python SDK. Search compounds by structure/properties, retrieve bioactivity (IC50, Ki, EC50), find target inhibitors, run SAR, access drug mechanism/indication data.' in text, "expected to find: " + 'description: Query ChEMBL via Python SDK. Search compounds by structure/properties, retrieve bioactivity (IC50, Ki, EC50), find target inhibitors, run SAR, access drug mechanism/indication data.'[:80]


def test_signal_185():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/clinicaltrials-database-search/SKILL.md')
    assert 'description: Query ClinicalTrials.gov API v2 for trial data. Search by condition, drug/intervention, location, sponsor, or phase; fetch details by NCT ID; filter by status; paginate; export CSV. For c' in text, "expected to find: " + 'description: Query ClinicalTrials.gov API v2 for trial data. Search by condition, drug/intervention, location, sponsor, or phase; fetch details by NCT ID; filter by status; paginate; export CSV. For c'[:80]


def test_signal_186():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/dailymed-database/SKILL.md')
    assert 'description: "Query FDA drug labels (DailyMed) via REST API. Search structured product labels (SPLs) by name, NDC, set ID, or RxCUI; get indications, dosage, warnings, adverse reactions, packaging. No' in text, "expected to find: " + 'description: "Query FDA drug labels (DailyMed) via REST API. Search structured product labels (SPLs) by name, NDC, set ID, or RxCUI; get indications, dosage, warnings, adverse reactions, packaging. No'[:80]


def test_signal_187():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/datamol-cheminformatics/SKILL.md')
    assert 'Pythonic RDKit wrapper with sensible defaults for drug discovery. SMILES parsing,' in text, "expected to find: " + 'Pythonic RDKit wrapper with sensible defaults for drug discovery. SMILES parsing,'[:80]


def test_signal_188():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/datamol-cheminformatics/SKILL.md')
    assert 'standardization, descriptors, fingerprints, similarity, clustering, diversity' in text, "expected to find: " + 'standardization, descriptors, fingerprints, similarity, clustering, diversity'[:80]


def test_signal_189():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/datamol-cheminformatics/SKILL.md')
    assert 'selection, scaffold analysis, BRICS/RECAP fragmentation, 3D conformers, and' in text, "expected to find: " + 'selection, scaffold analysis, BRICS/RECAP fragmentation, 3D conformers, and'[:80]


def test_signal_190():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/ddinter-database/SKILL.md')
    assert 'description: "Query DDInter drug-drug interactions via REST API (1.7M+ interactions, 2,400+ drugs). Search by drug name/ID for severity (major/moderate/minor), mechanisms, and clinical recommendations' in text, "expected to find: " + 'description: "Query DDInter drug-drug interactions via REST API (1.7M+ interactions, 2,400+ drugs). Search by drug name/ID for severity (major/moderate/minor), mechanisms, and clinical recommendations'[:80]


def test_signal_191():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/deepchem/SKILL.md')
    assert 'description: "Deep learning for drug discovery. 60+ models (GCN, GAT, AttentiveFP, MPNN, ChemBERTa, GROVER), 50+ featurizers, MoleculeNet benchmarks, HPO, transfer learning. Unified load-featurize-spl' in text, "expected to find: " + 'description: "Deep learning for drug discovery. 60+ models (GCN, GAT, AttentiveFP, MPNN, ChemBERTa, GROVER), 50+ featurizers, MoleculeNet benchmarks, HPO, transfer learning. Unified load-featurize-spl'[:80]


def test_signal_192():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/diffdock/SKILL.md')
    assert 'description: "Diffusion-based docking that predicts protein-ligand poses without a predefined site. Use for blind docking, when traditional docking fails, or exploring multiple binding modes. Pipeline' in text, "expected to find: " + 'description: "Diffusion-based docking that predicts protein-ligand poses without a predefined site. Use for blind docking, when traditional docking fails, or exploring multiple binding modes. Pipeline'[:80]


def test_signal_193():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/drugbank-database-access/SKILL.md')
    assert 'description: "Parse local DrugBank XML for drug info, interactions, targets, and properties. Search by ID/name/CAS, extract DDIs with severity, map targets/enzymes/transporters, compute SMILES similar' in text, "expected to find: " + 'description: "Parse local DrugBank XML for drug info, interactions, targets, and properties. Search by ID/name/CAS, extract DDIs with severity, map targets/enzymes/transporters, compute SMILES similar'[:80]


def test_signal_194():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/emdb-database/SKILL.md')
    assert 'description: "Search EMDB cryo-EM density maps, fitted atomic models, and metadata via REST API. Query by keyword, resolution, method, or organism; fetch entries, map URLs, linked PDB models, and publ' in text, "expected to find: " + 'description: "Search EMDB cryo-EM density maps, fitted atomic models, and metadata via REST API. Query by keyword, resolution, method, or organism; fetch entries, map URLs, linked PDB models, and publ'[:80]


def test_signal_195():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/fda-database/SKILL.md')
    assert 'description: "Query openFDA REST API for adverse events (FAERS), labeling, product info, recalls, enforcement. Search by drug name, ingredient, MedDRA, or NDC. 1k req/day no key; 120k with free key. F' in text, "expected to find: " + 'description: "Query openFDA REST API for adverse events (FAERS), labeling, product info, recalls, enforcement. Search by drug name, ingredient, MedDRA, or NDC. 1k req/day no key; 120k with free key. F'[:80]


def test_signal_196():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/gtopdb-database/SKILL.md')
    assert 'description: "Query IUPHAR/BPS Guide to Pharmacology (GtoPdb) REST API for receptor-ligand interactions and affinity (pKi/pIC50/pEC50). Get ligand classes (drugs, biologics, natural products), target ' in text, "expected to find: " + 'description: "Query IUPHAR/BPS Guide to Pharmacology (GtoPdb) REST API for receptor-ligand interactions and affinity (pKi/pIC50/pEC50). Get ligand classes (drugs, biologics, natural products), target '[:80]


def test_signal_197():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/mdanalysis-trajectory/SKILL.md')
    assert 'description: "Analyze MD trajectories from GROMACS, AMBER, NAMD, CHARMM, LAMMPS. Reads topology/trajectory into Universe objects; supports RMSD, RMSF, radius of gyration, contact maps, H-bonds, PCA, a' in text, "expected to find: " + 'description: "Analyze MD trajectories from GROMACS, AMBER, NAMD, CHARMM, LAMMPS. Reads topology/trajectory into Universe objects; supports RMSD, RMSF, radius of gyration, contact maps, H-bonds, PCA, a'[:80]


def test_signal_198():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/medchem/SKILL.md')
    assert 'composition query language. Built on RDKit/datamol. For hit-to-lead filtering, library' in text, "expected to find: " + 'composition query language. Built on RDKit/datamol. For hit-to-lead filtering, library'[:80]


def test_signal_199():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/medchem/SKILL.md')
    assert 'design, ADMET pre-screening. For molecular I/O use rdkit-cheminformatics or datamol.' in text, "expected to find: " + 'design, ADMET pre-screening. For molecular I/O use rdkit-cheminformatics or datamol.'[:80]


def test_signal_200():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/medchem/SKILL.md')
    assert 'Medicinal chemistry filters for compound triage. Drug-likeness rules (Lipinski Ro5,' in text, "expected to find: " + 'Medicinal chemistry filters for compound triage. Drug-likeness rules (Lipinski Ro5,'[:80]


def test_signal_201():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/molfeat-molecular-featurization/SKILL.md')
    assert 'description: Molecular featurization hub (100+ featurizers) for ML. SMILES to fingerprints (ECFP, MACCS, MAP4), descriptors (RDKit 2D, Mordred), pretrained embeddings (ChemBERTa, GIN, Graphormer), pha' in text, "expected to find: " + 'description: Molecular featurization hub (100+ featurizers) for ML. SMILES to fingerprints (ECFP, MACCS, MAP4), descriptors (RDKit 2D, Mordred), pretrained embeddings (ChemBERTa, GIN, Graphormer), pha'[:80]


def test_signal_202():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/opentargets-database/SKILL.md')
    assert 'description: "Query Open Targets GraphQL API for target-disease associations, evidence, drug links, safety. Search targets by gene, diseases by EFO ID; scores from 20+ sources, drug mechanisms, tracta' in text, "expected to find: " + 'description: "Query Open Targets GraphQL API for target-disease associations, evidence, drug links, safety. Search targets by gene, diseases by EFO ID; scores from 20+ sources, drug mechanisms, tracta'[:80]


def test_signal_203():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/pdb-database/SKILL.md')
    assert 'description: "Query RCSB PDB (200K+ structures) via rcsb-api SDK. Text/attribute/sequence/3D similarity search; metadata via GraphQL; download PDB/mmCIF. For AlphaFold predictions use alphafold-databa' in text, "expected to find: " + 'description: "Query RCSB PDB (200K+ structures) via rcsb-api SDK. Text/attribute/sequence/3D similarity search; metadata via GraphQL; download PDB/mmCIF. For AlphaFold predictions use alphafold-databa'[:80]


def test_signal_204():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/pubchem-compound-search/SKILL.md')
    assert 'description: "Query PubChem (110M+ compounds) via PubChemPy/PUG-REST. Search by name/CID/SMILES, get properties (MW, LogP, TPSA), similarity/substructure search, bioactivity. For local cheminformatics' in text, "expected to find: " + 'description: "Query PubChem (110M+ compounds) via PubChemPy/PUG-REST. Search by name/CID/SMILES, get properties (MW, LogP, TPSA), similarity/substructure search, bioactivity. For local cheminformatics'[:80]


def test_signal_205():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/pytdc-therapeutics-data-commons/SKILL.md')
    assert 'toxicity, DTI, DDI with scaffold/cold splits, standardized metrics, molecular oracles,' in text, "expected to find: " + 'toxicity, DTI, DDI with scaffold/cold splits, standardized metrics, molecular oracles,'[:80]


def test_signal_206():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/pytdc-therapeutics-data-commons/SKILL.md')
    assert 'and ADMET benchmarks for therapeutic ML and property prediction. For chemical database' in text, "expected to find: " + 'and ADMET benchmarks for therapeutic ML and property prediction. For chemical database'[:80]


def test_signal_207():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/pytdc-therapeutics-data-commons/SKILL.md')
    assert 'Therapeutics Data Commons (TDC) AI-ready drug discovery datasets. Curated ADME,' in text, "expected to find: " + 'Therapeutics Data Commons (TDC) AI-ready drug discovery datasets. Curated ADME,'[:80]


def test_signal_208():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/rdkit-cheminformatics/SKILL.md')
    assert 'description: "Cheminformatics toolkit for molecular analysis and virtual screening: SMILES/SDF parsing, descriptors (MW, LogP, TPSA), fingerprints (Morgan/ECFP, MACCS), Tanimoto similarity, SMARTS sub' in text, "expected to find: " + 'description: "Cheminformatics toolkit for molecular analysis and virtual screening: SMILES/SDF parsing, descriptors (MW, LogP, TPSA), fingerprints (Morgan/ECFP, MACCS), Tanimoto similarity, SMARTS sub'[:80]


def test_signal_209():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/rowan/SKILL.md')
    assert 'description: "Cloud quantum chemistry platform with Python SDK. Run geometry optimization, conformer generation, torsional scans, and energy minimization (DFT/semiempirical), and retrieve properties (' in text, "expected to find: " + 'description: "Cloud quantum chemistry platform with Python SDK. Run geometry optimization, conformer generation, torsional scans, and energy minimization (DFT/semiempirical), and retrieve properties ('[:80]


def test_signal_210():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/sar-analysis/SKILL.md')
    assert 'description: "Structure-Activity Relationship (SAR) analysis with RDKit: scaffold detection via MCS, R-group decomposition, aligned visualization, activity heatmaps, interpretive SAR output. For gener' in text, "expected to find: " + 'description: "Structure-Activity Relationship (SAR) analysis with RDKit: scaffold detection via MCS, R-group decomposition, aligned visualization, activity heatmaps, interpretive SAR output. For gener'[:80]


def test_signal_211():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/torchdrug/SKILL.md')
    assert 'description: "PyTorch-based ML platform for drug discovery: graph molecular representation learning, property prediction (ADMET, activity), retrosynthesis, drug-target interaction (DTI), and pretraini' in text, "expected to find: " + 'description: "PyTorch-based ML platform for drug discovery: graph molecular representation learning, property prediction (ADMET, activity), retrosynthesis, drug-target interaction (DTI), and pretraini'[:80]


def test_signal_212():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/unichem-database/SKILL.md')
    assert 'description: "Cross-reference compound IDs across 50+ databases (ChEMBL, DrugBank, PubChem, ChEBI, PDB, KEGG) via UniChem REST API. Resolve InChIKeys to source IDs, find structurally related compounds' in text, "expected to find: " + 'description: "Cross-reference compound IDs across 50+ databases (ChEMBL, DrugBank, PubChem, ChEBI, PDB, KEGG) via UniChem REST API. Resolve InChIKeys to source IDs, find structurally related compounds'[:80]


def test_signal_213():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/structural-biology-drug-discovery/zinc-database/SKILL.md')
    assert 'description: "Query ZINC15/ZINC22 virtual compound libraries (1.4B compounds, 750M purchasable). Search lead/fragment/drug-like compounds by MW, logP, reactivity, or SMILES similarity; download 3D set' in text, "expected to find: " + 'description: "Query ZINC15/ZINC22 virtual compound libraries (1.4B compounds, 750M purchasable). Search lead/fragment/drug-like compounds by MW, logP, reactivity, or SMILES similarity; download 3D set'[:80]


def test_signal_214():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-biology-multiomics/brenda-database/SKILL.md')
    assert 'description: "BRENDA Enzyme DB SOAP/REST queries: kinetic parameters (Km, Vmax, kcat, Ki), EC classes, substrate specificity, inhibitors, cofactors, organism data. 80K+ enzymes, 7M+ values. Free acade' in text, "expected to find: " + 'description: "BRENDA Enzyme DB SOAP/REST queries: kinetic parameters (Km, Vmax, kcat, Ki), EC classes, substrate specificity, inhibitors, cofactors, organism data. 80K+ enzymes, 7M+ values. Free acade'[:80]


def test_signal_215():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-biology-multiomics/cellchat-cell-communication/SKILL.md')
    assert 'description: "Infer and visualize intercellular communication from scRNA-seq with CellChat (R). Build CellChat from Seurat/counts → subset CellChatDB ligand-receptor pairs → over-expressed genes per g' in text, "expected to find: " + 'description: "Infer and visualize intercellular communication from scRNA-seq with CellChat (R). Build CellChat from Seurat/counts → subset CellChatDB ligand-receptor pairs → over-expressed genes per g'[:80]


def test_signal_216():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-biology-multiomics/cobrapy-metabolic-modeling/SKILL.md')
    assert 'description: "Constraint-based (COBRA) analysis of genome-scale metabolic models: FBA, FVA, knockouts, flux sampling, production envelopes, gapfilling, media optimization. Use for strain design, essen' in text, "expected to find: " + 'description: "Constraint-based (COBRA) analysis of genome-scale metabolic models: FBA, FVA, knockouts, flux sampling, production envelopes, gapfilling, media optimization. Use for strain design, essen'[:80]


def test_signal_217():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-biology-multiomics/kegg-pathway-analysis/SKILL.md')
    assert 'description: "Guide to KEGG pathway enrichment for DEG results. Covers ORA vs GSEA, mandatory directionality splitting, KEGG organism codes, API failure handling with offline fallbacks, cross-conditio' in text, "expected to find: " + 'description: "Guide to KEGG pathway enrichment for DEG results. Covers ORA vs GSEA, mandatory directionality splitting, KEGG organism codes, API failure handling with offline fallbacks, cross-conditio'[:80]


def test_signal_218():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-biology-multiomics/lamindb-data-management/SKILL.md')
    assert 'description: "Open-source FAIR biology data framework. Version artifacts (AnnData, DataFrame, Zarr), track lineage, validate via ontologies (Bionty), query datasets. Integrates with Nextflow, Snakemak' in text, "expected to find: " + 'description: "Open-source FAIR biology data framework. Version artifacts (AnnData, DataFrame, Zarr), track lineage, validate via ontologies (Bionty), query datasets. Integrates with Nextflow, Snakemak'[:80]


def test_signal_219():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-biology-multiomics/libsbml-network-modeling/SKILL.md')
    assert 'description: "Build, read, validate, modify SBML biological network models via the libSBML Python API. SBML Levels 1–3, reactions/kinetic laws, species, rules, FBC extension for flux balance, conversi' in text, "expected to find: " + 'description: "Build, read, validate, modify SBML biological network models via the libSBML Python API. SBML Levels 1–3, reactions/kinetic laws, species, rules, FBC extension for flux balance, conversi'[:80]


def test_signal_220():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-biology-multiomics/mofaplus-multi-omics/SKILL.md')
    assert 'description: "Multi-Omics Factor Analysis v2 (MOFA+) with mofapy2. Jointly decompose omics layers (scRNA, ATAC, proteomics, methylation) into latent factors capturing major variation. Multi-group desi' in text, "expected to find: " + 'description: "Multi-Omics Factor Analysis v2 (MOFA+) with mofapy2. Jointly decompose omics layers (scRNA, ATAC, proteomics, methylation) into latent factors capturing major variation. Multi-group desi'[:80]


def test_signal_221():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-biology-multiomics/muon-multiomics-singlecell/SKILL.md')
    assert 'description: "Multi-modal single-cell analysis with muon/MuData. Joint RNA+ATAC (10x Multiome), CITE-seq (RNA+protein), other multi-omics. MuData holds per-modality AnnData with shared obs. WNN joint ' in text, "expected to find: " + 'description: "Multi-modal single-cell analysis with muon/MuData. Joint RNA+ATAC (10x Multiome), CITE-seq (RNA+protein), other multi-omics. MuData holds per-modality AnnData with shared obs. WNN joint '[:80]


def test_signal_222():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-biology-multiomics/omics-analysis-guide/SKILL.md')
    assert 'description: "Decision guide for omics analysis (transcriptomics, proteomics) using a three-tiered approach: validated pipelines first, standard workflows second, custom last. Covers QC, normalization' in text, "expected to find: " + 'description: "Decision guide for omics analysis (transcriptomics, proteomics) using a three-tiered approach: validated pipelines first, standard workflows second, custom last. Covers QC, normalization'[:80]


def test_signal_223():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-biology-multiomics/reactome-database/SKILL.md')
    assert 'description: "Query Reactome pathways via REST: pathway queries, entity lookup, keyword search, gene list enrichment, hierarchy, cross-refs. Content + Analysis services. Python wrapper: reactome2py. F' in text, "expected to find: " + 'description: "Query Reactome pathways via REST: pathway queries, entity lookup, keyword search, gene list enrichment, hierarchy, cross-refs. Content + Analysis services. Python wrapper: reactome2py. F'[:80]


def test_signal_224():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-biology-multiomics/string-database-ppi/SKILL.md')
    assert 'description: Query STRING REST API for PPIs (59M proteins, 20B interactions, 5000+ species). Retrieve networks, run GO/KEGG enrichment, find partners, test PPI significance, visualize networks, analyz' in text, "expected to find: " + 'description: Query STRING REST API for PPIs (59M proteins, 20B interactions, 5000+ species). Retrieve networks, run GO/KEGG enrichment, find partners, test PPI significance, visualize networks, analyz'[:80]

