# Modernize Terraform config for self-hosted runners

## Problem

The Terraform configuration in `.github/gh-actions-self-hosted-runners/arc/` uses deprecated HCL syntax that is incompatible with recent Terraform versions (v1.14+) and newer provider versions:

- `helm.tf` uses legacy `set {}` block syntax and `dynamic "set"` blocks for the Helm releases. The modern Terraform Helm provider requires `set = [...]` list assignment syntax instead.
- `provider.tf` pins the Google provider to an old 4.x version and uses legacy `kubernetes {}` block syntax in the Helm provider configuration, which should be `kubernetes = {}` assignment syntax.

Running `terraform plan` or `terraform apply` with current Terraform and provider versions will produce errors or deprecation warnings due to these outdated patterns.

## Expected Behavior

- Helm release resources should use `set = [{ name = "...", value = "..." }]` list assignment syntax instead of `set { name = "..." value = "..." }` block syntax.
- The `dynamic "set"` block in the ARC release should be replaced with a `for` expression inside `set = [...]`.
- The Google provider version constraint should be updated to a modern 6.x release.
- The Helm provider should use `kubernetes = { ... }` assignment syntax.
- After making these code changes, update the README documentation to include instructions for updating an existing deployment — currently the README only covers initial installation but has no guidance for making configuration changes to an already-deployed setup.

## Files to Look At

- `.github/gh-actions-self-hosted-runners/arc/helm.tf` — Helm release definitions with deprecated syntax
- `.github/gh-actions-self-hosted-runners/arc/provider.tf` — Provider version constraints and configuration blocks
- `.github/gh-actions-self-hosted-runners/arc/README.md` — Documentation that should cover the update workflow
