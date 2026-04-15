# Fix: Custom component reload mode broken

## Problem

Custom components in Gradio do not update when the app is reloaded in development mode. The custom component is mounted once on initial load but prop updates are not propagated down to the component when the app tree reloads. This means that during development, any code changes to a custom component require a full page refresh rather than hot-reloading.

## Root Cause

In `MountCustomComponent.svelte`, the `$effect` block is guarded by a module-level variable that prevents it from re-triggering when props change. When `app_tree.reload` creates new prop objects, the effect does not detect the change because it does not read the prop references inside its body. Additionally, cleanup is handled via `onDestroy` instead of returning a cleanup function from `$effect`, which means the old component instance may not be properly unmounted before a new one is mounted.

There is also a typo where the runtime type uses `umount` instead of `unmount`. A stale `$inspect(node)` debug call exists in `MountComponents.svelte` that should be removed.

## Expected Behavior

- Custom components should re-mount with updated props when the app reloads in dev mode
- The old component instance should be properly unmounted before mounting the new one
- The runtime type should use correct spelling `unmount` (not `umount`)
- No debug `$inspect` calls should remain in production code

## Files to Investigate

- `js/core/src/MountCustomComponent.svelte` -- effect block for mounting/unmounting custom components
- `js/core/src/MountComponents.svelte` -- remove debug `$inspect` call
