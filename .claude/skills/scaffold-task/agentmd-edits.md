# AgentMD-Edits Architecture (Reference)

For tasks where the PR modifies BOTH code AND agent config files.

## Key decision

Config file edits are evaluated via **LLM judge (rubric)**, NOT binary pytest checks.

**Why:** LLM agents produce semantically equivalent but differently worded content. Exact string matching in pytest is unfair for natural language output.

- **Binary reward** = code tests only (pytest → reward.txt)
- **Config edit quality** = LLM judge, separate signal (rubric in eval_manifest.yaml)
- **Gold patch stays complete** (code + config in solve.sh)

## How the judge works

1. Gold config diffs are auto-extracted from solve.sh using `extract_config_hunks()` from `taskforge.config`
2. Stored in rubric `reference` field in eval_manifest.yaml
3. At eval time, same parser extracts agent's config hunks from their `git diff`
4. LLM compares side-by-side: "gold added X to AGENTS.md, agent added Y — semantically equivalent?"

## eval_manifest.yaml format

```yaml
rubric:
  - rule: "AGENTS.md indicates SDK is frozen"
    source:
      path: src/pyodide/AGENTS.md
      lines: "18"
      commit: "merge_commit_sha"
    reference: |
      Python SDK package (frozen)
      ## Python SDK
      Python SDK now lives in cloudflare/workers-py...
```

## Migration script

`scripts/migrate_config_to_rubric.py` moves `config_edit` checks from `checks[]` → `rubric[]` and auto-extracts gold reference text.

## instruction.md for agentmd tasks

Must mention that config/doc updates are part of the task:
- "After fixing the code, update the relevant documentation to reflect the change."
- "The project's CLAUDE.md should be updated to document this new behavior."
