# SearchBar clear button shows stale search value

## Problem

The SearchBar component in the Airflow UI has a bug where clearing the search input sometimes shows a stale (previously typed) value.

Steps to reproduce:
1. Start typing in the SearchBar (e.g., type "air")
2. Quickly click the clear button (the X icon) before finishing
3. The input clears momentarily, but then the previously typed value ("air") reappears

This happens because the search uses debouncing for performance, but when the user clears the input, something goes wrong with the timing.

## Location

The SearchBar component is located at:
- `airflow-core/src/airflow/ui/src/components/SearchBar.tsx`

## Expected behavior

When the user clicks the clear button:
1. The input should immediately show an empty value
2. The search should be cleared
3. No stale values should reappear after any delay

## Hints

- The component uses lodash's debounce function for the onChange handler
- Look at how the clear button handler interacts with the debounced function
- Consider what happens to pending debounced calls when the user clears the input

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
