# Support Entra ID Authentication in MSSQL Adapter Connection Strings

## Problem

The `@prisma/adapter-mssql` package supports connecting to SQL Server via a config object or a connection string. While the underlying `mssql`/`tedious` driver supports Azure Entra ID (formerly Azure Active Directory) authentication via the config object, the `parseConnectionString` function in `packages/adapter-mssql/src/connection-string.ts` does not recognize authentication parameters in connection strings.

This means users who want to use Entra ID authentication (DefaultAzureCredential, ActiveDirectoryPassword, ActiveDirectoryManagedIdentity, or ActiveDirectoryServicePrincipal) cannot do so through a connection string — they must use the config object approach.

## Expected Behavior

The connection string parser should support an `authentication` parameter that maps to the appropriate tedious authentication types:
- `DefaultAzureCredential`, `ActiveDirectoryIntegrated`, `ActiveDirectoryInteractive` → default Azure credential
- `ActiveDirectoryPassword` → password-based auth (requires `userName`, `password`, `clientId`)
- `ActiveDirectoryManagedIdentity` / `ActiveDirectoryMSI` → managed identity (requires `msiEndpoint`, `msiSecret`)
- `ActiveDirectoryServicePrincipal` → service principal (requires `userName` as clientId, `password` as clientSecret)

Invalid or incomplete authentication configurations should throw descriptive errors.

After implementing the code changes, update the adapter's README to document both the connection string usage and the Entra ID authentication options so that users can discover and use these features.

## Files to Look At

- `packages/adapter-mssql/src/connection-string.ts` — the connection string parser that needs authentication support
- `packages/adapter-mssql/README.md` — adapter documentation that should cover the new authentication options
