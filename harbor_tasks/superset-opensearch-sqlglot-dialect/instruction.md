# Add an OpenSearch SQL dialect to Superset

Superset ships a small set of SQL-dialect adapters layered on top of
[`sqlglot`](https://github.com/tobymao/sqlglot). They live under
`superset/sql/dialects/` and are wired into the `SQLGLOT_DIALECTS` mapping
in `superset/sql/parse.py`.

## Symptom

When Superset talks to an OpenSearch SQL connection (the SQLAlchemy driver
for OpenSearch is registered under the dialect name **`odelasticsearch`**),
queries against tables with mixed-case columns can be mis-emitted by
SQLGlot. Concretely, the following:

```sql
SELECT "AvgTicketPrice" FROM "flights"
```

is parsed and re-rendered as if `"AvgTicketPrice"` were a string literal,
not a column reference. The reason is that SQLGlot currently has **no entry
at all** for `odelasticsearch` in Superset's `SQLGLOT_DIALECTS` mapping —
there is only a placeholder comment — and there is no Superset-level
`OpenSearch` dialect class to bind it to. Falling back to plain MySQL
treats `"…"` as a string-literal delimiter, so identifiers vanish into
literals.

This is observed when, for example, building an unaggregated table chart
on a column whose name has any uppercase character. ElasticSearch is
**not** affected by this issue and does not need a dialect change.

## What to implement

The OpenSearch SQL grammar is essentially MySQL with one important
difference: it accepts **both** double-quotes and backticks as identifier
delimiters. Your job is to express that to SQLGlot and register it for
the `odelasticsearch` SQLAlchemy dialect name.

Specifically:

1. **Create a new module** for the OpenSearch dialect under
   `superset/sql/dialects/`. The module should expose a class named
   `OpenSearch` that subclasses `sqlglot.dialects.mysql.MySQL` and overrides
   the tokenizer so that **both `"` and `` ` ``** are treated as
   identifier delimiters (rather than MySQL's default of treating `"` as a
   string-literal delimiter).

2. **Re-export `OpenSearch`** from `superset/sql/dialects/__init__.py`
   alongside the other dialects (`DB2`, `Dremio`, `Firebolt`, `FireboltOld`,
   `Pinot`). It must be importable as `from superset.sql.dialects import
   OpenSearch` and should appear in `__all__`.

3. **Register it in `superset/sql/parse.py`** by mapping the
   SQLAlchemy dialect name `"odelasticsearch"` to the `OpenSearch`
   class inside the `SQLGLOT_DIALECTS` dictionary. Replace the existing
   placeholder line for that key.

## Behavioural contract

After your change, parsing and re-rendering with the `OpenSearch` dialect
must produce these exact outputs:

- Input: `SELECT "AvgTicketPrice" FROM "flights"`
  Output (pretty=True):
  ```
  SELECT
    "AvgTicketPrice"
  FROM "flights"
  ```

- Input: `SELECT * FROM flights WHERE Carrier = 'Kibana Airlines'`
  Output (pretty=True):
  ```
  SELECT
    *
  FROM flights
  WHERE
    Carrier = 'Kibana Airlines'
  ```
  (Single-quoted strings must remain string literals — only `"` and `` ` ``
  are identifier delimiters.)

- Input: ``SELECT `AvgTicketPrice` FROM `flights` `` — backtick-quoted
  identifiers must round-trip as identifiers. SQLGlot will emit them
  using the dialect's first identifier-quote character on output.

- Input mixing both quote styles must round-trip cleanly to a single
  consistent identifier-quote style.

In addition, `superset.sql.parse.SQLGLOT_DIALECTS["odelasticsearch"]` must
be the `OpenSearch` class (identity, not just a string match), and the
existing entries for other databases (`oceanbase`, `oracle`, `netezza`,
`pinot`, etc.) must remain intact.

## Code style requirements

- The new Python file must include the standard **Apache Software
  Foundation licence header** (the same header used by every other file
  under `superset/`). New files without it will fail the project's
  `pre-commit` checks (see `AGENTS.md` → "Apache License Headers").
- Add **type hints** to any new code (project rule from `AGENTS.md` → 
  "Python Backend").
- Keep the new module **lightweight**: it only needs to depend on
  `sqlglot.dialects.mysql.MySQL`. Do not pull in flask, SQLAlchemy or
  other heavy Superset modules.
- Provide a brief module-level docstring explaining the dialect's purpose
  (per `AGENTS.md` → "Documentation Requirements: Docstrings").

## Where to look

- `superset/sql/dialects/` — sibling dialect modules (`db2.py`,
  `dremio.py`, `pinot.py`, …) show the project's style for these adapters.
- `superset/sql/parse.py` — find the `SQLGLOT_DIALECTS` dictionary and the
  surrounding imports.

## Notes

- Do **not** modify the upstream `sqlglot` package; the OpenSearch dialect
  is Superset-local.
- Restrict your change to the dialect itself and its registration. Do
  not refactor unrelated code.
