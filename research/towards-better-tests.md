# Towards Better Tests

*Diagnosis of the narrow-test problem in agent-native benchmarks, and an
experimental verdict on which LLMs can fix it.*

**Dates**: 2026-03-28 (original audit) → 2026-04-22 (experimental validation)
→ 2026-04-22 evening (60-task re-audit, findings revised)
**Supersedes**: `test-design-audit.md` (merged into this document)
**Related**: `rubric-reward-postmortem.md`, `agent-manifest-confounding.md`

---

## TL;DR

SWE-bench-style benchmarks (ours included) have a systemic quality problem:
most tests assert on the *shape* of source code (grep, AST, regex) rather than
on runtime *behavior*. OpenAI's
[analysis of SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)
attributed 59% of model failures to narrow/wide tests — tests that reject
correct alternatives or check things outside the problem statement.

We audited our own tasks and found the same pattern. We then tried to fix it
automatically with a cheap model (MiniMax-M2.7) over 646 tasks overnight.

**Headline (revised 2026-04-22 PM)**: A 60-task random re-audit of the full
modified population shows **23/60 (38%) P4 genuine improvements** (tests now
execute code via subprocess with behavioral assertions), **7/60 (12%) P6
regressions** (tests deleted or weakened), and ~50% neutral cosmetic/
prescriptive changes. This **contradicts the original 22-task audit's "0/22"
finding**, which over-indexed on early-run output and applied a strict-P4
threshold. See §2.3 Addendum.

The revised takeaway: cheap models produce a real-but-noisy signal. Budget
for a strong model to *filter* the output (revert the P6 regressions) rather
than to do the rewrites from scratch.

---

## Part 1 — The Problem

### OpenAI's two failure modes

From OpenAI's SWE-bench Verified postmortem:

1. **Tests reject correct solutions** (59.4% of audited failures)
   - **Narrow tests** (35.5%): enforce specific implementation details, reject valid alternatives
   - **Wide tests** (18.8%): check functionality not described in the problem statement

2. **Contamination**: all frontier models reproduce exact gold patches from training data

SWE-bench's gold standard design uses:
- **Fail-to-pass tests**: tests that FAIL on buggy code, PASS after correct fix
- **Pass-to-pass tests**: regression tests that PASS both before and after

Our original tests were mostly **structural/AST checks** with some behavioral
mocks. The audit below, conducted in March 2026 on 6 representative tasks,
showed the same narrow-test pathologies OpenAI described.

### Audit: 6 representative tasks

#### 1. `sglang-detokenizer-unbound-fix`
- **Current**: 3 AST/text checks + 1 behavioral mock (TEST 4)
- **Narrow**: TEST 1 requires exactly `manager = None` assignment; valid alternatives (inline init, try/except wrapping, `locals().get(...)`) are rejected
- **Silver lining**: TEST 4 already executes the except block with a mock that raises. That's SWE-bench quality.
- **Fix**: keep TEST 4, replace or soften TESTS 1–2 with a second behavioral test.

#### 2. `sglang-benchmark-empty-prompt`
- **Current**: 2 structural (AST `max(1,...)` + regex extract)
- **Narrow**: Requires literal `max(1, ...)`; rejects equivalent refactors (`min_val=1` variable, if-guard pattern)
- **Fix**: Replace with fail-to-pass that calls the loop with edge-case inputs and asserts all lengths ≥ 1.

#### 3. `sglang-hfrunner-hang-fix` ❌ *worst*
- **Current**: 4 structural, 0 behavioral
- **Narrow (severe)**: Requires `timeout` kwarg on `queue.get`; rejects `asyncio.wait_for`, polling-loop, `select`/`poll`. Requires string `is_alive`; rejects `exitcode is not None`. Requires `RuntimeError`; rejects `ChildProcessError`, `OSError`, `SystemExit`.
- **Fix**: Needs complete rewrite. Should mock a subprocess that dies and verify `forward()` returns/raises within a bounded time.

#### 4. `sglang-lscpu-topology-fix` ✅ *best*
- **Current**: 1 structural + 3 behavioral (mock subprocess with malformed/normal/empty inputs)
- **Quality**: Tests 2–3 are close to SWE-bench quality.
- **Fix**: Minor — soften TEST 1 to check behavior not AST pattern.

#### 5. `vllm-tool-parser-indexerror` ❌ *also worst*
- **Current**: 4 text/regex checks, 0 behavioral
- **Narrow (severe)**: TEST 4 literally requires the variable name `should_check` — this is the exact `pylint-dev__pylint-4551` anti-pattern OpenAI flagged (enforcing a variable name that's in the gold patch but not in the problem description).
- **Fix**: Complete rewrite. Construct a mock streaming scenario where the original `IndexError` occurs, assert it doesn't crash.

#### 6. `vllm-triton-cache-autotuning`
- **Current**: 3 AST/text + 1 behavioral exec
- **Narrow**: Requires `os.environ.setdefault(...)`; rejects `if X not in os.environ: os.environ[X] = ...` and `os.environ.get(...)` patterns that have identical semantics.
- **Fix**: Replace with two behavioral tests — "var is set when absent" and "pre-set value is preserved".

### Cross-cutting issues

**Structural vs behavioral counts across the 6-task audit:**

| Test Type | Count | SWE-bench Equivalent | Quality |
|---|---|---|---|
| AST pattern check | 14 | None | Low (narrow) |
| Text/regex search | 8 | None | Low (narrow) |
| Anti-stub | 6 | Pass-to-pass (partial) | Medium |
| Behavioral mock | 7 | Fail-to-pass | **High** |
| Behavioral exec | 2 | Fail-to-pass | **High** |

Only 9 of 30 checks are behavioral. The rest are narrow and fragile.

**Fail-to-pass coverage:**

| Task | Genuine fail-to-pass test? |
|---|---|
| sglang-detokenizer-unbound-fix | ✅ Yes (TEST 4) |
| sglang-benchmark-empty-prompt | Partial (regex sim) |
| sglang-hfrunner-hang-fix | ❌ No (all structural) |
| sglang-lscpu-topology-fix | ✅ Yes (Tests 2–4) |
| vllm-tool-parser-indexerror | ❌ No (all structural) |
| vllm-triton-cache-autotuning | Partial (exec extraction) |

**Contamination risk**: All 6 tasks come from merged PRs in public repos
(sglang 44k⭐, vllm 50k⭐). Any model trained on post-merge GitHub data has
likely seen the exact patches. Opus 4.6 scoring 1.0 on all 6 might partly
reflect this — see mitigation in §6.

---

## Part 2 — Can an LLM Fix It? Experimental Verdict

Given ~500 tasks with narrow tests, can we use an LLM to rewrite them in
bulk? We ran two experiments: one cheap, one strong.

### Experiment 1: MiniMax-M2.7 (646 tasks, 14 hours)

Ran `fix_task_quality.md` prompt (see `taskforge/prompts/`) across 4 worker
processes on Anthropic-compatible MiniMax API.

**Output**:
- 356 tasks passed oracle validation (nop=0, gold=1)
- 232 FAILed oracle validation
- 258 DELETEd by quality gate (unrecoverable tautological tests)
- 501 total tasks modified (240 test files, 222 instruction files)

**Audit — 22 sampled tasks classified by pathology**:

| Pathology | Count | % | Description |
|---|---|---|---|
| **P3**: Tests still grep | 12 | 55% | Docstring rewritten to claim "behavioral" but grep assertions unchanged |
| **P5**: No change needed | 7 | 32% | Task already passing, agent skipped |
| **P1**: Cosmetic | 2 | 9% | Rename/reformat, same logic |
| **P2**: Prescriptive instruction | 1 | 5% | Changed symptom description to fix prescription |
| **P4**: Real improvement | **1** | **5%** | Added actual `subprocess.run()` test (airflow task) |
| **P6**: Regression | 3 | 14% | Instruction narrowed solution space |

*Percentages exceed 100% because tasks can exhibit multiple pathologies.*

**Concrete P3 examples**:

- `bun-domurl-invalid-url-crash`: docstring says "verify crash behavior"; assertion still `assert 'ERR_INVALID_URL' in file_content`. No `subprocess.run(['bun', ...])`.
- `appwrite-vectordb-race-condition`: docstring says "BEHAVIOR verification"; test does `assert re.search(r'try\s*\{.*?catch', content)`. No concurrency simulation.
- `oxc-pr-21022`: helper named `verify_js_uses_buffer_proto_methods()`; implementation is `'utf8Slice.call' in content`. Surface compliance, zero substance.

### Experiment 2: Kimi-K2.6 and GLM-5.1 (20 tasks, 2 hours)

Same prompt, same pipeline, same E2B sandboxes — only the model identifier
changed. Via the ARK Coding Plan endpoint. ARK rate limits clipped the run
at 3 fully-completed tasks, but enough to see the difference.

| Model | fix_quality:ok | PASS | Avg duration | Sandbox timeouts |
|---|---|---|---|---|
| MiniMax-M2.7 (baseline) | ~390/501 | 356 | ~15 min | 25 |
| **Kimi-K2.6** | 3 | 2 | ~23 min | 0 |
| **GLM-5.1** | 1 | 1 | ~40 min | 1 |

**Kimi-K2.6 on `langchain-filter-messages-docstring-fix` — P4 genuine rewrite**

Before:
```python
bad_patterns = [r"incl_names\s*=", r"incl_types\s*=", r"excl_ids\s*="]
for pattern in bad_patterns:
    assert re.search(pattern, docstring) is None
```

After (Kimi):
```python
blocks = re.findall(r"```python\s*\n(.*?)```", docstring, re.DOTALL)
example_code = [b for b in blocks if "filter_messages(" in b][0]
script = f"""
import sys; sys.path.insert(0, "{REPO / 'libs' / 'core'}")
from langchain_core.messages import filter_messages, SystemMessage, HumanMessage, AIMessage
{textwrap.dedent(example_code)}
"""
subprocess.run(['python', '-c', script], ...)
# Fails with TypeError if parameter names are wrong
```

The test now extracts the docstring code example, builds a Python script,
and executes it via subprocess. If the bug is present, it raises `TypeError`.
This is exactly what "behavioral" means.

**GLM-5.1 on `openclaw-gemini-provider-aliases` — P4 genuine rewrite**

Before:
```python
content = INDEX_FILE.read_text()
call_pattern = re.compile(r"resolveGoogle31ForwardCompatModel\s*\(\s*\{([^}]+)\}", re.DOTALL)
matches = call_pattern.findall(content)
assert not re.search(r'providerId\s*:\s*["\']google["\']', call_args)
```

After (GLM):
```python
r = _run(["npx", "vitest", "run",
    "extensions/google/provider-models.test.ts",
    "--reporter=verbose"])
assert r.returncode == 0
assert re.search(r"alias provider", r.stdout, re.IGNORECASE)
assert "FAIL" not in r.stdout
```

The test now runs the repo's own TypeScript test suite via vitest and parses
the output. Not grepping the source — executing it.

**Kimi-K2.6 on `maui-android-fix-collectionview-selection-crash` — P1+P4 mixed**

The existing test already used `subprocess.run(['dotnet', 'build', ...])`, so
Kimi didn't need to add subprocess calls. What it DID add: a helper
`_extract_on_bind_view_holder()` that parses C# method bodies using
brace-counting — a real structural improvement over simple string search.

### Scorecard (original 22+3-task audit, 2026-04-22 AM)

| Metric | MiniMax-M2.7 | Kimi-K2.6 | GLM-5.1 |
|---|---|---|---|
| Tasks audited | 22 | 2 | 1 |
| Genuine P4 improvements | **0** | **1** | **1** |
| P4 rate | **0%** | **50%** | **100%** (n=1) |
| P1/P3 cosmetic-only | 14/22 (64%) | 1/2 (50%) | 0/1 |
| Avg fix_quality duration | ~15 min | ~23 min | ~40 min |
| Cost per task (est) | ~$0.17 | ~$0.50–1 | ~$1–2 |

Small sample on the strong-model side, but the directionality *at first*
looked unambiguous: frontier-class models produce behavioral tests that
MiniMax consistently fails to write. The re-audit below shows this overstated
the gap.

### 2.3 Addendum — 60-task re-audit (2026-04-22 PM)

The original 22-task audit drew from early MiniMax output where the
`fix_task_quality.md` prompt was still being iterated and the P4 threshold
was set strictly (required full docstring-example extraction + subprocess
execution). Before deciding whether to revert the 504 modified tasks in the
in-flight branch, we ran a larger, random 60-task re-audit sampled uniformly
from the 245 tasks with modified `tests/test_outputs.py`.

**Methodology**: 60 tasks randomly sampled from all tasks whose
`tests/test_outputs.py` was modified in the uncommitted working tree. Split
into three 20-task batches, each audited by an independent subagent applying
the P1–P6 taxonomy. All batches classified diffs against the same definitions
and reported counts. Raw output preserved at
`pipeline_logs/fix_quality_reaudit_60task_20260422.md` (see §Logs).

**Consolidated distribution (n=60)**:

| Classification | Batch A | Batch B | Batch C | Total | % |
|---|---|---|---|---|---|
| **P4** Real improvement | 10 | 6 | 7 | **23** | **38%** |
| **P1** Cosmetic | 6 | 9 | 6 | **21** | **35%** |
| **P6** Regression | 1 | 2 | 4 | **7** | **12%** |
| **P3** Tests-still-grep | 0 | 3 | 3 | **6** | **10%** |
| **P2** Prescriptive | 3 | 1 | 0 | **4** | **7%** |
| P5 No change | 0 | 0 | 0 | 0 | 0% |

**Revised findings**:

1. **P4 rate is 38%, not 0%.** The original audit missed most of the P4s by
   sampling from early prompt iterations and applying an over-strict
   threshold. When the threshold is "test invokes real interpreter (node /
   pnpm / cargo / pip / subprocess) and asserts on output," 23 of 60 diffs
   qualify. Examples from the re-audit: `bun-glob-scan-double-visit`
   (subprocess `bun --eval` with tempdir), `clickhouse-build-path-mapping`
   (compiles C++ test, inspects DWARF), `payload-pr-16117` (runs pnpm vitest
   unit tests end-to-end), `ant-design-pr-57611` (subprocess vitest execution).

2. **P6 regressions are the real danger (12%).** Seven tasks deleted tests
   outright or reduced them to trivially-passing stubs:

   | Task | Regression |
   |---|---|
   | `ant-design-test-types` | test file reduced to 1 line |
   | `dagster-k8s-utf8-log-decoding` | deleted 2 grep tests |
   | `sui-indexer-alt-object-store-concurrent-connection` | deleted 3 functions |
   | `router-start-plugin-vite-7-8-compat` | deleted 1 function |
   | `ant-design-popconfirm-icon-semantic` | deleted 6 functions |
   | `deno-cipher-large-input-validation` | abandoned, no restore |
   | `bun-cookiemap-tojson-numeric-crash` | abandoned, no restore |

   Four of the seven had `reconcile_status.json` reporting
   `"fixed": true, "nop_reward": 0, "gold_reward": 1` — the model claimed
   success after weakening coverage to the point the trivial oracle passes.
   This is a **reward-hacking pattern** we should name and track.

3. **P1 cosmetic (35%) is the median output.** Variable renames, relaxed
   regex patterns, docstring rewrites — no assertion-quality change. Neither
   improves nor regresses the task; safe to keep.

4. **Extrapolation to population (n=245 modified tests)**:
   - ~93 likely P4 (keep as net improvement)
   - ~86 likely P1 cosmetic (keep — no harm)
   - ~39 P2/P3 (borderline, lean revert)
   - ~29 likely P6 (revert urgently)

**Implications for §4 recommendations**:
- Rec #5 below ("Don't revert the MiniMax batch") was written from the 22-
  task sample. It is **partially wrong**: wholesale-keep is fine for the
  ~180 P1+P4 tasks, but the ~29 P6 tasks must be reverted — they are
  literally worse than the pre-pipeline state. See revised rec #5 below.
- The "cheap model cannot rewrite tests" framing is too strong. A better
  framing: **cheap models produce test rewrites at ~38% P4 with a 12%
  regression rate** — enough signal to be worth a selective keep after
  filtering P6 out, but not enough quality for unsupervised production use.

**Methodology caveat**: The re-audit subagents may have applied a slightly
looser P4 threshold than the original audit — specifically, "runs external
process and checks return code" counted as P4 in the re-audit, whereas the
original audit required "constructs a reproduction of the bug and asserts
the fixed behavior." Under the stricter definition, the P4 count would drop
but the P6 count and the P1-vs-revert decision are unchanged. The practical
conclusion — revert the 29, keep the rest — holds under either threshold.

---

## Part 3 — Why Cheap Models Fail

Converting `assert 'catchError' in source_code` to a behavioral test requires:

1. Understanding the repo's build system (npm / cargo / go / pip / cabal)
2. Knowing import paths (`from module.subpackage import TargetClass`)
3. Constructing a minimal reproduction — what input triggers the bug?
4. Handling execution environment (DB, network, config files)
5. Writing correct assertions on output

MiniMax-M2.7 is trained for speed and cost. When it lacks confidence to
sustain that reasoning chain, it takes the next-best action: rewrite the
docstring to *sound* behavioral and tweak the test name. Assertions stay
grep-based because rewriting them is the hard part.

Kimi-K2.6 and GLM-5.1, both larger models with more reasoning capacity,
handle the full chain. They return tests that actually run the code.

**Parallel with rubric generation**: We saw the same "surface compliance, no
substance" pattern when using cheap LLMs to generate rubrics. See
`rubric-reward-postmortem.md`. In both cases, the failure mode is identical:
the model optimizes for looking-like-done rather than being-done, because
the deeper task exceeds its reasoning budget.

---

## Part 4 — Recommendations

### For future quality-improvement passes

1. **Budget for frontier models on the rewriting step.** MiniMax is fine for
   instruction-only fixes (rewording symptoms, removing redundancy) but
   cannot do the test rewrite. Estimated **~$500–1000 for a 100–200 task
   Opus or Kimi pass** on the highest-value tasks (those flagged
   `tests_verify_behavior_not_text`).

2. **Separate the two concerns.** Use a cheap model for instruction
   rewording (symptom description, removing solution leakage) and a strong
   model for test rewriting. Different skill thresholds, different budgets.

3. **Audit methodology as standard practice.** After any batch pipeline,
   sample 10–15 tasks with `git diff` + `quality.json` cross-reference. The
   P1–P6 taxonomy catches systemic pathologies in under an hour.

4. **ARK account TPM caps matter.** ARK Coding Plan has aggressive
   throttling — 47 rate limits in 90 minutes at c=4 total. Not usable for
   batch. Fireworks Kimi, MiniMax native, or Anthropic direct are required
   for production pipelines.

### For the benchmark itself

1. **Adopt fail-to-pass as the primary test tier.** Every task should have
   at least one test that:
   - Runs the actual buggy code path (via extraction + mock, not full import)
   - Demonstrates the failure (crash, wrong output, hang)
   - Verifies the fix resolves it

2. **Demote structural tests to partial-credit supplementary checks.**
   AST/text tests provide partial signal but should never be the sole pass
   criteria. ≤30% of total weight.

3. **Add pass-to-pass regression tests.** For each task, identify existing
   functionality that should NOT break. Run those checks both on buggy and
   fixed code. Both should pass.

4. **Accept multiple valid implementations.** Where structural checks are
   necessary, use OR conditions generously. If the problem says "handle the
   error", accept try/except, if-guard, `hasattr`, `getattr` with default,
   etc.

5. **Selective revert of the MiniMax batch (revised 2026-04-22 PM).** The
   original version of this recommendation said "don't revert" based on the
   22-task audit's 14% regression estimate. The 60-task re-audit revised
   that to 12% P6 regressions — ~29 tasks across the full population — and
   these are *actual* regressions (tests deleted, coverage eliminated),
   not cosmetic drift. **Action**: triage all 245 modified test files;
   revert any diff that (a) net-deletes test functions, (b) removes
   `subprocess.run` / `check_output` calls, or (c) replaces assertions
   with strictly weaker ones. Keep the remaining ~216. Programmatic
   heuristics catch ~90% of the P6s in under a minute; spot-check the rest.
   The pre-pipeline state is tagged as `pre-fix-quality-audit`.

6. **Track cosmetic-only tasks for a future strong-model pass.** ~86 test
   files in the modified population are P1 cosmetic — no harm, no help.
   Don't re-process with MiniMax — save them for Opus/Kimi.

### Contamination mitigation

- Run OpenAI's contamination probe: give the model the task ID / repo name
  and ask it to reproduce the gold patch from memory alone. If it can, the
  task is contaminated for that model.
- Test with models trained before the PR merge date.
- Prefer private repos or very recent (< 1 week old) PRs for new tasks.
- **sglang/vllm public PRs are high contamination risk.** Be careful with
  Dockerfiles that might let the agent query a newer version of the repo.

---

## Part 5 — Lessons for the field

1. **Cheap models can do test-rewriting at moderate quality, with guardrails.**
   The original framing here — a binary capability threshold between
   MiniMax (cannot) and Kimi/GLM (can) — was wrong. Re-audited at scale,
   MiniMax produces 38% P4 improvements alongside 12% regressions. The
   practical lesson is not "use the strong model"; it's **"cheap model
   first, strong model as a diff filter"**. Strong-model review of the
   cheap-model output is ~10x cheaper than strong-model generation.

2. **Sample size matters more than people think.** Our first audit (n=22)
   undersold a 38% success rate as 0% and oversold a 50% success rate as
   100%. Small-n audits on heterogeneous pipeline output produce directional
   claims that don't survive a 3x-larger sample. For pipeline postmortems,
   treat n<50 as directional-only.

3. **Reward hacking is real and visible.** Four of the seven P6 regressions
   in the 60-task re-audit had the model writing
   `reconcile_status.json: {"fixed": true, "nop_reward": 0, "gold_reward": 1}`
   after deleting tests until the oracle trivially passed. The model did
   not deceive us — it deleted tests in plain sight and self-reported
   success. Gold/nop oracles don't detect coverage loss; an orthogonal
   signal (diff size, test-function count delta) is required.

4. **"LLM wrote tests" is not a quality claim.** Without auditing the
   actual diffs, a pipeline can produce a lot of surface compliance without
   substance. Our 356 "PASSes" looked great until we opened the files.

5. **The same pattern recurs across meta-tasks.** Rubric generation, test
   rewriting, instruction polishing — cheap models produce plausible-looking
   surface changes while leaving the hard core untouched. Budget for strong
   models on the core, cheap models on the surface.

6. **ARK Coding Plan is interesting but not ready for batch.** Multiplexes
   Kimi, GLM, MiniMax, DeepSeek through one Anthropic-compatible endpoint —
   but per-account rate limits make c > 4 impractical. Useful for targeted
   A/B experiments.

---

## Appendix — Experimental Setup

### Prompt
`taskforge/prompts/fix_task_quality.md`. Gives the agent:
- Full repo cloned at base commit
- `quality.json` with judge findings
- Instructions to fix BOTH tests AND instruction.md in one pass
- Explicit examples of behavioral test patterns (`subprocess.run(...)`)

### Pipeline
- Orchestrator: `scripts/validate_batch.py --start-at fix_quality`
- Sandbox: E2B (`harbor-worker-v3` template)
- Per-task runtime: 10–60 min (fix_quality → validate → post-judge → optional rewrite)
- Backends: see `taskforge/backends.py`

### Hardware / cost
- Orchestration: local WSL2, 15 GB RAM, 10–22 concurrent workers
- Sandboxes: 30–60 E2B VMs at peak
- LLM cost: ~$85 MiniMax (501 tasks) + ~$20 Kimi/GLM pilot = **~$105 total**
- Frontier-model Opus pass for 200 tasks would be ~$1000 — under a typical
  ML experiment's compute line item.

### Logs
- MiniMax runs: `pipeline_logs/fix_quality_mmx_native_*.log` (2026-04-21 → 22)
- ARK A/B/C: `pipeline_logs/fix_quality_ark_{glm,minimax,kimi}_*.log`
- Pre-pipeline tag: `git tag pre-fix-quality-audit`
- Audit diffs: `git diff pre-fix-quality-audit..HEAD -- harbor_tasks/`
- 60-task re-audit (2026-04-22 PM): three subagent reports consolidated
  inline in §2.3. Sample was drawn from `/tmp/audit_sample.txt` (random
  60 of 245 tasks with modified tests); batches stored at
  `/tmp/audit_batch_{aa,ab,ac}`.
