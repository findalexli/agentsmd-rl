# Sitemap XML Validation Error

## Problem

The generated sitemap XML fails validation with the error:

```
Namespace prefix xhtml on link is not defined
```

This error occurs when validating sitemaps that include alternate language links (`xhtml:link` elements for `hreflang` attributes).

## Location

The sitemap generation code is in `packages/start-plugin-core/src/build-sitemap.ts`. The `jsonToXml` function constructs the XML sitemap document.

## Expected Behavior

Generated sitemaps should pass XML validation and comply with sitemap standards, including proper namespace declarations for any prefixed elements used.

## Reproduction

When a sitemap is generated with alternate language URLs (e.g., for multilingual sites), the resulting XML uses `xhtml:link` elements but the validator reports the `xhtml` namespace prefix is undefined.

## Hints

- Look at how the root XML element is created
- Check what namespace declarations are present vs. what prefixes are used in the document
- The `xhtml:link` elements are used for alternate language references per the sitemap protocol

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
