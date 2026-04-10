# E2B Worker Architecture — Full Pipeline in Sandboxes

## Problem

Our current pipeline runs on one machine:
- **Scaffold**: `claude -p` creates task files (~320 MB/process, 8 workers max)
- **Improve-tests**: `claude -p` upgrades stub tests (~320 MB/process)
- **Validate**: Must build Docker image per task + run test.sh twice — **cannot parallelize locally**

With 1000+ tasks, validation alone would take days serially. Scaffolding is bottlenecked by API rate limits, not compute. Moving everything to E2B gives us **50+ parallel workers**, each with its own Docker daemon.

## Architecture: E2B Worker Sandbox

One pre-built template. Each sandbox is a full-capability worker that can scaffold, improve, AND validate.

```
Local Orchestrator (taskforge/e2b_worker.py)
  │
  ├── Build template once: "harbor-worker"
  │     - Ubuntu 24.04 + Docker daemon
  │     - Claude Code CLI (npm -g @anthropic-ai/claude-code)
  │     - Python 3.12 + pytest + pyyaml
  │     - Git + gh CLI + ripgrep + jq
  │
  └── For each task (50 concurrent sandboxes):
        │
        ├── Create sandbox from "harbor-worker" template (~5s)
        ├── Inject env vars (API keys for GLM/Fireworks/OAuth)
        ├── Upload task files OR PR reference
        │
        ├── MODE: scaffold
        │     claude -p < scaffold_prompt.md
        │     → creates task files in /workspace/task/
        │
        ├── MODE: improve-tests
        │     claude -p < improve_tests_prompt.md
        │     → rewrites test_outputs.py
        │
        ├── MODE: validate
        │     cd /workspace/task/environment && docker build -t task .
        │     NOP:  docker run ... bash /tests/test.sh  → expect reward=0
        │     GOLD: apply solve.sh, run test.sh again   → expect reward=1
        │
        ├── Download results (task files + validation status)
        └── Kill sandbox
```

## E2B Template: harbor-worker

### e2b.toml
```toml
[template]
name = "harbor-worker"
cpu_count = 4
memory_mb = 8192
start_cmd = "dockerd --storage-driver=overlay2 &"
dockerfile = "Dockerfile"
```

### Dockerfile
```dockerfile
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# System deps
RUN apt-get update && apt-get install -y \
    curl git jq ripgrep python3 python3-pip python3-venv \
    ca-certificates gnupg lsb-release sudo && \
    rm -rf /var/lib/apt/lists/*

# Docker (runs natively in Firecracker microVM)
RUN curl -fsSL https://get.docker.com | sh

# Node.js 22 + Claude Code CLI
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @anthropic-ai/claude-code@latest

# GitHub CLI (for scaffold PR fetching)
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
    gpg --dearmor -o /usr/share/keyrings/githubcli.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/githubcli.gpg] https://cli.github.com/packages stable main" \
    > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update && apt-get install -y gh

# Python test deps
RUN pip3 install --break-system-packages pytest pyyaml

# Working directory
RUN mkdir -p /workspace/task /logs/verifier
WORKDIR /workspace
```

## Execution Modes

### Mode 1: Full Pipeline (scaffold → improve → validate)

Best for new PRs. One sandbox does everything.

```python
async def full_pipeline(sandbox, pr_ref: str, env: dict) -> dict:
    """Scaffold a task from PR, improve tests, validate with Docker."""

    # 1. Scaffold: claude -p creates all task files
    scaffold_prompt = SCAFFOLD_PROMPT.replace("$ARGUMENTS", pr_ref)
    r = await sandbox.commands.run(
        f"echo '{scaffold_prompt}' | claude -p --dangerously-skip-permissions "
        f"--model opus --max-budget-usd 10 --max-turns 30",
        timeout=600, envs=env,
    )
    if r.exit_code != 0:
        return {"status": "scaffold_error", "stderr": r.stderr[-500:]}

    # 2. Check if tests are stubs
    test_content = await sandbox.files.read("/workspace/task/tests/test_outputs.py")
    if "NotImplementedError" in test_content:
        # Run improve-tests
        improve_prompt = build_improve_prompt(task_dir="/workspace/task")
        r = await sandbox.commands.run(
            f"echo '{improve_prompt}' | claude -p --dangerously-skip-permissions "
            f"--model opus --max-budget-usd 5",
            timeout=600, envs=env,
        )

    # 3. Validate: Docker build + nop/gold tests
    return await validate_in_sandbox(sandbox)


async def validate_in_sandbox(sandbox) -> dict:
    """Build Docker image from task Dockerfile, run nop + gold tests."""

    # Build the task's Docker image
    r = await sandbox.commands.run(
        "cd /workspace/task/environment && docker build -t task-env .",
        timeout=600,
    )
    if r.exit_code != 0:
        return {"status": "build_error", "stderr": r.stderr[-1000:]}

    # NOP test (no fix, expect reward=0)
    await sandbox.commands.run("rm -f /logs/verifier/reward.txt")
    r = await sandbox.commands.run(
        "docker run --rm "
        "-v /workspace/task/tests:/tests:ro "
        "-v /logs/verifier:/logs/verifier "
        "task-env bash /tests/test.sh",
        timeout=300,
    )
    nop_reward = await _read_reward(sandbox)

    # Apply gold solution inside the image
    # We need to: run solve.sh in the container, commit, then re-test
    await sandbox.commands.run(
        "docker run --name task-solved "
        "-v /workspace/task/solution:/solution:ro "
        "task-env bash /solution/solve.sh",
        timeout=300,
    )
    await sandbox.commands.run("docker commit task-solved task-env-gold")
    await sandbox.commands.run("docker rm task-solved")

    # GOLD test (fix applied, expect reward=1)
    await sandbox.commands.run("rm -f /logs/verifier/reward.txt")
    r = await sandbox.commands.run(
        "docker run --rm "
        "-v /workspace/task/tests:/tests:ro "
        "-v /logs/verifier:/logs/verifier "
        "task-env-gold bash /tests/test.sh",
        timeout=300,
    )
    gold_reward = await _read_reward(sandbox)

    return {
        "status": "ok",
        "nop": nop_reward,
        "gold": gold_reward,
        "valid": nop_reward == 0 and gold_reward == 1,
    }
```

### Mode 2: Validate Only

For existing tasks with complete files. Upload task dir, build Docker, run tests.

```python
async def validate_only(sandbox, task_path: Path) -> dict:
    """Upload existing task files and validate."""

    # Upload all task files
    for f in task_path.rglob("*"):
        if f.is_file():
            rel = f.relative_to(task_path)
            await sandbox.files.write(f"/workspace/task/{rel}", f.read_bytes())

    return await validate_in_sandbox(sandbox)
```

### Mode 3: Improve + Validate

For tasks with stub tests. Upload, improve, validate.

```python
async def improve_and_validate(sandbox, task_path: Path, env: dict) -> dict:
    """Upload task, improve stub tests via claude -p, then validate."""

    # Upload task files
    for f in task_path.rglob("*"):
        if f.is_file():
            rel = f.relative_to(task_path)
            await sandbox.files.write(f"/workspace/task/{rel}", f.read_bytes())

    # Improve tests
    improve_prompt = build_improve_prompt(task_dir="/workspace/task")
    r = await sandbox.commands.run(
        f"echo '{improve_prompt}' | claude -p --dangerously-skip-permissions "
        f"--model opus --max-budget-usd 5",
        timeout=600, envs=env,
    )

    # Download improved test file
    improved = await sandbox.files.read("/workspace/task/tests/test_outputs.py")

    # Validate
    result = await validate_in_sandbox(sandbox)
    result["improved_test"] = improved  # Return to save locally
    return result
```

## Backend Pool Integration

The E2B worker inherits our backend pool strategy via env vars:

```python
def make_worker_env(pool_backend: str = "glm") -> dict:
    """Create env vars for claude -p inside E2B sandbox."""
    envs = {
        "GH_TOKEN": os.environ["GH_TOKEN"],  # For gh CLI
    }

    if pool_backend == "glm":
        envs.update({
            "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
            "ANTHROPIC_API_KEY": os.environ["GLM_API_KEY"],
            "ANTHROPIC_AUTH_TOKEN": os.environ["GLM_API_KEY"],
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5.1",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-5.1",
        })
    elif pool_backend == "fireworks":
        envs.update({
            "ANTHROPIC_BASE_URL": "https://api.fireworks.ai/inference",
            "ANTHROPIC_API_KEY": os.environ["FIREWORKS_API_KEY"],
            "ANTHROPIC_AUTH_TOKEN": os.environ["FIREWORKS_API_KEY"],
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo",
        })
    elif pool_backend == "oauth":
        envs.update({
            "CLAUDE_ACCESS_TOKEN": os.environ["CLAUDE_ACCESS_TOKEN"],
        })

    return envs
```

The orchestrator can distribute work across backends:
- GLM sandboxes: 4 concurrent (free tier limit)
- Fireworks sandboxes: 10 concurrent
- OAuth sandboxes: 4 concurrent (conserve daily limit)
- Total: ~18 concurrent full-pipeline workers

## Concurrency Model

```
Orchestrator (local)
  ├── GLM worker pool:      4 sandboxes  (scaffold + validate)
  ├── Fireworks worker pool: 10 sandboxes (scaffold + validate)
  ├── OAuth worker pool:     4 sandboxes  (scaffold + validate, sparingly)
  │
  ├── Validate-only pool:   30 sandboxes  (no LLM needed, just Docker)
  │   (for tasks with complete tests, only need Docker build + run)
  │
  └── Total: up to 48 concurrent sandboxes
```

### Throughput Estimates

| Mode | Per sandbox | Sandboxes | Throughput |
|------|------------|-----------|------------|
| Full pipeline (scaffold+validate) | ~5 min | 18 | ~3.6/min |
| Validate only (Docker build+test) | ~3 min | 30 | ~10/min |
| Improve + validate | ~4 min | 18 | ~4.5/min |

For 1000 tasks needing full pipeline: ~280 min (4.7 hrs) at 18 workers.
For 500 tasks needing validate-only: ~50 min at 30 workers.

## Cost Estimate

| Resource | Rate | Usage | Cost |
|----------|------|-------|------|
| E2B sandbox (4 CPU, 8 GB) | ~$0.20/hr | 1000 tasks × 5 min | ~$17 |
| GLM API | Free | ~500 tasks | $0 |
| Fireworks API | ~$0.001/task | ~500 tasks | ~$0.50 |
| Template build | One-time | 1 | ~$0.10 |
| **Total** | | | **~$18** |

## Implementation Plan

### Phase 1: Template + validate-only (do first)

1. Create `taskforge/e2b_template/Dockerfile` and `e2b.toml`
2. `e2b template build` to create harbor-worker template
3. Rewrite `taskforge/e2b.py` validate path to use single template + Docker-in-sandbox
4. Test: validate 10 known-good tasks
5. Batch: validate all ~500 GOOD tasks

### Phase 2: Scaffold + validate in E2B

1. Add `--mode scaffold` to e2b.py
2. Inject backend env vars per sandbox
3. Upload scaffold prompt, run claude -p, download results
4. Chain: scaffold → validate in same sandbox
5. Test: scaffold 10 new PRs end-to-end

### Phase 3: Full batch pipeline

1. Add `--mode full` to e2b.py
2. Orchestrator reads scouted PRs JSONL, dispatches to sandbox pool
3. Each sandbox: scaffold → improve-tests → validate → report
4. Only download + commit tasks that pass validation (nop=0, gold=1)
5. Run on all remaining ~800 unsaffolded PRs

## Validate-only Docker Pattern (Detail)

The key insight: each E2B sandbox runs Docker natively. The task's Dockerfile builds
a container WITH the repo at the pre-fix commit. Tests run inside that container.

```
E2B Sandbox (Firecracker microVM)
  └── Docker daemon
        ├── docker build -t task-env .     ← task's Dockerfile (clones repo)
        ├── docker run task-env test.sh    ← NOP test (expect reward=0)
        ├── docker run + solve.sh          ← Apply gold fix
        ├── docker commit → task-env-gold
        └── docker run task-env-gold test.sh  ← GOLD test (expect reward=1)
```

This is Docker-in-VM, not Docker-in-Docker. No privileged mode needed.

## Open Questions

1. **Template build time**: Building a template with Docker + Node + Claude CLI might take 5-10 min. One-time cost.
2. **Sandbox boot time**: Firecracker VMs boot in ~1-3s, but `dockerd` startup adds ~5s. Budget ~10s per sandbox creation.
3. **Docker image caching**: Each sandbox starts fresh — no shared Docker layer cache. Tasks from the same repo (e.g., 30 react tasks all cloning facebook/react) will each re-clone. Could pre-pull common base images in the template.
4. **File transfer**: Upload ~50 KB per task (10-20 files), download ~50 KB results. Negligible.
5. **E2B concurrency limits**: Default ~50 concurrent sandboxes. May need to request increase.
6. **claude -p in sandbox**: Need to test that Claude Code CLI works correctly inside E2B with env var auth (no interactive login).
7. **GH_TOKEN**: Scaffold needs `gh` CLI for PR fetching. Pass token as env var.

## Existing Code to Reuse

- `taskforge/e2b.py`: Has `validate_one()`, `run_cmd()`, `retry_on_429()`, resume support, CLI args. Rewrite `validate_one()` to use single template + Docker.
- `taskforge/backends.py`: `backends_from_env()` → generate env dicts for sandboxes.
- `taskforge/pipeline.py`: `load_command()` → build prompts for scaffold/improve.
- `.claude/commands/scaffold-task.md`: Scaffold prompt template.
- `taskforge/prompts/improve_tests.md`: Improve-tests prompt template.

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `taskforge/e2b_template/Dockerfile` | CREATE | Worker template: Docker + Claude CLI + Python + gh |
| `taskforge/e2b_template/e2b.toml` | CREATE | Template config (4 CPU, 8 GB) |
| `taskforge/e2b.py` | REWRITE | Single-template workers, 3 modes, backend pool |
| `taskforge/pipeline.py` | MODIFY | Add `--e2b` flag to dispatch to E2B workers |
