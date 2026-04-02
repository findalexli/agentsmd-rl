# Validate Task

Docker oracle test for `harbor_tasks/$ARGUMENTS/`. Builds the image, runs nop (base commit) and gold (solve.sh), checks binary reward.

Run AFTER `/scaffold-task` has created all files.

## Inputs

`harbor_tasks/$ARGUMENTS/` must have: instruction.md, task.toml, eval_manifest.yaml, tests/test.sh, solution/solve.sh, environment/Dockerfile.

## Steps

### 1. Build Docker image

```bash
docker build -q -t harbor-$ARGUMENTS:latest harbor_tasks/$ARGUMENTS/environment/
```

If build fails → verdict `fail_build`, note the error.

### 2. Nop test (base commit, no fix applied)

```bash
docker run --rm \
  -v $(pwd)/harbor_tasks/$ARGUMENTS/tests:/tests:ro \
  -v /tmp/nop_logs:/logs/verifier \
  harbor-$ARGUMENTS:latest \
  bash -c "mkdir -p /logs/verifier && chmod +x /tests/test.sh && /tests/test.sh"
```

Read `/tmp/nop_logs/reward.txt`.
- **Expected: `0`** — at least one fail-to-pass check must fail on buggy code.
- If reward is `1` → **CRITICAL**: tests can't distinguish buggy from fixed code.

### 3. Gold test (solve.sh applied)

```bash
docker run --rm \
  -v $(pwd)/harbor_tasks/$ARGUMENTS/tests:/tests:ro \
  -v $(pwd)/harbor_tasks/$ARGUMENTS/solution:/solution:ro \
  -v /tmp/gold_logs:/logs/verifier \
  harbor-$ARGUMENTS:latest \
  bash -c "mkdir -p /logs/verifier && chmod +x /tests/test.sh /solution/solve.sh && /solution/solve.sh 2>/dev/null && /tests/test.sh"
```

Read `/tmp/gold_logs/reward.txt`.
- **Expected: `1`** — gold patch must pass all checks.
- If reward is `0` → investigate which check fails. Fix test.sh or solve.sh.

### 4. Write verdict to status.json

```bash
python3 -m taskforge.validate --task $ARGUMENTS --phase validate --verdict <pass|fail_gold|fail_nop|fail_build|error> --note "<details>"
```

## Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| **pass** | nop=0, gold=1 | Task is production-ready |
| **fail_build** | Docker build failed | Fix Dockerfile |
| **fail_nop** | nop=1 (tests don't catch the bug) | Fix test.sh — add real fail-to-pass checks |
| **fail_gold** | gold=0 (gold patch fails tests) | Fix test.sh or solve.sh |
| **error** | Runtime error (timeout, crash) | Investigate logs |

## Rules

- Do NOT re-audit test quality — that's part of `/scaffold-task`
- Do NOT analyze instruction.md — that's part of `/scaffold-task`
- This command is purely mechanical: build, run, check scores, record verdict
- Can be run in batch across many tasks
