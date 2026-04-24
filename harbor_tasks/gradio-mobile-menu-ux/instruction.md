# Mobile Menu UX Issues in Docs Website Header

The Gradio documentation website's mobile navigation menu (`js/_website/src/lib/components/Header.svelte`) has several UX problems on small screens:

1. **Inline toggle instead of overlay**: When the hamburger icon is tapped, the nav links just appear/disappear inline within the header bar. This pushes content around and feels jarring. The mobile menu should render as a full-screen overlay (using fixed or absolute positioning that covers the entire viewport) inside a conditional block. The overlay must contain at least two navigation links (`<a>` elements) so users can navigate from the mobile menu.

2. **No accessible close button**: The overlay lacks a clear, accessible close button. There should be a `<button>` or `<a>` element inside the overlay with an `aria-label` attribute whose value contains the word "close" or "dismiss", so assistive technologies can identify it.

3. **Missing utilities on mobile**: The `Search` and `ThemeToggle` components are only rendered in the desktop section of the header. Mobile users have no way to access search or toggle the theme. Each of these two components must appear at least twice in the component — once in the desktop section and once in the mobile overlay — so that both desktop and mobile users can access them.

4. **Desktop/mobile state coupling**: The nav visibility is driven by a single reactive statement that combines the mobile click toggle with the responsive breakpoint store, causing stale visibility when resizing between desktop and mobile. This coupling must be removed so that mobile and desktop nav visibility are managed independently.

5. **Desktop elements must be preserved**: The existing desktop header must remain intact — including the logo image (with alt text containing "logo"), navigation links to `/docs` and `/guides`, and the Community section text.

The header component needs to be reworked so that mobile users get a proper full-screen overlay menu with clear navigation sections, accessible controls, and access to search/theme utilities — while keeping the existing desktop header behavior intact.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
