# Bump agent-browser dependency to v0.24.0 in desktop app

## Problem

The desktop app's download script is pinned to agent-browser v0.20.1, but v0.24.0 is now available with important new features including dashboard observability, batch execution, streaming support, and semantic locators. The outdated version prevents users from accessing these capabilities.

## Expected Behavior

The `download-agent-browser.mjs` script should download agent-browser v0.24.0 instead of v0.20.1.

## Files to Look At

- `apps/desktop/scripts/download-agent-browser.mjs` — downloads the agent-browser binary during build; contains the VERSION constant

## Implementation Notes

Update the `VERSION` constant from `'0.20.1'` to `'0.24.0'`. This is the single source of truth for which binary version gets downloaded and bundled with the desktop app.
