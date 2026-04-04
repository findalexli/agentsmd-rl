---
name: scout-prs
description: Find candidate GitHub PRs for new benchmark tasks. Searches repos for merged PRs with agent config files, filters by quality heuristics, and outputs JSONL candidates. Use when expanding the task pool.
argument-hint: "[--agentmd] [--repos repo1,repo2] [--limit N]"
allowed-tools: Bash(gh:*), Bash(python3:*), Read, Write
---

# Scout PRs

Find candidate merged PRs suitable for benchmark task generation.

## Two modes

### Standard scouting (code-only tasks)
```bash
python -m taskforge.scout scout --repos-file scouted_repos.jsonl --limit 20 --output scouted_prs.jsonl
```

### AgentMD scouting (code + config edit tasks)
PRs that modify BOTH code AND agent config files:
```bash
python -m taskforge.scout scout --agentmd --repos-file scouted_repos.jsonl --limit 15 --months 6 --output scouted_agentmd_prs.jsonl
```

Then filter for quality:
```bash
python -m taskforge.scout filter --agentmd --input scouted_agentmd_prs.jsonl --output scouted_agentmd_prs_filtered.jsonl
```

## Quality heuristics

| Filter | Standard | AgentMD |
|--------|----------|---------|
| Files changed | 1-8 | 2-15 |
| Total lines | 5-500 | 10-800 |
| Has code files | yes | yes |
| Has config files | - | yes (non-trivial) |
| Recency | any | 4-6 months |
| Skip labels | deps, docs, bot, ci | same |

## Finding new repos

Search GitHub for repos with agent config files:
```bash
gh api "search/code?q=filename:CLAUDE.md+extension:md&per_page=100" \
  --jq '[.items[].repository.full_name] | unique | .[]'
```

Filter for serious repos (>1000 stars, not archived, not fork):
```bash
gh api "repos/OWNER/REPO" --jq '[.stargazers_count, .archived, .fork] | @tsv'
```

## Repo list

Current repos are in `scouted_repos.jsonl` (49 repos, 3.9K-244K stars).
Extra repos in `scouted_repos_agentmd_extra.jsonl` (27 repos from code search).

## Output format

```json
{"repo": "owner/repo", "pr_number": 123, "title": "...", "changed_files": 3, "additions": 45, "deletions": 12, "merged_at": "2026-...", "merge_sha": "abc...", "file_paths": [...]}
```
