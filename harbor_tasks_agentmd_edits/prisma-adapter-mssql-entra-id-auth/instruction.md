# Support Entra ID Authentication in MSSQL Adapter Connection String Parser

## Problem

The `@prisma/adapter-mssql` package supports connecting to Azure SQL databases using Entra ID (formerly Azure Active Directory) authentication via the config object approach. However, the `parseConnectionString` function in `packages/adapter-mssql/src/connection-string.ts` does not recognize any authentication-related parameters. Users who pass `authentication=DefaultAzureCredential` or `authentication=ActiveDirectoryPassword` (etc.) in their connection string get those parameters silently ignored.

## Expected Behavior

`parseConnectionString` should parse and validate the `authentication` parameter from connection strings. Supported authentication types should include:

- `DefaultAzureCredential` / `ActiveDirectoryIntegrated` / `ActiveDirectoryInteractive` → maps to `azure-active-directory-default`
- `ActiveDirectoryPassword` (requires `userName`, `password`, `clientId`) → maps to `azure-active-directory-password`
- `ActiveDirectoryManagedIdentity` / `ActiveDirectoryMSI` (requires `msiEndpoint`, `msiSecret`) → maps to `azure-active-directory-msi-app-service`
- `ActiveDirectoryServicePrincipal` (requires `userName` as clientId, `password` as clientSecret) → maps to `azure-active-directory-service-principal-secret`

When required parameters are missing for a given authentication type, an appropriate error should be thrown.

After implementing the code changes, update the package's README (`packages/adapter-mssql/README.md`) to document the new authentication options — both the connection string approach and the config object approach for Entra ID. The README should also show that the adapter can be instantiated with a connection string directly.

## Files to Look At

- `packages/adapter-mssql/src/connection-string.ts` — the connection string parser that needs authentication support
- `packages/adapter-mssql/README.md` — documentation that should cover the new authentication options
