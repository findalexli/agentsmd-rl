# Scaffold Quality Gates — design doc

**Date**: 2026-04-24
**Status**: Changes 1 & 4 implemented (commit pending); Changes 2, 3, 5 designed
**Context**: 2026-04-23 4-way eval exposed that 13/30 eval-set tasks had task-design bugs. Per-task audits of 9 broken tasks surfaced 5 distinct failure classes.

## Pipeline node order (from `taskforge/e2b_worker.py`)

```
scaffold      (line 704)   PR → task skeleton via claude -p
    ↓
qgate         (line 789)   programmatic lint (task_lint.lint_task)  ← CHANGE 1, 2a, 3
    ↓
rubric        (line ~)     Gemini↔Kimi rubric extraction
    ↓
enrich        (line 1985)  pass_to_pass enrichment                  ← CHANGE 5
    ↓
improve       (line ~)     test enhancement (conditional)
    ↓
validate      (line 1347)  Docker oracle (nop=0, gold=1)            ← CHANGE 2b, 4
    ↓
lint          (line 1416)  post-validation rubric review
    ↓
judge         (line 1479)  LLM quality judge
    ↓
promote to harbor_tasks/
```

## Change 1: Reward purity (IMPLEMENTED)

**Rubric**: `reward_is_pure_pytest` (Tier A, programmatic)
**Hook**: `taskforge/task_lint.py:lint_test_sh()` — runs at **qgate**
**Flags**:
- grep/awk/sed on pytest output (28 corpus hits)
- early `exit` before LLM judge block (142)
- `|| true` silencing critical pytest/plugin installs (198)
- reward written to non-canonical path, e.g. `reward.json` (21)
- reward value as JSON object `{reward: 1.0, ...}` (4)

**Retrofit result**: 303/1125 tasks (27%) fail at least one of these patterns. Run `python -m taskforge.task_lint --all-tasks` to regenerate.

**Evidence from audit**: `airflow-migration-0097` (grep gate), `airflow-git-hook-security` (early exit + JSON reward), `lotti-due-date-display-readme` (silent pytest-json-ctrf install).

## Change 4: Every gold test must pass (IMPLEMENTED as helper)

**Rubric**: `every_gold_test_passes` (Tier A, programmatic)
**Helper**: `taskforge/task_lint.py:check_all_gold_tests_passed(ctrf_path)`
**Hook needed**: `e2b_worker.node_validate_and_fix` (line 1347) — after gold trial completes, call this helper against the trial's `/logs/verifier/ctrf.json`.

**Reason current oracle doesn't catch this**: `validate.verdict()` uses aggregate `gold` reward. If test.sh is weakened (writes `1` regardless, or the grep gate doesn't detect all failures), gold=1 ships with broken tests inside.

**Evidence**: `ruff-primer-setup-script-claude-md` — test calls script with 1 arg, script requires 2, test asserts on error message that never appears. No correct implementation can pass it, yet oracle approved the task.

**Wire-up stub** (to add to `e2b_worker.node_validate_and_fix`):

```python
from taskforge.task_lint import check_all_gold_tests_passed

# After gold run completes at `gold_trial_dir`:
ctrf = gold_trial_dir / "logs" / "verifier" / "ctrf.json"
gold_test_fails = check_all_gold_tests_passed(ctrf)
if gold_test_fails:
    status["verdict"] = "fail_gold_partial"
    status["gold_test_fails"] = [f.snippet for f in gold_test_fails]
    return  # don't promote
```

## Change 2: Environment-dependency pre-validation

**Rubric**: `test_deps_in_dockerfile` (Tier A, programmatic/docker)
**Two-phase design**:

### Phase A (qgate, deterministic): parse + static-check
Hook in `task_lint.py`. New function:
```python
def lint_test_env_deps(task_dir: Path) -> list[Finding]:
    """Extract subprocess binaries from test_outputs.py; verify Dockerfile mentions each."""
    tests = (task_dir / "tests" / "test_outputs.py").read_text()
    # Binaries in subprocess.run([...]): cargo, ruff, bun, deno, npx, tsx, pnpm, go, rustc
    called = set(re.findall(r'subprocess\.run\(\s*\[\s*["\'](\w+)', tests))
    dockerfile = (task_dir / "environment" / "Dockerfile").read_text()
    # Naive: does Dockerfile mention the binary name in an install RUN?
    missing = [b for b in called
               if b not in ('python','python3','pip','pip3','bash','sh','git','grep','sed','awk','cat')
               and b not in dockerfile]
    return [Finding(rubric="test_deps_in_dockerfile", tier="A", severity="fail", ...) for b in missing]
```

**Trade-off**: fast + deterministic, but can false-positive (tool pre-installed in base image) and false-negative (tool name doesn't appear in Dockerfile even when installed via apt). Live-check (Phase B) is authoritative.

### Phase B (validate, authoritative): live-check via `docker run`
Hook in `validate.py` or `e2b_worker.node_validate_and_fix`. Before running the gold trial:
```python
for binary in extract_binaries(task_dir):
    rc = docker_run(image, f"command -v {binary} >/dev/null")
    if rc != 0:
        status["missing_deps"].append(binary)
```

**Evidence**: `deno-chore-remove-some-top-level` and `uv-self-update-quiet-stderr-important` both have tests calling `cargo` but Dockerfile doesn't install Rust. All 3 models produced correct patches; tests errored with `FileNotFoundError: cargo`.

**Allowlist of benign builtins**: `python, python3, pip, pip3, bash, sh, git, grep, sed, awk, cat, ls, find, test, true, false, echo, printf`.

## Change 3: Literal-string assertions must be instructed

**Rubric**: `substring_assertions_are_instructed` (Tier A, hybrid programmatic + LLM judge)
**Hook**: `task_lint.py:lint_test_outputs()` (already does AST parsing via `_iter_test_functions`)

**Programmatic phase**:
```python
# AST-walk test_outputs.py for: `assert "LITERAL" in <anything>`
# For each LITERAL > 6 chars, verify it appears verbatim in instruction.md.
# False-positive ignore: literals that are obviously code (identifiers, paths).
```

**Evidence**: `ClickHouse-pr-102080` asserts `"is larger than 5 MB. Large files should not be committed to git"` — instruction says the warning must contain "is larger than 5 MB" and "download them at test time" but never specifies the full sentence with period separator. Models used `;` and `,` — all correct warnings, oracle rejected them.

**Fix choices per violation**:
1. Relax the test to use `re.search(r"is larger than 5 MB.*download them")`
2. OR add the exact literal to instruction.md
3. OR split into multiple weaker assertions (`assert "larger than 5 MB" in out and "download" in out`)

## Change 5: Auto-insert lint requirement in instruction.md

**Hook**: scaffold post-processing, BEFORE qgate. Could go in `e2b_worker.node_scaffold` output filter OR as a new node `node_auto_enrich_lint_requirement` before qgate.

**Detection logic**:
```python
LINTERS = {'ruff', 'black', 'prettier', 'clippy', 'cargo fmt', 'cargo clippy',
           'eslint', 'stylelint', 'gofmt', 'golangci-lint', 'mypy', 'pyright'}
tests_text = (task_dir / "tests" / "test_outputs.py").read_text()
used = [l for l in LINTERS if l in tests_text]
if used:
    instr = (task_dir / "instruction.md")
    if not any(l in instr.read_text() for l in used):
        instr.write_text(instr.read_text().rstrip() + "\n\n## Lint requirements\n\n"
            f"Your solution must satisfy these linters: {', '.join(used)}.\n"
            "Running the repository's CI lint step should produce zero new errors.\n")
```

**Evidence**: `areal-openai-proxy-empty-session` — tests include `ruff format --check`. Opus+MiniMax wrote semantically correct fixes but failed on formatting. Instruction never mentioned formatting.

## Implementation priority

1. ✅ **Change 1** — already catches 303/1125 tasks. 5 regex patterns.
2. ✅ **Change 4 helper** — 40 lines. Needs wire-up in `e2b_worker.node_validate_and_fix`.
3. **Change 2 Phase A** — extends `lint_task`. ~40 lines, deterministic.
4. **Change 5** — auto-enrich lint requirement. ~25 lines, scaffold-time.
5. **Change 2 Phase B** — docker live-check. Requires running `docker run` at validate time.
6. **Change 3** — AST walker + instruction cross-check. ~60 lines.

## Combined effect on the 9 broken eval tasks

| Task | Change that would catch it |
|---|---|
| airflow-migration-0097 | Change 1 (grep gate) |
| airflow-git-hook-security | Change 1 (early exit + JSON reward) |
| lotti-due-date-display-readme | Change 1 (silent `|| true` on pytest-json-ctrf) |
| deno-chore-remove-some-top-level | Change 2 (cargo not in Dockerfile) |
| uv-self-update-quiet-stderr-important | Change 2 (cargo not in Dockerfile) |
| bun-build-make-ccnopch | Change 2 (bun/tsx missing) + Change 3 (`r"cxx"` regex) |
| ClickHouse-pr-102080 | Change 3 (punctuation-sensitive substring) |
| ruff-primer-setup-script-claude-md | Change 4 (gold doesn't pass 1 of 18 tests) |
| areal-openai-proxy-empty-session | Change 5 (ruff formatting requirement not stated) |

**All 9 would have been prevented or auto-corrected.**
