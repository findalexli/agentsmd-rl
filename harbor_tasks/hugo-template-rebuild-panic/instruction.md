# Hugo Issue #14740: Panic on Template Edit with Legacy Mapped Names

## Problem Description

Hugo panics when editing template files that have legacy mapped names (e.g., `layouts/tags/list.html`) while the server is running in live reload mode.

### Symptoms

When you:
1. Create a Hugo site with a template at `layouts/tags/list.html`
2. Run the Hugo server or build the site
3. Edit the `layouts/tags/list.html` file (triggering a rebuild)

You get a panic during the rebuild. The panic occurs during template parsing when the system tries to re-register a template that already exists.

The error indicates a duplicate template name is being registered, suggesting the duplicate check is being skipped in certain code paths.

### Expected Behavior

Editing a template file during live reload should:
1. Not cause a panic
2. Properly update the template in the registry
3. Use the updated template for subsequent builds

### Required Function Signatures

After the fix, these function signatures must exist exactly as written:

- `func (s *TemplateStore) parseTemplate(ti *TemplInfo) error`
- `func (t *templateNamespace) doParseTemplate(ti *TemplInfo) error`
- `func (s *TemplateStore) parseTemplates() error`

All calls to these functions must match the signatures above (single parameter for `parseTemplate` and `doParseTemplate`, no parameters for `parseTemplates`).

### Required Code Pattern

The duplicate template name check must always run using exactly this pattern:
- `if prototype.Lookup(name) != nil`

This check should occur before registering a template name and should not be conditional on any boolean flag.

### Steps to Reproduce

1. Create a Hugo site with `layouts/tags/list.html` containing "Foo."
2. Build the site (should work)
3. Edit `layouts/tags/list.html` to contain "Bar."
4. Build again - this triggers the panic on the buggy version

### Implementation Notes

The panic occurs in the template parsing code path during live reload. Investigate how templates are parsed and registered during rebuilds, particularly when template files are updated. Look for places where duplicate template detection might be conditionally skipped.
