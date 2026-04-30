# Scaffold Quality Gates — design doc

**Date**: 2026-04-24
**Status**: Changes 1 & 4 implemented (commit pending); Changes 2, 3, 5 designed
**Context**: 2026-04-23 4-way eval found 13/30 eval-set tasks had task-design bugs. Per-task audit of 9 of them surfaced 5 distinct failure classes — one gate per class.

## Pipeline node order

From `taskforge/e2b_worker.py`:

```
scaffold      (704)   PR → task skeleton via claude -p
    ↓
qgate         (789)   programmatic lint (task_lint.lint_task)        ◄── Change 1, 2a, 3
    ↓
rubric                Gemini ↔ Kimi rubric extraction
    ↓
enrich       (1985)   pass_to_pass enrichment                        ◄── Change 5
    ↓
improve               test enhancement (conditional)
    ↓
validate     (1347)   Docker oracle (nop=0, gold=1)                  ◄── Change 2b, 4
    ↓
lint         (1416)   post-validation rubric review
    ↓
judge        (1479)   LLM quality judge
    ↓
promote to markdown_following/
```

## The 5 changes at a glance

| # | Rubric | Hook | Status | Catches |
|---|---|---|---|---|
| 1 | `reward_is_pure_pytest` | `task_lint.lint_test_sh()` at qgate | **DONE** | Reward written via grep/awk/sed, early exits, `\|\| true`, non-canonical paths |
| 2 | `test_deps_in_dockerfile` | qgate (Phase A) + validate (Phase B) | designed | `subprocess.run(["cargo", …])` when `cargo` not in Dockerfile |
| 3 | `substring_assertions_are_instructed` | `task_lint.lint_test_outputs()` at qgate | designed | `assert "exact literal" in out` when literal isn't in instruction.md |
| 4 | `every_gold_test_passes` | `e2b_worker.node_validate_and_fix` after gold trial | helper **DONE**, wire-up pending | Aggregate `gold=1` masking individual failing tests |
| 5 | auto-insert lint requirement | scaffold post-processing, before qgate | designed | tests run `ruff format --check` but instruction.md never mentioned formatting |

## Change 1: Reward purity (IMPLEMENTED)

`taskforge/task_lint.py:lint_test_sh()` flags five anti-patterns in `test.sh`:

| Anti-pattern | Corpus hits |
|---|---:|
| grep / awk / sed on pytest output | 28 |
| early `exit` before LLM judge block | 142 |
| `\|\| true` silencing critical pytest/plugin installs | 198 |
| reward written to non-canonical path (e.g. `reward.json`) | 21 |
| reward value as JSON object `{reward: 1.0, ...}` | 4 |

**Retrofit**: 303/1125 tasks (27%) fail at least one. Run `python -m taskforge.task_lint --all-tasks`.
**Audit evidence**: `airflow-migration-0097` (grep gate); `airflow-git-hook-security` (early exit + JSON reward); `lotti-due-date-display-readme` (silent pytest-json-ctrf install).

## Change 4: Every gold test must pass (HELPER IMPLEMENTED)

The current oracle uses aggregate `gold` reward. If `test.sh` is weakened (writes `1` regardless, or grep gate misses a failure), gold=1 ships with broken tests inside.

**Evidence**: `ruff-primer-setup-script-claude-md` — test calls script with 1 arg, script requires 2; assertion checks for an error message that never appears. No correct implementation can pass it; oracle approved the task.

Helper `taskforge/task_lint.py:check_all_gold_tests_passed(ctrf_path)` is in. Wire-up stub for `e2b_worker.node_validate_and_fix`:

```python
from taskforge.task_lint import check_all_gold_tests_passed

ctrf = gold_trial_dir / "logs" / "verifier" / "ctrf.json"
gold_test_fails = check_all_gold_tests_passed(ctrf)
if gold_test_fails:
    status["verdict"] = "fail_gold_partial"
    status["gold_test_fails"] = [f.snippet for f in gold_test_fails]
    return  # don't promote
```

## Change 2: Environment-dependency pre-validation

Two phases — fast static check at qgate, authoritative live check at validate.

### Phase A — qgate, deterministic

```python
def lint_test_env_deps(task_dir: Path) -> list[Finding]:
    """Extract subprocess binaries from test_outputs.py; verify Dockerfile mentions each."""
    tests = (task_dir / "tests" / "test_outputs.py").read_text()
    called = set(re.findall(r'subprocess\.run\(\s*\[\s*["\'](\w+)', tests))
    dockerfile = (task_dir / "environment" / "Dockerfile").read_text()
    missing = [b for b in called
               if b not in BENIGN_BUILTINS
               and b not in dockerfile]
    return [Finding(rubric="test_deps_in_dockerfile", tier="A", severity="fail", ...) for b in missing]
```

Allowlist: `python, python3, pip, pip3, bash, sh, git, grep, sed, awk, cat, ls, find, test, true, false, echo, printf`.

Trade-off: fast and deterministic but can false-positive (tool already in base image) and false-negative (apt-installed name doesn't appear textually).

### Phase B — validate, authoritative

```python
for binary in extract_binaries(task_dir):
    if docker_run(image, f"command -v {binary} >/dev/null") != 0:
        status["missing_deps"].append(binary)
```

**Evidence**: `deno-chore-remove-some-top-level`, `uv-self-update-quiet-stderr-important` — both call `cargo` from tests, neither installs Rust. All 3 candidate models produced correct patches; tests errored with `FileNotFoundError: cargo`.

## Change 3: Literal-string assertions must be instructed

Walk `test_outputs.py` AST for `assert "LITERAL" in <expr>`. For each LITERAL > 6 chars that isn't an identifier or path, verify it appears verbatim in `instruction.md`.

**Evidence**: `ClickHouse-pr-102080` asserts the full sentence `"is larger than 5 MB. Large files should not be committed to git"`. Instruction says the warning must contain "is larger than 5 MB" and "download them at test time" — never specifies the period separator. Models used `;` and `,` — all correct, oracle rejected them.

Three remediations per violation:

| Choice | When |
|---|---|
| Relax test → `re.search(r"is larger than 5 MB.*download them")` | Instruction is intentionally underspecified |
| Add the literal to instruction.md | Wording is intended to be exact |
| Split into multiple weaker assertions | Substrings are individually meaningful |

## Change 5: Auto-insert lint requirement in instruction.md

When tests invoke a linter, the instruction must say so.

```python
LINTERS = {'ruff', 'black', 'prettier', 'clippy', 'cargo fmt', 'cargo clippy',
           'eslint', 'stylelint', 'gofmt', 'golangci-lint', 'mypy', 'pyright'}
tests_text = (task_dir / "tests" / "test_outputs.py").read_text()
used = [l for l in LINTERS if l in tests_text]
if used and not any(l in instr.read_text() for l in used):
    instr.write_text(instr.read_text().rstrip() + "\n\n## Lint requirements\n\n"
        f"Your solution must satisfy these linters: {', '.join(used)}.\n"
        "Running the repository's CI lint step should produce zero new errors.\n")
```

**Evidence**: `areal-openai-proxy-empty-session` — tests include `ruff format --check`. Opus and MiniMax wrote semantically correct fixes that failed on formatting. Instruction never mentioned formatting.

## Implementation priority

| Order | Change | Size | Why this order |
|---|---|---|---|
| 1 | Change 1 | done | Already catches 303/1125 |
| 2 | Change 4 wire-up | ~10 lines | Helper done; one call site |
| 3 | Change 2 Phase A | ~40 lines | Extends `lint_task`; deterministic; fast iteration |
| 4 | Change 5 | ~25 lines | Scaffold-time, no infra cost |
| 5 | Change 2 Phase B | depends | Needs `docker run` at validate time |
| 6 | Change 3 | ~60 lines | AST walker + cross-check; most fiddly |

## Combined effect on the 9 broken eval tasks

| Task | Caught by |
|---|---|
| airflow-migration-0097 | 1 (grep gate) |
| airflow-git-hook-security | 1 (early exit + JSON reward) |
| lotti-due-date-display-readme | 1 (silent `\|\| true` on pytest-json-ctrf) |
| deno-chore-remove-some-top-level | 2 (cargo not in Dockerfile) |
| uv-self-update-quiet-stderr-important | 2 (cargo not in Dockerfile) |
| bun-build-make-ccnopch | 2 (bun/tsx missing) + 3 (`r"cxx"` regex) |
| ClickHouse-pr-102080 | 3 (punctuation-sensitive substring) |
| ruff-primer-setup-script-claude-md | 4 (gold fails 1/18 tests) |
| areal-openai-proxy-empty-session | 5 (ruff formatting requirement not stated) |

**All 9 prevented or auto-corrected.**
