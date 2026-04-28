#!/usr/bin/env bash
set -euo pipefail

cd /workspace/content

# Idempotency guard
if grep -qF "- **OCP4/Kubernetes rules** live under `applications/openshift/`, organized by c" ".claude/CLAUDE.md" && grep -qF "6. **Present results** organized by match strength. For every rule, include a **" ".claude/skills/find-rule/SKILL.md" && grep -qF "2. If the `product` field does not list all the products from the argument, warn" ".claude/skills/manage-profile/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -0,0 +1,301 @@
+# ComplianceAsCode/content
+
+## Project Overview
+
+This repository produces SCAP data streams, Ansible playbooks, Bash scripts, and other artifacts for compliance scanning and remediation.
+
+Each supported operating system or platform is called a **product**. To see the full list of products, check the subdirectories under `products/` — each subdirectory name is a product ID (e.g., `rhel9`, `ocp4`, `ubuntu2404`). Product-specific configuration lives in `products/<product>/product.yml`.
+
+## Repository Structure
+
+```
+applications/openshift/    # OCP4 and Kubernetes rules, organized by component
+linux_os/guide/            # Linux rules (RHEL, RHCOS, etc.), organized by system area
+controls/                  # Compliance framework mappings (CIS, STIG, SRG, NIST, etc.)
+products/                  # Product definitions, profiles, and product-specific controls
+shared/templates/          # Reusable check/remediation templates (60+ types)
+shared/macros/             # Jinja2 macro files for generating OVAL, Ansible, Bash, etc.
+components/                # Component definitions mapping rules to packages/groups
+```
+
+### Discovering Rule Directories
+
+- **OCP4/Kubernetes rules** live under `applications/openshift/`, organized by component (e.g., `api-server/`, `kubelet/`, `etcd/`). Each component directory contains rule subdirectories. The rule ID prefix typically matches the component directory name with hyphens replaced by underscores (e.g., rules in `api-server/` use the `api_server_` prefix). Browse `applications/openshift/` to see all component directories.
+- **Linux rules** (RHEL, RHCOS, Fedora, Ubuntu, etc.) live under `linux_os/guide/`, organized by system area (e.g., `system/`, `services/`, `auditing/`). Browse the subdirectories to find the appropriate category for a rule.
+- When placing a new rule, find 2-3 existing rules with a similar prefix or topic and place the new rule alongside them.
+
+## Rule Format
+
+Each rule lives in its own directory. The **directory name is the rule ID**. The directory contains `rule.yml` and optionally a `tests/` subdirectory.
+
+### `rule.yml` Fields
+
+```yaml
+documentation_complete: true          # Must be true for the rule to be built
+
+title: 'Short descriptive title'
+
+description: |-                        # Full description, supports HTML tags and Jinja2 macros
+    Description text here.
+
+rationale: |-                          # Why this rule matters
+    Rationale text here.
+
+severity: medium                       # low, medium, high, unknown
+
+identifiers:                           # Product-specific CCE identifiers
+    cce@ocp4: CCE-XXXXX-X
+    cce@rhel9: CCE-XXXXX-X
+
+references:                            # Compliance framework references
+    cis@ocp4: 1.2.3                    # CIS benchmark section
+    nist: CM-6,CM-6(1)                 # NIST 800-53 controls
+    srg: SRG-APP-000516-CTR-001325     # DISA SRG ID
+    stigid@rhel9: RHEL-09-XXXXXX       # STIG rule ID (product-scoped)
+    nerc-cip: CIP-003-8 R6             # NERC CIP references
+    pcidss: Req-2.2                    # PCI DSS requirements
+
+ocil_clause: 'condition when rule fails'  # Used in OCIL questionnaire
+
+ocil: |-                               # Manual check instructions
+    Run the following command:
+    <pre>$ oc get ...</pre>
+
+platform: ocp4                         # Platform applicability (optional)
+
+warnings:                              # Optional warnings section
+    - general: |-
+        Warning text, often includes openshift_cluster_setting macro.
+
+template:                              # Optional - uses a shared template for checks
+    name: yamlfile_value
+    vars:
+        ocp_data: "true"
+        filepath: '/api/path/here'
+        yamlpath: '.spec.field'
+        values:
+          - value: 'expected_value'
+            operation: "pattern match"
+
+fixtext: 'Remediation instructions'    # STIG fixtext (optional)
+srg_requirement: 'SRG requirement'     # SRG requirement text (optional)
+```
+
+## Templates
+
+Templates generate OVAL checks, Ansible playbooks, and Bash remediation scripts automatically.
+
+### `yamlfile_value` (primary OCP4 template)
+
+Checks values in YAML/JSON files or API responses.
+
+```yaml
+template:
+    name: yamlfile_value
+    vars:
+        ocp_data: "true"                        # "true" for OCP API data
+        filepath: '/apis/...'                   # API path or file path
+        yamlpath: '.spec.config.field'          # JSONPath-like expression
+        check_existence: "at_least_one_exists"  # Optional existence check
+        entity_check: "at least one"            # How to evaluate multiple matches
+        values:
+          - value: 'expected'                   # Expected value or regex
+            type: "string"                      # string, int, boolean
+            operation: "pattern match"          # equals, not equal, pattern match,
+                                                # greater than or equal, less than or equal
+            entity_check: "at least one"        # Per-value entity check
+```
+
+### `file_permissions` (RHEL)
+
+```yaml
+template:
+    name: file_permissions
+    vars:
+        filepath: /etc/cron.d/
+        filemode: '0700'
+```
+
+### `shell_lineinfile` (RHEL)
+
+```yaml
+template:
+    name: shell_lineinfile
+    vars:
+        path: '/etc/sysconfig/sshd'
+        parameter: 'SSH_USE_STRONG_RNG'
+        value: '32'
+        datatype: int                       # Optional
+        no_quotes: 'true'                   # Optional
+```
+
+### `sysctl` (RHEL)
+
+```yaml
+template:
+    name: sysctl
+    vars:
+        sysctlvar: net.ipv6.conf.all.accept_ra
+        datatype: int
+```
+
+### `service_enabled` / `service_disabled` (RHEL)
+
+```yaml
+template:
+    name: service_disabled
+    vars:
+        servicename: avahi
+```
+
+### `package_installed` / `package_removed` (RHEL)
+
+```yaml
+template:
+    name: package_removed
+    vars:
+        pkgname: avahi
+        pkgname@ubuntu2204: avahi-daemon    # Platform-specific overrides
+```
+
+## Common Jinja2 Macros
+
+Used in rule descriptions, OCIL, fixtext, and warnings fields:
+
+- `{{{ openshift_cluster_setting("/api/path") }}}` - Generates OCP API check instructions
+- `{{{ openshift_filtered_cluster_setting({'/api/path': jqfilter}) }}}` - Filtered API check with jq
+- `{{{ openshift_filtered_path('/api/path', jqfilter) }}}` - Generates filtered filepath for templates
+- `{{{ full_name }}}` - Expands to product full name (e.g., "Red Hat Enterprise Linux 9")
+- `{{{ xccdf_value("var_name") }}}` - References an XCCDF variable
+- `{{{ weblink("https://...") }}}` - Creates an HTML link
+- `{{{ describe_service_disable(service="name") }}}` - Standard service disable description
+- `{{{ describe_service_enable(service="name") }}}` - Standard service enable description
+- `{{{ describe_file_permissions(file="/path", perms="0700") }}}` - File permission description
+- `{{{ describe_sysctl_option_value(sysctl="key", value="val") }}}` - Sysctl description
+- `{{{ complete_ocil_entry_sysctl_option_value(sysctl="key", value="val") }}}` - Full OCIL for sysctl
+- `{{{ complete_ocil_entry_package(package="name") }}}` - Full OCIL for package check
+- `{{{ fixtext_package_removed("name") }}}` - Fixtext for package removal
+- `{{{ fixtext_sysctl("key", "value") }}}` - Fixtext for sysctl setting
+- `{{{ fixtext_directory_permissions(file="/path", mode="0600") }}}` - Fixtext for dir permissions
+
+## Control File Format
+
+Control files map compliance framework requirements to rules. They exist in two layouts:
+
+### Single-file format
+
+```yaml
+# controls/stig_rhel9.yml (or products/rhel9/controls/stig_rhel9.yml)
+policy: 'Red Hat Enterprise Linux 9 STIG'
+title: 'DISA STIG for RHEL 9'
+id: stig_rhel9
+source: https://www.cyber.mil/stigs/downloads/
+version: V2R7
+reference_type: stigid
+product: rhel9
+
+levels:
+    - id: high
+    - id: medium
+    - id: low
+
+controls:
+    - id: RHEL-09-211010
+      levels:
+          - high
+      title: RHEL 9 must be a vendor-supported release.
+      rules:
+          - installed_OS_is_vendor_supported
+      status: automated
+```
+
+### Split-directory format
+
+```
+controls/cis_ocp.yml          # Top-level: policy, title, id, levels
+controls/cis_ocp/             # Directory with section files
+    section-1.yml             # Controls for section 1
+    section-2.yml             # Controls for section 2
+    ...
+```
+
+Section files contain nested controls:
+
+```yaml
+controls:
+    - id: '1'
+      title: Control Plane Components
+      controls:
+          - id: '1.1'
+            title: Master Node Configuration Files
+            controls:
+                - id: 1.1.1
+                  title: Ensure that the API server pod specification...
+                  status: automated
+                  rules:
+                      - file_permissions_kube_apiserver
+                  levels:
+                      - level_1
+```
+
+### Control entry fields
+
+- `id` - Control identifier (e.g., "RHEL-09-211010", "1.2.3")
+- `title` - Human-readable title
+- `levels` - Applicable compliance levels
+- `rules` - List of rule IDs that satisfy this control
+- `status` - `automated`, `manual`, `inherently met`, `does not meet`, `pending`, `not applicable`
+- `notes` - Optional notes explaining status or implementation
+
+## Profile File Format
+
+Profiles select which rules apply to a product. Located at `products/<product>/profiles/<name>.profile`.
+
+```yaml
+documentation_complete: true
+title: 'Profile Title'
+description: |-
+    Profile description text.
+platform: ocp4
+metadata:
+    version: V2R7
+    SMEs:
+        - github_username
+
+selections:
+    - control_id:all              # Include all rules from a control file
+    - rule_id                     # Include a specific rule
+    - '!rule_id'                  # Exclude a specific rule
+    - var_name=value              # Set a variable value
+```
+
+Common selection patterns:
+- `stig_rhel9:all` - Pull in all rules from the stig_rhel9 control file
+- `cis_ocp:all` - Pull in all rules from the cis_ocp control file
+- `!audit_rules_immutable_login_uids` - Exclude a specific rule
+- `var_sshd_set_keepalive=1` - Set a variable
+
+## Build Instructions
+
+```bash
+# Build a single product (full build)
+./build_product ocp4
+
+# Build data stream only (faster, skips guides and tables)
+./build_product ocp4 --datastream-only
+
+# Build with only specific rules (fastest, for testing individual rules)
+./build_product ocp4 --datastream-only --rule-id api_server_tls_security_profile
+```
+
+Build output goes to `build/`. The data stream file is at:
+`build/ssg-<product>-ds.xml`
+
+## Guidelines for Claude
+
+1. **Always show proposals before making changes.** Present the full content of any new or modified file and wait for explicit approval.
+2. **Follow existing patterns.** Before creating a rule, find 2-3 similar existing rules and match their style exactly.
+3. **Check for duplicates.** Before creating a new rule, search for existing rules that might already cover the requirement.
+4. **Use the correct directory.** Find existing rules with the same prefix to determine the right directory. When in doubt, browse `applications/openshift/` or `linux_os/guide/` to find the appropriate component or category.
+5. **Preserve formatting.** This project uses consistent YAML formatting. Match the indentation and style of surrounding content.
+6. **Don't invent references.** Only include reference IDs (CCE, CIS, STIG, SRG, NIST) that the user provides or that exist in source documents.
diff --git a/.claude/skills/find-rule/SKILL.md b/.claude/skills/find-rule/SKILL.md
@@ -0,0 +1,77 @@
+---
+disable-model-invocation: true
+---
+
+Search for existing rules that match the following requirement:
+
+$ARGUMENTS
+
+Follow these steps:
+
+1. **Extract key concepts** from the requirement text. Identify:
+   - Technical terms (e.g., "TLS", "audit", "encryption", "RBAC")
+   - Component references (e.g., "API server", "kubelet", "etcd", "SSH")
+   - Specific settings or parameters mentioned
+   - Any reference IDs (SRG-xxx, CIS section numbers, STIG IDs, NIST controls)
+
+2. **Respect scope constraints.** If the user specifies a scope (e.g., "only OpenShift control plane", "only node-level"), restrict results to that scope. Do not return rules outside the requested scope. OCP4/Kubernetes rules live under `applications/openshift/` and Linux rules live under `linux_os/guide/`. If no scope is specified, search both.
+
+3. **Search broadly** across rule titles, descriptions, and template configurations:
+   - Search `applications/openshift/` and `linux_os/guide/` for `rule.yml` files
+   - Search for keywords in titles, descriptions, template vars, and reference fields
+   - If reference IDs were provided, search for those exact IDs in rule.yml files
+
+4. **Check control files** in `controls/` and `products/*/controls/` for matching control IDs or titles that already map to this requirement.
+
+5. **Note product applicability** for each matched rule. Check the `identifiers` section of each rule.yml for `cce@<product>` entries (e.g., `cce@ocp4`, `cce@rhel9`). The product IDs after `@` correspond to subdirectory names under `products/`. This tells the user which products the rule applies to.
+
+6. **Present results** organized by match strength. For every rule, include a **Rationale** — a concise (1-2 sentence) explanation of why this rule satisfies or partially satisfies the requirement. Write the rationale so that a maintainer unfamiliar with the rule can understand the connection without reading the full rule.yml. Focus on *what the rule checks* and *how that maps to the requirement*.
+
+   **Strong matches** (title or template directly addresses the requirement):
+   - Rule ID, file path, title, severity
+   - Template type and key vars (if templated)
+   - Matching references (SRG, CIS, STIG, NIST)
+   - Product applicability (which products have CCE identifiers)
+   - Whether the rule has an automated template or is manual review only
+   - **Rationale:** Why this rule is a strong match for the requirement
+
+   **Partial matches** (related but not exact):
+   - Same fields as above
+   - **Rationale:** What aspect of the requirement this rule covers and what it does not
+
+   **Weak matches** (tangentially related):
+   - Rule ID, file path, title
+   - **Rationale:** Why it was included despite being tangential
+
+7. **Include a summary table** at the end mapping requirement aspects to rule IDs, so the user can quickly see coverage.
+
+8. **Always suggest a control structure** with a `notes` field that includes a concise rationale for each rule, explaining why it was included for this control. This helps maintainers understand the reasoning without needing to read every rule.yml. When no strong automated matches exist, say so clearly and use `status: partial` or `status: manual` as appropriate. Example:
+
+   ```yaml
+   - id: X.Y.Z
+     title: Control Title
+     status: automated
+     notes: |-
+         automated_rule_1 - Rationale for why this rule satisfies the control.
+         automated_rule_2 - Rationale for why this rule satisfies the control.
+     rules:
+         - automated_rule_1
+         - automated_rule_2
+   ```
+
+   For partial or manual controls, also include guidance for assessors:
+
+   ```yaml
+   - id: X.Y.Z
+     title: Control Title
+     status: partial
+     notes: |-
+         automated_rule_1 - Rationale for why this rule partially covers the control.
+         The remaining aspects of this control require manual verification: [manual steps].
+     rules:
+         - automated_rule_1
+   ```
+
+   When suggesting rules for partial/manual controls, only include rules that provide automated value. Omit rules that are themselves manual-only (no template, no automated check) unless they are the only matches available.
+
+9. **Rules can appear in multiple controls.** The build system handles this correctly. Each control should list the complete set of rules needed to satisfy it, even if some rules also appear in other controls. This ensures each control is self-contained and readers don't need to cross-reference other controls to understand coverage.
diff --git a/.claude/skills/manage-profile/SKILL.md b/.claude/skills/manage-profile/SKILL.md
@@ -0,0 +1,135 @@
+---
+disable-model-invocation: true
+---
+
+Create or update a versioned profile.
+
+Arguments: $ARGUMENTS
+
+Expected arguments: `<action> <profile_name> <product(s)> [version]`
+
+Actions:
+- `create` — Create a new versioned profile pair (versioned + unversioned)
+- `update` — Bump an existing profile to a new version
+
+For example:
+- `create cis ocp4 1.7.0`
+- `update cis ocp4 1.8.0`
+
+## Background: Profile Versioning Pattern
+
+This project uses a two-file versioning pattern for profiles (browse existing profiles under `products/<product>/profiles/` for examples):
+
+- **Versioned profile** (e.g., `cis-v1-7-0.profile`): Contains the actual `selections`, `metadata.version`, and all profile configuration. Users pin to this for a stable baseline.
+- **Unversioned profile** (e.g., `cis.profile`): Contains `extends: cis-v1-7-0` and no `selections` of its own. Users referencing this always get the latest version.
+
+When multiple products are specified (e.g., `ocp4,rhcos4`), both profile pairs are created/updated under their respective `products/<product>/profiles/` directories.
+
+---
+
+## Action: `create`
+
+### Step 1: Validate
+
+1. Parse the product list (comma-separated). Valid product IDs are subdirectory names under `products/`.
+2. Verify `products/<product>/profiles/` exists for each product.
+3. Check that the profile does not already exist. If it does, suggest using `update` instead.
+4. Convert the version to a filename-safe format by replacing dots with dashes (e.g., `2.0.0` → `v2-0-0`).
+
+### Step 2: Check for a Control File
+
+Check if a control file exists that matches the profile name. Control files live under `controls/` and `products/*/controls/`, typically named `<profile>_<product>.yml` or as a split directory with the same base name. If found:
+
+1. Read the control file's top-level YAML to check the `product` field.
+2. If the `product` field does not list all the products from the argument, warn the user and offer to update it. A control file needs all target products listed in its `product` field to work with each product's profile. Check existing multi-product control files for examples of this pattern.
+
+### Step 3: Show the Proposed Files
+
+For each product, show the two files that will be created:
+
+**Versioned profile** (`products/<product>/profiles/<name>-<version>.profile`):
+```yaml
+---
+documentation_complete: true
+
+title: '<Title> for <Product Full Name>'
+
+platform: <product>
+
+metadata:
+    version: <Version>
+
+description: |-
+    <Description text.>
+
+selections:
+    - <control_id>:all
+```
+
+**Unversioned profile** (`products/<product>/profiles/<name>.profile`):
+```yaml
+---
+documentation_complete: true
+
+title: '<Title> for <Product Full Name>'
+
+platform: <product>
+
+metadata:
+    version: <Version>
+
+description: |-
+    <Description text.>
+
+extends: <name>-<version>
+```
+
+Ask the user to confirm before creating.
+
+### Step 4: Apply
+
+Create all files for each product after approval.
+
+---
+
+## Action: `update`
+
+### Step 1: Validate
+
+1. Parse the product list.
+2. Locate the existing unversioned profile for each product at `products/<product>/profiles/<name>.profile`.
+3. Read the unversioned profile to find the current `extends` target (e.g., `cis-v1-7-0`).
+4. Read the current versioned profile to get its `selections` and other configuration.
+5. Convert the new version to filename-safe format (e.g., `2.1.0` → `v2-1-0`).
+
+If the unversioned profile doesn't use `extends`, warn the user that it doesn't follow the versioning pattern and offer to convert it.
+
+### Step 2: Show the Proposed Changes
+
+For each product, show what will happen:
+
+1. **New versioned profile** (`<name>-<new_version>.profile`): Created with the same `selections` as the current versioned profile (the user can modify selections afterward).
+2. **Previous versioned profile** (`<name>-<old_version>.profile`): Add `status: deprecated` to mark it as superseded.
+3. **Unversioned profile** (`<name>.profile`): Update `extends` to point to the new version and update `metadata.version`.
+
+Ask the user to confirm before applying.
+
+### Step 3: Apply
+
+After approval:
+
+1. Create the new versioned profile by copying the current versioned profile's content and updating `metadata.version`.
+2. Add `status: deprecated` to the previous versioned profile.
+3. Update the unversioned profile's `extends` field to reference the new versioned profile.
+4. Update the unversioned profile's `metadata.version` to the new version.
+5. Show the final state of all modified/created files.
+
+---
+
+## Notes
+
+- **Product full names** for titles/descriptions: Read the `full_name` field from `products/<product>/product.yml` for each product.
+- **Version format in filenames**: Replace dots with dashes and prefix with `v` (e.g., `2.0.0` → `v2-0-0`, `V2R3` → `v2r3`).
+- **Version format in metadata**: Use the version as provided by the user (e.g., `V2.0.0`, `V2R3`).
+- Always show the full proposed file contents before creating or modifying.
+- When updating, preserve all existing `selections`, `filter_rules`, variables, and other configuration from the current versioned profile.
PATCH

echo "Gold patch applied."
