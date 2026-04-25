# Quarantined Tasks (2026-04-24)

These tasks were moved out of `harbor_tasks/` because they fail at least one
of the 3 hardest Tier-A quality gates introduced in commits `f1a558f1a`,
`b7ecaf227`, and `535d439d4`. They have **zero RL training signal**.

## Quarantine reasons (3 mutually-non-exclusive)

| Reason | Count | Why no signal |
|---|---|---|
| `contaminated_oracle` | 15 | `solution/solve.sh` fetches the gold patch via `curl github.com/.../*.diff`, `git show <sha>`, `wget`, or `gh pr diff`. An agent with internet access could do the same and trivially pass — the oracle is game-able. |
| `trivial_gold` | 92 | Gold patch adds <4 non-blank lines, OR <15 lines across docs-only files. All models pass these regardless of capability. No differentiation. |
| `grep_only_tests` | 12 | `tests/test_outputs.py` contains zero `subprocess.run` / `check_output` / `Popen` / `os.system` calls. Tests only grep source — they don't verify runtime behavior. |

Total quarantined: **117 unique tasks** (some have multiple reasons).

## Per-task reasons

See `MANIFEST.json` for the full mapping. `INDEX.txt` has a flat list of
task names for easy grepping.

## Reinstating a task

If you fix the issue (e.g., inline a curl'd patch as a heredoc, beef up
a trivial diff, add subprocess.run tests), you can move the task back:

```bash
mv harbor_tasks_quarantine/<task-name> harbor_tasks/
.venv/bin/python -c "from taskforge.task_lint import lint_task; from pathlib import Path; \
  print(lint_task(Path('harbor_tasks/<task-name>')))"
```

If lint_task returns no Tier-A `severity=fail` findings for the 3 gates
above, it's clean to reinstate.

## Source rubrics

These gates live in `taskforge/rubrics.py` and are checked by
`taskforge/task_lint.py`. The relevant rubric names:

- `oracle_no_external_fetch` (Tier A)
- `gold_diff_non_trivial` (Tier A)
- `tests_have_subprocess` (Tier A)
