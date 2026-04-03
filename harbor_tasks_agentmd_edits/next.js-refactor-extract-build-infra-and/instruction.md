# Extract Pipeable Stream Exports and Add V8 JIT Skill

## Problem

The `react-dom-server` webpack alias files (`packages/next/src/build/webpack/alias/react-dom-server.js` and `react-dom-server-experimental.js`) currently re-export `renderToReadableStream`, `renderToString`, `renderToStaticMarkup`, and `resume` from the underlying React DOM server module. However, they are missing re-exports for `renderToPipeableStream` and `resumeToPipeableStream`, which are needed for Node.js streaming support.

Without these exports, code that tries to use pipeable streams through the webpack aliases gets `undefined` — the exports are available on the underlying module but not forwarded through the alias layer.

## Expected Behavior

Both alias files should conditionally re-export `renderToPipeableStream` and `resumeToPipeableStream`, following the same pattern used for other conditional exports (like `resume`). The exports should be guarded by availability checks so they are only exposed when the underlying module provides them.

Additionally, this project uses `.agents/skills/` for detailed agent guidance. Since this change involves performance-sensitive server-side streaming infrastructure, a new V8 JIT optimization skill should be added at `.agents/skills/v8-jit/SKILL.md` to guide future work on hot-path server code. Review the existing skills (especially `.agents/skills/authoring-skills/SKILL.md`) to understand the required format and conventions.

## Files to Look At

- `packages/next/src/build/webpack/alias/react-dom-server.js` — webpack alias for react-dom/server
- `packages/next/src/build/webpack/alias/react-dom-server-experimental.js` — experimental channel variant of the same alias
- `.agents/skills/authoring-skills/SKILL.md` — conventions for creating new agent skills
- `.agents/skills/` — existing skills for reference on format and content depth
