# Self-hosted local deploys fail without a network tunnel

## Problem

When running Trigger.dev self-hosted on a local development machine, deploying tasks via `pnpm exec trigger deploy --self-hosted` fails. The deployed Docker container cannot reach the local webapp API server.

Two issues contribute to this:

1. The project environment endpoint always returns the app's origin as the API URL, but in self-hosted setups the API may be served from a different origin than the dashboard. There's currently no way to configure a separate API origin.

2. On macOS, Docker containers cannot access `localhost` on the host machine directly. The CLI's Docker image build passes the API URL as-is into the build args, so containers built on macOS receive an unreachable `localhost` URL.

Contributors following the setup guide in `CONTRIBUTING.md` also hit issues because the build instructions are incomplete -- they only cover building the webapp, but self-hosted deploys require additional packages to be built first.

## Expected Behavior

- Self-hosted deploys should work on macOS without requiring an external tunnel (like ngrok).
- The API URL handling should support configuring a separate API origin, falling back to the existing app origin.
- Development documentation should accurately reflect all the packages that need to be built for the full local development workflow.

## Files to Look At

- `apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts` -- project environment config endpoint that returns the API URL
- `packages/cli-v3/src/deploy/buildImage.ts` -- Docker image build logic for self-hosted deploys
- `CONTRIBUTING.md` -- development setup instructions (build step)
- `apps/supervisor/README.md` -- supervisor app development setup docs
