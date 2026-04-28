# Remove knowledge-graph.json references from copilot-instructions.md

Source: [department-of-veterans-affairs/va.gov-team#139110](https://github.com/department-of-veterans-affairs/va.gov-team/pull/139110)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Copilot models see `knowledge-graph.json` mentioned as an option in `.github/copilot-instructions.md`, default to reading it directly, hit repeated truncation on the 35k-line file, and fail to answer. Removing all user-facing KG references eliminates the decision paralysis — summary files become the only documented path.

### Removed
- Entire "Knowledge Graph" section: node/edge type tables, JSON structure examples, query workflows, `<knowledge_graph_usage>` block (~225 lines)
- KG-specific advice in `<critical_tool_calling_instructions>`
- `knowledge-graph.json` entry from Repository Structure
- All KG references in troubleshooting sections

### Replaced with
- Concise "Team and Research Information" section (~57 lines): question→file lookup table, three `getfile` examples, file characteristics, fallback to directory search
- One-line technical note: `knowledge-graph.json` is for automation only, do not read directly

### Kept unchanged
- `knowledge-graph.json` in sparse checkout config (needed by workflows)
- Script descriptions (`build-knowledge-graph.js`, `generate-copilot-summaries.js`)
- Research Data Integrity Rules, Setup Requirements, all other sections

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
