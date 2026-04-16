# Fix: Custom component reload mode broken

## Problem

Custom components in Gradio do not update when the app is reloaded in development mode. The custom component is mounted once on initial load but prop updates are not propagated down to the component when the app tree reloads. This means that during development, any code changes to a custom component require a full page refresh rather than hot-reloading.

## Expected Behavior

- Custom components should re-mount with updated props when the app reloads in dev mode
- The old component instance should be properly cleaned up before mounting the new one
- There should be no debug logging calls in production component code
- All type names in the runtime should use correct spelling

## Files to Investigate

- `js/core/src/MountCustomComponent.svelte`
- `js/core/src/MountComponents.svelte`
