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

### Audit Report Format

```markdown
## Test Audit: $ARGUMENTS
### Reliability Score: X/10
### Narrow Test Score: X/10 (10 = accepts all valid implementations, 0 = only gold patch passes)

### Gaming Analysis
- Max stub score: X.XX
- Max comment-injection score: X.XX

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

### Tier System

| Tier | When | Example | Quality |
|------|------|---------|---------|
| **Fail-to-pass** | Can extract + exec the buggy code path with mocks | Extract function via AST, exec with mock deps, assert crash on buggy / no crash on fixed | Best |
| **Pass-to-pass** | Existing behavior must not break | Normal input still parses correctly before and after fix | Good |
| **Silver behavioral** | Can import + call + check output | `merged = Cache.merge([c1,c2]); assert merged.shape[0]==2` | Good |
| **Bronze structural** | Can only check AST (needs GPU/service) | Function exists AND body >3 non-docstring stmts | Partial |
| **Never** | `grep "keyword"` or bare `import` | Comment `# keyword` passes grep | Always gameable |

### Avoid the "Narrow Test" Anti-Pattern

DO NOT:
- Check for specific variable names from the gold patch
- Require a specific API when alternatives work (e.g., `setdefault` vs `if not in`)
- Require specific code structure when multiple valid restructurings exist
- Import a function name added by the PR

INSTEAD, test the BEHAVIOR: does the buggy code path crash / produce wrong output? Does ANY correct fix resolve it?

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
  Behavioral: X% | Structural: Y%
```

## Rules

- Show specific exploit code, not just risk descriptions
- Calculate exact gaming scores by walking each check
- Flag pure regex/string checks as always gameable
- Flag "warn but pass" patterns as critical bugs
- For EVERY structural check, think of 2 valid alternative implementations and check if they'd pass
- A test that only passes the gold patch is a BAD test, even if it catches the bug
