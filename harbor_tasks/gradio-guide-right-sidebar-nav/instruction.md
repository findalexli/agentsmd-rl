# Missing Table of Contents Sidebar on Guide Pages

## Problem

The Gradio documentation website's guide pages (`js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte`) currently only have a left-side navigation panel that lists all available guides by category. However, for longer guides with many sections, there is no way for users to quickly see or jump to specific sections within the current guide.

## Requirements

The guide page component needs to display a right-side table of contents panel with the following specific implementation details:

### Data Structure

The `guide_slug` type declaration must include these three fields:
- `text: string` - the heading text
- `href: string` - the anchor link (e.g., "#section-name")
- `level: number` - the heading level for indentation (h2=2, h3=3, etc.)

### Right Sidebar Layout

The right sidebar container must:
- Use the CSS class `sticky` so it remains visible while scrolling
- Use `hidden` and `lg:block` classes to only appear on larger screens (hidden on mobile)
- Use `float-right` positioning
- Include `overflow-y-auto` for scrollability when many sections exist
- Use `h-screen` for full-height display
- Use `top-8` for positioning offset

### Table of Contents Content

The sidebar must iterate over `guide_slug` entries using Svelte's `{#each}` syntax and:
- Render anchor elements (`<a>`) linking to each section
- Apply indentation based on heading level using the calculation pattern `(slug.level - 2)` multiplied by a rem value (e.g., 0.75rem) to compute `padding-left`
- Display the guide's `pretty_name` as a header at the top of the TOC
- Use an unordered list (`<ul>`) with `space-y-2` and `list-none` classes for the TOC entries

### Scroll Tracking

The implementation must track which section is currently visible:
- Declare a variable named `current_header_id` of type `string` to store the active section ID
- Use Svelte's reactive statement syntax (`$:`) that references both `y` (scroll position) and `slug` entries
- Bind scroll position using `bind:scrollY={y}` on `<svelte:window>`
- Compare `y` against element `offsetTop` positions to determine visibility (with a 100px offset buffer)
- Highlight the current TOC entry using conditional classes based on `current_header_id === slug.href.slice(1)`
- Use orange color (`text-orange-500`) with `font-medium` for the active/highlighted entry
- Use gray color (`text-gray-600` or `dark:text-gray-400`) for inactive entries with hover states

### Main Content Layout

The main content area currently uses `lg:w-8/12 mx-auto` which centers the content. This must be modified to:
- Remove the `mx-auto` centering
- Keep appropriate width classes like `lg:w-8/12`
- Add `lg:min-w-0` to allow proper flex shrinking
- Add `lg:pl-8` for left padding to accommodate the sidebar

### Conditional Rendering

The right sidebar must only render when there are sections to display:
- Use `{#if guide_slug.length > 0}` to conditionally render the sidebar

## Expected Behavior

After implementation:
1. Users see a sticky right sidebar on large screens listing all guide sections
2. TOC entries are indented hierarchically based on heading level (h2 flush left, h3 indented, etc.)
3. The currently visible section is highlighted as the user scrolls
4. The sidebar is hidden on mobile devices
5. Existing left sidebar navigation is preserved
6. Previous/next guide navigation links remain functional
