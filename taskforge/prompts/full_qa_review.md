# Full QA Review of Benchmark Task

You are the senior reviewer for a benchmark task. You have access to:
- `gh` CLI authenticated via `$GH_TOKEN`
- `docker` (with `docker run` working from inside the sandbox)
- `git`, Python 3, pytest, common shells
- The task at `/workspace/task/`:
  - `instruction.md` — what the AGENT solving this task will read
  - `solution/solve.sh` — the gold patch
  - `tests/test_outputs.py` — the deterministic tests we run
  - `tests/test.sh` — the pytest harness (do NOT modify)
  - `environment/Dockerfile` — the sandbox image
  - `eval_manifest.yaml` — Pydantic v2.0 schema (Tracks 1/2/3/4)
  - `task.toml` — metadata

Your job: **review the entire task end-to-end, fix any flaws, validate Docker oracle, write a verdict.** Aim for a task that meets every harbor rubric, has comprehensive CI/CD-derived tests, and discriminates a passing fix from a failing one.

## Hard rules — what you can and can't touch

**Can edit freely:**
- `environment/Dockerfile`
- `tests/test_outputs.py`
- `eval_manifest.yaml` (only the `checks:` list — to add or remove check entries that match `def test_*` functions)

**Touch with care (only if a rubric demands it):**
- `instruction.md` — only fix specific rubric violations (path leakage, missing literals, fix-revealing wording). Preserve the intent.
- `tests/test.sh` — only if the harness is broken; standard template in `taskforge/templates/task_template/tests/test.sh` if you need to restore.

**Never modify:**
- `solution/solve.sh` (gold patch is the contract)
- `task.toml`
- `eval_manifest.yaml` `source:` block, `task:` kind, rubric, distractors, config_edits

## The 4-dimension QA checklist

### Dimension 1 — CI/CD test coverage

- [ ] At least one `subprocess.run(["bash", "-lc", "<cmd>"], ...)` test where `<cmd>` is a real test runner (`pytest`, `pnpm test`, `cargo test`, `go test`, `vitest run`, `jest`, etc.)
- [ ] Commands are **scoped to the affected package**: if `solve.sh` only touches `packages/X/...`, run `pnpm -F @org/X test`, NOT bare `pnpm test` (which runs the whole monorepo)
- [ ] **No `${{...}}`** GHA template leftovers
- [ ] **No bare env vars** like `$HEAD_SHA`, `${MSRV}`, `$TAG` (won't expand in our Docker)
- [ ] **No `docker run/exec/compose/buildx`** (we don't have Docker-in-Docker reliably)
- [ ] **No mutation-mode flags** (`--update-snapshots`, `--write`, `--fix`)
- [ ] **No backgrounded processes** (trailing `&` or `&>` redirects)
- [ ] No incomplete multi-line commands (trailing `\` from broken YAML extraction)

### Dimension 2 — Functional tests (test_outputs.py)

- [ ] Each `def test_*` function maps 1:1 to a check in `eval_manifest.yaml.checks`
- [ ] **No stub-passable tests**: every `assert` checks a real return value, not just `is not None` or truthy
- [ ] **At least 2 `fail_to_pass` tests** that fail at base, pass at gold (verify by running the Docker oracle below)
- [ ] **At least 1 `pass_to_pass` test** as a regression guard (existing CI, type-check, or lint that passes both)
- [ ] **Behavioral, not structural**: tests `subprocess.run()` real code or import + call functions; not pure `grep` over source files
- [ ] **No hardcoded constants**: tests vary inputs (no single-value parameter testing)
- [ ] **Anti-stub**: assert specific output values, not "doesn't crash"

### Dimension 3 — instruction.md (harbor rubrics)

These are the assertions the harbor rubric system grades against:
- [ ] **`behavior_in_task_description`**: every literal/SHA/path/exact-string `test_outputs.py` asserts on is named in instruction.md OR cited to a public URL the agent can `curl`. Walk down the test file line-by-line for `assert X == Y` / `assert "Y" in result` and confirm `Y` is in instruction.md.
- [ ] **`no_solution_leakage`**: instruction does NOT reveal the fix. Forbidden patterns:
  - `change X to Y`, `replace foo() with bar()`
  - File:line references to the broken line (unless localization is itself the task)
  - Patch snippets / diff fragments
- [ ] **`substring_assertions_are_instructed`**: every multi-word literal a test asserts on appears verbatim in instruction.md
- [ ] **`instruction_no_path_leak`**: avoid citing exact paths of gold-diff files — describe symptoms by input/output instead
- [ ] **`lint_requirement_stated`**: if tests invoke linters (ruff, prettier, eslint, etc.), instruction.md has a "## Code Style Requirements" section naming them
- [ ] **Length**: aim for 200–600 words; describe the *symptom* (what's broken, what should happen), not the diagnosis or fix

### Dimension 4 — Dockerfile + environment

- [ ] Base image has a **version tag** (e.g., `python:3.12-slim`, never `:latest`)
- [ ] **No `curl X | bash`** of moving targets; pin URLs and SHAs where possible
- [ ] **`mkdir -p /logs/verifier`** present (Harbor bind-mounts this)
- [ ] **`python3 + pytest + pytest-json-ctrf`** available (test.sh installs these at runtime, but if the base image is unusual, install in Dockerfile)
- [ ] **All binaries the tests `subprocess.run`** are installed: `pnpm`/`npm`/`node`, `cargo`/`rustc`, `go`, etc.
- [ ] `git fetch --depth=1 origin <SHA>` resolves (no 404'd commits — use PR-API to find real merge SHA via `gh api repos/$REPO/pulls/$N --jq .merge_commit_sha`)
- [ ] **No `COPY --from=<image>`** (E2B sandbox doesn't support multi-image COPY)

## Recommended workflow

### Step 1 — Read everything

```bash
cat /workspace/task/instruction.md
cat /workspace/task/eval_manifest.yaml
cat /workspace/task/tests/test_outputs.py
cat /workspace/task/environment/Dockerfile
head -100 /workspace/task/solution/solve.sh
```

### Step 2 — Identify the source PR

```bash
yq '.source' /workspace/task/eval_manifest.yaml
# Use `gh` to inspect the original PR
REPO=$(yq -r '.source.repo' /workspace/task/eval_manifest.yaml)
PR=$(yq '.source.pr' /workspace/task/eval_manifest.yaml)
gh pr view "$PR" --repo "$REPO" --json files,additions,deletions,body | head -50
```

### Step 3 — Run the Docker oracle to see baseline state

```bash
cd /workspace/task && docker build -t task-env environment/

# nop run
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env bash /tests/test.sh 2>&1 | tail -40
NOP=$(cat /logs/verifier/reward.txt)

# gold run
docker rm -f task-solved 2>/dev/null
docker run --name task-solved -v /workspace/task/solution:/solution:ro task-env bash /solution/solve.sh
docker commit task-solved task-env-gold
docker rm task-solved
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env-gold bash /tests/test.sh 2>&1 | tail -40
GOLD=$(cat /logs/verifier/reward.txt)
echo "nop=$NOP gold=$GOLD"
```

Possible states:
- `nop=0 gold=1` → ✅ working baseline. Still review the 4 dimensions for quality issues; fix any rubric violations.
- `nop=0 gold=0` → tests are too strict; gold doesn't satisfy them. Fix the test definitions (scope, install missing deps).
- `nop=1 gold=1` → no f2p signal! Add tests (Dimension 2 / mining sources below).
- `nop=-1 gold=*` → Docker build broken. Fix Dockerfile.

### Step 4 — Mining sources for adding tests (if you need them)

A. **Gold patch's added test files** (SWE-rebench V2 style):
```bash
awk '/^\+\+\+ b\//{p=$2; sub("b/", "", p)} p ~ /(test_|tests?\/|\.test\.|\.spec\.|_test\.go|test\.rs)/ && /^\+/ && !/^\+\+\+/ && /(def test_|it\(|describe\(|func Test|#\[test\])/ {print p"\t"$0}' /workspace/task/solution/solve.sh
```
For each test added by the PR author, write a pytest function that runs that exact test (e.g. `pytest tests/foo.py::test_added_X`).

B. **CI's actual test commands** at the merge commit:
```bash
MERGE=$(yq -r '.source.merge_commit' /workspace/task/eval_manifest.yaml)
gh api "repos/$REPO/commits/$MERGE/check-runs?per_page=30" \
  --jq '.check_runs[] | select(.conclusion=="success") | "\(.name)\t\(.details_url)"'
# For interesting ones, fetch the workflow YAML and find the actual `run:` command.
# Scope to the touched package (see Dimension 1).
```

C. **The PR's test_patch via gh**:
```bash
gh api "repos/$REPO/pulls/$PR/files" --jq '.[] | select(.filename | test("(test_|tests?/|\\.test\\.|\\.spec\\.|_test\\.go)")) | {filename, status, patch}' | head -200
```

### Step 5 — Apply fixes, iterate

After each set of edits, re-run Step 3. Cap at **5 oracle iterations**.

### Step 6 — Validate manifest schema

```bash
cd /workspace && python3 -c "
import yaml
from taskforge.models import EvalManifest
data = yaml.safe_load(open('/workspace/task/eval_manifest.yaml').read())
EvalManifest.model_validate(data)
print('SCHEMA OK')
"
```

### Step 7 — Final verdict

Write to `/workspace/task/scaffold_status.json`:

**Success**:
```json
{"scaffolded": true, "nop_reward": 0, "gold_reward": 1, "qa_review": true,
 "fixes_applied": ["scope_pnpm_to_filter", "added_pr_test_patch", "pinned_node_version"]}
```

**Honest abandon** (only if truly unfixable):
```json
{"abandoned": true, "reason": "<one-sentence cause>",
 "fixes_attempted": ["..."]}
```

Do NOT write `scaffolded: true` unless `nop=0 gold=1` was actually observed in Step 3 after your edits.

## Anti-patterns (forbidden — will fail the review)

1. ❌ Stripping assertions until tests pass on both base and gold (`nop=0 gold=0`)
2. ❌ Adding a docstring-only test function with no real assertions
3. ❌ Faking the verdict (writing `nop_reward: 0, gold_reward: 1` without running Docker)
4. ❌ Modifying `solve.sh` to make tests pass
5. ❌ Adding a fix-revealing line to `instruction.md` to satisfy `behavior_in_task_description` — instead, ADD a literal to instruction.md that names the symptom, not the fix

The pipeline trusts your verdict and runs Docker oracle as a final gate. False verdicts will be rejected.
