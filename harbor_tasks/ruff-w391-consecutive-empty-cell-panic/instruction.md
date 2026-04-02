# W391 Trailing Newline Check Panics on Notebooks with Consecutive Empty Cells

## Bug Description

When running ruff's `W391` rule (too many newlines at end of file) with `--preview` mode on a Jupyter notebook (`.ipynb`) that contains **consecutive empty code cells**, ruff panics instead of producing diagnostics.

For example, a notebook with the following cell structure triggers the crash:
- Cell 1: `1+1\n`
- Cell 2: `\n\n` (empty/whitespace only)
- Cell 3: `\n\n` (empty/whitespace only)
- Cell 4: `\n\n` (empty/whitespace only)

Running `ruff check --preview --select W391 notebook.ipynb` on this notebook causes a panic.

## Relevant Code

The trailing newline diagnostic logic lives in:
- `crates/ruff_linter/src/rules/pycodestyle/rules/too_many_newlines_at_end_of_file.rs` — the `notebook_newline_diagnostics` function processes notebook cells for W391
- `crates/ruff_notebook/src/cell.rs` — `CellOffsets` provides cell boundary information
- `crates/ruff_notebook/src/notebook.rs` — builds the concatenated source and cell offsets

## Root Cause

The current implementation iterates tokens in reverse across the **entire concatenated notebook source** and tries to advance past cell boundaries using `peeking_take_while`. This approach fails when consecutive empty cells produce token sequences that don't align with the expected reverse iteration pattern, leading to incorrect offset calculations and eventually a panic.

## Expected Behavior

`ruff check --preview --select W391` should process each cell independently and emit W391 diagnostics for cells with too many trailing newlines, without panicking — regardless of how many consecutive empty cells exist.
