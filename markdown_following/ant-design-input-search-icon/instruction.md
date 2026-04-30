# Add `searchIcon` customization to `Input.Search`

You are working in the `ant-design` repository at `/workspace/ant-design`.
The Search variant of the Input component (`Input.Search` / `<Search />`,
defined in `components/input/Search.tsx`) currently renders a hard-coded
`SearchOutlined` icon inside its enter-button. There is no way for an
application to swap that icon out — neither via a prop on the component
nor via a global setting through `ConfigProvider`.

Your task is to add an opt-in customization point named **`searchIcon`**
that controls what is rendered inside the Search button when the default
icon-only button is used (i.e. when `enterButton` is the default boolean
`false`, so a button with just the icon is shown).

## Required behaviour

1. **Direct prop on Search.** A new prop on `<Search>`:

   ```tsx
   <Search searchIcon={<MyIcon />} />
   ```

   When supplied, the search button must render `<MyIcon />` in place
   of the built-in `SearchOutlined` icon. The button is the element
   matching the selector `.ant-input-search-btn`.

2. **Global default via `ConfigProvider`.** A new field on the
   `inputSearch` config of `ConfigProvider`:

   ```tsx
   <ConfigProvider inputSearch={{ searchIcon: <MyIcon /> }}>
     <Search />
   </ConfigProvider>
   ```

   When supplied through this context, all descendant `<Search>` components
   that do not provide their own `searchIcon` prop must render the
   ConfigProvider's icon inside the search button.

3. **Prop wins over context.** When both are supplied (a `searchIcon`
   prop on `<Search>` AND a `searchIcon` value on the surrounding
   `ConfigProvider`'s `inputSearch` config), the prop must win.

4. **Backward compatible default.** When no value is supplied via either
   path, the existing `SearchOutlined` icon must still be rendered. The
   pre-existing `Search.test.tsx` suite must continue to pass without
   modification.

5. **`enterButton` interaction unchanged.** The new prop affects only
   the icon-button case (`typeof enterButton === 'boolean'`). When
   `enterButton` is set to a non-boolean value (a string label or a
   custom button node), Search behaviour is unchanged.

## API surface

The TypeScript type for `searchIcon` should be `React.ReactNode` (it can
be any renderable React node — element, string, number, etc., or
`undefined` for the default).

## Documentation requirements

Per the repository's agent-instruction files (`AGENTS.md`, `CLAUDE.md`,
`.github/copilot-instructions.md`), you must document the new prop in
**both** the English and Chinese API docs and include a version
annotation:

- `components/input/index.en-US.md`: add an API table row for
  `searchIcon` with description, type `ReactNode`, default `-`, and a
  SemVer version annotation in the **Version** column (use `6.4.0`).
- `components/input/index.zh-CN.md`: add the equivalent Chinese row
  (description in Chinese, same type/default/version).
- `components/config-provider/index.en-US.md` /
  `components/config-provider/index.zh-CN.md`: extend the existing
  `inputSearch` row's type description to mention `searchIcon`, and add a
  version annotation on the same row (e.g. `searchIcon: 6.4.0`) so that
  ConfigProvider users can also discover the option.

The repository's API table format (columns: Property, Description, Type,
Default, Version) must be followed: string defaults in backticks,
booleans/numbers as literals, `-` when there is no default, descriptions
starting with a capital letter and **no** trailing period.

## Files you will probably need to touch

- `components/input/Search.tsx` — the component itself.
- `components/config-provider/context.ts` — the `InputSearchConfig`
  TypeScript type that backs `useComponentConfig('inputSearch')`.
- `components/config-provider/index.tsx` — the `ProviderChildren`
  forwarding/memoization for the `inputSearch` config.
- `components/input/index.en-US.md` and `components/input/index.zh-CN.md`
  for documentation.
- `components/config-provider/index.en-US.md` and
  `components/config-provider/index.zh-CN.md` for the global config docs.

The repository already has a `fallbackProp` utility under
`components/_util/fallbackProp.ts` that returns the first non-`undefined`
of its arguments — you may want to use it (it is the same helper the
existing Input/InputNumber code uses for analogous prop/context/default
chains).

## Verification

- `npx jest --config .jest.js --no-cache --testPathPatterns='input/__tests__/Search.test.tsx'`
  must continue to pass (no regressions).
- The new behaviour must hold for all three cases above (prop, context,
  prop-overrides-context).
