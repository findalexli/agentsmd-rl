# Fix Panic on Edit of Legacy Mapped Template Names

## Problem Description

Hugo v0.146.0 introduced a panic when editing templates with legacy mapped template names. Specifically, if you edit a template like `tags/list.html` (which has a legacy mapping from the old `layouts/tags/list.html` to a new internal path), Hugo crashes with a panic during the file refresh/rebuild process.

The issue occurs in the template store's refresh logic. When a file is edited and Hugo tries to refresh templates, it calls `parseTemplates(true)` with a `replace` parameter. This parameter was intended to indicate whether we're in a refresh scenario, but it accidentally disables duplicate name checking, leading to template name collisions.

## Relevant Files and Functions

The bug is in the `tpl/tplimpl` package:

1. **`templatestore.go`**:
   - `parseTemplates(replace bool)` - This function should not take a `replace` parameter
   - Called from `NewStore()` (with `false`) and `RefreshFiles()` (with `true`)

2. **`templates.go`**:
   - `parseTemplate(ti *TemplInfo, replace bool)` - Should not take `replace` parameter
   - `doParseTemplate(ti *TemplInfo, replace bool)` - Should not take `replace` parameter
   - The key logic bug is in `doParseTemplate`:
     ```go
     // BEFORE (buggy):
     if !replace && prototype.Lookup(name) != nil {
         name += "-" + strconv.FormatUint(t.nameCounter.Add(1), 10)
     }

     // AFTER (fixed):
     if prototype.Lookup(name) != nil {
         name += "-" + strconv.FormatUint(t.nameCounter.Add(1), 10)
     }
     ```

## Expected Behavior

When editing a template file (like `layouts/tags/list.html`), Hugo should:
1. Successfully refresh the template without panicking
2. Properly handle duplicate template name conflicts by appending a counter
3. Complete the rebuild and serve the updated content

## What You Need to Do

Remove the `replace bool` parameter from the template parsing functions and always perform the duplicate name check. Specifically:

1. Remove `replace bool` parameter from `parseTemplates()` in `templatestore.go`
2. Remove `replace bool` parameter from `parseTemplate()` in `templates.go`
3. Remove `replace bool` parameter from `doParseTemplate()` in `templates.go`
4. Remove the `!replace &&` condition in `doParseTemplate()` - always check for duplicates
5. Update all call sites to not pass the `replace` parameter

The fix is straightforward refactoring - removing a parameter that was causing incorrect behavior. The `replace` flag was meant to optimize refresh scenarios but instead caused panics.

## Test the Fix

To verify your fix works:
1. Build Hugo: `go build .`
2. Run the regression test: `go test -run TestRebuildEditTagsListLayout ./hugolib`
3. Run all related tests: `go test ./tpl/tplimpl ./hugolib`

If the fix is correct, Hugo will no longer panic when editing templates with legacy mapped names.
