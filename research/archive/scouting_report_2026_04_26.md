# Scouting & Causality Classification — 2026-04-26

A single-day pass that took the candidate pool from 204 baseline wins to **977 candidate PRs** ready for scaffolding.

## TL;DR

| Stage | Count | Note |
|---|---:|---|
| Repos processed | 107 + 40 in-flight discovery | 147 total |
| Raw PRs fetched | 19,417 | 107 repos × 12-month window, cap 800/repo |
| Unique after dedup | 14,549 | vs. 4,809-stub baseline |
| Into causality judge | 13,046 | tier-1 repo allowlist |
| A + B wins today | **750** | A=204, B=546, C=10,398, D=1,896, ERR=2 |
| Cumulative candidates | **977** | |
| Gemini cost | ~$153 | Flex tier (50% off Standard) |
| Wall clock | ~14 h scout + 17 min judge | |

## Funnel breakdown

### Stage 1 — Repo discovery

107 repos came from earlier rounds; left static for this pass. A late-day discovery effort surfaced **40 fresh repos** (zero overlap), ≥500 stars, with confirmed tier-1 files. Method: `gh search repos` on topics like `claude-code`, `claude-skills`, `mcp-server`, `vibe-coding`, plus WebFetch on awesome-claude-code / awesome-agents-md lists. Avoided `gh search code` — its abuse-detection bucket was already exhausted.

Top discoveries:

| Stars | Repo |
|---|---|
| 185,684 | n8n-io/n8n |
| 124,239 | anthropics/skills |
| 102,460 | google-gemini/gemini-cli |
| 78,042 | openai/codex |
| 53,785 | upstash/context7 |
| 47,033 | metabase/metabase |
| 44,461 | CherryHQ/cherry-studio |
| 40,941 | HKUDS/nanobot |
| 37,279 | ChromeDevTools/chrome-devtools-mcp |
| 26,856 | eyaltoledano/claude-task-master |

Sixteen of the 40 have rich SKILL.md trees (15-20 tier-1 files each). Full list: `/tmp/new_skill_repos.jsonl`.

### Stage 2 — PR fetching

`taskforge.scout` with `gh pr list --state merged --limit 800 --json …` against each of 107 repos, hard-capped at 12 months. Hit GitHub's primary rate limit (~5,000/h) every hour; retry sleeps until reset. 10 h wall = ~5.6 min/repo. Output: 19,417 rows.

### Stage 3 — Dedup

Two-key dedup against the 4,809-stub corpus: `slugify(repo, title)` (semantic) and `(repo, pr_number)` (strict). Of 19,417, dropped 4,868 (3,823 both keys, 1,045 slug-only — likely renamed PRs). **14,549 unique survivors.**

### Stage 4 — Tier-1 repo allowlist

1,503 PRs dropped because their repos weren't in `repo_tier1.json` (manually-curated repo → tier-1 path mapping). The filter trusts the snapshot — a few repos had recently added or removed tier-1 files. **13,046 PRs into the judge.**

### Stage 5 — Causality judge (Gemini 3.1 Pro Flex)

Each PR gets a structured-output verdict on whether the gold diff is causally shaped by the repo's tier-1 instruction files.

| Verdict | Count | % | Definition |
|---|---:|---:|---|
| **A** | 204 | 1.6 | Diff includes a tier-1 markdown file. Path-only — no LLM call. |
| **B** | 546 | 4.2 | Code-only PR whose fix specifically applies a tier-1 rule (LLM). |
| C | 10,398 | 79.7 | Decorative — fix determined by the bug, not by any rule (LLM). |
| D | 1,896 | 14.5 | Unscaffoldable — platform-specific, >500-line refactor, no testable behavior (LLM). |
| ERR | 2 | 0.0 | Judge call failed end-to-end. |

5.7 % A + B yield. The "short-circuit" path (file-path matching, no LLM) handled 3,876 of 13,046 PRs — all the As plus 3,672 C-unfetchable cases (PR's tier-1 markdown didn't exist at base commit, default-class decorative). The remaining 9,171 got real LLM calls.

## Top contributing repos

### Class B — code-fix-follows-rule (the canonical bucket)

| Count | Repo | Count | Repo |
|---:|---|---:|---|
| 42 | openai/openai-agents-js | 22 | pulumi/pulumi |
| 42 | remix-run/remix | 20 | weaviate/weaviate |
| 41 | astral-sh/uv | 17 | dotnet/runtime |
| 30 | huggingface/transformers | 15 | anomalyco/opencode |
| 27 | prefecthq/prefect | 12 | SeleniumHQ/selenium |
| 26 | apache/superset | 11 | effect-ts/effect |
| 25 | vitessio/vitess | 10 | astral-sh/ruff |
| 22 | cloudflare/workers-sdk | | |

Top three (openai-agents-js, remix, uv) have very mature CLAUDE.md / AGENTS.md adoption with explicit handling rules for cookbook generation, lockfile regen, migration patterns.

### Class A — markdown-edit

| Count | Repo | Count | Repo |
|---:|---|---:|---|
| 22 | ant-design/ant-design | 7 | withastro/astro |
| 9 | openai/openai-agents-js | 6 | apache/airflow |
| 9 | vitessio/vitess | 6 | dotnet/runtime |
| 8 | microsoft/playwright | 6 | mlflow/mlflow |
| 7 | PRQL/prql | 5 | All-Hands-AI/OpenHands |
| 7 | dotnet/maui | 5 | dotnet/efcore |
| 7 | remix-run/remix | 5 | gradio-app/gradio |

ant-design dominates — they actively curate CLAUDE.md and ship one PR per agent-instruction tweak.

## Cost

| Item | Cost |
|---|---:|
| GitHub API | $0 (rate-limited only) |
| Gemini scout-judge (9,171 Flex prompts) | ~$140 |
| Gemini ERR-recheck (287) | ~$3 |
| Gemini C-unfetchable-recheck (890) | ~$10 |
| Failed batch attempt (cancelled) | $0 |
| **Total** | **~$153** |

Projected scaffolding pass on 977 PRs via `oneshot_scaffold` (Opus 4.7 + E2B): ~$8 × 977 = **~$7,800**. At 60 % Docker-oracle pass rate → ~580 new tasks against existing 442 = 1,022 reached.

## Batch vs Flex

Initially submitted the 9,171-prompt job as a Gemini batch (camelCase JSONL, `responseSchema`, `thinkingConfig.thinkingBudget=512`). Advertised 50 % off with up to 24 h SLA, typically minutes-to-hours. Outcome: 3 + h in `JOB_STATE_RUNNING`, `update_time` freshness drifting from sub-second to 16 min stale; no `completion_stats` exposed mid-run. Cancelled and switched to **Flex tier**.

| | Batch (cancelled) | Flex |
|---|---|---|
| Pricing | 50 % off Standard | 50 % off Standard (identical) |
| Endpoint | Async, file-based | Sync `generateContent` |
| Wall clock (9,171 prompts) | 3 h+ and counting | **17 min** at concurrency 32 |
| Per-call latency | (opaque) | ~2-3 s typical |
| Failure modes | Opaque queueing | 429 / 503 fail-fast, client retries |
| Visibility | `state` only | Per-call results streaming |

Flex is the right default for medium-sized classifier passes — same per-token cost, better visibility, incremental results. One-line config: `service_tier=ServiceTier.FLEX`. The earlier "Flex doesn't exist" memory was stale-SDK / wrong-spelling — canonical Python field is **`service_tier`** (snake_case).

## What was thrown away

| What | Count | Reason | Recovery? |
|---|---:|---|---|
| C / tier-1 unfetchable | 3,672 | tier-1 markdown didn't exist at base commit (PR predates adoption) | No — accepted as pre-adoption noise |
| C-unfetchable rerun | 890 | only 5 A wins | Confirms default-decorative is correct |
| ERR-row reruns | 287 | 18 wins (9 A + 9 B); some were `lobe-chat` httpx-redirect bugs (fixed via `follow_redirects=True`) | Recovered |

## Lessons

| # | Lesson |
|---|---|
| 1 | `follow_redirects=True` on every httpx GitHub client. Several repos (e.g., `lobehub/lobe-chat`) have moved; without it, every PR silently becomes ERR. |
| 2 | Gemini batch JSONL uses raw REST format (`generationConfig`, `responseMimeType`), not SDK snake_case. Discovered after a `400 INVALID_ARGUMENT` storm. |
| 3 | Drop `gh pr list --json files` — triggers GraphQL 504 storms on busy repos (PostHog, OpenHands). Re-fetch per PR if needed. |
| 4 | Short-circuit count is misleading: ~95 % of "no LLM call" hits are tier-1-unfetchable C dropouts, not class-A wins. We initially projected ~2,800 A wins from the rate; actual was 204. Separate the two paths in progress logs. |
| 5 | The 4,809-stub baseline was already tight — only 890 unfetchables had ever bypassed the LLM. Re-judging the rest wasn't worth it. |
| 6 | Discovery is bursty-cheap (40 repos in 6 min via topic search + WebFetch); scouting is slow (4 + h GH-rate-limited per 40 repos). Run discovery hot, scouting cold. |

## Class composition for RL training

The 977-PR pool maps to three task shapes via `task.kind` in `eval_manifest.yaml`:

| Kind | Source | ~Count | What it tests |
|---|---|---:|---|
| `code_fix` | Class B | ~600 | Canonical: agent reads a SKILL.md / AGENTS.md rule, applies during code change |
| `code_with_config` | Class A bundled (code + markdown) | ~140 | Cross-file consistency: agent updates a rule AND the code following it |
| `markdown_authoring` | Class A markdown-only | ~70 | Agent writes a SKILL.md from a brief — adjacent skill, not core hypothesis |

Bundled-vs-pure-markdown split inside Class A is done at scaffold time by counting tier-1 paths in `changed_files`. Pure markdown-only is ~30 % of A from spot-checks. RL weighting: heavy `code_fix` + `code_with_config`, ~5-10 % `markdown_authoring` for diversity.

## Next steps

1. Wait for scout-new-40 (~4-5 h). Judge with Flex (~$30, 17 min). Expected ~100-300 more wins.
2. Scaffold the 977-PR pool through `oneshot_scaffold`: ~$7,800, 60 % expected pass → ~580 new tasks.
3. Build + push GHCR images for the 399 tier-A scaffolded tasks (`push-images.yml` in flight).
4. Distractor-generation pass on 91 tasks scaffolded last night with rubric but no distractor block.
5. Class-A triage script: split bundled vs pure-markdown via `changed_files`, set `task.kind`, route into `markdown_edits/` vs `markdown_authoring/`.

## Artifacts on disk

- `pipeline_logs/batch_judge_2026_04_25/deep_scout_judges.csv` — 13,208 verdict rows
- `pipeline_logs/batch_judge_2026_04_25/err_rechecks.csv` — 287-row ERR-recheck
- `pipeline_logs/batch_judge_2026_04_25/c_unfetchable_rechecks.csv` — 890-row C-unfetchable rerun
- `scouted_deep_2026_04_25.jsonl` — 19,417 raw scout rows
- `scouted_deep_2026_04_25_unique.jsonl` — 14,549 deduped
- `/tmp/new_skill_repos.jsonl` — 40 newly-discovered repos
- `scripts/audit_stub_batch.py` — batch judge with rate-limit-aware GH fetch
- `scripts/judge_flex.py` — Flex sync judge (drop-in for batch JSONL)
- `scripts/dockerfile_shallow_migrate.py` — Dockerfile full-clone → shallow migration
