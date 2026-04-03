# Add Docker-based Integration Test Infrastructure

## Problem

Integration tests sometimes pass locally but fail on CI due to OS differences (e.g., font rendering, browser behavior). Developers currently have no way to reproduce the CI environment locally, making these failures hard to debug.

## What's Needed

Add infrastructure to run the Playwright integration tests inside a Docker container that replicates the CI environment. This should include:

1. **A Docker setup under `playwright/docker/`** — a Dockerfile that installs Playwright and its browser dependencies on a Node.js base image, a `docker-compose.yml` to orchestrate the container, and an entrypoint script that waits for the dev server to be healthy before running tests.

2. **An orchestration script** (`playwright/docker/run-tests.sh`) — a shell script that handles the full lifecycle: detects if the dev server is already running (starts one if not), runs the Docker container, and cleans up afterward. It should accept extra arguments to pass through to the Playwright test runner.

3. **A Docker-specific Playwright config** (`playwright/docker/playwright.config.docker.ts`) — extends the base `playwright.config.ts` but points to the correct test directory relative to the Docker context.

4. **Make `playwright.config.ts` base URL configurable** — the Docker container needs to connect to the host's dev server. The base `playwright.config.ts` should read `PLAYWRIGHT_BASE_URL` from the environment, falling back to `http://localhost:3000`.

5. **A `package.json` script** — add a `test:integration-docker` script so developers can run Docker tests with a single `yarn` command.

## Files to Look At

- `playwright.config.ts` — the base Playwright configuration
- `package.json` — where the new script entry goes
- `playwright/docker/` — where the new Docker infrastructure lives
- `docs/general/contributing.md` — the project's contributor guide, which documents how to run tests

After implementing the Docker test infrastructure, update the contributing documentation (`docs/general/contributing.md`) to explain how developers can use it. Include the command to run the tests and examples of passing additional arguments (e.g., running a specific test file or browser project).
