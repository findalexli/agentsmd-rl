# Embedded dashboards must default to light theme, not OS preference

You are working in the Apache Superset frontend at
`/workspace/superset/superset-frontend`. The repo has a Flask/Python backend and
a React/TypeScript frontend organised as an npm workspace under `packages/*`,
`plugins/*`, and `src/setup/*`. For this task you only need the frontend.

## Symptom

When a user views an embedded Superset dashboard (loaded via the Superset
Embedded SDK) and both a default and a dark theme are configured in bootstrap
data, the dashboard incorrectly inherits the host OS dark/light mode
preference on its very first render.

Concretely, in `src/theme/ThemeController.ts`, `determineInitialMode()`
defaults to `ThemeMode.SYSTEM` whenever both default and dark themes are
available in bootstrap data. `ThemeMode.SYSTEM` reads
`window.matchMedia('(prefers-color-scheme: dark)')` from the user's OS, so an
embedded dashboard whose host machine is configured for dark mode is rendered
in dark mode.

Embedded dashboards are launched from
`src/embedded/EmbeddedContextProviders.tsx`, which constructs a singleton
`ThemeController` that the SDK's `setThemeMode()` only updates *after* the
initial render. Embedded dashboards therefore must start in light/default mode
regardless of the host's OS preference; the SDK can still switch to dark or
system mode after init.

## Required behaviour

`ThemeController` (in `src/theme/ThemeController.ts`) must accept an opt-in
constructor option that lets a caller specify the initial theme mode used when
no mode has been previously saved. The contract:

1. The public options interface `ThemeControllerOptions` (declared in
   `packages/superset-core/src/theme/types.ts`) gains an optional
   `initialMode?: ThemeMode` field. The new field must use the `ThemeMode`
   enum type — not a string literal type.
2. When `ThemeController` is constructed with `initialMode` set to a valid
   `ThemeMode` value AND no previously saved mode exists in storage AND a dark
   theme is available, the controller starts in that supplied mode. The
   controller must therefore expose `getCurrentMode()` returning that
   `ThemeMode` value immediately after construction.
3. If `initialMode` is omitted, the existing default of `ThemeMode.SYSTEM`
   (when both themes are present) is preserved — the main (non-embedded)
   Superset app's behaviour must be unchanged.
4. A previously saved mode in storage must take precedence over `initialMode`.
   `initialMode` is *only* consulted as a fallback when no saved mode is
   present.
5. When no dark theme is available, the controller still forces
   `ThemeMode.DEFAULT` regardless of `initialMode` (this matches existing
   behaviour: dark/system aren't valid without a dark theme).
6. An invalid `initialMode` value (one that is not a member of `ThemeMode`,
   or one that requires unavailable theme data) must be rejected and the
   controller must fall through to its existing default
   (`ThemeMode.SYSTEM` when both themes are available). Reject using the
   existing `isValidThemeMode()` helper, the same way the saved-mode path
   already validates input.
7. The user must still be able to call `setThemeMode(...)` after init to
   switch to any other valid mode (e.g. the SDK overriding to dark or
   system). `initialMode` only affects the *initial* mode.

The `ThemeController` constructor signature is destructured options. A
correct fix should add `initialMode` to the destructuring (defaulting to
`undefined`) and store it on the instance for use in
`determineInitialMode()`.

## Embedded provider must opt in

In `src/embedded/EmbeddedContextProviders.tsx`, the singleton
`themeController` is currently constructed as

```ts
const themeController = new ThemeController({
  storage: new ThemeMemoryStorageAdapter(),
});
```

Update this construction to pass `initialMode: ThemeMode.DEFAULT` so embedded
dashboards start in light mode. `ThemeMode` is a runtime enum (not just a
type) and must be imported as a value from `@apache-superset/core/theme` —
the existing import only brings in `ThemeStorage` as a type.

Do **not** modify any other top-level `new ThemeController(...)` call site
(in particular, the main app's controller must keep its existing behaviour:
no `initialMode`, so it defaults to system preference when both themes are
configured).

## Code Style Requirements

- This is TypeScript. Do **not** use `any`. Use the existing `ThemeMode`
  enum and `ThemeControllerOptions` interface types.
- Validate the new `initialMode` argument by reusing the existing
  `isValidThemeMode()` helper rather than introducing a new validator.
- Keep code comments timeless — do not add comments referencing "now",
  "currently", or other dated language.

## Scope

Functional code changes are limited to:

- `superset-frontend/packages/superset-core/src/theme/types.ts`
- `superset-frontend/src/theme/ThemeController.ts`
- `superset-frontend/src/embedded/EmbeddedContextProviders.tsx`

The pre-existing `superset-frontend/src/theme/tests/ThemeController.test.ts`
test suite must keep passing — your fix must not regress any of its
existing assertions.
