# Revise Foldseek skill

Source: [adaptyvbio/protein-design-skills#3](https://github.com/adaptyvbio/protein-design-skills/pull/3)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/foldseek/SKILL.md`

## What to add / change

I stumbled upon this repo through a linkedin post. Cool idea!

I revised some of the recommendations. Both 3Di-only and reducing --max-seqs are a bit dangerous and I would recommend against changing defaults. Reducing `--max-seqs` affects sensitivity strongly, as this controls not the number of reported results, but the number of results that are allowed to pass through the prefilter to the alignment stage.

The TM-score rescoring of the alignment hits also improves result ranking with a very minor difference in speed, as its only done on a small number of hits that pass the alignment stage.

The FS webserver is also (very similar to ColabFold) rate-limited. I want to make this clear so whatever AI system doesn't start to query large numbers of structures in a loop.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
