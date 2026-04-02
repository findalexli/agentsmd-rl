# Missing Table of Contents Sidebar on Guide Pages

## Problem

The Gradio documentation website's guide pages (`js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte`) currently only have a left-side navigation panel that lists all available guides by category. However, for longer guides with many sections, there is no way for users to quickly see or jump to specific sections within the current guide.

## Expected Behavior

Guide pages should display a right-side table of contents panel that:

1. Shows all section headings from the current guide
2. Supports hierarchical indentation based on heading level (h2, h3, etc.)
3. Highlights the currently visible section as the user scrolls
4. Is sticky so it remains visible while scrolling
5. Only appears on larger screens (hidden on mobile)

## Current Behavior

The guide page layout centers the main content (`mx-auto`) with only the left sidebar for inter-guide navigation. There is no in-page section navigation, making it difficult to navigate long guides.

## Relevant Files

- `js/_website/src/routes/[[version]]/guides/[guide]/+page.svelte` — the guide page component
- The `guide_slug` data already provides section heading text and anchor hrefs, but is missing heading level information needed for proper indentation

## Additional Context

The guide slug data structure currently only has `text` and `href` fields. To support hierarchical display, the heading level needs to be available as well. The scroll tracking should use a reactive approach consistent with the existing Svelte patterns in the file.
