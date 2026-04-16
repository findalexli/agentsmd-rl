# Bug: Jinja templates not rendering in adhoc column filters

When using a virtual dataset with Jinja templates in the SQL definition (e.g., `{{ current_username() }}`), the templates work correctly in most contexts. However, when applying a cross-filter (adhoc column filter) to a chart using this virtual dataset, the Jinja template syntax is passed directly to SQLGlot instead of being rendered first.

This causes SQLGlot to fail parsing the SQL because it receives unparsed Jinja syntax like `{{ current_username() }}` instead of the rendered value.

## Symptoms

- Virtual dataset with Jinja template SQL works normally for basic queries
- Adding an adhoc column filter (cross-filter) to a chart causes a parse error
- Error mentions SQLGlot failing to parse the query containing unrendered Jinja syntax

## Details

The `adhoc_column_to_sqla` method accepts a `template_processor` parameter for rendering Jinja templates before SQL processing. Investigate the query generation code paths — specifically how adhoc column filters are converted to SQL expressions — to find where the template processor is not being passed through, causing Jinja templates to remain unrendered in that code path.
