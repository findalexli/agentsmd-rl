# Add Rust SDK Support to Appwrite

## Problem

Appwrite's SDK generation system supports many server-side languages (Python, Ruby, PHP, Swift, Kotlin, and others) but does not yet support Rust. When Rust SDK generation is requested, the system fails because Rust is not recognized as a valid SDK platform and no language handler exists for it.

## Requirements

### SDK Registration

Register Rust as a new server-side SDK in Appwrite's configuration. The Rust SDK has these characteristics:

- It is a **server-side** SDK, belonging to the same platform family as Kotlin, Swift, and Python. The family must be set using the `APP_SDK_PLATFORM_SERVER` constant (not a string literal).
- Version: `0.1.0` (initial release)
- The SDK is **enabled**, currently in **beta**, and in **dev** status (all three flags set to `true`)
- The GitHub repository is `appwrite/sdk-for-rust` (URL: `https://github.com/appwrite/sdk-for-rust`)
- The package is published on crates.io at `https://crates.io/crates/appwrite`
- The configuration entry must include **all** standard SDK fields that other server SDKs use: `key`, `name`, `version`, `url`, `package`, `enabled`, `beta`, `dev`, `family`, `prism`, `source`, `gitUrl`, `gitRepoName`, `gitUserName`, `gitBranch`, and `changelog`. Follow the conventions of existing server-side SDK entries (such as Kotlin or Swift) for values like `gitUrl`, `gitRepoName`, `gitUserName`, `gitBranch`, `source`, and `changelog`.

### Language Handling

The SDK generation logic must recognize the `'rust'` platform key and instantiate the corresponding `Rust` language class from the SDK language library (`Appwrite\SDK\Language\Rust`). Ensure the class is properly imported.

### Ordering

Rust must be positioned **after Kotlin and before GraphQL** in both the SDK configuration list and the language handling logic.

### Code Quality

All changes must pass the project's existing CI checks:

- PHP syntax validation (`php -l`)
- PSR-12 code style compliance via Laravel Pint (using the project's `pint.json` configuration)
- Static analysis via PHPStan (using the project's `phpstan.neon` configuration)
- `composer validate` and `composer dump-autoload` must succeed
