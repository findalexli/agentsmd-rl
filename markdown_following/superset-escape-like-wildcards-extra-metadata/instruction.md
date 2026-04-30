# Fix wildcard handling in `ReportScheduleDAO.find_by_extra_metadata`

In Apache Superset, `ReportScheduleDAO.find_by_extra_metadata(slug)` returns
the report schedules whose `extra_json` column contains the given slug as a
substring. It is used (e.g.) when a dashboard tab is deleted to look up
alert/report schedules referencing that tab via its identifier.

The current implementation matches more rows than it should: when the slug
contains the SQL `LIKE` wildcards `%` (any sequence of characters) or `_`
(any single character), those characters are interpreted as wildcards
instead of literal characters in the user-supplied slug. As a result,
unrelated `extra_json` values can be returned, and operations driven by
this lookup (deactivating schedules tied to a deleted dashboard tab,
auditing schedules by metadata, etc.) act on the wrong rows.

The lookup should match the slug as a literal string regardless of which
characters appear inside it. A search for `"abc%xyz"` must match an
`extra_json` containing the seven-character substring `abc%xyz` and no
others; a search for `"p_q"` must match `extra_json` values containing
`p_q` and not values like `pXq`. A search for `"foo%"` must match
`extra_json` values containing the literal four characters `foo%` and
not, for example, `foobar`. Plain slugs with no special characters must
continue to behave as a normal substring match, and a slug that does not
appear anywhere must still produce an empty list.

The same module performs an analogous substring lookup elsewhere already
in a way that handles user-supplied input correctly; bringing
`find_by_extra_metadata` in line with the rest of the module is the
expected approach.

## Scope

- The fix lives in the backend module that defines
  `ReportScheduleDAO.find_by_extra_metadata`. The function's signature
  (`(slug: str) -> list[ReportSchedule]`) and its callers must not
  change — only the filter it builds against `ReportSchedule.extra_json`.
- No database migration is needed; this is a pure query change.
- You do not need to add tests; held-out tests are run separately.

## Code Style Requirements

The held-out test runner imports `superset.daos.report` and runs
`pytest`. It does not invoke linters or formatters, but the repository's
contribution guide (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/dev-standard.mdc`)
requires that all backend changes:

- Keep type hints on functions you touch.
- Stay MyPy-compliant (`pre-commit run mypy` is the CI gate).
- Stay Ruff-clean (no new linter violations); in particular, prefer
  `~Model.field` over `Model.field == False` in SQLAlchemy filters.
- Use timeless wording in any new code comments (avoid words like "now",
  "currently", "today").

These rules apply because the fix lives in a Python backend file
(`superset/daos/...`).
