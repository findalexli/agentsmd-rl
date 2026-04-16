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

### Actual Behavior

- Browser tab shows: `[object Object] - My CMS`

## Relevant Files

- `packages/next/src/utilities/meta.ts` — Contains `generateMetadata` function that handles meta title generation
- `packages/next/src/utilities/meta.spec.ts` — Test file (does not exist on base commit)

## Investigation Notes

The bug occurs in the `generateMetadata` function when processing the `title` property. When `title` is a Next.js `TemplateString` object (with `default`, `template`, or `absolute` properties), the current implementation does not properly extract the string values from the object structure.

The function needs to handle three cases for the `title` property:
1. Plain string (e.g., `'Dashboard'`)
2. TemplateString object with `default` and `template` fields
3. TemplateString object with `absolute` field

The `titleSuffix` should be properly appended to the appropriate fields of the TemplateString object, not stringified as `[object Object]`.
