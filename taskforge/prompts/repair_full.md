# Repair Task — Full Pipeline Repair (Dockerfile + tests/test_outputs.py)

You are repairing a benchmark task so its Docker oracle passes:
- **nop run** (no fix applied) → `/logs/verifier/reward.txt` = `0` (one or more f2p tests fail because the bug is present)
- **gold run** (`solve.sh` applied) → `/logs/verifier/reward.txt` = `1` (ALL tests pass)

## Hard rules — DO NOT touch

- `solution/solve.sh` (the gold patch — fixed contract)
- `instruction.md` (agent reads this — fixed contract)
- `eval_manifest.yaml` (Pydantic schema — touch only if absolutely needed; never invent new check ids)

## You CAN modify

- `environment/Dockerfile` (fix rot, add missing toolchains, scope dependencies)
- `tests/test_outputs.py` — specifically the `# === CI-mined tests ===` section. Adapt commands so they actually work in this Docker:
  - **Scope to the affected package**, not the whole monorepo (e.g. `pnpm --filter @effect/cluster test` instead of `pnpm test`)
  - **Drop tests that require unavailable infra** (GPU, K8s, AWS secrets, network)
  - **Drop redundant duplicates** (lint+typecheck+build redundancy if any one suffices)
- `tests/test.sh` — only if absolutely needed to install runtime deps

## Available tools in your sandbox

- `gh` CLI authenticated via `$GH_TOKEN` — query the PR, repo metadata
- `git` (repo cloned at base commit in `/workspace/<repo-short>/`)
- `docker` (with the worker user in the docker group — Docker-in-Docker via dind sidecar)
- Python 3 + pytest + yaml

## Recommended workflow

### 1. Understand what's broken

```bash
# What's the source PR?
cat /workspace/task/eval_manifest.yaml | grep -E "^  (repo|pr|base_commit|merge_commit):"

# What does the gold patch touch?
grep -E '^(diff --git|\+\+\+ b/)' /workspace/task/solution/solve.sh | head -20

# What CI did the merge actually run? (you may already see this — if not, query gh)
REPO=$(yq '.source.repo' /workspace/task/eval_manifest.yaml)
MERGE=$(yq '.source.merge_commit' /workspace/task/eval_manifest.yaml)
gh api "repos/$REPO/commits/$MERGE/check-runs?per_page=20" --jq '.check_runs[] | "\(.conclusion)\t\(.name)"'
```

### 2. Run the Docker oracle to see what's actually failing

```bash
# Build (or pull-from-ghcr if available)
cd /workspace/task && docker build -t task-env environment/

# nop run
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env bash /tests/test.sh
NOP=$(cat /logs/verifier/reward.txt 2>/dev/null || echo "?")

# gold run
docker rm -f task-solved 2>/dev/null
docker run --name task-solved -v /workspace/task/solution:/solution:ro task-env bash /solution/solve.sh
docker commit task-solved task-env-gold
docker rm task-solved
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env-gold bash /tests/test.sh
GOLD=$(cat /logs/verifier/reward.txt 2>/dev/null || echo "?")
echo "nop=$NOP gold=$GOLD"
```

You want **nop=0 gold=1**. Anything else is a bug.

### 3. Diagnose the failure

**Invariant before touching tests**: the desired state is `nop=0 gold=1`. Both `nop=0 gold=0` (no f2p signal — tests too lenient) and `nop=1 gold=*` (no signal either) are **regressions** worse than the starting state. If you find yourself making assertions weaker, stop and instead try **adding** a stronger test (see "When `nop=1`" below — the same logic applies in reverse to `gold=0`).

When `gold=0`: pytest output in the run shows which test(s) failed. Common patterns:

- **CI command runs whole monorepo** — too many unrelated failures. **Fix:** scope to `--filter <package>` based on what `solve.sh` touches.
- **Toolchain missing** (`cargo: not found`, `pnpm: not found`) — **Fix:** add install step in Dockerfile.
- **Test file path doesn't exist** — gold patch creates it; nop run fails because file's not there. That's CORRECT for an f2p; double-check test allows for ENOENT to count as failure.
- **Test depends on env var / secret** that CI had — drop the test or stub the env.
- **Network-required install at test time** (`pnpm install` inside test.sh) — move to Dockerfile, or pin a lockfile, or drop the test.

When `nop=1` (no f2p signal): all tests pass even WITHOUT the fix. **The right move is almost always to ADD a test, not drop one.** Why: a benchmark task with no failing test on the buggy base is meaningless — there's nothing for the agent to fix, and we'd be teaching the model the bug is fine.

Mining sources for adding f2p tests, in priority order:

1. **The PR's gold patch (`solve.sh` HEREDOC)** — the patch may include test files the author added. SWE-rebench V2 style:
   ```bash
   # Extract added test files from the gold patch
   awk '/^\+\+\+ b\//{p=$2} p ~ /(test_|tests?\/|\.test\.|\.spec\.)/{print}' /workspace/task/solution/solve.sh
   # For each `def test_*` / `it("...")` / `func TestX` line ADDED by the patch,
   # write a pytest function that runs that exact test by name.
   ```
   Each PR-author-written test is a perfect f2p: fails on base (test doesn't even exist or its assertion is on new behavior), passes on gold.

2. **GitHub CI's actual test commands** — the merge_commit's check-runs ran some tests. Pull them and pick the SCOPED variant relevant to the bug:
   ```bash
   REPO=$(yq '.source.repo' /workspace/task/eval_manifest.yaml)
   MERGE=$(yq '.source.merge_commit' /workspace/task/eval_manifest.yaml)
   gh api "repos/$REPO/commits/$MERGE/check-runs?per_page=50" \
     --jq '.check_runs[] | select(.conclusion=="success") | "\(.name)\t\(.details_url)"'
   # Pick check-runs related to the affected package/file from solve.sh.
   # Extract the actual `run:` command from .github/workflows/<wf>.yml.
   # Run that command — scoped to the affected directory — as a pytest subprocess.
   ```

3. **A behavioral test you write yourself** — last resort: read `instruction.md` for the symptom, write a Python `subprocess.run(...)` call that exercises the bug and asserts the post-fix expected output.

Whichever you choose, the contract is the same: **run on base → fail; run on gold → pass.** Do NOT try to satisfy `gold=1` by stripping or relaxing assertions until both base and gold pass — that yields `nop=0 gold=0` which is a worse outcome than the original problem (we lose the f2p signal entirely).

Cap: add 1–8 new tests if you need them, prioritizing the strongest signal (PR-added > scoped CI > synthesized).

### 4. Apply minimal fixes, iterate

After each modification, re-run the Docker oracle. Cap at **5 attempts** before abandoning.

### 5. Final verdict

When you achieve nop=0 + gold=1, write:

```bash
echo '{"scaffolded": true, "nop_reward": 0, "gold_reward": 1, "repair_full": true}' > /workspace/task/scaffold_status.json
```

If you genuinely cannot fix it (e.g., test requires GPU or external service), abandon honestly:

```bash
echo '{"abandoned": true, "reason": "<one-sentence cause>"}' > /workspace/task/scaffold_status.json
```

Do NOT write `"scaffolded": true` unless you actually saw `nop=0` AND `gold=1` from the Docker runs above. The pipeline trusts your verdict.

## Common heuristics for command scoping

- **pnpm monorepo**: PR touches `packages/<pkg>/...` → run `pnpm --filter @org/<pkg> test` or `pnpm -F @org/<pkg> <script>`
- **Cargo workspace**: PR touches `crates/<crate>/...` → run `cargo test -p <crate>`
- **Pytest mono**: PR touches `src/<module>/...` → run `pytest tests/<module>/` (if exists) or `pytest src/<module>/`
- **Go**: PR touches `pkg/<sub>/...` → run `go test ./pkg/<sub>/...`

## Self-check before declaring done

- [ ] Docker build succeeds
- [ ] nop run: `cat /logs/verifier/reward.txt` says `0`
- [ ] gold run: `cat /logs/verifier/reward.txt` says `1`
- [ ] You did NOT modify `solve.sh`, `instruction.md`, or invent new manifest check ids
