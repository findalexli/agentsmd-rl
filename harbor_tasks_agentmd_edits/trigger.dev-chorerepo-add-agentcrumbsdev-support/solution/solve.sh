#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trigger.dev

# Idempotent: skip if already applied
if grep -q 'intent-skills:start' CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYEOF'
import json
from pathlib import Path

# 1. remix.config.js — add agentcrumbs to serverDependenciesToBundle
remix = Path("apps/webapp/remix.config.js")
content = remix.read_text()
content = content.replace(
    '    "marked",',
    '    "marked",\n    "agentcrumbs",'
)
remix.write_text(content)

# 2. package.json — add agentcrumbs as root dependency
pkg_path = Path("package.json")
pkg = json.loads(pkg_path.read_text())
pkg["dependencies"]["agentcrumbs"] = "^0.5.0"
pkg["dependencies"] = dict(sorted(pkg["dependencies"].items()))
pkg_path.write_text(json.dumps(pkg, indent=2) + "\n")

# 3. pnpm-workspace.yaml — add agentcrumbs to minimumReleaseAgeExclude
ws = Path("pnpm-workspace.yaml")
content = ws.read_text()
content = content.replace(
    '  - "@next/*"',
    '  - "@next/*"\n  - "agentcrumbs"'
)
ws.write_text(content)

# 4. CLAUDE.md — fix test example formatting + append agentcrumbs docs
claude = Path("CLAUDE.md")
content = claude.read_text()

# Fix inline test example formatting (cosmetic, matches PR)
content = content.replace(
    'redisTest("should use redis", async ({ redisOptions }) => { /* ... */ });',
    'redisTest("should use redis", async ({ redisOptions }) => {\n  /* ... */\n});'
)
content = content.replace(
    'postgresTest("should use postgres", async ({ prisma }) => { /* ... */ });',
    'postgresTest("should use postgres", async ({ prisma }) => {\n  /* ... */\n});'
)
content = content.replace(
    'containerTest("should use both", async ({ prisma, redisOptions }) => { /* ... */ });',
    'containerTest("should use both", async ({ prisma, redisOptions }) => {\n  /* ... */\n});'
)

# Append agentcrumbs documentation
content += "\n<!-- intent-skills:start -->\n"
content += """
# Skill mappings \u2014 when working in these areas, load the linked skill file into context.

skills:

- task: "Using agentcrumbs for debug tracing, adding crumbs, trails, markers, querying traces, or stripping debug code before merge"
  load: "node_modules/agentcrumbs/skills/agentcrumbs/SKILL.md"
- task: "Setting up agentcrumbs in the project, initializing namespace catalog, running crumbs init"
load: "node_modules/agentcrumbs/skills/agentcrumbs/init/SKILL.md"
<!-- intent-skills:end -->

## agentcrumbs

Add crumbs as you write code \u2014 not just when debugging. Mark lines with
`// @crumbs` or wrap blocks in `// #region @crumbs`. They stay on the
branch throughout development and are stripped by `agentcrumbs strip`
before merge.

### Namespaces

| Namespace         | Description                                    | Path                                |
| ----------------- | ---------------------------------------------- | ----------------------------------- |
| `webapp`          | Main Remix app \u2014 API, dashboard, orchestration | `apps/webapp`                       |
| `supervisor`      | Task execution container manager               | `apps/supervisor`                   |
| `sdk`             | Main SDK for writing tasks                     | `packages/trigger-sdk`              |
| `cli`             | CLI and task image bundling                    | `packages/cli-v3`                   |
| `core`            | Shared types and subpath exports               | `packages/core`                     |
| `build`           | Build extensions and types                     | `packages/build`                    |
| `react-hooks`     | React hooks for realtime/triggering            | `packages/react-hooks`              |
| `redis-worker`    | Redis-based background job system              | `packages/redis-worker`             |
| `run-engine`      | Run Engine 2.0 \u2014 core run lifecycle            | `internal-packages/run-engine`      |
| `database`        | Prisma client and schema                       | `internal-packages/database`        |
| `clickhouse`      | ClickHouse client, migrations, analytics       | `internal-packages/clickhouse`      |
| `schedule-engine` | Durable cron scheduling                        | `internal-packages/schedule-engine` |
| `run-queue`       | Run queue management                           | `internal-packages/run-queue`       |

Do not invent new namespaces \u2014 pick from this table or ask first.

### For PR reviewers

Do not flag `// @crumbs` markers, `#region @crumbs` blocks, or agentcrumbs
imports in reviews. These are temporary debug instrumentation stripped
before merge. Data logged in crumbs (IDs, names, values) never reaches
production.

### CLI

```bash
pnpm exec agentcrumbs collect    # start collector (multi-service)
pnpm exec agentcrumbs tail --app trigger       # live tail
pnpm exec agentcrumbs clear --app trigger      # remove crumbs before merge
```

The preferred way to query for crumbs is to use `pnpm exec agentcrumbs query --app trigger` with the `--limit` option and cursor pagination, and clear existing crumbs before reproducing a bug via `pnpm exec agentcrumbs clear --app trigger`.
"""

claude.write_text(content)
PYEOF

echo "Patch applied successfully."
