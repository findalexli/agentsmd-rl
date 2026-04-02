# Bug Report: eslint-plugin-react-hooks fails to install with ESLint 10

## Problem

After upgrading to ESLint 10, installing `eslint-plugin-react-hooks` fails with a peer dependency conflict. npm reports that the plugin requires a version of ESLint that doesn't satisfy `^10.0.0`, causing installation to fail or produce warnings depending on the package manager and its strictness settings.

Developers upgrading their projects to ESLint 10 cannot use `eslint-plugin-react-hooks` without using `--legacy-peer-deps` or similar workarounds to bypass the peer dependency check.

## Expected Behavior

`eslint-plugin-react-hooks` should install cleanly alongside ESLint 10 without peer dependency errors, since the plugin is compatible with ESLint 10.

## Actual Behavior

npm/yarn/pnpm reports an unmet peer dependency error because the plugin's declared peer dependency range for `eslint` does not include version 10. Users are forced to override or ignore peer dependency checks to proceed.

## Files to Look At

- `packages/eslint-plugin-react-hooks/package.json`
