# Why LLM-Generated Rubrics Failed as Reward Signal

**Date:** 2026-04-20
**Status:** Post-mortem / design decision

LLM-generated convention-following rubrics (Tracks 3 and 4) do not discriminate between agents that solve a task and agents that don't. After 1000+ tasks of rubric generation and an 8-task controlled eval, we are demoting rubrics to a monitoring/diagnostic signal and using binary outcome reward (Track 1) as the sole RL training signal.

## 1. What we tried

| Track | Signal | Method |
|---|---|---|
| 1. Code correctness | Did the agent fix the bug? | Deterministic tests in `test.sh` |
| 2. Config edits | Did the agent update config files? | Gold diff comparison |
| 3. Positive rubric | Does the fix follow repo conventions? | LLM judge (Gemini) scores agent diff against rules from `CLAUDE.md`/`AGENTS.md` |
| 4. Distractors | Did the agent ignore irrelevant conventions? | Inverted LLM judge — passes when agent did NOT apply a plausible-but-wrong rule |

Tracks 3 and 4 were intended to capture a quality dimension beyond "does the code work" — whether the agent actually engages with agent instruction files. Three generators were tried: Gemini (structured output with `responseSchema`), Kimi (with Gemini validation loop), and Codex/GPT-5.4 (with `cat -n` reading + `--output-schema`).

## 2. The smoking gun

Kimi scored **6/6 on Track 3 rubric for `nextjs-status-task` while solving 0/1 on Track 1**. The code was wrong; the rubric rules were tautological enough that any plausible-looking diff passed.

Across 8 tasks (Opus vs Kimi controlled eval, April 2026):

| Track | Opus | Kimi | Discrimination? |
|---|---|---|---|
| 1 (tests) | 3/8 | 1/8 | clear |
| 3 (rubric) | 78% | 83% | none |
| 4 (distractors) | 100% | 100% | ceiling |

Track 3 measured "does the diff look reasonable" rather than "did the agent follow project conventions." Track 4 was uninformative because agents simply don't apply random conventions unprompted.

## 3. Five systemic pathologies

Audit examined ~48 rubric rules and ~24 distractor rules across 8 repos.

| Pathology | Prevalence | Why it kills signal |
|---|---:|---|
| Tautological rules | ~50% | Describe what the gold solution does; any correct diff passes |
| Duplicates | ~17% | Same rule rephrased 2-4× within one task |
| Redundant with Track 1 | ~15% | Rule already deterministically tested in `test.sh` |
| Wrong line numbers | ~30% | Gemini hallucinated line refs (off by 3-80 lines); paths accurate |
| Wrong-scope distractors | ~60% | Pulled from unrelated config files in the same repo |

After dedup and Track 1 redundancy removal, **~15% of rules were unique and non-trivial**; only **~4% were genuinely hard** (would distinguish a convention-aware agent from one that ignores config files).

## 4. Fixes that didn't fix it

| Fix | Improved | Did NOT solve |
|---|---|---|
| Codex/GPT-5.4 replaced Gemini for extraction | Line accuracy → 100% | Tautology (problem is in task definition, not extraction) |
| Kimi → Gemini → Kimi validation loop | Caught 25-75% of hallucinated rules per task | High-precision tautological rules (technically correct, semantically empty) survive |
| Anti-tautology gate (reject rules ≈ instruction.md) | Caught some | Boundary between "convention solution follows" and "description of solution" is irreducibly fuzzy |
| Path-proximity filtering for distractors | Improved scope relevance | Track 4 ceiling effect (agents don't apply random conventions, regardless of scope) |

## 5. Why this is fundamentally hard

Generating discriminative convention-following rubrics is harder than the underlying task.

| Problem | Statement |
|---|---|
| **Circularity** | The generator sees the gold diff and reverse-engineers "conventions" from it. Any anti-tautology gate has to draw a line that's irreducibly fuzzy. |
| **Relevance** | Repos have dozens of conventions. Determining which apply to a specific change requires understanding the change deeply enough that you've essentially already evaluated it — the same judgment we want to train. |
| **Discrimination** | Even valid + relevant rules add signal only if agents sometimes violate them. Most violations are cosmetic (tabs vs spaces); the discriminative ~4% is rare. |
| **Eval-of-eval** | Validating rubric quality requires human judgment at scale. Our 8-task audit took ~4 hours for ~72 rules. Doesn't scale to 1000+ tasks. |

## 6. Decision: outcome reward + rubric as monitoring

### Primary reward: binary outcome (Track 1)

All checks pass → reward `1`. Any check fails → reward `0`. Matches every major SWE benchmark — SWE-bench / Verified, Terminal-Bench, SWE-smith, R2E-Gym.

| Property | Outcome reward | LLM-rubric reward |
|---|---|---|
| Deterministic | yes | no (judge variance) |
| Discriminative | yes (0% vs 100% gap) | no (78% vs 83%) |
| Reproducible across runs | yes | no |
| Cost per scoring | $0 | ~$0.01 / rule × 6-11 rules |

### Tracks 3 & 4 → monitoring

Still computed and logged per trial; do NOT contribute to RL reward. Roles:

| Role | What it gives us |
|---|---|
| Diagnostic | When agent solves a task, rubric scores explain *how* — convention-following vs shortcut |
| Macro convention-following proxy | Aggregate scores across many tasks compare model versions / training checkpoints |
| Distractor early warning | If Track 4 drops below 90%, the agent is over-indexing on configs. Today: ceiling at 100%. |
| Pipeline iteration | Plumbing stays in place for if/when we solve the discrimination problem |

### Training-loop consequence

`claude-code-rl-w-tinker/train.py` consumes only `/logs/verifier/reward.txt`. GRPO updates treat each trajectory as success (1) or failure (0). No partial credit, no rubric weighting. We lose richer quality signal but avoid training agents to optimize for tautological rules.

## 7. Future direction: trace-derived rubrics

The fundamental mistake was deriving rubrics from the **gold diff** — circular by construction. Better: derive them from **multiple SOTA agent traces**, comparing what successful agents do differently from failed ones.

```
                                      partition by Track 1 outcome
N agents × M tasks  ──►  traces  ──┬──►  successful traces (set S)
(Opus, Sonnet, Kimi,                │
 GPT-5.4, Codex, …)                 └──►  failed traces (set F)
                                                  │
                                                  │  diff behaviors
                                                  ▼
                                          patterns in S \ F
                                          (e.g. "read CLAUDE.md
                                           before editing src/parser.ts")
                                                  │
                                                  │  LLM summarize
                                                  ▼
                                          rubric rules grounded in
                                          observed behavior differences
```

Why this addresses the core problems:

| Problem | Gold-diff approach | Trace-diff approach |
|---|---|---|
| Circularity | Rules describe what the solution does | Rules describe what distinguishes success from failure |
| Discrimination | 50% tautological — any diff passes | Discriminative by construction |
| Relevance | Generator must guess relevance | Agents naturally focus on relevant conventions; irrelevant ones don't appear |
| Distractor scope | Pulled from random config files | Conventions agents *actually* over-applied in failed traces |

Anchor on Opus (highest baseline solve rate, 30%): its successful traces are the most reliable signal for what convention-aware problem-solving looks like.

### Requirements

- **Multi-model trace data** — produced as byproduct of model-comparison eval already planned.
- **Trace logging** — capture file reads, not just final diff. Tool-call logging already exists per `research/trajectory-logging-design.md`.
- **Sufficient task coverage** — need tasks where ≥1 agent succeeds and ≥1 fails. All-pass / all-fail tasks produce no discriminative signal.

### Practicality

Second-phase effort. Requires (1) multi-model eval (planned), (2) trace-diffing pipeline (new, conceptually simple), (3) human audit on ~50 tasks to validate that trace-derived rules outperform gold-diff rules. Until then, outcome-level reward is the right choice.

## 8. When to revisit

Rubric-as-reward becomes viable if any of:

| Trigger | Threshold |
|---|---|
| Trace-derived rubrics show discrimination in controlled eval | Rules from Opus traces predict Sonnet success/failure |
| A generator passes human audit on held-out validation | <10% tautological rate |
| Track 4 shows variance | Some agent applies distractors (today: ceiling 100%) |
