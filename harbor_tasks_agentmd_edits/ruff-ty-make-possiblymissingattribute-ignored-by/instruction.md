# Make `possibly-missing-attribute` ignored by default and split out `possibly-missing-submodule`

## Problem

The ty type checker's `possibly-missing-attribute` warning currently fires for both general attribute access on types with conditionally-defined attributes AND for submodule access on packages where the submodule wasn't explicitly imported. This produces a lot of false positives for the general attribute case, and other type checkers don't report it.

The submodule case, however, is valuable — accessing `html.parser` without first doing `import html.parser` really will raise `AttributeError` at runtime.

## What's Needed

1. **Split out `possibly-missing-submodule`** as a new, separate lint rule from `possibly-missing-attribute`:
   - Register the new lint in the diagnostic registry
   - Define it with a `warn` default level (since this case has real value)
   - Update `builder.rs` to use the new lint for submodule-specific diagnostics instead of `possibly-missing-attribute`
   - The diagnostic message should say something like "Submodule `X` might not have been imported" and suggest explicitly importing the submodule

2. **Change `possibly-missing-attribute` default to `ignore`**:
   - Change `default_level` from `Level::Warn` to `Level::Ignore` in `diagnostic.rs`
   - Add a "Rule status" section to the doc comment explaining why it's disabled

3. **Update all affected files**:
   - `ty.schema.json` — regenerate (run `cargo dev generate-all`)
   - `crates/ty/docs/rules.md` — regenerate
   - `.github/mypy-primer-ty.toml` — add `possibly-missing-attribute = "warn"` to keep it enabled for ecosystem testing
   - mdtest files — update `[possibly-missing-attribute]` → `[possibly-missing-submodule]` for submodule test cases
   - Snapshot files — update expected diagnostic output

## Files to Look At

- `crates/ty_python_semantic/src/types/diagnostic.rs` — lint definitions and registry
- `crates/ty_python_semantic/src/types/infer/builder.rs` — where diagnostics are emitted
- `crates/ty_python_semantic/resources/mdtest/attributes.md` — attribute test cases
- `crates/ty_python_semantic/resources/mdtest/import/nonstandard_conventions.md` — submodule import test cases
- `ty.schema.json` — JSON schema (regenerated)
- `AGENTS.md` — project conventions (see "Development Guidelines" for lint rule guidance)
