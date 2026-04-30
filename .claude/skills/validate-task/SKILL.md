---
name: validate-task
description: Validate a harbor task with Docker oracle test — builds the image, runs nop test (expect reward=0), applies gold patch, runs gold test (expect reward=1). Use after scaffolding to verify task quality.
argument-hint: "<task-name> (e.g., sglang-detokenizer-unbound-fix)"
allowed-tools: Bash(docker:*), Bash(python3:*), Read, Glob
---

# Validate Task

Oracle test for a harbor task: build Docker image, verify tests catch the bug (nop=0) and accept the fix (gold=1).

## Input

`$ARGUMENTS` = task name in `markdown_following/` or `markdown_edits/`

## Quick steps

1. **Build**: `docker build -t harbor-$TASK:latest markdown_following/$TASK/environment/`
2. **Nop test** (base commit, no fix): run test.sh → expect reward=0
3. **Gold test** (after solve.sh): run test.sh → expect reward=1
4. **Write verdict** to `status.json`

## Verdicts

| Verdict | Meaning |
|---------|---------|
| `pass` | nop=0, gold=1 — task works correctly |
| `fail_build` | Docker build failed |
| `fail_nop` | nop=1 — tests don't catch the bug |
| `fail_gold` | gold=0 — gold patch doesn't pass tests |
| `error` | Runtime error |

## Docker run pattern

```bash
TASK="$ARGUMENTS"
TASK_DIR="markdown_following/$TASK"

# Find task directory
if [ ! -d "$TASK_DIR" ]; then
    TASK_DIR="markdown_edits/$TASK"
fi

# Build
docker build -t harbor-$TASK:latest $TASK_DIR/environment/

# Nop test (no fix applied)
docker run --rm \
    -v $(pwd)/$TASK_DIR/tests:/tests:ro \
    -v /tmp/harbor-$TASK:/logs/verifier \
    harbor-$TASK:latest \
    bash -c "mkdir -p /logs/verifier && bash /tests/test.sh"
NOP_REWARD=$(cat /tmp/harbor-$TASK/reward.txt 2>/dev/null || echo "-1")

# Apply gold patch + gold test
docker run --rm \
    -v $(pwd)/$TASK_DIR/tests:/tests:ro \
    -v $(pwd)/$TASK_DIR/solution:/solution:ro \
    -v /tmp/harbor-$TASK:/logs/verifier \
    harbor-$TASK:latest \
    bash -c "mkdir -p /logs/verifier && bash /solution/solve.sh && bash /tests/test.sh"
GOLD_REWARD=$(cat /tmp/harbor-$TASK/reward.txt 2>/dev/null || echo "-1")

echo "nop=$NOP_REWARD gold=$GOLD_REWARD"
```

## E2B alternative

For faster validation at scale, use E2B sandboxes:
```bash
python -m taskforge.e2b --task-dir markdown_following --filter "$TASK"
```

## After validation

Update `status.json` with the verdict. If `fail_gold`, investigate test_outputs.py for assertion bugs.
