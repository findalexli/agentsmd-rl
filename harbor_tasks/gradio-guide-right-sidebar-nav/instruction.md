# Missing Table of Contents Sidebar on Guide Pages

## Problem

The Gradio documentation website's guide pages currently have a left-side navigation panel listing available guides by category, but longer guides with many sections offer no way for readers to quickly see or jump to specific sections within the guide.

## Goal

Add a right-side table of contents (TOC) panel to the guide page component at `js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte`. The TOC should appear on large screens and let users navigate directly to any section.

## Requirements

### TOC Data Structure

The guide slug data used by the page already contains section information. Extend or use the existing `guide_slug` type to include a numeric level field representing heading depth (e.g., h2=2, h3=3). Each slug entry must have:
- `text: string` — the heading text
- `href: string` — the anchor link (e.g., "#section-name")
- `level: number` — the heading level for indentation

### Right-Side TOC Panel

Add a sidebar container that:
- Appears only on large screens (hidden on mobile)
- Stays visible while scrolling (sticky positioning)
- Shows all sections from the guide_slug data

### TOC Content and Styling

- Display the guide's `pretty_name` as a header at the top of the TOC
- List each section as a clickable link using the slug's `href`
- Indent entries based on their heading level (h2 entries at the base indent, h3 entries indented more, etc.)
- Highlight the currently-visible section with a distinct color while scrolling
- Use standard Tailwind utility classes consistent with the rest of the file

### Scroll Tracking

Track which section is currently in view. As the user scrolls, the TOC entry corresponding to the visible section should be highlighted.

### Content Area Adjustment

The main content area currently uses centered wide formatting. Modify it to make room for the right-side TOC by removing the center alignment and adjusting padding so both sidebars fit without overlap.

### Conditional Display

The TOC panel should only render when the guide has sections to display.

### Preservation

The existing left sidebar navigation and previous/next guide links must remain functional.