# Fix External Link Security Issue in Connections Page

## Problem

The "Nothing Found" info component on the Connections page has an external link that doesn't work correctly. When users click the documentation link, it should open in a new browser tab, but the current implementation has issues with how the link opens.

Additionally, there are security concerns with external links that open in new tabs - they can potentially be exploited if not configured properly.

## Location

The issue is in the Connections page UI component:
- `airflow-core/src/airflow/ui/src/pages/Connections/NothingFoundInfo.tsx`

## Expected Behavior

1. The documentation link should open in a new browser tab
2. The link should follow security best practices for external links
3. The solution should pass the existing linting and type-checking

## Hints

- Look at the HTML attributes on the `<Link>` component
- Consider what security attributes are recommended for links that open in new tabs
- Check that attribute values follow correct HTML syntax
