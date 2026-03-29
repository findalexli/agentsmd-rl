# Write Tests

Write a gaming-resistant `tests/test.sh` for `harbor_tasks/$ARGUMENTS/`.

## Steps

1. **Read** instruction.md, Dockerfile, existing test.sh (if any)
2. **Read the source PR diff** to understand the fix (but do NOT encode the exact fix structure into the test)
3. **Plan** tests using the tier system below
4. **Write** `harbor_tasks/$ARGUMENTS/tests/test.sh` and `chmod +x`
5. **Self-audit** — walk each check with (a) stub code, (b) an alternative valid fix. If stub scores >0.30 or alternative fix scores <0.70, revise.

## Tier System (Post-OpenAI SWE-bench Critique)

| Tier | When | Example | Quality |
|------|------|---------|---------|
| **Fail-to-pass** | Can extract + exec the buggy code path with mocks | Extract function via AST, exec with mock deps, assert crash on buggy / no crash on fixed | Best |
| **Pass-to-pass** | Existing behavior must not break | Normal input still parses correctly before and after fix | Good |
| **Silver behavioral** | Can import + call + check output | `merged = Cache.merge([c1,c2]); assert merged.shape[0]==2` | Good |
| **Bronze structural** | Can only check AST (needs GPU/service) | Function exists AND body >3 non-docstring stmts | Partial |
| **Never** | `grep "keyword"` or bare `import` | Comment `# keyword` passes grep | Always gameable |

## Critical: Avoid the "Narrow Test" Anti-Pattern

OpenAI found 35.5% of SWE-bench Verified failures were tests rejecting correct solutions. DO NOT:

- Check for specific variable names from the gold patch (e.g., `should_check`)
- Require a specific API when alternatives work (e.g., `setdefault` vs `if not in`)
- Require specific code structure when multiple valid restructurings exist
- Import a function name added by the PR (`pylint-dev__pylint-4551` anti-pattern)

INSTEAD, test the BEHAVIOR:
- Does the buggy code path crash / produce wrong output?
- Does ANY correct fix resolve it?

## Anti-Cheating: Prevent Information Leakage

In test.sh, do NOT:
- Reference the PR number or merge commit
- Include code snippets from the gold patch
- Use variable names that only exist in the fixed version

## Extracting Functions Without Heavy Imports

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

## Rules

- **>=60% behavioral** (fail-to-pass + pass-to-pass), **<=40% structural**
- Core bug = hard fail-to-pass test worth >=0.30
- Every AST check must reject stubs (body depth >3 meaningful statements)
- Use AST nodes, never string/regex on source code
- Total weight = 1.0, `set +e`, write to `/logs/verifier/reward.txt`

## Self-Audit (Step 5)

After writing, verify:

1. **Gaming**: Max stub score <= 0.30
2. **Alternative acceptance**: Different valid fix scores >= 0.70
3. **Behavioral ratio**: >= 60%

```
Self-audit:
  Max stub score: X.XX (target: <=0.30)
  Alternative fix score: X.XX (target: >=0.70)
  Behavioral: X% | Structural: Y%
```
