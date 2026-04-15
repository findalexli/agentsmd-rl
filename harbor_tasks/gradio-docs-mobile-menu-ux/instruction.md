# Improve mobile menu UX in docs website

## Problem

The mobile navigation menu in the Gradio docs website has several UX issues:

1. **No full-screen overlay**: When the hamburger menu is tapped on mobile, the nav links expand inline within the header bar rather than appearing as a proper full-screen mobile menu that covers the viewport. This causes the header to grow awkwardly and push page content down.

2. **Desktop/mobile coupling**: The desktop navigation visibility is controlled by a reactive statement `$: show_nav = click_nav || ...` and uses `class:hidden={!show_nav}`, which ties desktop visibility to the mobile toggle state. This causes the desktop nav to flicker or behave unexpectedly when the mobile menu is toggled.

3. **No close-on-navigate**: When a user taps a navigation link in the mobile menu, the menu stays open instead of automatically closing. Users have to manually close the menu after navigating.

4. **Accessibility**: The hamburger icon is a bare `<svg>` element with a click handler but no semantic `<button>` wrapper or `aria-label` attribute. Screen readers cannot identify it as a menu toggle.

5. **Hardcoded nav links**: Navigation links ("API" linking to "/docs", "Guides" linking to "/guides", "HTML Components" linking to "/custom-components/html-gallery") and community links ("File an Issue", "Discord", "Github") are hardcoded as individual `<a>` elements rather than being defined as JavaScript data arrays and rendered with Svelte `{#each}` loops.

## Expected Behavior

When modifying `js/_website/src/lib/components/Header.svelte`, ensure:

1. **Mobile full-screen overlay**: The mobile menu should be wrapped in `{#if click_nav}` conditional block and use:
   - `fixed` positioning for viewport coverage
   - `inset-0` Tailwind class for full inset coverage
   - `lg:hidden` Tailwind class so it only appears on mobile
   - `z-50` or similar z-index to appear above content

2. **Desktop navigation decoupled**: The desktop `<nav>` element should:
   - Remove the reactive statement `$: show_nav = click_nav || ...`
   - Remove `class:hidden={!show_nav}` pattern
   - Use Tailwind classes `hidden lg:flex` so desktop nav is always visible at `lg` breakpoint regardless of mobile toggle state

3. **Close-on-navigate**: All navigation links within the mobile overlay (`{#if click_nav}` block) should have click handlers that set `click_nav = false` to close the menu when tapped.

4. **Accessibility**: The mobile menu toggle should be:
   - A semantic `<button>` element wrapping the icon (not a bare `<svg>` with click handler)
   - Have an `aria-label` attribute containing the word "menu" (e.g., "Open menu" or "Close menu")

5. **Data-driven navigation**: Navigation and community links should be:
   - Defined as JavaScript arrays in the `<script>` section containing objects with `label` and `href` keys
   - The main nav array should include links to `/docs`, `/guides`, and `/custom-components/html-gallery`
   - Rendered using Svelte `{#each}` loops with destructuring syntax: `{#each nav_links as { label, href }}`
   - At least two `{#each}` loops (one for main nav, one for community links)

## Files to Look At

- `js/_website/src/lib/components/Header.svelte` — The main header/navigation component for the docs website
