# Typography Component Performance Issue

## Problem

The `Typography` component's ellipsis feature is causing performance issues in dense table scenarios. When rendering many Typography elements with CSS ellipsis enabled, the page experiences significant reflow and layout thrashing due to expensive `isEleEllipsis` calls happening repeatedly.

## Symptom

Users report that tables with truncated text cells become sluggish. The `isEleEllipsis` function is being called unconditionally whenever CSS ellipsis is enabled, even when the tooltip feature is not configured.

## Affected Code

- `components/typography/Base/index.tsx` - the main Typography Base component implementation

## Expected Behavior

Native ellipsis measurement (via `isEleEllipsis`) should only be performed when both CSS ellipsis is enabled AND the tooltip feature is configured with a title. The component currently uses `useTooltipProps` hook to obtain tooltip configuration - this measurement is only needed to determine if a tooltip should be shown, not for the ellipsis display itself.

Specifically, the implementation must ensure that:

1. The expensive `isEleEllipsis` measurement is gated behind a condition that checks both `cssEllipsis` and whether a tooltip title is present
2. The hook that provides tooltip configuration is accessible before any measurement-dependent logic
3. The useEffect that controls ellipsis measurement includes appropriate dependencies that reflect whether measurement is needed
4. The ellipsis merging logic accounts for whether native measurement is required when determining if ellipsis is active
5. The IntersectionObserver setup properly reflects whether native ellipsis measurement is needed
6. The IntersectionObserver dependency array properly reflects the conditions under which native measurement is required
