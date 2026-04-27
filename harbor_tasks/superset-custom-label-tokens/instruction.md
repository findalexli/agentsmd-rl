# Custom theme tokens for Published/Draft and Dataset type labels

Apache Superset's UI library exposes a set of "Superset-specific" theme tokens
on top of Ant Design's tokens. Today, the `PublishedLabel` and
`DatasetTypeLabel` components in `@superset-ui/core` always render with
hard-coded theme colors (`colorSuccess` / `colorPrimary` etc.) — there is no
way for downstream installations to customize their text color, background,
border, or icon color through theming.

Your job is to make these labels themeable.

## What needs to change

### 1. Add new token declarations

Extend the `SupersetSpecificTokens` interface (in
`superset-frontend/packages/superset-core/src/theme/types.ts`) with **sixteen**
new optional string fields. The exact names — these are the names the rest
of the codebase, downstream users, and tests will look for:

**Dashboard status labels (Published / Draft):**
- `labelPublishedColor`
- `labelPublishedBg`
- `labelPublishedBorderColor`
- `labelPublishedIconColor`
- `labelDraftColor`
- `labelDraftBg`
- `labelDraftBorderColor`
- `labelDraftIconColor`

**Dataset type labels (Physical / Virtual):**
- `labelDatasetPhysicalColor`
- `labelDatasetPhysicalBg`
- `labelDatasetPhysicalBorderColor`
- `labelDatasetPhysicalIconColor`
- `labelDatasetVirtualColor`
- `labelDatasetVirtualBg`
- `labelDatasetVirtualBorderColor`
- `labelDatasetVirtualIconColor`

Each is `string | undefined` (i.e. `?: string`).

### 2. Register them as valid Superset custom tokens

The token-validation utility at
`superset-frontend/src/theme/utils/antdTokenNames.ts` keeps a
`SUPERSET_CUSTOM_TOKENS` set used by `isValidTokenName(...)` and
`isSupersetCustomToken(...)`. All sixteen new token names must be added to
that set.

### 3. Wire the tokens into the components

Modify the two label components so that, when a token is set on the theme,
that value wins over the existing hard-coded color; when it is unset, the
existing color is preserved as the fallback.

**`PublishedLabel`** (`superset-frontend/packages/superset-ui-core/src/components/Label/reusable/PublishedLabel.tsx`)

| Style property | When `isPublished` is true | When `isPublished` is false |
| --- | --- | --- |
| text color | `labelPublishedColor` else `colorSuccessText` | `labelDraftColor` else `colorPrimaryText` |
| background-color | `labelPublishedBg` (only applied when set) | `labelDraftBg` (only applied when set) |
| border-color | `labelPublishedBorderColor` (only applied when set) | `labelDraftBorderColor` (only applied when set) |
| icon color | `labelPublishedIconColor` else `colorSuccess` | `labelDraftIconColor` else `colorPrimary` |

`backgroundColor` and `borderColor` must NOT be emitted in the inline
`style={{ ... }}` object when the corresponding token is `undefined` — only
add them when a value is present.

**`DatasetTypeLabel`** (`superset-frontend/packages/superset-ui-core/src/components/Label/reusable/DatasetTypeLabel.tsx`)

| Style property | When `datasetType === 'physical'` | When `datasetType === 'virtual'` |
| --- | --- | --- |
| text color | `labelDatasetPhysicalColor` else `colorPrimaryText` | `labelDatasetVirtualColor` else `colorPrimary` |
| background-color | `labelDatasetPhysicalBg` (only applied when set) | `labelDatasetVirtualBg` (only applied when set) |
| border-color | `labelDatasetPhysicalBorderColor` (only applied when set) | `labelDatasetVirtualBorderColor` (only applied when set) |
| icon color | `labelDatasetPhysicalIconColor` else `colorPrimary` | `labelDatasetVirtualIconColor` else *(no explicit icon color — leave `iconColor` unset on the icon)* |

The wrapping `<Label>` element rendered by `DatasetTypeLabel` must also carry
the attribute `data-test="dataset-type-label"` so callers (and tests) can
target it.

For the virtual branch's icon, the default — i.e. when
`labelDatasetVirtualIconColor` is undefined — must be **no `iconColor` prop
at all** on the `<Icons.ConsoleSqlOutlined ... />` (so the SVG renders with
no inline `color` style and falls back to whatever the surrounding CSS
provides). Only pass `iconColor` when the token is defined.

## Behavioral expectations (summary)

- Defaults: rendering with an unmodified `supersetTheme` keeps all the
  pre-existing colors (`colorSuccess` / `colorSuccessText` /
  `colorPrimary` / `colorPrimaryText`).
- Full overrides: when all four `*Color` / `*Bg` / `*BorderColor` /
  `*IconColor` tokens are set, the rendered `<Label>` element shows
  exactly those colors via inline style for `color`, `background-color`,
  `border-color`, and the icon SVG carries the `iconColor`.
- Partial overrides: e.g. setting only `labelPublishedBg` overrides the
  background but leaves the text color at `colorSuccessText` — the
  fallback chain is per-property, not all-or-nothing.
- The virtual dataset icon, by default (no token set), continues to render
  with no explicit icon color — its `style.color` is the empty string.

## Code Style Requirements

The repo enforces strict frontend style rules:

- TypeScript only (no plain JS), no `any` types.
- Use Ant Design / theming tokens via `@apache-superset/core` rather than
  hard-coded colors.
- Tests should use `test()` (not `describe()`-nested blocks) and React
  Testing Library — Enzyme is removed.
- New `.ts` / `.tsx` files require the Apache Software Foundation license
  header.
- Run `pre-commit run --all-files` (prettier, eslint, mypy, etc.) before
  considering the change done.

## Out of scope

- Wiring these tokens into any consumer dashboard / dataset-list pages.
- Changing the Ant Design tokens themselves.
- Documentation site updates beyond what is strictly required for the
  feature to compile and pass type checks.
