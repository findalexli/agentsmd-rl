# Task: Fix erofs Snapshotter Block Mode Ownership Handling

## Problem

The erofs snapshotter in containerd attempts to change ownership of the upper directory during snapshot creation, even when running in **block mode**. In block mode, the upperdir lives inside the block image itself, making host ownership permissions irrelevant. This causes unnecessary `chown` operations that may fail or be ineffective in environments where host permissions are restricted.

## Relevant Code

The issue is in `plugins/snapshots/erofs/erofs.go`, specifically in the `createSnapshot` function. The function currently performs UID/GID remapping and `os.Lchown` unconditionally, without considering whether the snapshotter is running in block mode.

## What Needs to Change

The ownership remapping and `chown` logic should only execute when **not** in block mode. When `blockMode` is enabled:

1. Skip the UID/GID mapping label checks and remapping calculations
2. Skip the parent ownership fallback
3. Skip the `os.Lchown` call entirely

The fix should:
- Wrap the relevant ownership code in a conditional that checks the `blockMode` flag
- Add a comment explaining why this is skipped in block mode (host ownership is irrelevant for block devices)
- Preserve all existing logic for non-block mode operation

## Verification

The fix should ensure:
- Code compiles successfully
- `createSnapshot` function structure is preserved
- All UID/GID remapping logic remains intact for non-block mode
- Parent ownership fallback is preserved
- The `Lchown` call and its setup logic are guarded by a `!s.blockMode` check
- An explanatory comment is present describing the block mode behavior
