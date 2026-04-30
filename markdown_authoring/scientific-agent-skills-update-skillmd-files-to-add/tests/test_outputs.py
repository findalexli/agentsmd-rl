"""Behavioral checks for scientific-agent-skills-update-skillmd-files-to-add (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/scientific-agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/alphafold-database/SKILL.md')
    assert 'description: "Access and analyze AlphaFold protein structure predictions from the DeepMind/EMBL-EBI database containing 200M+ AI-predicted protein structures. Use this skill for: retrieving protein st' in text, "expected to find: " + 'description: "Access and analyze AlphaFold protein structure predictions from the DeepMind/EMBL-EBI database containing 200M+ AI-predicted protein structures. Use this skill for: retrieving protein st'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/chembl-database/SKILL.md')
    assert 'description: "Comprehensive toolkit for accessing and querying the ChEMBL database, the world\'s largest manually curated repository of bioactive drug-like molecules. Use this skill when you need to: s' in text, "expected to find: " + 'description: "Comprehensive toolkit for accessing and querying the ChEMBL database, the world\'s largest manually curated repository of bioactive drug-like molecules. Use this skill when you need to: s'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/clinpgx-database/SKILL.md')
    assert 'description: "Comprehensive toolkit for accessing ClinPGx (Clinical Pharmacogenomics Database), the successor to PharmGKB providing clinical pharmacogenomics information on how genetic variation affec' in text, "expected to find: " + 'description: "Comprehensive toolkit for accessing ClinPGx (Clinical Pharmacogenomics Database), the successor to PharmGKB providing clinical pharmacogenomics information on how genetic variation affec'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/clinvar-database/SKILL.md')
    assert 'description: "Access and analyze ClinVar, NCBI\'s authoritative database of human genomic variants and their clinical significance classifications. Use this skill when: searching for pathogenic, benign' in text, "expected to find: " + 'description: "Access and analyze ClinVar, NCBI\'s authoritative database of human genomic variants and their clinical significance classifications. Use this skill when: searching for pathogenic, benign'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/cosmic-database/SKILL.md')
    assert 'description: "Access and analyze COSMIC (Catalogue of Somatic Mutations in Cancer), the world\'s largest database of somatic cancer mutations. Use this skill for downloading cancer mutation datasets, a' in text, "expected to find: " + 'description: "Access and analyze COSMIC (Catalogue of Somatic Mutations in Cancer), the world\'s largest database of somatic cancer mutations. Use this skill for downloading cancer mutation datasets, a'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/ena-database/SKILL.md')
    assert 'description: "Comprehensive toolkit for accessing, searching, and retrieving data from the European Nucleotide Archive (ENA) - the primary European repository for nucleotide sequence data. Provides pr' in text, "expected to find: " + 'description: "Comprehensive toolkit for accessing, searching, and retrieving data from the European Nucleotide Archive (ENA) - the primary European repository for nucleotide sequence data. Provides pr'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/ensembl-database/SKILL.md')
    assert 'description: "Access and query the Ensembl genome database for comprehensive vertebrate genomic data analysis. Use this skill for gene lookups, sequence retrieval, variant analysis, comparative genomi' in text, "expected to find: " + 'description: "Access and query the Ensembl genome database for comprehensive vertebrate genomic data analysis. Use this skill for gene lookups, sequence retrieval, variant analysis, comparative genomi'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/gene-database/SKILL.md')
    assert 'description: "Access and query NCBI Gene database programmatically using E-utilities and Datasets API. Search genes by symbol, name, ID, or biological context across organisms. Retrieve comprehensive ' in text, "expected to find: " + 'description: "Access and query NCBI Gene database programmatically using E-utilities and Datasets API. Search genes by symbol, name, ID, or biological context across organisms. Retrieve comprehensive '[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/geo-database/SKILL.md')
    assert 'description: "Work with the Gene Expression Omnibus (GEO) database to search, retrieve, download, and analyze high-throughput gene expression and functional genomics data. Use this skill for microarra' in text, "expected to find: " + 'description: "Work with the Gene Expression Omnibus (GEO) database to search, retrieve, download, and analyze high-throughput gene expression and functional genomics data. Use this skill for microarra'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/gwas-database/SKILL.md')
    assert 'description: "Comprehensive toolkit for accessing and querying the GWAS Catalog (NHGRI-EBI database of published genome-wide association studies). Use this skill when you need to: find genetic variant' in text, "expected to find: " + 'description: "Comprehensive toolkit for accessing and querying the GWAS Catalog (NHGRI-EBI database of published genome-wide association studies). Use this skill when you need to: find genetic variant'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/hmdb-database/SKILL.md')
    assert 'description: "Access and analyze the Human Metabolome Database (HMDB) for comprehensive metabolite information, metabolomics research, biomarker discovery, metabolite identification, pathway analysis,' in text, "expected to find: " + 'description: "Access and analyze the Human Metabolome Database (HMDB) for comprehensive metabolite information, metabolomics research, biomarker discovery, metabolite identification, pathway analysis,'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/kegg-database/SKILL.md')
    assert 'description: "Access and analyze the KEGG (Kyoto Encyclopedia of Genes and Genomes) database for comprehensive biological pathway analysis, molecular interaction networks, and cross-database integrati' in text, "expected to find: " + 'description: "Access and analyze the KEGG (Kyoto Encyclopedia of Genes and Genomes) database for comprehensive biological pathway analysis, molecular interaction networks, and cross-database integrati'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/metabolomics-workbench-database/SKILL.md')
    assert 'description: "Comprehensive toolkit for accessing and analyzing metabolomics data through the Metabolomics Workbench REST API. This NIH-sponsored repository contains 4,200+ metabolomics studies with s' in text, "expected to find: " + 'description: "Comprehensive toolkit for accessing and analyzing metabolomics data through the Metabolomics Workbench REST API. This NIH-sponsored repository contains 4,200+ metabolomics studies with s'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/pdb-database/SKILL.md')
    assert 'description: "Access and analyze the RCSB Protein Data Bank (PDB) - the global repository for 3D structural data of biological macromolecules including proteins, nucleic acids, complexes, and ligands.' in text, "expected to find: " + 'description: "Access and analyze the RCSB Protein Data Bank (PDB) - the global repository for 3D structural data of biological macromolecules including proteins, nucleic acids, complexes, and ligands.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/pubchem-database/SKILL.md')
    assert 'description: "Access and analyze chemical compound data from PubChem database using PubChemPy and PUG-REST API. Use this skill when you need to: search compounds by name/CID/SMILES/InChI/formula, retr' in text, "expected to find: " + 'description: "Access and analyze chemical compound data from PubChem database using PubChemPy and PUG-REST API. Use this skill when you need to: search compounds by name/CID/SMILES/InChI/formula, retr'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/pubmed-database/SKILL.md')
    assert 'description: "Comprehensive PubMed database expertise for searching, retrieving, and analyzing biomedical research literature. Use for literature searches, systematic reviews, meta-analyses, citation ' in text, "expected to find: " + 'description: "Comprehensive PubMed database expertise for searching, retrieving, and analyzing biomedical research literature. Use for literature searches, systematic reviews, meta-analyses, citation '[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/reactome-database/reactome-database/SKILL.md')
    assert 'description: "Comprehensive Reactome pathway database integration for biological pathway analysis, enrichment studies, molecular interaction queries, and gene expression analysis. Use this skill for p' in text, "expected to find: " + 'description: "Comprehensive Reactome pathway database integration for biological pathway analysis, enrichment studies, molecular interaction queries, and gene expression analysis. Use this skill for p'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/string-database/SKILL.md')
    assert 'description: "Access and analyze the STRING database for comprehensive protein-protein interaction (PPI) network analysis, functional enrichment, pathway analysis, and protein interaction discovery. T' in text, "expected to find: " + 'description: "Access and analyze the STRING database for comprehensive protein-protein interaction (PPI) network analysis, functional enrichment, pathway analysis, and protein interaction discovery. T'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/uniprot-database/SKILL.md')
    assert 'description: "Access and query the UniProt protein database for comprehensive protein information retrieval. Use this skill when you need to search for proteins by name, gene symbol, accession number,' in text, "expected to find: " + 'description: "Access and query the UniProt protein database for comprehensive protein information retrieval. Use this skill when you need to search for proteins by name, gene symbol, accession number,'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-databases/zinc-database/SKILL.md')
    assert 'description: "Access and query the ZINC database containing 230+ million commercially-available compounds for virtual screening, drug discovery, and molecular docking studies. Use this skill when you ' in text, "expected to find: " + 'description: "Access and query the ZINC database containing 230+ million commercially-available compounds for virtual screening, drug discovery, and molecular docking studies. Use this skill when you '[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/anndata/SKILL.md')
    assert 'description: "Comprehensive AnnData (Annotated Data) manipulation for single-cell genomics, multi-omics, and structured scientific datasets. Use this skill for: loading/saving .h5ad files, creating An' in text, "expected to find: " + 'description: "Comprehensive AnnData (Annotated Data) manipulation for single-cell genomics, multi-omics, and structured scientific datasets. Use this skill for: loading/saving .h5ad files, creating An'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/arboreto/SKILL.md')
    assert 'description: "Python toolkit for gene regulatory network (GRN) inference from gene expression data using machine learning algorithms. Use this skill for inferring transcription factor-target gene rela' in text, "expected to find: " + 'description: "Python toolkit for gene regulatory network (GRN) inference from gene expression data using machine learning algorithms. Use this skill for inferring transcription factor-target gene rela'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/astropy/SKILL.md')
    assert 'description: "Expert guidance for astronomical data analysis using the astropy Python library. Use this skill for FITS file operations (reading, writing, inspecting, modifying), coordinate transformat' in text, "expected to find: " + 'description: "Expert guidance for astronomical data analysis using the astropy Python library. Use this skill for FITS file operations (reading, writing, inspecting, modifying), coordinate transformat'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/biomni/SKILL.md')
    assert 'description: "Use this skill for autonomous biomedical research execution across genomics, proteomics, drug discovery, and computational biology. Biomni is an AI agent that combines LLM reasoning with' in text, "expected to find: " + 'description: "Use this skill for autonomous biomedical research execution across genomics, proteomics, drug discovery, and computational biology. Biomni is an AI agent that combines LLM reasoning with'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/biopython/SKILL.md')
    assert 'description: "Use BioPython for computational molecular biology and bioinformatics tasks. Essential for: sequence manipulation (DNA/RNA/protein transcription, translation, complement, reverse compleme' in text, "expected to find: " + 'description: "Use BioPython for computational molecular biology and bioinformatics tasks. Essential for: sequence manipulation (DNA/RNA/protein transcription, translation, complement, reverse compleme'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/bioservices/SKILL.md')
    assert 'description: "Python toolkit for programmatic access to 40+ biological web services and databases including UniProt, KEGG, ChEBI, ChEMBL, PubChem, NCBI BLAST, PSICQUIC, QuickGO, BioMart, ArrayExpress,' in text, "expected to find: " + 'description: "Python toolkit for programmatic access to 40+ biological web services and databases including UniProt, KEGG, ChEBI, ChEMBL, PubChem, NCBI BLAST, PSICQUIC, QuickGO, BioMart, ArrayExpress,'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/cellxgene-census/SKILL.md')
    assert 'description: "Access, query, and analyze single-cell genomics data from the CZ CELLxGENE Census containing 61+ million cells from human and mouse. Use this skill for single-cell RNA-seq analysis, cell' in text, "expected to find: " + 'description: "Access, query, and analyze single-cell genomics data from the CZ CELLxGENE Census containing 61+ million cells from human and mouse. Use this skill for single-cell RNA-seq analysis, cell'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/cobrapy/SKILL.md')
    assert 'description: "Python library for constraint-based reconstruction and analysis (COBRA) of metabolic models. Essential for systems biology, metabolic engineering, and computational biology tasks involvi' in text, "expected to find: " + 'description: "Python library for constraint-based reconstruction and analysis (COBRA) of metabolic models. Essential for systems biology, metabolic engineering, and computational biology tasks involvi'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/dask/SKILL.md')
    assert 'description: "Toolkit for parallel and distributed computing in Python enabling larger-than-memory operations, parallel processing, and distributed computation. Use this skill when: (1) datasets excee' in text, "expected to find: " + 'description: "Toolkit for parallel and distributed computing in Python enabling larger-than-memory operations, parallel processing, and distributed computation. Use this skill when: (1) datasets excee'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/datamol/SKILL.md')
    assert 'description: "Complete molecular cheminformatics toolkit using datamol (Pythonic RDKit wrapper). Use for SMILES parsing/conversion, molecular standardization/sanitization, descriptor calculation, fing' in text, "expected to find: " + 'description: "Complete molecular cheminformatics toolkit using datamol (Pythonic RDKit wrapper). Use for SMILES parsing/conversion, molecular standardization/sanitization, descriptor calculation, fing'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/deepchem/SKILL.md')
    assert 'description: "DeepChem toolkit for molecular machine learning, drug discovery, and materials science. Use for: molecular property prediction (solubility, toxicity, ADMET, binding affinity, drug-likene' in text, "expected to find: " + 'description: "DeepChem toolkit for molecular machine learning, drug discovery, and materials science. Use for: molecular property prediction (solubility, toxicity, ADMET, binding affinity, drug-likene'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/deeptools/SKILL.md')
    assert 'description: "deepTools is a comprehensive Python toolkit for analyzing next-generation sequencing (NGS) data including ChIP-seq, RNA-seq, ATAC-seq, MNase-seq, and other genomic experiments. Use this ' in text, "expected to find: " + 'description: "deepTools is a comprehensive Python toolkit for analyzing next-generation sequencing (NGS) data including ChIP-seq, RNA-seq, ATAC-seq, MNase-seq, and other genomic experiments. Use this '[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/diffdock/SKILL.md')
    assert 'description: "This skill provides comprehensive guidance for using DiffDock, a state-of-the-art diffusion-based deep learning tool for molecular docking that predicts 3D binding poses of small molecul' in text, "expected to find: " + 'description: "This skill provides comprehensive guidance for using DiffDock, a state-of-the-art diffusion-based deep learning tool for molecular docking that predicts 3D binding poses of small molecul'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/etetoolkit/SKILL.md')
    assert 'description: "Expert toolkit for phylogenetic and hierarchical tree analysis using ETE (Environment for Tree Exploration). Use this skill for any tree-related bioinformatics tasks including phylogenet' in text, "expected to find: " + 'description: "Expert toolkit for phylogenetic and hierarchical tree analysis using ETE (Environment for Tree Exploration). Use this skill for any tree-related bioinformatics tasks including phylogenet'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/flowio/SKILL.md')
    assert 'description: "Python library for reading, writing, and manipulating Flow Cytometry Standard (FCS) files. Use this skill for: parsing FCS files (versions 2.0, 3.0, 3.1) to extract event data as NumPy a' in text, "expected to find: " + 'description: "Python library for reading, writing, and manipulating Flow Cytometry Standard (FCS) files. Use this skill for: parsing FCS files (versions 2.0, 3.0, 3.1) to extract event data as NumPy a'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/gget/SKILL.md')
    assert 'description: "Comprehensive bioinformatics toolkit for genomic database queries, sequence analysis, and molecular biology workflows. Use this skill for: gene information retrieval (Ensembl, UniProt, N' in text, "expected to find: " + 'description: "Comprehensive bioinformatics toolkit for genomic database queries, sequence analysis, and molecular biology workflows. Use this skill for: gene information retrieval (Ensembl, UniProt, N'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/matchms/SKILL.md')
    assert 'description: "Process and analyze mass spectrometry data using matchms, a Python library for spectral similarity calculations, metadata harmonization, and compound identification. Use this skill when:' in text, "expected to find: " + 'description: "Process and analyze mass spectrometry data using matchms, a Python library for spectral similarity calculations, metadata harmonization, and compound identification. Use this skill when:'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/matplotlib/SKILL.md')
    assert 'description: "Python\'s foundational data visualization library for creating publication-quality plots, charts, and scientific figures. Use this skill for any visualization task including line plots, s' in text, "expected to find: " + 'description: "Python\'s foundational data visualization library for creating publication-quality plots, charts, and scientific figures. Use this skill for any visualization task including line plots, s'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/medchem/SKILL.md')
    assert 'description: "Python library for medicinal chemistry filtering and compound prioritization in drug discovery workflows. Use medchem when you need to: apply drug-likeness rules (Lipinski Rule of Five, ' in text, "expected to find: " + 'description: "Python library for medicinal chemistry filtering and compound prioritization in drug discovery workflows. Use medchem when you need to: apply drug-likeness rules (Lipinski Rule of Five, '[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/molfeat/SKILL.md')
    assert 'description: "Comprehensive molecular featurization toolkit for converting chemical structures into numerical representations for machine learning. Use this skill when working with molecular data, SMI' in text, "expected to find: " + 'description: "Comprehensive molecular featurization toolkit for converting chemical structures into numerical representations for machine learning. Use this skill when working with molecular data, SMI'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/polars/SKILL.md')
    assert 'description: "Use this skill for all Polars DataFrame operations, data manipulation, analysis, and processing tasks in Python. This includes: DataFrame creation and operations (select, filter, group_b' in text, "expected to find: " + 'description: "Use this skill for all Polars DataFrame operations, data manipulation, analysis, and processing tasks in Python. This includes: DataFrame creation and operations (select, filter, group_b'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/pydeseq2/SKILL.md')
    assert 'description: "Comprehensive toolkit for differential gene expression analysis using PyDESeq2, the Python implementation of DESeq2 for bulk RNA-seq data. Use this skill when users need to identify diff' in text, "expected to find: " + 'description: "Comprehensive toolkit for differential gene expression analysis using PyDESeq2, the Python implementation of DESeq2 for bulk RNA-seq data. Use this skill when users need to identify diff'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/pymatgen/SKILL.md')
    assert 'description: "Python Materials Genomics (pymatgen) toolkit for comprehensive materials science analysis and computational chemistry workflows. Use for crystal structure manipulation, molecular systems' in text, "expected to find: " + 'description: "Python Materials Genomics (pymatgen) toolkit for comprehensive materials science analysis and computational chemistry workflows. Use for crystal structure manipulation, molecular systems'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/pymc/SKILL.md')
    assert 'description: "Comprehensive toolkit for Bayesian modeling, probabilistic programming, and statistical inference using PyMC. Use this skill for building, fitting, validating, and analyzing Bayesian mod' in text, "expected to find: " + 'description: "Comprehensive toolkit for Bayesian modeling, probabilistic programming, and statistical inference using PyMC. Use this skill for building, fitting, validating, and analyzing Bayesian mod'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/pymoo/SKILL.md')
    assert 'description: "Comprehensive Python framework for solving optimization problems including single-objective, multi-objective (2-3 objectives), many-objective (4+ objectives), constrained, and dynamic op' in text, "expected to find: " + 'description: "Comprehensive Python framework for solving optimization problems including single-objective, multi-objective (2-3 objectives), many-objective (4+ objectives), constrained, and dynamic op'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/pyopenms/SKILL.md')
    assert 'description: "Toolkit for mass spectrometry data analysis with pyOpenMS, supporting proteomics and metabolomics workflows including LC-MS/MS data processing, peptide identification, feature detection,' in text, "expected to find: " + 'description: "Toolkit for mass spectrometry data analysis with pyOpenMS, supporting proteomics and metabolomics workflows including LC-MS/MS data processing, peptide identification, feature detection,'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/pysam/SKILL.md')
    assert 'description: "Toolkit for working with genomic data files in Python, including SAM/BAM/CRAM alignment files, VCF/BCF variant files, and FASTA/FASTQ sequence files. This skill should be used when readi' in text, "expected to find: " + 'description: "Toolkit for working with genomic data files in Python, including SAM/BAM/CRAM alignment files, VCF/BCF variant files, and FASTA/FASTQ sequence files. This skill should be used when readi'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/pytdc/SKILL.md')
    assert 'description: "PyTDC (Therapeutics Data Commons) provides AI-ready datasets and benchmarks for drug discovery, therapeutic machine learning, and pharmacological research. Use this skill for: loading cu' in text, "expected to find: " + 'description: "PyTDC (Therapeutics Data Commons) provides AI-ready datasets and benchmarks for drug discovery, therapeutic machine learning, and pharmacological research. Use this skill for: loading cu'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/pytorch-lightning/SKILL.md')
    assert 'description: "PyTorch Lightning deep learning framework skill for organizing PyTorch code and automating training workflows. Use this skill for: creating LightningModules with training_step/validation' in text, "expected to find: " + 'description: "PyTorch Lightning deep learning framework skill for organizing PyTorch code and automating training workflows. Use this skill for: creating LightningModules with training_step/validation'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/rdkit/SKILL.md')
    assert 'description: "Comprehensive cheminformatics toolkit for molecular manipulation, analysis, and visualization. Use this skill when working with chemical structures (SMILES, MOL files, SDF, InChI), calcu' in text, "expected to find: " + 'description: "Comprehensive cheminformatics toolkit for molecular manipulation, analysis, and visualization. Use this skill when working with chemical structures (SMILES, MOL files, SDF, InChI), calcu'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/reportlab/SKILL.md')
    assert 'description: "ReportLab PDF generation skill for creating professional PDF documents programmatically in Python. Use this skill for generating invoices, reports, certificates, labels, forms, charts, t' in text, "expected to find: " + 'description: "ReportLab PDF generation skill for creating professional PDF documents programmatically in Python. Use this skill for generating invoices, reports, certificates, labels, forms, charts, t'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/scanpy/SKILL.md')
    assert 'description: "Use this skill for comprehensive single-cell RNA-seq analysis with scanpy. Essential for: loading single-cell data (.h5ad, 10X Genomics, CSV, HDF5), performing quality control and filter' in text, "expected to find: " + 'description: "Use this skill for comprehensive single-cell RNA-seq analysis with scanpy. Essential for: loading single-cell data (.h5ad, 10X Genomics, CSV, HDF5), performing quality control and filter'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/scikit-bio/SKILL.md')
    assert 'description: "Comprehensive Python toolkit for biological data analysis and bioinformatics workflows. Handles DNA/RNA/protein sequence manipulation, sequence alignments (global/local), phylogenetic tr' in text, "expected to find: " + 'description: "Comprehensive Python toolkit for biological data analysis and bioinformatics workflows. Handles DNA/RNA/protein sequence manipulation, sequence alignments (global/local), phylogenetic tr'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/scikit-learn/SKILL.md')
    assert 'description: "Comprehensive machine learning toolkit using scikit-learn for Python. Use this skill for supervised learning (classification, regression), unsupervised learning (clustering, dimensionali' in text, "expected to find: " + 'description: "Comprehensive machine learning toolkit using scikit-learn for Python. Use this skill for supervised learning (classification, regression), unsupervised learning (clustering, dimensionali'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/seaborn/SKILL.md')
    assert 'description: "Use seaborn for statistical data visualization, exploratory data analysis, and publication-quality plots. This skill covers creating scatter plots, line plots, histograms, KDE plots, box' in text, "expected to find: " + 'description: "Use seaborn for statistical data visualization, exploratory data analysis, and publication-quality plots. This skill covers creating scatter plots, line plots, histograms, KDE plots, box'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/statsmodels/SKILL.md')
    assert 'description: "Comprehensive statistical modeling and econometric analysis toolkit for Python. This skill should be used when you need to fit statistical models, perform hypothesis testing, conduct eco' in text, "expected to find: " + 'description: "Comprehensive statistical modeling and econometric analysis toolkit for Python. This skill should be used when you need to fit statistical models, perform hypothesis testing, conduct eco'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/torch_geometric/SKILL.md')
    assert 'description: "PyTorch Geometric (PyG) skill for building, training, and deploying Graph Neural Networks (GNNs) on structured data including graphs, 3D meshes, point clouds, and heterogeneous networks.' in text, "expected to find: " + 'description: "PyTorch Geometric (PyG) skill for building, training, and deploying Graph Neural Networks (GNNs) on structured data including graphs, 3D meshes, point clouds, and heterogeneous networks.'[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/transformers/SKILL.md')
    assert 'description: "Essential toolkit for Hugging Face Transformers library enabling state-of-the-art machine learning across natural language processing, computer vision, audio processing, and multimodal a' in text, "expected to find: " + 'description: "Essential toolkit for Hugging Face Transformers library enabling state-of-the-art machine learning across natural language processing, computer vision, audio processing, and multimodal a'[:80]


def test_signal_58():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/umap-learn/SKILL.md')
    assert 'description: "Comprehensive guide for UMAP (Uniform Manifold Approximation and Projection) - a fast, scalable dimensionality reduction technique for visualization, clustering, and machine learning. Us' in text, "expected to find: " + 'description: "Comprehensive guide for UMAP (Uniform Manifold Approximation and Projection) - a fast, scalable dimensionality reduction technique for visualization, clustering, and machine learning. Us'[:80]


def test_signal_59():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-packages/zarr-python/SKILL.md')
    assert 'description: "Toolkit for working with Zarr, a Python library for chunked, compressed N-dimensional arrays optimized for cloud storage and large-scale scientific computing. Use this skill when working' in text, "expected to find: " + 'description: "Toolkit for working with Zarr, a Python library for chunked, compressed N-dimensional arrays optimized for cloud storage and large-scale scientific computing. Use this skill when working'[:80]


def test_signal_60():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-thinking/document-skills/pdf/SKILL.md')
    assert 'description: "Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. When Claude needs to fill in a PDF form or prog' in text, "expected to find: " + 'description: "Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. When Claude needs to fill in a PDF form or prog'[:80]


def test_signal_61():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-thinking/exploratory-data-analysis/SKILL.md')
    assert 'description: "Comprehensive exploratory data analysis (EDA) toolkit for analyzing datasets and generating actionable insights. Use this skill when users provide data files and request analysis, explor' in text, "expected to find: " + 'description: "Comprehensive exploratory data analysis (EDA) toolkit for analyzing datasets and generating actionable insights. Use this skill when users provide data files and request analysis, explor'[:80]


def test_signal_62():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-thinking/hypothesis-generation/SKILL.md')
    assert 'description: "Generate robust, testable scientific hypotheses grounded in existing literature. Use this skill when users need to formulate hypotheses from observations, design experiments to test hypo' in text, "expected to find: " + 'description: "Generate robust, testable scientific hypotheses grounded in existing literature. Use this skill when users need to formulate hypotheses from observations, design experiments to test hypo'[:80]


def test_signal_63():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-thinking/peer-review/SKILL.md')
    assert 'description: "Comprehensive scientific peer review toolkit for evaluating manuscripts, papers, preprints, and research documents across all disciplines. Use this skill to conduct systematic peer revie' in text, "expected to find: " + 'description: "Comprehensive scientific peer review toolkit for evaluating manuscripts, papers, preprints, and research documents across all disciplines. Use this skill to conduct systematic peer revie'[:80]


def test_signal_64():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-thinking/scientific-brainstorming/SKILL.md')
    assert 'description: "Structured conversational brainstorming partner for scientific research ideation and creative problem-solving. Activates when scientists need to: generate novel research ideas and hypoth' in text, "expected to find: " + 'description: "Structured conversational brainstorming partner for scientific research ideation and creative problem-solving. Activates when scientists need to: generate novel research ideas and hypoth'[:80]


def test_signal_65():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-thinking/scientific-critical-thinking/SKILL.md')
    assert 'description: "Apply systematic scientific critical thinking to rigorously evaluate research methodology, statistical analyses, evidence quality, and scientific claims. Use this skill when: analyzing r' in text, "expected to find: " + 'description: "Apply systematic scientific critical thinking to rigorously evaluate research methodology, statistical analyses, evidence quality, and scientific claims. Use this skill when: analyzing r'[:80]


def test_signal_66():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-thinking/scientific-visualization/SKILL.md')
    assert 'description: "Create publication-ready scientific figures, plots, charts, and visualizations using matplotlib, seaborn, and plotly. Use this skill for any scientific data visualization task including:' in text, "expected to find: " + 'description: "Create publication-ready scientific figures, plots, charts, and visualizations using matplotlib, seaborn, and plotly. Use this skill for any scientific data visualization task including:'[:80]


def test_signal_67():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-thinking/statistical-analysis/SKILL.md')
    assert 'description: "Comprehensive statistical analysis toolkit for rigorous academic research using Python. This skill handles hypothesis testing (t-tests, ANOVA, chi-square, non-parametric tests), regressi' in text, "expected to find: " + 'description: "Comprehensive statistical analysis toolkit for rigorous academic research using Python. This skill handles hypothesis testing (t-tests, ANOVA, chi-square, non-parametric tests), regressi'[:80]

