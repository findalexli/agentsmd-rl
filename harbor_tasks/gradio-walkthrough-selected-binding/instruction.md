# Bug: Walkthrough tab navigation breaks when going back and forward

## Summary

The Gradio `Tabs` component has a "walkthrough" mode (used for step-by-step wizard UIs). When a user navigates forward programmatically (e.g., by clicking a "next step" button that sets `selected`), then clicks a stepper button to go **back** to a previous step, and then tries to go **forward** again by clicking the same "next step" button — the forward navigation silently fails.

## Reproduction

1. Create a Gradio app with `gr.Tabs()` in walkthrough mode containing multiple tab steps
2. Each step has a button that programmatically advances to the next step by updating `selected`
3. Navigate from step 0 → step 1 using the button
4. Click the stepper UI (tab header) to go back to step 0
5. Click the "next" button again to go to step 1
6. **Expected**: Step 1 becomes visible again
7. **Actual**: Nothing happens — the UI stays on step 0

## Root Cause Area

The issue is in `js/tabs/Index.svelte`, in the section that renders the `Walkthrough` component. The `selected` prop is being passed in a way that doesn't synchronize state changes back to the parent when the user interacts with the stepper UI directly. This creates a mismatch: the parent thinks the selected tab is still the one it last set programmatically, so when the button tries to set the same value again, no change is detected and no navigation occurs.

Compare how the same prop is handled for the regular `Tabs` component in the same file — the two branches handle it differently.

## Files to Investigate

- `js/tabs/Index.svelte` — the main Tabs component wrapper that delegates to either `Tabs` or `Walkthrough`
- `js/tabs/shared/Walkthrough.svelte` — the walkthrough implementation
