# DAG Architecture: Reactive Agent Nodes

## Core Insight

Each node is NOT a single action. Each node is an **agent with its own feedback loop**. A failed Docker build doesn't wait for a "repair" node — the Docker Build node's agent sees the error immediately and fixes it.

```
OLD (rigid pipeline with repair at the end):
  Lint → Improve → Docker Build → NOP → Gold → Judge → P2P → Repair → loop back
  Problem: Docker build fails at step 3, but repair happens at step 7.
  Problem: Repair loops ALL the way back to step 1.

NEW (each node is a self-healing agent):
  [Scaffold Agent] → [Test Agent] → [Docker Agent] → [Validation Agent] → [Judge Agent] → [P2P Agent]
       ↻ retry          ↻ retry        ↻ retry           ↻ retry            ↻ retry         ↻ retry
  Each node retries internally until it passes, then hands off to the next.
```

## The Nodes

### Node 0: Scaffold Agent (new PRs only)
```
┌─────────────────────────────────────────────────────────┐
│ SCAFFOLD AGENT                                          │
│                                                         │
│ Trigger: PR reference (owner/repo#123)                  │
│ Agent: claude -p + prompts/scaffold.md                  │
│                                                         │
│ Loop:                                                   │
│   1. Run scaffold prompt                                │
│   2. Check: do all required files exist?                │
│      - environment/Dockerfile                           │
│      - tests/test_outputs.py (with def test_*)          │
│      - solution/solve.sh                                │
│      - eval_manifest.yaml                               │
│      - instruction.md                                   │
│      - task.toml                                        │
│   3. If missing → agent reads own output, fills gaps    │
│   4. Repeat until all files exist or max retries        │
│                                                         │
│ Writes to status.json:                                  │
│   nodes.scaffold: {                                     │
│     status: "ok",                                       │
│     files_created: ["Dockerfile", "test_outputs.py"...],│
│     repo: "microsoft/playwright",                       │
│     language: "typescript",                              │
│     test_framework: "jest",                              │
│     notes: "Created 8 files, 5 f2p + 2 p2p + 1 static" │
│   }                                                     │
│                                                         │
│ Output: Complete task directory                          │
│ SYNC: Download all files to local after completion      │
└─────────────────────────────────────────────────────────┘
```

### Node 1: Test Quality Agent
```
┌─────────────────────────────────────────────────────────┐
│ TEST QUALITY AGENT                                      │
│                                                         │
│ Trigger: task files exist                               │
│ Reads: status.json (scaffold notes: language, framework)│
│                                                         │
│ Phase A — Programmatic quality gate (orchestrator, no LLM):
│   1. ast.parse(test_outputs.py) → syntax ok?            │
│   2. grep NotImplementedError → stubs?                  │
│   3. grep subprocess.run → behavioral?                  │
│   4. Count def test_ functions                          │
│   5. Check eval_manifest.yaml has matching checks       │
│   → If all pass: SKIP agent, go to next node            │
│                                                         │
│ Phase B — LLM improve (only if gate fails):             │
│   Agent: claude -p + prompts/improve_tests.md           │
│   Agent reads: status.json (knows language, framework)  │
│   Agent reads: scaffold notes (what was created)        │
│                                                         │
│   Loop:                                                 │
│     1. Run improve prompt                               │
│     2. Re-run quality gate                              │
│     3. If still fails → agent reads own output + error  │
│     4. Repeat until gate passes or max retries          │
│                                                         │
│ Writes to status.json:                                  │
│   nodes.test_quality: {                                 │
│     status: "ok",                                       │
│     has_subprocess: true,                                │
│     test_count: 8,                                      │
│     f2p_count: 5,                                       │
│     p2p_count: 3,                                       │
│     notes: "Upgraded 4 grep tests to subprocess.        │
│             Repo uses vitest, added vitest run p2p."    │
│   }                                                     │
│                                                         │
│ SYNC: Download improved test_outputs.py + eval_manifest │
└─────────────────────────────────────────────────────────┘
```

### Node 2: Docker Build Agent
```
┌─────────────────────────────────────────────────────────┐
│ DOCKER BUILD AGENT                                      │
│                                                         │
│ Trigger: test quality passed                            │
│ Reads: status.json (language, framework, test_quality)  │
│                                                         │
│ Loop:                                                   │
│   1. docker build -t task-env environment/              │
│   2. If exit=0 → PASS, go to next node                  │
│   3. If exit≠0 → INVOKE claude -p with:                 │
│      ┌──────────────────────────────────────┐           │
│      │ PROMPT (dynamic, not a file):        │           │
│      │                                      │           │
│      │ Docker build failed. Read:           │           │
│      │ - /workspace/task/status.json        │           │
│      │ - /workspace/task/environment/       │           │
│      │   Dockerfile                         │           │
│      │                                      │           │
│      │ Error output:                        │           │
│      │ {stderr last 1000 chars}             │           │
│      │                                      │           │
│      │ Fix the Dockerfile. Common issues:   │           │
│      │ - Missing apt package                │           │
│      │ - Wrong base image                   │           │
│      │ - git clone/checkout failure         │           │
│      │ - Missing python3 on node images     │           │
│      │                                      │           │
│      │ After fixing, update status.json     │           │
│      │ nodes.docker_build.notes with        │           │
│      │ what you changed.                    │           │
│      └──────────────────────────────────────┘           │
│   4. Re-run docker build                                │
│   5. Repeat until build succeeds or max retries         │
│                                                         │
│ Writes to status.json:                                  │
│   nodes.docker_build: {                                 │
│     status: "ok",                                       │
│     attempts: 2,                                        │
│     notes: "Build failed on 1st try: missing corepack.  │
│             Added RUN corepack enable. 2nd try passed." │
│   }                                                     │
│                                                         │
│ SYNC: Download fixed Dockerfile                         │
│ Output: Working Docker image "task-env"                 │
└─────────────────────────────────────────────────────────┘
```

### Node 3: Validation Agent (NOP + Gold)
```
┌─────────────────────────────────────────────────────────┐
│ VALIDATION AGENT                                        │
│                                                         │
│ Trigger: Docker image built                             │
│ Reads: status.json (all previous nodes)                 │
│                                                         │
│ Step A — NOP test:                                      │
│   docker run task-env bash /tests/test.sh               │
│   Read reward.txt → expect 0                            │
│                                                         │
│   If reward=1 (tests too weak):                         │
│     INVOKE claude -p:                                   │
│     ┌──────────────────────────────────────┐            │
│     │ Tests pass without the fix applied.  │            │
│     │ NOP reward = 1, expected 0.          │            │
│     │                                      │            │
│     │ Read status.json for context.        │            │
│     │ Read test output: {pytest output}    │            │
│     │ Read solve.sh to understand the fix. │            │
│     │                                      │            │
│     │ The f2p tests must FAIL on base      │            │
│     │ commit. Rewrite them to test the     │            │
│     │ behavior that actually changes.      │            │
│     │                                      │            │
│     │ After rewriting, update status.json  │            │
│     │ and eval_manifest.yaml.              │            │
│     └──────────────────────────────────────┘            │
│     → Re-run NOP test (no Docker rebuild needed,        │
│       tests are volume-mounted)                         │
│     → Repeat until nop=0 or max retries                 │
│                                                         │
│ Step B — Gold test:                                     │
│   Apply solve.sh → docker commit → run test.sh          │
│   Read reward.txt → expect 1                            │
│                                                         │
│   If reward=0:                                          │
│     Read pytest output to diagnose:                     │
│     - Which specific tests failed?                      │
│     - Did solve.sh apply cleanly?                       │
│     INVOKE claude -p:                                   │
│     ┌──────────────────────────────────────┐            │
│     │ Tests fail after applying the fix.   │            │
│     │ Gold reward = 0, expected 1.         │            │
│     │                                      │            │
│     │ Pytest output: {output}              │            │
│     │ solve.sh exit code: {code}           │            │
│     │                                      │            │
│     │ Read status.json for full context.   │            │
│     │ Diagnose: is solve.sh wrong, are     │            │
│     │ tests too strict, or is Dockerfile   │            │
│     │ missing deps for the tests?          │            │
│     │                                      │            │
│     │ Fix the issue. If you change the     │            │
│     │ Dockerfile, note it in status.json   │            │
│     │ so Docker Build can re-run.          │            │
│     └──────────────────────────────────────┘            │
│     → If Dockerfile changed: go back to Docker Build    │
│     → If only tests/solve changed: re-run Gold test     │
│     → Repeat until gold=1 or max retries                │
│                                                         │
│ Writes to status.json:                                  │
│   nodes.validation: {                                   │
│     status: "pass",                                     │
│     nop_reward: 0.0,                                    │
│     gold_reward: 1.0,                                   │
│     nop_attempts: 1,                                    │
│     gold_attempts: 2,                                   │
│     pytest_nop_summary: "3 failed, 2 passed",           │
│     pytest_gold_summary: "5 passed",                    │
│     notes: "Gold failed 1st try: solve.sh had wrong     │
│             path. Fixed path in solve.sh. 2nd try OK."  │
│   }                                                     │
│                                                         │
│ SYNC: Download fixed test_outputs.py / solve.sh         │
│ Output: Confirmed nop=0 and gold=1                      │
└─────────────────────────────────────────────────────────┘
```

### Node 4: Rubric Judge
```
┌─────────────────────────────────────────────────────────┐
│ RUBRIC JUDGE                                            │
│                                                         │
│ Trigger: nop=0 and gold=1 confirmed                     │
│ Reads: eval_manifest.yaml rubric rules                  │
│                                                         │
│ Action: python3 judge.py --manifest ... --repo ...      │
│   (standardized — no custom prompts)                    │
│                                                         │
│ If ICR < 0.8:                                           │
│   The rubric rules are soft (style, convention).        │
│   These should already pass for the gold solution.      │
│   If they don't, either:                                │
│   - The rubric rules are wrong (too strict)             │
│   - The gold solution missed a convention               │
│   → Log warning but don't block. Rubric is advisory.    │
│                                                         │
│ Writes to status.json:                                  │
│   nodes.rubric_judge: {                                 │
│     status: "pass",                                     │
│     icr: 1.0,                                           │
│     notes: "2/2 rubric rules satisfied"                 │
│   }                                                     │
│                                                         │
│ No SYNC needed (no files changed)                       │
└─────────────────────────────────────────────────────────┘
```

### Node 5: P2P Enrichment Agent
```
┌─────────────────────────────────────────────────────────┐
│ P2P ENRICHMENT AGENT                                    │
│                                                         │
│ Trigger: validation passed                              │
│ Reads: status.json (language, framework, what CI exists)│
│ Agent: claude -p + prompts/enrich_p2p.md                │
│                                                         │
│ Loop:                                                   │
│   1. Agent discovers repo CI (package.json, Makefile..) │
│   2. Agent adds p2p tests to test_outputs.py            │
│   3. Orchestrator re-runs NOP test (volume-mounted)     │
│      → If nop≠0: p2p tests broke something             │
│        → Agent reads error, removes broken p2p test     │
│   4. Orchestrator re-runs Gold test                     │
│      → If gold≠1: p2p test fails after fix              │
│        → Agent reads error, fixes or removes            │
│   5. Repeat until all pass or max retries               │
│                                                         │
│ Writes to status.json:                                  │
│   nodes.p2p_enrichment: {                               │
│     status: "ok",                                       │
│     ci_commands_found: ["npm test", "npm run lint"],     │
│     tests_added: ["test_repo_lint"],                     │
│     tests_removed: [],                                   │
│     notes: "Found 3 CI commands. Added lint as p2p.     │
│             Skipped 'npm test' — takes 300s, too slow." │
│   }                                                     │
│                                                         │
│ SYNC: Download enriched test_outputs.py + eval_manifest │
└─────────────────────────────────────────────────────────┘
```

## Communication Flow

```
status.json is the shared memory across all nodes:

Scaffold → writes: repo, language, framework, files_created
    ↓
Test Quality → reads: language, framework
             → writes: test_count, subprocess status, what was improved
    ↓
Docker Build → reads: all above (for context in error diagnosis)
             → writes: build attempts, what was fixed
    ↓
Validation  → reads: all above (especially test_quality notes)
            → writes: nop/gold rewards, pytest output, what was fixed
            → CAN GO BACK TO Docker Build if Dockerfile needs changing
    ↓
Rubric Judge → reads: eval_manifest.yaml (standardized format)
             → writes: ICR score, which rules passed/failed
    ↓
P2P Enrich  → reads: all above (especially language, CI info)
            → writes: what CI was found, what tests were added
            → RE-RUNS Validation internally to verify
```

## Key Difference: Back-edges

The current pipeline only goes forward. The new architecture has **back-edges**:

```
                    ┌──────────────────────────┐
                    │                          │
                    ▼                          │
Scaffold → Test Quality → Docker Build → Validation → Judge → P2P
                              ▲              │           │
                              │              │           │
                              └──────────────┘           │
                          (if Dockerfile needs           │
                           fixing for gold test)         │
                                                         │
                              ▲                          │
                              └──────────────────────────┘
                          (if p2p test needs Dockerfile dep)
```

Validation Agent can say "I need to go back to Docker Build" by writing to status.json:
```json
{
  "nodes": {
    "validation": {
      "status": "needs_docker_rebuild",
      "notes": "Fixed Dockerfile to add missing libxml2-dev for p2p lxml test"
    }
  }
}
```

The orchestrator reads this and routes back to Docker Build, not to the beginning.

## Prompts Inventory

| Node | Prompt Source | When Used |
|------|-------------|-----------|
| Scaffold | `prompts/scaffold.md` | Always (new PRs) |
| Test Quality | `prompts/improve_tests.md` | Only if quality gate fails |
| Docker Build fix | **Dynamic** (error + context) | Only if build fails |
| NOP fix | **Dynamic** (pytest output + context) | Only if nop≠0 |
| Gold fix | **Dynamic** (pytest output + context) | Only if gold≠1 |
| Rubric Judge | `judge.py` (standardized) | Always (if rubric rules exist) |
| P2P Enrichment | `prompts/enrich_p2p.md` | Always (first pass) |

"Dynamic" prompts are built by the orchestrator from error output + status.json context.
They are NOT hardcoded LLM judge prompts — they're "here's what broke, fix it" instructions.

## Orchestrator Pseudocode

```python
async def run_task_dag(task, sandbox, pool):
    status = {}
    
    # Node 0: Scaffold (if new)
    if is_new:
        status = await scaffold_agent(sandbox, pr_ref)
        sync_to_local(sandbox, dest)
    
    # Node 1: Test Quality
    status = await test_quality_agent(sandbox, status)
    sync_to_local(sandbox, dest)
    
    # Node 2: Docker Build (with internal retry)
    status = await docker_build_agent(sandbox, status)
    sync_to_local(sandbox, dest)
    
    # Node 3: Validation (NOP + Gold, with back-edge to Docker)
    while True:
        status = await validation_agent(sandbox, status)
        if status.needs_docker_rebuild:
            status = await docker_build_agent(sandbox, status)
            continue
        break
    sync_to_local(sandbox, dest)
    
    # Node 4: Rubric Judge
    status = await rubric_judge(sandbox, status)
    
    # Node 5: P2P (with re-validation)
    status = await p2p_agent(sandbox, status)
    sync_to_local(sandbox, dest)
    
    # Always save final state
    write_status_json(dest, status)
```

## Per-Node Retry Budget

Instead of MAX_DAG_ITERATIONS=3 globally, each node gets its own retry budget:

| Node | Max Retries | Timeout | Why |
|------|------------|---------|-----|
| Scaffold | 1 | 600s | If scaffold fails, task is likely bad PR |
| Test Quality | 2 | 600s | Improve can take 2 tries to get right |
| Docker Build | 3 | 300s | Build errors are usually fixable |
| NOP test | 2 | 120s | If tests still pass after 2 rewrites, task is broken |
| Gold test | 3 | 120s | solve.sh + test fixes may need iteration |
| Rubric Judge | 0 | 60s | Advisory only, no retry |
| P2P Enrichment | 2 | 600s | CI discovery + test addition |
