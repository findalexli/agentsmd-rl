# Biome HTML formatter: break parents that mix text and visible block-like children

You are working on the Biome toolchain (https://github.com/biomejs/biome), a
multi-language linter and formatter. The repository is checked out at
`/workspace/biome`.

The HTML formatter inside `crates/biome_html_formatter/` currently mis-formats
block-like elements that have **a mix of text nodes and visible block-like
children**. Your job is to fix the formatter so it matches Prettier's
behavior, while leaving formatting around `display: none` elements alone.

## The bug

Given the input:

```html
<div>a<div>b</div> c</div>
```

the formatter currently keeps the line as-is (printing it back unchanged on
one line). Prettier produces, and Biome should produce:

```html
<div>
	a
	<div>b</div>
	c
</div>
```

The rule: when an element contains both text and at least one **visible
block-like** child element, the parent must be broken across multiple lines,
with each child on its own line.

## What "visible block-like" means here

Biome already has the helper `CssDisplay::is_block_like()` in
`crates/biome_html_formatter/src/utils/css_display.rs`. For historical
reasons that helper currently returns `true` for `CssDisplay::None` even
though `display: none` is whitespace-sensitive. **Do not change which variants
`is_block_like()` matches.** Instead, treat `display: none` as a separate case
at the call sites: a child whose `CssDisplay` equals `CssDisplay::None`
must NOT trigger the new line-breaking behaviour.

Concretely the input

```html
<div>123<meta attr />456</div>
```

must continue to format on a single line as `<div>123<meta attr>456</div>`
(the `<meta>` element resolves to `display: none`, and inserting whitespace
around it would be a visible behavior change).

## Where the change lives

The fix is purely inside the HTML formatter crate, no cross-crate changes.
Look at how children are joined in
`crates/biome_html_formatter/src/html/lists/element_list.rs` — the formatter
already distinguishes `is_inline_like()` children, but in the non-inline
branch it treats every kind of non-inline element identically. You need to
split that branch into three cases (visible block-like / `display: none` /
everything else) in **multiple places** along the joining logic, including:

- where a Word (text node) is followed by a non-inline child,
- where a non-inline child is followed by a Word, and
- where the joiner picks the line-break mode between two non-text children.

In all three places, a visible block-like neighbour should force a hard
line break (and set the parent to multiline); a `display: none` neighbour
should keep the existing behaviour without inserting any extra whitespace.

## Code Style Requirements

The test runner enforces the repository's standard Rust toolchain:

- `cargo fmt --check` (whole workspace) — must succeed.
- `cargo clippy -p biome_html_formatter --all-targets -- --deny warnings`
  — must succeed; no new warnings.

## Acceptance criteria

The following test names are part of the snapshot test harness in
`crates/biome_html_formatter/tests/specs/html/whitespace/`:

- `force-break-nontext-and-non-sensitive-sibling.html`
  (input `<div>a<div>b</div> c</div>`) — currently fails; must pass.
- `force-break-nontext-and-non-sensitive-sibling-2.html`
  (input `<div>before<article>middle</article>after</div>`) — same rule
  with a different visible block-like element (`<article>`); currently
  fails; must pass.
- `no-break-display-none.html`
  (input `<div>123<meta attr />456</div>`) — must continue to pass.

All other tests under `cargo test -p biome_html_formatter --test spec_tests`
must continue to pass, and the workspace must remain `cargo fmt`- and
`cargo clippy`-clean.
