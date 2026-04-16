# Handle Package Manager Catalogs in Migration Codemod

## What's Broken

When running the `turbo migrate` command on projects that use **package manager catalogs** (pnpm or yarn), the codemod currently fails to upgrade turbo correctly. Instead of updating the catalog file, it runs `pnpm add turbo@latest` (or equivalent), which overwrites the `catalog:` reference in `package.json` with a literal version string — breaking the entire catalog setup.

For example, a project with this `package.json`:
```json
{
  "devDependencies": {
    "turbo": "catalog:"
  }
}
```

Should update the version in `pnpm-workspace.yaml` (or `.yarnrc.yml` for yarn):
```yaml
catalog:
  turbo: "^2.0.0"   # ← this should be updated to the new version
```

But instead, the current codemod runs `pnpm add turbo@latest`, which replaces `"catalog:"` with a literal version like `"2.9.0"`.

## Required Changes

The migration codemod in `packages/turbo-codemod` must be updated to correctly handle catalog protocol references. The following specific changes are required:

### 1. Catalog Detection and Update Logic

Create a new source file at `packages/turbo-codemod/src/commands/migrate/steps/update-catalog.ts` containing:
- A type/interface for catalog information
- A function to detect catalog usage in `package.json` (checking for `"catalog:"` or `"catalog:<name>"` patterns in dependencies)
- A function to update the catalog version in the appropriate catalog file (`pnpm-workspace.yaml` for pnpm, `.yarnrc.yml` for yarn)

### 2. Dist-Tag Resolution

In `packages/turbo-codemod/src/commands/migrate/steps/get-latest-version.ts`, ensure that dist-tags like `"latest"` are resolved to concrete versions before being returned. The code should check if the target version exists as a key in the npm registry's `tags` object.

### 3. Install Command Logic

In `packages/turbo-codemod/src/commands/migrate/steps/get-turbo-upgrade-command.ts`, modify the logic to:
- Accept catalog information as a parameter
- Return an install command (rather than add) when a catalog is detected and already updated

### 4. Migration Integration

In `packages/turbo-codemod/src/commands/migrate/index.ts`, integrate the catalog detection and update functions into the migration flow so that catalog references are handled before falling back to package manager add commands.

### 5. YAML Dependency

Add the `yaml` package (version 2.x) as a dependency in `packages/turbo-codemod/package.json` for parsing catalog YAML files.

### 6. Test File

Create `packages/turbo-codemod/__tests__/update-catalog.test.ts` with tests for the catalog update functionality.

### 7. Test Fixtures

Create the following test fixtures in `packages/turbo-codemod/__tests__/__fixtures__/get-turbo-upgrade-command/`:

**pnpm-catalog-default/** containing:
- `package.json` with `"turbo": "catalog:"` in devDependencies
- `pnpm-workspace.yaml` with a `catalog:` section including turbo

**yarn-catalog-default/** containing:
- `package.json` with catalog turbo reference
- `.yarnrc.yml` with a `catalog:` section including turbo

## Package Manager Notes

- pnpm catalogs use `pnpm-workspace.yaml` with a `catalog:` (default) or `catalogs:` (named) key
- yarn catalogs use `.yarnrc.yml` with a `catalog:` key
- Catalog versions may have prefixes (`^`, `~`, etc.) that must be preserved when updating
