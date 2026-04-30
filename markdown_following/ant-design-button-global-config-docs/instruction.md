# Document Button's per-prop Global Config support

The `<Button>` component supports being configured globally through `<ConfigProvider componentSize="large" button={{ ... }}>`. Today, that information is only documented as a single dense type signature on the `button` row of the **ConfigProvider** API table — readers have to mentally cross-reference it against the Button API table to learn which Button props are globally configurable and from which version.

Restructure the documentation so the per-prop information lives on the Button page itself, in a new column.

## Required changes

### 1. Button API table — add a "Global Config" column

In **both** `components/button/index.en-US.md` and `components/button/index.zh-CN.md`, the API/属性 table currently has 5 columns: `Property | Description | Type | Default | Version`. Add a new **6th column** at the end:

- English header cell: `[Global Config](/components/config-provider#component-config)`
- Chinese header cell: `[全局配置](/components/config-provider-cn#component-config)`

For each existing prop row, fill the new column with:

- The version in which that prop became globally configurable (e.g. `5.17.0`, `5.25.0`, `5.27.0`, `6.0.0`, `6.3.0`), or
- An empty cell if that prop is not globally configurable.

The version source-of-truth is the existing verbose entry in the ConfigProvider API table (the `button` row at `components/config-provider/index.en-US.md` and `components/config-provider/index.zh-CN.md`, around line 117). It currently spells out: base `5.6.0`, `autoInsertSpace`: 5.17.0, `variant` and `color`: 5.25.0, `shape`: 5.27.0, `loadingIcon`: 6.3.0. In addition, `classNames` and `styles` are configurable from `6.0.0`.

### 2. Add a new `loadingIcon` row to the Button API table

`loadingIcon` is *only* available through ConfigProvider (it has no instance-level prop). Add it as a new row in both Button tables, with:

- **English** description: `(Only supports global configuration) Set the loading icon of button`
- **Chinese** description: `（仅支持全局配置）设置按钮的加载图标`
- Type: `ReactNode`
- Default: `` `<LoadingOutlined />` ``
- Version column: empty
- Global Config column: `6.3.0`

Keep rows alphabetically ordered (`loading` → `loadingIcon` → `onClick`).

### 3. ConfigProvider — collapse the verbose `button` row

In **both** `components/config-provider/index.en-US.md` and `components/config-provider/index.zh-CN.md`, the `button` row currently inlines the full type signature *and* a comma-separated version-history string. Now that this information lives on the Button page, replace the row's `Type` cell with a short reference and reset the `Version` cell to just `5.6.0`:

- English: `| button | Set Button common props | See [Button](/components/button#api) | - | 5.6.0 |`
- Chinese: `| button | 设置 Button 组件的通用属性 | 参见 [Button](/components/button-cn#api) | - | 5.6.0 |`

### 4. CLAUDE.md — update the documentation-format guide

`CLAUDE.md` describes how API tables in this repo should be laid out. The example under `### API 表格格式` must reflect the new 6-column convention, with the same `[Global Config](/components/config-provider#component-config)` header used on real component pages.

While editing `CLAUDE.md`, also normalize markdown table separator rows in this file from the compact `|---|---|...` form to the spaced `| --- | --- | ...` form (this matches the separator style used in the rest of `CLAUDE.md` and the live component docs).

## Notes

- All anchor link targets (`/components/config-provider#component-config`, `/components/button#api`, etc.) must match exactly — they are clickable cross-references on the live docs site.
- Do not rename, reorder, or remove any other Button props. The only new row is `loadingIcon`.
- The Chinese docs link to `*-cn` paths (`config-provider-cn`, `button-cn`); the English docs do not.
