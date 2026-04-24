# Task: Add hugo.Data Access and Deprecate Site Methods

## Problem Description

Hugo needs to make site data (from the `/data` directory) accessible via `hugo.Data` in addition to the existing `site.Data` access point. The existing `site.Data` and several other Site methods should then be deprecated with appropriate warnings.

## Requirements

### 1. hugo.Data Access Point

Make site data accessible via `hugo.Data` in templates. This follows the same pattern as `hugo.Sites` which is already available. The Data identity constant in the siteidentities package should reference `"hugo.Data"` instead of `"site.Data"`.

The provider system (in the `resources/page` package) and the HugoInfo system need to be updated to support Data access alongside the existing Sites access. The HugoSites provider in hugolib also needs to expose Data.

### 2. Deprecation Warnings

Add deprecation warnings for the following Site methods in `hugolib/site.go`:

- **Site.Data**: Add a `// Deprecated: Use hugo.Data instead.` doc comment. The runtime deprecation should call `hugo.Deprecate(".Site.Data", "Use hugo.Data instead.", "v0.156.0")`.

- **Site.AllPages**: Add a `// Deprecated: See https://discourse.gohugo.io/t/56732.` doc comment. The runtime deprecation should call `hugo.Deprecate(".Site.AllPages", "See https://discourse.gohugo.io/t/56732.", "v0.156.0")`.

- **Site.BuildDrafts**: Add a `// Deprecated: See https://discourse.gohugo.io/t/56732.` doc comment. The runtime deprecation should call `hugo.Deprecate(".Site.BuildDrafts", "See https://discourse.gohugo.io/t/56732.", "v0.156.0")`.

- **Site.Languages**: Add a `// Deprecated: See https://discourse.gohugo.io/t/56732.` doc comment. The runtime deprecation should call `hugo.Deprecate(".Site.Languages", "See https://discourse.gohugo.io/t/56732.", "v0.156.0")`.

Each deprecation should use `sync.Once` to ensure the warning prints only once per method, following the existing deprecation pattern in the codebase (e.g., for `.Site.Sites`).

## Relevant Files

- `hugolib/site.go` - Main Site struct with methods to deprecate
- `hugolib/hugo_sites.go` - HugoSites struct and provider
- `resources/page/hugoinfo.go` - HugoInfo configuration and provider interfaces
- `resources/page/page.go` - Core interfaces and nop providers
- `resources/page/siteidentities/identities.go` - Identity constants

## Testing

The repository uses Go's testing framework. Run:
- `go test ./hugolib/...` for hugolib package tests
- `go test ./resources/page/...` for page package tests
- `go vet ./...` for static analysis

Look at existing deprecation implementations (like `.Site.Sites`) for the pattern to follow.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
