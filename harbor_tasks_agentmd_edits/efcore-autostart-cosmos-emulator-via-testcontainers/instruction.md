# Auto-start Cosmos DB Emulator via Testcontainers

## Problem

The Cosmos DB functional tests rely on manually-managed Docker scripts (`eng/testing/run-cosmos-container.ps1` and `eng/testing/run-cosmos-container.sh`) to start the Azure Cosmos DB emulator. These scripts are invoked via `PreCommands` in `eng/helix.proj` on CI, and developers must run them manually or have the emulator already running locally.

This approach is fragile: the scripts duplicate container lifecycle logic, require explicit environment variable setup (`Test__Cosmos__DefaultConnection`, `Test__Cosmos__EmulatorType=linux`, `Test__Cosmos__SkipConnectionCheck=true`), and the CI configuration in `helix.proj` has to wire up pre/post commands for starting and cleaning up the container.

## Expected Behavior

Replace the explicit Docker scripts with automatic `Testcontainers.CosmosDb` lifecycle management in `TestEnvironment`, matching the pattern already established for SQL Server in PR #37809. The test environment should:

1. Use a configured endpoint if `Test__Cosmos__DefaultConnection` is set
2. Probe `https://localhost:8081` for an already-running emulator (e.g., Windows emulator)
3. Fall back to automatically starting a `Testcontainers.CosmosDb` container

The old Docker scripts should be removed, `helix.proj` should be simplified to remove the script-based pre/post commands, and `cosmosConfig.json` should no longer hardcode the default connection.

After making the code changes, update the relevant agent skill documentation (`.agents/skills/cosmos-provider/SKILL.md`) to reflect the new emulator management approach — the current documentation references the old Docker scripts which will no longer exist.

## Files to Look At

- `test/EFCore.Cosmos.FunctionalTests/TestUtilities/TestEnvironment.cs` — static test environment configuration; needs `InitializeAsync` with 3-path connection logic
- `test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosTestStore.cs` — test store that should call `TestEnvironment.InitializeAsync` and update its connection properties
- `test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosDbContextOptionsBuilderExtensions.cs` — options builder that should use the testcontainer's `HttpMessageHandler` when available
- `eng/helix.proj` — CI configuration referencing Docker scripts in pre/post commands
- `eng/testing/run-cosmos-container.ps1` and `eng/testing/run-cosmos-container.sh` — old Docker scripts to remove
- `test/EFCore.Cosmos.FunctionalTests/cosmosConfig.json` — config with hardcoded default connection
- `test/Directory.Packages.props` and `test/EFCore.Cosmos.FunctionalTests/EFCore.Cosmos.FunctionalTests.csproj` — package references
- `.agents/skills/cosmos-provider/SKILL.md` — agent skill documentation describing emulator setup
