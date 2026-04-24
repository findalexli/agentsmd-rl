# Add Rust SDK Support to Appwrite

## Problem

Appwrite's SDK generation system supports many server-side languages (Python, Ruby, PHP, Swift, Kotlin, and others) but does not yet support Rust. When Rust SDK generation is requested, the system fails because Rust is not recognized as a valid SDK platform and no language handler exists for it.

## Requirements

### SDK Registration

Add Rust as a new server-side SDK to Appwrite's SDK configuration. The Rust SDK entry must have:

- **Platform family**: Rust is a server-side SDK (same family as Kotlin, Swift, and Python). Use the `APP_SDK_PLATFORM_SERVER` constant for the family field.
- **Version**: `0.1.0` (initial release)
- **Status flags**: The SDK is **enabled**, in **beta**, and in **dev** mode (all three boolean flags set to `true`)
- **Repository**: GitHub URL pointing to `appwrite/sdk-for-rust`
- **Package registry**: crates.io package URL at `https://crates.io/crates/appwrite`
- **Configuration fields**: All standard fields that other server SDKs include (key, name, version, url, package, enabled, beta, dev, family, prism, source, gitUrl, gitRepoName, gitUserName, gitBranch, changelog). Mirror the pattern used by similar server-side SDKs for values like gitUrl, gitRepoName, gitUserName, gitBranch, source, and changelog.

### Language Handling

The SDK generation logic needs a case for the `'rust'` platform key that instantiates the corresponding Rust language class from the SDK language library. The class must be imported in the file where SDK generation is handled.

### Code Quality

All changes must pass the project's existing CI checks:

- PHP syntax validation (`php -l`)
- PSR-12 code style compliance via Laravel Pint (using the project's `pint.json` configuration)
- Static analysis via PHPStan (using the project's `phpstan.neon` configuration)
- `composer validate` and `composer dump-autoload` must succeed
