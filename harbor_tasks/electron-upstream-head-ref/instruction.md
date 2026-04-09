# Fix gclient worktree upstream-head ref conflicts

## Problem

The `script/lib/git.py` file contains logic for managing upstream head refs during patch import/export. Currently, it uses a **fixed ref name** `refs/patches/upstream-head` for all worktrees.

This causes a problem in gclient-new-workdir worktrees where `.git/refs` is symlinked back to the source checkout. Multiple worktrees sharing the same `.git/refs` directory will **clobber each other's upstream-head refs**, causing patch operations to reference the wrong base commits.

## Task

Modify `script/lib/git.py` to derive a unique upstream-head ref per checkout.

## Key Requirements

1. **Per-checkout unique ref**: The `UPSTREAM_HEAD` constant should include a hash suffix derived from the checkout path, so each worktree gets its own ref.

2. **Backwards compatibility**: The code must still handle the legacy `refs/patches/upstream-head` ref for existing checkouts. When importing patches, update **both** the new unique ref and the legacy ref. When guessing base commits, try the new ref first, then fall back to the legacy ref.

3. **Use SCRIPT_DIR**: The hash should be derived from `SCRIPT_DIR` (which is already defined in the file), using the first 8 characters of its MD5 hash.

## Files to Modify

- `script/lib/git.py` - Main logic for patch import/export and base commit guessing

## What Success Looks Like

- `UPSTREAM_HEAD` should be in format `refs/patches/upstream-head-<8-char-hex-hash>`
- The hash is derived from `SCRIPT_DIR`
- `import_patches()` updates both the new ref and the legacy ref
- `guess_base_commit()` tries the new ref first, falls back to legacy
- Existing functionality is preserved for backwards compatibility
