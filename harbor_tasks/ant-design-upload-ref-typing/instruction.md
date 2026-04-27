# Tighten ref typing in the `Upload` component

The `components/upload/index.tsx` module is responsible for assembling the
public `Upload` compound component (with `Upload.Dragger` and
`Upload.LIST_IGNORE`) and for re-exporting the upload component's public
types. Two type-safety problems exist in this file as it stands.

## Problem 1 — `UploadRef` is not part of the upload module's public surface

`components/upload/Upload.tsx` defines and exports an interface:

```ts
export interface UploadRef<T = any> {
  onBatchStart: ...;
  onSuccess: ...;
  onProgress: ...;
  onError: ...;
  fileList: UploadFile<T>[];
  upload: RcUpload | null;
  nativeElement: HTMLSpanElement | null;
}
```

This is the shape of the imperative handle that consumers receive when
they attach a `ref` to `<Upload>`. However, `components/upload/index.tsx`
re-exports many other public types from this module (`UploadProps`,
`UploadFile`, `DraggerProps`, `RcFile`, `UploadChangeParam`,
`UploadListProps`, `UploadSemanticName`, `UploadSemanticStyles`,
`UploadSemanticClassNames`) but **does not** re-export `UploadRef`. As a
result, application code that imports the upload module's type surface
cannot reference `UploadRef` by its public name.

The expected behaviour is that the following should compile, given the
upload module's index file:

```ts
import type { UploadRef } from '<path-to-upload-index>';
const handle: UploadRef<File> | null = null;
```

## Problem 2 — the compound component's `ref` is typed as `any`

In the same file, the compound component type is declared as:

```ts
type CompoundedComponent<T = any> = InternalUploadType & {
  <U extends T>(
    props: React.PropsWithChildren<UploadProps<U>> & React.RefAttributes<any>,
  ): React.ReactElement;
  Dragger: typeof Dragger;
  LIST_IGNORE: string;
};
```

The `React.RefAttributes<any>` means the component will accept literally
any shape of ref — including, for example, a `React.RefObject<string>`
or a `React.RefObject<HTMLInputElement>`. This silently defeats type
safety: a consumer who attaches the wrong kind of ref gets no compiler
warning, and any downstream code that uses `ref.current` to call the
imperative handle's methods (`onBatchStart`, `onSuccess`, etc.) will
fail at runtime with no compile-time hint.

The expected behaviour is that the ref attribute on `<Upload<U>>` must
be a `Ref<UploadRef<U>>` (so the inner type tracks `U` — i.e.
`<Upload<File> ref={...} />` should require a ref to `UploadRef<File>`).
A wrong-typed ref such as `React.RefObject<string | null>` must
fail to type-check with a `TS2322` "is not assignable" error.

## Additional cleanup — `tests/utils.tsx`

`tests/utils.tsx` exports a `renderHook<T>` helper. Its body opens with:

```ts
export function renderHook<T>(func: () => T): { result: React.RefObject<T> } {
  const result = createRef<any>();
  ...
}
```

The `createRef<any>()` is an explicit `any` that can be replaced by a
type derived from `func`'s return type. Replace this `any` with a proper
type so the local `result` variable's type tracks the function's return
type without weakening anything.

## Constraints

- Do not change `components/upload/Upload.tsx` itself — `UploadRef` is
  already defined there and is the canonical source.
- Do not change the runtime behaviour of `Upload`, `Upload.Dragger`,
  `Upload.LIST_IGNORE`, or `renderHook`.
- The fix must be type-only.
- Keep the existing exports in `components/upload/index.tsx` intact.

## Code Style Requirements

The project enforces strict TypeScript with `strict: true`,
`noImplicitAny: true`, `noUnusedLocals: true`, and
`noUnusedParameters: true`. Your edit must keep `tsc --noEmit` clean for
the files you touch (the project has one pre-existing tsc error in
`components/watermark/useWatermark.ts` which is unrelated and not in
scope for this task).
