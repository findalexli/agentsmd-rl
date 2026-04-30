# Scaffold Task

Create a benchmark task from a GitHub PR. Copies `templates/task/` → `markdown_following/<task-name>/`, then fills in placeholders.

## Input

`$ARGUMENTS` = PR URL or `owner/repo#number` (e.g., `sgl-project/sglang#21471`).

## Steps

### 1. Fetch PR metadata

```bash
gh pr view <N> --repo <owner/repo> --json title,body,files,mergeCommit
gh api repos/<owner/repo>/commits/<merge_sha> --jq '.parents[0].sha'   # base commit
gh pr diff <N> --repo <owner/repo>                                      # full diff
```

### 1b. Abandon check

After reading the PR metadata and diff, decide if this PR is suitable for a benchmark task. **Abandon immediately** by writing this file and stopping:

```bash
echo '{"abandoned": true, "reason": "your reason"}' > /workspace/task/status.json
```

Abandon if ANY of these apply:
- **CI-only**: PR only changes `.github/workflows/`, CI configs, with no code or instruction-file changes
- **Too large**: PR touches >10 files or >500 lines of functional code changes
- **Needs secrets/accounts**: Requires API keys, OAuth tokens, cloud accounts, or paid services
- **Needs GPU/special hardware**: CUDA kernels, model weights, TPU, etc. that can't be tested on CPU
- **Repo deleted/archived**: Can't clone or checkout the base commit
- **Trivial rename/typo**: One-line change with no behavioral or instruction-rule difference
- **Reverted PR**: The merge commit was later reverted
- **No testable behavior AND no agent-instruction edit**: e.g. pure CSS/UI layout, *and* the PR doesn't modify any tier-1 instruction file

**EXCEPTION — agent-instruction-file edits are valid even without behavioral tests.**
If the PR's diff includes changes to an agent-instruction file (CLAUDE.md, AGENTS.md, SKILL.md anywhere, .cursorrules, .cursor/rules/*, .github/copilot-instructions.md, .agents/skills/*/SKILL.md, .claude/skills/*/SKILL.md, .opencode/skills/*/SKILL.md, .codex/skills/*/SKILL.md), this is a valid task even if the rest of the PR is docs-only. Set `task.kind = markdown_authoring` (or `code_with_config` if there are bundled code changes) and use the markdown-authoring scaffold rules in step 6 below.

**Lockfile/dependency-only PRs** (only `*.lock` / `pyproject.toml` / `package.json` version bumps with no functional code) → STILL ABANDON. The behavior the rule "regenerate the lockfile" tests doesn't have a stable in-repo verification — the agent's job there is mechanical, not behavioral, and the fix lives upstream in the dependency.

If the PR looks good, continue to step 2.

### 2. Discover and load ALL agent config files

This is critical — our benchmark tests how well agents follow repo instructions.

**Step 2a: Discover all config files at the base commit:**
```bash
gh api "repos/OWNER/REPO/git/trees/BASE_COMMIT?recursive=1" \
  --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md|\\.cursorrules|\\.cursor/rules|copilot-instructions\\.md|\\.windsurfrules|\\.clinerules|\\.continuerules|\\.cody|CONVENTIONS\\.md|README\\.md")) | .path'
```

**Step 2b: Fetch the FULL content of every config file found:**
```bash
gh api "repos/OWNER/REPO/contents/PATH?ref=BASE_COMMIT" --jq '.content' | base64 -d
```

Read completely — do NOT grep for snippets. We need full context to find all rules, not just keyword matches.

**Step 2c: Determine which configs apply:**
- Root-level configs (CLAUDE.md, AGENTS.md, .cursorrules) → always apply
- Subdirectory configs → apply if PR touches files in that subtree
- `.claude/skills/*/SKILL.md` → apply if task matches the skill's domain

**Step 2d: Classify every rule in applicable configs:**
1. **Programmatic + relevant** → pytest check with `origin: agent_config` and `source` ref
2. **Soft/subjective + relevant** → `rubric` section of eval_manifest.yaml
3. **Irrelevant** (process, PR, commit, tooling rules) → skip
4. **Trivially vague** ("follow existing style" without specifics) → skip

Aim for **more rules rather than fewer** — better to include a borderline rule than miss a relevant one.

### 3. Copy template and fill placeholders

**IMPORTANT**: All task files MUST be created under `/workspace/task/`. This is the expected output location.

```bash
mkdir -p /workspace/task/{environment,solution,tests}
```

Create all files from scratch in `/workspace/task/` — there is no template to copy from.

Replace all `{{PLACEHOLDER}}` tokens across files:

| Placeholder | Value |
|-------------|-------|
| `{{OWNER}}` | GitHub org/user |
| `{{REPO}}` | Repository name |
| `{{REPO_SHORT}}` | Short repo name (for paths) |
| `{{BASE_COMMIT}}` | Parent of merge commit |
| `{{MERGE_COMMIT}}` | Merge commit SHA |
| `{{PR_NUMBER}}` | PR number |
| `{{TASK_NAME}}` | Task slug |
| `{{TASK_TITLE}}` | Human-readable title |
| `{{TARGET_FILE}}` | Primary file(s) the PR modifies |
| `{{DISTINCTIVE_LINE}}` | Unique string from the patch (for idempotency) |
| `{{PATCH_CONTENT}}` | Full gold patch diff |
| `{{CONFIG_FILE}}`, `{{LINES}}`, `{{COMMIT}}` | Agent config source refs |

### 4. Fill in the files (this order)

#### 4a. Branch on `task.kind`

Before writing files, decide which kind of task this is. Set `task.kind` in `eval_manifest.yaml.task` and follow the matching scaffold rules:

| `task.kind` | When | Track 1 (test.sh) | Track 2 (config diff) |
|---|---|---|---|
| `code_fix` | PR has functional code changes, no tier-1 markdown changes | **Behavioral fail_to_pass tests** (canonical) | not used |
| `code_with_config` | PR has BOTH functional code AND tier-1 markdown changes | Behavioral tests on the code changes | Gemini compares gold markdown vs agent diff |
| `markdown_authoring` | PR's diff is **only** tier-1 markdown changes (no functional code) | Lightweight structural check — see below | Gemini compares gold markdown vs agent diff (this is the real eval signal) |

**For `markdown_authoring` tasks, write `test.sh` like this:**
- Pick 1-3 unique signal lines from the gold markdown (specific phrases the gold diff added — e.g., `name: <skill-name>` from frontmatter, a distinctive sentence, a heading).
- `test.sh` greps for those lines in `/workspace/<repo>/<tier1_path>` and writes `1` to `/logs/verifier/reward.txt` if all are present, else `0`.
- This gives a clean nop=0 / gold=1 oracle without requiring behavioral tests.
- Populate `eval_manifest.yaml.config_edits` with the gold added/removed markdown chunks for Gemini's Track 2 semantic-diff judgment — that is the actual evaluation signal. Track 1 is a sanity gate.
- `eval_manifest.yaml.checks` can be empty (or one structural pass_to_pass) for `markdown_authoring`.

**For `code_with_config`,** scaffold the behavioral tests as for `code_fix` AND populate `config_edits` with the markdown delta. Both tracks score.

#### Dockerfile — reproducibility rules

- Choose base image with **exact tag** (NEVER `:latest`): `python:3.12-slim` / `node:22-slim` / `rust:1.85-slim`
- **Pin every `pip install`** with `==X.Y.Z` (e.g., `pip install pytest==8.3.4 requests==2.32.3`). Unpinned deps cause reward noise when upstream bumps a minor.
- For non-Python repos, ensure `python3` is available (needed by pytest runner)
- Clone with `--filter=blob:none` (default) or `--depth=N` for large repos
- Install ONLY deps needed by test_outputs.py — no torch, no GPU libs
- **Enumerate every binary test_outputs.py calls via `subprocess.run([...])`
  and verify it is installed in the final image.** Check via `docker run
  task-env command -v <binary>`. Missing tools make tests error with
  `FileNotFoundError` and look like an agent failure. Rubric
  `test_deps_in_dockerfile` auto-rejects scaffolds with missing tools.
  Base-image implicits are fine: `FROM node:*` includes npm/npx/pnpm/yarn;
  `FROM rust:*` includes cargo/clippy/rustfmt; `FROM python:*` includes
  python/pip. Linters (`ruff`, `black`, `mypy`, `isort`, etc.) are NOT
  implicit and must be explicitly `pip install`ed.
- **Do NOT** `COPY solution/` or `COPY tests/` — harness mounts them externally. Including them leaks the answer.
- Always `mkdir -p /logs/verifier`

#### solve.sh
- Paste the gold patch into the HEREDOC (single-quoted `<<'PATCH'`)
- Set idempotency grep to a distinctive line from the patch
- Ensure `cd /workspace/{{REPO_SHORT}}` at the top
- **FORBIDDEN: fetching gold from an external source.** Never use any of
  these in solve.sh:
    - `curl … github.com/…/pull/N.diff` or `…/N.patch`
    - `wget … github.com`
    - `gh pr diff`
    - `git show <sha>` of the merge commit
    - `git fetch … pull/N` + `git cherry-pick`
    - `git apply https://…`
  These make the oracle trivially game-able (an agent with network could do
  the same) and are auto-rejected by `taskforge.task_lint.lint_solve_sh`
  via rubric `oracle_no_external_fetch`.

#### task.toml
- Set `name = "<repo-short>-<descriptive-slug>"` (e.g., `name = "ruff-dedent-formfeed-strip"`)
- Set difficulty, tags, time estimates

#### test_outputs.py — THE CORE WORK

Replace each `raise NotImplementedError(...)` placeholder with real tests. Every `def test_*` function maps 1:1 to a check in eval_manifest.yaml.

**Design principles:**

1. **Call code, don't inspect it.** Import the function, call it with bug-triggering input, assert the result. AST is a last resort (only for GPU kernels, CUDA C++, or code needing unavailable model weights).

2. **Fail-to-pass is primary.** Each f2p test MUST fail on the base commit and pass on a correct fix. Test the *behavior*, not the *structure*.

3. **Vary inputs.** Never test with a single parameter value — agents hardcode constants.

4. **Anti-stub.** Verify return values, not just "doesn't crash". `assert result == expected`, not `assert result is not None`.

5. **Upstream P2P.** If the repo has pytest/jest/vitest tests that run on CPU, include them. Don't invent fake regression tests.

6. **For non-Python repos:** Use `subprocess.run()` to compile/run/test. Python is the universal test harness.

```python
# Rust example
def test_cargo_check():
    r = subprocess.run(["cargo", "check"], cwd=REPO, capture_output=True, timeout=600)
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()}"

# Node example
def test_build():
    r = subprocess.run(["node", "-e", "require('./dist/index.js')"], cwd=REPO, capture_output=True)
    assert r.returncode == 0
```

**10 anti-patterns to avoid:**

| # | Pattern | Fix |
|---|---------|-----|
| 1 | Self-referential constant extraction | Compare against ground-truth values |
| 2 | Import fallback to AST | Import fails = test fails |
| 3 | Grep-only frontend tests | Execute functions, not grep |
| 4 | Stub-passable tests | Assert return values |
| 5 | Superficial guard checks | Assert state CHANGED |
| 6 | Single parameter value | Vary across multiple values |
| 7 | Ungated structural tests | Gate behind behavioral pass |
| 8 | Compilation-ungated structural | Gate behind syntax check |
| 9 | Keyword stuffing | Check coherence |
| 10 | File-exists fallback | No existence checks for points |

#### test.sh — DO NOT MODIFY

The template test.sh is standardized boilerplate. It installs pytest, runs test_outputs.py, and writes binary reward. Do not add task-specific logic here.

**Hard rules enforced by `reward_is_pure_pytest` rubric (auto-rejected):**
- Reward MUST be written to `/logs/verifier/reward.txt` — never `reward.json`,
  `reward.bin`, `/tests/reward`, or any other path. Harbor only reads `.txt`.
- Reward value MUST be the literal string `0` or `1` — never a JSON object
  like `{"reward": 1.0, "status": "success"}`.
- Reward MUST come from pytest's exit code directly: `if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi`.
  Do NOT pipe pytest output to `grep/awk/sed` and decide reward from matched
  strings. Output text can contain "failed" in non-failure contexts; only the
  exit code is trustworthy.
- NO `exit` statement before the LLM-judge block (the `--- LLM Judge ---`
  section). An early exit makes the judge unreachable dead code.
- NO `|| true` on pytest / pytest-plugin installs. If pytest doesn't install,
  the task is broken — surface it by failing loud, not silently.

#### eval_manifest.yaml

**The schema is enforced by Pydantic in `taskforge/models.py` — these field names and enum values are NOT optional.** Use exactly these names, in this shape:

```yaml
version: "2.0"

source:                          # toplevel — NOT under metadata.source_pr
  repo: "{{OWNER}}/{{REPO}}"
  pr: {{PR_NUMBER}}
  base_commit: "{{BASE_COMMIT}}"
  merge_commit: "{{MERGE_COMMIT}}"

task:
  kind: code_fix                 # one of: code_fix | code_with_config | markdown_authoring

checks:
  - id: <slug>
    type: fail_to_pass            # fail_to_pass | pass_to_pass — ONLY these two
    origin: pr_diff               # pr_diff | repo_tests | agent_config | static — ONLY these four
    description: "<one line>"
    source:                       # REQUIRED iff origin == agent_config
      path: "AGENTS.md"           # NOT `file:` — the field is `path`
      lines: "30"                 # numeric line or range like "30-35" — NOT a section name
      commit: "{{BASE_COMMIT}}"

config_edits:                     # REQUIRED for code_with_config & markdown_authoring kinds
  - path: "AGENTS.md"             # NOT `file:`
    tier: 1                       # 1 = agent instruction, 2 = doc
    gold_added: "<lines added>"   # NOT `added:`
    gold_removed: "<lines removed>"  # NOT `removed:`

rubric:
  - rule: "<verbatim text from agent config>"   # NOT `description:` — the field is `rule`
    source:
      path: "AGENTS.md"
      lines: "45"
      commit: "{{BASE_COMMIT}}"
    evidence: "<how gold demonstrates this>"
    category: "naming"            # naming | style | architecture | testing | etc.
    verification: llm_judge       # programmatic | llm_judge | semantic_diff

distractors:                      # negative rubric — collisions to ignore
  - rule: "<verbatim text>"
    source: { path: "...", lines: "...", commit: "..." }
    collision_type: rule_conflict # rule_conflict | scope_ambiguity | meta_confusion | architecture_boundary | would_cause_bug
    why_distracting: "<one line>"
    severity: medium              # high | medium | low
```

**Common drift to AVOID** (we have hundreds of legacy tasks with these mistakes — don't add to the pile):
- ❌ Inventing new `origin:` values (e.g. `task_specific`, `pr_behavior`, `gold_diff`). The four canonical values are exhaustive — pick the closest match. Behavioral PR tests are `pr_diff`. Pre-existing repo tests are `repo_tests`. Anti-stub / syntax gates are `static`.
- ❌ Using `file:` instead of `path:` (anywhere — checks, rubric, config_edits)
- ❌ Using `description:` for rubric items instead of `rule:`
- ❌ Putting `lines:` as a section name like `"Intent Layer Maintenance"` — it must be a line number or range.
- ❌ Putting source PR metadata under `metadata.source_pr` instead of toplevel `source`.
- ❌ Leaving `rubric: []` when applicable agent-config files exist with relevant rules.
- ❌ Omitting `distractors:` — every code_with_config task should ship at least 1-2 distractor rules.

The agent that runs YOU does not see CLAUDE.md, only this prompt. The Pydantic model in `taskforge/models.py` is the single source of truth — what's written above mirrors it exactly.

**Other manifest authoring rules:**
- Fill in source PR metadata (the toplevel `source:` block) from the PR fetch in Step 1.
- One `check:` entry per `def test_*` function in test_outputs.py (keep ids in sync).
- Add `source:` refs for ALL `agent_config` checks (Pydantic enforces this).
- Every soft/subjective rule from CLAUDE.md, AGENTS.md, SKILL.md etc. that is relevant to this PR's changes MUST become a rubric entry with source ref. If the repo has agent configs, the rubric section MUST NOT be empty — extract at least 2-3 rules. Only leave `rubric: []` if the repo has NO agent config files at all.

#### instruction.md — WRITE THIS LAST

By now you know exactly what test_outputs.py checks. The instruction MUST describe the *symptom* those tests capture — with enough specificity that every asserted detail is recoverable, **without** revealing the fix.

**The two failure modes we must avoid:**

1. **Spec-test coupling** (76% of our prior batch failed this): tests assert on an exact literal `"4acc9acc76d5079…"` but the instruction only says "install rustup with SHA256 verification." The agent cannot discover the SHA. → *FAIL.*

   Rule: **every specific value `test_outputs.py` asserts on — file paths, function names, SHAs, schema keys, literal strings, HTTP status codes, error messages — must be named in the instruction OR cited to an authoritative URL the agent can fetch.** Walk down your test file line by line. For each `assert X == Y` / `assert Y in result`, confirm `Y` is findable from instruction.md.

2. **Solution leakage**: the instruction tells the agent *what to change* ("change line 42 to return None", "add `except KeyError`"). The agent copy-pastes and passes. → *FAIL.*

   Rule: describe **what is broken** (symptom, observable behavior, expected contract) without naming the fix. "Parsing `foo.toml` with an empty `[section]` raises `KeyError: 'name'`; it should return an empty dict." — good.  "Change `d[name]` to `d.get(name, {})` in parser.py:42." — leakage.

**Checklist before finishing:**
- [ ] Every literal/SHA/path/name your tests assert on is in the instruction OR cited to a URL
- [ ] **Every multi-word literal tests assert on MUST appear verbatim in
      instruction.md.** Example failure: test asserts `"is larger than 5 MB.
      Large files should not be committed to git"` (exact sentence with
      period) but instruction only says "warning must mention size limit
      and remediation" — Opus writes `"…5 MB; download…"` and fails.
      Rubric `substring_assertions_are_instructed` flags this.
- [ ] The *fix* is not named (no `change X to Y`, no `replace foo() with bar()`, no file:line reference to the broken line unless localization is genuinely part of the task)
- [ ] **Do not cite the exact paths of gold-diff code files** unless
      localization is genuinely impossible otherwise. Describing symptoms
      by input/output is preferable. Naming paths makes localization
      trivial and reduces the task's difficulty signal. Rubric
      `instruction_no_path_leak` tracks this (as a warning).
- [ ] **If tests invoke linters/formatters (ruff, black, prettier, eslint,
      clippy, cargo fmt, gofmt, mypy, etc.), add a `## Code Style
      Requirements` section to instruction.md listing them.** Otherwise
      agents write semantically-correct fixes that fail on style. Rubric
      `lint_requirement_stated` auto-flags this; `scripts/fix_lint_requirement.py`
      can auto-append the section.
- [ ] Structured outputs (JSON/CSV): exact schema keys/types documented
- [ ] No PR-body boilerplate, no "this PR fixes…" phrasing
- [ ] HTML comment guidelines from the template deleted

### 5. Build Docker and discover repo CI/CD

**5a. Build the Docker image first:**
```bash
cd /workspace/task/environment && docker build -t task-env .
```
If it fails, fix the Dockerfile and retry until it builds.

**5b. Discover CI/CD commands.** From the Dockerfile WORKDIR, check:
- `package.json` → `scripts.test`, `scripts.lint`, `scripts.check`, `scripts.typecheck`, `scripts.build`
- `Makefile` / `Justfile` → test/lint/check targets
- `Cargo.toml` → `cargo test`, `cargo check`, `cargo clippy`
- `pyproject.toml` → pytest, ruff, mypy
- `go.mod` → `go test`, `go vet`
- `.github/workflows/*.yml` → actual CI commands

**5c. Test which commands work** inside the Docker container on the base commit:
```bash
docker run --rm task-env <command>
```
Only add commands that actually succeed on the base commit. Skip commands that require network access, GPU, or special accounts. When writing test timeouts, use what you observe — if a command takes 30s, set timeout=60; if it takes 200s, set timeout=600. Check `.github/workflows/` for the repo's own CI timeout settings as a reference.

**5d. Add p2p tests** to test_outputs.py for each working CI command:
```python
def test_repo_lint():
    """Repo's linter passes (pass_to_pass)."""
    r = subprocess.run(["npm", "run", "lint"], capture_output=True, text=True, timeout=600, cwd=REPO)
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"
```

**5e. Add matching checks** in eval_manifest.yaml:
```yaml
  - id: test_repo_lint
    type: pass_to_pass
    origin: repo_tests
    description: Repo's linter passes
```

### 6. Docker validation (REQUIRED)

The image is already built from step 5a. Now validate:

**6b. NOP test (base commit — expect reward=0):**
```bash
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env bash /tests/test.sh
cat /logs/verifier/reward.txt
```
Must be `0`. If `1`, your f2p tests are too weak — they pass even without the fix. Rewrite them.

**6c. Gold test (apply fix — expect reward=1):**
```bash
docker rm -f task-solved 2>/dev/null || true
docker run --name task-solved -v /workspace/task/solution:/solution:ro task-env bash /solution/solve.sh
docker commit task-solved task-env-gold
docker rm task-solved
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env-gold bash /tests/test.sh
cat /logs/verifier/reward.txt
```
Must be `1`. If `0`, read the pytest output (`-v --tb=short`), fix solve.sh or tests, rebuild and retry.

**Keep iterating until NOP=0 and GOLD=1.** Do not finish without passing both.

### 7. Self-audit

After Docker validation passes, verify **every** item below. If any fails, fix and re-validate.

**Tier A — reward-integrity (these are BLOCKING):**
- [ ] **behavior_in_task_description**: every literal/SHA/path/name asserted in tests is in instruction.md or cited to a URL
- [ ] **no_solution_leakage**: instruction describes the symptom, not the fix; no file:line of the bug, no patch snippet
- [ ] **solution_uniqueness_guard**: tests would pass on 3 different correct fixes (not only on gold's exact variable names / helper functions / line layout)
- [ ] **tests_verify_behavior_not_text**: every test calls code, runs subprocess, or compiles — no pure `grep 'literal'` tests
- [ ] **test_not_tautological**: no f2p passes on `return None` / empty function / stub
- [ ] **pass_to_pass_coverage**: ≥1 p2p from repo CI/CD
- [ ] **no_hidden_solution_artifacts**: `COPY solution/` and `COPY tests/` NOT in Dockerfile; `.dockerignore` covers them (Harbor's runtime already hides solution/ at agent-run time — this check guards against it being baked into the image)
- [ ] **oracle_no_external_fetch** (new 2026-04-24): solve.sh does NOT curl/wget/git-show/gh-pr-diff the gold patch. Patch is inlined as a HEREDOC.
- [ ] **tests_have_subprocess** (new 2026-04-24): `tests/test_outputs.py` contains at least one `subprocess.run(...)` / `check_output(...)` / `Popen(...)` call that executes real code.
- [ ] **gold_diff_non_trivial** (new 2026-04-24): gold patch is not a 1–3 line no-op (e.g., method rename with no semantic change) or a pure docs/CHANGELOG edit.
- [ ] **reward_is_pure_pytest** (new 2026-04-24): test.sh writes reward from `$?` of pytest to `/logs/verifier/reward.txt` as literal `0`/`1`; no grep gates, no early exit, no silent `|| true` on pytest install.
- [ ] **test_deps_in_dockerfile** (new 2026-04-24): every binary tests invoke via subprocess is installed in the Dockerfile (base-image implicits accepted).
- [ ] **every_gold_test_passes** (new 2026-04-24): on the gold run, EVERY individual pytest test passes (not just aggregate reward=1). Read `/logs/verifier/ctrf.json` and verify no `"status": "failed"` entries.

**Tier B — important:**
- [ ] **dockerfile_determinism**: base image has a version tag (NEVER `:latest`); no `curl | bash` of moving target
- [ ] **no_network_during_tests**: test.sh has no `pip install`, `apt-get install`, `npm install`, or `curl` at test time
- [ ] **pinned_dependencies**: every `pip install` has `==X.Y.Z`
- [ ] **f2p_p2p_classification_correct**: all f2p actually fail at base, all p2p actually pass at base
- [ ] **lint_requirement_stated** (new 2026-04-24): if tests invoke linters/formatters, instruction.md has a "## Code Style Requirements" section naming them.
- [ ] **instruction_no_path_leak** (new 2026-04-24, warn-only): instruction avoids citing exact gold-diff file paths when localization should be part of the task's difficulty.

**Anti-pattern scan** (from §4 above): none of the 10 anti-patterns present.

**Manifest sync**: every `def test_*` has a matching check id in eval_manifest.yaml.

```
Self-audit:
  Docker: NOP=0, GOLD=1
  Tests: N total (X f2p, Y p2p)
  CI/CD tests: [list commands added]
  Tier A checklist: all pass
  Tier B checklist: all pass
  Anti-patterns: none
  Manifest sync: yes
```

### 8. Write final verdict

Before writing the verdict, do these final mechanical checks:

1. **eval_manifest.yaml MUST exist**. If you skipped it, go back and write it now — the task is worthless without a manifest.
   ```bash
   test -f /workspace/task/eval_manifest.yaml || echo "MISSING — write it now"
   ```

2. **eval_manifest schema must validate** against the canonical Pydantic model. Run:
   ```bash
   cd /workspace && python3 -c "
   import yaml
   from taskforge.models import EvalManifest
   data = yaml.safe_load(open('/workspace/task/eval_manifest.yaml').read())
   EvalManifest.model_validate(data)
   print('SCHEMA OK')
   "
   ```
   If that errors, **read the error carefully and fix the manifest** — the most common drifts are listed in section 4 (eval_manifest.yaml). Re-run until it prints `SCHEMA OK`. Do NOT proceed to write `scaffolded: true` until the schema passes — the pipeline will reject your work otherwise.

3. **task.toml** is required (not just instruction.md + tests). Verify it exists.
   ```bash
   test -f /workspace/task/task.toml || echo "MISSING task.toml"
   ```
2. **No scratch files in tests/**. The only files allowed in
   `/workspace/task/tests/` are `test.sh`, `test_outputs.py`,
   `eval_manifest.yaml`, `standalone_judge.py`. Any debug `test_*.py` or
   `*.txt` you wrote during exploration must be deleted.

After Docker validation passes AND the self-audit clears, write your verdict
to `/workspace/task/scaffold_status.json`. The runtime trusts this file —
without it, your work is discarded.

On success:
```json
{"scaffolded": true, "nop_reward": 0, "gold_reward": 1}
```

If you tried hard but cannot make the oracle work (e.g., the PR's behavior
genuinely can't be tested on CPU, or the base commit's build is broken in
ways you can't fix without modifying upstream code), write:
```json
{"abandoned": true, "reason": "<one-sentence cause>"}
```

Do not invent success. Only write `"scaffolded": true` if you actually saw
NOP=0 AND GOLD=1 from the Docker runs in step 6. Bogus verdicts pollute the
benchmark and are worse than abandoning.
