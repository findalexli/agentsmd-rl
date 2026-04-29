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

**Discovery + funnel:**

| Stage | Count |
|---|---:|
| Candidate merged PRs (code-search 2,745 ∪ title-search 4,301, deduped) | 6,966 |
| Every changed file is a markdown file (path regex, free) | ~3,800 |
| Not already scaffolded | 1,351 built |
| After secret / unfetchable-SHA quarantine | **+1,345 net new** (1,137 → 2,482) |

Per-PR yield 19.3 %. Discovery covers ≥ 100-star public repos, 8-month merge window.

**What the 2,482 gold patches touch (per-task averages):**

| File kind | Tasks | Avg files / task | Avg +lines / task | Median +lines | Avg net / task | Median net |
|---|---:|---:|---:|---:|---:|---:|
| `SKILL.md` | 1,040 | 2.34 | 139 | 47 | 107 | 29 |
| `AGENTS.md` | 743 | 1.23 | 106 | 45 | 93 | 35 |
| `CLAUDE.md` | 552 | 1.21 | 65 | 10 | 36 | 5 |
| `.github/copilot-instructions.md` | 233 | 1.00 | 121 | 94 | 109 | 87 |
| `.cursor/rules/*.mdc` | 126 | 3.78 | 291 | 65 | 158 | 60 |
| `.cursorrules` | 33 | 1.03 | 68 | 39 | 34 | 39 |
| other markdown | 185 | 4.04 | 260 | 67 | 150 | 52 |
| **Whole corpus** | **2,482** | **2.22** | **151** | **56** | **110** | **38** |

`+lines` = lines added by the gold patch; `net` = lines added minus lines removed. Tasks column doesn't sum to 2,482 because ~13 % of PRs touch markdown files of multiple kinds at once.

Read across:
- Median task adds **56 lines of markdown**; mean is 151 — the long tail (one PR adds 197 files / thousands of lines) pulls the mean.
- `CLAUDE.md` is the lightest unit of work (median 10 +lines): "tighten one bullet" edits to an existing canonical file.
- `copilot-instructions.md` is the most consistent (mean ≈ median ≈ 100): always one file, almost always written from scratch.
- `.cursor/rules/*.mdc` PRs are batched: 3.78 files at ~290 +lines each.

**File-status split** (created vs. modified at the base commit, summed across all 5,509 file touches): 2,127 created (39 %), 2,977 modified (54 %), 319 deleted, 86 binary/other. Skills skew toward edits (1,679 modified vs. 630 created); `AGENTS.md` and `copilot-instructions.md` skew toward fresh authoring.

A Gemini post-judge tags low-quality scaffolds for quarantine; the 2026-04-28 pass was killed by Gemini Flex timeouts and is queued for re-run.

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
