# Merge extension-provided policies into policy export

## Problem

The `--export-policy-data` command runs in the OSS dev build, which has no access to `extensionConfigurationPolicy` data — that lives only in `vscode-distro`'s `product.json`. As a result, extension policies for settings like `github.copilot.nextEditSuggestions.enabled` never appear in the exported `policyData.jsonc`. This means they're missing from Windows Group Policy ADMX/ADML artifacts, macOS `.mobileconfig` profiles, Linux `policy.json`, and the enterprise policy reference page.

## Expected Behavior

The policy export should fetch extension configuration policies from the distro's `product.json` (using the commit pinned in `package.json`) and merge them into the exported `policyData.jsonc`. The workflow should be wrapped in a convenient npm script that handles GitHub authentication automatically.

Additionally, the integration test needs a way to test this merge path without requiring real distro access — an environment variable should allow pointing to a local test fixture instead.

## Files to Look At

- `src/vs/workbench/contrib/policyExport/electron-browser/policyExport.contribution.ts` — the `--export-policy-data` CLI handler; this is where extension policy merging logic should be added
- `build/lib/policies/exportPolicyData.ts` — new build script to create (handles transpilation, auth, and invoking the export)
- `src/vs/workbench/contrib/policyExport/test/node/policyExport.integrationTest.ts` — integration test that verifies exported data matches the checked-in file
- `package.json` — needs a new `export-policy-data` script entry
- `.github/skills/add-policy/SKILL.md` — the skill documentation for adding policies; update it to document the extension policy lifecycle, the distro format, and the new export workflow

## Hints

- The distro's `product.json` contains an `extensionConfigurationPolicy` map where keys are setting names and values describe the policy (name, category, minimumVersion, description).
- For testing without distro access, support a `DISTRO_PRODUCT_JSON` environment variable that points to a local JSON file with the same structure.
- Create a test fixture at `src/vs/workbench/contrib/policyExport/test/node/extensionPolicyFixture.json` for the integration test.
- Don't forget to update the project's skill documentation to cover how extension policies work, the distro format, and the updated export workflow.
