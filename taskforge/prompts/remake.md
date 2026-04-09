# Remake Task

Remake `harbor_tasks/$ARGUMENTS/` using the v2 format: pytest-based test_outputs.py, binary scoring, eval_manifest.yaml.

## Context

This task already exists but uses the old format (weighted bash test.sh, rubric.yaml). You are remaking it with:
- **pytest test_outputs.py** (binary: all pass = 1, any fail = 0)
- **eval_manifest.yaml** (replaces rubric.yaml, declares checks + rubric rules)
- **Standardized test.sh** (fixed boilerplate, do not customize)

The template is at `taskforge/templates/task_template/`. Copy it, then fill in.

## Steps

### 1. Read existing task files

Read ALL files in `harbor_tasks/$ARGUMENTS/`:
- `instruction.md` — keep the bug description (may need minor edits)
- `task.toml` — keep metadata, extract source PR info if present
- `environment/Dockerfile` — keep as-is (or fix if broken)
- `solution/solve.sh` — keep as-is (gold patch)
- `tests/test.sh` — OLD format, read to understand what's being tested
- `rubric.yaml` — OLD format, extract rules for eval_manifest.yaml

### 2. Read the PR diff

If `task.toml` has `source_repo` and `source_pr`:
```bash
gh pr diff <PR_NUMBER> --repo <REPO>
```

If not, read `solve.sh` to understand the gold patch.

### 3. Read agent config files

The file `harbor_tasks/$ARGUMENTS/agent_configs.md` contains the FULL content of every agent config file (CLAUDE.md, AGENTS.md, SKILL.md, .cursorrules, copilot-instructions.md, README.md, etc.) found in the repo at the task's exact base commit, with line numbers.

**Read this file completely.** It is the authoritative source for all repo-level coding rules.

**Use subagents to process configs in parallel:**
- Launch one subagent to read `agent_configs.md` and extract ALL rules with line numbers, classifying each as programmatic vs soft vs irrelevant
- Launch another subagent to read the PR diff (from step 2) and identify which files/directories are modified — this determines which subdirectory configs apply

**Once both return**, build the rule list:

1. **Programmatic + relevant** → becomes a `check` in test_outputs.py with `origin: agent_config`
   - Examples: "no wildcard imports", "use bun.* APIs not std.*", "no .unwrap()"
   - These get `source: {path, lines, commit}` in eval_manifest.yaml
2. **Soft/subjective + relevant** → goes in `rubric` section of eval_manifest.yaml
   - Examples: "prefer composition over inheritance", "add comments for non-obvious logic"
   - Must be evaluable from a diff by an LLM judge
3. **Irrelevant to this task** → skip (process rules, commit rules, tooling rules, unrelated domains)
4. **Trivially vague** → skip ("follow existing style" without specifics)

Aim for **more rules rather than fewer** — it's better to include a borderline rule than miss a relevant one.

### 4. Create new test_outputs.py

Copy `taskforge/templates/task_template/tests/test_outputs.py` to `harbor_tasks/$ARGUMENTS/tests/test_outputs.py`.

**Convert the old test.sh checks to pytest functions:**
- Each weighted check becomes a `def test_*()` function
- Remove all weight arithmetic, bash boilerplate, add() helpers
- Keep the actual assertion logic (Python code inside bash heredocs → standalone Python)
- Add attribution comments: `# [origin] type`
- Every test must be self-contained (no shared state between tests)

**Design principles:**

1. **CALL code, don't inspect it.** `ast.parse` is a LAST RESORT.
   - If the module can be imported (pure Python, deps installed in Dockerfile) → import and call it
   - If the module has heavy deps (torch, triton) but the target function is pure Python → extract via AST then EXEC it with mocks, and test the executed function behaviorally
   - ONLY use ast.parse for structural checks when code literally cannot execute (GPU kernels, CUDA C++)
   - For every `ast.parse` check, add a comment: `# AST-only because: <reason code can't be called>`

2. **Vary inputs.** Never test with a single hardcoded value — agents will hardcode the expected output.
   - Test at least 3 different inputs per behavioral check
   - Include edge cases (None, empty, negative, boundary values)
   - If testing a computation, verify the formula with diverse inputs, not just one known answer

3. **Fail-to-pass tests must FAIL on the base commit, PASS on a correct fix.**

4. **Anti-stub.** Verify return values and behavior, not just "doesn't crash".
   - `assert result == expected` not `assert result is not None`
   - For exception tests: `pytest.raises(ValueError, match="specific message")`

5. **For non-Python repos:** Use `subprocess.run()` to compile and execute.
   ```python
   # Rust: compile then test binary behavior
   r = subprocess.run(["cargo", "check"], cwd=REPO, capture_output=True, timeout=600)
   assert r.returncode == 0
   
   # Node: execute JS and check output
   r = subprocess.run(["node", "-e", "..."], cwd=REPO, capture_output=True)
   assert "expected" in r.stdout
   ```

### 4. Replace test.sh with standardized boilerplate

Copy `taskforge/templates/task_template/tests/test.sh` to `harbor_tasks/$ARGUMENTS/tests/test.sh`.

This is the fixed pytest runner — do NOT customize it per task.

### 5. Create eval_manifest.yaml

Copy `taskforge/templates/task_template/eval_manifest.yaml` and fill in:
- `source`: repo, pr, base_commit, merge_commit from task.toml or Dockerfile
- `checks`: one entry per `def test_*()` in test_outputs.py
- `rubric`: soft rules from old rubric.yaml (only genuinely subjective ones)

Drop from rubric:
- Trivial/vague rules ("follow existing style")
- Programmatic rules (move to test_outputs.py as agent_config checks)
- Process rules (commit messages, PR format)

### 6. Clean up old files

- Delete `rubric.yaml` (replaced by eval_manifest.yaml)
- Delete `tests/judge.py` (old LLM judge copy)
- Delete `tests/judge_hook.sh` (old hook)
- Keep: instruction.md, task.toml, Dockerfile, solve.sh

### 7. Update instruction.md if needed

- If it's too vague or leaks the fix, rewrite
- If it's fine, leave it alone
- Structure: Problem → Expected Behavior → Files to Look At

### 8. Self-audit

1. **Stub walk**: every test must fail with `def f(): pass`
2. **Alternative fix**: a different valid implementation should pass
3. **F2P coverage**: at least 2 tests must fail on base commit
4. **Manifest sync**: every `def test_*` has a matching check in eval_manifest.yaml

```
Self-audit:
  Tests: N total (X f2p, Y p2p)
  Stub score: 0
  Alternative fix passes: yes
  Anti-patterns: none
  Manifest sync: yes
```
