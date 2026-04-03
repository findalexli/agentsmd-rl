# Fix panic when using join inside group clause

## Problem

The PRQL compiler panics (crashes) when a user writes a query that uses `join` inside a `group` clause that references a table from an outer scope. For example:

```prql
from c = companies
join ca = companies_addresses (c.tax_code == ca.company)
group c.tax_code (
  join a = addresses (a.id == ca.address)
  sort {-ca.created_at}
  take 2..
)
sort tax_code
```

This query causes a panic in the semantic lowering phase because the code assumes a table lookup will always succeed, but inside a `group` clause the outer table references are not accessible.

## Expected Behavior

Instead of panicking, the compiler should return a clear error message explaining that the table is not accessible in the current context, with a hint that `join` is not supported inside `group`.

The error handling pattern here — converting a panic on user input to a proper error return — is an important principle for the codebase. The project's `CLAUDE.md` should be updated to document this error handling guideline so that contributors avoid introducing similar `.unwrap()` calls on operations that can fail with user input.

## Files to Look At

- `prqlc/prqlc/src/semantic/lowering.rs` — where the panic occurs during the lowering phase
- `prqlc/prqlc/src/semantic/module.rs` — related `.unwrap()` call that should be made safe
- `CLAUDE.md` — project development guidelines that should document the error handling rule
