# Combine Alert props with global config in the docs

You are working in the Ant Design (`antd`) repository. Treat the project's
existing `CLAUDE.md` and `AGENTS.md` as authoritative; this task asks you to
both **extend the documentation convention recorded there** and **apply the
extended convention to the Alert component**.

## Background

Ant Design's `<ConfigProvider>` lets users set common props for many
components globally (e.g. a default `closeIcon` for every Alert in the tree).
At the moment the component-level "API" tables and the `ConfigProvider` table
duplicate this information, and there is no shared convention for telling the
reader, on the component page itself, which individual props are
globally-configurable, which ones are *only* settable through `ConfigProvider`,
and which `ConfigProvider` version first added the support.

The Alert component, in particular, has accumulated a family of icon-related
global-only props (`closeIcon`, `successIcon`, `infoIcon`, `warningIcon`,
`errorIcon`) whose existence is currently hidden inside a long inline type in
the `ConfigProvider` API table.

## What you need to do

### 1. Extend the API-table convention in `CLAUDE.md`

In `CLAUDE.md`, under the section that describes the API-table format
(`### API 表格格式`), replace the current single example with **two
side-by-side example tables — an English one and a Chinese one** — that both
include an additional final column for global-config information. Use these
exact column headers:

- English table: `Property | Description | Type | Default | Version | [Global Config](/components/config-provider#component-config)`
- Chinese table: `参数 | 说明 | 类型 | 默认值 | 版本 | [全局配置](/components/config-provider-cn#component-config)`

Each example table should illustrate three rows (`disabled`, `loadingIcon`,
`type`) so that all of the new column's annotation conventions are
demonstrated. In particular:

- The `loadingIcon` row in the English example must use the literal phrase
  **`(Only supports global configuration) Custom loading icon`** as its
  Description, with `ReactNode` as Type, `-` as Default, `-` as Version, and
  `6.2.0` as the Global Config value.
- The `loadingIcon` row in the Chinese example must use the literal phrase
  **`(仅支持全局配置) 自定义加载图标`** as its 说明 (note: half-width
  parentheses are used in the CLAUDE.md example), with `ReactNode` as 类型,
  `-` as 默认值, `×` as 版本, and `6.2.0` as 全局配置.
- `disabled` rows mark Global Config as `×` (not globally configurable).
- `type` rows mark Global Config as `✔` (already supported in the previous
  major version).

After the two example tables, replace the existing two bullet points with a
list of bullets — one bullet per column — that documents the rules. Keep the
existing rules (alphabetical ordering, default-value formatting) and add new
rules covering Description, Type, Version and Global Config:

- Description: should briefly describe the prop; if a prop is only available
  through global config, the description must annotate this in parentheses.
- Type: TypeScript type.
- Default: existing rule (string in backticks, boolean/number literal, `-` if
  none).
- Version: same as before, plus: previous-major props use `-`; props that are
  only globally configurable use `×`.
- Global Config: globally-configurable props record the version that first
  introduced global-config support; props supported before the previous major
  use `✔`; props that cannot be set globally use `×`.

### 2. Apply the new convention to `components/alert/index.en-US.md`

Replace the existing API table (the one starting with
`| Property | Description | Type | Default | Version |`) with a new table
that adds the same `[Global Config](/components/config-provider#component-config)`
column described above. Keep every previously-documented prop (`action`,
`afterClose`, `banner`, `classNames`, `closable`, `description`, `icon`,
`message`, `onClose`, `showIcon`, `styles`, `title`, `type`) **and add five
new rows** for the global-only icon props that already live in
`ConfigProvider`: `closeIcon`, `successIcon`, `infoIcon`, `warningIcon`,
`errorIcon`.

Concrete requirements for the resulting English table:

- Rows are sorted alphabetically (deprecated `~~name~~` entries sort by
  underlying name; deprecated `~~onClose~~` sorts after `~~message~~`, before
  `showIcon`).
- For every globally-configurable icon prop, the Description column starts
  with the literal phrase `(Only supports global configuration)`. Specifically:
  - `closeIcon` description: `(Only supports global configuration) Custom close icon`
  - `successIcon` description: `(Only supports global configuration) Custom success icon in Alert icon`
  - `infoIcon` description: `(Only supports global configuration) Custom info icon in Alert icon`
  - `warningIcon` description: `(Only supports global configuration) Custom warning icon in Alert icon`
  - `errorIcon` description: `(Only supports global configuration) Custom error icon in Alert icon`
- All five global-only icon rows have Type `ReactNode`, Default `-`, and
  Version `×`. Their Global Config values are `6.3.0` for `closeIcon` and
  `6.2.0` for the four per-status icons.
- Existing rows pick up their Global Config annotation according to the new
  rules: `closable` is `✔`; `classNames` and `styles` are `6.0.0`; every
  other previously-documented row (including the deprecated ones) is `×`.
- Drop the standalone `4.9.0` version label that was previously attached to
  `action`, and drop the trailing `, >=5.15.0: support \`aria-*\`` from the
  `closable` description — that information is no longer carried in this
  table.

### 3. Apply the new convention to `components/alert/index.zh-CN.md`

Mirror the English table changes in the Chinese doc, using the
`[全局配置](/components/config-provider-cn#component-config)` header and the
parenthesised annotation `（仅支持全局配置）` (full-width parentheses) on the
same five icon props. In particular `closeIcon` must read
`（仅支持全局配置）自定义关闭图标`. Drop the trailing
`，>=5.15.0: 支持 \`aria-*\`` from the `closable` description and the standalone
`4.9.0` version on `action`.

### 4. Simplify the `alert` row in `ConfigProvider`

Now that the per-prop information lives on the Alert page, simplify the
`alert` row in **both** ConfigProvider docs.

- In `components/config-provider/index.en-US.md`, change the `alert` row's
  Type column to the literal `See [Alert](/components/alert#api)` and replace
  the long Version cell with a plain `5.7.0`.
- In `components/config-provider/index.zh-CN.md`, change the `alert` row's
  Type column to the literal `参见 [Alert](/components/alert-cn#api)` and
  replace the long Version cell with a plain `5.7.0`.

Do not modify any other rows in the ConfigProvider tables.

## Scope

The change is documentation-only:

- `CLAUDE.md`
- `components/alert/index.en-US.md`
- `components/alert/index.zh-CN.md`
- `components/config-provider/index.en-US.md`
- `components/config-provider/index.zh-CN.md`

No source code, tests, demos or styles change.
