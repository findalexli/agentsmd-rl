# Scouting & Causality Classification — 2026-04-26

A single-day pass that took our candidate PR pool from 204 baseline wins to **977 candidate PRs** ready for scaffolding. This document records what was scouted, what was thrown away, what it cost, and the lessons we'd carry into the next pass.

## TL;DR

- **Repos in pool:** 107 fully processed today + 40 newly discovered (in-flight scout). 147 total.
- **PRs fetched today:** 19,417 (107 repos × 12-month window, capped at 800 per repo)
- **Dedup against 4,809-stub baseline:** 14,549 unique new PRs
- **Tier-1 repo allowlist filter:** 13,046 PRs went to the judge
- **Causality verdicts:** A=204, B=546, C=10,398, D=1,896, ERR=2
- **Today's wins:** 750 A+B
- **Grand total candidate PRs (cumulative):** 977
- **Total Gemini cost today:** ~$140 (Flex tier, 50% off Standard)
- **Wall clock:** ~14 hours scout + 17 min judge

## Funnel breakdown

### Stage 1 — Repo discovery

107 starting repos came from earlier rounds (`gh search code` + curated lists). For this pass we left them static and scouted in depth.

A separate discovery effort late in the day surfaced **40 fresh repos** (zero overlap), ≥500 stars, with confirmed tier-1 files. Method that worked: `gh search repos` with topics like `claude-code`, `claude-skills`, `mcp-server`, `vibe-coding`, plus WebFetch on awesome-claude-code / awesome-agents-md curated lists. Avoided `gh search code` because its secondary abuse-detection bucket was already exhausted from prior runs and recovers in hours.

Top discoveries by star count:

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

Sixteen of the 40 have rich SKILL.md trees (15-20 tier-1 files each) — strong signal these are skill-authoring-active repos. The full list: `/tmp/new_skill_repos.jsonl`.

### Stage 2 — PR fetching

`taskforge.scout` with `gh pr list --state merged --limit 800 --json …` against each of the 107 repos. Hard-capped at 12 months ago. Hit GitHub primary rate limit every hour (~5,000 calls); rate-limit-aware retry sleeps until reset. Total wall time: 10 hours for 107 repos = ~5.6 minutes per repo on average. Output JSONL: 19,417 rows.

Per-repo PR yield wasn't logged but ranged ~50-200 useful candidates (after `too_few_changes` / `too_many_files` / `too_old` / `label_skip` filters baked into scout).

### Stage 3 — Dedup

Two-key dedup against existing 4,809-stub corpus:

- `slugify(repo, title)` — semantic dedup
- `(repo, pr_number)` — strict dedup

Of 19,417 fetched: 4,868 dropped as duplicates (3,823 matched both keys, 1,045 matched slug only — likely PRs renamed but reused). **14,549 unique new PRs** survived.

### Stage 4 — Tier-1 repo allowlist

1,503 PRs dropped because their repos didn't appear in our `repo_tier1.json` (manually-curated mapping of repo → confirmed tier-1 file paths). A few rare repos in the scout output had recently added or removed their tier-1 files; this filter trusts the snapshot.

**13,046 PRs into the causality judge.**

### Stage 5 — Causality judge (Gemini 3.1 Pro Flex)

Each PR gets a structured-output verdict on whether the gold diff is causally shaped by the repo's tier-1 instruction files. Three useful verdicts (A, B, D) plus one discard (C):

| Verdict | Count | % | Definition |
|---|---|---|---|
| **A** | 204 | 1.6% | PR's diff includes changes to a tier-1 markdown file. Determined by file paths alone — no LLM call needed. |
| **B** | 546 | 4.2% | LLM-judged: code-only PR whose fix specifically applies a rule from a tier-1 file. |
| C | 10,398 | 79.7% | LLM-judged decorative — fix is determined by the bug, not by any rule. |
| D | 1,896 | 14.5% | LLM-judged unscaffoldable — platform-specific (Android/iOS/macOS/CUDA), >500-line refactor, no testable behavior, etc. |
| ERR | 2 | 0.0% | Judge call failed end-to-end. |

5.7% A+B yield. The "short-circuit" path (verdict by file-path matching, no LLM) handled 3,876 of the 13,046 PRs — all the As plus the 3,672 C-unfetchable cases (PR's tier-1 markdown didn't exist at base commit, default-classed as decorative). The remaining 9,171 PRs got a real LLM call.

## Top contributing repos

### Class B (code-fix-follows-rule) by repo

The interesting bucket. These tasks test "did the agent read the instructions and apply them when fixing code" — the canonical hypothesis.

| Count | Repo |
|---|---|
| 42 | openai/openai-agents-js |
| 42 | remix-run/remix |
| 41 | astral-sh/uv |
| 30 | huggingface/transformers |
| 27 | prefecthq/prefect |
| 26 | apache/superset |
| 25 | vitessio/vitess |
| 22 | cloudflare/workers-sdk |
| 22 | pulumi/pulumi |
| 20 | weaviate/weaviate |
| 17 | dotnet/runtime |
| 15 | anomalyco/opencode |
| 12 | SeleniumHQ/selenium |
| 11 | effect-ts/effect |
| 10 | astral-sh/ruff |

OpenAI agents-js, Remix, and Astral's uv are the top three — all repos with very mature CLAUDE.md / AGENTS.md adoption that explicitly tell the agent how to handle cookbook generation, lockfile regen, and migration patterns.

### Class A (markdown-edit) by repo

| Count | Repo |
|---|---|
| 22 | ant-design/ant-design |
| 9 | openai/openai-agents-js |
| 9 | vitessio/vitess |
| 8 | microsoft/playwright |
| 7 | PRQL/prql |
| 7 | dotnet/maui |
| 7 | remix-run/remix |
| 7 | withastro/astro |
| 6 | apache/airflow |
| 6 | dotnet/runtime |
| 6 | mlflow/mlflow |
| 5 | All-Hands-AI/OpenHands |
| 5 | dotnet/efcore |
| 5 | gradio-app/gradio |
| 4 | PostHog/posthog |

ant-design dominates with 22 — they actively curate CLAUDE.md and ship one PR per agent-instruction tweak.

## Cost

| Item | Cost |
|---|---|
| GitHub API | $0 (free tier, just rate-limited) |
| Gemini scout-judge (today's 9,171-prompt Flex pass) | ~$140 |
| Gemini ERR-recheck batch (287 prompts) | ~$3 |
| Gemini C-unfetchable-recheck batch (890 prompts) | ~$10 |
| Failed batch attempt (cancelled, no charge) | $0 |
| Discovery subagent (web search + repo metadata) | $0 |
| **Total Gemini** | **~$153** |

For the projected scaffolding pass on the 977-PR pool: ~$8 per PR via the `oneshot_scaffold` pipeline (Opus 4.7 in E2B sandbox) → **~$7,800**. Of those 977, expect ~60% to pass the Docker oracle on the first scaffold attempt → ~580 new runnable tasks, against the existing 442 = 1,022-task target reached.

## Batch vs Flex experiment

Initially submitted the 9,171-prompt classification job as a **Gemini batch** with structured output (camelCase JSONL, `responseSchema`, `thinkingConfig.thinkingBudget=512`). Batch is advertised at 50% off Standard with up to 24h SLA but typically minutes-to-hours.

**Outcome:** the batch ran 3+ hours in `JOB_STATE_RUNNING`, with `update_time` freshness degrading from sub-second to 8 min stale to 16 min stale. Google's API exposes no `completion_stats` mid-run, so we couldn't tell if it was 95% done or stuck. We cancelled at the 3-hour mark and switched to **Flex tier** (same 50% off pricing as batch, but synchronous endpoint).

| | Batch (cancelled) | Flex |
|---|---|---|
| Pricing | 50% off Standard | 50% off Standard (identical) |
| Endpoint | Async, file-based | Sync `generateContent` |
| Wall clock for 9,171 prompts | 3h+ and counting (cancelled) | **17 min** at concurrency 32 |
| Per-call latency | (opaque) | ~2-3s typical |
| Failure modes | Opaque queueing; no progress hint | 429 / 503 fail-fast, client retries |
| Visibility | `state` only | Per-call results streaming |

Flex is the right default for medium-sized classifier passes. Same per-token cost as batch but you get throughput visibility and incremental results. The integration was a one-line config: `service_tier=ServiceTier.FLEX` on `GenerateContentConfig`.

The earlier "Flex tier rejected — `serviceTier` field doesn't exist" memory note was a stale-SDK / wrong-spelling artifact; the canonical Python SDK field is **`service_tier`** (snake_case).

## What was thrown away

We didn't migrate or recover everything:

- **3,672 PRs** classified as "C / tier-1 unfetchable" — their tier-1 markdown didn't exist at the PR's base commit (PR predated the repo adopting CLAUDE.md/AGENTS.md). We default-classified these as decorative without an LLM call. Recovery would require either (a) loosening the rule and re-fetching at HEAD, or (b) accepting that pre-adoption PRs aren't relevant. We chose (b).
- **890 PRs** in the C-unfetchable rerun yielded only 5 A wins. Confirms the default-decorative is the right call.
- **287 ERR-row reruns** yielded 18 wins (9 A + 9 B). Some of these were `lobe-chat` PRs hitting an httpx redirect bug (the repo had moved); we fixed by passing `follow_redirects=True` and recovered them.

## Lessons

1. **Add `follow_redirects=True` to every httpx GitHub client.** Several repos have moved (e.g., `lobehub/lobe-chat` was a redirect destination). Without redirect-following, every PR from a moved repo silently becomes ERR.
2. **JSONL camelCase, not snake_case.** Gemini batch JSONL uses raw REST format (`generationConfig`, `responseMimeType`), not the SDK's snake_case. Discovered after a `400 INVALID_ARGUMENT` storm on the first batch attempt.
3. **Drop heavy GraphQL fields.** `gh pr list --json files,…` causes GraphQL 504 storms on busy repos (PostHog, OpenHands). The `files` field is what triggers it; we drop it and re-fetch per PR if needed.
4. **Most "short-circuit" hits are misleadingly framed.** Our short-circuit count tracks "didn't need LLM call", but ~95% of those are actually tier-1-unfetchable C dropouts, not class-A wins. We initially projected ~2,800 A wins from 30% short-circuit rate; the real number was 204. Make sure progress logs separate the two paths.
5. **The 4,809-stub baseline was already tight.** Re-judging the 4,265 C-classified rows wasn't worth it; only 890 of them (the unfetchable subset) had ever bypassed the LLM. The rest were correctly judged on the first pass.
6. **Discovery is bursty-cheap, scouting is slow.** A discovery subagent finds 40 high-quality repos in 6 minutes via topic search + WebFetch. Scouting those 40 will take 4+ hours of GH-rate-limited PR enumeration. Run discovery hot, scouting cold.

## Class composition for the RL training corpus

The 977-PR pool breaks down into the three task shapes we now distinguish in `eval_manifest.yaml` via `task.kind`:

| Kind | Source class | Approx count | What it tests |
|---|---|---|---|
| `code_fix` | Class B (code follows rule) | ~600 | The canonical hypothesis. Agent reads a SKILL.md / AGENTS.md rule, applies it during a code change. |
| `code_with_config` | Class A subset (PR has both code AND markdown changes — bundled) | ~140 | Agent updates a rule AND ships the code change that follows it. Tests cross-file consistency. |
| `markdown_authoring` | Class A subset (PR is markdown-only) | ~70 | Agent writes a SKILL.md from scratch given a brief. Adjacent skill, not the core hypothesis. |

The split inside Class A (bundled vs markdown-only) has to be done at scaffold time by counting how many of the PR's `changed_files` are tier-1 paths. Pure markdown-only is roughly 30% of A based on spot-checks; the rest is bundled.

For RL training, we'd weight heavily toward `code_fix` (the canonical signal) and `code_with_config` (cross-file consistency), and use `markdown_authoring` as a small diversity subset (~5-10%).

## Next steps

1. **Wait for scout-new-40 to finish** (~4-5 hours). Judge with Flex (~$30, 17 min). Expected yield ~100-300 more wins.
2. **Run scaffolding pass** on the 977-PR pool through `oneshot_scaffold`. ~$8/PR × 977 = ~$7,800. Expect 60% pass rate → ~580 new runnable tasks.
3. **Build + push GHCR images** for the 399 tier-A scaffolded tasks (workflow `push-images.yml` is triggered, in progress).
4. **Distractor-generation pass** on the 91 tasks scaffolded last night that have rubric but missing distractor block.
5. **Class-A triage script** to split bundled vs pure-markdown via `changed_files` analysis, set `task.kind`, and route into `harbor_tasks_agentmd_edits/` vs `harbor_tasks_md_authoring/`.

## Artifacts on disk

- `pipeline_logs/batch_judge_2026_04_25/deep_scout_judges.csv` — 13,208 verdict rows from today's pass
- `pipeline_logs/batch_judge_2026_04_25/err_rechecks.csv` — 287-row ERR-recheck output
- `pipeline_logs/batch_judge_2026_04_25/c_unfetchable_rechecks.csv` — 890-row C-unfetchable-recheck output
- `scouted_deep_2026_04_25.jsonl` — 19,417 raw scout rows
- `scouted_deep_2026_04_25_unique.jsonl` — 14,549 deduped
- `/tmp/new_skill_repos.jsonl` — 40 newly-discovered repos
- `scripts/audit_stub_batch.py` — batch judge with rate-limit-aware GH fetch
- `scripts/judge_flex.py` — Flex sync judge (drop-in replacement for batch JSONL)
- `scripts/dockerfile_shallow_migrate.py` — Dockerfile full-clone → shallow migration
