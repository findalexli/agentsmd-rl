# Pipeline v2: Cost-Optimized Task Generation

## Current State (v1 results)

432 tasks scaffolded across 14 repos. 326 audited (all rewrote), 67 validated, 305 pending validation.

| Phase    | Tasks | Avg $/task | Total   | Avg cache read | Avg output    | Cache hit |
|----------|-------|------------|---------|----------------|---------------|-----------|
| Scaffold | 406   | $0.87      | $353    | 601K tokens    | 12,878 tokens | 95.1%     |
| Audit    | 326   | $0.68      | $222    | 234K tokens    | 14,783 tokens | 89.4%     |
| Validate | 39    | $0.39      | $15     | 311K tokens    | 4,229 tokens  | 92.6%     |
| **Total**|       | **$1.94**  | **$590**|                |               |           |

**Problems found:**
- 27% of scaffold output is mechanical (solve.sh, Dockerfile, task.toml) — wasted LLM tokens
- 65-70% of test.sh is scoring boilerplate — only 30-35% is unique test logic
- Audit rewrote ALL 326 tasks — not rubber-stamping, found real exploits (stub score dropped 50-80%)
- Validate timed out 89% at 120 parallel (Docker builds); 13% at 30 parallel
- No pre-filtering — bad PRs get the full $0.87 scaffold treatment

---

## v2 Pipeline: Phase-by-Phase

```
Scout ──→ Heuristic Pre-filter ──→ Pre-gen + Context Bundle ──→ LLM Scaffold ──→ E2B Validate
(gh CLI)   (Python, $0)             (Python+gh, $0)              (OpenRouter)     (E2B sandbox)
~600 PRs   ~420 survive             420 task dirs                 instruction.md   oracle test
                                    + _context.json               test.sh          base≠gold
                                    + mechanical files            rubric.yaml      leakage check
```

**Target: $0.21–0.29/task ($105–145 for 500 tasks) vs v1's $1.94/task ($970)**

---

### Phase 0: Scout (`scripts/scout_prs.py` — EXISTS, works)

No changes needed. 420 PRs already scouted across 14 repos.

**To scale to 2000+ candidates** (needed for 97%+ attrition — see Lessons below):
- Add more repos to `REPOS` list in `scout_prs.py`
- Tighten filters to match R2E-Gym thresholds: max 5 files (not 8), max 200 lines (not 500)

---

### Phase 1: Heuristic Pre-filter (`scripts/prefilter_prs.py` — TO BUILD)

**What it does:** Python-only filtering on scouted PRs. No LLM, no API calls. $0/task.

**Filters to implement (from R2E-Gym's filter chain):**

```python
# Source: .repos/R2E-Gym/src/r2egym/repo_analysis/commit_data_heuristics.py

def is_good_candidate(pr_data: dict) -> bool:
    # 1. Size filter (from R2E-Gym: is_small_commit)
    if pr_data["changed_files"] > 5: return False        # R2E-Gym: max_num_non_test_files=5
    if pr_data["additions"] + pr_data["deletions"] > 200: return False  # R2E-Gym: max_num_non_test_edited_lines=200
    if len(pr_data.get("diff", "")) > 10_000: return False  # R2E-Gym: max_patch_length=10000

    # 2. Not docs/deps only (already in scout, but double-check)
    code_files = [f for f in pr_data["file_paths"]
                  if not f.endswith((".md",".rst",".txt",".yml",".yaml",".json",".toml"))
                  and not f.startswith(("docs/","doc/",".github/"))]
    if not code_files: return False

    # 3. Patch splitting — must have code changes (not just tests)
    # Reuse SWE-bench's extract_patches pattern:
    #   .repos/SWE-bench/swebench/collect/utils.py → extract_patches()
    code_patch, test_patch = split_patch(pr_data["diff"])
    if not code_patch.strip(): return False  # test-only PR

    # 4. Quality heuristics from SWE-bench make_lite:
    #   .repos/SWE-bench/swebench/collect/make_lite/criteria.py
    if contains_git_commit_hash(pr_data["title"]): return False

    return True

def split_patch(diff_text: str) -> tuple[str, str]:
    """Split diff into code vs test hunks. From SWE-bench extract_patches()."""
    from unidiff import PatchSet
    code, test = [], []
    for patched_file in PatchSet(diff_text):
        if any(w in patched_file.path for w in ["test", "tests", "e2e", "testing"]):
            test.append(str(patched_file))
        else:
            code.append(str(patched_file))
    return "\n".join(code), "\n".join(test)
```

**Optional advanced filter (from R2E-Gym, Python repos only):**

```python
# Source: .repos/R2E-Gym/src/r2egym/commit_models/entity_utils.py
# Technique: line-to-entity mapping
# Build entities_by_line: dict[int, set[Entity]] for fast lookup
# of which functions/classes a diff hunk touches.
# Then check: has_testmatch_edit() — do test files reference modified entity names?

# Worth implementing for Python repos. Skip for JS/Rust repos.
```

**Dependencies:** `unidiff` (pip install)

**Expected outcome:** ~30% rejection → 420 → ~294 candidates survive.

---

### Phase 2: Pre-generate Mechanical Files (`scripts/pregen_task.py` — TO BUILD)

**What it does:** For each surviving PR, fetch all data via `gh` CLI and generate deterministic files. No LLM needed. $0/task.

**Steps per PR:**

```python
# 1. Fetch full PR diff
diff = gh("pr diff {pr_num} --repo {repo}")

# 2. Get base commit (parent of merge commit)
base_commit = gh(f"api repos/{repo}/commits/{merge_sha} --jq '.parents[0].sha'")

# 3. Fetch agent config files at base commit
#    (CLAUDE.md, AGENTS.md, .cursorrules, copilot-instructions.md)
tree = gh(f"api repos/{repo}/git/trees/{base_commit}?recursive=1")
config_files = [f for f in tree if matches_agent_config_pattern(f["path"])]
for cf in config_files:
    content = gh(f"api repos/{repo}/contents/{cf['path']}?ref={base_commit}")
    # base64 decode

# 4. Split patch into code (for solve.sh) vs test (for reference)
code_patch, test_patch = split_patch(diff)

# 5. Generate task directory
task_name = f"{repo_short}-{slug}"
```

**Deterministic files generated (templates, no LLM):**

| File | Template source | Variables |
|------|----------------|-----------|
| `solve.sh` | Heredoc wrapper + `git apply` | `code_patch` |
| `Dockerfile` | Jinja2 from SWE-rebench-V2 pattern | `repo_url`, `base_commit`, `language` |
| `task.toml` | Static template | `tags`, `source_repo`, `source_pr` |
| `judge.py` | Static copy from `agentsmd_rl/judge.py` | None |
| `judge_hook.sh` | Static copy | None |

**Dockerfile template — sanitized snapshot (default):**

```dockerfile
# Default: snapshot mode — fetch tree at BASE_COMMIT, strip .git, reinit clean.
# Rationale: Epoch AI (July 2025) showed Django .git = 291MB/330MB (88%).
# Eliminates history leakage by construction (no git log/blame of future commits).
# Preserves git status/diff/add/commit — the only git ops agents actually use.

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
 && rm -rf /var/lib/apt/lists/*

# Fetch ONLY the tree at this commit (--depth=1), then sanitize
RUN git init /workspace \
 && cd /workspace \
 && git remote add origin https://github.com/{repo}.git \
 && git fetch --depth=1 origin {base_commit} \
 && git checkout FETCH_HEAD -- . \
 && rm -rf .git \
 && git init && git add -A && git commit -m "snapshot"

WORKDIR /workspace
```

**Context bundle for LLM phase:**

```python
# _context.json — everything the LLM needs, no gh calls required
{
    "repo": "owner/repo",
    "pr_number": 123,
    "pr_title": "...",
    "pr_body": "...",
    "diff": "...",           # full unified diff
    "code_patch": "...",     # non-test hunks only
    "test_patch": "...",     # test hunks only
    "base_commit": "abc123",
    "agent_configs": {       # verbatim content of each config file
        "CLAUDE.md": "...",
        "extensions/AGENTS.md": "..."
    },
    "changed_files": ["path/to/file.py", ...],
    "repo_language": "python",
}
```

**Dependencies:** `gh` CLI, `unidiff`, `jinja2`

---

### Phase 3: LLM Scaffold — Creative Files Only (`scripts/llm_scaffold.py` — TO BUILD)

**What it does:** LLM generates ONLY the 3 creative files. Reads `_context.json`, writes `instruction.md`, `test.sh`, `rubric.yaml`. Single API call per task.

**Why OpenRouter instead of `claude -p`:**
- `claude -p` has overhead: process spawn, CLAUDE.md loading, tool initialization, 601K cached token reads
- OpenRouter API call is a single HTTP request with the full context bundled in
- Can swap models (Kimi K2.5 @ $0.15/task vs Opus @ $0.87/task)
- No `--dangerously-skip-permissions` needed
- Simpler parallelism (async HTTP vs subprocess management)

**Prompt structure:**

```python
# Three output sections, each with clear instructions
# Total prompt ~5K tokens (vs v1's 601K cached context)

SCAFFOLD_PROMPT = """
You are generating 3 files for a SWE benchmark task.

## Context
Repository: {repo}
PR #{pr_number}: {pr_title}
{pr_body}

## Diff (the gold fix — DO NOT leak this in instruction.md)
{diff}

## Agent Config Files (for rubric.yaml)
{agent_configs}

## Output 1: instruction.md
{instruction_rules}
Communication style: {random_template}  # from Saving SWE-Bench's 11 templates

## Output 2: test.sh
{test_rules}  # condensed from audit-tests.md

## Output 3: rubric.yaml
{rubric_rules}

Return as JSON: {"instruction_md": "...", "test_sh": "...", "rubric_yaml": "..."}
"""
```

**Instruction style variation** (from Saving SWE-Bench):

```python
# Source: "Saving SWE-Bench" (Microsoft, 2025) — 11 developer communication templates
# Real user queries are 10-30 words. GitHub issues are >100 words.
# Performance drops 23-37% with realistic phrasing.

TEMPLATES = [
    "paste_error",           # Stack trace only, no explanation
    "fix_this",              # "Fix the error in X"
    "expected_vs_actual",    # Detailed bug report with repro steps
    "specific_function_fix", # "The function X in file Y has a bug..."
    "test_failure",          # CI output paste
    "minimal_request",       # "X doesn't work correctly"
]
# Randomly sample per task. Detailed variant used for validation.
```

**Built-in self-checks (run after LLM response, no separate audit):**

```python
def self_check(instruction_md, test_sh, rubric_yaml, context):
    errors = []

    # 1. Leakage detection (from SWE-bench+: 32.67% of tasks leaked)
    #    Check if any identifier unique to the diff appears in instruction
    diff_identifiers = extract_new_identifiers(context["diff"])
    base_identifiers = extract_identifiers_at_base(context)  # from context
    leaked = diff_identifiers - base_identifiers
    for ident in leaked:
        if ident in instruction_md:
            errors.append(f"LEAK: '{ident}' appears in instruction but only in diff")

    # 2. Weight sum
    weights = re.findall(r'\((\d+\.\d+)\)', test_sh)
    total = sum(float(w) for w in weights)
    if abs(total - 1.0) > 0.01:
        errors.append(f"Weights sum to {total}, not 1.0")

    # 3. Rubric source paths exist in agent_configs
    for rule in parse_rubric(rubric_yaml):
        if rule["from"] and rule["from"].split(":")[0] not in context["agent_configs"]:
            errors.append(f"Rubric cites {rule['from']} but file not in configs")

    return errors  # If any, regenerate
```

**Model options:**

| Model | $/task (est.) | Quality risk | Notes |
|-------|---------------|-------------|-------|
| Kimi K2.5 (OpenRouter) | ~$0.15 | Medium — may need audit phase | 3.4x cheaper than Opus |
| Opus 4.6 (Anthropic) | ~$0.45 | Low — v1 proved quality | Higher cost but skip audit |
| Hybrid: Opus for test.sh, Kimi for rest | ~$0.25 | Low | test.sh is highest-stakes |

**Decision: Start with Kimi, A/B test 20 tasks against Opus, measure stub scores.**

---

### Phase 4: Validate on E2B (`scripts/validate_e2b.py` — TO BUILD)

**What it does:** Oracle test in E2B sandbox. Replaces v1's Docker-based validate that timed out 89%.

**Why E2B:**
- No local disk/timeout bottleneck (v1's #1 problem)
- Pre-built templates per repo (build once, reuse for all tasks in that repo)
- Parallel sandbox execution at scale
- ~$0.05/task compute vs $0.39/task for v1's LLM-based validate

**E2B template strategy (one per repo, not per task):**

```python
# Source pattern: .repos/SWE-smith/swesmith/profiles/base.py → Registry
# Source pattern: .repos/SWE-rebench-V2/combine.Dockerfile.j2 → base+instance layering

# We already have: scripts/prebuild_e2b_templates.py + scripts/e2b_sandbox.py

REPO_TEMPLATES = {
    "sgl-project/sglang":     {"base": "python:3.12-slim", "deps": ["pytest"]},
    "gradio-app/gradio":      {"base": "node:22-slim",     "deps": ["python3", "pnpm", "pytest"]},
    "astral-sh/ruff":         {"base": "rust:1.77-slim",   "deps": ["python3", "pytest"]},
    "oven-sh/bun":            {"base": "ubuntu:22.04",     "deps": ["bun", "node", "python3"]},
    "huggingface/transformers":{"base": "python:3.12-slim", "deps": ["pytest"]},
    # ... 14 repos total
}

# Per task: git checkout BASE_COMMIT inside the template (~seconds, not minutes)
```

**Oracle test (2-step):**

```python
async def oracle_test(task_dir: Path, sandbox) -> dict:
    # Step 1: Run test.sh on buggy code (base commit)
    base_result = await sandbox.run("bash /tests/test.sh")
    base_score = parse_reward(base_result)

    # Step 2: Apply gold patch, run test.sh again
    await sandbox.run("bash /solution/solve.sh")
    gold_result = await sandbox.run("bash /tests/test.sh")
    gold_score = parse_reward(gold_result)

    # Verdict
    if base_score == gold_score:
        return {"verdict": "REJECT", "reason": "CRITICAL: tests don't distinguish buggy from fixed"}
    if gold_score < 0.95:
        return {"verdict": "NEEDS_FIX", "reason": f"Gold patch scores {gold_score}, expected ~1.0"}
    if base_score > 0.50:
        return {"verdict": "NEEDS_FIX", "reason": f"Base scores {base_score}, tests too lenient"}

    return {"verdict": "PASS", "base_score": base_score, "gold_score": gold_score}
```

**Container timeout pattern (from OpenSWE):**

```python
# Source: .repos/OpenSWE/app/agents/test_analysis_agent/docker_utils.py
# exec_run_with_timeout() uses threading to implement timeouts
# cleanup_container() does graceful stop → force kill → removal
# copy_to_container() uses tar-based file transfer (works without mounts)

# For E2B we don't need this directly (E2B handles timeouts),
# but the pattern is useful if we fall back to local Docker.
```

**Log parsing (from SWE-rebench-V2):**

```python
# Source: .repos/SWE-rebench-V2/lib/agent/log_parsers.py
# 60+ parsers, zero external deps, all return dict[str, TestStatus]
# Router: MAP_REPO_TO_PARSER[repo_name] → parse function
# Can copy verbatim for multi-language validate.

# We probably don't need this for v2 (our test.sh writes reward.txt directly),
# but useful if we add upstream test suite regression checks.
```

---

## Lessons from Prior Work (Pitfalls to Avoid)

### From SWE-bench (princeton-nlp, ICLR 2024)

| Pitfall | Numbers | Our mitigation |
|---------|---------|----------------|
| **Attrition is brutal** | 90K PRs → 2,294 tasks (97.5% drop) | Scout 2000+ PRs to land 500 validated |
| **Solution leakage** | 32.67% of tasks leaked fix in description | Automated leakage detection in self-check |
| **Narrow tests** | 35.5% of SWE-bench Verified (OpenAI audit) | audit-tests.md anti-narrow checks, alt-fix scoring ≥0.70 |
| **Dependency rot** | "Conda crisis" — unpinned deps broke envs | Pin exact versions from requirements at base commit |
| **Repo concentration** | Django = 37.1% of SWE-bench | 14 repos, max 12% per repo (gradio) |
| **Contamination** | Resolution 12.47% → 0.55% on post-cutoff | Agent-config dimension is novel; rotate tasks |

### From SWE-Gym (Berkeley, ICML 2025)

| Pitfall | Numbers | Our mitigation |
|---------|---------|----------------|
| **Manual env setup** | 200 human hours + 6 TB images for 2,438 tasks | E2B templates per repo (not per task) |
| **Easy-task bias** | Overtrained on easy patterns | Cap 2-3 trajectories per task |
| **On-policy hurts** | Qwen dropped 15.3% → 8.7% on self-trajectories | Mix off-policy + on-policy data |
| **No reward hacking defense** | Neither SWE-Gym nor SWE-Next addresses this | Our anti-stub + rubric graders fill the gap |

### From SWE-Next (Waterloo, March 2026)

| Pitfall | Numbers | Our mitigation |
|---------|---------|----------------|
| **Most PRs don't flip tests** | 74.5% show zero test behavior change | Execution pre-filter before LLM spend |
| **Leaky prompting** | Giving F2P test lists helps agents cheat | instruction.md hides fix AND test file |
| **Per-task Docker builds** | 30.8 TB → 639 GB with quarter-profiles | One E2B template per repo, `git checkout` at runtime |
| **Lazy agent submissions** | Agents submit without running tests | Submission gate: must run ≥1 test first |

### From Saving SWE-Bench (Microsoft, 2025)

| Pitfall | Numbers | Our mitigation |
|---------|---------|----------------|
| **Overly-detailed instructions** | Real queries: 10-30 words; issues: >100 | Vary instruction specificity via 11 templates |
| **Single instruction style** | 23-37% perf drop with realistic phrasing | Generate 2-3 variants per task for training |

---

## Reusable Components (Verified in Code)

### Tier 1: Copy/Adapt Directly

| Component | Source | What | Effort |
|-----------|--------|------|--------|
| `extract_patches()` | `.repos/SWE-bench/swebench/collect/utils.py` | Split diff into code vs test via `unidiff.PatchSet` | Copy as-is |
| Lite criteria filters | `.repos/SWE-bench/swebench/collect/make_lite/criteria.py` | Pure functions: `leq_n_files()`, `leq_n_hunks()`, `contains_hyperlinks()` | Copy as-is |
| `CommentAndDocstringRemover` | `.repos/R2E-Gym/src/r2egym/commit_models/entity_utils.py` | AST transformer to strip docs, detect real vs cosmetic changes | Copy, Python-only |
| Entity extraction | `.repos/R2E-Gym/src/r2egym/commit_models/entity_utils.py` | `build_code_structure()` → `entities_by_line` mapping | Copy, Python-only |
| Filter thresholds | `.repos/R2E-Gym/src/r2egym/repo_analysis/commit_data_heuristics.py` | `is_small_commit()`, `bugedit_type_commit()`, `has_testmatch_edit()` | Adapt thresholds |
| Profile registry | `.repos/SWE-smith/swesmith/profiles/base.py` | `Registry` singleton: repo → config class | Model E2B templates on this |
| F2P/P2P grading | `.repos/SWE-smith/swesmith/harness/grading.py` | `get_valid_report()`, `get_eval_tests_report()` | Adapt for reward.txt |
| 36 base Dockerfiles | `.repos/SWE-rebench-V2/base_dockerfiles/` | Python 3.7-3.11, Node 16/18/20, Go, Rust, Java, Ruby | Reference for E2B templates |
| Jinja2 Dockerfile | `.repos/SWE-rebench-V2/combine.Dockerfile.j2` | `FROM base AS instance` + git clone + install | Adapt for pregen |
| PR description prompt | `.repos/SWE-rebench-V2/prompts/annotations/pr_description.j2` | Non-leaky problem description from diff | Adapt for instruction.md |
| 60+ log parsers | `.repos/SWE-rebench-V2/lib/agent/log_parsers.py` | `parse_log_pytest`, `parse_log_jest`, etc. → `dict[str, TestStatus]` | Copy if needed |

### Tier 2: Pattern Reference

| Pattern | Source | What | Use case |
|---------|--------|------|----------|
| Rate limiting | `.repos/SWE-bench/swebench/collect/utils.py` → `Repo.call_api()` | 5-min backoff on 403, multi-token parallelism | scout/pregen scripts |
| Resume/dedup | `.repos/SWE-bench/swebench/collect/build_dataset.py` | Track seen IDs, append mode, skip processed | All batch scripts |
| Container timeout | `.repos/OpenSWE/app/agents/test_analysis_agent/docker_utils.py` | `exec_run_with_timeout()` via threading | Fallback to local Docker |
| File-based queue | `.repos/OpenSWE/scripts/parallel/master.py` + `worker.py` | Master distributes task files, workers poll | Scale beyond E2B if needed |
| JSON extraction | `.repos/OpenSWE/app/agents/test_analysis_agent/test_analysis_utils.py` | Extract JSON from LLM response with retries | llm_scaffold.py response parsing |
| Iterative refinement | `.repos/OpenSWE/app/agents/agents_manager.py` | Generate → test → analyze failure → modify → retry | Hard validation cases |
| Mirror collect | `.repos/SWE-smith/swesmith/bug_gen/mirror/collect/` | PR collection without issue-linking requirement | Matches our use case |

### Tier 3: Not Using

| Component | Source | Why skip |
|-----------|--------|----------|
| `ghapi` library | SWE-bench | We use `gh` CLI, works fine, no need to switch |
| Multi-agent orchestration | OpenSWE | 4-agent pipeline is overkill for our needs |
| Selenium PyPI scraper | SWE-bench `get_top_pypi.py` | We manually curate repos |
| Django-specific parsing | SWE-bench `utils.py` | Not in our repo list |

---

## Implementation Plan

### Build order (dependency-driven)

```
Week 1: scripts/prefilter_prs.py + scripts/pregen_task.py
         ├── prefilter needs: unidiff, SWE-bench criteria functions
         └── pregen needs: gh CLI, jinja2, patch splitting

Week 2: scripts/llm_scaffold.py + A/B test (20 tasks Kimi vs Opus)
         ├── needs: OpenRouter API, prompt engineering
         └── A/B test measures: stub score, alt-fix score, behavioral %

Week 3: scripts/validate_e2b.py + E2B template creation
         ├── needs: e2b SDK (already have), template per repo
         └── builds on existing: scripts/e2b_sandbox.py, scripts/prebuild_e2b_templates.py

Week 4: Run full pipeline on 500+ PRs, iterate on quality
```

### Script specifications

**1. `scripts/prefilter_prs.py`**
- Input: `scouted_prs.jsonl`
- Output: `filtered_prs.jsonl`
- Logic: `split_patch()` + R2E-Gym thresholds + SWE-bench criteria
- Dependencies: `unidiff`
- Lines of code: ~150

**2. `scripts/pregen_task.py`**
- Input: `filtered_prs.jsonl`
- Output: `markdown_following/<name>/` with mechanical files + `_context.json`
- Logic: `gh` CLI calls, Jinja2 templates, patch splitting
- Dependencies: `jinja2`, `gh` CLI
- Lines of code: ~300

**3. `scripts/llm_scaffold.py`**
- Input: `markdown_following/<name>/_context.json`
- Output: `instruction.md`, `test.sh`, `rubric.yaml` in task dir
- Logic: OpenRouter API call, JSON response parsing, self-check
- Dependencies: `httpx` or `openai` SDK
- Lines of code: ~400

**4. `scripts/validate_e2b.py`**
- Input: complete task dirs
- Output: validation results JSON, verdicts (PASS/NEEDS_FIX/REJECT)
- Logic: E2B sandbox oracle test (base vs gold), leakage detection
- Dependencies: `e2b` SDK
- Lines of code: ~250

---

## Open Questions

1. **Kimi test.sh quality** — Will Kimi produce gaming-resistant tests comparable to Opus? A/B test on 20 tasks will answer this. If Kimi stub scores are >0.30, fall back to hybrid (Opus for test.sh, Kimi for instruction+rubric).

2. **E2B costs at scale** — Estimated ~$0.05/task but need to verify with 50-task pilot. If too expensive, fall back to local Docker with OpenSWE's timeout pattern.

3. **Execution pre-filter ROI** — SWE-Next found 74.5% of PRs show zero test flip. But this requires running the repo's test suite in E2B for every candidate (expensive). May be cheaper to just LLM-scaffold all candidates and validate afterward. Calculate break-even point.

4. **Agent config extraction** — Currently LLM extracts rules from config files for rubric.yaml. Could be partially deterministic (regex for bullet points/numbered rules) with LLM filtering only for ambiguous rules. Worth ~$0.02/task savings.

---

## Existing Pipeline Files (v1)

```
/home/alex/agentsmd-rl/
├── scripts/
│   ├── scout_prs.py              # Phase 0: Scout → scouted_prs.jsonl (EXISTS)
│   ├── batch_scaffold.py         # v1 scaffold via claude -p (EXISTS, keep for fallback)
│   ├── run_pipeline.py           # v1 orchestrator: audit/validate/solve (EXISTS, keep)
│   ├── e2b_sandbox.py            # E2B sandbox wrapper (EXISTS)
│   ├── prebuild_e2b_templates.py # E2B template builder (EXISTS)
│   ├── prefilter_prs.py          # TO BUILD — heuristic pre-filter
│   ├── pregen_task.py            # TO BUILD — deterministic file gen + context bundle
│   ├── llm_scaffold.py           # TO BUILD — OpenRouter creative scaffold
│   └── validate_e2b.py           # TO BUILD — E2B oracle testing
├── .claude/commands/
│   ├── scaffold-task.md          # v1 LLM prompt (keep as reference)
│   ├── audit-tests.md            # v1 audit prompt (keep — may still use for Kimi output)
│   ├── validate-task.md          # v1 validate prompt (keep as reference)
│   └── build-rubric.md           # v1 rubric prompt (keep as reference)
├── scouted_prs.jsonl             # 420 PR candidates (EXISTS)
├── markdown_following/                 # 432 tasks (EXISTS)
└── pipeline_logs/                # v1 run logs (EXISTS)
```

## Reference Repos (cloned locally)

```
/home/alex/agentsmd-rl/.repos/
├── SWE-bench/          # princeton-nlp/SWE-bench — PR collection, patch splitting, criteria
├── SWE-smith/          # SWE-bench/SWE-smith — profile registry, grading, mirror collect
├── R2E-Gym/            # R2E-Gym/R2E-Gym — heuristic filters, AST entity extraction
├── SWE-rebench-V2/     # SWE-rebench/SWE-rebench-V2 — 36 Dockerfiles, 60+ log parsers, prompts
└── OpenSWE/            # GAIR-NLP/OpenSWE — Docker utils, master-worker, JSON extraction
```
