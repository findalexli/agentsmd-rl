# Bound arrow elements not updated after element mutations

In Excalidraw, shape elements can have bound arrows attached to them. When a shape is moved or resized, its bound arrows must be repositioned to stay attached. The codebase provides an `updateBoundElements` function in `packages/element/src/binding.ts` for this purpose.

Two code paths mutate elements but fail to call `updateBoundElements` afterward, causing bound arrows to become detached:

## 1. Element distribution

When distributing elements (evenly spacing selected elements along an axis), the elements are moved but their bound arrows are not updated.

The `distributeElements` function currently lacks access to the `Scene` object needed to call `updateBoundElements`. The `Scene` type is available from `./Scene`.

To batch bound-element updates correctly when multiple elements move simultaneously, `updateBoundElements` should be called with the option `{ simultaneouslyUpdated: group }` where `group` contains all elements being distributed together.

The expected behavior after fix includes:
- `updateBoundElements` is imported from `"./binding"` with an import pattern like `from "./binding"`
- The Scene type is imported with a pattern like `import type { Scene }`
- `distributeElements` accepts a `scene: Scene` parameter
- Elements are mutated via `scene.mutateElement` instead of `newElementWith`
- After each element mutation, `updateBoundElements(element, scene, { simultaneouslyUpdated: group })` is called
- The caller in `packages/excalidraw/actions/actionDistribute.tsx` passes `app.scene` to `distributeElements`

## 2. WYSIWYG text container resizing

When editing text inside a container in WYSIWYG mode, if the text overflows or shrinks, the container height is updated via `app.scene.mutateElement(container, { height: targetContainerHeight })`, but bound arrows attached to the container are not updated.

The expected behavior after fix includes:
- `updateBoundElements` is imported from `@excalidraw/element`
- After each `app.scene.mutateElement(container, { height: targetContainerHeight })` call, `updateBoundElements(container, app.scene)` is called
