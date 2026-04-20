# Shadow DOM Support for Combobox Component

## Background

Shadow DOM is a browser technology that encapsulates DOM subtrees, preventing external CSS and JavaScript from accessing internal elements. When a web component uses Shadow DOM, its internal elements are hidden from `document.querySelector()` calls made from outside.

## The Problem

The Mantine `Combobox` component uses `document.querySelector` and `document.querySelectorAll` to locate option elements within the dropdown. This works fine in regular DOM trees, but **fails when the Combobox is rendered inside a Shadow DOM**.

When a Combobox is used inside a Shadow DOM context:
- `selectOption()` cannot find the dropdown options
- `selectActiveOption()` cannot find the active option
- `selectNextOption()` / `selectPreviousOption()` keyboard navigation fails
- The dropdown options exist in the DOM but are invisible to the query functions

### Example Failure Scenario

A web component with Shadow DOM renders a Mantine `Combobox` with options:

```tsx
class MyComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    render(
      <Combobox>
        <Combobox.Option value="1">One</Combobox.Option>
        <Combobox.Option value="2">Two</Combobox.Option>
      </Combobox>,
      this.shadowRoot
    );
  }
}
```

When the user tries to select an option using keyboard navigation or clicks, the selection fails silently because `document.querySelector` cannot penetrate the Shadow DOM boundary.

## Expected Behavior

The Combobox component should function correctly regardless of whether it's rendered in a regular DOM or inside a Shadow DOM. Specifically:

1. `findElementsBySelector()` should find all elements matching a CSS selector, even when they are inside Shadow DOM boundaries
2. `findElementBySelector()` should find a single element, searching through Shadow DOM levels
3. `getRootElement()` should return the correct root node (`document` or `ShadowRoot`) for queries
4. The Combobox's `selectOption()`, `selectActiveOption()`, `selectNextOption()`, `selectPreviousOption()`, `selectFirstOption()`, `updateSelectedOptionIndex()`, `clickSelectedOption()`, and `clearSelectedItem()` methods should all work correctly inside Shadow DOM

## Verification

After the fix is applied, the following should be true:

- New utility functions `findElementBySelector`, `findElementsBySelector`, and `getRootElement` exist in `packages/@mantine/core/src/core/utils/`
- The `use-combobox.ts` hook uses these utilities to query elements
- The utilities correctly traverse Shadow DOM boundaries to find elements
- The TypeScript compilation succeeds without errors