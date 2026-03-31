# Audit Tests

Audit `harbor_tasks/$ARGUMENTS/tests/test.sh` for gaming resistance and narrow-test problems, then rewrite if issues are found.

## Phase 1: Audit

1. **Read** test.sh, instruction.md
2. **Parse** every check: what it tests, points awarded, structural vs behavioral
3. **Answer 7 questions** with specific exploit code (not descriptions)
4. **Output** the audit report below

### The 7 Questions

1. **False Positive (0-10)**: Can agent score 1.0 without solving? Show exact exploit files.
2. **False Negative (0-10)**: Can a CORRECT but differently-structured solution score 0.0? Show the failing check. (This is the OpenAI "narrow test" problem.)
3. **Gaming (0-10)**: Max score with stubs? Walk each check with `def f(): pass`.
4. **Specificity (0-10)**: Tested vs untested requirements table.
5. **Missing Coverage**: Top 3 untested functional requirements.
6. **Narrow Test Audit**: For each structural check, list 2 valid alternative implementations that would FAIL the check. If >40% of weighted score comes from narrow checks, flag as CRITICAL.
7. **Fail-to-Pass Coverage**: Does the test have at least one behavioral test that FAILS on the buggy code and PASSES on a correct fix? If not, flag as CRITICAL.

### 10 Known Gaming Anti-Patterns

Check each test against these specific exploit patterns. If ANY pattern matches, flag and fix.

| # | Pattern | Exploit | Fix |
|---|---------|---------|-----|
| 1 | **Self-referential constant extraction** | Test extracts LUT/values from agent's code, simulates with those same values → any constants pass | Compare against fixed ground-truth values, not agent-extracted ones |
| 2 | **AST fallback on import failure** | `try: from X import fn; test(fn)` / `except: check_ast()` → stub file with keywords passes fallback | No fallbacks — import failure = 0 points |
| 3 | **Structural-only frontend tests** | All tests grep for patterns (`IntersectionObserver`, `useState`) → agent adds keywords without logic | Extract and execute functions; grep alone is never sufficient |
| 4 | **Stub-passable behavioral tests** | Test only checks "doesn't crash" on empty input → `if not x: return` passes | Verify return values on both empty AND non-empty inputs |
| 5 | **Superficial guard checks** | `assert len(data) != 1` is trivially true if no processing runs | Assert state CHANGED (e.g., `len(after) < len(before)` for dedup) |
| 6 | **Hardcoded offset/parameter** | Tests with single parameter value (e.g., BLOCK_N=64) → agent hardcodes `//64` | Vary the parameter across multiple values |
| 7 | **Ungated structural tests** | AST/dict checks award points independently of behavioral tests → stub dicts score | Gate structural points behind behavioral pass: `if behavioral_passed:` |
| 8 | **Compilation-ungated structural** | Structural checks run even when code doesn't compile → broken code scores | Gate ALL structural checks behind compilation/syntax check |
| 9 | **Keyword stuffing** | Markdown/config tests check for section headers → agent copy-pastes keywords | Check coherence (Jaccard similarity < 0.70 between sections), validate code blocks |
| 10 | **Import fallback to file-exists** | `try: import_ts(module)` / `except: if os.path.exists(file): REWARD += X` → empty file scores | No existence fallbacks — import/parse failure = 0 points |

For each check in test.sh, ask: **which of the 10 patterns could exploit this?** List the pattern number in the audit report.

### Audit Report Format

```markdown
## Test Audit: $ARGUMENTS
### Reliability Score: X/10
### Narrow Test Score: X/10 (10 = accepts all valid implementations, 0 = only gold patch passes)

### Gaming Analysis
- Max stub score: X.XX
- Max comment-injection score: X.XX
- Anti-patterns matched: [list pattern #s from the 10 Known Gaming Anti-Patterns]

### Narrow Test Analysis (per OpenAI SWE-bench Verified critique)
| Check | Weight | Type | Narrow? | Alternative that would fail |
|-------|--------|------|---------|---------------------------|
| ... | ... | behavioral/structural | yes/no | ... |
Narrow-weighted score: X% (target: <=40%)

### Fail-to-Pass Coverage
- Has fail-to-pass behavioral test: yes/no
- Buggy baseline score: X.XX (should be >0 and <1.0)

### Question-by-Question
#### 1. False Positive: X/10  [exploit code]
#### 2. False Negative: X/10  [valid alternative that fails]
#### 3. Gaming: X/10  [stubs + walk-through]
#### 4. Specificity: X/10  [tested | not tested]
#### 5. Missing Coverage  [top 3]
#### 6. Narrow Tests  [per-check analysis]
#### 7. Fail-to-Pass  [coverage assessment]

### Weight: X% behavioral, Y% structural (target: >=60% behavioral)
### Verdict: PASS / REWRITE NEEDED
```

## Phase 2: Rewrite (if audit verdict is REWRITE NEEDED)

If max stub score > 0.30, alternative fix score < 0.70, or behavioral ratio < 60%, rewrite test.sh.

1. **Read** instruction.md, Dockerfile, the source PR diff
2. **Write** `harbor_tasks/$ARGUMENTS/tests/test.sh` and `chmod +x`
3. **Self-audit** the rewritten tests

### CRITICAL: Prefer Calling Code Over Inspecting Code

**AST checks are a last resort, not a default.** Before writing any `ast.parse` check, ask: can I just call this function?

Almost all our tasks run in Docker with CPU-only Python. This means:
- **torch.nn.Module code works on CPU tensors** — instantiate with small dims, call `forward()`
- **Pure Python logic** (config parsing, data structures, string ops, file I/O) — call it directly
- **numpy/scipy** — works on CPU, create test arrays
- **torch.compile** — works on CPU tensors

**Only use AST when the code literally cannot execute:**
- Triton `@triton.jit` kernels (GPU compiler, can't run on CPU)
- CUDA C++ code (`.cu` files)
- Code requiring model weights that aren't in the Docker image

When in doubt: try importing and calling. If it fails, THEN fall back to AST.

```bash
# BAD: AST check when you could just call the function
python3 -c "
import ast
tree = ast.parse(open('/workspace/lib/utils.py').read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'check_resolution':
        # check for specific implementation details...
"

# GOOD: Actually call the function and check behavior
python3 -c "
import sys; sys.path.insert(0, '/workspace')
from lib.utils import check_resolution
try:
    result = check_resolution(1024, 768, min_res=0, max_res=float('inf'))
    assert result == True, f'Expected True, got {result}'
except ValueError:
    sys.exit(1)  # Bug not fixed
"
```

### Tier System

| Tier | When | Example | Quality |
|------|------|---------|---------|
| **Fail-to-pass** | Can call buggy code path and observe failure | Call function with bug-triggering input, assert it crashes/returns wrong result | Best |
| **Pass-to-pass** | Existing behavior must not break | Normal input still works before and after fix | Good |
| **Silver behavioral** | Can import + call + check output | `merged = Cache.merge([c1,c2]); assert merged.shape[0]==2` | Good |
| **Bronze structural** | Can only check AST (needs GPU/service) | Function exists AND body >3 non-docstring stmts | Last resort |
| **Never** | `grep "keyword"` or bare `import` | Comment `# keyword` passes grep | Always gameable |

### Avoid the "Narrow Test" Anti-Pattern

Per OpenAI's SWE-bench Verified analysis (35.5% of failures were narrow tests). DO NOT:
- Check for specific variable names from the gold patch
- Require a specific API when alternatives work (e.g., `setdefault` vs `if not in`)
- Require specific code structure when multiple valid restructurings exist
- Import a function name added by the PR
- **Use AST to check code structure when you could just call the code and check behavior**

INSTEAD, test the BEHAVIOR: does the buggy code path crash / produce wrong output? Does ANY correct fix resolve it?

### Pass-to-Pass via Upstream Tests

Before writing test.sh, check if the repo has a usable test suite. If it does, include it as a P2P regression check (10-20% weight). If not, skip P2P — don't write synthetic/fake P2P tests.

1. Check the Dockerfile for the cloned repo path
2. Look for `tests/`, `test/`, or test config files (pytest.ini, vitest.config.ts, jest.config.js)
3. Check if pytest/vitest/jest is already installed in the Dockerfile
4. Identify CPU-safe tests (no GPU, no model weights, no network)

If upstream tests exist, add a P2P check:
```bash
# PASS-TO-PASS: upstream test suite (CPU-safe subset)
cd /workspace
python3 -m pytest tests/test_utils.py tests/test_config.py -x --timeout=60 -q 2>/dev/null
if [ $? -eq 0 ]; then REWARD=$((REWARD + P2P_WEIGHT)); fi
```

### Extracting Functions Without Heavy Imports

Many target files import torch/triton. Use AST extraction:

```python
import ast, textwrap
with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "target_func":
        lines = source.splitlines(keepends=True)
        func_src = textwrap.dedent("".join(lines[node.lineno-1:node.end_lineno]))
        ns = {"subprocess": subprocess, "logger": logger, "__builtins__": __builtins__}
        exec(func_src, ns)
        FUNC = ns["target_func"]
```

### Writing Rules

- **>=60% behavioral** (fail-to-pass + pass-to-pass), **<=40% structural**
- Core bug = hard fail-to-pass test worth >=0.30
- Every AST check must reject stubs (body depth >3 meaningful statements)
- Use AST nodes, never string/regex on source code
- Total weight = 1.0, `set +e`, write to `/logs/verifier/reward.txt`
- Do NOT reference the PR number, merge commit, or code snippets from the gold patch

### Self-Audit

After rewriting, verify:

```
Self-audit:
  Max stub score: X.XX (target: <=0.30)
  Alternative fix score: X.XX (target: >=0.70)
  Behavioral: X% | Structural: Y% (target: >=60% behavioral)
  AST checks: N (each justified: [reason code can't be called])
  P2P: upstream tests included / none available
  | # | Weight | Tier | F2P/P2P | Calls code? | Stub passes? | Alt fix passes? |
```

### Programmatic Pre-Checks (run first, before LLM analysis)

Before doing the 7-question audit, check these mechanically. If ANY CRITICAL issue exists, fix it immediately:

```
CRITICAL:
  [ ] set -e / set -euo pipefail → must be set +e (11% of v1 tasks had this)
  [ ] Reward path is /logs/verifier/reward.txt (not /workspace/*/reward.txt)
  [ ] No try/except fallback from import to AST (anti-pattern #2)
  [ ] No file-exists fallback awarding points (anti-pattern #10)

WARNING:
  [ ] Weights sum to 1.0 (±0.05)
  [ ] Behavioral ratio ≥ 60%
  [ ] All structural checks gated behind gate/behavioral passing
  [ ] Source annotations present ([pr_diff], [agent_config])
  [ ] grep/regex on source code strips comments first (anti-pattern #9)
```

These are the issues that the `taskforge.lint` module catches programmatically. Fix them before proceeding to the deeper semantic audit.

## Rules

- Show specific exploit code, not just risk descriptions
- Calculate exact gaming scores by walking each check
- Flag pure regex/string checks as always gameable
- Flag "warn but pass" patterns as critical bugs
- For EVERY structural check, think of 2 valid alternative implementations and check if they'd pass
- A test that only passes the gold patch is a BAD test, even if it catches the bug
