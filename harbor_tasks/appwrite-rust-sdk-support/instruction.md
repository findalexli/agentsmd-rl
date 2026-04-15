# Task: Add Rust SDK Support

## Problem

Appwrite currently supports multiple SDKs for different programming languages, but Rust SDK support is missing. You need to add Rust as a supported server-side SDK platform.

## What You Need to Do

### 1. Add Rust SDK configuration to `app/config/sdks.php`

Add a new SDK entry for Rust in the server platform section with the following **exact field names and values**:

**Complete Rust SDK array structure:**
```php
[
    'key' => 'rust',
    'name' => 'Rust',
    'version' => '0.1.0',
    'url' => 'https://github.com/appwrite/sdk-for-rust',
    'package' => 'https://crates.io/crates/appwrite',
    'enabled' => true,
    'beta' => true,
    'dev' => true,
    'hidden' => false,
    'family' => APP_SDK_PLATFORM_SERVER,
    'prism' => 'rust',
    'source' => \realpath(__DIR__ . '/../sdks/server-rust'),
    'gitUrl' => 'git@github.com:appwrite/sdk-for-rust.git',
    'gitRepoName' => 'sdk-for-rust',
    'gitUserName' => 'appwrite',
    'gitBranch' => 'dev',
    'changelog' => \realpath(__DIR__ . '/../../docs/sdks/rust/CHANGELOG.md'),
],
```

**Position requirement:** The Rust SDK entry must be placed **after the Kotlin SDK entry and before the GraphQL SDK entry** in the server platform array.

### 2. Wire up the Rust language class in `src/Appwrite/Platform/Tasks/SDKs.php`

Add the following import statement with the other language imports (alphabetically ordered between Ruby and Swift):
```php
use Appwrite\SDK\Language\Rust;
```

Add a switch case for Rust **after the Kotlin case and before the GraphQL case**:
```php
case 'rust':
    $config = new Rust();
    break;
```

## Files to Modify

- `app/config/sdks.php` - Add the complete Rust SDK configuration array with all fields listed above
- `src/Appwrite/Platform/Tasks/SDKs.php` - Add the import and switch case as specified

## Verification

Your solution will be tested by:
1. Checking that Rust SDK configuration exists with all required fields and exact values
2. Verifying the Rust language class is properly imported with `use Appwrite\SDK\Language\Rust;`
3. Confirming the Rust switch case exists with `case 'rust':` and `$config = new Rust();`
4. Validating PHP syntax is valid
5. Validating the Rust SDK entry is positioned after Kotlin and before GraphQL
6. Validating the Rust switch case is positioned after Kotlin and before GraphQL
