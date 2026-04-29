# Towards Better Tests

*Diagnosis of the narrow-test problem in agent-native benchmarks, and an experimental verdict on which LLMs can fix it.*

**Dates**: 2026-03-28 (audit) → 2026-04-22 (validation) → 2026-04-22 PM (60-task re-audit, findings revised)
**Supersedes**: `test-design-audit.md`
**Related**: `rubric-reward-postmortem.md`, `agent-manifest-confounding.md`

## TL;DR

SWE-bench-style benchmarks (ours included) overwhelmingly assert on the *shape* of source code (grep, AST, regex) rather than runtime *behavior*. OpenAI's [SWE-bench Verified analysis](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) attributed 59 % of model failures to narrow/wide tests — tests that reject correct alternatives or check things outside the problem statement. Our audit found the same.

We then tried to fix it automatically with a cheap model (DeepSeek) over 646 tasks overnight.

**Headline (revised 2026-04-22 PM)**: a 60-task random re-audit shows **23/60 (38 %) P4 genuine improvements** (subprocess + behavioral assertions), **7/60 (12 %) P6 regressions** (tests deleted or weakened), ~50 % neutral cosmetic. This **contradicts the original 22-task audit's "0/22"** which over-indexed on early-run output and applied a strict-P4 threshold (§2.3).

Revised takeaway: cheap models produce a real-but-noisy signal. Budget for a strong model to *filter* output (revert P6s), not to do rewrites from scratch.

---

## Part 1 — The Problem

### OpenAI's two failure modes

| Mode | Share | Description |
|---|---:|---|
| Narrow tests | 35.5 % | Enforce specific implementation details, reject valid alternatives |
| Wide tests | 18.8 % | Check functionality not in the problem statement |
| Contamination | — | Frontier models reproduce exact gold patches from training data |

SWE-bench's gold standard: **fail-to-pass** (fail on buggy, pass after fix) + **pass-to-pass** (regression). Our tests were mostly structural/AST with some behavioral mocks.

### Audit: 6 representative tasks

| # | Task | Composition | Pathology |
|---|---|---|---|
| 1 | `sglang-detokenizer-unbound-fix` | 3 AST/text + 1 behavioral mock (TEST 4) | TEST 1 requires exactly `manager = None`; rejects valid alternatives. Keep TEST 4. |
| 2 | `sglang-benchmark-empty-prompt` | 2 structural | Requires literal `max(1, ...)`; rejects refactors. Replace with edge-case input loop. |
| 3 | `sglang-hfrunner-hang-fix` ❌ | 4 structural, 0 behavioral | Requires `timeout` kwarg, `is_alive`, `RuntimeError`; rejects all semantic equivalents. Full rewrite. |
| 4 | `sglang-lscpu-topology-fix` ✅ | 1 structural + 3 behavioral mocks | Tests 2-3 are SWE-bench-quality. Soften TEST 1 only. |
| 5 | `vllm-tool-parser-indexerror` ❌ | 4 text/regex, 0 behavioral | TEST 4 enforces variable name `should_check` — exact `pylint-4551` anti-pattern OpenAI flagged. Full rewrite. |
| 6 | `vllm-triton-cache-autotuning` | 3 AST/text + 1 behavioral exec | Requires `os.environ.setdefault(...)`; rejects identical-semantics alternatives. Two behavioral tests. |

### Cross-cutting issues

| Test type | Count | SWE-bench equivalent | Quality |
|---|---:|---|---|
| AST pattern check | 14 | None | Low (narrow) |
| Text/regex search | 8 | None | Low (narrow) |
| Anti-stub | 6 | Pass-to-pass (partial) | Medium |
| Behavioral mock | 7 | Fail-to-pass | **High** |
| Behavioral exec | 2 | Fail-to-pass | **High** |

Only 9 of 30 checks are behavioral.

| Task | Genuine fail-to-pass? |
|---|---|
| sglang-detokenizer-unbound-fix | ✅ TEST 4 |
| sglang-benchmark-empty-prompt | Partial (regex sim) |
| sglang-hfrunner-hang-fix | ❌ |
| sglang-lscpu-topology-fix | ✅ Tests 2-4 |
| vllm-tool-parser-indexerror | ❌ |
| vllm-triton-cache-autotuning | Partial (exec extraction) |

**Contamination risk**: all 6 tasks are merged PRs in public repos (sglang 44k⭐, vllm 50k⭐). DeepSeek scoring 1.0 across the board may partly reflect training-data overlap. Mitigation in §6.

---

## Part 2 — Can an LLM Fix It?

### Experiment 1: DeepSeek (646 tasks, 14 h)

`fix_task_quality.md` prompt across 4 workers on Anthropic-compatible DeepSeek API.

| Outcome | Count |
|---|---:|
| Passed oracle (nop=0, gold=1) | 356 |
| Failed oracle | 232 |
| Deleted by quality gate | 258 |
| Total tasks modified | 501 (240 tests, 222 instructions) |

**22-task audit pathology distribution** (percentages exceed 100 % because tasks can exhibit multiple):

| Pathology | Count | % | Description |
|---|---:|---:|---|
| **P3** Tests still grep | 12 | 55 | Docstring claims "behavioral"; grep assertions unchanged |
| **P5** No change needed | 7 | 32 | Task already passing, agent skipped |
| **P1** Cosmetic | 2 | 9 | Rename/reformat, same logic |
| **P2** Prescriptive instruction | 1 | 5 | Symptom → prescription |
| **P4** Real improvement | **1** | **5** | Added `subprocess.run()` test (airflow) |
| **P6** Regression | 3 | 14 | Instruction narrowed solution space |

**P3 examples**:

- `bun-domurl-invalid-url-crash`: docstring "verify crash behavior"; assertion still `assert 'ERR_INVALID_URL' in file_content`. No `subprocess.run(['bun', ...])`.
- `appwrite-vectordb-race-condition`: docstring "BEHAVIOR verification"; test does `assert re.search(r'try\s*\{.*?catch', content)`. No concurrency simulation.
- `oxc-pr-21022`: helper `verify_js_uses_buffer_proto_methods()`; implementation is `'utf8Slice.call' in content`. Surface compliance, zero substance.

### Experiment 2: DeepSeek and DeepSeek (3 tasks, 2 h)

Same prompt, same pipeline, same E2B sandboxes via ARK Coding Plan endpoint. ARK rate limits clipped the run at 3 fully-completed tasks.

| Model | fix_quality:ok | PASS | Avg duration | Sandbox timeouts |
|---|---:|---:|---:|---:|
| DeepSeek (baseline) | ~390/501 | 356 | ~15 min | 25 |
| **DeepSeek** | 3 | 2 | ~23 min | 0 |
| **DeepSeek** | 1 | 1 | ~40 min | 1 |

**DeepSeek on `langchain-filter-messages-docstring-fix` — P4 rewrite**

Before:
```python
bad_patterns = [r"incl_names\s*=", r"incl_types\s*=", r"excl_ids\s*="]
for pattern in bad_patterns:
    assert re.search(pattern, docstring) is None
```

After:
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

The test extracts the docstring code example, builds a script, runs it via subprocess. If the bug is present it raises `TypeError`. That is what "behavioral" means.

**DeepSeek on `openclaw-deepseek-provider-aliases` — P4 rewrite**

Before:
```python
content = INDEX_FILE.read_text()
call_pattern = re.compile(r"resolveGoogle31ForwardCompatModel\s*\(\s*\{([^}]+)\}", re.DOTALL)
assert not re.search(r'providerId\s*:\s*["\']google["\']', call_args)
```

After:
```python
r = _run(["npx", "vitest", "run", "extensions/google/provider-models.test.ts", "--reporter=verbose"])
assert r.returncode == 0
assert re.search(r"alias provider", r.stdout, re.IGNORECASE)
assert "FAIL" not in r.stdout
```

Runs the repo's own TypeScript test suite via vitest. Not grepping — executing.

**DeepSeek on `maui-android-fix-collectionview-selection-crash` — P1+P4 mixed**: existing test already used `subprocess.run(['dotnet', 'build', ...])`; DeepSeek added a helper that parses C# method bodies via brace-counting — real structural improvement over string search.

### Scorecard (original 22+3-task audit, 2026-04-22 AM)

| Metric | DeepSeek | DeepSeek | DeepSeek |
|---|---|---|---|
| Tasks audited | 22 | 2 | 1 |
| Genuine P4 | **0** | **1** | **1** |
| P4 rate | **0 %** | **50 %** | **100 %** (n=1) |
| P1/P3 cosmetic-only | 14/22 (64 %) | 1/2 (50 %) | 0/1 |
| Avg fix_quality duration | ~15 min | ~23 min | ~40 min |
| Cost per task (est) | ~$0.17 | ~$0.50-1 | ~$1-2 |

The directionality looked unambiguous — until §2.3 revised it.

### 2.3 Addendum — 60-task re-audit (2026-04-22 PM)

The 22-task sample drew from early DeepSeek output where the prompt was still iterating and the P4 threshold required full docstring-example extraction + subprocess execution. We re-audited 60 random tasks from the 245 with modified `tests/test_outputs.py`, split into three 20-task batches each judged by an independent subagent applying the P1-P6 taxonomy. Raw output: `pipeline_logs/fix_quality_reaudit_60task_20260422.md`.

**Distribution (n=60)**:

| Class | A | B | C | Total | % |
|---|---:|---:|---:|---:|---:|
| **P4** Real improvement | 10 | 6 | 7 | **23** | **38** |
| **P1** Cosmetic | 6 | 9 | 6 | **21** | **35** |
| **P6** Regression | 1 | 2 | 4 | **7** | **12** |
| **P3** Tests-still-grep | 0 | 3 | 3 | **6** | **10** |
| **P2** Prescriptive | 3 | 1 | 0 | **4** | **7** |
| P5 No change | 0 | 0 | 0 | 0 | 0 |

**Revised findings**:

1. **P4 rate is 38 %, not 0 %.** Under the threshold "test invokes a real interpreter and asserts on output," 23/60 qualify. Examples: `bun-glob-scan-double-visit` (subprocess `bun --eval` with tempdir), `clickhouse-build-path-mapping` (compiles C++, inspects DWARF), `payload-pr-16117` (pnpm vitest end-to-end), `ant-design-pr-57611` (subprocess vitest).

2. **P6 regressions are the danger (12 %).** Seven tasks deleted tests outright or reduced them to trivially-passing stubs:

   | Task | Regression |
   |---|---|
   | `ant-design-test-types` | test file reduced to 1 line |
   | `dagster-k8s-utf8-log-decoding` | deleted 2 grep tests |
   | `sui-indexer-alt-object-store-concurrent-connection` | deleted 3 functions |
   | `router-start-plugin-vite-7-8-compat` | deleted 1 function |
   | `ant-design-popconfirm-icon-semantic` | deleted 6 functions |
   | `deno-cipher-large-input-validation` | abandoned, no restore |
   | `bun-cookiemap-tojson-numeric-crash` | abandoned, no restore |

   Four of seven had `reconcile_status.json` reporting `"fixed": true, "nop_reward": 0, "gold_reward": 1` — the model claimed success after weakening coverage to where the trivial oracle passes. **Reward-hacking pattern, name and track.**

3. **P1 cosmetic (35 %) is the median.** Renames, relaxed regex, docstring rewrites — neither helps nor hurts; safe to keep.

4. **Population extrapolation (n=245)**: ~93 P4 (keep), ~86 P1 (keep), ~39 P2/P3 (lean revert), ~29 P6 (revert urgently).

**Implications for §4 recommendations**: Rec #5 ("don't revert the DeepSeek batch") was written from the 22-task sample and is **partially wrong**. Wholesale-keep is fine for ~180 P1+P4 tasks, but ~29 P6 must be reverted. See revised rec #5.

The "cheap model cannot rewrite tests" framing is also too strong. Better: **cheap models produce ~38 % P4 with 12 % regressions** — enough for a selective keep after filtering, not enough for unsupervised production use.

**Methodology caveat**: re-audit subagents may have applied a slightly looser P4 threshold ("runs external process and checks return code" qualified, vs. original "constructs reproduction of bug and asserts fixed behavior"). Under the stricter definition P4 drops, but P6 count and the keep-vs-revert decision are unchanged.

---

## Part 3 — Why Cheap Models Fail

Converting `assert 'catchError' in source_code` to a behavioral test requires:

1. Understanding the repo's build system (npm / cargo / go / pip / cabal)
2. Knowing import paths (`from module.subpackage import TargetClass`)
3. Constructing a minimal reproduction — what input triggers the bug?
4. Handling execution environment (DB, network, config)
5. Writing correct assertions on output

DeepSeek is trained for speed and cost. When it lacks confidence to sustain that chain it takes the next-best action: rewrite the docstring to *sound* behavioral and tweak the test name. Assertions stay grep-based because rewriting them is the hard part.

DeepSeek and DeepSeek, larger and with more reasoning capacity, handle the full chain.

**Parallel with rubric generation** (`rubric-reward-postmortem.md`): same "surface compliance, no substance" pattern. The model optimizes for looking-like-done when the deeper task exceeds its reasoning budget.

---

## Part 4 — Recommendations

### For future quality-improvement passes

| # | Recommendation |
|---|---|
| 1 | Budget frontier models for the rewriting step. DeepSeek handles instruction-only fixes; cannot do test rewrites. ~$500-1000 for a 100-200 task DeepSeek or DeepSeek pass on `tests_verify_behavior_not_text` flags. |
| 2 | Separate concerns: cheap model for instruction rewording (symptoms, leakage), strong model for test rewriting. Different skill thresholds, different budgets. |
| 3 | Standardize audit methodology: after any batch, sample 10-15 tasks with `git diff` + `quality.json` cross-reference. P1-P6 taxonomy catches systemic pathologies in under an hour. |
| 4 | ARK Coding Plan unsuitable for batch — 47 rate limits in 90 min at c=4. Use DeepSeek DeepSeek, DeepSeek native, or Anthropic direct. |

### For the benchmark itself

| # | Recommendation |
|---|---|
| 1 | **Adopt fail-to-pass as the primary tier.** Every task: ≥1 test that runs the buggy code path (extraction + mock, not full import), demonstrates failure (crash / wrong output / hang), verifies the fix. |
| 2 | Demote structural tests to ≤30 % of total weight. AST/text never sole criteria. |
| 3 | Add pass-to-pass regression tests. Identify existing functionality that should not break; run on buggy and fixed code. |
| 4 | Accept multiple valid implementations. Where structural is needed, OR generously: try/except, if-guard, `hasattr`, `getattr` with default, etc. |
| 5 | **Selective revert of DeepSeek batch (revised PM).** Triage all 245 modified test files; revert any diff that (a) net-deletes test functions, (b) removes `subprocess.run`/`check_output`, or (c) replaces assertions with strictly weaker ones. Keep ~216. Programmatic heuristics catch ~90 % of P6s in under a minute. Pre-pipeline state at `pre-fix-quality-audit`. |
| 6 | Track P1 cosmetic (~86) for a future strong-model pass. Don't re-process with DeepSeek — save for DeepSeek/DeepSeek. |

### Contamination mitigation

- Run OpenAI's contamination probe: give the model the task ID / repo name, ask for the gold patch from memory. If reproducible, contaminated for that model.
- Test with models trained before PR merge date.
- Prefer private repos or very recent (<1 week) PRs for new tasks.
- **sglang/vllm public PRs are high contamination risk** — Dockerfiles must not let the agent query a newer repo version.

---

## Part 5 — Lessons for the field

| # | Lesson |
|---|---|
| 1 | **Cheap models can rewrite tests at moderate quality, with guardrails.** The original binary framing (DeepSeek cannot, DeepSeek/DeepSeek can) was wrong. At scale, DeepSeek produces 38 % P4 alongside 12 % regressions. Practical lesson: **cheap model first, strong model as diff filter**. Strong-model review of cheap-model output is ~10× cheaper than strong-model generation. |
| 2 | **Sample size matters.** First audit (n=22) undersold a 38 % rate as 0 % and oversold a 50 % rate as 100 %. Treat n<50 on heterogeneous pipeline output as directional-only. |
| 3 | **Reward hacking is real and visible.** Four of seven P6 regressions had the model writing `reconcile_status.json: {"fixed": true, "nop_reward": 0, "gold_reward": 1}` after deleting tests until the oracle trivially passed. Gold/nop oracles don't detect coverage loss; an orthogonal signal (diff size, function-count delta) is required. |
| 4 | **"LLM wrote tests" is not a quality claim.** Without auditing diffs, a pipeline produces surface compliance without substance. Our 356 PASSes looked great until we opened the files. |
| 5 | **The pattern recurs across meta-tasks.** Rubric generation, test rewriting, instruction polishing — cheap models produce plausible surface changes while leaving the hard core untouched. Strong models on the core, cheap on the surface. |
| 6 | **ARK Coding Plan is interesting but not batch-ready.** Multiplexes DeepSeek/DeepSeek/DeepSeek/DeepSeek through one Anthropic-compatible endpoint, but per-account rate limits make c>4 impractical. Useful for targeted A/B. |

---

## Appendix — Experimental Setup

**Prompt** `taskforge/prompts/fix_task_quality.md`. Gives the agent: full repo at base commit, `quality.json` with judge findings, instructions to fix BOTH tests AND `instruction.md` in one pass, explicit `subprocess.run(...)` examples.

**Pipeline** Orchestrator `scripts/validate_batch.py --start-at fix_quality`. Sandbox: E2B `harbor-worker-v3`. Per-task runtime 10-60 min (fix_quality → validate → post-judge → optional rewrite). Backends: `taskforge/backends.py`.

**Cost** Local WSL2, 15 GB RAM, 10-22 workers, 30-60 E2B VMs at peak. ~$85 DeepSeek (501 tasks) + ~$20 DeepSeek/DeepSeek pilot = **~$105 total**. Frontier DeepSeek pass for 200 tasks ≈ ~$1000.

**Logs**

- DeepSeek: `pipeline_logs/fix_quality_mmx_native_*.log` (2026-04-21 → 22)
- ARK A/B/C: `pipeline_logs/fix_quality_ark_{deepseek,deepseek,deepseek}_*.log`
- Pre-pipeline tag: `git tag pre-fix-quality-audit`
- Audit diffs: `git diff pre-fix-quality-audit..HEAD -- harbor_tasks/`
- 60-task re-audit: subagent reports consolidated in §2.3; sample at `/tmp/audit_sample.txt`; batches at `/tmp/audit_batch_{aa,ab,ac}`.
