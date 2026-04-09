# Fix styled-jsx styles dropped during Pages Router SSR

## Problem

In the Pages Router SSR path, dynamic styled-jsx styles (those with interpolated expressions that compute class names at runtime via DJB2 hashing) are silently dropped from the rendered HTML. This causes a flash of unstyled content (FOUC) on first load.

The issue is particularly visible in production deployments where components use dynamic styled-jsx with interpolated props (e.g., `color: ${color}`), since those styles only exist in the registry after rendering completes. The numeric `jsx-*` class names are present in the HTML elements, but the corresponding `<style>` tags are missing from the SSR output.

## Expected Behavior

All dynamic styled-jsx styles should be present as inline `<style>` tags in the SSR output. When a page uses multiple nested components with dynamic styled-jsx, every component's styles should appear in the rendered HTML.

## Files to Look At

- `packages/next/src/server/render.tsx` — the server-side rendering implementation for the Pages Router. The `renderToHTMLImpl` function orchestrates page rendering and style collection. Look at how `styledJsxInsertedHTML()` interacts with the page render lifecycle — the timing of when the style registry is read relative to when the page finishes rendering is critical.
