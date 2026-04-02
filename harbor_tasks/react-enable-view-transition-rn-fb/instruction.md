## Task: Enable ViewTransition for React Native FB Build

The ViewTransition feature needs to be enabled for the React Native Facebook build. Currently it's disabled in the feature flags configuration for the native-fb channel.

### Context

React uses feature flags to gate experimental features across different release channels (OSS, www, React Native). The flag values are defined in fork files under `packages/shared/forks/`.

### What needs to be done

Enable the ViewTransition feature for:
- React Native FB (`native-fb.js`)
- Test renderer for React Native FB (`test-renderer.native-fb.js`)
- Test renderer for www (`test-renderer.www.js`)

### Hints

- Look in the feature flags fork files (not the main `ReactFeatureFlags.js`)
- Search for "ViewTransition" in the shared/forks directory
- For TypeScript-aware help with these skills: `.claude/skills/feature-flags/SKILL.md` and `.claude/skills/flags/SKILL.md`
