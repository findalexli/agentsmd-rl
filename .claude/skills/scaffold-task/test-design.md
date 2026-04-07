# Test Design Guide (Reference)

## CRITICAL: Structural integrity

Every assertion MUST be inside a `def test_*():` function. NEVER write:
- Bare assertions outside a function
- Code blocks after `# [origin] type` comments without a `def test_*():` wrapper
- Raw non-Python code (TypeScript, Rust, etc.) directly in the file

If you can't finish a test function, DELETE the placeholder entirely. An empty file is better than one with orphaned code that crashes pytest at import.

## Two-phase test writing (skeleton then fill)

**Phase 1 — Write the skeleton first:**
```python
def test_syntax_check():
    """Modified files parse without errors."""
    ...  # fill next

def test_core_behavior():
    """Function returns correct result for bug-triggering input."""
    ...  # fill next

def test_agents_md_documents_change():
    """AGENTS.md references the new module."""
    ...  # fill next
```

**Phase 2 — Fill each body.** Only after ALL signatures are written. This prevents orphaned code.

## Design principles

1. **Execute code, don't grep it.** For non-Python repos, at least ONE f2p test MUST use `subprocess.run()`. See [examples.md](examples.md) for the `_run_ts()` pattern.

2. **Grep is acceptable ONLY when:** the language genuinely can't be executed from Python (Svelte components, CUDA kernels, configs that need a running server). Document why.

3. **Fail-to-pass is primary.** Each f2p test MUST fail on the base commit and pass on a correct fix.

4. **Vary inputs.** Test >=3 different values including edge cases (None, empty, negative, boundaries).

5. **Anti-stub.** `assert result == expected`, not `assert result is not None`.

6. **Upstream P2P.** If the repo has pytest/jest/vitest tests, include them as pass-to-pass.

## 10 anti-patterns

| # | Pattern | Fix |
|---|---------|-----|
| 1 | Self-referential constant extraction | Compare against ground-truth values |
| 2 | Import fallback to AST | Import fails = test fails |
| 3 | Grep-only frontend tests | Execute via subprocess, not grep |
| 4 | Stub-passable tests | Assert return values |
| 5 | Superficial guard checks | Assert state CHANGED |
| 6 | Single parameter value | Vary across multiple values |
| 7 | Ungated structural tests | Gate behind behavioral pass |
| 8 | Compilation-ungated structural | Gate behind syntax check |
| 9 | Keyword stuffing | Check coherence |
| 10 | File-exists fallback | No existence checks for points |

## Source ref rules

For `agent_config` checks:
- `source.path` → the config file containing the rule (e.g., `AGENTS.md`)
- `source.commit` → the **base commit** (rule existed before this PR)
- Verify the file EXISTS at that commit before writing the ref
- Do NOT point source at the file being edited
- Do NOT use the merge commit (that's post-fix)

## Complete examples

See [examples.md](examples.md) for 3 gold-standard test files.
