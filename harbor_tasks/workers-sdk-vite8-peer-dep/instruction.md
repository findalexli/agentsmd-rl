# Add Vite 8 to vite-plugin-cloudflare peer dependency range

The `@cloudflare/vite-plugin` package (in `packages/vite-plugin-cloudflare/`) does not declare Vite 8 as a supported peer dependency. When a project installs this plugin alongside Vite 8, npm/pnpm emits a peer dependency warning because the package.json only allows Vite 6 and 7.

Additionally, the package's agent instructions file (`packages/vite-plugin-cloudflare/AGENTS.md`) still references Vite 8 as a beta release in the testing section. Vite 8 is now stable, and the documentation should reflect that.

## What to do

1. **Update the peer dependency range** in `package.json` so that the `vite` peer dependency accepts `^8.0.0` in addition to the existing `^6.1.0` and `^7.0.0` ranges. The new range should be a disjunction (OR) of all three major versions.

2. **Update AGENTS.md** — the playground testing line currently reads "tested across Vite 6/7/8-beta in CI". It should read "tested across Vite 6/7/8 in CI" (dropping the "-beta" since Vite 8 is now stable).

3. **Add a changeset** following the conventions documented in the repo's `AGENTS.md` and `.changeset/README.md`. The changeset should:
   - Be a `minor` bump for `@cloudflare/vite-plugin` (adding support for a new major version is a feature)
   - Describe the change and its user-facing impact
   - Use the changeset format from `.changeset/README.md`

## Code Style Requirements

Format all changes with Prettier using the repo's configuration. Run `pnpm prettify` in the workspace root before finishing.
