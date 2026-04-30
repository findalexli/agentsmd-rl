# harbor_tasks_agentmd_edits — Collection Status

## Overview

Tasks from PRs that change both **functional code** AND **agent config files** (CLAUDE.md, AGENTS.md, README.md, SKILL.md, etc.). Each task tests whether agents make the right documentation/config update alongside code changes.

## Collection Timeline (2026-04-03)

### Phase 1: Scout (1:00am - 1:30am)
- Scouted 49 existing repos + 27 new repos (76 total)
- 6-month lookback, 500 PRs/repo
- Filters: 2-15 files, 10-800 lines, both code + config changed, non-trivial config edit
- **Result: 242 candidate PRs**

### Phase 2: Quality Filter (1:30am - 2:00am)
- Fetched diffs, classified config edits
- Removed trivial config changes, bot PRs, changelog-only
- Edit types: new_feature_doc (97), other (75), rule_update (43), architecture_doc (20)
- **Result: 208 filtered → 242 total (some repos re-scouted)**

### Phase 3: Batch Scaffold (1:06am - 6:50am, 5.7h)
- Claude Opus, $6/task budget, 4 workers, 900s timeout
- LLM intelligently skipped 48 unsuitable PRs (merge commits, trivial changes)
- **Result: 194 success, 48 skipped → 236 tasks**

### Phase 4: Post-Scaffold Cleanup
- Removed NotImplementedError placeholder tests from template
- Relabeled config file tests to `origin: config_edit`
- **Result: 236/236 tasks have config_edit checks (661 total)**

### Phase 5: E2B Validation (6:54am - 7:20am, 26min)
- **Result: 132 valid (56%), 37 gold=0, 44 build errors, 23 solve errors**

## Current Scoreboard

| Status | Count | % |
|--------|-------|---|
| **pass** | **132** | **55.9%** |
| fail (gold=0) | 37 | 15.7% |
| fail_build | 44 | 18.6% |
| error (solve.sh) | 23 | 9.7% |
| **Total** | **236** | |

## Config Edit Check Coverage

- 236/236 tasks have at least one `config_edit` check
- 661 total config_edit checks across all tasks
- Average: 2.8 config_edit checks per task

## Repos Represented (top 15)

| Repo | Tasks |
|------|-------|
| remix-run/remix | 17 |
| microsoft/playwright | 14 |
| matthiasn/lotti | 11 |
| vercel/next.js | 10 |
| cloudflare/workerd | 9 |
| dotnet/maui | 8 |
| payloadcms/payload | 7 |
| apache/beam | 7 |
| prisma/prisma | 6 |
| facebook/react | 6 |
| ant-design/ant-design | 5 |
| PostHog/posthog | 4 |
| triggerdotdev/trigger.dev | 4 |
| microsoft/vscode | 4 |
| huggingface/transformers | 4 |

## Next Steps

- [ ] Fix 44 Dockerfile build errors (common: missing deps, GPG keys, shallow clone)
- [ ] Re-scaffold 37 gold=0 tasks with improved prompt
- [ ] Fix 23 solve.sh patch errors (context mismatch)
- [ ] Target: 180+ passing tasks
