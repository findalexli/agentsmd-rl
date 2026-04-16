# Fix Parallel Image Unpacking with OverlayFS

## Problem

When containerd unpacks container images in parallel using the overlayfs snapshotter, whiteout files are not properly processed. Files that should be deleted (marked by whiteout entries in image layers) incorrectly remain visible in the final rootfs.

This is tracked in GitHub issue #13030. The issue occurs because during parallel unpacking, the parent snapshot isn't provided to the snapshotter, causing overlayfs to return bind mounts instead of overlay mounts. The applier cannot correctly process whiteout conversions when working with bind mounts.

## Required Behavior

Implement a fix that converts bind mounts to overlay mounts during parallel unpack. The fix must:

1. **Detect when the fix is needed** - Check for ALL of these conditions in the layer loop:
   - Layer index > 0 (not the first layer)
   - Parallel unpack mode is enabled
   - Snapshotter key equals `"overlayfs"`

2. **Convert single bind mounts to overlay mounts** - When a single bind mount is detected, convert it to an overlay mount with these properties:
   - The check verifies the mount count and type
   - New mount type: `"overlay"`
   - New mount source: `"overlay"`
   - The `"rbind"` option is filtered out from the original options
   - The original source path becomes the `upperdir` option value

3. **Pass through unchanged**:
   - Multiple mounts (any count other than 1)
   - Single mounts that are not bind type

4. **Integrate the fix** - Call the conversion function when the parallel overlayfs conditions are met, before passing mounts to the applier's Apply method.

5. **Add reference comment** - Include a comment referencing issue #13030 or noting this is a temporary workaround.

## Testing

The fix can be verified by:
1. Running the `TestBindToOverlay` unit tests
2. Building the project successfully
3. The fix should handle:
   - Single bind mounts with options like `["ro", "rbind"]` → converted to overlay with `["ro", "upperdir=/path/to/source"]`
   - Existing overlay mounts → returned unchanged
   - Multiple bind mounts → returned unchanged
   - Single bind mounts without options → converted to overlay with just `["upperdir=/path/to/source"]`

## Notes

- This is a temporary workaround until PR #13053 lands
- The fix should only affect parallel unpack with overlayfs
- Other snapshotters and sequential unpack mode must not be affected
- See: https://github.com/containerd/containerd/issues/13030
