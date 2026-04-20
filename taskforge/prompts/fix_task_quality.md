# Fix Task Quality

Fix all quality issues in a task — tests AND instruction — in a single coordinated pass.

## Context

A quality judge (`quality.json`) flagged this task with rubric failures. Your job is to fix
**both tests and instruction.md** so the task passes all rubrics while keeping the oracle
intact (nop=0, gold=1).

Read `/workspace/task/quality.json` first — it tells you exactly what's wrong.

## Files in `/workspace/task/`

- `quality.json` — **start here**. Per-rubric verdicts with reasons.
- `instruction.md` — what the agent sees (you MAY rewrite this)
- `tests/test_outputs.py` — test oracle (you MAY rewrite this)
- `eval_manifest.yaml` — check declarations (you MAY update this)
- `solution/solve.sh` — the gold patch (do NOT modify)
- `environment/Dockerfile` — the environment (do NOT modify)
- `status.json` — previous validation notes

The full repo is cloned at `/workspace/repo/` at the base commit. Browse it to understand
the codebase. Note: `/workspace/repo/` is for reference — `test_outputs.py` runs inside
Docker where the repo path is different (check Dockerfile WORKDIR).

## Step 1: Read quality.json and classify issues

```bash
cat /workspace/task/quality.json
```

Focus on any rubric with `"outcome": "fail"`. Issues fall into two buckets:

**Test issues** (fix in test_outputs.py):
- `tests_verify_behavior_not_text` — tests use grep/string matching instead of executing code
- `test_not_tautological` — tests pass on trivial stubs (e.g., `return None`)
- `solution_uniqueness_guard` — tests reject valid alternative fixes (too coupled to gold patch)

**Instruction issues** (fix in instruction.md):
- `behavior_in_task_description` — instruction.md omits specifics the tests check
  (file paths, function names, literal strings, error messages, schema keys)
- `no_solution_leakage` — instruction spoils the fix (names file:line, contains patch snippet)
- `instruction_no_hint_leakage` — instruction gives away the bug's location when
  localization is part of the task

**Both** — many tasks have issues in BOTH buckets. Fix them together so they stay consistent.

## Step 2: Read all task files

Read every file listed above. Also fetch the PR diff:

```bash
# Read task.toml for source_repo and source_pr
cat /workspace/task/task.toml
# Then fetch the diff
gh pr diff <PR_NUMBER> --repo <REPO>
```

Understand:
- What functional behavior changed?
- What inputs trigger the old (broken) behavior?
- What is the correct output after the fix?

## Step 3: Fix tests (if test issues flagged)

### 3a. Rewrite grep-only tests to behavioral tests

**CRITICAL**: At least ONE `fail_to_pass` test MUST use `subprocess.run()` to execute
actual code. Grep-only tests are not acceptable for f2p checks.

For Node/TypeScript repos:
```python
import subprocess, json
from pathlib import Path

REPO = "/workspace/<repo-name>"  # Match Dockerfile WORKDIR

def _run_ts(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)

def test_core_behavior():
    """The function returns the correct result for the bug-triggering input."""
    r = _run_ts("""
import { targetFunction } from './src/module.js';
const result = targetFunction(bugTriggeringInput);
console.log(JSON.stringify(result));
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data == expectedValue
```

For Python repos:
```python
def test_core_behavior():
    r = subprocess.run(
        ["python3", "-c", """
from module import target_function
result = target_function(edge_case_input)
assert result == expected, f"Got {result}"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
```

For Rust repos: use `cargo check` / `cargo test`. For Go repos: use `go vet` / `go test`.

### 3b. Fix solution_uniqueness_guard

Tests should verify BEHAVIOR, not the exact text of the gold patch. If a test does
`assert "specific_variable_name" in content`, ask: would a different correct fix also
have this string? If not, test the behavior instead.

### 3c. Add repo CI as pass_to_pass gates

Find the repo's test commands (package.json scripts, Makefile targets, CI workflows)
and add a p2p test that runs the relevant subset.

## Step 4: Fix instruction.md (if instruction issues flagged)

### 4a. behavior_in_task_description

Every specific value that tests assert on must be recoverable from instruction.md.
If a test does `assert "4acc9acc76d5079" in content`, the instruction must either:
- State the literal value, OR
- Cite a URL the agent can fetch to discover it

### 4b. no_solution_leakage / instruction_no_hint_leakage

Describe the **symptom**, not the fix:
- GOOD: "Parsing foo.toml with an empty section raises KeyError: 'name'; it should return `{}`"
- BAD: "Change line 42 of parser.py to use `.get()`"

If the instruction names the exact file and function to change, and localization is part
of the task's difficulty, rephrase to describe what goes wrong from the user's perspective.

### 4c. Keep instruction and tests consistent

**This is why these fixes must happen together.** After rewriting tests:
- If you ADDED a behavioral assertion (e.g., checking a specific error message),
  make sure instruction.md mentions that error message
- If you REMOVED a string-matching test, the instruction no longer needs to spell
  out that specific string
- The instruction should describe what the agent needs to KNOW to fix the bug,
  and the tests should verify the FIX works — they meet in the middle

## Step 5: Update eval_manifest.yaml

Ensure every `def test_*()` function has a matching check:
```yaml
checks:
  - id: test_core_behavior      # must match function name exactly
    type: fail_to_pass
    origin: pr_diff
    description: ...
```

## Step 6: Self-audit

Before finishing, verify:
1. `python3 -c "import ast; ast.parse(open('/workspace/task/tests/test_outputs.py').read())"` — no syntax errors
2. At least ONE f2p test uses `subprocess.run()`
3. Every `def test_*()` has a matching check in eval_manifest.yaml
4. No `NotImplementedError`, no `{{` placeholders
5. Instruction.md describes symptom, not fix
6. Every asserted specific in tests is recoverable from instruction.md

## Step 7: Validate

Build and run the oracle to confirm your changes didn't break anything:

```bash
cd /workspace/task/environment && docker build -t task-env . > /dev/null 2>&1
```

NOP test (expect reward=0):
```bash
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro \
  -v /logs/verifier:/logs/verifier task-env bash /tests/test.sh
cat /logs/verifier/reward.txt   # must be 0
```

GOLD test (expect reward=1):
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

If nop≠0 or gold≠1, iterate — don't just give up. The most common causes:
- New behavioral test has a wrong assertion (fix the test)
- Instruction change altered task semantics (revert instruction, keep tests)
- Test timeout too short (increase it)

## Step 8: Write status

On success:
```json
{"fixed": true, "tests_changed": true, "instruction_changed": true, "nop_reward": 0, "gold_reward": 1}
```

Write to `/workspace/task/reconcile_status.json`. Set `tests_changed` / `instruction_changed`
to false if you didn't need to modify that file.

If truly irreparable:
```json
{"abandoned": true, "reason": "..."}
```

## What NOT to do

- Do NOT modify solve.sh or Dockerfile
- Do NOT add tests outside the PR's scope
- Do NOT use `assert True` or `assert "string"` as real assertions
- Do NOT use `origin: config_edit` — valid origins are: `pr_diff`, `repo_tests`, `agent_config`, `static`
