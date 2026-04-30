# Support Entra ID Authentication in MSSQL Adapter Connection Strings

## Problem

The `@prisma/adapter-mssql` package supports connecting to SQL Server via a config object or a connection string. While the underlying `mssql`/`tedious` driver supports Azure Entra ID (formerly Azure Active Directory) authentication via the config object, the `parseConnectionString` function in `packages/adapter-mssql/src/connection-string.ts` does not recognize authentication parameters in connection strings.

This means users who want to use Entra ID authentication cannot do so through a connection string — they must use the config object approach.

## Expected Behavior

The connection string parser should support an `authentication` parameter that maps to the appropriate tedious authentication types. The returned config object must have an `authentication.type` string and an `authentication.options` object with specific keys depending on the auth method.

### Authentication Type Mappings

| Connection String Value | tedious `authentication.type` | Required Options |
|---|---|---|
| `DefaultAzureCredential` | `azure-active-directory-default` | (none) |
| `ActiveDirectoryPassword` | `azure-active-directory-password` | `userName`, `password`, `clientId` |
| `ActiveDirectoryServicePrincipal` | `azure-active-directory-service-principal-secret` | `userName` → `clientId`, `password` → `clientSecret` |
| `ActiveDirectoryManagedIdentity` | `azure-active-directory-msi-app-service` | `clientId`, `msiEndpoint`, `msiSecret` |

The parser should throw a descriptive error when `ActiveDirectoryPassword` is missing `clientId`.

The parser should throw a descriptive error when duplicate parameters (e.g., `database` specified twice) appear in the connection string.

Existing connection string parameters (`server`, `port`, `database`, `user`, `password`, `encrypt`, `trustServerCertificate`, `connectionLimit`, `poolTimeout`, `connectTimeout`, `loginTimeout`, `socketTimeout`, `applicationName`, `isolationLevel`) must continue to work as before.

## Config Object Schema

When authentication is parsed, the result must conform to this schema:

```
{
  server: string,
  port: number,
  database: string,
  user?: string,
  password?: string,
  options?: {
    encrypt?: boolean,
    trustServerCertificate?: boolean,
    appName?: string,
    isolationLevel?: number,
    ...
  },
  authentication?: {
    type: string,        // one of the tedious type strings above
    options?: {
      userName?: string,
      password?: string,
      clientId?: string,
      clientSecret?: string,
      msiEndpoint?: string,
      msiSecret?: string
    }
  },
  pool?: {
    max?: number,
    acquireTimeoutMillis?: number
  },
  connectionTimeout?: number,
  requestTimeout?: number
}
```

## Files to Look At

- `packages/adapter-mssql/src/connection-string.ts` — the connection string parser that needs authentication support
- `packages/adapter-mssql/README.md` — adapter documentation that should cover the new authentication options

## Requirements

1. Update `connection-string.ts` to parse the `authentication` parameter and its associated options (`userName`, `password`, `clientId`, `msiEndpoint`, `msiSecret`) from connection strings
2. Map each `authentication` value to the correct tedious `authentication.type` string as specified in the table above
3. Validate that required options are present for each authentication type; throw descriptive errors otherwise
4. Detect and reject duplicate connection string parameters with a descriptive error
5. Update the README to document Entra ID authentication options and connection string usage (include `sqlserver://` example and `PrismaMssql` constructor example)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
