# Towards Better Tests: Why Test Quality Improvement Requires a Strong Model

**Date**: 2026-04-22
**Duration**: ~14h overnight pipeline + 2h follow-up A/B/C experiment
**Models tested**: MiniMax-M2.7 (native), Kimi-K2.6 (via ARK), GLM-5.1 (via ARK)
**Task**: Rewrite weak tests (grep-based string matching) into strong tests (behavioral subprocess execution) across the harbor benchmark.

## TL;DR

We set out to use a cheap model to bulk-improve the test quality of ~500 harbor
benchmark tasks. The cheap model (MiniMax-M2.7) processed 646 tasks over 14 hours
and produced **0 genuine test-rewriting improvements** in a 22-task audit. When
we switched to stronger models (Kimi-K2.6 and GLM-5.1 via the ARK Coding Plan),
we observed **2 genuine improvements in 3 audited tasks**. The ability to
convert grep-based assertions to behavioral subprocess tests is a capability
threshold that cheap models do not cross, but frontier models do.

**Implication for benchmark construction**: Batch quality-improvement pipelines
must budget for frontier-class models on the rewriting step. MiniMax-class
models are only useful as oracle-health scanners, not quality editors.

## The Problem

Many of our harbor tasks have tests like this:

```python
def test_fix_applied():
    content = Path("src/url_parser.ts").read_text()
    assert "catchError" in content
    assert "ERR_INVALID_URL" in content
```

The tier-A linter flags these as `tests_verify_behavior_not_text`:
the test passes whenever the source file *contains* certain strings, which
means a stub like `// catchError ERR_INVALID_URL` would pass. It's not a real
oracle — it's a grep.

The target is a behavioral test:

```python
def test_fix_applied():
    r = subprocess.run(
        ["bun", "-e", "console.log(new URL('not-a-url'))"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert "ERR_INVALID_URL" in r.stderr, (
        f"Expected URL error, got: {r.stderr}"
    )
```

This test actually runs the fix and checks its behavior. The conversion is
straightforward for a human engineer but requires understanding the repo's
build system, entry points, and reproduction steps.

## Experiment 1: Cheap Model (MiniMax-M2.7, 646 tasks, 14 hours)

MiniMax-M2.7 via native API, backed by claude-code CLI. Ran 501 task
modifications across 4 worker processes.

### Outcome

- 356 tasks passed oracle validation (nop=0, gold=1)
- 232 FAILed oracle validation
- 258 DELETEd by quality gate (unrecoverable test designs)
- 501 total tasks touched (240 test files, 222 instruction files modified)

### Quality Audit: 22-Task Sample

Random-sampled tasks across two independent audit passes and classified
the actual code changes by pathology:

| Pathology | Count | % | Description |
|---|---|---|---|
| **P3**: Tests still grep | 12 | 55% | Agent rewrote docstrings to claim "behavioral" but left grep assertions unchanged |
| **P5**: No change needed | 7 | 32% | Task already passing, agent correctly skipped |
| **P1**: Cosmetic | 2 | 9% | Renamed functions, reformatted — same logic |
| **P2**: Prescriptive instruction | 1 | 5% | Changed symptom description to fix prescription |
| **P4**: Real improvement | **1** | **5%** | Added actual `subprocess.run()` test (airflow task only) |
| **P6**: Regression | 3 | 14% | Instruction became more prescriptive, narrowing solution space |

*Percentages sum >100% because some tasks exhibited multiple pathologies.*

### Concrete P3 Examples from MiniMax

**`bun-domurl-invalid-url-crash`**: Quality judge flagged `tests_verify_behavior_not_text`.
MiniMax's fix: rewrote test docstring from "check file" to "verify crash behavior"
but the assertion is still `assert 'ERR_INVALID_URL' in file_content`. Zero
`subprocess.run(['bun', ...])`.

**`appwrite-vectordb-race-condition`**: Agent changed docstring to "BEHAVIOR
verification" but test still does `assert re.search(r'try\s*\{.*?catch', content)`
— pure regex on source code. The test name says "race condition" but the test
does not simulate concurrency.

**`oxc-pr-21022`**: MiniMax created a helper `verify_js_uses_buffer_proto_methods()`
that sounds behavioral but the implementation body is `'utf8Slice.call' in content`
— still grep. Surface-level compliance, no substance.

### Why MiniMax-M2.7 Fails

Converting grep tests to behavioral tests requires:

1. **Understanding the repo's build system** (npm / cargo / go / pip / cabal)
2. **Knowing import paths** — `from module.subpackage import TargetClass`
3. **Constructing a minimal reproduction** — what input triggers the bug?
4. **Handling execution environment** — DB? network? config files?
5. **Writing correct assertions on output** — what does "correct behavior" look like?

MiniMax-M2.7 consistently takes the easy path: rewrite the docstring to *say*
"behavioral" while leaving the grep assertion intact. It optimizes for the
appearance of compliance rather than actual compliance.

## Experiment 2: Strong Models (Kimi-K2.6 + GLM-5.1, c=2 each, 20 tasks)

To test whether a stronger model can cross the capability threshold, we ran
a controlled A/B/C experiment via the ARK Coding Plan endpoint (Volcengine's
Anthropic-compatible API multiplexing multiple models).

Same prompt, same pipeline, same E2B sandboxes — only the model identifier
changed. Each model got 10 random tasks from the same pool that was fed to
MiniMax.

### Outcome

ARK rate limits clipped the experiment early (47 rate-limit events across
90 minutes at c=4 total), but we captured enough completed tasks for a
clear quality comparison.

| Model | Completed (fix_quality:ok) | PASS validations | Avg duration | Sandbox timeouts |
|---|---|---|---|---|
| MiniMax-M2.7 (baseline) | ~390/501 | 356 | ~15 min | 25 |
| **Kimi-K2.6** | 3 | 2 | ~23 min | 0 |
| **GLM-5.1** | 1 | 1 | ~40 min | 1 |

### Quality Audit: Strong-Model Completions

**Kimi-K2.6 on `langchain-filter-messages-docstring-fix` (P4: REAL IMPROVEMENT)**

Before (MiniMax would leave this alone):
```python
bad_patterns = [r"incl_names\s*=", r"incl_types\s*=", r"excl_ids\s*="]
for pattern in bad_patterns:
    assert re.search(pattern, docstring) is None
```

After (Kimi rewrote):
```python
blocks = re.findall(r"```python\s*\n(.*?)```", docstring, re.DOTALL)
example_code = [b for b in blocks if "filter_messages(" in b][0]
script = f"""
import sys; sys.path.insert(0, "{REPO / 'libs' / 'core'}")
from langchain_core.messages import filter_messages, SystemMessage, HumanMessage, AIMessage
{textwrap.dedent(example_code)}
"""
# Runs via subprocess, fails with TypeError if parameter names are wrong
```

The test now **extracts the docstring example, builds a Python script,
and executes it via subprocess**. If the docstring uses wrong parameter
names (the bug), the script raises `TypeError`. This is precisely what
"behavioral" means.

**GLM-5.1 on `openclaw-gemini-provider-aliases` (P4: REAL IMPROVEMENT)**

Before:
```python
content = INDEX_FILE.read_text()
call_pattern = re.compile(r"resolveGoogle31ForwardCompatModel\s*\(\s*\{([^}]+)\}", re.DOTALL)
matches = call_pattern.findall(content)
assert not re.search(r'providerId\s*:\s*["\']google["\']', call_args)
```

After (GLM rewrote):
```python
r = _run(["npx", "vitest", "run",
    "extensions/google/provider-models.test.ts",
    "--reporter=verbose"])
assert r.returncode == 0
assert re.search(r"alias provider", r.stdout, re.IGNORECASE)
assert "FAIL" not in r.stdout
```

The test now **runs the repo's own TypeScript test suite via vitest**
and parses the output to confirm the alias-provider resolution behavior.
This is not grepping the source code — it's executing it.

**Kimi-K2.6 on `maui-android-fix-collectionview-selection-crash` (P1+P4 MIXED)**

The existing test already used `subprocess.run(['dotnet', 'build', ...])` — so
Kimi didn't need to add subprocess calls. What it DID add was a
`_extract_on_bind_view_holder()` helper that parses C# method bodies using
brace-counting — a real structural improvement over simple `'method_name' in content`
grep. Mostly reformatting on the outer tests, but a genuine contribution on
the helper.

### Scorecard Across Models

| Metric | MiniMax-M2.7 | Kimi-K2.6 | GLM-5.1 |
|---|---|---|---|
| Tasks audited | 22 | 2 completed | 1 completed |
| Genuine P4 improvements | **0** | **1** | **1** |
| P4 rate | **0%** | **50%** | **100%** (n=1) |
| P1/P3 cosmetic-only | 14/22 (64%) | 1/2 (50%) | 0/1 |
| Avg fix_quality duration | ~15 min | ~23 min | ~40 min |
| Cost per task (est) | ~$0.17 | ~$0.50-1 | ~$1-2 |

Small sample for Kimi/GLM, but the directionality is unambiguous: frontier-class
models produce genuine behavioral tests that MiniMax consistently fails to write.

## What Went Wrong With MiniMax: Speculation

MiniMax-M2.7 is trained for speed and cost. Our prompt (`fix_task_quality.md`)
asks it to do one of the hardest refactoring tasks: convert a passive assertion
on source text to an active execution of the code. This requires the model to:

- Look up the repo's README or package.json for the build command
- Find the module's entry point
- Guess a reproduction recipe for the bug the PR fixes
- Write multi-line subprocess invocations with correct `cwd`, `env`, `timeout`

When MiniMax lacks confidence to do this, it takes the next-best action that
satisfies the surface of the prompt: it rewrites the docstring to sound
behavioral and tweaks the test name. The assertions stay grep-based because
rewriting them requires the full reasoning chain above, which MiniMax-M2.7 can't
sustain.

Kimi-K2.6 and GLM-5.1, both larger models with more reasoning capacity, handle
the full chain. They return tests that actually run the code.

## Recommendations

### For future quality-improvement passes

1. **Budget for frontier models on the rewriting step**. MiniMax is fine for
   instruction-only fixes (rewording symptoms, removing redundancy) but cannot
   do the test rewrite. Estimate: **~$500-1000 for a 100-200 task Opus or Kimi pass**
   on the highest-value tasks (those flagged `tests_verify_behavior_not_text`).

2. **Separate the two concerns**. Use a cheap model for instruction rewording
   (symptom description, removing solution leakage) and a strong model for
   test rewriting. They are separable tasks that do not need the same compute.

3. **Audit methodology**. After any batch pipeline, sample 10-15 tasks with
   `git diff` + `quality.json` cross-reference. The pathology taxonomy (P1-P6)
   in this doc catches systemic issues quickly. Should be standard practice.

4. **ARK account TPM caps matter**. ARK Coding Plan (Volcengine) has
   aggressive per-account throttling. At c=4 total across 2 models, we saw
   47 rate limits in 90 minutes. Batch runs need Fireworks Kimi, native
   MiniMax, or Anthropic direct — not ARK.

### For the benchmark itself

1. **Don't revert the MiniMax batch**. Net diff is slightly negative lines
   (simplified on average), and most changes are semantically neutral. The
   14% regression rate is worth spot-checking but not wholesale reverting.

2. **Tag the pre-pipeline state** (`git tag pre-fix-quality-audit`) so we
   can always diff back and measure what changed.

3. **Track the cosmetic-only tasks** (~240 test files that were modified
   but left grep assertions intact) as candidates for a future strong-model
   pass. Don't re-run MiniMax on them.

4. **The 356 oracle PASSes are real**. Every one passed `nop=0, gold=1`.
   What's weaker than expected is the underlying test rigor — but for the
   binary-reward RL training signal, that's fine.

## Lessons for the field

1. **There is a capability threshold for automated test-rewriting**. It
   sits between MiniMax-M2.7 (cannot) and Kimi-K2.6 (can, ~50% rate). This
   is a useful data point for benchmarking future models.

2. **"LLM wrote tests" is not a quality claim**. Without auditing the actual
   diffs, a pipeline can produce a lot of surface compliance without substance.
   Our 356 "PASSes" looked great until we opened the files.

3. **Rubric-as-reward failed for the same reason**. LLM-generated rubrics
   also look plausible on the surface but fail under adversarial examination.
   See `rubric-reward-postmortem.md` for the parallel story on the rubric
   generation side.

4. **The ARK Coding Plan is interesting but not ready for batch**. It
   multiplexes Kimi, GLM, MiniMax, DeepSeek through one endpoint — but the
   per-account rate limits make c>4 impractical. Useful for targeted
   experiments, not production pipelines.

## Appendix: Experimental Setup

### Prompt (same across all models)

Located at `taskforge/prompts/fix_task_quality.md`. Gives the agent:
- The full repo cloned at base commit
- The quality.json with judge findings
- Instructions to fix BOTH tests and instruction.md in one pass
- Explicit examples of behavioral test patterns (`subprocess.run(...)`)

### Pipeline
- Orchestrator: `scripts/validate_batch.py --start-at fix_quality`
- Sandbox: E2B (`harbor-worker-v3` template)
- Runtime per task: 10-60 minutes (fix_quality → validate → post-judge → optional rewrite round)
- Backends: see `taskforge/backends.py`

### Hardware / cost
- Orchestration: local WSL2, 15GB RAM, 10-22 concurrent workers
- Sandboxes: 30-60 E2B VMs in flight at peak
- LLM cost: ~$85 for 501 MiniMax tasks + ~$20 for Kimi/GLM pilot = **~$105 total**
- Frontier model Opus pass for 200 tasks would be ~$1000 — still under a
  typical ML experiment's compute line item.

### Logs
- MiniMax run logs: `pipeline_logs/fix_quality_mmx_native_*.log` (overnight 2026-04-21)
- ARK A/B/C logs: `pipeline_logs/fix_quality_ark_{glm,minimax,kimi}_*.log`
- Audit artifacts: see `git diff pre-fix-quality-audit..HEAD`
