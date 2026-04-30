# Update SKILL.md files to add double quotation marks for all skills

Source: [K-Dense-AI/scientific-agent-skills#1](https://github.com/K-Dense-AI/scientific-agent-skills/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `scientific-databases/alphafold-database/SKILL.md`
- `scientific-databases/chembl-database/SKILL.md`
- `scientific-databases/clinpgx-database/SKILL.md`
- `scientific-databases/clinvar-database/SKILL.md`
- `scientific-databases/cosmic-database/SKILL.md`
- `scientific-databases/ena-database/SKILL.md`
- `scientific-databases/ensembl-database/SKILL.md`
- `scientific-databases/gene-database/SKILL.md`
- `scientific-databases/geo-database/SKILL.md`
- `scientific-databases/gwas-database/SKILL.md`
- `scientific-databases/hmdb-database/SKILL.md`
- `scientific-databases/kegg-database/SKILL.md`
- `scientific-databases/metabolomics-workbench-database/SKILL.md`
- `scientific-databases/pdb-database/SKILL.md`
- `scientific-databases/pubchem-database/SKILL.md`
- `scientific-databases/pubmed-database/SKILL.md`
- `scientific-databases/reactome-database/reactome-database/SKILL.md`
- `scientific-databases/string-database/SKILL.md`
- `scientific-databases/uniprot-database/SKILL.md`
- `scientific-databases/zinc-database/SKILL.md`
- `scientific-packages/anndata/SKILL.md`
- `scientific-packages/arboreto/SKILL.md`
- `scientific-packages/astropy/SKILL.md`
- `scientific-packages/biomni/SKILL.md`
- `scientific-packages/biopython/SKILL.md`
- `scientific-packages/bioservices/SKILL.md`
- `scientific-packages/cellxgene-census/SKILL.md`
- `scientific-packages/cobrapy/SKILL.md`
- `scientific-packages/dask/SKILL.md`
- `scientific-packages/datamol/SKILL.md`
- `scientific-packages/deepchem/SKILL.md`
- `scientific-packages/deeptools/SKILL.md`
- `scientific-packages/diffdock/SKILL.md`
- `scientific-packages/etetoolkit/SKILL.md`
- `scientific-packages/flowio/SKILL.md`
- `scientific-packages/gget/SKILL.md`
- `scientific-packages/matchms/SKILL.md`
- `scientific-packages/matplotlib/SKILL.md`
- `scientific-packages/medchem/SKILL.md`
- `scientific-packages/molfeat/SKILL.md`
- `scientific-packages/polars/SKILL.md`
- `scientific-packages/pydeseq2/SKILL.md`
- `scientific-packages/pymatgen/SKILL.md`
- `scientific-packages/pymc/SKILL.md`
- `scientific-packages/pymoo/SKILL.md`
- `scientific-packages/pyopenms/SKILL.md`
- `scientific-packages/pysam/SKILL.md`
- `scientific-packages/pytdc/SKILL.md`
- `scientific-packages/pytorch-lightning/SKILL.md`
- `scientific-packages/rdkit/SKILL.md`
- `scientific-packages/reportlab/SKILL.md`
- `scientific-packages/scanpy/SKILL.md`
- `scientific-packages/scikit-bio/SKILL.md`
- `scientific-packages/scikit-learn/SKILL.md`
- `scientific-packages/seaborn/SKILL.md`
- `scientific-packages/statsmodels/SKILL.md`
- `scientific-packages/torch_geometric/SKILL.md`
- `scientific-packages/transformers/SKILL.md`
- `scientific-packages/umap-learn/SKILL.md`
- `scientific-packages/zarr-python/SKILL.md`
- `scientific-thinking/document-skills/pdf/SKILL.md`
- `scientific-thinking/exploratory-data-analysis/SKILL.md`
- `scientific-thinking/hypothesis-generation/SKILL.md`
- `scientific-thinking/peer-review/SKILL.md`
- `scientific-thinking/scientific-brainstorming/SKILL.md`
- `scientific-thinking/scientific-critical-thinking/SKILL.md`
- `scientific-thinking/scientific-visualization/SKILL.md`
- `scientific-thinking/statistical-analysis/SKILL.md`

## What to add / change

No changes to content other than adding quotation marks to prevent in-line colons from breaking the YAML syntax.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
