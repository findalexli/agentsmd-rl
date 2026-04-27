# feat(prognostics): expose ISO 13374 Block 5 as MCP tools + plugin skill

Source: [LGDiMaggio/predictive-maintenance-mcp#29](https://github.com/LGDiMaggio/predictive-maintenance-mcp/pull/29)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugin/skills/prognostics/SKILL.md`

## What to add / change

## Summary
- Expose the existing prognostics module (trend analysis, degradation onset, RUL estimation) as 3 new MCP tools: `analyze_trend`, `detect_degradation_onset`, `estimate_rul`
- Add Pydantic response models (`TrendAnalysisResult`, `DegradationOnsetResult`, `RULEstimationResult`) for structured outputs
- Create `plugin/skills/prognostics/SKILL.md` with a 6-step guided workflow, enabling Claude to orchestrate prognostic assessments via the plugin

## Test plan
- [x] All imports verified (`src.prognostics`, `src.models`, `src.mcp_tools.prognostics_tools`)
- [x] 3 tools confirmed registered in MCP server (total: 43 tools)
- [x] 413 existing tests pass with 0 failures
- [ ] End-to-end: load multiple measurement sessions, extract features, run `analyze_trend` + `estimate_rul`
- [ ] Verify skill triggers correctly in Claude Code plugin

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
