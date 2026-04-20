# Why LLM-Generated Rubrics Failed as Reward Signal

**Date:** 2026-04-20
**Status:** Post-mortem / design decision

## TL;DR

We attempted to use LLM-generated convention-following rubrics (Tracks 3 and 4)
as part of the RL reward signal for agent training. After generating rubrics
for 1000+ tasks and running an 8-task controlled evaluation, we found that
**rubric scores do not discriminate between agents that solve the task and agents
that don't**. We are demoting rubrics to a monitoring/diagnostic signal and using
binary outcome reward (Track 1: tests pass or fail) as the sole training signal.

---

## 1. What we tried

Our evaluation architecture has four tracks:

| Track | Signal | Method |
|-------|--------|--------|
| 1. Code correctness | Did the agent fix the bug? | Deterministic tests (test.sh) |
| 2. Config edits | Did the agent update config files? | Gold diff comparison |
| 3. Positive rubric | Does the fix follow repo conventions? | LLM judge (Gemini) scores agent diff against rules extracted from CLAUDE.md / AGENTS.md |
| 4. Distractors | Did the agent ignore irrelevant conventions? | Inverted LLM judge — passes when agent did NOT apply a plausible-but-wrong rule |

The idea was that Tracks 3 and 4 would capture a dimension of quality beyond
"does the code work" — specifically, whether the agent reads and follows project
conventions when writing its fix. This would reward agents that engage with
agent instruction files rather than just pattern-matching the bug.

We tried three generators for rubric rules:
- **Gemini** (structured output with `responseSchema`)
- **Kimi** (with Gemini validation loop)
- **Codex / GPT-5.4** (with `cat -n` file reading + `--output-schema`)

## 2. What we found

### 2.1 Five systemic pathologies in generated rubrics

An 8-task deep-dive audit (Opus vs Kimi, April 2026) examined ~48 rubric rules
and ~24 distractor rules across tasks from 8 different repos:

| Pathology | Prevalence | Description |
|-----------|-----------|-------------|
| **Tautological rules** | ~50% | Rules that describe what the gold solution does, not pre-existing conventions. Any correct solution passes automatically. |
| **Duplicates** | ~17% | Same rule rephrased 2-4x within a single task's rubric. |
| **Redundant with Track 1** | ~15% | Rules already tested programmatically in test.sh, re-added as LLM-judged rules. |
| **Wrong line numbers** | ~30% | Gemini hallucinated line references (off by 3-80 lines). Paths were accurate. |
| **Wrong-scope distractors** | ~60% | Distractor rules pulled from unrelated config files in the same repo. |

After dedup and removing Track 1 redundancies, only **~15% of rubric rules were
unique, non-trivial, and actually tested convention-following**. Of those, ~4%
were genuinely hard (would distinguish a convention-aware agent from one that
ignores config files).

### 2.2 The smoking gun: rubric doesn't discriminate

In our controlled evaluation, Kimi scored **6/6 on Track 3 rubric for
nextjs-status-task — without solving the task at all**. Its code changes were
wrong, but the rubric rules were tautological enough that any plausible-looking
diff passed them.

Across 8 tasks:
- **Track 1 (tests):** Opus solved 3/8, Kimi solved 1/8 — clear discrimination
- **Track 3 (rubric):** Both models scored 78-83% — no discrimination
- **Track 4 (distractors):** Both models scored 100% — complete ceiling effect

Track 3 measured "does the diff look reasonable" rather than "did the agent
follow project conventions." Track 4 was too easy because agents simply don't
apply random conventions unprompted.

### 2.3 The fixes helped but didn't solve the core problem

We iterated on the pipeline:

1. **Codex/GPT-5.4 replaced Gemini for extraction** — fixed line number drift
   (100% accuracy), but tautological rules persisted because the problem is in
   the *task definition*, not the *extraction accuracy*.

2. **Kimi→Gemini→Kimi validation loop** — caught 25-75% of hallucinated rules
   per task, improving precision. But high-precision tautological rules survived
   validation because they're *technically correct* — they just don't test
   anything meaningful.

3. **Anti-tautology gate** — rejected rules semantically equivalent to
   instruction.md. Caught some, but the boundary between "convention the
   solution follows" and "description of the solution" is genuinely fuzzy.

4. **Path-proximity filtering for distractors** — improved scope relevance,
   but didn't solve the ceiling effect (agents don't apply random conventions
   regardless of scope).

## 3. Why this is fundamentally hard

Generating discriminative convention-following rubrics requires solving a
problem that is, in some sense, harder than the task itself:

**The circularity problem.** To generate a rubric rule, you need to identify a
convention in a config file that (a) the gold solution follows, (b) a naive
solution might violate, and (c) is genuinely a pre-existing convention rather
than a description of the solution. But the generator sees the gold diff, and
any LLM will reverse-engineer "conventions" from it. The anti-tautology gate
helps, but the boundary is irreducibly fuzzy — many real conventions are
indistinguishable from descriptions of correct code.

**The relevance problem.** Repos have dozens of conventions in their config
files. Most are irrelevant to any specific bug fix. Determining which
conventions *should* apply to a specific code change requires understanding the
change deeply enough that you've essentially already evaluated it. This is the
same judgment we're trying to train the agent to make.

**The discrimination problem.** Even when a rubric rule is valid and relevant,
it only adds training signal if agents sometimes violate it. In practice, most
convention violations are things like "use tabs not spaces" or "run the
formatter" — agents either always follow them (because their training data
includes the convention) or the violation is cosmetic. Rules that actually
distinguish convention-aware agents from convention-ignorant ones are rare
(~4% in our audit).

**The evaluation-of-evaluation problem.** Validating rubric quality requires
human judgment at scale. Our 8-task audit took ~4 hours of manual review for
~72 rules. Scaling this to 1000+ tasks is impractical, which means we can't
confidently characterize rubric quality across the full dataset.

## 4. Decision: outcome reward + rubric as monitoring

### Primary reward signal: binary outcome (Track 1)

All checks pass → reward `1`. Any check fails → reward `0`.

This matches every major SWE benchmark:
- SWE-bench / SWE-bench Verified: binary pass/fail
- Terminal-Bench: binary pass/fail
- SWE-smith: binary pass/fail
- R2E-Gym: binary pass/fail

Binary outcome reward is:
- **Deterministic** — same input always produces same reward
- **Discriminative** — clearly separates working fixes from broken ones
- **Reproducible** — no LLM judge variance between runs
- **Cheap** — no API calls for scoring

### Monitoring signals: rubric + distractors (Tracks 3 & 4)

Rubric and distractor scores are still computed and logged for every trial, but
they do NOT contribute to the RL reward. They serve as:

1. **Diagnostic signal** — when an agent solves a task, rubric scores help us
   understand *how* it solved it. Did it follow conventions? Did it take
   shortcuts? This is useful for qualitative analysis, not gradient updates.

2. **Convention-following proxy** — aggregate rubric scores across many tasks
   can indicate whether a model *tends to* engage with config files, even if
   individual scores are noisy. Useful for comparing model versions or training
   checkpoints at a macro level.

3. **Distractor early warning** — if a future model starts scoring <90% on
   Track 4, that signals it's over-indexing on config files and applying
   irrelevant conventions. This hasn't happened yet (ceiling effect at 100%),
   but it's worth monitoring as agents get more instruction-aware.

4. **Rubric pipeline development** — keeping the infrastructure running lets us
   iterate on rubric quality. If we eventually solve the discrimination problem
   (e.g., through human-curated rubrics for a small high-quality subset), the
   plumbing is already in place to incorporate it into reward.

### What this means for training

The RL training loop (`claude-code-rl-w-tinker/train.py`) uses only the binary
reward from `/logs/verifier/reward.txt`. The GRPO update treats each trajectory
as either success (reward=1) or failure (reward=0). No partial credit, no
rubric weighting.

This is a conservative choice. We lose the potential for richer signal about
*quality* of solutions. But given that our rubrics don't reliably measure
quality, including them in reward would add noise — potentially training agents
to optimize for tautological rules rather than actual convention-following.

## 5. Future direction: trace-derived rubrics

The fundamental mistake was deriving rubrics from the **gold diff** — this
creates circular, tautological rules. The better approach is to derive them
from **multiple SOTA agent traces**, comparing what successful agents do
differently from failed ones.

### Proposed approach

1. **Run N diverse agents per task** — Opus, Sonnet, Kimi, GPT-5.4, Codex,
   etc. Collect full traces: which files they read, which conventions they
   engaged with, what code patterns they produced.

2. **Partition traces by outcome** — successful (test.sh passes) vs failed.
   For each task, we get a set of {successful traces} and {failed traces}.

3. **Diff the behaviors** — identify conventions/patterns that appear in
   successful traces but NOT in failed traces. These are discriminative by
   construction. Examples:
   - "Successful agents read CLAUDE.md before editing src/parser.ts"
   - "Successful agents used the repo's custom test runner instead of Jest"
   - "Failed agents ignored the import boundary rule in AGENTS.md"

4. **Use Opus as anchor** — Opus has the highest solve rate (30% in our
   baseline). Its successful traces are the most reliable signal for what
   "convention-aware problem solving" looks like. Compare Opus's successful
   traces against weaker models' failed traces for maximum contrast.

5. **LLM-summarize into rubric rules** — a judge model reads the trace diff
   and extracts rubric rules. These rules are grounded in observed behavior
   differences, not in the gold diff.

### Why this solves the core problems

| Problem | Gold-diff approach | Trace-diff approach |
|---------|-------------------|---------------------|
| **Circularity** | Rules describe what the solution does | Rules describe what distinguishes success from failure |
| **Discrimination** | 50% of rules are tautological — any diff passes | By construction, only discriminative rules survive |
| **Relevance** | Generator must guess which conventions matter | Agents naturally focus on relevant conventions; irrelevant ones don't appear in traces |
| **Scope** | Distractors pulled from random config files | Distractors are conventions that agents *actually* over-applied in failed traces |

### Requirements

- **Multiple agent runs per task** — expensive upfront, but we need this data
  for training anyway. Each eval run produces traces as a byproduct.
- **Trace logging infrastructure** — need to capture file reads, not just the
  final diff. Our trajectory logging (`research/trajectory-logging-design.md`)
  already captures tool calls.
- **Sufficient task coverage** — need enough tasks where at least one agent
  succeeds and one fails. Tasks that all agents solve (or all fail) produce
  no discriminative signal.

### Practicality check

This is a second-phase effort. It requires:
1. Running the eval across multiple models (already planned for model comparison)
2. Building a trace-diffing pipeline (new work, but conceptually simple)
3. Validating that trace-derived rules actually improve over gold-diff rules
   (human audit of ~50 tasks)

Until we have multi-model trace data, outcome-level reward remains the right
choice. But this is the path to eventually incorporating convention-following
into reward — grounded in what agents actually do, not what we imagine they
should do.

## 6. When to revisit

Rubric-as-reward becomes viable if:

1. **Trace-derived rubrics** demonstrate discrimination in a controlled eval
   (e.g., rules derived from Opus traces predict Sonnet success/failure).

2. **A generator achieves <10% tautological rate** on a held-out validation
   set, verified by human audit.

3. **Track 4 shows variance** — if agents start applying distractors, the
   distractor signal becomes informative and worth including in reward.

Until then, outcome-level reward is the honest choice.
