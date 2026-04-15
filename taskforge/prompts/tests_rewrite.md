# Rewrite tests to verify behavior (not text)

A quality judge flagged this task's tests. The tests assert on gold-specific
strings or verify text presence rather than behavior. Your job is to rewrite
`tests/test_outputs.py` (and only `tests/test.sh` if needed) so the tests
verify actual behavior — **without breaking the oracle** (nop=0, gold=1 must
still hold).

## Files in `/workspace/task/`

- `tests/test_outputs.py` — **you may rewrite this**
- `tests/test.sh` — **you may modify this if needed** (e.g., add dependencies)
- `instruction.md` — do NOT modify
- `solution/solve.sh` — do NOT modify
- `environment/Dockerfile` — do NOT modify (but note: modifying the image
  requires rebuilding)
- `eval_manifest.yaml` — do NOT modify
- `quality.json` — judge's rubric verdicts with specific reasoning
- `reconcile_status.json` (if present) — instruction was already reconciled
  this session; trust its current state

## Target rubrics — the EXACT questions the judge will ask next

After your rewrite, the same Opus judge will re-score your new tests against
the same rubrics. To pass, your rewrite must satisfy these verbatim judge
questions:

### `tests_verify_behavior_not_text` (Tier A)

> **Judge question:** Do tests import and CALL the code, execute subprocesses,
> or inspect behavior? FAIL if every test is `assert 'foo' in open(path).read()`
> with no execution.

**How to pass:** every `def test_*` must either (a) `subprocess.run` the code
and assert on output/exit code, (b) `import` a module and call a function and
assert on its return value, or (c) compile/build and assert artifact content.
Pure `assert "literal" in open(path).read()` fails this.

### `solution_uniqueness_guard` (Tier A)

> **Judge question:** Consider three alternative correct fixes the agent might
> write. Would each still pass test_outputs.py? FAIL if tests assert on
> gold-specific variable names, exact line positions, specific internal helper
> functions, or implementation details that a correct alternative fix wouldn't
> share.

**How to pass:** before committing a rewrite, write down three alternative
fixes for the bug (different variable names, different implementation
strategies). Trace each through your tests. If any would fail, your tests are
still too tight. Prefer assertions on OBSERVABLE OUTPUT (return values, stdout,
file contents produced) over assertions on SOURCE CODE STRUCTURE.

### `test_not_tautological` (Tier A)

> **Judge question:** For each f2p test, could a stub implementation (always
> returns default value, pass, return None, return empty collection) pass this
> test? FAIL if any f2p can be satisfied without implementing the bug fix.

**How to pass:** mentally stub every function under test with
`def foo(*args, **kwargs): return None` (or empty list / default). Run your
tests against this stub. If any f2p test passes, it's tautological. Replace
with assertions on the actual computed value or side effect.

### `anti_cheating_measures` (Tier A, partial)

> **Judge question:** Could the agent win by (a) reading /solution/ if it
> exists in container, (b) grepping env files for the expected test fixture
> value, (c) matching the literal fixture string without understanding the bug?
> FAIL if any route works.

**What you CAN do:** avoid embedding gold-specific fixture strings in test
assertions (use parameterized inputs/outputs). What you CAN'T do here: change
the Dockerfile or container layout. If the only remaining fail after your
rewrite is (a), write `abandoned=true, reason="anti_cheating needs Dockerfile
changes beyond test rewrite scope"`.

### When to abandon

If the ONLY remaining fails are structural (e.g., `pass_to_pass_coverage`
because eval_manifest needs new check entries, or `anti_cheating_measures`
solvable only by removing `COPY solution/` from Dockerfile), stop and write
abandoned=true with an explicit reason.

## Steps

### 1. Read what the judge flagged

```bash
cat /workspace/task/quality.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
for name, v in d.get('rubric_verdicts', {}).items():
    if v.get('outcome') == 'fail':
        print(f'{name}: {v.get(\"reason\", \"\")[:300]}')
"
```

Map each flagged rubric to a concrete test function to rewrite.

### 2. Read the current tests + solve.sh

```bash
cat /workspace/task/tests/test_outputs.py
cat /workspace/task/solution/solve.sh
```

For each `def test_*`, ask:
- Does it CALL the fixed code, or just grep source files?
- Does it assert on a VALUE, or on a literal from gold?
- Would three different correct fixes all pass this test?

### 3. Rewrite behavioral tests

Rules:

1. **Prefer subprocess over grep.** If testing Python code: `import module; call function; assert return`. If testing Node/Rust/Go: `subprocess.run([...])` and assert on exit code or stdout.

2. **Assert observable output, not implementation.** Bad: `assert 'newVariable' in content`. Good: `result = fn(bad_input); assert result == expected`.

3. **Replace gold-specific literals with parameterization.** If gold uses a variable named `uncroppedSize`, don't hard-code that name. Check that the computation PRODUCES the right number.

4. **Kill tautological asserts.** Replace `is not None` / `isinstance` / `len > 0` guards with assertions on actual content.

5. **Preserve coverage.** For every OLD f2p test, there should be a NEW f2p test covering the same bug (but behaviorally). Don't drop tests.

6. **Keep p2p tests.** Pass-to-pass tests (linter, upstream test suite) are usually fine. Don't touch them unless they're the ones flagged.

7. **Use structured assertions.** If the fix changes how a data structure is serialized, create the structure, serialize it, parse the output, assert on the parsed fields — not on the serialization text.

### 4. Re-validate

```bash
cd /workspace/task/environment && docker build -t task-env . >/dev/null 2>&1

# NOP — expect reward=0 (behavioral tests MUST still fail on base code)
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro \
  -v /logs/verifier:/logs/verifier task-env bash /tests/test.sh
cat /logs/verifier/reward.txt  # must be 0

# GOLD — expect reward=1 (behavioral tests MUST pass on fixed code)
docker rm -f task-solved 2>/dev/null || true
docker run --name task-solved -v /workspace/task/solution:/solution:ro \
  task-env bash /solution/solve.sh
docker commit task-solved task-env-gold
docker rm task-solved
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro \
  -v /logs/verifier:/logs/verifier task-env-gold bash /tests/test.sh
cat /logs/verifier/reward.txt  # must be 1
```

If either check fails, the new tests broke the oracle. Iterate:
- NOP=1: your new tests pass on the broken base. They're too loose — they no
  longer discriminate bug from fix. Tighten them.
- GOLD=0: your new tests fail on the correct fix. They're too strict or
  incorrect. Fix them — often the behavioral expectation was wrong, or
  subprocess path is incorrect.

**Iterate until nop=0 AND gold=1.** Do not proceed otherwise.

### 4b. Self-audit against the judge questions

Before declaring success, walk through each target rubric question with your
NEW test_outputs.py:

1. **tests_verify_behavior_not_text**: for each `def test_*` you rewrote, does
   it call code (subprocess / import) or only read files? If any test still
   does only `open().read() + grep`, keep rewriting.
2. **solution_uniqueness_guard**: imagine three different correct fixes. Write
   them down. Would each pass ALL your new tests? If even one wouldn't, your
   tests are still coupled to the gold implementation.
3. **test_not_tautological**: stub each function with a default-returning
   implementation. Do any of your new f2p tests still pass? If yes, those
   tests are tautological.

After your rewrite, the Opus judge will be re-invoked on the entire task and
will score all 20 rubrics. If a target rubric still fails, the retrofit
pipeline records the outcome but does not iterate further — so this self-audit
is your one shot.

### 5. Write status

On success:
```bash
echo '{"rewritten": true, "nop_reward": 0, "gold_reward": 1, "tests_touched": ["test_outputs.py"]}' > \
  /workspace/task/tests_rewrite_status.json
```

On abandon (the flagged rubrics are structural, not fixable via test rewrite):
```bash
echo '{"abandoned": true, "reason": "why"}' > \
  /workspace/task/tests_rewrite_status.json
```

If you rewrite but can't restore nop=0/gold=1:
```bash
echo '{"abandoned": true, "reason": "could not preserve oracle: nop=X gold=Y after rewrite"}' > \
  /workspace/task/tests_rewrite_status.json
```

The pipeline gates downloads on `result.valid` (nop=0 AND gold=1), so if the
rewrite breaks the oracle, your sandbox changes will NOT be written back to
the local task dir. The local copy is safe — just abandon and stop.

## Absolute rules

- Only `tests/test_outputs.py` and `tests/test.sh` may change
- nop=0 AND gold=1 must hold after rewrite (no exceptions)
- If you abandon, restore any partial edits
