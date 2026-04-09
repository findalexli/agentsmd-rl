# Fix Patches Upstream-Head Ref for Worktree Compatibility

## Problem

The `script/lib/git.py` module uses a hardcoded git ref name (`refs/patches/upstream-head`) to track where patches were imported from. This causes issues with gclient worktrees where multiple worktrees share a `.git/refs` directory - they clobber each other's upstream-head refs, leading to incorrect patch export behavior.

## Your Task

Modify `script/lib/git.py` to derive a checkout-specific upstream-head ref name from the script's absolute path. The fix should:

1. Generate a unique ref suffix based on the script directory path using MD5 hash
2. Maintain backward compatibility by preserving the legacy ref name constant
3. Update `import_patches()` to set both the new checkout-specific ref AND the legacy ref
4. Update `guess_base_commit()` to try both the new ref and the legacy ref when looking up the upstream head

The ref format should be: `refs/patches/upstream-head-<8-char-md5-hash>`

## Key Files

- `script/lib/git.py` - Contains `UPSTREAM_HEAD` constant, `import_patches()`, and `guess_base_commit()` functions

## Context

In gclient-new-workdir worktrees, `.git/refs` is symlinked back to the source checkout. A single fixed ref name gets shared (and clobbered) across all worktrees. By deriving a per-checkout suffix from the script's absolute path, each worktree can record its own upstream head in the shared refs directory without conflicts.
