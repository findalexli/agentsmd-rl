The SessionDatabase class in `src/vs/platform/agentHost/node/sessionDatabase.ts` has internal members (`_dbPromise`, `_closed`, `_ensureDb`) that are currently marked as `private`, making them inaccessible for subclassing in test scenarios.

The test suite uses file-based SQLite databases in temporary directories, which causes intermittent test failures due to database locking issues. To enable testing with in-memory SQLite databases (`:memory:`), tests need to be able to subclass SessionDatabase to inject database connections directly.

Additionally, the `runMigrations` helper function needs to be exported so it can be used by test subclasses when initializing injected database connections.

Modify the SessionDatabase class to:
1. Export the `runMigrations` function
2. Change `_dbPromise`, `_closed`, and `_ensureDb` from `private` to `protected`

This will enable the test suite to create a `TestableSessionDatabase` subclass that can:
- Eject the raw database connection for reuse across test cases
- Create SessionDatabase instances from existing database connections
- Avoid the filesystem lock contention issues present with file-based test databases
