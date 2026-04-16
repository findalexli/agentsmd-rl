# Self-hosted local deploys fail without a network tunnel

## Problem

When running Trigger.dev self-hosted on a local development machine, deploying tasks via `pnpm exec trigger deploy --self-hosted` fails. The deployed Docker container cannot reach the local webapp API server.

Two issues contribute to this failure:

1. **The project environment endpoint always uses `APP_ORIGIN` for the API URL**: The file `apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts` contains a Remix route with an `export async function loader` that returns a `json()` response. One of the fields in that response is `apiUrl`, which is currently set from `APP_ORIGIN` (imported via `env.server`). In self-hosted setups, the API may be served from a different origin than the dashboard, but there is no support for using a separate `API_ORIGIN` environment variable. When `API_ORIGIN` is set it should be preferred; when it is not set, `APP_ORIGIN` should be used as the fallback.

2. **`localhost` URLs are unreachable from Docker on macOS**: The file `packages/cli-v3/src/deploy/buildImage.ts` handles building Docker images for deployment and passes the API URL via the `TRIGGER_API_URL` build argument. On macOS (Darwin), Docker containers cannot access `localhost` on the host machine -- they need to use `host.docker.internal` instead. Currently, the URL is passed through without any platform-specific normalization, so deploys fail on macOS when the API server is running on localhost.

## Expected Behavior

- In `apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts`: the `apiUrl` value in the loader response should prefer `API_ORIGIN` when it is available, falling back to `APP_ORIGIN` when it is not.
- In `packages/cli-v3/src/deploy/buildImage.ts`: a function named `normalizeApiUrlForBuild` should normalize the API URL before it is used in the Docker build. On macOS (Darwin), it should replace `localhost` with `host.docker.internal` in the URL. On Linux, the URL should be returned unchanged.
- Self-hosted deploys should work on macOS without requiring an external network tunnel (like ngrok).
