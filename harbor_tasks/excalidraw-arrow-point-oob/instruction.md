# Arrow point index Out-of-Bounds

You are working in the Excalidraw monorepo (https://github.com/excalidraw/excalidraw) cloned at `/workspace/excalidraw`. The repository is a Yarn 1 monorepo with workspaces under `packages/*` and `excalidraw-app/`.

## Symptom

Production telemetry (Sentry) keeps reporting an invariant violation that aborts the user's drag operation. The thrown message looks like:

```
There must be a valid lastClickedPoint in order to drag it. selectedPointsIndices([2]) points(0..1) lastClickedPoint(2)
```

The trigger is a corrupted `LinearElementEditor` state in which `lastClickedPoint` points outside the current `element.points` array (or is negative, or is missing from `selectedPointsIndices`). When that happens, the linear-element drag handler currently calls `invariant(...)`, which throws — the entire drag operation fails and the user-facing interaction breaks.

The same telemetry stream surfaces another, less actionable warning:

```
could not repair binding for element
```

This message has no context — there is no way to tell which element failed, or how many candidate elements were considered.

## What you need to do

There are three separate problems to fix in three files. Tests run on a Node 20 / vitest setup; you do **not** need to launch a browser.

### 1. `packages/element/src/linearElementEditor.ts` — make `handlePointDragging` resilient

The static method `LinearElementEditor.handlePointDragging` validates `lastClickedPoint` against `selectedPointsIndices` and `element.points` and currently throws via `invariant(...)` when the validation fails. Replace that throw with a non-fatal recovery:

- When `lastClickedPoint` is invalid (negative, or not present in `selectedPointsIndices`, or `element.points[lastClickedPoint]` is undefined), the function must **log the same diagnostic message via `console.error`** instead of throwing. The exact message body must remain unchanged so existing log-aggregation / dashboards keep matching it — it must still contain the literal substring `"There must be a valid lastClickedPoint in order to drag it"` and continue interpolating `selectedPointsIndices`, `points(0..N)`, and `lastClickedPoint(idx)`.
- After logging, the function must recover and continue the drag, using a `lastClickedPoint` value that points to a real index in `element.points` so the remaining body of the function (which dereferences `element.points[lastClickedPoint]`) executes without further crashes.
- The function must **return its normal `Pick<AppState, "suggestedBinding" | "selectedLinearElement">` patch object** in this fallback path — it must not return `null` or short-circuit.
- The other `invariant(...)` calls in the same function (the ones validating that the element exists and has more than one point) are correct and must remain.

### 2. `packages/excalidraw/components/App.tsx` — robust index clamping during multi-element commit

Inside `handleCanvasPointerMove`, when a multi-element drag crosses the line-confirm threshold and the trailing point is removed, the code currently rebuilds `selectedPointsIndices` only when it happens to contain the (now stale) `multiElement.points.length` index. That branch is too narrow — any index that was pointing past the new last point needs to be clamped, otherwise the `LinearElementEditor` state still leaves stale indices behind, which is one source of the corrupted state in problem (1).

Rewrite that update so that:

- It runs whenever the previous `selectedPointsIndices` is non-null (not only when it contains the specific value `multiElement.points.length`).
- Every index in the previous `selectedPointsIndices` is clamped to the new last index (`multiElement.points.length - 1`).
- Duplicates introduced by the clamping are removed (so that two indices that both clamped to the same value collapse into one).
- The accompanying `lastCommittedPoint` and `initialState.lastClickedPoint` continue to refer to the new last index.

The behaviour must be a strict superset of the old behaviour: nothing else in the same `setState({ selectedLinearElement: { ... } })` call should change semantically.

### 3. `packages/excalidraw/data/restore.ts` — informative diagnostic in `repairBinding`

In `repairBinding`, when the bound element cannot be located in either `targetElementsMap` or `existingElementsMap`, the code calls `console.error("could not repair binding for element")`. Replace that with a **single** `console.error(...)` call whose message:

- includes the bound-element id, formatted exactly as `element "<id>"` where `<id>` comes from optional-chaining the bound element (so `undefined` is acceptable when the element really cannot be resolved);
- includes the size of the candidate elements map, formatted exactly as `out of (<N>) elements` where `<N>` comes from optional-chaining the elements map's `.size`;
- starts with a capital `C` (the new message is a sentence: `Could not repair binding for element …`).

Concretely, the new message must match this template:

```
Could not repair binding for element "<boundElement?.id>" out of (<elementsMap?.size>) elements
```

The substring `out of (` followed by a number followed by `) elements` is asserted by the regression test. The phrase `repair binding` (case-insensitive) must also remain anywhere in the message so existing log-matching keeps working.

## What is in the working tree

`/workspace/excalidraw` is checked out at the parent of the merge commit. `yarn install --frozen-lockfile` has already run; you do **not** need to install dependencies. The repo's own test infrastructure is available via `yarn test:app`, `yarn test:typecheck` and `yarn test:code`.

The repository's `CLAUDE.md` and `.github/copilot-instructions.md` describe project-wide conventions. Notably:

- TypeScript everywhere; prefer immutable data (`const`, `readonly`).
- Use optional chaining (`?.`) and nullish coalescing (`??`).
- React functional components with hooks; follow the rules of hooks.
- Use `yarn test:typecheck` to verify TypeScript and `yarn test:app` to run vitest. Both must keep passing on your fix.

## Code Style Requirements

The grading test harness invokes the repository's TypeScript compiler (`yarn test:typecheck` ⇒ `tsc`) as a pass-to-pass check. Your edits must keep the project type-clean — every change must compile without TypeScript errors. The existing `linearElementEditor.test.tsx` vitest suite is also run as a pass-to-pass check; do not break any of its existing assertions.

## How you'll be graded

The grader runs `pytest` against a small Python harness that drives `yarn test:app` and `yarn test:typecheck`. The reward is binary: either every check passes, or it does not. Specifically:

- A regression test asserts that `LinearElementEditor.handlePointDragging` does **not throw** when handed a `LinearElementEditor` whose `initialState.lastClickedPoint` is out of range (e.g. `2` for an arrow with two points), **and** that it logs the validation message via `console.error` and returns a non-null patch.
- A second regression test asserts the same for a negative `lastClickedPoint`.
- A third regression test calls `restoreElements` with an arrow whose legacy startBinding points to a non-existent element id, and asserts the new diagnostic format matches `out of (\d+) elements`.
- `yarn test:typecheck` must succeed.
- `packages/element/tests/linearElementEditor.test.tsx` must continue to pass.
