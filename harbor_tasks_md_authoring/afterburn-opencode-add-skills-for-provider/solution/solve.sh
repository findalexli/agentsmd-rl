#!/usr/bin/env bash
set -euo pipefail

cd /workspace/afterburn

# Idempotency guard
if grep -qF "**For config drive providers**, use the ProxmoxVE provider (`src/providers/proxm" ".opencode/skills/add-provider/SKILL.md" && grep -qF "Some release notes entries may already exist (contributors often add entries whe" ".opencode/skills/prepare-release/SKILL.md" && grep -qF "This is a multi-phase, interactive workflow. The skill runs what it can automati" ".opencode/skills/publish-release/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.opencode/skills/add-provider/SKILL.md b/.opencode/skills/add-provider/SKILL.md
@@ -0,0 +1,351 @@
+---
+name: add-provider
+description: Scaffold a new cloud/platform provider for Afterburn with all required files, wiring, docs, and tests
+---
+
+# Add Provider
+
+Scaffold a new cloud/platform provider for the Afterburn metadata agent, including the Rust implementation, mock tests, documentation, and systemd/dracut service entries.
+
+## What it does
+
+1. Gathers provider details from the user (name, metadata source, features, attributes)
+2. Creates the provider Rust module (`src/providers/{name}/mod.rs`)
+3. Creates mock tests (`src/providers/{name}/mock_tests.rs`)
+4. Wires the provider into the module tree and dispatch table
+5. Updates all documentation files (platforms, attributes, release notes)
+6. Updates systemd/dracut service files based on supported features
+7. Verifies the build compiles, tests pass, and lints are clean
+
+## Prerequisites
+
+- Rust toolchain installed (`cargo`, `rustfmt`, `clippy`)
+- The repository builds successfully before starting (`cargo build --all-targets`)
+
+## Usage
+
+```bash
+/add-provider
+/add-provider --name linode
+/add-provider --name cherry --type imds
+```
+
+## Workflow
+
+### Step 1: Gather Provider Information
+
+Ask the user for the following information. If any arguments were provided via the command, use those instead of asking.
+
+Use the question tool to ask:
+
+**Question 1: Provider name**
+- What is the platform ID for this provider? (lowercase, no spaces, e.g., `linode`, `cherry`, `vultr`)
+- This will be used as the directory name under `src/providers/` and the match arm in `fetch_metadata()`
+
+**Question 2: Provider struct name**
+- What should the Rust struct be named? (e.g., `LinodeProvider`, `CherryProvider`)
+- Default: derive from provider name by capitalizing and appending `Provider`
+
+**Question 3: Metadata source type**
+- Is this an IMDS (HTTP metadata service) or config drive (mounted filesystem) provider?
+- Options: `imds`, `configdrive`
+
+**Question 4 (if IMDS): Base URL**
+- What is the metadata service base URL?
+- Common pattern: `http://169.254.169.254/metadata/v1`
+
+**Question 5 (if IMDS): Authentication**
+- What authentication method does the metadata service use?
+- Options: `none`, `token-header` (static header like OracleCloud's `Bearer Oracle`), `imdsv2` (token exchange like AWS)
+
+**Question 6: Supported features**
+- Which features does this provider support? (multi-select)
+- Options: `attributes` (always), `ssh-keys`, `hostname`, `boot-checkin`, `network-config`
+
+**Question 7: Attributes**
+- What attributes does this provider expose?
+- For each attribute, ask: attribute name (e.g., `HOSTNAME`, `INSTANCE_ID`, `REGION`) and the metadata endpoint/path to fetch it from
+- Attribute names will be prefixed with `AFTERBURN_{UPPER_PROVIDER_NAME}_`
+
+### Step 2: Validate Inputs
+
+Before creating any files, verify:
+
+1. Read `src/providers/mod.rs` and confirm no `pub mod {name};` exists
+2. Read `src/metadata.rs` and confirm no `"{name}"` match arm exists in `fetch_metadata()`
+3. Confirm no directory exists at `src/providers/{name}/`
+
+If any conflict is found, report the conflict and stop.
+
+### Step 3: Create Provider Module
+
+Create `src/providers/{name}/mod.rs`.
+
+**For IMDS providers**, use the UpCloud provider (`src/providers/upcloud/mod.rs`) as the primary reference. Key patterns:
+
+```rust
+// Structure:
+// 1. Apache 2.0 license header
+// 2. Module doc comment with platform ID and metadata docs URL
+// 3. Imports: anyhow::Result, openssh_keys::PublicKey, slog_scope::error, std::collections::HashMap
+// 4. Import crate::providers::MetadataProvider and crate::retry
+// 5. #[cfg(test)] mod mock_tests;
+// 6. Provider struct with retry::Client field
+// 7. impl block with try_new(), endpoint_for(), and helper methods
+// 8. impl MetadataProvider with attributes(), hostname(), ssh_keys()
+```
+
+Key rules:
+- The `endpoint_for()` helper constructs the full URL from base URL + endpoint name
+- Use `retry::Raw` for plain text endpoints, `retry::Json` for JSON endpoints
+- For providers with auth headers, use `.header()` on the request builder
+- SSH keys: iterate lines, parse each with `PublicKey::parse()`, log errors with `slog_scope::error!`
+- Hostname: return `Ok(None)` if empty or missing, `Ok(Some(hostname))` otherwise
+- Attributes: use `HashMap::with_capacity(N)` where N is the number of attributes
+
+**For config drive providers**, use the ProxmoxVE provider (`src/providers/proxmoxve/`) as reference. These are more complex and variable -- adapt based on the specific config drive format.
+
+### Step 4: Create Mock Tests
+
+Create `src/providers/{name}/mock_tests.rs`.
+
+Use the UpCloud mock tests (`src/providers/upcloud/mock_tests.rs`) as the primary reference. Every provider should have at minimum:
+
+1. **`test_hostname()`** (if hostname supported):
+   - Test successful fetch (200 with body)
+   - Test 404 returns `None`
+   - Test empty body returns `None`
+   - Test 503 returns error
+   - Test connection error (server reset) returns error
+
+2. **`test_pubkeys()`** (if SSH keys supported):
+   - Test with 2 SSH keys
+   - Verify key count and comment fields
+   - Test connection error returns error
+
+3. **`test_attributes()`**:
+   - Mock all attribute endpoints with test values
+   - Verify all attributes are returned with correct keys
+   - Test connection error returns error
+
+Use `mockito::Server` for all HTTP mocking. Create the provider with `try_new().unwrap()` and override the client:
+```rust
+provider.client = provider.client.max_retries(0).mock_base_url(server.url());
+```
+
+### Step 5: Wire into Module Tree
+
+Edit `src/providers/mod.rs`:
+- Add `pub mod {name};` in **alphabetical order** among the existing module declarations
+
+### Step 6: Register in Metadata Dispatch
+
+Edit `src/metadata.rs`:
+- Add `use crate::providers::{name}::{ProviderStruct};` in the import block (alphabetical order)
+- Add match arm `"{platform_id}" => box_result!({ProviderStruct}::try_new()?),` in `fetch_metadata()` (alphabetical order)
+
+### Step 7: Update Documentation
+
+#### 7a. `docs/platforms.md`
+Add entry in **alphabetical order** among the platform list:
+```markdown
+* {platform_id}
+  - Attributes
+  - Hostname        (if supported)
+  - SSH Keys        (if supported)
+  - Boot check-in   (if supported)
+  - Network configuration (if supported)
+```
+
+#### 7b. `docs/usage/attributes.md`
+Add entry in **alphabetical order** with all attributes:
+```markdown
+* {platform_id}
+  - AFTERBURN_{UPPER_NAME}_ATTRIBUTE_1
+  - AFTERBURN_{UPPER_NAME}_ATTRIBUTE_2
+  ...
+```
+
+#### 7c. `docs/release-notes.md`
+Add under "Major changes:":
+```markdown
+- Add support for {Provider Display Name}
+```
+
+### Step 8: Update Service Files
+
+Based on supported features, add `ConditionKernelCommandLine=|ignition.platform.id={platform_id}` to the appropriate service files. Insert in **alphabetical order** among existing entries.
+
+#### 8a. SSH Keys (if supported)
+Edit `systemd/afterburn-sshkeys@.service.in`:
+```ini
+ConditionKernelCommandLine=|ignition.platform.id={platform_id}
+```
+
+#### 8b. Hostname (if supported)
+Edit `dracut/30afterburn/afterburn-hostname.service`:
+```ini
+ConditionKernelCommandLine=|ignition.platform.id={platform_id}
+```
+
+#### 8c. Boot Check-in (if supported)
+Edit `systemd/afterburn-checkin.service`:
+```ini
+ConditionKernelCommandLine=|ignition.platform.id={platform_id}
+```
+
+### Step 9: Verify
+
+Run the following commands sequentially and fix any issues:
+
+```bash
+cargo fmt
+cargo build --all-targets
+cargo test --all-targets
+cargo clippy --all-targets -- -D warnings
+```
+
+If any command fails:
+1. Read the error output carefully
+2. Fix the issue in the relevant file
+3. Re-run from the failing command
+
+### Step 10: Summary
+
+After all steps complete, present a summary:
+
+```
+Provider scaffold complete!
+
+Files created:
+  - src/providers/{name}/mod.rs
+  - src/providers/{name}/mock_tests.rs
+
+Files modified:
+  - src/providers/mod.rs
+  - src/metadata.rs
+  - docs/platforms.md
+  - docs/usage/attributes.md
+  - docs/release-notes.md
+  - systemd/afterburn-sshkeys@.service.in (if SSH keys)
+  - dracut/30afterburn/afterburn-hostname.service (if hostname)
+  - systemd/afterburn-checkin.service (if boot check-in)
+
+Verification:
+  - cargo build: PASS
+  - cargo test: PASS
+  - cargo clippy: PASS
+
+Next steps:
+  1. Fill in the actual metadata endpoint logic in mod.rs
+  2. Update mock tests with realistic test data
+  3. Run `cargo test` to verify
+  4. Submit a PR with commit message: "{name}: implement {name} provider"
+```
+
+## Checklist Coverage
+
+This skill automates the following from the contributor workflow:
+
+- [x] Create provider module with MetadataProvider trait implementation
+- [x] Create mock tests for hostname, SSH keys, and attributes
+- [x] Register module in `src/providers/mod.rs`
+- [x] Register provider in `src/metadata.rs` dispatch table
+- [x] Update `docs/platforms.md` with supported features
+- [x] Update `docs/usage/attributes.md` with attribute list
+- [x] Update `docs/release-notes.md` with release note
+- [x] Update `systemd/afterburn-sshkeys@.service.in` (if SSH keys supported)
+- [x] Update `dracut/30afterburn/afterburn-hostname.service` (if hostname supported)
+- [x] Update `systemd/afterburn-checkin.service` (if boot check-in supported)
+- [x] Run `cargo build`, `cargo test`, `cargo clippy`
+
+## What's NOT covered
+
+- Implementing the actual metadata fetching logic (provider-specific API calls, JSON parsing, etc.)
+- Creating test fixtures for config drive providers
+- Testing against a real cloud environment
+- The PR review and merge process
+- Release notes for subsequent releases
+
+## Example Output
+
+When you run `/add-provider`, the interaction looks like:
+
+```
+> /add-provider
+
+What is the platform ID? > mycloud
+What should the struct be named? > MyCloudProvider
+IMDS or config drive? > imds
+Base URL? > http://169.254.169.254/metadata/v1
+Authentication? > none
+Features? > attributes, ssh-keys, hostname
+Attributes? > HOSTNAME (hostname), INSTANCE_ID (instance_id), REGION (region)
+
+Creating provider scaffold...
+
+Created: src/providers/mycloud/mod.rs (124 lines)
+Created: src/providers/mycloud/mock_tests.rs (106 lines)
+Modified: src/providers/mod.rs (+1 line)
+Modified: src/metadata.rs (+2 lines)
+Modified: docs/platforms.md (+4 lines)
+Modified: docs/usage/attributes.md (+4 lines)
+Modified: docs/release-notes.md (+2 lines)
+Modified: systemd/afterburn-sshkeys@.service.in (+1 line)
+Modified: dracut/30afterburn/afterburn-hostname.service (+1 line)
+
+Running verification...
+  cargo fmt: PASS
+  cargo build: PASS
+  cargo test: PASS
+  cargo clippy: PASS
+
+Provider scaffold complete!
+```
+
+## Provider Architecture Variants
+
+There are two main architectural patterns. Read the referenced providers to match the right pattern:
+
+### Pattern A: IMDS (Instance Metadata Service)
+Used by: upcloud, oraclecloud, akamai, aws, gcp, digitalocean, exoscale, aliyun, hetzner, scaleway, vultr, packet
+- Fetches metadata via HTTP from a well-known IP (usually `169.254.169.254`)
+- May require token-based authentication (IMDSv2 style)
+- Uses `retry::Client` for HTTP requests
+- Provider struct holds the client (or pre-fetched data)
+
+### Pattern B: Config Drive
+Used by: proxmoxve, powervs, ibmcloud-classic, cloudstack-configdrive
+- Reads metadata from a mounted filesystem (ISO/config drive)
+- Parses JSON or YAML files from the mount point
+- May include network configuration
+- Often includes test fixtures in `tests/fixtures/{name}/`
+
+## Reference Examples
+
+### UpCloud (commit `c8cc721`) -- simplest IMDS pattern
+- 9 files, +245 lines
+- Plain text endpoints, no auth, `retry::Client` with `return_on_404(true)`
+- Fetches individual endpoints per attribute (`/metadata/v1/{attr}`)
+
+### OracleCloud (commit `d4f8031`) -- IMDS with JSON + auth
+- 8 files, +332 lines
+- Single JSON endpoint with `Authorization: Bearer Oracle` header
+- Serde deserialization with `#[serde(rename_all = "camelCase")]`
+- `try_new_with_client()` pattern for test injection
+
+### Akamai (commit `bacbf84`) -- IMDS with token auth, many attributes
+- 8 files, +411 lines
+- Token-based authentication, 13 attributes
+- No hostname service entry
+
+### ProxmoxVE (commit `a92c78d`) -- config drive with network config
+- 27 files, +707 lines
+- Reads from mounted filesystem, YAML parsing
+- Includes test fixtures in `tests/fixtures/proxmoxve/`
+
+## References
+
+- Provider trait: `src/providers/mod.rs:190` (`MetadataProvider` trait)
+- Dispatch table: `src/metadata.rs:54` (`fetch_metadata()` function)
+- Contributing guide: `docs/contributing.md`
diff --git a/.opencode/skills/prepare-release/SKILL.md b/.opencode/skills/prepare-release/SKILL.md
@@ -0,0 +1,312 @@
+---
+name: prepare-release
+description: Create the pre-release PR with dependency updates and drafted release notes
+---
+
+# Prepare Release
+
+Automate the pre-release PR for an Afterburn release: create branch, update dependencies, draft release notes from commit history, and open the PR.
+
+## What it does
+
+1. Creates the `pre-release-X.Y.Z` branch from up-to-date `main`
+2. Checks `Cargo.toml` for unintended lower bound changes since the last tag
+3. Runs `cargo update` and commits with message `cargo: update dependencies`
+4. Analyzes commits since the last tag to draft release notes
+5. Updates `docs/release-notes.md` with the drafted notes and commits with message `docs/release-notes: update for release X.Y.Z`
+6. Pushes the branch and opens a PR
+
+## Prerequisites
+
+- On the `main` branch, up to date with the upstream remote
+- `cargo` installed
+- `gh` CLI installed and authenticated (for opening the PR)
+- Write access to the repository
+
+## Usage
+
+```bash
+/prepare-release 5.11.0
+/prepare-release 5.11.0 --next 5.12.0
+```
+
+## Workflow
+
+### Step 1: Gather Version Information
+
+Get the release version from the user's command arguments. If not provided, ask:
+
+```
+What version are you releasing? (e.g., 5.11.0)
+```
+
+Determine the next development version:
+- If `--next` was provided, use that
+- Otherwise, auto-increment the minor version (e.g., `5.11.0` -> `5.12.0`)
+
+### Step 2: Validate Prerequisites
+
+Run these checks and stop if any fail:
+
+```bash
+# Verify we're on main
+git branch --show-current
+# Should output: main
+
+# Verify main is up to date
+git fetch origin
+git status
+# Should show "Your branch is up to date with 'origin/main'"
+
+# Verify no existing branch
+git branch --list "pre-release-${RELEASE_VER}"
+# Should be empty
+
+# Verify no existing tag
+git tag --list "v${RELEASE_VER}"
+# Should be empty
+
+# Get the last tag for reference
+git describe --abbrev=0
+```
+
+If `main` is behind, run `git pull origin main` first.
+
+If a branch or tag already exists, warn the user and stop.
+
+### Step 3: Create Pre-Release Branch
+
+```bash
+git checkout -b pre-release-${RELEASE_VER}
+```
+
+### Step 4: Check Cargo.toml Lower Bounds
+
+```bash
+git diff $(git describe --abbrev=0) Cargo.toml
+```
+
+If there are changes to dependency version lower bounds, present them to the user:
+
+```
+The following Cargo.toml changes were detected since the last release.
+Please review for unintended lower bound increases:
+
+{diff output}
+
+Continue? (y/n)
+```
+
+Use the question tool to ask the user to confirm. If the user wants to stop, provide instructions for cleaning up the branch.
+
+### Step 5: Update Dependencies
+
+```bash
+cargo update
+git add Cargo.lock
+git commit -m "cargo: update dependencies"
+```
+
+### Step 6: Analyze Commits for Release Notes
+
+Get all commits since the last tag, excluding noise:
+
+```bash
+# Get the last tag
+LAST_TAG=$(git describe --abbrev=0)
+
+# Get commits since last tag, excluding merges
+git log ${LAST_TAG}..HEAD --oneline --no-merges
+```
+
+Classify each commit into categories. Use these rules:
+
+**EXCLUDE these commits (do not include in release notes):**
+- Commits starting with `build(deps):` (Dependabot bumps)
+- Commits starting with `Sync repo templates` (automated)
+- Commits starting with `cargo: update dependencies` (the one we just made)
+- Commits starting with `cargo: Afterburn release` (release machinery)
+- Commits starting with `docs/release-notes:` (release notes updates)
+- Any merge commits
+
+**MAJOR changes (new features, new providers, significant changes):**
+- New provider implementations (commits mentioning "implement" + "provider", or "Add support for")
+- Major new feature areas (network config, new platform support)
+- Significant architectural changes or refactors
+
+**MINOR changes (bug fixes, small improvements):**
+- Bug fixes to existing providers
+- Small feature additions (new attributes, config tweaks)
+- Documentation changes
+- Test additions/improvements
+- Build/CI fixes
+- Dracut/systemd service changes
+
+**PACKAGING changes:**
+- Rust version requirement changes (check if `rust-version` changed in Cargo.toml)
+- Dependency requirement changes (not routine bumps, but actual new deps or removed deps)
+- Build system changes
+
+### Step 7: Draft Release Notes
+
+Read the current `docs/release-notes.md` file. The top section will look like:
+
+```markdown
+## Upcoming Afterburn X.Y.Z (unreleased)
+
+Major changes:
+
+- {existing items that were added incrementally}
+
+Minor changes:
+
+- {existing items}
+
+Packaging changes:
+
+{existing items}
+```
+
+Some release notes entries may already exist (contributors often add entries when they merge features). Preserve those and add any missing ones from the commit analysis.
+
+Present the drafted release notes to the user for review:
+
+```
+Here are the drafted release notes for Afterburn ${RELEASE_VER}:
+
+## Afterburn ${RELEASE_VER}
+
+Major changes:
+
+- {items}
+
+Minor changes:
+
+- {items}
+
+Packaging changes:
+
+- {items}
+
+Does this look correct? You can edit or I can proceed.
+```
+
+Use the question tool to ask the user to confirm or request changes.
+
+### Step 8: Update Release Notes File
+
+Edit `docs/release-notes.md` to:
+
+1. **Replace** the `## Upcoming Afterburn X.Y.Z (unreleased)` header with `## Afterburn ${RELEASE_VER}`
+2. **Prepend** a new upcoming section before it:
+
+```markdown
+## Upcoming Afterburn ${NEXT_VER} (unreleased)
+
+Major changes:
+
+Minor changes:
+
+Packaging changes:
+
+```
+
+3. Clean up any empty sections from the now-current release (remove "Packaging changes:" if it has no items under it, etc.)
+
+Then commit:
+
+```bash
+git add docs/release-notes.md
+git commit -m "docs/release-notes: update for release ${RELEASE_VER}"
+```
+
+### Step 9: Push and Open PR
+
+```bash
+git push origin pre-release-${RELEASE_VER}
+```
+
+Open a PR:
+
+```bash
+gh pr create \
+  --title "pre-release ${RELEASE_VER}" \
+  --body "$(cat <<'EOF'
+Pre-release PR for Afterburn ${RELEASE_VER}.
+
+This PR contains:
+1. `cargo: update dependencies` - Updated Cargo.lock
+2. `docs/release-notes: update for release ${RELEASE_VER}` - Release notes
+
+Please review and merge. After merging, continue with the release checklist.
+EOF
+)"
+```
+
+### Step 10: Summary
+
+```
+Pre-release PR created!
+
+Branch: pre-release-${RELEASE_VER}
+Commits:
+  1. cargo: update dependencies
+  2. docs/release-notes: update for release ${RELEASE_VER}
+
+PR: {PR_URL}
+
+Next steps (from the release checklist):
+  1. Get PR reviewed and merged
+  2. Run /publish-release ${RELEASE_VER} to continue with the release
+```
+
+## Checklist Coverage
+
+From the release checklist in `.github/ISSUE_TEMPLATE/release-checklist.md`:
+
+- [x] `RELEASE_VER=x.y.z` -- captured as input
+- [x] `git checkout -b pre-release-${RELEASE_VER}` -- Step 3
+- [x] `git diff $(git describe --abbrev=0) Cargo.toml` -- Step 4
+- [x] `cargo update` -- Step 5
+- [x] `git add Cargo.lock && git commit` -- Step 5
+- [x] Write release notes -- Steps 6-8
+- [x] `git add docs/release-notes.md && git commit` -- Step 8
+- [x] PR the changes -- Step 9
+
+## What's NOT covered
+
+- Reviewing the actual dependency changes in `Cargo.lock`
+- Branched releases (cherry-picking release notes into main)
+- Final approval/merge of the PR
+
+## Worked Examples
+
+### Release 5.10.0
+Commits between v5.9.0 and pre-release (excluding noise):
+```
+e469d05 providers/azure: switch SSH key retrieval from certs endpoint to IMDS
+96c5530 microsoft/azure: Fix SharedConfig parsing of XML attributes
+627089c microsoft/azure: Add XML attribute alias for serde-xml-rs Fedora compat
+c8cc721 upcloud: implement UpCloud provider
+```
+Resulting release notes:
+- Major: "Add support for UpCloud"
+- Minor: "Azure: fetch SSH keys from IMDS instead of deprecated certificates endpoint", "Azure: fix parsing of SharedConfig XML document with current serde-xml-rs"
+
+### Release 5.9.0
+Key commits:
+```
+d4f8031 oraclecloud: implement oraclecloud provider
+62d9ce2 dracut: Return 255 in module-setup
+5f3dca0 Add TMT test structure and basic smoke test
+```
+Resulting release notes:
+- Major: "Add support for Oracle Cloud Infrastructure", "dracut: don't include module by default"
+- Minor: "Add TMT test structure and basic smoke test"
+
+## References
+
+- Full release checklist: `.github/ISSUE_TEMPLATE/release-checklist.md`
+- Release notes format: `docs/release-notes.md`
+- Example pre-release PRs: #1223 (5.9.0), #1205 (5.8.2), #1199 (5.8.0)
+- Commit message convention: `docs/contributing.md:48-69`
diff --git a/.opencode/skills/publish-release/SKILL.md b/.opencode/skills/publish-release/SKILL.md
@@ -0,0 +1,351 @@
+---
+name: publish-release
+description: Guide the post-merge release process - release branch, tag, vendor archive, and GitHub release
+---
+
+# Publish Release
+
+Guide the post-merge release process for Afterburn. This skill runs automatable steps directly and prompts the user for steps requiring credentials (GPG signing, crates.io publishing).
+
+## What it does
+
+1. Verifies the pre-release PR has been merged
+2. Runs clean build verification with vendored dependencies
+3. Creates the release branch and guides user through `cargo release`
+4. Opens the release PR
+5. After merge, pushes the tag and guides user through `cargo publish`
+6. Creates the vendor archive with SHA256 digests
+7. Drafts the GitHub release body
+8. Cleans up local and remote branches
+
+## Prerequisites
+
+- The pre-release PR for this version must already be merged to `main`
+- `cargo-release` installed (`cargo install cargo-release`)
+- `cargo-vendor-filterer` installed (`cargo install cargo-vendor-filterer`)
+- GPG key configured for commit/tag signing
+- crates.io account with publish access
+- `gh` CLI installed and authenticated
+
+## Usage
+
+```bash
+/publish-release 5.11.0
+/publish-release 5.11.0 --remote origin
+```
+
+## Workflow
+
+This is a multi-phase, interactive workflow. The skill runs what it can automatically and prompts the user at credential-gated steps. Track progress with a checklist displayed after each phase.
+
+### Step 1: Gather Inputs
+
+Get the release version from arguments. If not provided, ask the user.
+
+Set `UPSTREAM_REMOTE` from `--remote` flag, defaulting to `origin`.
+
+### Step 2: Verify Prerequisites
+
+Run these checks:
+
+```bash
+# Verify cargo-release is installed
+cargo release --version
+
+# Verify cargo-vendor-filterer is installed
+cargo vendor-filterer --help 2>&1 | head -1
+```
+
+If either is missing, offer to install:
+
+```bash
+cargo install cargo-release cargo-vendor-filterer
+```
+
+Then verify the pre-release was merged:
+
+```bash
+# Pull latest main
+git checkout main
+git pull ${UPSTREAM_REMOTE} main
+
+# Verify the dependency update commit exists
+git log --oneline -5
+# Should contain "cargo: update dependencies" and "docs/release-notes: update for release X.Y.Z"
+```
+
+If the pre-release commits are not found, warn the user and stop. They need to run `/prepare-release` first.
+
+### Step 3: Clean Build Verification
+
+Display: "**Phase 1: Clean Build Verification**"
+
+Run these commands sequentially:
+
+```bash
+cargo vendor-filterer target/vendor
+```
+
+```bash
+cargo test --all-features --config 'source.crates-io.replace-with="vv"' --config 'source.vv.directory="target/vendor"'
+```
+
+```bash
+cargo clean
+git clean -fd
+```
+
+If any step fails, report the error and stop. The build must be clean before proceeding.
+
+### Step 4: Create Release Branch
+
+Display: "**Phase 2: Create Release Commit and Tag**"
+
+```bash
+git checkout -b release-${RELEASE_VER}
+```
+
+Now instruct the user to run `cargo release` manually, because it requires GPG signing and interactive confirmation:
+
+```
+Please run the following command in your terminal:
+
+    cargo release --execute ${RELEASE_VER}
+
+This will:
+- Update version in Cargo.toml to ${RELEASE_VER}
+- Create a signed commit: "cargo: Afterburn release ${RELEASE_VER}"
+- Create a signed tag: v${RELEASE_VER}
+
+Confirm the version when prompted. Let me know when it completes.
+```
+
+Use the question tool to ask the user if it completed successfully.
+
+After confirmation, verify:
+
+```bash
+# Verify the commit exists
+git log --oneline -1
+# Should show "cargo: Afterburn release X.Y.Z"
+
+# Verify Cargo.toml version
+grep "^version = \"${RELEASE_VER}\"$" Cargo.toml
+
+# Verify tag exists
+git tag --list "v${RELEASE_VER}"
+```
+
+If verification fails, report what went wrong.
+
+### Step 5: Push and Open Release PR
+
+Display: "**Phase 3: Release PR**"
+
+```bash
+git push ${UPSTREAM_REMOTE} release-${RELEASE_VER}
+```
+
+Open the PR:
+
+```bash
+gh pr create \
+  --title "Release ${RELEASE_VER}" \
+  --body "$(cat <<'EOF'
+Release PR for Afterburn ${RELEASE_VER}.
+
+This PR should contain exactly one commit updating the version in Cargo.toml.
+EOF
+)"
+```
+
+Verify the PR has exactly one commit:
+
+```bash
+git log main..release-${RELEASE_VER} --oneline
+```
+
+Tell the user:
+
+```
+Release PR opened: {PR_URL}
+
+Please:
+1. Verify the PR contains exactly one commit
+2. Get it reviewed and approved
+3. Merge the PR
+4. Come back here to continue
+
+Let me know when the PR is merged.
+```
+
+Use the question tool to wait for the user.
+
+### Step 6: Publish Tag
+
+Display: "**Phase 4: Publish Artifacts**"
+
+After user confirms PR is merged:
+
+```bash
+git checkout v${RELEASE_VER}
+```
+
+Verify version:
+
+```bash
+grep "^version = \"${RELEASE_VER}\"$" Cargo.toml
+```
+
+Push the tag:
+
+```bash
+git push ${UPSTREAM_REMOTE} v${RELEASE_VER}
+```
+
+Now instruct the user to publish to crates.io:
+
+```
+Please run the following command to publish to crates.io:
+
+    cargo publish
+
+This requires your crates.io authentication token.
+Let me know when it completes.
+```
+
+Use the question tool to wait for the user.
+
+### Step 7: Vendor Archive
+
+Display: "**Phase 5: Vendor Archive**"
+
+```bash
+cargo vendor-filterer --format=tar.gz --prefix=vendor target/afterburn-${RELEASE_VER}-vendor.tar.gz
+```
+
+Compute digests:
+
+```bash
+sha256sum target/package/afterburn-${RELEASE_VER}.crate
+sha256sum target/afterburn-${RELEASE_VER}-vendor.tar.gz
+```
+
+Store the digest values to include in the GitHub release.
+
+### Step 8: Draft GitHub Release
+
+Display: "**Phase 6: GitHub Release**"
+
+Read the release notes for this version from `docs/release-notes.md`. Extract the section between `## Afterburn ${RELEASE_VER}` and the next `## ` header.
+
+Present to the user:
+
+```
+Please create a GitHub release:
+
+1. Go to: https://github.com/coreos/afterburn/tags
+2. Find tag v${RELEASE_VER}, click the three-dot menu, and create a release
+3. Paste the following changelog:
+
+---
+{extracted release notes}
+---
+
+4. Upload: target/afterburn-${RELEASE_VER}-vendor.tar.gz
+
+5. Include these digests in the release description:
+
+    sha256sum afterburn-${RELEASE_VER}.crate: {digest}
+    sha256sum afterburn-${RELEASE_VER}-vendor.tar.gz: {digest}
+
+6. Publish the release
+
+Let me know when done.
+```
+
+Use the question tool to wait for the user.
+
+### Step 9: Cleanup
+
+Display: "**Phase 7: Cleanup**"
+
+```bash
+cargo clean
+git checkout main
+git pull ${UPSTREAM_REMOTE} main
+git push ${UPSTREAM_REMOTE} :pre-release-${RELEASE_VER} :release-${RELEASE_VER}
+git branch -d pre-release-${RELEASE_VER} release-${RELEASE_VER}
+```
+
+### Step 10: Final Summary
+
+```
+Release ${RELEASE_VER} complete!
+
+Completed steps:
+  [x] Clean build verification
+  [x] Release commit and tag (cargo release)
+  [x] Release PR merged
+  [x] Tag pushed to upstream
+  [x] Crate published to crates.io
+  [x] Vendor archive created
+  [x] GitHub release published
+  [x] Branches cleaned up
+
+Remaining manual steps (Fedora/CentOS packaging):
+  [ ] Review Packit PR in Fedora: https://src.fedoraproject.org/rpms/rust-afterburn/pull-requests
+  [ ] Merge rawhide into relevant branches (e.g., f43) and run fedpkg build
+  [ ] Submit builds to bodhi
+  [ ] Submit fast-track for FCOS testing-devel
+  [ ] Submit fast-track for FCOS next-devel (if open)
+  [ ] Create rebase-c9s-afterburn issue (CentOS Stream 9)
+  [ ] Create rebase-c10s-afterburn issue (CentOS Stream 10)
+```
+
+## Checklist Coverage
+
+From the release checklist, this skill covers:
+
+- [x] Make sure cargo-release and cargo-vendor-filterer are up to date
+- [x] `git checkout main && git pull`
+- [x] `cargo vendor-filterer target/vendor`
+- [x] `cargo test` with vendored deps
+- [x] `cargo clean && git clean -fd`
+- [x] `git checkout -b release-X.Y.Z`
+- [x] `cargo release --execute X.Y.Z` (guided, user runs)
+- [x] Push release branch and open PR
+- [x] `git checkout vX.Y.Z` and verify version
+- [x] Push tag
+- [x] `cargo publish` (guided, user runs)
+- [x] Vendor archive creation
+- [x] SHA256 digest computation
+- [x] GitHub release body preparation
+- [x] Branch cleanup
+
+## What's NOT covered
+
+- GPG key setup or management
+- crates.io account setup
+- Fedora packaging (Packit PR review, bodhi submissions)
+- CentOS Stream packaging (internal team process)
+- FCOS fast-track submissions
+
+## Automation Boundaries
+
+| Step | Automated? | Reason |
+|------|-----------|--------|
+| cargo vendor-filterer, cargo test | Yes | Deterministic build commands |
+| git checkout, push, branch, clean | Yes | Standard git operations |
+| gh pr create | Yes | CLI-based |
+| cargo release --execute | No | Requires GPG signing + interactive confirmation |
+| cargo publish | No | Requires crates.io auth token |
+| GitHub release creation | No | User should review changelog before publishing |
+| sha256sum computation | Yes | Deterministic |
+
+## References
+
+- Full release checklist: `.github/ISSUE_TEMPLATE/release-checklist.md`
+- cargo-release config: `Cargo.toml:14-20`
+- Example release PRs: #1224 (5.9.0), #1206 (5.8.2), #1200 (5.8.0)
+- Release that needed a redo: v5.8.1 ("Re-release of 5.8.0 due to error")
PATCH

echo "Gold patch applied."
