# Validate and Fix Task

You have a benchmark task at `/workspace/task/`. Your job is to make it pass Docker oracle validation. You have full access to Docker and can run any command.

## Context

Read `/workspace/task/status.json` if it exists — previous agents may have left notes about what they found or fixed.

## What Must Pass

All four of these must succeed:

### 1. Docker build
```bash
cd /workspace/task/environment && docker build -t task-env .
```
If it fails, read the error, fix the Dockerfile, try again.

### 2. NOP test (base commit, no fix — expect reward=0)
```bash
rm -f /logs/verifier/reward.txt
docker run --rm \
  -v /workspace/task/tests:/tests:ro \
  -v /logs/verifier:/logs/verifier \
  task-env bash /tests/test.sh
cat /logs/verifier/reward.txt
```
The reward MUST be `0`. This means the fail-to-pass tests correctly fail on the buggy base code. If reward is `1`, the tests are too weak — they can't distinguish broken from fixed code. Read the pytest output, understand which tests passed that shouldn't have, and rewrite the f2p tests to check behavior that actually differs.

### 3. Gold test (solve.sh applied — expect reward=1)
```bash
# Apply the gold fix inside a container and commit
docker rm -f task-solved 2>/dev/null || true
docker run --name task-solved \
  -v /workspace/task/solution:/solution:ro \
  task-env bash /solution/solve.sh
docker commit task-solved task-env-gold
docker rm task-solved

# Run tests on the fixed code
rm -f /logs/verifier/reward.txt
docker run --rm \
  -v /workspace/task/tests:/tests:ro \
  -v /logs/verifier:/logs/verifier \
  task-env-gold bash /tests/test.sh
cat /logs/verifier/reward.txt
```
The reward MUST be `1`. This means all tests pass after the gold fix. If reward is `0`, read the pytest output to see which tests failed:
- If solve.sh failed to apply (patch error) → fix solve.sh
- If tests are too strict (testing exact strings that the fix changed differently) → relax tests
- If tests need a dependency not in the Dockerfile → fix the Dockerfile and rebuild

### 4. Rubric judge (if rubric rules exist)
```bash
python3 /workspace/judge.py --manifest /workspace/task/eval_manifest.yaml --repo <REPO_WORKDIR>
```
The judge reads the `rubric:` section of eval_manifest.yaml and checks if the gold solution follows those style/convention rules. If ICR < 0.8, read which rules failed from stderr and assess whether the rubric rules are too strict or the gold solution genuinely violates them. You may adjust individual rubric rules that are genuinely unreasonable, but do NOT remove all rubric rules or leave the section empty — a previous agent enriched them from the repo's config files.

## Important: Getting pytest output

When a test fails, you need the detailed output to diagnose. Run tests with verbose output:
```bash
docker run --rm \
  -v /workspace/task/tests:/tests:ro \
  -v /logs/verifier:/logs/verifier \
  task-env bash -c "python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; cat /logs/verifier/reward.txt"
```

## What you can fix

- `environment/Dockerfile` — missing packages, wrong base image, git checkout issues
- `tests/test_outputs.py` — tests that are too weak, too strict, or have bugs
- `solution/solve.sh` — patch application errors, wrong paths
- `eval_manifest.yaml` — check IDs out of sync with test functions, unreasonable rubric rules

Do NOT modify `instruction.md` or `tests/test.sh` (boilerplate).

## When you're done

Read the existing `/workspace/task/status.json` first (previous agents wrote their nodes there), then **merge** your validate node into it. Do NOT overwrite the entire file — preserve existing nodes:

```python
import json
status = json.load(open('/workspace/task/status.json'))
if 'nodes' not in status:
    status['nodes'] = {}
status['nodes']['validate'] = {
    "status": "pass or fail",
    "nop_reward": 0.0,
    "gold_reward": 1.0,
    "attempts": 2,
    "notes": "What you found and fixed"
}
json.dump(status, open('/workspace/task/status.json', 'w'), indent=2)
```

Keep iterating until all four checks pass. If after several attempts something is fundamentally broken (wrong base commit, repo deleted, PR reverted), update status.json with a clear explanation and stop.
