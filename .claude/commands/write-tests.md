# Write Tests

Write a gaming-resistant `tests/test.sh` for `harbor_tasks/$ARGUMENTS/`.

## Steps

1. **Read** instruction.md, user_simulation_prompt.md, Dockerfile, existing test.sh, original_session.json
2. **Plan** tests using the tier system below
3. **Write** `harbor_tasks/$ARGUMENTS/tests/test.sh` and `chmod +x`
4. **Self-audit** — walk each check with stub code, calculate max gaming score. If >0.30, revise.

## Tier System

| Tier | When | Example | Gameable? |
|------|------|---------|-----------|
| **Gold** | Numerical output verifiable against reference lib | Quantize with libggml, dequant with agent code, compare within tolerance | No |
| **Silver** | Can import + call + check output | `merged = Cache.merge([c1,c2]); assert merged.shape[0]==2` | No |
| **Bronze** | Can only check AST (needs GPU/service) | Function exists AND body >3 non-docstring stmts | Partially |
| **Never** | `grep "keyword"` or bare `import` | Comment `# keyword` passes grep | Always |

## Rules

- **≥60% behavioral** (Gold/Silver), **≤40% structural** (Bronze)
- Core bug = hard behavioral test worth ≥0.15
- Every AST check must reject stubs (body depth >3 meaningful statements)
- Every import check must call something
- Use AST nodes, never string/regex on source code
- Test error handling (bad inputs → error dict, not crash)
- If task says "write tests", run agent's tests with pytest (>50% pass)
- Total weight = 1.0, `set +e`, write to `/logs/verifier/reward.txt`

## Anti-Stub Pattern

```python
# WRONG: accepts `def merge(): pass`
if node.name == "merge": print("PASS")

# RIGHT: rejects stubs
body = [s for s in node.body if not isinstance(s, (ast.Expr, ast.Pass))
        or (isinstance(s, ast.Expr) and not isinstance(s.value, (ast.Constant,)))]
if len(body) < 3: sys.exit(1)
```

## Self-Audit (Step 4)

After writing, walk every check assuming the agent creates minimal stubs (`def f(): pass`, empty classes, keyword comments). For each check answer: does the stub pass? Sum the points. If total >0.30:
- Replace string/regex checks with AST or behavioral equivalents
- Add body-depth rejection to any pure existence check
- Increase behavioral weight

Print the final audit:
```
Gaming analysis:
  Max stub score: X.XX (target: ≤0.30)
  Behavioral: X% | Structural: Y%
  | # | Weight | Tier | Stub passes? |
```
