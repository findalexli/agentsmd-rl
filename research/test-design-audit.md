# Test Design Audit: Applying OpenAI's SWE-bench Verified Critique

## Context

OpenAI's analysis of SWE-bench Verified identified two systemic problems:
https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
1. **Tests reject correct solutions** (59.4% of audited failures)
   - **Narrow tests** (35.5%): Enforce specific implementation details, reject valid alternatives
   - **Wide tests** (18.8%): Check functionality not described in the problem statement

2. **Contamination**: All frontier models reproduce exact gold patches from training data

SWE-bench's gold standard test design uses:
- **Fail-to-pass tests**: Tests that FAIL on buggy code, PASS after correct fix
- **Pass-to-pass tests**: Regression tests that PASS both before and after

Our current tests are **structural/AST checks** and **some behavioral mocks**.
This audit examines each task against these higher standards.

---

## Task-by-Task Audit Example

### 1. sglang-detokenizer-unbound-fix

**Current tests:**
- TEST 1: AST check for `manager = None` before try block
- TEST 2: AST check for `if manager is not None` guard in except block
- TEST 3: Anti-stub (keyword presence + line count)
- TEST 4: Behavioral exec with mocked constructor that raises

**Narrow test problem:**
- TEST 1 requires exactly `manager = None` assignment. Valid alternatives rejected:
  - `manager = None` inside the try block as first statement
  - Wrapping the except body in `try/except (NameError, UnboundLocalError)`
  - Using `locals().get('manager')` pattern
- TEST 2 accepts multiple guard patterns (good) but still checks for specific variable name `manager`

**What a fail-to-pass test would look like:**
```python
# FAIL-TO-PASS: Call run_detokenizer_process with a constructor that raises.
# Buggy code: raises UnboundLocalError
# Fixed code: handles gracefully (no UnboundLocalError)
```
TEST 4 already does this! It's our best test.

**Verdict:** TEST 4 (behavioral) is SWE-bench quality. Tests 1-2 are narrow structural checks that could reject valid solutions. TEST 3 is fine as regression guard.

**Recommendation:** Weight TEST 4 heavily. Tests 1-2 should be softened or replaced with a second behavioral test that verifies the except block runs to completion without crashing.

---

### 2. sglang-benchmark-empty-prompt

**Current tests:**
- TEST 1: AST check for `max(1,...)` and absence of `max(0,...)`
- TEST 2: Behavioral regex extraction of the clamp value and simulation
- TEST 3: Anti-stub

**Narrow test problem:**
- TEST 1 requires EXACTLY `max(1, ...)`. Valid alternatives rejected:
  - `max(1, input_lens[i] - num_special_tokens)` using `min_val = 1` variable
  - `input_lens[i] = input_lens[i] - num_special_tokens; if input_lens[i] < 1: input_lens[i] = 1`
  - Any refactoring that doesn't use literal `max(1,...)`
- TEST 2 uses regex to find `max(N, ...)` pattern - also narrow

**What a fail-to-pass test would look like:**
```python
# FAIL-TO-PASS: Generate requests with random_input_len = num_special_tokens.
# Buggy code: produces input_lens containing zeros
# Fixed code: all input_lens >= 1
```

**Verdict:** Both tests are narrow. A proper behavioral test would call the function (or an extracted version) with edge-case inputs and assert no zero-length outputs. The specific implementation (max(1,...) vs if-guard vs clamp) shouldn't matter.

**Recommendation:** Replace TEST 1 + TEST 2 with a single behavioral fail-to-pass test that extracts the loop logic and runs it with edge-case inputs.

---

### 3. sglang-hfrunner-hang-fix

**Current tests:**
- TEST 1: AST - no bare `out_queue.get()` without timeout
- TEST 2: Text search for `is_alive` in forward method
- TEST 3: AST - RuntimeError (or similar) raised
- TEST 4: AST - `queue.get()` uses timeout parameter
- TEST 5: Anti-stub

**Narrow test problem:**
- TEST 1 requires `timeout` keyword arg. Valid alternatives:
  - `out_queue.get(block=True, timeout=5)` - positional timeout (handled)
  - Using `out_queue.get_nowait()` in a polling loop (rejected!)
  - Using `asyncio.wait_for` wrapper (rejected!)
  - Using `select` or `poll` on the queue's underlying pipe (rejected!)
- TEST 2 requires the string `is_alive`. But a valid fix could check `model_proc.exitcode is not None` instead
- TEST 3 requires `RuntimeError`. But `ChildProcessError`, `OSError`, or even `SystemExit` could be valid
- TEST 4 is redundant with TEST 1

**What a fail-to-pass test would look like:**
```python
# FAIL-TO-PASS: Create an HFRunner-like mock where the subprocess dies immediately.
# Call forward(). Buggy code: hangs forever. Fixed code: raises within N seconds.
# Use signal.alarm() or threading.Timer to enforce timeout.
```

**Verdict:** All 4 functional tests are narrow structural checks. None test actual behavior. A real fail-to-pass test would create a subprocess that dies and verify forward() returns/raises within a bounded time instead of hanging.

**Recommendation:** Replace tests 1-4 with a behavioral test that mocks the queue/process and verifies the hang is resolved.

---

### 4. sglang-lscpu-topology-fix

**Current tests:**
- TEST 1: AST - no bare `map(int, ...)` unpack with 4-tuple target
- TEST 2: Behavioral - malformed lines don't crash (mock subprocess)
- TEST 3: Behavioral - normal 4-field input parses correctly
- TEST 4: Behavioral - empty fields default to 0
- TEST 5: Anti-stub

**Narrow test problem:**
- TEST 1 specifically checks for 4-tuple unpack from `map(int, ...)`. Valid alternatives:
  - Keeping `map(int, ...)` but wrapping in try/except ValueError
  - Using a list comprehension with error handling
  - These would still have the 4-tuple unpack pattern but be safe

**Quality of behavioral tests:**
- TEST 2 is a genuine fail-to-pass test! Buggy code crashes, fixed code handles gracefully.
- TEST 3 is a pass-to-pass regression test! Normal input works before and after.
- TEST 4 tests specific behavior (empty -> 0 default) that's in the PR but might not be the only valid approach.

**Verdict:** Tests 2-3 are close to SWE-bench quality. TEST 1 is narrow. TEST 4 assumes a specific default strategy.

**Recommendation:** This task has the best test design of the six. Could improve TEST 1 to check behavior rather than AST pattern.

---

### 5. vllm-tool-parser-indexerror

**Current tests:**
- TEST 1: Text - `index = 0` before conditional block (not inside else)
- TEST 2: Text - `auto_tools_called` appears near `_should_check_for_unstreamed_tool_arg_tokens`
- TEST 3: Anti-stub
- TEST 4: Text/regex - `should_check` variable or `auto_tools_called` in restructured conditional

**Narrow test problem: SEVERE**
- TEST 1 requires `index = 0` as a standalone assignment. But valid fixes include:
  - `index = len(tool_parser.prev_tool_call_arr) - 1 if ... else 0` refactored inline
  - Using `index = getattr(tool_parser, 'current_index', 0)` pattern
  - Any approach that ensures `index` is always defined
- TEST 2 requires `auto_tools_called` to appear near the function call. But moving the check elsewhere (e.g., early return) would also be valid.
- TEST 4 looks for `should_check` variable name (!). This is the exact `pylint-dev__pylint-4551` anti-pattern OpenAI flagged - requiring a specific variable name that's in the gold patch but not in the problem description.

**What a fail-to-pass test would look like:**
```python
# FAIL-TO-PASS: Construct a mock streaming scenario where:
#   - tool_parser is None OR tool_parser.prev_tool_call_arr is empty
#   - _should_check_for_unstreamed_tool_arg_tokens returns True
# Buggy code: raises IndexError or UnboundLocalError on `index`
# Fixed code: handles gracefully
```

**Verdict:** This is our worst task for test quality. All 4 tests enforce specific structural patterns from the gold patch. A model that fixes the bug differently (e.g., wrapping in try/except, using a default dict, early-return pattern) would fail all of them.

**Recommendation:** Complete rewrite. Need behavioral tests that construct the error scenario and verify it doesn't crash.

---

### 6. vllm-triton-cache-autotuning

**Current tests:**
- TEST 1: Text - `TRITON_CACHE_AUTOTUNING` string present
- TEST 2: AST - `os.environ.setdefault` call with TRITON_CACHE_AUTOTUNING
- TEST 3: AST - value is `"1"`
- TEST 4: Behavioral - exec the setdefault line and check env var
- TEST 5: Anti-stub

**Narrow test problem:**
- TEST 2 requires `setdefault`. Valid alternatives rejected:
  - `if "TRITON_CACHE_AUTOTUNING" not in os.environ: os.environ["TRITON_CACHE_AUTOTUNING"] = "1"`
  - `os.environ["TRITON_CACHE_AUTOTUNING"] = os.environ.get("TRITON_CACHE_AUTOTUNING", "1")`
  - Both achieve the same semantics (user can override) but use different APIs
- TEST 3 requires string `"1"`. But `"true"`, `"True"`, `"enabled"` could all be valid depending on Triton's parser.
- TEST 4 specifically extracts and execs `setdefault` calls, which couples it to TEST 2's assumption.

**What a fail-to-pass test would look like:**
```python
# FAIL-TO-PASS: After loading env_override.py's env-setting logic:
#   Scenario A: TRITON_CACHE_AUTOTUNING not set -> should be set to truthy value
#   Scenario B: TRITON_CACHE_AUTOTUNING=0 pre-set -> should remain "0" (user override)
# Buggy code: TRITON_CACHE_AUTOTUNING is never set (scenario A fails)
# Fixed code: set to "1" by default but respects user override
```

**Verdict:** Tests are narrow. TEST 4 is closest to behavioral but is coupled to the setdefault assumption. The real contract is: (a) env var gets set if absent, (b) user can override. Tests should verify those two properties, not the specific API.

**Recommendation:** Replace tests 2-4 with two behavioral tests: one that checks the var is set when absent, one that checks a pre-set value is preserved.

---

## Cross-Cutting Issues

### Contamination Risk

All 6 tasks are sourced from PUBLIC merged PRs in popular repos (sglang: 44k stars, vllm: 50k stars). Any model trained on GitHub data from after the merge date has likely seen these exact patches. The fact that both Opus 4.6 agents scored 1.0 on ALL tasks could partly reflect contamination.

**Mitigation needed:**
- Run OpenAI's contamination probing: give the model the task ID and ask it to reproduce the gold patch
- Test with models trained before the PR merge dates
- Consider tasks from private repos or very recent (< 1 week old) PRs

### Structural vs Behavioral Testing

| Test Type | Count | SWE-bench Equivalent | Quality |
|-----------|-------|---------------------|---------|
| AST pattern check | 14 | None (SWE-bench doesn't do this) | Low - narrow |
| Text/regex search | 8 | None | Low - narrow |
| Anti-stub | 6 | Pass-to-pass (partial) | Medium |
| Behavioral mock | 7 | Fail-to-pass | High |
| Behavioral exec | 2 | Fail-to-pass | High |

Only 9 of our 30 test checks are behavioral. The rest are structural and prone to the "narrow test" problem.

### Fail-to-Pass Coverage

| Task | Has genuine fail-to-pass test? |
|------|-------------------------------|
| sglang-detokenizer-unbound-fix | YES (TEST 4: mocked exec) |
| sglang-benchmark-empty-prompt | PARTIAL (TEST 2: regex simulation) |
| sglang-hfrunner-hang-fix | NO (all structural) |
| sglang-lscpu-topology-fix | YES (TESTS 2-4: mock subprocess) |
| vllm-tool-parser-indexerror | NO (all structural) |
| vllm-triton-cache-autotuning | PARTIAL (TEST 4: exec extraction) |

---

## Recommendations

### 1. Adopt fail-to-pass as the PRIMARY test tier

Every task should have at least one test that:
- Runs the actual buggy code path (via extraction + mock, not full import)
- Demonstrates the failure (crash, wrong output, hang)
- Then verifies the fix resolves it

This is the ONLY way to be implementation-agnostic.

### 2. Demote structural tests to partial-credit supplementary checks

AST/text tests can provide partial credit signal but should never be the sole pass criteria. They should carry ≤30% of the total weight.

### 3. Add pass-to-pass regression tests

For each task, identify existing functionality that should NOT break. Run those checks both on buggy and fixed code. Both should pass.

### 4. Accept multiple valid implementations

Where we must do structural checks, use OR conditions generously. If the problem says "handle the error", accept: try/except, if-guard, hasattr, getattr with default, etc.

### 5. Run contamination probes

Before declaring a task valid, probe frontier models with just the task ID / repo name to check if they can reproduce the gold patch verbatim. If they can, the task is contaminated for that model.

The sglang/vllm PRs are high contamination risk. We shall be super careful when designing the docker and also wehn we apply such instruction that the also do not cheat by going into higher versions of issues. 