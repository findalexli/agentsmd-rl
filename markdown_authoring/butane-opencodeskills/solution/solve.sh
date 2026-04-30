#!/usr/bin/env bash
set -euo pipefail

cd /workspace/butane

# Idempotency guard
if grep -qF "- **Config merging** (recommended): Generate a fresh Ignition config struct, the" ".opencode/skills/add-sugar/SKILL.md" && grep -qF "Read the file and identify the test case block for the removed feature. Test cas" ".opencode/skills/remove-feature/SKILL.md" && grep -qF "**Note**: This step implements lines 20-21 (base) and 28-30 (distro) from `.gith" ".opencode/skills/stabilize-spec/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.opencode/skills/add-sugar/SKILL.md b/.opencode/skills/add-sugar/SKILL.md
@@ -0,0 +1,674 @@
+---
+name: add-sugar
+description: Add syntactic sugar features to Butane experimental spec versions
+---
+
+# Add Sugar Feature
+
+## What it does
+
+Guides and scaffolds the addition of a new syntactic sugar feature to a Butane experimental spec version:
+
+1. Gathers requirements from the user (spec type, field design, translation behavior)
+2. Validates prerequisites (experimental spec exists, git status clean)
+3. Adds struct definitions to `schema.go`
+4. Implements translation (desugaring) logic in `translate.go`
+5. Adds test cases in `translate_test.go`
+6. Adds validation logic in `validate.go` and tests in `validate_test.go` (if needed)
+7. Adds error constants to `config/common/errors.go`
+8. Updates documentation descriptors in `internal/doc/butane.yaml`
+9. Runs `./generate` to regenerate spec docs
+10. Adds examples to `docs/examples.md`
+11. Adds a release note to `docs/release-notes.md`
+12. Runs `./test` to validate everything compiles and passes
+
+## Prerequisites
+
+- Go toolchain installed
+- Target experimental spec version exists (directory ends with `_exp`)
+- Understanding of what the sugar should do (what YAML the user writes, what Ignition config it generates)
+
+## Usage
+
+```bash
+# Interactive mode - will ask for details
+/add-sugar
+
+# Target a specific spec
+/add-sugar --spec fcos/v1_8_exp --field boot_device.luks.method
+
+# Base spec sugar (distro-independent)
+/add-sugar --spec base/v0_8_exp --field storage.files.parent
+```
+
+## Workflow
+
+### Step 1: Gather Requirements
+
+If not provided via arguments, ask the user:
+
+1. **Target spec**: Where should the sugar live?
+   - **Base spec** (`base/v0_8_exp`): distro-independent, will appear in all variants
+   - **Distro spec** (e.g., `config/fcos/v1_8_exp`, `config/openshift/v4_22_exp`): distro-specific
+
+2. **Feature description**: What does the sugar do?
+   - What YAML fields does the user write?
+   - What Ignition config does it expand to?
+   - Any validation constraints?
+
+3. **Schema design**: Ask the user to describe or confirm:
+   - Field name(s) and types
+   - Whether it's a new top-level field or nested within an existing struct
+   - Any new struct types needed
+
+4. **Translation approach**: Per `docs/development.md:62`:
+   - **Config merging** (recommended): Generate a fresh Ignition config struct, then use `baseutil.MergeTranslatedConfigs()` to merge with the user's config. The desugared struct is the merge parent, user config is child.
+   - **Direct modification**: Only if config merging is not expressive enough.
+
+5. **Validation needs**: What input constraints exist?
+   - Required fields
+   - Valid value ranges
+   - Mutually exclusive options
+
+### Step 2: Pre-flight Validation
+
+Run these checks:
+
+```bash
+# Verify experimental spec directory exists
+ls -la base/{version}/ || ls -la config/{distro}/{version}/
+
+# Check that the version ends with _exp
+# CRITICAL: Sugar must ONLY be added to experimental specs
+
+# Check git status
+git status --porcelain
+```
+
+**Stop if**:
+- Target spec does not exist
+- Target spec is NOT experimental (name must end with `_exp`)
+- Working directory has unexpected uncommitted changes
+
+### Step 3: Update Schema
+
+**File**: `{spec_dir}/schema.go`
+
+Read the existing schema file first to understand the current struct layout.
+
+#### 3a: Adding a new top-level field to Config
+
+If the sugar is a new top-level section (like `boot_device` or `grub`), add a field to the `Config` struct:
+
+```go
+type Config struct {
+    base.Config `yaml:",inline"`
+    BootDevice  BootDevice `yaml:"boot_device"`
+    Grub        Grub       `yaml:"grub"`
+    NewSugar    NewSugar   `yaml:"new_sugar"`  // ADD THIS
+}
+```
+
+Then add the new struct type(s):
+
+```go
+type NewSugar struct {
+    FieldOne *string `yaml:"field_one"`
+    FieldTwo *bool   `yaml:"field_two"`
+}
+```
+
+#### 3b: Adding a field to an existing struct in base
+
+If extending an existing base struct (like adding `parent` to `File`), modify the struct in `base/{version}/schema.go`:
+
+```go
+type File struct {
+    // ... existing fields ...
+    NewField NewFieldType `yaml:"new_field"`  // ADD THIS
+}
+```
+
+**Conventions**:
+- Use `*string`, `*bool`, `*int` for optional scalar fields
+- Use `[]Type` for lists
+- Use struct types for nested objects
+- YAML tags use `snake_case`
+- Add ` butane:"auto_skip"` tag for fields not in the Ignition spec that should be automatically filtered from the output (see `config/util/filter.go`)
+
+### Step 4: Implement Translation
+
+**File**: `{spec_dir}/translate.go`
+
+Read the existing translate.go to understand the current translation pipeline.
+
+#### 4a: Config Merging Pattern (Recommended)
+
+This is the recommended approach per `docs/development.md:62`. The desugared config is the merge parent, user config is the child, so users can override sugar-generated values.
+
+For **distro specs** (e.g., `config/fcos/v1_8_exp/translate.go`):
+
+Add a new processing function and call it from `ToIgn3_7Unvalidated()`:
+
+```go
+func (c Config) ToIgn3_7Unvalidated(options common.TranslateOptions) (types.Config, translate.TranslationSet, report.Report) {
+    ret, ts, r := c.Config.ToIgn3_7Unvalidated(options)
+    if r.IsFatal() {
+        return types.Config{}, translate.TranslationSet{}, r
+    }
+    // Existing sugar processing...
+    r.Merge(c.processBootDevice(&ret, &ts, options))
+
+    // ADD: Call new sugar processing
+    retp, tsp, rp := c.processNewSugar(options)
+    retConfig, ts := baseutil.MergeTranslatedConfigs(retp, tsp, ret, ts)
+    ret = retConfig.(types.Config)
+    r.Merge(rp)
+
+    return ret, ts, r
+}
+```
+
+Implement the processing function:
+
+```go
+func (c Config) processNewSugar(options common.TranslateOptions) (types.Config, translate.TranslationSet, report.Report) {
+    rendered := types.Config{}
+    ts := translate.NewTranslationSet("yaml", "json")
+    var r report.Report
+
+    // Early return if sugar is not being used
+    if /* sugar not configured */ {
+        return rendered, ts, r
+    }
+
+    yamlPath := path.New("yaml", "new_sugar")
+
+    // Generate Ignition config elements
+    // Example: creating a file
+    file := types.File{
+        Node: types.Node{
+            Path: "/path/to/generated/file",
+        },
+        FileEmbedded1: types.FileEmbedded1{
+            Contents: types.Resource{
+                Source: util.StrToPtr("data:,generated-content"),
+            },
+        },
+    }
+    rendered.Storage.Files = append(rendered.Storage.Files, file)
+
+    // Track translations for error reporting
+    ts.AddFromCommonSource(yamlPath, path.New("json", "storage"), rendered.Storage)
+
+    return rendered, ts, r
+}
+```
+
+For **base specs** (e.g., `base/v0_8_exp/translate.go`):
+
+The pattern is the same, but the processing function is called from the base `ToIgn3_7Unvalidated()` and operates on base types. When modifying translation at the base level, you may need to:
+- Create or modify a custom translator function (e.g., `translateStorage()`)
+- Register it with `tr.AddCustomTranslator()`
+
+#### 4b: Direct Modification Pattern (Alternative)
+
+Only use this when config merging isn't expressive enough:
+
+```go
+func (c Config) processNewSugar(config *types.Config, ts *translate.TranslationSet, options common.TranslateOptions) report.Report {
+    var r report.Report
+
+    if /* sugar not configured */ {
+        return r
+    }
+
+    // Directly modify the Ignition config
+    config.Storage.Files = append(config.Storage.Files, types.File{...})
+
+    // Track translations
+    yamlPath := path.New("yaml", "new_sugar")
+    jsonPath := path.New("json", "storage", "files", len(config.Storage.Files)-1)
+    ts.AddFromCommonSource(yamlPath, jsonPath, config.Storage.Files[len(config.Storage.Files)-1])
+
+    return r
+}
+```
+
+**Key imports** (add as needed):
+
+```go
+import (
+    baseutil "github.com/coreos/butane/base/util"
+    "github.com/coreos/butane/config/common"
+    "github.com/coreos/butane/translate"
+
+    "github.com/coreos/ignition/v2/config/util"
+    "github.com/coreos/ignition/v2/config/v3_7_experimental/types"
+    "github.com/coreos/vcontext/path"
+    "github.com/coreos/vcontext/report"
+)
+```
+
+**IMPORTANT**: The Ignition types import version must match the one already used in the file. Check the existing imports before adding new ones.
+
+### Step 5: Write Tests
+
+**File**: `{spec_dir}/translate_test.go`
+
+Read the existing test file to understand the test patterns used.
+
+Tests follow a table-driven pattern. Add a new test function:
+
+```go
+func TestTranslateNewSugar(t *testing.T) {
+    tests := []struct {
+        in  Config
+        out types.Config
+    }{
+        // empty / no-op case
+        {
+            in:  Config{},
+            out: types.Config{
+                Ignition: types.Ignition{
+                    Version: "3.7.0-experimental",
+                },
+            },
+        },
+        // basic sugar usage
+        {
+            in: Config{
+                NewSugar: NewSugar{
+                    FieldOne: util.StrToPtr("value"),
+                },
+            },
+            out: types.Config{
+                Ignition: types.Ignition{
+                    Version: "3.7.0-experimental",
+                },
+                Storage: types.Storage{
+                    Files: []types.File{
+                        {
+                            Node: types.Node{
+                                Path: "/path/to/generated/file",
+                            },
+                            FileEmbedded1: types.FileEmbedded1{
+                                Contents: types.Resource{
+                                    Source: util.StrToPtr("data:,generated-content"),
+                                },
+                            },
+                        },
+                    },
+                },
+            },
+        },
+    }
+
+    for i, test := range tests {
+        t.Run(fmt.Sprintf("translate %d", i), func(t *testing.T) {
+            out, translations, r := test.in.ToIgn3_7Unvalidated(common.TranslateOptions{})
+            r = confutil.TranslateReportPaths(r, translations)
+            baseutil.VerifyReport(t, test.in, r)
+            assert.Equal(t, test.out, out, "bad output")
+            assert.Equal(t, report.Report{}, r, "expected empty report")
+            assert.NoError(t, translations.DebugVerifyCoverage(out), "incomplete TranslationSet coverage")
+        })
+    }
+}
+```
+
+**IMPORTANT**: The Ignition version in test expectations (e.g., `"3.7.0-experimental"`) must match the version used in the spec's translate.go. Check the existing tests for the correct value.
+
+**Test categories to cover**:
+- Empty/no-op: sugar not configured, should produce default output
+- Basic usage: simplest valid configuration
+- Complex usage: all options exercised
+- User overrides: verify user can override sugar-generated values (for merge pattern)
+- Edge cases: boundary conditions
+- Error cases: invalid inputs (test separately in validate tests)
+
+### Step 6: Add Validation (If Needed)
+
+**File**: `{spec_dir}/validate.go`
+
+Read the existing validate.go to understand validation patterns.
+
+Add a `Validate` method on the new sugar type:
+
+```go
+func (s NewSugar) Validate(c path.ContextPath) (r report.Report) {
+    if s.FieldOne != nil && *s.FieldOne == "" {
+        r.AddOnError(c.Append("field_one"), common.ErrNewSugarFieldOneEmpty)
+    }
+    // ... more validations
+    return
+}
+```
+
+Or add validation to an existing `Validate` method on `Config`:
+
+```go
+func (conf Config) Validate(c path.ContextPath) (r report.Report) {
+    // ... existing validations ...
+
+    // New sugar validation
+    if someCondition {
+        r.AddOnError(c.Append("new_sugar", "field"), common.ErrSomething)
+    }
+    return
+}
+```
+
+**Validation test file**: `{spec_dir}/validate_test.go`
+
+```go
+func TestValidateNewSugar(t *testing.T) {
+    tests := []struct {
+        in      NewSugar
+        out     error
+        errPath path.ContextPath
+    }{
+        // valid config
+        {
+            in:      NewSugar{FieldOne: util.StrToPtr("valid")},
+            out:     nil,
+            errPath: path.New("yaml"),
+        },
+        // invalid config
+        {
+            in:      NewSugar{FieldOne: util.StrToPtr("")},
+            out:     common.ErrNewSugarFieldOneEmpty,
+            errPath: path.New("yaml", "field_one"),
+        },
+    }
+
+    for i, test := range tests {
+        t.Run(fmt.Sprintf("validate %d", i), func(t *testing.T) {
+            actual := test.in.Validate(path.New("yaml"))
+            baseutil.VerifyReport(t, test.in, actual)
+            expected := report.Report{}
+            expected.AddOnError(test.errPath, test.out)
+            assert.Equal(t, expected, actual, "bad validation report")
+        })
+    }
+}
+```
+
+### Step 7: Add Error Constants
+
+**File**: `config/common/errors.go`
+
+Read the existing errors.go to understand the naming pattern.
+
+Add new error variables in the appropriate section:
+
+```go
+var (
+    // ... existing errors ...
+
+    // New sugar
+    ErrNewSugarFieldOneEmpty = errors.New("field_one must not be empty")
+    ErrNewSugarInvalidCombo  = errors.New("field_one and field_two are mutually exclusive")
+)
+```
+
+**Naming convention**: `Err` + CamelCase description. Error messages should be lowercase, concise, and actionable.
+
+### Step 8: Update Documentation Descriptors
+
+**File**: `internal/doc/butane.yaml`
+
+Read the existing butane.yaml to understand the YAML structure for field documentation.
+
+Add documentation descriptors for new fields. Place them in the correct location within the document hierarchy.
+
+For a new top-level field (sibling of `boot_device`, `grub`):
+
+```yaml
+    - name: new_sugar
+      after: $
+      desc: describes the desired new sugar configuration.
+      children:
+        - name: field_one
+          desc: the value for field one.
+        - name: field_two
+          desc: whether to enable feature two. If omitted, defaults to false.
+```
+
+For a field within an existing section (e.g., under `storage.files`):
+
+```yaml
+        - name: files
+          children:
+            # ... existing children ...
+            - name: new_field
+              after: $
+              desc: description of the new field.
+```
+
+**Key patterns in butane.yaml**:
+- `after: $` means "add at the end" (after all Ignition-defined fields)
+- `after: ^` means "add at the beginning" (before all Ignition-defined fields)
+- `transforms` can conditionally modify descriptions per variant/version
+- `use: component_name` reuses a named component definition
+- `required: true` marks a field as required
+- Limit new fields to experimental spec versions using transforms if needed (add `"Unsupported"` replacement for older versions)
+
+### Step 9: Regenerate Documentation
+
+Run the documentation generator:
+
+```bash
+./generate
+```
+
+**Expected outcome**: Several `docs/config-*-exp.md` files are updated with the new field documentation.
+
+Verify the docs were regenerated:
+
+```bash
+git diff docs/
+```
+
+If `./generate` fails, the schema or butane.yaml likely has an error. Fix and retry.
+
+### Step 10: Add Usage Examples
+
+**File**: `docs/examples.md`
+
+Read the existing examples.md to understand the format.
+
+Add a new example section:
+
+```markdown
+## New Sugar Feature Name
+
+This example {describes what the example demonstrates}.
+
+<!-- butane-config -->
+```yaml
+variant: fcos
+version: 1.8.0-experimental
+new_sugar:
+  field_one: value
+  field_two: true
+```
+<!-- /butane-config -->
+
+This {describes what gets generated/created}.
+```
+
+**Notes**:
+- The `<!-- butane-config -->` comment markers are used for automated validation
+- Use the experimental version string (e.g., `1.8.0-experimental`)
+- Keep examples minimal but complete
+- Show the simplest useful configuration first
+
+### Step 11: Add Release Notes
+
+**File**: `docs/release-notes.md`
+
+Read the current release notes section.
+
+Add a note under `## Upcoming Butane X.Y.Z (unreleased)` > `### Features`:
+
+```markdown
+### Features
+
+- Add {sugar description} _(fcos 1.8.0-exp, openshift 4.22.0-exp, ...)_
+```
+
+**Notes**:
+- List all affected variants/versions in the parenthetical
+- For base sugar, list all experimental variants since they all inherit it
+- Use the `-exp` suffix convention for experimental versions
+- Keep the description concise (one line)
+
+### Step 12: Run Tests
+
+Execute the full test suite:
+
+```bash
+./test
+```
+
+**Expected outcome**: All tests pass.
+
+If tests fail:
+1. Read the error output carefully
+2. Common issues:
+   - Missing `TranslationSet` coverage: Add translation path tracking
+   - Type mismatches: Check Ignition types vs Butane types
+   - Import errors: Verify import paths match the experimental spec version
+   - Validation failures: Check that test expectations match the validation logic
+3. Fix issues and re-run
+
+### Step 13: Report Results
+
+Provide a comprehensive summary:
+
+```
+Sugar feature "{name}" added to {spec_type}/{version}
+
+Files Modified:
+  - {spec_dir}/schema.go (+N lines)
+  - {spec_dir}/translate.go (+N lines)
+  - {spec_dir}/translate_test.go (+N lines)
+  - {spec_dir}/validate.go (+N lines) [if applicable]
+  - {spec_dir}/validate_test.go (+N lines) [if applicable]
+  - config/common/errors.go (+N lines) [if applicable]
+  - internal/doc/butane.yaml (+N lines)
+  - docs/examples.md (+N lines)
+  - docs/release-notes.md (+N lines)
+  - docs/config-*-exp.md (N files, regenerated)
+
+Tests: PASSED
+Docs: REGENERATED
+
+Suggested commit message:
+
+  {spec}/{version}: add {sugar_name} sugar
+
+  {description of what the sugar does and why}
+
+  resolves: #{issue_number}
+```
+
+## Checklist Coverage
+
+This skill guides the following workflow:
+
+- ✅ Schema definition in `schema.go`
+- ✅ Translation logic in `translate.go` (config merging or direct modification)
+- ✅ Comprehensive tests in `translate_test.go`
+- ✅ Validation logic in `validate.go` (when needed)
+- ✅ Validation tests in `validate_test.go` (when needed)
+- ✅ Error constants in `config/common/errors.go`
+- ✅ Documentation descriptors in `internal/doc/butane.yaml`
+- ✅ Doc regeneration via `./generate`
+- ✅ Usage examples in `docs/examples.md`
+- ✅ Release notes in `docs/release-notes.md`
+- ✅ Full test suite validation via `./test`
+
+## What's NOT Covered
+
+- ❌ **Designing the sugar semantics** - the user must know what Ignition config the sugar should produce
+- ❌ **Complex translation logic** - the skill provides patterns, but domain-specific logic (e.g., partition layout calculations for boot_device) must be written by the developer
+- ❌ **Integration tests** - only unit tests are scaffolded
+- ❌ **Updating upgrading docs** - `docs/upgrading-*.md` must be updated manually when the sugar is stabilized
+- ❌ **Creating git commits** - user should review changes first
+
+## Example Output
+
+```
+/add-sugar --spec fcos/v1_8_exp
+
+Analyzing config/fcos/v1_8_exp...
+
+Current experimental spec:
+  - Ignition version: 3.7.0-experimental
+  - Base dependency: base/v0_8_exp
+  - Existing sugar: boot_device, grub
+
+What sugar would you like to add?
+> Network configuration shortcut for static IPs
+
+Gathering schema design...
+
+Schema: New top-level field `network` with nested structs
+Translation: Config merging pattern
+Validation: Required fields, IP format validation
+
+Phase 1: Schema
+  schema.go updated (+15 lines)
+
+Phase 2: Translation
+  translate.go updated (+45 lines)
+
+Phase 3: Tests
+  translate_test.go updated (+120 lines)
+
+Phase 4: Validation
+  validate.go updated (+20 lines)
+  validate_test.go updated (+40 lines)
+
+Phase 5: Errors
+  config/common/errors.go updated (+3 lines)
+
+Phase 6: Documentation
+  internal/doc/butane.yaml updated (+10 lines)
+  ./generate completed
+  docs/config-fcos-v1_8-exp.md regenerated
+  docs/config-fiot-v1_1-exp.md regenerated
+  docs/config-flatcar-v1_2-exp.md regenerated
+  docs/config-openshift-v4_22-exp.md regenerated
+  docs/config-r4e-v1_2-exp.md regenerated
+
+Phase 7: Examples & Release Notes
+  docs/examples.md updated (+12 lines)
+  docs/release-notes.md updated (+1 line)
+
+Phase 8: Validation
+  ./test: All tests passed
+
+Sugar feature "network" added to fcos/v1_8_exp
+
+Suggested commit message:
+
+  fcos/v1_8_exp: add network configuration sugar
+
+  Add a `network` section that allows users to configure static
+  IP addresses without manually creating NetworkManager keyfiles.
+
+  resolves: #XXX
+```
+
+## References
+
+- Design document: `.opencode/skills/add-sugar/DESIGN.md`
+- Examples: `.opencode/skills/add-sugar/examples/`
+- Development guide: `docs/development.md` (esp. lines 60-64 on sugar implementation)
+- Stabilize checklist: `.github/ISSUE_TEMPLATE/stabilize-checklist.md`
+- Current base experimental: `base/v0_8_exp/`
+- Current FCOS experimental: `config/fcos/v1_8_exp/`
+- Current OpenShift experimental: `config/openshift/v4_22_exp/`
diff --git a/.opencode/skills/remove-feature/SKILL.md b/.opencode/skills/remove-feature/SKILL.md
@@ -0,0 +1,326 @@
+---
+name: remove-feature
+description: Remove unsupported sugar features from stabilized OpenShift spec versions
+---
+
+# Remove Feature from Stabilized Spec
+
+## What it does
+
+Automates the removal of sugar features from stabilized OpenShift spec versions:
+
+1. Validates the target spec directory and feature existence
+2. Removes the feature's translation function call from `translate.go`
+3. Removes the translation function definition from `translate.go`
+4. Removes related test cases from `translate_test.go`
+5. Bumps the `max` version in `internal/doc/butane.yaml` for doc transforms
+6. Runs `./generate` to regenerate spec documentation
+7. Runs `./test` to validate all changes
+
+## Prerequisites
+
+- Go toolchain installed
+- Target spec version is stabilized (directory does NOT end with `_exp`)
+- Feature exists in the target spec's `translate.go`
+- Feature has doc transform entries in `internal/doc/butane.yaml`
+
+## Usage
+
+```bash
+# Interactive mode - will ask for details
+/remove-feature
+
+# Specify the version and feature
+/remove-feature --distro openshift --version v4_22 --feature grub
+
+# With tracking reference
+/remove-feature --distro openshift --version v4_22 --feature grub --ref MCO-630
+```
+
+## Workflow
+
+### Step 1: Gather Requirements
+
+If not provided via arguments, ask the user:
+
+1. **Distro**: Which distro variant? (typically `openshift`)
+2. **Version**: Which stabilized version? (e.g., `v4_22`)
+3. **Feature**: Which feature to remove? (e.g., `grub`)
+4. **Reference**: Optional tracking issue (e.g., `MCO-630`, `#515`)
+
+### Step 2: Pre-flight Validation
+
+Run these checks:
+
+```bash
+# Verify target directory exists and is NOT experimental
+ls -la config/{distro}/{version}/
+
+# Verify version does NOT end with _exp
+# CRITICAL: Only remove features from stabilized specs
+
+# Check git status
+git status --porcelain
+```
+
+**Stop if**:
+- Target directory does not exist
+- Version ends with `_exp` (experimental specs should be modified differently)
+- Working directory has unexpected uncommitted changes
+
+### Step 3: Identify Feature Code
+
+Read the target files to locate the feature:
+
+```bash
+# Read translate.go to find feature function
+cat config/{distro}/{version}/translate.go
+
+# Read translate_test.go to find test cases
+cat config/{distro}/{version}/translate_test.go
+
+# Read butane.yaml to find doc transform entries
+cat internal/doc/butane.yaml
+```
+
+**Identify**:
+1. The function call in the main translation pipeline (e.g., `ts = translateUserGrubCfg(&cfg, &ts)`)
+2. The function definition (e.g., `func translateUserGrubCfg(...)`)
+3. The test case block (e.g., `// Test Grub config` test struct)
+4. The butane.yaml transform entries with `replacement: "Unsupported"` and `max` version
+
+**Stop if** the feature code is not found in `translate.go` - it may have already been removed or never existed in this version.
+
+### Step 4: Remove Translation Function Call
+
+**File**: `config/{distro}/{version}/translate.go`
+
+Read the file and find the function call within the main `ToMachineConfig{Version}Unvalidated()` function.
+
+Remove the line calling the feature's translation function. For example:
+
+```go
+// REMOVE THIS LINE:
+ts = translateUserGrubCfg(&cfg, &ts)
+```
+
+Use the Edit tool:
+```
+oldString: "\tts = translateUserGrubCfg(&cfg, &ts)\n"
+newString: ""
+```
+
+### Step 5: Remove Translation Function Definition
+
+**File**: `config/{distro}/{version}/translate.go`
+
+Remove the entire function definition. The function is typically at the end of the file.
+
+For the GRUB removal pattern, remove the entire `translateUserGrubCfg` function:
+
+```go
+// REMOVE THIS ENTIRE BLOCK:
+
+// fcos config generates a user.cfg file using append; however, OpenShift config
+// does not support append (since MCO does not support it). Let change the file to use contents
+func translateUserGrubCfg(config *types.Config, ts *translate.TranslationSet) translate.TranslationSet {
+    // ... function body ...
+}
+```
+
+Use the Edit tool to remove from the comment above the function through the closing brace.
+
+### Step 6: Clean Up Dead Imports
+
+After removing the function, check if any imports are now unused. Common imports that may become dead:
+
+- For GRUB removal: no imports typically become dead (the remaining code uses the same packages)
+
+If imports are dead, remove them. Run `./test` later to catch any remaining issues.
+
+### Step 7: Remove Test Cases
+
+**File**: `config/{distro}/{version}/translate_test.go`
+
+Read the file and identify the test case block for the removed feature. Test cases are typically marked with a comment like `// Test Grub config` and consist of a struct literal in the test table.
+
+Remove the entire test case struct. For GRUB removal, this includes:
+- The comment marker (e.g., `// Test Grub config`)
+- The Config input struct
+- The expected result.MachineConfig output struct  
+- The expected translate.Translation slice
+
+Use the Edit tool to remove the entire block. Be careful to:
+- Include the leading comment
+- Include all three struct elements (input, expected output, expected translations)
+- Preserve the closing of the test table (`}` and `for` loop)
+
+### Step 8: Update Doc Descriptors
+
+**File**: `internal/doc/butane.yaml`
+
+Find the doc transform entries for the removed feature. These have the pattern:
+
+```yaml
+transforms:
+  - regex: ".*"
+    replacement: "Unsupported"
+    if:
+      - variant: openshift
+        max: {PREVIOUS_VERSION}
+```
+
+**Determine the new max version**:
+- From the directory version `v4_22`, derive `4.22.0`
+- The current `max` should be the previous stabilized version (e.g., `4.21.0`)
+- Bump `max` to the new version: `4.22.0`
+
+**Update ALL occurrences** for the feature. For GRUB, there are 4 entries:
+1. `grub` itself
+2. `grub.users`
+3. `grub.users.name`
+4. `grub.users.password_hash`
+
+Use the Edit tool for each occurrence:
+```
+oldString: "max: 4.21.0"
+newString: "max: 4.22.0"
+```
+
+**IMPORTANT**: Only update `max` values within the feature's section. Verify the surrounding context (field names) to avoid changing unrelated transforms.
+
+Alternatively, if all occurrences have the same old value, use `replaceAll` with enough context to scope the changes correctly.
+
+### Step 9: Regenerate Documentation
+
+Run the documentation generator:
+
+```bash
+./generate
+```
+
+**Expected outcome**: The `docs/config-openshift-{version}.md` file is updated, with the removed feature's fields now showing "Unsupported" instead of their original descriptions.
+
+Verify the change:
+
+```bash
+git diff docs/config-openshift-{version}.md
+```
+
+The diff should show lines like:
+```
+-* **_grub_** (object): describes the desired GRUB bootloader configuration.
++* **_grub_** (object): Unsupported
+```
+
+If `./generate` fails, check the butane.yaml changes for syntax errors.
+
+### Step 10: Run Tests
+
+```bash
+./test
+```
+
+**Expected outcome**: All tests pass.
+
+If tests fail:
+1. Check for compilation errors (dead imports, missing functions)
+2. Check for test expectation mismatches
+3. Fix and re-run
+
+### Step 11: Report Results
+
+Provide a comprehensive summary:
+
+```
+Feature "{feature}" removed from {distro}/{version}
+
+Files Modified:
+  - config/{distro}/{version}/translate.go (-N lines)
+  - config/{distro}/{version}/translate_test.go (-N lines)
+  - internal/doc/butane.yaml (N version bumps)
+  - docs/config-{distro}-{version}.md (regenerated, N fields -> "Unsupported")
+
+Tests: PASSED
+Docs: REGENERATED
+
+Suggested commit message:
+
+  {distro}/{version}: Remove {feature_description}
+
+  {reason for removal, e.g., "Support is still missing in the MCO."}
+
+  See: {reference_link}
+  See: #{github_issue}
+```
+
+## Checklist Coverage
+
+This skill automates the following steps:
+
+- ✅ Remove feature translation function call from `translate.go`
+- ✅ Remove feature translation function definition from `translate.go`
+- ✅ Remove related test cases from `translate_test.go`
+- ✅ Bump `max` version in `internal/doc/butane.yaml` for all feature fields
+- ✅ Regenerate documentation via `./generate`
+- ✅ Validate changes via `./test`
+
+## What's NOT Covered
+
+- ❌ **Determining which features to remove** - requires knowledge of MCO support status
+- ❌ **Removing features from experimental specs** - experimental specs should use different approaches
+- ❌ **Removing schema definitions** - this skill only removes translation/test code; schemas are inherited from parent and remain (they just become dead code for that version)
+- ❌ **Removing validation logic** - if the feature has validation in `validate.go`, that must be handled separately
+- ❌ **Creating git commits** - user should review changes first
+- ❌ **Updating release notes** - user should note the removal if appropriate
+
+## Example Output
+
+```
+/remove-feature --distro openshift --version v4_22 --feature grub --ref MCO-630
+
+Validating prerequisites...
+✅ Target directory exists: config/openshift/v4_22
+✅ Version is stabilized (not experimental)
+✅ Git working directory is clean
+
+Identifying feature code...
+✅ Found function call: ts = translateUserGrubCfg(&cfg, &ts)
+✅ Found function definition: translateUserGrubCfg (21 lines)
+✅ Found test case: // Test Grub config (83 lines)
+✅ Found 4 butane.yaml transform entries (max: 4.21.0)
+
+Phase 1: Remove translation code
+  ✅ Removed function call from translate.go
+  ✅ Removed function definition from translate.go (-22 lines)
+
+Phase 2: Remove test cases
+  ✅ Removed test case from translate_test.go (-83 lines)
+
+Phase 3: Update doc descriptors
+  ✅ Bumped max: 4.21.0 → 4.22.0 for grub (4 entries)
+
+Phase 4: Regenerate docs
+  ✅ ./generate completed
+  ✅ docs/config-openshift-v4_22.md updated (4 fields → "Unsupported")
+
+Phase 5: Validate
+  ✅ ./test passed
+
+Feature "grub" removed from openshift/v4_22
+
+Suggested commit message:
+
+  openshift/v4_22: Remove GRUB config support
+
+  See: https://issues.redhat.com/browse/MCO-630
+  See: #515
+```
+
+## References
+
+- Design document: `.opencode/skills/remove-feature/DESIGN.md`
+- Examples: `.opencode/skills/remove-feature/examples/`
+- Example commits: `4a2be91`, `2d9a25e`, `aa6ad0b`, `9821f9b`, `cd75f80`, `1f65fb6`
+- Current experimental spec with GRUB code: `config/openshift/v4_22_exp/translate.go:264-285`
+- Doc descriptors: `internal/doc/butane.yaml:402-438`
diff --git a/.opencode/skills/stabilize-spec/SKILL.md b/.opencode/skills/stabilize-spec/SKILL.md
@@ -0,0 +1,597 @@
+---
+name: stabilize-spec
+description: Stabilize experimental Butane config spec versions
+---
+
+# Stabilize Spec Version
+
+## What it does
+
+Automates the complete stabilization workflow for Butane spec versions:
+
+**Phase 1: Stabilize Experimental → Stable**
+1. Validating the working directory and checking prerequisites
+2. Renaming the experimental directory to stable (e.g., `v1_7_exp` → `v1_7`)
+3. Updating all package statements in the renamed directory
+4. Updating imports in the stabilized spec (base dependencies, Ignition versions)
+5. Updating `config/config.go` registration (for distro specs only)
+
+**Phase 2: Create Next Experimental Version**
+6. Copying the newly stabilized version to create the next experimental version (e.g., `v1_7` → `v1_8_exp`)
+7. Updating package statements in the new experimental directory
+8. Bumping base and Ignition dependencies to experimental versions
+9. Registering the new experimental version in `config/config.go`
+
+**Phase 3: Validation & Documentation**
+10. Running tests to validate all changes
+11. Running `./generate` to update documentation
+12. Reporting all changes and suggesting next steps
+
+## Prerequisites
+
+- Clean git working directory (or only expected changes)
+- Go toolchain installed
+- Experimental spec version exists
+- Target stable version doesn't already exist
+
+## Usage
+
+```bash
+# Stabilize a base version (creates v0_7 stable + v0_8_exp experimental)
+/stabilize-spec --type base --version v0_7_exp
+
+# Stabilize a distro version (creates v1_7 stable + v1_8_exp experimental)
+/stabilize-spec --type fcos --version v1_7_exp
+
+# Stabilize a distro version with Ignition downgrade
+/stabilize-spec --type openshift --version v4_21_exp --base-version v1_6 --ignition-version v3_5
+
+# Skip creating the next experimental version (not recommended)
+/stabilize-spec --type fcos --version v1_7_exp --skip-next-exp
+```
+
+## Workflow
+
+### Step 1: Gather Requirements
+
+If not provided via arguments, ask the user:
+
+1. **Spec type**: base, fcos, openshift, flatcar, r4e, or fiot?
+2. **Version to stabilize**: Which experimental version? (e.g., `v1_7_exp`, `v4_21_exp`)
+3. **For distro specs only**:
+   - Which stable base version to depend on? (e.g., `v1_6`, `v0_6`)
+   - Does the Ignition version change? If yes, what's the target? (e.g., `v3_5`)
+4. **Create next experimental version?** (default: yes, per stabilize-checklist.md)
+   - If yes, calculate the next version number (e.g., v1_7 → v1_8_exp)
+   - Ask which experimental base to use (e.g., v0_8_exp)
+   - Ask which experimental Ignition version to use (e.g., v3_7_experimental)
+
+### Step 2: Pre-flight Validation
+
+Run these checks in parallel:
+
+```bash
+# Check git status
+git status --porcelain
+
+# Verify experimental directory exists
+ls -la base/{version}/ || ls -la config/{distro}/{version}/
+
+# Verify stable directory doesn't exist
+ls -la base/{stable_version}/ || ls -la config/{distro}/{stable_version}/
+
+# For distro specs: verify base version exists
+ls -la base/{base_version}/ || ls -la config/fcos/{base_version}/
+```
+
+**Validation criteria**:
+- Git working directory should be clean or only contain expected changes
+- Source experimental directory must exist
+- Target stable directory must NOT exist
+- If distro spec: base dependency must exist
+
+If any check fails, report the error and stop.
+
+### Step 3: Rename Directory
+
+Use `git mv` to rename the experimental directory:
+
+```bash
+# For base specs:
+git mv base/{version} base/{stable_version}
+
+# For distro specs:
+git mv config/{distro}/{version} config/{distro}/{stable_version}
+```
+
+**Example**:
+```bash
+git mv config/fcos/v1_7_exp config/fcos/v1_7
+```
+
+### Step 4: Update Package Statements
+
+Find all `.go` files in the renamed directory and update package statements:
+
+```bash
+# Find all .go files
+find {renamed_directory} -name "*.go"
+
+# For each file, update the package statement
+# OLD: package v1_7_exp
+# NEW: package v1_7
+```
+
+Use the Edit tool to replace:
+```
+oldString: "package {version}"
+newString: "package {stable_version}"
+```
+
+**Files typically affected**:
+- Base specs: schema.go, translate.go, translate_test.go, util.go, validate.go, validate_test.go (6 files)
+- Distro specs: schema.go, translate.go, translate_test.go, validate.go, validate_test.go (5-7 files)
+
+### Step 5: Update Imports (Distro Specs Only)
+
+For distro specs, update base dependency imports:
+
+1. **Identify files that import base**:
+   - schema.go
+   - translate_test.go
+   - validate.go
+   - validate_test.go
+
+2. **Update base import**:
+```go
+// OLD:
+import (
+    base "github.com/coreos/butane/base/v0_7_exp"
+)
+
+// NEW:
+import (
+    base "github.com/coreos/butane/base/v0_6"
+)
+```
+
+3. **For OpenShift specs, also update fcos import in schema.go**:
+```go
+// OLD:
+import (
+    fcos "github.com/coreos/butane/config/fcos/v1_7_exp"
+)
+
+// NEW:
+import (
+    fcos "github.com/coreos/butane/config/fcos/v1_6"
+)
+```
+
+### Step 6: Update Ignition Imports (If Version Changes)
+
+If the Ignition version is changing (common for OpenShift stabilizations):
+
+1. **Find files that import Ignition types**:
+   - result/schema.go (OpenShift only)
+   - translate.go
+   - translate_test.go
+
+2. **Update Ignition imports**:
+```go
+// OLD:
+import (
+    "github.com/coreos/ignition/v2/config/v3_6_experimental/types"
+)
+
+// NEW:
+import (
+    "github.com/coreos/ignition/v2/config/v3_5/types"
+)
+```
+
+3. **Rename translation functions in translate.go**:
+   - `ToIgn3_6Unvalidated` → `ToIgn3_5Unvalidated`
+   - `ToIgn3_6` → `ToIgn3_5`
+   - Update function comments
+   - Update `cutil.Translate` and `cutil.TranslateBytes` calls
+
+4. **Update test version strings in translate_test.go**:
+```go
+// OLD:
+Version: "3.6.0-experimental",
+
+// NEW:
+Version: "3.5.0",
+```
+
+### Step 7: Update config/config.go (Distro Specs Only)
+
+For distro specs, update the registration in `config/config.go`:
+
+1. **Update import statement**:
+```go
+// OLD:
+import (
+    fcos1_7_exp "github.com/coreos/butane/config/fcos/v1_7_exp"
+)
+
+// NEW:
+import (
+    fcos1_7 "github.com/coreos/butane/config/fcos/v1_7"
+)
+```
+
+2. **Update RegisterTranslator call in init()**:
+```go
+// OLD:
+RegisterTranslator("fcos", "1.7.0-experimental", fcos1_7_exp.ToIgn3_6Bytes)
+
+// NEW:
+RegisterTranslator("fcos", "1.7.0", fcos1_7.ToIgn3_6Bytes)
+```
+
+**Pattern**: Remove `-experimental` suffix from version string, update import alias
+
+### Step 8: Create Next Experimental Version
+
+**Note**: This step implements lines 20-21 (base) and 28-30 (distro) from `.github/ISSUE_TEMPLATE/stabilize-checklist.md`.
+
+If `--skip-next-exp` was NOT specified (default behavior):
+
+#### 8a. Calculate Next Version
+
+Determine the next experimental version:
+- For base: `v0_7` → `v0_8_exp`
+- For fcos: `v1_7` → `v1_8_exp`  
+- For openshift: `v4_21` → `v4_22_exp`
+
+Parse the stable version number and increment it.
+
+#### 8b. Copy Stable to New Experimental
+
+Use `cp -r` or recursive copy to duplicate the newly stabilized directory:
+
+```bash
+# For base specs:
+cp -r base/{stable_version} base/{next_exp_version}
+
+# For distro specs:
+cp -r config/{distro}/{stable_version} config/{distro}/{next_exp_version}
+
+# Then add to git:
+git add base/{next_exp_version} || git add config/{distro}/{next_exp_version}
+```
+
+**Example**:
+```bash
+cp -r config/fcos/v1_7 config/fcos/v1_8_exp
+git add config/fcos/v1_8_exp
+```
+
+#### 8c. Update Package Statements in New Experimental
+
+Find all `.go` files in the new experimental directory and update package statements:
+
+```bash
+# For each .go file in the new experimental directory:
+# OLD: package v1_7
+# NEW: package v1_8_exp
+```
+
+Use the Edit tool to replace in each file.
+
+#### 8d. Update Base Dependency (Distro Specs Only)
+
+For distro specs, update the base import to use the new experimental base:
+
+```go
+// In schema.go, translate_test.go, validate.go, validate_test.go:
+// OLD:
+import (
+    base "github.com/coreos/butane/base/v0_7"
+)
+
+// NEW:
+import (
+    base "github.com/coreos/butane/base/v0_8_exp"
+)
+```
+
+**For OpenShift**, also update fcos import in schema.go if fcos has a new experimental version.
+
+#### 8e. Update Ignition Imports (If Version Increases)
+
+If the Ignition version is increasing (e.g., v3_6 → v3_7_experimental):
+
+1. **Update Ignition imports in**:
+   - result/schema.go (OpenShift only)
+   - translate.go
+   - translate_test.go
+
+```go
+// OLD:
+import (
+    "github.com/coreos/ignition/v2/config/v3_6/types"
+)
+
+// NEW:
+import (
+    "github.com/coreos/ignition/v2/config/v3_7_experimental/types"
+)
+```
+
+2. **Rename translation functions in translate.go**:
+   - `ToIgn3_6Unvalidated` → `ToIgn3_7Unvalidated`
+   - `ToIgn3_6` → `ToIgn3_7`
+   - Update function comments
+   - Update `cutil.Translate` and `cutil.TranslateBytes` calls
+
+3. **Update test version strings in translate_test.go**:
+```go
+// OLD:
+Version: "3.6.0",
+
+// NEW:
+Version: "3.7.0-experimental",
+```
+
+#### 8f. Add New Experimental to config/config.go (Distro Specs Only)
+
+For distro specs, register the new experimental version in `config/config.go`:
+
+1. **Add import statement**:
+```go
+// After the just-stabilized import:
+import (
+    fcos1_7 "github.com/coreos/butane/config/fcos/v1_7"
+    fcos1_8_exp "github.com/coreos/butane/config/fcos/v1_8_exp"  // ADD THIS
+)
+```
+
+2. **Add RegisterTranslator call in init()**:
+```go
+// After the just-stabilized registration:
+RegisterTranslator("fcos", "1.7.0", fcos1_7.ToIgn3_6Bytes)
+RegisterTranslator("fcos", "1.8.0-experimental", fcos1_8_exp.ToIgn3_7Bytes)  // ADD THIS
+```
+
+**Pattern**: Add `-experimental` suffix, use experimental Ignition version
+
+### Step 9: Run Tests
+
+Execute the test suite to validate all changes:
+
+```bash
+./test
+```
+
+**Expected outcome**: All tests should pass.
+
+If tests fail:
+- Review the error messages
+- Check for missed imports or package statements
+- Verify function renames are complete
+- Report the failure to the user and suggest manual review
+
+### Step 10: Regenerate Documentation
+
+Run the documentation generator:
+
+```bash
+./generate
+```
+
+**Expected outcome**: Documentation files in `docs/` are updated.
+
+Check for uncommitted changes:
+```bash
+git status docs/
+```
+
+If `./generate` fails or produces unexpected changes, report to the user.
+
+### Step 11: Report Results
+
+Provide a comprehensive summary:
+
+```
+✅ Spec stabilization complete!
+
+## Phase 1: Stabilization
+### Directory Renamed:
+- {old_path} → {new_path}
+
+### Files Modified:
+- {count} files with package statement updates
+- {count} files with import updates
+- config/config.go updated (distro specs only)
+
+## Phase 2: Next Experimental Version Created
+### Directory Created:
+- {new_exp_path}
+
+### Files Modified:
+- {count} files with package statement updates
+- {count} files with import updates (bumped to experimental versions)
+- config/config.go updated with new experimental registration
+
+## Validation:
+✅ Tests passed (./test)
+✅ Documentation regenerated (./generate)
+
+## Git Status:
+{output of git status}
+
+## Next Steps (from stabilize-checklist.md):
+
+1. Review the changes with `git diff`
+2. Consider creating TWO commits:
+   - Commit 1: Stabilization (e.g., "fcos/v1_7_exp: stabilize to v1_7")
+   - Commit 2: New experimental (e.g., "fcos: add v1_8_exp")
+3. Update docs/upgrading-*.md (requires manual content creation)
+4. Note the stabilization in docs/release-notes.md
+5. If this is a base stabilization, stabilize the distro versions that depend on it
+
+## Suggested commit messages:
+
+### Commit 1: Stabilization
+{distro}/v{X}_exp: stabilize to v{X}
+
+- Rename {distro}/v{X}_exp to {distro}/v{X}
+- Update package statements and imports
+- Drop -experimental from config registration
+{additional details based on what changed}
+
+### Commit 2: New Experimental
+{distro}: add v{X+1}_exp
+
+- Copy {distro}/v{X} to {distro}/v{X+1}_exp
+- Update package statements to v{X+1}_exp
+- Bump base dependency to {base}_exp
+- Bump Ignition version to v{Y}_experimental
+- Add experimental config registration
+```
+
+## Checklist Coverage
+
+This skill automates the following items from `.github/ISSUE_TEMPLATE/stabilize-checklist.md`:
+
+### For Base Stabilization (lines 17-21):
+- ✅ Rename `base/vB_exp` to `base/vB` and update `package` statements
+- ✅ Update imports
+- ✅ **Copy `base/vB` to `base/vB+1_exp`**
+- ✅ **Update `package` statements in `base/vB+1_exp`**
+
+### For Distro Stabilization (lines 23-30):
+- ✅ Rename `config/distro/vD_exp` to `config/distro/vD` and update `package` statements
+- ✅ Update imports
+- ✅ Drop `-experimental` from `init()` in `config/config.go`
+- ✅ **Copy `config/distro/vD` to `config/distro/vD+1_exp`**
+- ✅ **Update `package` statements in `config/distro/vD+1_exp`**
+- ✅ **Bump base dependency to `base/vB+1_exp`**
+- ✅ **Import `config/vD+1_exp` in `config/config.go` and add experimental registration**
+
+### For Ignition Spec Version Bumps (lines 32-35):
+- ✅ Bump Ignition types imports in new experimental version
+- ✅ Rename `ToIgnI` functions in new experimental version
+- ✅ Bump Ignition spec versions in translate_test.go
+
+### For Documentation (lines 37-40):
+- ✅ Run `./generate` to regenerate spec docs
+
+## What's NOT Covered
+
+This skill does NOT automate:
+
+- ❌ **Bumping go.mod for Ignition releases** - done before stabilization (line 14)
+- ❌ **Updating vendor directory** - done before stabilization (line 14)
+- ❌ **Dropping -experimental from examples in docs/** - requires content analysis (line 27)
+- ❌ **Updating `internal/doc/main.go`** - requires manual editing (line 39)
+- ❌ **Updating docs/specs.md** - requires manual editing (line 41)
+- ❌ **Updating docs/upgrading-*.md** - requires content creation (line 42)
+- ❌ **Writing release notes** - requires human judgment (line 43)
+- ❌ **Creating git commits** - user should review changes first
+
+These steps require human judgment and should be done manually following the stabilization.
+
+## Example Output
+
+```
+/stabilize-spec --type fcos --version v1_7_exp
+
+═══════════════════════════════════════════════
+ PHASE 1: Stabilize v1_7_exp → v1_7
+═══════════════════════════════════════════════
+
+Validating prerequisites...
+✅ Git working directory is clean
+✅ Experimental version exists: config/fcos/v1_7_exp
+✅ Stable version doesn't exist: config/fcos/v1_7
+✅ Base dependency exists: base/v0_7
+
+Renaming directory...
+✅ Renamed: config/fcos/v1_7_exp → config/fcos/v1_7
+
+Updating package statements (5 files)...
+✅ config/fcos/v1_7/schema.go
+✅ config/fcos/v1_7/translate.go
+✅ config/fcos/v1_7/translate_test.go
+✅ config/fcos/v1_7/validate.go
+✅ config/fcos/v1_7/validate_test.go
+
+Updating imports...
+✅ Updated base import in 4 files
+
+Updating config/config.go...
+✅ Import statement updated: fcos1_7_exp → fcos1_7
+✅ Registration updated: removed -experimental suffix
+
+═══════════════════════════════════════════════
+ PHASE 2: Create Next Experimental v1_8_exp
+═══════════════════════════════════════════════
+
+Calculating next version...
+✅ Next version: v1_8_exp
+✅ Next experimental base: v0_8_exp
+✅ Next Ignition version: v3_7_experimental
+
+Copying stable to experimental...
+✅ Copied: config/fcos/v1_7 → config/fcos/v1_8_exp
+
+Updating package statements (5 files)...
+✅ config/fcos/v1_8_exp/schema.go
+✅ config/fcos/v1_8_exp/translate.go
+✅ config/fcos/v1_8_exp/translate_test.go
+✅ config/fcos/v1_8_exp/validate.go
+✅ config/fcos/v1_8_exp/validate_test.go
+
+Updating imports to experimental versions...
+✅ Updated base import: v0_7 → v0_8_exp (4 files)
+✅ Updated Ignition import: v3_6 → v3_7_experimental (2 files)
+
+Updating translation functions...
+✅ Renamed: ToIgn3_6Unvalidated → ToIgn3_7Unvalidated
+✅ Renamed: ToIgn3_6 → ToIgn3_7
+✅ Updated: ToIgn3_6Bytes → ToIgn3_7Bytes
+
+Updating config/config.go...
+✅ Added import: fcos1_8_exp
+✅ Added registration: 1.8.0-experimental
+
+═══════════════════════════════════════════════
+ PHASE 3: Validation
+═══════════════════════════════════════════════
+
+Running tests...
+✅ All tests passed (./test)
+
+Regenerating documentation...
+✅ Documentation updated (./generate)
+
+═══════════════════════════════════════════════
+ SUMMARY
+═══════════════════════════════════════════════
+
+📊 Phase 1 (Stabilization):
+  - 1 directory renamed
+  - 5 files updated in config/fcos/v1_7/
+  - config/config.go updated
+
+📊 Phase 2 (New Experimental):
+  - 1 directory created (2874 lines)
+  - 5 files updated in config/fcos/v1_8_exp/
+  - config/config.go updated
+
+✅ Tests: PASSED
+✅ Docs: REGENERATED
+
+🎯 Ready for review and commit!
+```
+
+## References
+
+- Design document: `.opencode/skills/stabilize-spec/DESIGN.md`
+- Examples: `.opencode/skills/stabilize-spec/examples/`
+- Issue template: `.github/ISSUE_TEMPLATE/stabilize-checklist.md`
+- Development docs: `docs/development.md`
PATCH

echo "Gold patch applied."
