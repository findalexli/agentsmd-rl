# Prerelease config: decouple npm dist-tag from prerelease channel

## Problem

The `remix` package's prerelease publishing system has two interconnected issues:

1. **Dist-tag coupling**: When a `remix` prerelease like `3.0.0-alpha.0` is published to npm, it receives the npm dist-tag matching its version suffix (e.g., `alpha`). The desired behavior is that all remix prereleases — regardless of whether the version suffix is `alpha`, `beta`, or `rc` — are published with the npm dist-tag `next`.

2. **Configuration naming**: The prerelease configuration file conflates the prerelease channel (which determines the version suffix) with the npm distribution tag. These are separate concepts and should be represented by separate configuration.

## Expected Behavior

After the fix, the system must work as follows:

### Configuration
The JSON configuration for the remix prerelease must use a `channel` field (e.g., `{ "channel": "alpha" }`). This field controls only the version suffix — it does not determine the npm dist-tag.

### Prerelease Configuration Reader
The `RemixPrereleaseConfig` interface must define `channel: string`. The reader function must validate the config by checking `'channel' in obj`, reading `obj.channel`, and applying `.trim()` to the value. The function must return an object with the shape `config: { channel: ... }`.

### Version Calculation
The `getNextVersion` function must use `semver.inc` for prerelease version computation.

### Publishing
The publish script must use a variable named `remixPrereleaseChannel`. The publish command for the remix package must use `--tag next` (never interpolating the channel name as the npm tag). The script must include a real `pnpm publish` command.

### Documentation
- `AGENTS.md` must describe a `channel` field for prerelease configuration and explain that the npm dist-tag is always `"next"`.
- `CONTRIBUTING.md` must use the phrase `prerelease channels` in section headers and show a JSON example containing `"channel": "alpha"`.

## Areas of Change

The fix should touch:
- The remix package's prerelease configuration (a JSON file under `.changes/`)
- The release scripts that read prerelease config and handle publishing
- The contributor documentation

## Code Style Requirements

Your solution must pass the repository's ESLint checks. The repository uses Prettier for formatting. All modified files must be properly linted and formatted.
