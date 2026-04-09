# Task: Add Rust SDK Support

## Problem

Appwrite currently supports multiple SDKs for different programming languages, but Rust SDK support is missing. You need to add Rust as a supported server-side SDK platform.

## What You Need to Do

1. **Add Rust SDK configuration** to `app/config/sdks.php`
   - Add a new SDK entry for Rust in the server platform array
   - The entry should include: key, name, version (0.1.0), URLs, git info, and feature flags
   - Rust should be marked as: enabled=true, beta=true, dev=true
   - Platform family should be the server platform constant

2. **Wire up the Rust language class** in `src/Appwrite/Platform/Tasks/SDKs.php`
   - Import the Rust language class from the SDK namespace
   - Add a case for 'rust' in the switch statement that creates the language config
   - Position it appropriately among other language cases

## Files to Modify

- `app/config/sdks.php` - Add Rust SDK configuration array
- `src/Appwrite/Platform/Tasks/SDKs.php` - Add import and switch case

## Hints

- Look at existing SDK entries (like Kotlin or Swift) to understand the configuration structure
- The Rust language class is `Appwrite\SDK\Language\Rust`
- The SDK generator repository is at `github.com/appwrite/sdk-for-rust`
- The package will be published to `crates.io/crates/appwrite`
- Look at how other languages are structured in the switch statement

## Verification

Your solution will be tested by:
1. Checking that Rust SDK configuration exists with all required fields
2. Verifying the Rust language class is properly imported and wired up
3. Confirming PHP syntax is valid
4. Validating the switch case is in the correct position
