# Self-hosted local deploys fail without a network tunnel

## Problem

When running Trigger.dev self-hosted on a local development machine, deploying tasks via `pnpm exec trigger deploy --self-hosted` fails. The deployed Docker container cannot reach the local webapp API server.

Two issues contribute to this failure:

1. **The project environment endpoint ignores `API_ORIGIN`**: The file `apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts` contains a Remix loader that returns project environment configuration, including an `apiUrl` field. This field is currently hard-coded to use `APP_ORIGIN` (from `env.server`). In self-hosted setups, the API may be served from a different origin than the dashboard, and operators configure this via the `API_ORIGIN` environment variable. However, the endpoint ignores `API_ORIGIN` entirely and always returns the `APP_ORIGIN` value, causing the CLI to connect to the wrong URL.

2. **`localhost` URLs are unreachable from Docker on macOS**: The file `packages/cli-v3/src/deploy/buildImage.ts` builds Docker images for deployment and passes the API URL via the `TRIGGER_API_URL` build argument. On macOS (Darwin), Docker containers cannot reach `localhost` on the host machine -- they need to use `host.docker.internal` instead. The URL is currently passed through without any platform-specific handling, so deploys fail on macOS when the API server is running on localhost.

## Expected Behavior

- The `apiUrl` in the environment endpoint response should reflect `API_ORIGIN` when that variable is configured, instead of always using `APP_ORIGIN`.
- Before the API URL is passed as the `TRIGGER_API_URL` build argument, `localhost` in the URL should be replaced with `host.docker.internal` on macOS (Darwin). On Linux, the URL should be left unchanged.
- Self-hosted deploys should work on macOS without requiring an external network tunnel (like ngrok).
