# Add Jinja Inheritance Example for Beam YAML Pipelines

## Problem

The Beam YAML examples already demonstrate two Jinja templating patterns — `{% include %}` and `{% import %}` — with working examples under `sdks/python/apache_beam/yaml/examples/transforms/jinja/`. However, there is no example showing Jinja2 **template inheritance** (`{% extends %}` / `{% block %}`), even though the examples catalog README already mentions "inheritance directives" as a planned pattern.

## What Needs to Be Done

Add a complete Jinja inheritance example, following the same structure as the existing `include/` and `import/` examples:

1. **Create a base pipeline YAML** at `inheritance/base/base_pipeline.yaml` that defines a full WordCount-style pipeline (Read → Split → Explode → Format → Write) with an extensible injection point where child pipelines can add extra transform steps. The base pipeline must use a Jinja `{% block %}` directive — the block name used in the existing `include/` and `import/` examples follows the same pattern.

2. **Create a child pipeline YAML** at `inheritance/wordCountInheritance.yaml` that uses `{% extends "apache_beam/yaml/examples/transforms/jinja/inheritance/base/base_pipeline.yaml" %}` to inherit from the base pipeline, and uses `{% block %}` to override the injection point and insert a `Combine` (word counting) step.

3. **Register the new example in the test framework** so it runs alongside the existing jinja tests:
   - The test identifier must be `test_wordCountInheritance_yaml`
   - In `examples_test.py`, register it in the wordcount Jinja preprocessor, the io_write preprocessor, and the jinja preprocessor (appearing at least 3 times total)
   - In `input_data.py`, the function `word_count_jinja_template_data('test_wordCountInheritance_yaml')` must return the base pipeline path `inheritance/base/base_pipeline.yaml`
   - In `input_data.py`, the function `word_count_jinja_parameter_data()` must include keys for `readFromTextTransform`, `combineTransform`, and `mapToFieldsSplitConfig`

4. **Document the new example** with a README following the same pattern as the sibling `include/README.md` and `import/README.md` — explain the files, what the inheritance pattern does, and how to run the pipeline.

## Files to Look At

- `sdks/python/apache_beam/yaml/examples/transforms/jinja/include/` — reference example using `{% include %}`
- `sdks/python/apache_beam/yaml/examples/transforms/jinja/import/` — reference example using `{% import %}`
- `sdks/python/apache_beam/yaml/examples/testing/examples_test.py` — test preprocessor registrations
- `sdks/python/apache_beam/yaml/examples/testing/input_data.py` — template data for jinja tests (must return `readFromTextTransform`, `combineTransform`, `mapToFieldsSplitConfig` keys from `word_count_jinja_parameter_data()`)

## Jinja Template Variables

The base and child pipelines must accept these template variable names (matching the pattern used by the existing include/import examples):

| Variable name | Purpose |
|---|---|
| `readFromTextTransform` | Configuration for the ReadFromText transform (must include a `path` sub-key) |
| `mapToFieldsSplitConfig` | Configuration for splitting lines into words (must include `language` and `fields` sub-keys) |
| `explodeTransform` | Configuration for exploding lines into words (must include a `fields` sub-key) |
| `combineTransform` | Configuration for the Combine transform in the child's block override (must include `group_by` and `combine` sub-keys) |
| `mapToFieldsCountConfig` | Configuration for formatting the count output (must include `language` and `fields` sub-keys) |
| `writeToTextTransform` | Configuration for writing results (must include a `path` sub-key) |

## Notes

- All new source files must include the appropriate Apache 2.0 license header (see `.agent/skills/license-compliance/SKILL.md`).
- The child pipeline should demonstrate a practical use case — adding a word-counting aggregation step is a natural fit.
- Follow the same Jinja variable naming conventions used by the existing include/import examples.
