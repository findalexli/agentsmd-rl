# Add Rust SDK Support to Appwrite

## Problem

Appwrite's SDK generation system currently lacks support for Rust. When the SDK generation task runs, Rust is not recognized as a valid server-side SDK platform, causing the generation to fail for Rust.

## What You Need to Do

The SDK generation system must be extended to support Rust as a server-side SDK platform. This requires adding Rust SDK configuration and language handling.

### Rust SDK Configuration

The Rust SDK must be registered in the SDK configuration with these properties:

| Property | Value |
|----------|-------|
| key | `rust` |
| name | `Rust` |
| version | `0.1.0` |
| url | `https://github.com/appwrite/sdk-for-rust` |
| package | `https://crates.io/crates/appwrite` |
| enabled | `true` |
| beta | `true` |
| dev | `true` |
| hidden | `false` |
| family | `APP_SDK_PLATFORM_SERVER` |
| prism | `rust` |
| source | `../sdks/server-rust` (relative path) |
| gitUrl | `git@github.com:appwrite/sdk-for-rust.git` |
| gitRepoName | `sdk-for-rust` |
| gitUserName | `appwrite` |
| gitBranch | `dev` |
| changelog | `../../docs/sdks/rust/CHANGELOG.md` (relative path) |

### SDK Language Handler

The SDK generation task must be able to handle Rust code generation. This requires:
- A Rust language class exists in the SDK language registry
- The SDK generation task recognizes the `rust` platform

## Files to Examine

- `app/config/sdks.php` — SDK registry configuration
- `src/Appwrite/Platform/Tasks/SDKs.php` — SDK generation task handler

## Verification

Your solution will be validated by:
1. Confirming Rust SDK configuration exists with all required fields
2. Verifying the Rust language handling exists in the SDK generation task
3. Checking PHP syntax validity
4. Verifying correct ordering (Rust after Kotlin, before GraphQL)
5. Running code style and static analysis checks
