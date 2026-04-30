# Surface validation errors in the chart-generation MCP pipeline

You are working in the Apache Superset repository, checked out at
`/workspace/superset`. This task is about a silent-looking failure in the
Model-Context-Protocol (MCP) chart-generation pipeline.

## Symptom

When `ValidationPipeline.validate_request_with_warnings` (in
`superset/mcp_service/chart/validation/pipeline.py`) catches a `ValueError`
raised by `parse_chart_config`, it routes the sanitized reason through
`ChartErrorBuilder.build_error(...)` in
`superset/mcp_service/utils/error_builder.py`, passing
`template_key="validation_error"`. The current behavior of that call is:

```text
error.message     == "An error occurred"
error.details     == ""
error.suggestions == []
error.error_code  == "VALIDATION_PIPELINE_ERROR"
```

The actionable Pydantic error (which fields are wrong, which values are
expected) is silently discarded. LLM callers that read this response have
no idea what went wrong.

A concrete trigger that exposes the bug: pass a `mixed_timeseries` chart
config that uses the field names `kind` / `kind_secondary` (the wrong
names — the schema expects `primary_kind` / `secondary_kind`). At HEAD
the pipeline must instead return an error whose message and details name
the offending fields (e.g. `Unknown field 'kind'`) and whose `suggestions`
list is non-empty.

## Root cause

Two issues compound:

1. **Missing template registration.** `ChartErrorBuilder.TEMPLATES` is a
   dict of templates keyed by name (`missing_field`, `invalid_type`,
   `invalid_value`, `dataset_not_found`, `column_not_found`, …). The
   pipeline's call site already passes `template_key="validation_error"`,
   but no entry with that key exists. `build_error` falls back to its
   hard-coded defaults (`"An error occurred"`, empty details, no
   suggestions). The sanitized reason is discarded.

2. **Pydantic tagged-union prefix swallows the body.** When
   `parse_chart_config` raises, Pydantic's error string starts with a
   long header of the form

   ```
   1 validation error for tagged-union[…XYChartConfig…MixedTimeseriesChartConfig…]
   <discriminator>
     Value error, Unknown field 'kind'. Valid fields: …      ← actionable body
       For further information visit https://errors.pydantic.dev/…
   ```

   The header alone is well over 200 characters. The existing 200-char
   truncation in `_sanitize_validation_error` therefore returns the
   header and drops the body the user actually needs. The body always
   sits on a line indented by exactly two spaces; the trailing
   `For further information ...` footer is indented by four spaces.

   Both `Value error, …` bodies (from `field_validator` failures) and
   `Input should be …` bodies (from Pydantic `literal_error` failures)
   must survive the cleanup.

## Required behavior after the fix

1. `ChartErrorBuilder.TEMPLATES` must contain an entry for
   `"validation_error"`. Its `message` and `details` strings must use the
   `{reason}` template variable so the sanitized error reaches the user.
   Its `suggestions` must be a non-empty list.

2. Because this template fires for every chart type, its suggestions
   **must not** mention chart-type-specific field names — strings like
   `mixed_timeseries`, `primary_kind`, or `secondary_kind` must not
   appear in the suggestions list.

3. The 200-char truncation must operate on the actionable body, not on
   the tagged-union header. After the fix, neither
   `error.message` nor `error.details` may contain the substring
   `tagged-union`, and the body (e.g. the literal substrings
   `Unknown field` for the mixed-timeseries case and `Input should be`
   for an invalid pie-chart aggregate) must still be present in
   `error.details`.

4. Existing template keys (`missing_field`, `invalid_type`,
   `invalid_value`, `dataset_not_found`, `column_not_found`) must remain
   registered.

5. The valid happy-path config (mixed_timeseries with `primary_kind` /
   `secondary_kind`) must still validate successfully.

## Code Style Requirements

The repository runs `ruff check` and `ruff format` as part of its
pre-commit hooks. Both tools must report clean on the files you modify
(`superset/mcp_service/chart/validation/pipeline.py` and
`superset/mcp_service/utils/error_builder.py`). New code follows the
existing house style: type hints on all functions, modern Python 3.10+
union syntax (`X | None`, not `Optional[X]`), and ASF license headers
preserved at the top of every Python file.

## Verification

The grader runs `pytest /tests/test_outputs.py`. Each test mocks the
runtime side of the pipeline (dataset lookup, column normalisation,
runtime validation) and exercises only the schema-validation +
error-building path under test, so you do not need a live Superset
database.
