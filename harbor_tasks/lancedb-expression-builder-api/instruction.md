# LanceDB: type-safe expression builder for query filters

LanceDB exposes a Rust query API where filters are passed as raw SQL
strings via `QueryBase::only_if(filter: impl AsRef<str>)`. This works,
but it forces callers to construct SQL by string concatenation, which is
awkward when the filter values are typed Rust variables (numbers, bools,
quoted strings, dates) and there is no compile-time check that column
names exist or that operators line up with column types.

Add a public expression-builder API to the `lancedb` crate that lets
callers compose filter expressions in pure Rust and pass them to a query
without ever building a SQL string by hand.

## Public API surface

A new module `lancedb::expr` (i.e. a new file `rust/lancedb/src/expr.rs`,
exposed via `pub mod expr;` in `rust/lancedb/src/lib.rs`) must export the
following public items:

- `pub use datafusion_expr::col;` — column reference (`col("age")`).
- `pub use datafusion_expr::lit;` — typed literal (`lit(18)`, `lit("Alice")`).
- `pub use datafusion_expr::Expr as DfExpr;` — re-export the underlying
  expression type so callers can name it without depending on
  `datafusion_expr` directly.
- `pub fn lower(expr: Expr) -> Expr` — wraps the SQL `LOWER(...)` function.
- `pub fn upper(expr: Expr) -> Expr` — wraps the SQL `UPPER(...)` function.
- `pub fn contains(expr: Expr, search: Expr) -> Expr` — wraps the SQL
  `CONTAINS(haystack, needle)` function.
- `pub fn expr_cast(expr: Expr, data_type: arrow_schema::DataType) -> Expr` —
  wraps a SQL `CAST(... AS ...)`.
- `pub fn func(name: ..., args: Vec<Expr>) -> crate::Result<Expr>` — looks
  up a named scalar UDF in a registry that contains at least these names:
  `"lower"`, `"upper"`, `"contains"`, `"btrim"`, `"ltrim"`, `"rtrim"`,
  `"concat"`, `"octet_length"`. Returns `Err(crate::Error::InvalidInput
  { .. })` if the name is not in the registry.
- `pub fn expr_to_sql_string(expr: &Expr) -> crate::Result<String>` —
  unparses a Datafusion `Expr` back to a SQL string. On failure it must
  return `Err(crate::Error::InvalidInput { .. })`. (Implementation hint:
  the `datafusion-sql` crate provides an `unparser::expr_to_sql` API;
  `.to_string()` on the resulting AST yields the SQL text.)

Operator and combinator behaviour comes from Datafusion's `Expr` type:
`expr.gt(other)`, `expr.lt(other)`, `expr.eq(other)`, `expr.and(other)`,
`expr.or(other)`, `expr * other`, etc. all produce a new `Expr`. For
example, `col("age").gt(lit(18)).and(col("status").eq(lit("active")))`
must serialize to a SQL string that contains `age`, `18`, `status`,
`active`, the `AND` keyword, and a `>` operator.

To keep the surface area small you may put the unparser shim
(`expr_to_sql_string`) in a private submodule and re-export only the
function.

## Wiring it into the query API

Add a new method on the `QueryBase` trait in `rust/lancedb/src/query.rs`:

```rust
fn only_if_expr(self, filter: datafusion_expr::Expr) -> Self;
```

The blanket `impl<T: HasQuery> QueryBase for T` must implement it by
storing the expression on `QueryRequest::filter` as
`QueryFilter::Datafusion(...)`. The existing `QueryFilter::Datafusion`
variant already exists in the enum — you do not need to add a new variant.

Two filter codepaths must be updated to actually consume the new
`QueryFilter::Datafusion` variant instead of erroring out on it:

1. `rust/lancedb/src/remote/table.rs`, when serializing a query body for
   the cloud REST endpoint, currently rejects any filter that isn't
   `QueryFilter::Sql(...)` and returns `Error::NotSupported`. After this
   change, it must accept `QueryFilter::Datafusion(expr)`, convert it to
   a SQL string via `expr_to_sql_string`, and put that string in the
   request body's `filter` field. The same applies to the
   `Filter::Datafusion(expr)` arm in the version-counting / predicate
   request body — it should serialize to SQL into the `predicate` field.
   `Substrait` filters remain unsupported on the remote path.

2. `rust/lancedb/src/table/query.rs`, function `filter_to_sql`, currently
   returns `Error::NotSupported` for the `QueryFilter::Datafusion(_)`
   arm. After this change it must call `expr_to_sql_string` on the
   expression and return the resulting SQL.

Substrait filters keep their existing `NotSupported` behaviour on both
codepaths.

## Behavioural contract that must hold

- `expr_to_sql_string(&col("age").gt(lit(18)))` returns `Ok(sql)` where
  `sql` contains `age`, `18`, and `>`.
- `expr_to_sql_string(&col("name").eq(lit("Alice")))` returns `Ok(sql)`
  where `sql` contains `name` and `Alice`.
- `expr_to_sql_string(&col("a").gt(lit(18)).and(col("b").eq(lit("x"))))`
  produces a SQL string containing both `a` and `b`, both literals, and
  the keyword `AND`.
- `expr_to_sql_string(&col("a").lt(lit(5)).or(col("b").gt(lit(10))))`
  produces SQL containing `a`, `b`, `5`, `10`, and the keyword `OR`.
- `lower(col("name"))`, `upper(col("name"))`, and
  `contains(col("text"), lit("search"))` each round-trip through
  `expr_to_sql_string` to a SQL string that contains, respectively, the
  function names `lower`, `upper`, and `contains` (case-insensitive),
  along with the column / argument literals you passed in.
- `func("lower", vec![col("x")])` returns `Ok` and unparses to SQL
  containing `lower`. The same holds for `"upper"` and `"contains"`
  among the other names listed above.
- `func("totally_unknown_function_xyz", vec![col("x")])` returns `Err`
  (specifically a `crate::Error::InvalidInput`).
- The trait method `lancedb::query::QueryBase::only_if_expr(self, expr)`
  exists and takes a `datafusion_expr::Expr` by value.
- All existing query behaviour — including the SQL-string `only_if` path
  on a local `NativeTable` — continues to work unchanged.

## Crate dependencies

The `rust/lancedb/Cargo.toml` `[dependencies]` table will need to
reference `datafusion-functions` and `datafusion-sql` (matching the
DataFusion `51.0` major already used elsewhere in the workspace) so that
the string helpers and the SQL unparser are available.

## Code Style Requirements

This task is verified using the repo's own toolchain. Make sure your
changes:

- Compile cleanly: `cargo check -p lancedb --tests` must succeed.
- Are formatted with `cargo fmt --all` — the project enforces this in CI.
- Pass the project's lints: `cargo clippy --features remote --tests
  --examples` is the lint command the maintainers run before merging.
- Follow the rustdoc-example convention documented in `AGENTS.md`: any
  doctest that needs a live `Table` should be wrapped in a
  `# async fn query(table: &Table) -> Result<...>` shim so type-checking
  runs without requiring a populated test environment.
- Prefer `Into<T>` / `AsRef<T>` for stringy public-API parameters when
  practical.
