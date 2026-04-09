# Sui External Keystore File Creation Bug

## Problem Description

The Sui CLI has an issue with external keystore file handling. When `external_keys` is configured in `client.yaml` but the corresponding external keystore files (`external.keystore` and `external.aliases`) don't exist on disk, the system fails rather than creating them automatically.

## Expected Behavior

When external keys are configured or when a user runs external-keys commands, the system should:
1. Automatically create `external.keystore` and `external.aliases` files if they don't exist
2. Initialize them with empty but valid JSON content (`{}`)
3. Ensure the `client.yaml` config has the `external_keys` field set appropriately

## Files to Modify

### 1. `crates/sui-keys/src/external.rs`

The `External::load_or_create()` method currently only loads existing files but doesn't actually create them when missing. You need to modify this method to:
- Track whether the aliases and keystore files exist before attempting to read them
- After initializing empty BTreeMaps for missing files, write those empty maps back to disk
- Use proper error handling with context messages

Key areas to look at:
- The `load_or_create` function around line 132
- The aliases file creation (with `.aliases` extension)
- The keystore file creation

### 2. `crates/sui/src/sui_commands.rs`

Several changes are needed here:

1. **Add import**: Import `External` from `sui_keys::keystore` module

2. **Add helper functions**:
   - `default_external_keystore_path(client_path: &Path) -> PathBuf`: Returns the path for external keystore based on client.yaml location
   - `ensure_external_keystore_config(config, client_path)`: Checks if `config.external_keys` is `None` and if so, creates it using `External::load_or_create()` and saves the config

3. **Modify `prompt_if_no_config`**: Update the default config creation to initialize `external_keys` with a proper `External` keystore instead of `None`

4. **Modify external-keys command handler**: Update the command execution to:
   - Call `prompt_if_no_config` if needed
   - Call `ensure_external_keystore_config` before executing external key commands
   - Save the config after ensuring external keystore is set up

## Testing Your Changes

After making changes:

1. Verify compilation: `cargo check -p sui-keys` and `cargo check -p sui`
2. Run the specific test: `cargo test -p sui-keys --lib -- test_load_or_create_creates_external_files`
3. Run all sui-keys tests: `SUI_SKIP_SIMTESTS=1 cargo nextest run -p sui-keys --lib`

## Constraints

- Do NOT modify existing test files (they have snapshot expectations)
- Do NOT change the public API signatures of existing functions
- New functions can be added with appropriate visibility
- Ensure proper error handling with context messages using `anyhow`
- Follow existing code style and patterns in the repository
