# Improve mobile menu UX in docs website

## Problem

The mobile navigation menu in the Gradio docs website has several UX issues:

1. **No full-screen overlay**: When the hamburger menu is tapped on mobile, the nav links expand inline within the header bar rather than appearing as a proper full-screen mobile menu. This causes the header to grow awkwardly and push page content down.

2. **Desktop/mobile coupling**: The desktop navigation visibility is tied to the same `show_nav` state as the mobile toggle. This means the desktop nav flickers or behaves unexpectedly when the mobile toggle state changes.

3. **No close-on-navigate**: When a user taps a navigation link in the mobile menu, the menu stays open instead of automatically closing. Users have to manually close the menu after navigating.

4. **Accessibility**: The hamburger icon is a bare `<svg>` element with a click handler but no semantic button wrapper or `aria-label`. Screen readers cannot identify it as a menu toggle.

5. **Hardcoded nav links**: Navigation links (API, Guides, HTML Components) and community links (File an Issue, Discord, Github) are hardcoded as separate HTML elements rather than being data-driven, making them harder to maintain.

## Expected Behavior

- The mobile menu should appear as a **full-screen overlay** that covers the viewport, with proper `fixed` positioning
- The mobile overlay should only show on small screens (hidden on `lg` breakpoint)
- Desktop navigation should **always be visible** on large screens, independent of the mobile toggle state
- Mobile nav links should **close the menu** when tapped (set `click_nav = false`)
- The menu toggle should be a semantic `<button>` element with `aria-label`
- Navigation data should be extracted into arrays and rendered with `{#each}` loops

## Files to Look At

- `js/_website/src/lib/components/Header.svelte` — The main header/navigation component for the docs website
