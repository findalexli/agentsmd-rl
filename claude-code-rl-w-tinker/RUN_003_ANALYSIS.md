# Run 003 Analysis (2026-03-31)

## Config
- Model: Qwen/Qwen3.5-35B-A3B (MoE, 3B active, 64K context)
- Tasks: first 10 areal-* tasks, 4 rollouts each = 40 trials
- max_turns: 10, max_concurrent: 4, Docker sandboxes
- 1 training step

## Result: 0/40 successful, no training step executed

### Failure breakdown (47 total, some tasks retried)
| Category | Count | Root cause |
|---|---|---|
| Agent setup timeout (>360s) | 7 | Claude Code npm install too slow in Docker |
| Install failure (exit 1) | 4 | curl/npm network issues |
| No reward file | 36 | test.sh ran but didn't produce reward.txt — model couldn't fix the code |

### Root cause: reward file path mismatch (NOT model capability!)

Most task `test.sh` scripts write `reward.txt` to the **wrong path** for Harbor:
- Tasks write to: `/tests/reward.txt` or `$TASK_DIR/tests/reward.txt` (tinker-cookbook convention)
- Harbor expects: `/logs/verifier/reward.txt`

Only 2/10 tasks use the Harbor convention. The verifier ran and test scripts produced
scores (e.g., `Total score: 0.1` for areal-config-postinit-validation), but Harbor
couldn't find the reward file.

**Evidence**: `areal-config-postinit-validation` trial has `test-stdout.txt` with
actual test results and a score, but no `reward.txt` in `/logs/verifier/`.

### Other issues
1. **Claude Code install timeouts (11 failures)**: npm install >360s in Docker.
   Fix: pre-build images with Claude Code.

### Next steps
1. **Fix reward path** — either:
   a. Symlink `/tests/reward.txt` → `/logs/verifier/reward.txt` in the Harbor trial config
   b. Or fix `test.sh` in all tasks to write to `/logs/verifier/reward.txt`
   c. Or add a wrapper in the verifier that copies the file
2. Pre-build Docker images with Claude Code already installed
3. Re-run with the path fix — many tasks likely already got partial credit
