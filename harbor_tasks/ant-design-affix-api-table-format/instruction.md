# Document Affix API in Standard Format

The Ant Design v6 docs have an inconsistency in how the `Affix` component documents its props, and the project's `CLAUDE.md` rules describing the API-table convention are missing a heading and an important detail. Fix all five files described below.

## Background

Component API tables in this repo follow a 6-column convention:

- English: `Property | Description | Type | Default | Version | Global Config`
- Chinese: `参数 | 说明 | 类型 | 默认值 | 版本 | 全局配置`

`Alert`, `Anchor`, and most other v6 components already follow this. `Affix` does not — its props table currently has only 4 columns. The example tables inside `CLAUDE.md`'s "## 文档规范 → ### API 表格格式" section already show the canonical 6-column shape, so use those examples as the formatting reference.

A separate but related inconsistency lives in the `ConfigProvider` "Component Config" props table: the row for `affix` inlines a literal type (`{ className?: string, style?: React.CSSProperties }`), whereas comparable rows (e.g. `alert`, `anchor`) use a short `See [<Component>](...)` link reference. Bring `affix` in line with that pattern.

## Tasks

### 1. `components/affix/index.en-US.md`

Replace the existing 4-column props table with a 6-column table whose header is exactly:

```
| Property | Description | Type | Default | Version | [Global Config](/components/config-provider#component-config) |
```

For each existing prop (`offsetBottom`, `offsetTop`, `target`, `onChange`):

- Leave the `Version` cell empty (these props all predate v6 and have no introduction-version annotation).
- Mark the `Global Config` cell with `×` (none of these support global config).

  For example, the `offsetTop` data row should read:
  `| offsetTop | Offset from the top of the viewport (in pixels) | number | 0 |  | × |`

While editing, also refresh the `target` prop's `Type` cell from `() => HTMLElement` to `() => Window \| HTMLElement \| null` (escape pipes inside markdown table cells with `\|`).

### 2. `components/affix/index.zh-CN.md`

Mirror the same change in Chinese. The header must be exactly:

```
| 参数 | 说明 | 类型 | 默认值 | 版本 | [全局配置](/components/config-provider-cn#component-config) |
```

Note `config-provider-cn` (Chinese variant), not `config-provider`. Same `×` markers; same `target` type refresh to `() => Window \| HTMLElement \| null`.

  For example, the `offsetTop` data row should read:
  `| offsetTop | 距离窗口顶部达到指定偏移量后触发 | number | 0 |  | × |`

### 3. `components/config-provider/index.en-US.md`

In the "Component Config" props table, the `affix` row currently reads:

```
| affix | Set Affix common props | { className?: string, style?: React.CSSProperties } | - | 6.0.0 |
```

Replace it with a `See [Affix](/components/affix#api)` reference, matching the style of `alert`/`anchor` rows. The full row must read:

```
| affix | Set Affix common props | See [Affix](/components/affix#api) | - | 6.0.0 |
```

### 4. `components/config-provider/index.zh-CN.md`

Apply the same change in Chinese. The full row must read:

```
| affix | 设置 Affix 组件的通用属性 | 参见 [Affix](/components/affix-cn#api) | - | 6.0.0 |
```

(`参见` is the Chinese translation of `See`; note `affix-cn` here.)

### 5. `CLAUDE.md`

In the `## 文档规范 → ### API 表格格式` section, the column-explanation bullet list currently appears immediately after the Chinese example table. Two changes are required:

1. Insert a `列说明：` paragraph (followed by a blank line) before the bullet list, so the list has an introductory heading.

2. The first bullet currently reads:

   ```
   - 参数：按字母顺序排列
   ```

   Replace it with the more detailed rule:

   ```
   - 参数：按字母顺序排列，忽略 className, style, onClick, onKeyDown 等通用属性, onChange, onClick 等事件回调放在最后
   ```

   (Common DOM/event attributes are ignored when alphabetizing; event-callback props such as `onChange`/`onClick` are placed at the end of the list.)

Do not touch the other bullets (`- 说明：…`, `- 类型：…`, `- 默认值：…`, `- 版本：…`, `- 全局配置：…`) or the example tables themselves.

## Scope

These five files are the only ones you need to edit. Do not modify other component docs, source code, tests, or unrelated sections of `CLAUDE.md`.
