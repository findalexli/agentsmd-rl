# Fix [object Object] in Browser Tab Title

## Problem

When configuring Payload admin with a Next.js `TemplateString` object for `admin.meta.title`, the browser tab displays `[object Object]` instead of the properly formatted title.

### Example Configuration

```typescript
// config.ts
export default buildConfig({
  admin: {
    meta: {
      title: { default: 'Dashboard', template: '%s | Dashboard' },
      titleSuffix: '- My CMS',
    },
  },
})
```

### Expected Behavior

- Browser tab should show: `Dashboard - My CMS`
- Collection pages should show: `Posts | Dashboard - My CMS`

When `title` is a TemplateString object with `default` and `template` fields (e.g., `{ default: 'Dashboard', template: '%s | Dashboard' }`), the `titleSuffix` should be appended to both fields:
- `default` becomes `'Dashboard - My CMS'`
- `template` becomes `'%s | Dashboard - My CMS'`

When `title` is a TemplateString object with an `absolute` field, the `titleSuffix` is appended to the `absolute` field.

### Actual Behavior

- Browser tab shows: `[object Object] - My CMS`

## Relevant Files

- `packages/next/src/utilities/meta.ts` — Contains `generateMetadata` function that handles meta title generation
- `packages/next/src/utilities/meta.spec.ts` — Test file (does not exist on base commit)

## Investigation Notes

The bug occurs in the `generateMetadata` function when processing the `title` property. When `title` is a Next.js `TemplateString` object (with `default`, `template`, or `absolute` properties), the current implementation does not properly extract the string values from the object structure.

The function needs to handle three cases for the `title` property:
1. Plain string (e.g., `'Dashboard'`) — `titleSuffix` is appended directly
2. TemplateString object with `default` and `template` fields — `titleSuffix` is appended to both fields
3. TemplateString object with `absolute` field — `titleSuffix` is appended to `absolute`

The `titleSuffix` should be properly appended to the appropriate fields of the TemplateString object, not stringified as `[object Object]`.

For OpenGraph titles, the function must extract the string value from the `title` object (using `.default` or `.absolute` depending on which field is present) before appending `titleSuffix`.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
