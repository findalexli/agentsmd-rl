# MongoDB Docker Port Conflicts with Local Installation

## Problem

When running the project's Docker-based MongoDB for testing, it binds to port `27017` on the host — the same default port used by a locally installed MongoDB instance. If a developer has MongoDB already running locally, `docker compose up` fails or connects to the wrong server, leading to confusing test failures.

The same issue cascades to MongoDB Atlas Local, which currently uses port `27018` — but if MongoDB is moved off `27017`, Atlas needs to shift too.

## Expected Behavior

The Docker MongoDB containers should use non-default host ports that don't collide with a locally-installed MongoDB:
- MongoDB test container should use a different host port than the MongoDB default
- MongoDB Atlas Local container should use a different host port than MongoDB's new port
- All connection URLs across the codebase (adapter config, CI actions, connection test scripts) must be updated consistently

After fixing the port configuration, update the project's contributor documentation to reflect the new connection URLs and improve the "Testing with your own database" section for developers who prefer a local MongoDB/PostgreSQL installation without Docker.

## Files to Look At

- `test/helpers/db/mongodb/docker-compose.yml` — MongoDB container port mapping
- `test/helpers/db/mongodb-atlas/docker-compose.yml` — MongoDB Atlas container port mapping
- `test/generateDatabaseAdapter.ts` — default database URLs used by the test framework
- `test/helpers/db/mongodb/run-test-connection.ts` — MongoDB connection test script
- `test/helpers/db/mongodb-atlas/run-test-connection.ts` — Atlas connection test script
- `.github/actions/start-database/action.yml` — CI database startup action
- `CONTRIBUTING.md` — contributor documentation with database setup instructions
- `.env.example` — example environment variables
