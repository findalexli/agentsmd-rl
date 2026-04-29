# Data Construction Methods

How we turn merged GitHub PRs into runnable benchmark tasks.

**Snapshot 2026-04-28: 3,172 active tasks across two corpora.**

| Part | Folder | Active | What the agent does |
|---|---|---:|---|
| **Markdown authoring** | `harbor_tasks_md_authoring/` | **2,482** | Writes / edits a skill or AGENTS.md / CLAUDE.md file |
| **Markdown following** | `harbor_tasks/` | **609** | Reads the skill / markdown files, then writes code that obeys them |
| Hybrid (small) | `harbor_tasks_agentmd_edits/` | 81 | Both — fix code AND update the markdown in one diff |

All shipped as Docker images on `ghcr.io/findalexli/agentsmd-rl/<task>:latest`.

A "skill / markdown file" throughout this doc means one of `CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `.cursor/rules/*`, `.claude/{rules,skills,agents}/*.md`, `.github/copilot-instructions.md`, and a few similar paths — the markdown files repos check in to tell coding agents how to behave.

## What we keep, what we drop

A merged PR is useful only when its gold diff is shaped by these markdown files. Every PR falls into one of four buckets:

| Gold diff content | Goes to | Why |
|---|---|---|
| Edits a skill / markdown file (possibly alongside code) | Markdown authoring | Tests authoring |
| Code-only fix that encodes a convention from a markdown file | Markdown following | Tests following |
| Code-only, fix is fully determined by the bug | Drop | Nothing markdown-specific to test |
| Platform-specific (iOS/Windows/GPU) or > 500-line refactor | Drop | Can't fit a Linux Docker oracle |

## Markdown authoring (2,482 tasks)

Built deterministically — no LLM at scaffold time. The gold patch IS the answer; tests are auto-derived from the most distinctive added lines.

**Discovery (dual-path, comprehensive scout 2026-04-28):**

- **Method A — code search.** 24 `gh api search/code` queries (`filename:SKILL.md`, `extension:mdc path:.cursor/rules/`, etc.) subdivided by path to break GitHub's 1,000-result cap → **15,608 unique repos**. Filter to ≥ 100 stars, not archived, not a fork (batched GraphQL) → 846 repos. Enumerate last 50 merged PRs per repo since 2025-09-01, keep ones touching a markdown path → **2,745 PRs**.
- **Method B — title search.** 28 queries like `is:pr is:merged SKILL.md in:title`, popular ones split into four disjoint date windows → **4,301 PRs**.
- **Merged + deduped:** **6,966 unique candidate PRs**.

The two methods miss different subsets (A misses repos that later deleted their markdown; B misses PRs that don't quote the file in the title — ~40 % of skill-authoring work). Combined coverage is near-exhaustive for ≥ 100-star public repos in the 8-month window.

**Funnel:**

| Stage | Output | Drop |
|---|---:|---:|
| 6,966 unique PRs | – | – |
| Path regex: every changed file is a markdown file (free) | ~3,800 | ~45 % |
| Name-dedup against existing tasks | 1,351 newly built | – |
| Quarantine: secret-shaped strings + unfetchable SHAs | 1,345 net new | 0.4 % |

Net new from this scout: **+1,345** (1,137 → 2,482). Per-PR yield: **19.3 %**.

**What the 2,482 gold patches actually touch.** Across the corpus, the 2,482 tasks change **5,509 markdown files in total** — 71 % of tasks touch a single file, 14 % touch two, the rest touch 3+ (the long tail goes up to 197 files in one batched skill-authoring PR).

Files that existed at the base commit are **modified** (an agent edits prose already there); files that did not are **created** (an agent writes a brand-new skill / instruction file from scratch); a few are **deleted** (agent removes a stale skill). Breakdown by canonical file kind:

| File kind                | Created (new in PR) | Modified (existed at base) | Deleted | Total touches | Tasks touching ≥ 1 |
|---|---:|---:|---:|---:|---:|
| `SKILL.md`               |  630 | 1,679 | 101 | 2,438 | 1,040 |
| `AGENTS.md`              |  479 |   391 |  15 |   911 |   743 |
| `CLAUDE.md`              |  306 |   319 |  42 |   670 |   552 |
| `.github/copilot-instructions.md` | 140 |  82 |   8 |   233 |   233 |
| `.cursor/rules/*.mdc`    |  210 |   188 |  68 |   476 |   126 |
| `.cursorrules`           |   16 |    12 |   6 |    34 |    33 |
| other markdown (e.g. `docs/*.md` paired with the above) | 346 | 306 | 79 | 747 | 185 |
| **Total**                | **2,127** | **2,977** | **319** | **5,509** | – |

So the corpus is **38.6 % create-from-scratch authoring** and **54.0 % edit-existing-prose authoring**, with the remainder removals or binary moves. Skills (`SKILL.md`) dominate by file-count (44 % of all touches) but `AGENTS.md` is close behind on a per-task basis. The "tasks touching ≥ 1" column doesn't sum to 2,482 because ~13 % of tasks touch markdown files of multiple kinds in the same PR (e.g. adds an `AGENTS.md` and a `CLAUDE.md` together).

A Gemini post-judge (`load_bearing`, `research_relevant`, `slop_score`, `verdict`) tags low-quality scaffolds for quarantine. Tasks default to active until judged. The 2026-04-28 pass was killed mid-flight by Gemini Flex timeouts; re-judge is queued.

## Markdown following (609 tasks)

Each task needs a custom behavioural test, so Claude Opus 4.7 in an E2B sandbox writes the Dockerfile, gold patch, and test, then runs `nop=0 / gold=1` as the oracle.

**Funnel:**

| Stage | Output | Drop |
|---|---:|---:|
| Walk recent merged PRs from 147 markdown-equipped repos | 19,417 | – |
| De-dup against existing tasks | 14,549 | 25 % |
| Re-confirm markdown still present at merge SHA | 13,046 | 8 % |
| **Gemini causality judge** — did the markdown shape the fix? | 546 (class B) | 94 % |
| Opus build + Docker oracle (`nop=0`, `gold=1`) | ~540 built | ~28 % |

Per-PR yield: **2.8 %**. The dominant cut is the causality judge — almost all merged PRs are bug fixes any agent could write without consulting any markdown. Class A (gold edits a markdown file) is routed back to the authoring corpus.

## Why the two pipelines look different

Markdown authoring gets a free path-regex shortcut: "the diff edits a markdown file" is visible in file paths alone. Markdown following has no syntactic short-circuit — there's no way to know whether a code-only fix encodes a documented convention without reading the diff, so every candidate costs an LLM call.

## Persistent raw outputs

Kept under `scout_data/` (gitignored) so the post-judge can be re-run without re-fetching:
- `code_search_repos_overnight_2026_04_27.txt` — 15,608 repos
- `code_search_phase2_overnight_2026_04_27.jsonl` — 2,745 PRs (Method A)
- `title_overnight_2026_04_27.jsonl` — 4,301 PRs (Method B)
- `final_merged_overnight_2026_04_27.jsonl` — 6,966 unique merged candidates

Per-row decision logs: `scouted_*_prejudged.decisions.csv`, `research/md_authoring_quality_judgments.json`. Discovery code in `scripts/discover_recent_skill_prs.py` and `scripts/discover_via_code_search.py`; batched GraphQL in `taskforge/gh_graphql.py`.

## What a markdown-authoring task contains

1. **`solution/solve.sh`** — verbatim git patch from the merged PR, applied with `git apply`. The canonical "gold answer".
2. **`eval_manifest.yaml`** — declarative metadata; `config_edits.gold_added` mirrors `solve.sh`.
3. **`tests/test_outputs.py`** — auto-derived grep harness. The scaffolder picks the 1–10 most distinctive added lines from the patch and emits one `assert "<verbatim line>" in text` per line.

The tradeoff is explicit: the test rewards reproducing the human's prose. An agent that paraphrases fails. We accept this because the alternative ("did the agent write *something* about X?") fails to discriminate. The post-judge rejects tasks where the gold is so generic that paraphrase is plausible.

## Limitations

- **Verbatim-grep tests** for the authoring corpus require literal-string reproduction; mitigated by the post-judge but not eliminated.
- **Single-classifier post-judge** (no second-classifier cross-check).
- **Closed file-path definition.** Novel agent-instruction formats need adding to the regex by hand.
- **Pending re-judge** — the 2026-04-28 post-judge pass was killed by Gemini Flex timeouts; ~50 of 1,351 new tasks have full `md_quality.json`, the rest are default-active until re-judge runs.
- **Recall floor** — < 100-star repos, archived/private repos, forks, and PRs older than 2025-09-01 are intentionally excluded.
