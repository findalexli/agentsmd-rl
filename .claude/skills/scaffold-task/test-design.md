# Test Design Guide (Reference)

Design principles and anti-patterns for test_outputs.py.

## Design principles

1. **Call code, don't inspect it.** Import the function, call it with bug-triggering input, assert the result. AST is a last resort (only for GPU kernels, CUDA C++, or code needing unavailable model weights).

2. **Fail-to-pass is primary.** Each f2p test MUST fail on the base commit and pass on a correct fix. Test the *behavior*, not the *structure*.

3. **Vary inputs.** Never test with a single parameter value — agents hardcode constants. Test >=3 different values including edge cases (None, empty, negative, boundaries).

4. **Anti-stub.** Verify return values, not just "doesn't crash". `assert result == expected`, not `assert result is not None`.

5. **Upstream P2P.** If the repo has pytest/jest/vitest tests that run on CPU, include them as pass-to-pass checks.

6. **For non-Python repos:** Use `subprocess.run()` to compile/run/test. Python is the universal test harness.

## 10 anti-patterns

| # | Pattern | Fix |
|---|---------|-----|
| 1 | Self-referential constant extraction | Compare against ground-truth values |
| 2 | Import fallback to AST | Import fails = test fails |
| 3 | Grep-only frontend tests | Execute functions, not grep |
| 4 | Stub-passable tests | Assert return values |
| 5 | Superficial guard checks | Assert state CHANGED |
| 6 | Single parameter value | Vary across multiple values |
| 7 | Ungated structural tests | Gate behind behavioral pass |
| 8 | Compilation-ungated structural | Gate behind syntax check |
| 9 | Keyword stuffing | Check coherence |
| 10 | File-exists fallback | No existence checks for points |

## Non-Python examples

```python
# Rust
def test_cargo_check():
    r = subprocess.run(["cargo", "check"], cwd=REPO, capture_output=True, timeout=120)
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()}"

# Node
def test_build():
    r = subprocess.run(["node", "-e", "require('./dist/index.js')"], cwd=REPO, capture_output=True)
    assert r.returncode == 0
```
