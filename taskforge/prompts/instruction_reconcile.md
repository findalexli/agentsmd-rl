# Reconcile instruction.md against tests

A quality judge flagged this task with rubric failures — most likely
`behavior_in_task_description` (instruction.md omits specifics the tests check)
or `no_solution_leakage` (instruction spoils the fix). Your job is to rewrite
`instruction.md` so it passes both rubrics **without breaking the oracle**
(nop=0, gold=1 must still hold).

## Files in `/workspace/task/`

- `instruction.md` — the current instruction, flagged by the judge
- `tests/test_outputs.py` — the hidden test oracle (do NOT modify)
- `solution/solve.sh` — the gold patch (do NOT modify)
- `environment/Dockerfile` — the environment (do NOT modify)
- `quality.json` — the judge's per-rubric verdict + reasoning

## Steps

### 1. Read the judge's findings

```bash
cat /workspace/task/quality.json
```

Focus on any rubric with `"outcome": "fail"`. Key rubrics:

- `behavior_in_task_description`: instruction omits specifics the tests check
  (file paths, function names, literal strings, SHAs, schema keys). You must
  ADD this information.
- `no_solution_leakage`: instruction spoils the fix (names file:line,
  contains patch snippet, dictates exact change). You must REPHRASE to
  describe only the symptom.
- `instruction_no_hint_leakage`: instruction gives away the bug's location
  when localization is part of the task. REPHRASE to describe the symptom,
  not the location.
- `solution_uniqueness_guard` / `tests_verify_behavior_not_text` /
  `test_not_tautological`: these are test problems, not instruction problems.
  If ONLY these are failing, write `{"abandoned": true, "reason": "tests need
  rewrite, not instruction"}` to `/workspace/task/reconcile_status.json` and
  stop.

### 2. Identify what each test asserts

```bash
cat /workspace/task/tests/test_outputs.py
```

For each `def test_*` function, list:
- What specific values it asserts on (literal strings, SHAs, file paths,
  function names, schema keys, error messages, HTTP codes)
- What behavior it exercises (which function called, with what inputs)

### 3. Rewrite instruction.md

Rules:

1. **Every asserted specific must be recoverable.** If a test does
   `assert "4acc9acc76d5079" in content`, the instruction must either:
   - (a) State the literal value: "the installer should verify SHA-256
     `4acc9acc76d5079…`", OR
   - (b) Cite a URL the agent can fetch to discover it: "use the SHA-256
     listed at https://forge.rust-lang.org/infra/other-installation-methods.html".
2. **Describe the SYMPTOM, not the fix.** "Parsing foo.toml with an empty
   section raises KeyError: 'name'; it should return `{}`" — good. "Change
   line 42 of parser.py to use `.get()`" — leakage, bad.
3. **Schema keys must be enumerated.** If a test expects a JSON response
   with `{"id", "name", "status"}`, spell those keys out.
4. **Error messages are content.** If a test asserts a specific error
   string, quote it in the instruction.
5. **Do not copy PR body prose.** Descriptions like "This PR fixes…" spoil
   the task.
6. **Preserve the existing task's intent.** Don't invent new requirements.
   If the original instruction describes the task in broad strokes, fill
   in specifics from the tests, but don't add unrelated requirements.

### 4. Re-validate

```bash
cd /workspace/task/environment && docker build -t task-env . > /dev/null 2>&1
```

Then NOP test (expect reward=0):
```bash
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro \
  -v /logs/verifier:/logs/verifier task-env bash /tests/test.sh
cat /logs/verifier/reward.txt   # must be 0
```

Then GOLD test (expect reward=1):
```bash
docker rm -f task-solved 2>/dev/null || true
docker run --name task-solved -v /workspace/task/solution:/solution:ro \
  task-env bash /solution/solve.sh
docker commit task-solved task-env-gold
docker rm task-solved
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro \
  -v /logs/verifier:/logs/verifier task-env-gold bash /tests/test.sh
cat /logs/verifier/reward.txt   # must be 1
```

If nop≠0 or gold≠1 after your rewrite, you've altered the task's semantics.
**Do NOT modify tests or solve.sh.** Revert your instruction.md changes
until nop=0 and gold=1 hold.

### 5. Write status

On success:
```bash
echo '{"reconciled": true, "nop_reward": 0, "gold_reward": 1}' > \
  /workspace/task/reconcile_status.json
```

If the judge-flagged issue is irreparable (e.g., tests require information
that's genuinely impossible to convey without leaking the solution, OR
reconcile broke the oracle and can't be fixed):

```bash
echo '{"abandoned": true, "reason": "..."}' > \
  /workspace/task/reconcile_status.json
```

Do NOT modify `tests/`, `solution/`, `environment/`, or `eval_manifest.yaml`.
The only file you should edit is `instruction.md`.
