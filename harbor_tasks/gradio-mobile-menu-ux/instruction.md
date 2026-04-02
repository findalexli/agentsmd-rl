# Mobile Menu UX Issues in Docs Website Header

The Gradio documentation website's mobile navigation menu (`js/_website/src/lib/components/Header.svelte`) has several UX problems on small screens:

1. **Inline toggle instead of overlay**: When the hamburger icon is tapped, the nav links just appear/disappear inline within the header bar. This pushes content around and feels jarring rather than providing a clean, full-screen mobile menu experience.

2. **No dedicated close affordance**: The close button is a small inline SVG that's hard to tap. There's no clear, accessible close button with proper `aria-label` attributes.

3. **Missing utilities on mobile**: The Search and ThemeToggle components are only visible on desktop (`hidden lg:flex`). Mobile users have no way to access search or toggle the theme.

4. **Community dropdown is desktop-only styled**: The Community submenu renders inline on mobile with inconsistent padding and no visual grouping, making it hard to distinguish from primary nav links.

5. **Desktop/mobile state coupling**: The nav visibility is driven by a reactive statement `$: show_nav = click_nav || $store?.lg` that couples desktop responsive state with mobile toggle state, leading to stale visibility when resizing.

The header component needs to be reworked so that mobile users get a proper full-screen overlay menu with clear navigation sections, accessible controls, and access to search/theme utilities — while keeping the existing desktop header behavior intact.
