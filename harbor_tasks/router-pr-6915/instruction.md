# Markdown Sanitization Bug

The `sanitizeMarkdown` function in `scripts/llms-generate.mjs` is used to prepare markdown content for embedding in JavaScript template literals. However, it's currently producing incorrect output when the markdown contains backslashes.

## Problem

When markdown content contains backslash characters (e.g., Windows file paths like `C:\Users\name` or LaTeX expressions like `\frac{a}{b}`), the resulting JavaScript template literal can have syntax errors or produce unexpected output.

For example:
- Input: `path\to\file`
- Current output: The backslashes are not properly escaped for template literal usage
- Expected: Backslashes should be escaped so they appear correctly in the final output

## Location

Look at the `sanitizeMarkdown` function in `scripts/llms-generate.mjs`. The function currently handles backticks and template variable syntax (`${}`), but something is missing for proper template literal escaping.

## Requirements

- Fix the escaping issue so backslashes in markdown content are handled correctly
- Ensure existing functionality for backtick and template variable escaping still works
- The fix should handle various backslash-containing content: file paths, LaTeX, escape sequences
