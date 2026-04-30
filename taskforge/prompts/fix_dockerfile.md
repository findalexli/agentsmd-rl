# Fix Rotted Dockerfile

You are repairing a benchmark task's `environment/Dockerfile` whose build is currently broken — the GitHub Actions push-images workflow logged a specific failure when trying to build this image. Your job is to fix the rot in-place, preserve all task semantics (same base commit, same dependencies, same logical install order), and produce a Dockerfile that `docker build` succeeds on.

## DO NOT

- Touch `tests/`, `solution/`, `instruction.md`, `eval_manifest.yaml`, `task.toml`
- Change the base commit (`git fetch --depth=1 origin <SHA>`)
- Switch to a different upstream repo
- Add unnecessary dependencies (e.g., the entire dev toolchain)
- Use `:latest` tags (CLAUDE.md forbids; keep base image pinned)

## YOUR JOB

1. Read `/workspace/task/environment/Dockerfile`
2. Read `/workspace/task/_failure.log` (the tail of the failed `docker build` output captured from the GHA run)
3. Identify the broken instruction(s)
4. Apply a **minimal** fix using the Known Recipes below (or analogous reasoning)
5. Verify by running `docker build -t task-env /workspace/task/environment/` inside the sandbox
6. Write final verdict to `/workspace/task/scaffold_status.json`

## Known recipes for common Dockerfile rot

### `curl bun.sh/install | bash` returns exit 1 (URL/auth changed)

Replace with one of:

```dockerfile
# Option A — npm-based install (works on Node bases)
RUN npm install -g bun

# Option B — pinned tarball
RUN curl -fsSL https://github.com/oven-sh/bun/releases/download/bun-v1.1.34/bun-linux-x64.zip -o /tmp/bun.zip && \
    unzip /tmp/bun.zip -d /usr/local/bin/ && rm /tmp/bun.zip
```

### `pip install uv` exits 1 (PEP 668 externally-managed venv)

Use `--break-system-packages` or astral-sh installer:

```dockerfile
# Option A
RUN pip install --break-system-packages -q uv

# Option B (recommended — pulls precompiled binary)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv
```

### `git fetch --depth=1 origin <SHA>` returns exit 128 (commit gone)

The PR's commit was rebased / squashed and no longer exists on the remote. Look up the **real** merge commit via the PR API:

```bash
gh api repos/<OWNER>/<REPO>/pulls/<N> --jq '.merge_commit_sha'
```

Replace the SHA in the Dockerfile.

### Missing `/tests` dir → tests can't be mounted

Add `RUN mkdir -p /tests` somewhere before `WORKDIR`.

### `pip3 install ...` exits 1 on slim base (pip not present)

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-venv && rm -rf /var/lib/apt/lists/*
```

### `apt-get install -y <pkg>` exits 100 (package list expired)

Always pair with `apt-get update`:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends <pkg> && \
    rm -rf /var/lib/apt/lists/*
```

### `corepack enable` exits non-zero (Node version too old)

Either bump base image to `node:20-slim` or use direct npm install:

```dockerfile
FROM node:20-slim
RUN corepack enable && corepack prepare pnpm@9.4.0 --activate
```

## Self-validate before declaring success

```bash
cd /workspace && docker build -t task-env-test ./task/environment/ 2>&1 | tail -50
```

The build must succeed (exit 0). If it doesn't, READ the new error and adjust. Iterate up to 3 times before giving up.

## Final verdict

Write to `/workspace/task/scaffold_status.json`:

```json
{"scaffolded": true, "nop_reward": 0, "gold_reward": 1, "dockerfile_fixed": true}
```

If unfixable (e.g., upstream repo deleted, base image yanked, hardware-specific dep), abandon honestly:

```json
{"abandoned": true, "reason": "<one-sentence cause>"}
```

The pipeline trusts your verdict. Do not write `scaffolded: true` if `docker build` did not succeed.
