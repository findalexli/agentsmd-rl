# Worker Configuration Defaults

## Problem

The BullMQ background worker has several configuration inconsistencies across the Docker Compose and Helm deployments:

1. **Worker build format**: The worker is built as a single CJS bundle (`worker.cjs`) with `--packages=external`, which requires copying workspace packages (`@sim/logger`, `@sim/db`) into the Docker image separately. The build should use ESM format with code splitting so the bundle is self-contained.

2. **Worker not enabled by default**: In `docker-compose.local.yml`, the worker service is gated behind a `profiles: [worker]` section, meaning it does not start with `docker compose up`. In the Helm chart, `worker.enabled` defaults to `false`. The worker should start by default in both environments so self-hosted deployments get queue processing out of the box.

3. **Redis should be optional**: The Helm chart's `_helpers.tpl` validation fails the deploy if `worker.enabled=true` but `REDIS_URL` is not set. Since the worker gracefully idles when Redis is unavailable, this hard requirement should be removed. The `REDIS_URL` should be plumbed through helm secrets and external secrets as an optional config.

4. **Healthcheck tooling**: Docker Compose healthchecks use `wget --spider --quiet`, but `wget` is not installed in the container images — the images have `curl` instead (the realtime Dockerfile should install `curl` in the base stage so all downstream stages inherit it).

5. **Worker path resolution**: When the worker runs from the new ESM bundle directory (`dist/worker/`), the isolated-vm worker file cannot be found because `candidatePaths` in `isolated-vm.ts` does not account for the changed directory depth. Additional fallback paths are needed.

## Expected Behavior

- The worker builds as an ESM bundle with `--splitting --outdir ./dist/worker --external isolated-vm`
- All compose files and Helm templates reference `worker/index.js` instead of `worker.cjs`
- The app Dockerfile copies `dist/worker` as a directory (no longer needs separate `@sim/logger`/`@sim/db` copies)
- The worker starts by default in `docker-compose.local.yml` (no profiles gate) and in Helm (`worker.enabled: true`)
- Helm validation does not require `REDIS_URL` when the worker is enabled
- `REDIS_URL` is added as an optional config in Helm values, secrets, and external secrets
- Healthchecks use `curl -fsS` instead of `wget --spider --quiet`
- The realtime Dockerfile installs `curl` in the base stage
- `isolated-vm.ts` has additional `candidatePaths` entries for parent-directory traversal

After making the code changes, update the relevant documentation to reflect the new worker behavior:
- The project README should explain that the worker starts by default and what happens without Redis
- The Helm chart README should document the worker/Redis relationship and how to disable the worker if not needed
- The `dev:full` command description and the "run separately" instructions should reflect that the worker is now part of the default dev stack

## Files to Look At

- `apps/sim/package.json` — build:worker script
- `docker-compose.local.yml` / `docker-compose.prod.yml` — worker service config, healthchecks
- `docker/app.Dockerfile` — worker bundle copy
- `docker/realtime.Dockerfile` — base image packages
- `helm/sim/values.yaml` — worker defaults
- `helm/sim/templates/_helpers.tpl` — validation logic
- `helm/sim/templates/deployment-worker.yaml` — worker command
- `helm/sim/templates/secrets-app.yaml` / `external-secret-app.yaml` — REDIS_URL plumbing
- `apps/sim/lib/execution/isolated-vm.ts` — worker path resolution
- `README.md` — self-hosting and dev setup docs
- `helm/sim/README.md` — Helm chart docs
