#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ignition

# Idempotency guard
if grep -qF "This skill automates adding support for a new cloud provider or platform to Igni" ".opencode/skills/add-platform-support/SKILL.md" && grep -qF "This skill automates the Ignition release process, handling version bumps and re" ".opencode/skills/release_note_update/SKILL.md" && grep -qF "This skill automates the complete Ignition config spec stabilization process fol" ".opencode/skills/stabilize-spec/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.opencode/skills/add-platform-support/SKILL.md b/.opencode/skills/add-platform-support/SKILL.md
@@ -0,0 +1,390 @@
+---
+name: add-platform-support
+description: Automate adding new cloud provider/platform support to Ignition
+---
+
+# Add Platform Support
+
+This skill automates adding support for a new cloud provider or platform to Ignition, following the exact pattern from commits like [ef142f33](https://github.com/coreos/ignition/commit/ef142f33) (Hetzner) and [9b833b21](https://github.com/coreos/ignition/commit/9b833b21) (Akamai).
+
+## What it does
+
+Performs a complete platform addition by:
+
+1. Creating provider implementation code in `internal/providers/{provider}/{provider}.go`
+2. Registering the provider in `internal/register/providers.go`
+3. Documenting the platform in `docs/supported-platforms.md`
+4. Adding a release note entry in `docs/release-notes.md`
+5. Running validation tests to ensure correctness
+6. Creating a properly formatted commit
+
+## Prerequisites
+
+None - the skill handles everything automatically.
+
+## Usage
+
+### Interactive Mode (Recommended)
+
+```bash
+/add-platform-support
+```
+
+The skill will prompt you for:
+- Platform ID (e.g., "hetzner")
+- Platform name (e.g., "Hetzner Cloud")
+- Metadata URL (e.g., "http://169.254.169.254/hetzner/v1/userdata")
+- Documentation URL (e.g., "https://www.hetzner.com/cloud")
+- Optional: Custom description
+
+### Direct Mode
+
+```bash
+/add-platform-support --id hetzner --name "Hetzner Cloud" --url "http://169.254.169.254/hetzner/v1/userdata" --docs "https://www.hetzner.com/cloud"
+```
+
+## Step-by-Step Workflow
+
+When invoked, follow these steps in order:
+
+### Step 1: Gather Required Information
+
+If not provided as arguments, ask the user for:
+
+**Required:**
+- `provider_id`: Platform ID (lowercase, alphanumeric, e.g., "hetzner")
+- `provider_name`: Display name (e.g., "Hetzner Cloud")
+- `metadata_url`: Full URL to fetch config from
+- `provider_url`: Documentation URL for the platform
+
+**Optional:**
+- `description`: Custom description (default: "Ignition will read its configuration from the instance userdata. Cloud SSH keys are handled separately.")
+
+**Validation:**
+- Provider ID must be lowercase, alphanumeric (no spaces, no special chars except hyphen)
+- Provider ID must not already exist in `internal/providers/`
+- URLs must be well-formed
+
+### Step 2: Determine Current Spec Version
+
+Find the latest experimental spec version:
+
+```bash
+# List config spec directories
+ls -d internal/config/v*_experimental/ | sort -V | tail -1
+```
+
+Extract the version (e.g., `v3_6_experimental`) to use in import paths.
+
+### Step 3: Parse Metadata URL
+
+Parse the metadata URL to extract components:
+
+```
+http://169.254.169.254/hetzner/v1/userdata
+→ Scheme: "http"
+→ Host: "169.254.169.254"
+→ Path: "hetzner/v1/userdata" (with leading slash)
+```
+
+### Step 4: Generate Provider Code
+
+Create `internal/providers/{provider_id}/{provider_id}.go` with this content:
+
+```go
+// Copyright 2026 CoreOS, Inc.
+//
+// Licensed under the Apache License, Version 2.0 (the "License");
+// you may not use this file except in compliance with the License.
+// You may obtain a copy of the License at
+//
+//     http://www.apache.org/licenses/LICENSE-2.0
+//
+// Unless required by applicable law or agreed to in writing, software
+// distributed under the License is distributed on an "AS IS" BASIS,
+// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+// See the License for the specific language governing permissions and
+// limitations under the License.
+
+// The {provider_id} provider fetches a remote configuration from the {provider_name}
+// user-data metadata service URL.
+
+package {provider_id}
+
+import (
+	"net/url"
+
+	"github.com/coreos/ignition/v2/config/{spec_version}/types"
+	"github.com/coreos/ignition/v2/internal/platform"
+	"github.com/coreos/ignition/v2/internal/providers/util"
+	"github.com/coreos/ignition/v2/internal/resource"
+
+	"github.com/coreos/vcontext/report"
+)
+
+var (
+	userdataURL = url.URL{
+		Scheme: "{scheme}",
+		Host:   "{host}",
+		Path:   "{path}",
+	}
+)
+
+func init() {
+	platform.Register(platform.Provider{
+		Name:  "{provider_id}",
+		Fetch: fetchConfig,
+	})
+}
+
+func fetchConfig(f *resource.Fetcher) (types.Config, report.Report, error) {
+	data, err := f.FetchToBuffer(userdataURL, resource.FetchOptions{})
+
+	if err != nil && err != resource.ErrNotFound {
+		return types.Config{}, report.Report{}, err
+	}
+
+	return util.ParseConfig(f.Logger, data)
+}
+```
+
+**Substitutions:**
+- `{provider_id}` → provider ID (e.g., "hetzner")
+- `{provider_name}` → provider name (e.g., "Hetzner Cloud")
+- `{spec_version}` → current spec version (e.g., "v3_6_experimental")
+- `{scheme}` → URL scheme (e.g., "http")
+- `{host}` → URL host (e.g., "169.254.169.254")
+- `{path}` → URL path with leading slash (e.g., "/hetzner/v1/userdata")
+
+**Important:**
+- Preserve all tabs/spaces for indentation
+- License header must be exactly 13 lines (enforced by test script)
+- Package comment describes what the provider does
+
+### Step 5: Update Provider Registry
+
+Read `internal/register/providers.go` to find the import section.
+
+Add the new provider import in **alphabetical order**:
+
+```go
+import (
+	_ "github.com/coreos/ignition/v2/internal/providers/exoscale"
+	_ "github.com/coreos/ignition/v2/internal/providers/file"
+	_ "github.com/coreos/ignition/v2/internal/providers/gcp"
++	_ "github.com/coreos/ignition/v2/internal/providers/{provider_id}"
+	_ "github.com/coreos/ignition/v2/internal/providers/hyperv"
+	...
+)
+```
+
+Use the Edit tool to insert the import in the correct alphabetical position.
+
+### Step 6: Update Platform Documentation
+
+Read `docs/supported-platforms.md` to find:
+1. The main platform list (bullet points)
+2. The URL reference section at the bottom
+
+**Main List Addition:**
+Insert in alphabetical order by display name:
+
+```markdown
+* [Google Cloud] (`gcp`) - Ignition will read its...
++ * [{provider_name}] (`{provider_id}`) - {description}
+* [Microsoft Hyper-V] (`hyperv`) - Ignition will read its...
+```
+
+**URL Reference Addition:**
+Insert in alphabetical order at bottom:
+
+```markdown
+[Google Cloud]: https://cloud.google.com/compute
++ [{provider_name}]: {provider_url}
+[Microsoft Hyper-V]: https://learn.microsoft.com/...
+```
+
+Use the Edit tool twice (once for list, once for reference).
+
+### Step 7: Update Release Notes
+
+Read `docs/release-notes.md` to find the "Unreleased" section.
+
+Add entry under "### Features":
+
+```markdown
+## Upcoming Ignition X.Y.Z (unreleased)
+
+### Breaking changes
+
+### Features
+
++ - Support {provider_name}
+
+### Changes
+```
+
+Use the Edit tool to insert after the "### Features" line.
+
+### Step 8: Validate Changes
+
+Run the test script to verify:
+
+```bash
+./test
+```
+
+**Expected results:**
+- ✅ License headers are valid (13 lines)
+- ✅ Platform ID is documented in supported-platforms.md
+- ✅ All tests pass
+
+If validation fails, show the error output and do NOT proceed to commit.
+
+### Step 9: Create Commit
+
+If all validation passes, create a commit:
+
+```bash
+# Stage all modified files
+git add internal/providers/{provider_id}/{provider_id}.go \
+        internal/register/providers.go \
+        docs/supported-platforms.md \
+        docs/release-notes.md
+
+# Create commit
+git commit -m "$(cat <<'EOF'
+providers/{provider_id}: add support for {provider_name}
+
+{Optional: Additional details about the provider}
+
+Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
+EOF
+)"
+```
+
+**Commit message format:**
+- Title: `providers/{provider_id}: add support for {provider_name}`
+- Body: Optional details
+- Co-author: Claude
+
+### Step 10: Provide Summary
+
+Show the user what was done:
+
+```
+✨ Platform support added successfully!
+
+Platform: {provider_name} ({provider_id})
+Metadata URL: {metadata_url}
+
+Files created/modified:
+  ✅ internal/providers/{provider_id}/{provider_id}.go (new file, 54 lines)
+  ✅ internal/register/providers.go (+1 import)
+  ✅ docs/supported-platforms.md (+2 lines)
+  ✅ docs/release-notes.md (+1 line)
+
+Validation:
+  ✅ ./test script passed
+  ✅ License headers correct
+  ✅ Platform documented
+
+Commit created:
+  providers/{provider_id}: add support for {provider_name}
+
+Next steps:
+1. Review changes: git show
+2. Test the provider if you have access to the platform
+3. Push to remote when ready: git push
+4. Create a PR to main branch
+```
+
+## Example Execution
+
+### Input:
+```
+Provider ID: hetzner
+Provider Name: Hetzner Cloud
+Metadata URL: http://169.254.169.254/hetzner/v1/userdata
+Documentation URL: https://www.hetzner.com/cloud
+Description: (use default)
+```
+
+### Output:
+```
+✨ Platform support added successfully!
+
+Platform: Hetzner Cloud (hetzner)
+Metadata URL: http://169.254.169.254/hetzner/v1/userdata
+
+Files created/modified:
+  ✅ internal/providers/hetzner/hetzner.go (new file, 54 lines)
+  ✅ internal/register/providers.go (+1 import)
+  ✅ docs/supported-platforms.md (+2 lines)
+  ✅ docs/release-notes.md (+1 line)
+
+Commit: providers/hetzner: add support for Hetzner Cloud
+```
+
+## Validation Details
+
+The `./test` script automatically validates:
+
+1. **License headers**: All .go files must have Apache 2.0 header (13 lines)
+2. **Platform documentation**: Checks that every `platform.Register()` call has corresponding docs
+3. **Code compilation**: Ensures Go code is valid
+
+**From test script (lines 70-85):**
+```bash
+platforms=$(grep -A 1 -h platform.Register internal/providers/*/* | grep Name: | cut -f2 -d\")
+for id in ${platforms}; do
+    case "${id}" in
+    file) ;;  # Undocumented platform ID for testing
+    *)
+        if ! grep -qF "\`${id}\`" docs/supported-platforms.md; then
+            echo "Undocumented platform ID: $id" >&2
+            exit 1
+        fi
+        ;;
+    esac
+done
+```
+
+## What's NOT Covered
+
+This skill creates **simple providers** only (single HTTP GET from metadata URL).
+
+For complex providers requiring:
+- Authentication tokens (like Akamai)
+- Base64 decoding
+- Gzip decompression
+- Multiple URLs (IPv4/IPv6)
+- Special HTTP headers
+
+You'll need to manually enhance the generated code after the skill runs.
+
+## References
+
+**Example Commits:**
+- [ef142f33](https://github.com/coreos/ignition/commit/ef142f33) - Hetzner Cloud (simple provider)
+- [9b833b21](https://github.com/coreos/ignition/commit/9b833b21) - Akamai (complex provider with auth)
+
+**Documentation:**
+- `docs/supported-platforms.md` - Platform list
+- `test` script (lines 70-85) - Validation logic
+
+**Existing Providers:** 35+ examples in `internal/providers/`
+
+## Troubleshooting
+
+**"Provider already exists"**
+→ Check if provider is already in `internal/providers/{id}/`
+
+**"Test validation failed"**
+→ Check the error message, likely:
+  - License header formatting issue
+  - Platform not properly documented
+  - Code syntax error
+
+**"Alphabetical order incorrect"**
+→ Verify the import/list/reference was inserted in correct alphabetical position
diff --git a/.opencode/skills/release_note_update/SKILL.md b/.opencode/skills/release_note_update/SKILL.md
@@ -0,0 +1,175 @@
+---
+name: release_note_update:stage Notes
+description: Automate release notes update and offer tagging.
+---
+
+# Ignition Release
+
+This skill automates the Ignition release process, handling version bumps and release notes updates following the established conventions from [PR #2181](https://github.com/coreos/ignition/pull/2181).
+
+## What it does
+
+Performs a complete release preparation by:
+
+1. Moving unreleased items from the "Unreleased" section to a new version section in `docs/release-notes.md`
+2. Formatting the release notes with the proper date and version
+3. Converting release note items to imperative mood (e.g., "Fixed" → "Fix")
+4. Creating a properly formatted commit following the naming convention
+5. Optionally creating a GitHub release and tag
+
+## Release Types
+
+The skill supports different types of releases:
+
+- **Patch release** (e.g., 2.25.0 → 2.25.1): Bug fixes only
+- **Minor release** (e.g., 2.25.0 → 2.26.0): New features and changes
+- **Major release** (e.g., 2.25.0 → 3.0.0): Breaking changes
+
+## Usage
+
+When invoked, the skill will:
+
+1. Analyze the current "Unreleased" section in `docs/release-notes.md`
+2. Ask you to confirm the new version number (or you can provide it upfront)
+3. Ask you to confirm the release date (defaults to today)
+4. Move all unreleased items to a new version section
+5. Format items in imperative mood
+6. Create a commit with the format: `docs/release-notes: update for <version>`
+
+### Example invocation
+
+```
+/release 2.26.0
+```
+
+or simply:
+
+```
+/release
+```
+
+The skill will detect the appropriate next version based on the unreleased items.
+
+## Release Notes Format
+
+The skill follows this structure:
+
+```markdown
+## Upcoming Ignition <NEXT_VERSION> (unreleased)
+
+### Breaking changes
+
+### Features
+
+### Changes
+
+### Bug fixes
+
+## Ignition <VERSION> (<DATE>)
+
+### Breaking changes
+- Fix/Add/Update <description>
+
+### Features
+- Add <description>
+
+### Changes
+- Update <description>
+
+### Bug fixes
+- Fix <description>
+```
+
+### Formatting Rules
+
+1. **Version header format**: `## Ignition <VERSION> (<YYYY-MM-DD>)`
+2. **Date format**: ISO format (YYYY-MM-DD)
+3. **Item format**: Imperative mood
+   - Use "Fix" not "Fixed"
+   - Use "Add" not "Added"
+   - Use "Update" not "Updated"
+4. **Sections**: Include only non-empty sections (Breaking changes, Features, Changes, Bug fixes)
+5. **Empty sections**: The "Unreleased" section should have empty subsections after release
+
+## Commit Format
+
+The skill creates a commit with this exact format:
+
+```
+docs/release-notes: update for <version>
+```
+
+Example: `docs/release-notes: update for 2.26.0`
+
+## What the skill does step-by-step
+
+1. ✅ Read current `docs/release-notes.md`
+2. ✅ Parse the "Unreleased" section
+3. ✅ Determine the new version (provided or auto-detect)
+4. ✅ Get the release date (provided or use today)
+5. ✅ Convert all items to imperative mood
+6. ✅ Create new version section with formatted date
+7. ✅ Move all items from "Unreleased" to the new version section
+8. ✅ Leave "Unreleased" section with empty subsections
+9. ✅ Update `docs/release-notes.md`
+10. ✅ Create commit with proper naming convention
+11. ✅ Provide summary of changes
+
+## Example Output
+
+After running the skill, you'll see:
+
+```
+✨ Release preparation complete!
+
+Version: 2.26.0
+Date: 2026-02-17
+
+Release notes updated:
+  - 1 breaking change
+  - 2 features
+  - 0 changes
+  - 1 bug fix
+
+Created commit:
+  docs/release-notes: update for 2.26.0
+
+Next steps:
+1. Review the changes: git show
+2. Push the commit if everything looks good
+3. Create a GitHub release/tag if needed
+```
+
+## Optional: Creating GitHub Release
+
+The skill can optionally:
+
+1. Create a git tag for the version
+2. Create a GitHub release with the release notes
+
+To enable this, confirm when prompted or pass the `--create-release` flag.
+
+## Reference
+
+- [PR #2181 - Example Release (2.25.1)](https://github.com/coreos/ignition/pull/2181)
+- [Release Notes Documentation](https://github.com/coreos/ignition/blob/main/docs/release-notes.md)
+
+## Checklist Coverage
+
+This skill automates:
+
+- ✅ Moving unreleased items to versioned section
+- ✅ Formatting version header with date
+- ✅ Converting items to imperative mood
+- ✅ Creating properly named commit
+- ✅ Optionally creating git tag and GitHub release
+
+## What's NOT covered
+
+The following tasks are NOT automated and must be done manually:
+
+- Updating version numbers in code files (e.g., `version.go`, `package.json`)
+- Running tests before release
+- Building and publishing release artifacts
+- Updating external documentation
+- Announcing the release
diff --git a/.opencode/skills/stabilize-spec/SKILL.md b/.opencode/skills/stabilize-spec/SKILL.md
@@ -0,0 +1,139 @@
+---
+name: stabilize-spec
+description: Automate the Ignition config spec stabilization process
+---
+
+# Ignition Spec Stabilization
+
+This skill automates the complete Ignition config spec stabilization process following the exact 8-commit structure from [PR #2202](https://github.com/coreos/ignition/pull/2202).
+
+## What it does
+
+Performs a complete spec stabilization by creating 8 atomic commits that:
+
+1. Rename the experimental package to stable (e.g., `v3_6_experimental` → `v3_6`)
+2. Stabilize the spec (remove PreRelease, update tests, update Accept header)
+3. Copy the stable spec to a new experimental version (e.g., `v3_6` → `v3_7_experimental`)
+4. Adapt the new experimental spec
+5. Update all imports across the codebase (72+ files)
+6. Update blackbox tests
+7. Update documentation generation
+8. Update docs and regenerate schemas
+
+## Prerequisites
+
+Before running this skill, ensure:
+
+```bash
+# Install schematyper (required for regenerating schemas)
+cd /tmp
+git clone https://github.com/idubinskiy/schematyper.git
+cd schematyper
+go mod init github.com/idubinskiy/schematyper
+echo 'replace gopkg.in/alecthomas/kingpin.v2 => github.com/alecthomas/kingpin/v2 v2.4.0' >> go.mod
+go mod tidy
+go install .
+
+# Install build dependencies (Fedora/RHEL)
+sudo dnf install -y libblkid-devel
+```
+
+## Usage
+
+When invoked, provide the version information:
+
+```
+Current experimental version: 3.6.0-experimental
+Target stable version: 3.6.0
+Next experimental version: 3.7.0-experimental
+```
+
+The skill will then:
+
+1. ✅ Perform all code changes across the repository
+2. ✅ Create 8 properly structured commits
+3. ✅ Run `./generate` to regenerate schemas and docs
+4. ✅ Run `./build` to verify compilation
+5. ✅ Run `./test` to verify all tests pass
+6. ✅ Provide a summary of what was done
+
+## Checklist Coverage
+
+This skill completes all items from the [stabilization checklist](https://github.com/coreos/ignition/blob/main/.github/ISSUE_TEMPLATE/stabilize-checklist.md):
+
+### Making the experimental package stable ✅
+- Rename `config/vX_Y_experimental` to `config/vX_Y`
+- Drop `_experimental` from all imports
+- Update `MaxVersion` to delete the `PreRelease` field
+- Update `config.go` comment block
+- Update `config_test.go` to test stable version valid, experimental invalid
+- Update Accept header in `internal/resource/url.go`
+
+### Creating the new experimental package ✅
+- Copy `config/vX_Y` into `config/vX_(Y+1)_experimental`
+- Update all imports to `config/vX_(Y+1)_experimental`
+- Update `MaxVersion` with `PreRelease = "experimental"`
+- Update `config.go` prev import to stable package
+- Update `config_test.go` for new experimental version
+- Simplify `translate.go` to only `translateIgnition` and `Translate`
+- Update `translate_test.go` old import to stable version
+- Update `config/config.go` imports to experimental version
+- Update `config/config_test.go` to add new experimental version
+- Update `generate` script
+
+### Update all relevant places ✅
+- Update all imports from `vX_Y_experimental` to `vX_(Y+1)_experimental`
+- Add import `config/vX_Y/types` to `tests/register/register.go`
+- Update import to `vX_(Y+1)_experimental` in `tests/register/register.go`
+- Add `vX_Y/types` to `configVersions` in `Register()`
+
+### Update the blackbox tests ✅
+- Bump invalid `-experimental` version in `VersionOnlyConfig` test
+- Change all `X.Y.0-experimental` to `X.Y.0` in tests
+- Update Accept header checks in `tests/servers/servers.go`
+
+### Update docs ✅
+- Update `internal/doc/main.go`
+- Run `generate` to regenerate schemas and docs
+- Add section to `docs/migrating-configs.md`
+- Update `docs/specs.md`
+- Note stabilization in `docs/release-notes.md`
+
+## What's NOT covered
+
+The following sections from the checklist require external repos and are NOT automated:
+
+- External tests (`.cci.jenkinsfile`, fedora-coreos-config)
+- Other packages (ignition-config-rs, coreos-installer, ign-converter, Butane, FCOS docs, coreos-assembler, MCO)
+
+These must be done manually after the PR is merged.
+
+## Example Output
+
+After running the skill, you'll see:
+
+```
+✨ Stabilization complete!
+
+Created 8 commits:
+  ceb03d33 docs: update for spec stabilization
+  e5cac5c1 docs: shuffle for spec stabilization
+  2aca7225 tests: update for new experimental spec
+  3252aa50 *: update to v3_7_experimental spec
+  0e5a3297 config/v3_7_experimental: adapt for new experimental spec
+  21d51407 config: copy v3_6 to v3_7_experimental
+  57d4d86e config/v3_6: stabilize
+  8a071635 config: rename v3_6_experimental to v3_6
+
+Next steps:
+1. Review commits: git log --oneline -8
+2. Create PR to main branch
+3. Update issue checkboxes (see checklist above)
+4. After merge, handle external tests and packages
+```
+
+## Reference
+
+- [Issue #2200 - Stabilization Checklist](https://github.com/coreos/ignition/issues/2200)
+- [PR #2202 - Example Stabilization (3.6.0)](https://github.com/coreos/ignition/pull/2202)
+- [Stabilization Template](https://github.com/coreos/ignition/blob/main/.github/ISSUE_TEMPLATE/stabilize-checklist.md)
PATCH

echo "Gold patch applied."
