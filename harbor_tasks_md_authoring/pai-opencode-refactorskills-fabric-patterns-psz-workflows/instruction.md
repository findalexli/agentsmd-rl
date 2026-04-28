# refactor(skills): Fabric Patterns Ps–Z + Workflows + SKILL.md → Utilities/Fabric/ (PR-06 of 12)

Source: [Steffen025/pai-opencode#73](https://github.com/Steffen025/pai-opencode/pull/73)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.opencode/skills/Utilities/Fabric/Patterns/suggest_pattern/user_updated.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize/dmiessler/summarize/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize/dmiessler/summarize/user.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize/user.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_board_meeting/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_debate/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_git_changes/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_git_diff/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_lecture/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_legislation/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_meeting/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_micro/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_micro/user.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/README.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/user.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_prompt/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_pull-requests/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_pull-requests/user.md`
- `.opencode/skills/Utilities/Fabric/Patterns/summarize_rpg_session/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_analyze_challenge_handling/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_check_dunning_kruger/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_check_metrics/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_create_h3_career/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_create_opening_sentences/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_describe_life_outlook/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_extract_intro_sentences/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_extract_panel_topics/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_find_blindspots/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_find_negative_thinking/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_find_neglected_goals/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_give_encouragement/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_red_team_thinking/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_threat_model_plans/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_visualize_mission_goals_projects/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/t_year_in_review/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/threshold/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/to_flashcards/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/transcribe_minutes/README.md`
- `.opencode/skills/Utilities/Fabric/Patterns/transcribe_minutes/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/translate/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/tweet/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/write_essay/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/write_essay_pg/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/write_hackerone_report/README.md`
- `.opencode/skills/Utilities/Fabric/Patterns/write_hackerone_report/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/write_latex/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/write_micro_essay/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/write_nuclei_template_rule/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/write_nuclei_template_rule/user.md`
- `.opencode/skills/Utilities/Fabric/Patterns/write_pull-request/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/write_semgrep_rule/system.md`
- `.opencode/skills/Utilities/Fabric/Patterns/write_semgrep_rule/user.md`
- `.opencode/skills/Utilities/Fabric/Patterns/youtube_summary/system.md`
- `.opencode/skills/Utilities/Fabric/SKILL.md`
- `.opencode/skills/Utilities/Fabric/Workflows/ExecutePattern.md`
- `.opencode/skills/Utilities/Fabric/Workflows/UpdatePatterns.md`

## What to add / change

## PR-06: Fabric Patterns Ps–Z + Workflows + SKILL.md → Utilities/Fabric/

**Part 6 of 12** in the PAI-OpenCode v3.0 migration from `dev` to `main`.

### What
Relocates 58 files completing the Fabric pattern migration:
- Remaining patterns (Ps–Z range) to `.opencode/skills/Utilities/Fabric/Patterns/`
- Workflows to `.opencode/skills/Utilities/Fabric/Workflows/`
- SKILL.md to `.opencode/skills/Utilities/Fabric/SKILL.md`

### Patterns included (selection)
- `summarize_*` family (meeting, debate, lecture, legislation, paper, git changes/diff, pull-requests, rpg_session, micro, prompt, board_meeting)
- `write_*` family (essay, essay_pg, hackerone_report, latex, micro_essay, nuclei_template_rule, pull-request, semgrep_rule)
- `t_*` family (analyze_challenge_handling, check_dunning_kruger, check_metrics, create_h3_career, find_blindspots, red_team_thinking, etc.)
- `threshold`, `to_flashcards`, `transcribe_minutes`, `translate`, `tweet`, `youtube_summary`

### Context
Completes the 3-part Fabric pattern reorganization:
- PR-04: Patterns A–Kn (130 files) ✅ merged
- PR-05: Patterns Ko–Pr (130 files) ✅ merged
- **PR-06: Patterns Ps–Z + Workflows + SKILL.md (58 files) ← this PR**

All content is upstream Fabric — no PAI-specific code changes.

### Jira
WARNEX-80

---
@coderabbitai Review für Korrektheit, OpenCode-Konformität, und verbleibende Claude→OpenCode Probleme

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Dokumentation*

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
