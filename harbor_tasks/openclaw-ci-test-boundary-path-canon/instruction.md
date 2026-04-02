# Fix deterministic CI test regressions

Two test files are failing deterministically in CI. Both are in the core test suite (not extension tests).

## Bug 1: Extension test boundary violation in `src/auto-reply/reply/commands.test.ts`

The command handler test file imports a Telegram test plugin helper directly from the `extensions/telegram/` package at `extensions/telegram/test-support.js`. This violates the project's extension test boundary rule: core tests must not deep-import bundled plugin internals. CI enforces this boundary and the import causes a hard failure.

The test needs a Telegram-shaped channel plugin to exercise command routing, but it should obtain that through in-tree helpers (e.g. from `src/test-utils/channel-plugins.ts` and the public plugin SDK helpers) rather than reaching into the extension package.

Look at how other channel test plugins are constructed in the codebase (e.g. `createChannelTestPluginBase` and the various plugin SDK adapter builders) and replicate the Telegram-specific configuration, allowlist, and approval adapter behavior locally in the test file.

## Bug 2: Path comparison flakiness in `src/media-understanding/media-understanding-misc.test.ts`

The media attachment cache SSRF tests compare file paths using direct equality. On macOS (and some Linux configurations), the temporary directory path returned by `os.tmpdir()` may be a symlink (e.g. `/var/folders/...` which is really `/private/var/folders/...`). When the code resolves through the symlink but the test compares against the original unresolved path, assertions fail.

The fix should canonicalize paths (e.g. via `fs.realpath`) before comparing them in the two affected test cases within the `"media understanding attachments SSRF"` describe block.
