# Towards Better Tests

*Diagnosis of the narrow-test problem in agent-native benchmarks, and an
experimental verdict on which LLMs can fix it.*

**Dates**: 2026-03-28 (original audit) → 2026-04-22 (experimental validation)
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
automatically: running MiniMax-M2.7 over 646 tasks overnight produced **0
genuine test rewrites** across 22 audited samples. Switching to Kimi-K2.6 and
GLM-5.1 (via ARK Coding Plan) produced **2 genuine rewrites in 3 audited
samples** — a clear capability-threshold difference.

The takeaway: test-rewriting is a frontier-model task. Budget accordingly.

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

### Scorecard

| Metric | MiniMax-M2.7 | Kimi-K2.6 | GLM-5.1 |
|---|---|---|---|
| Tasks audited | 22 | 2 | 1 |
| Genuine P4 improvements | **0** | **1** | **1** |
| P4 rate | **0%** | **50%** | **100%** (n=1) |
| P1/P3 cosmetic-only | 14/22 (64%) | 1/2 (50%) | 0/1 |
| Avg fix_quality duration | ~15 min | ~23 min | ~40 min |
| Cost per task (est) | ~$0.17 | ~$0.50–1 | ~$1–2 |

Small sample on the strong-model side, but the directionality is unambiguous:
frontier-class models produce behavioral tests that MiniMax consistently
fails to write.

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

5. **Don't revert the MiniMax batch.** Net diff is slightly negative lines
   (simplified on average), most changes are semantically neutral. The 14%
   regression rate is worth spot-checking but not wholesale reverting. The
   pre-pipeline state is tagged as `pre-fix-quality-audit` if needed.

6. **Track cosmetic-only tasks for a future strong-model pass.** ~240 test
   files were modified by MiniMax with grep assertions intact. Don't
   re-process with MiniMax — save them for Opus/Kimi.

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

1. **There is a capability threshold for automated test-rewriting.** It
   sits between MiniMax-M2.7 (cannot) and Kimi-K2.6 (can, ~50% rate). A
   useful data point for benchmarking future models.

2. **"LLM wrote tests" is not a quality claim.** Without auditing the
   actual diffs, a pipeline can produce a lot of surface compliance without
   substance. Our 356 "PASSes" looked great until we opened the files.

3. **The same pattern recurs across meta-tasks.** Rubric generation, test
   rewriting, instruction polishing — cheap models produce plausible-looking
   surface changes while leaving the hard core untouched. Budget for strong
   models on the core, cheap models on the surface.

4. **ARK Coding Plan is interesting but not ready for batch.** Multiplexes
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
