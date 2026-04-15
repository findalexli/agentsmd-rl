# Add Jinja Inheritance Example for Beam YAML Pipelines

## Background

The Beam YAML examples directory at `sdks/python/apache_beam/yaml/examples/transforms/jinja/` contains two working Jinja templating examples:

- `include/wordCountInclude.yaml` — uses `{% include %}` to pull in sub-templates from `include/submodules/`
- `import/wordCountImport.yaml` — uses `{% import %}` to import macros from `import/macros/wordCountMacros.yaml`

Both examples are referenced in `input_data.py` via `word_count_jinja_template_data()` and `word_count_jinja_parameter_data()`.

## Problem

There is no example demonstrating Jinja2 **template inheritance** (`{% extends %}` / `{% block %}`). The examples catalog README mentions "inheritance directives" as a planned pattern but no such example exists.

The existing `include/` and `import/` examples serve as reference implementations for:
- How the base pipeline defines transforms with Jinja variable placeholders
- How the test framework (`examples_test.py` and `input_data.py`) registers examples
- What variable names the test data functions (`word_count_jinja_template_data`, `word_count_jinja_parameter_data`) provide

## Task

Demonstrate Jinja2 template inheritance by creating a working inheritance-based example alongside the existing `include/` and `import/` examples. The example should:

1. Provide a **base pipeline** that defines a WordCount-style pipeline (Read → Split → Explode → Format → Write) with one named `{% block %}` where child pipelines can inject additional transforms
2. Provide a **child pipeline** that uses `{% extends %}` to inherit from the base and `{% block %}` to inject a `Combine` step
3. Register in the test framework so the Jinja preprocessor tests exercise the new example
4. Include a README explaining the inheritance pattern

## Existing Test Data Contracts

The test framework has established contracts for what template data functions must return:

- `word_count_jinja_parameter_data()` returns JSON containing keys for each transform variable (e.g., `readFromTextTransform`, `mapToFieldsSplitConfig`, `combineTransform`). The existing include/import examples use specific variable names that must remain functional.
- `word_count_jinja_template_data('test_wordCountInclude_yaml')` returns a list of template paths including one that references `wordCountMacros.yaml`
- `word_count_jinja_template_data('test_wordCountImport_yaml')` returns a list of template paths
- `text_data()` returns text containing `KING LEAR` (used as test input for word count pipelines)

Your new example must follow the same variable naming conventions so the test framework can provide appropriate values.

## Reference Files

- `sdks/python/apache_beam/yaml/examples/transforms/jinja/include/` — reference for `{% include %}` pattern
- `sdks/python/apache_beam/yaml/examples/transforms/jinja/import/` — reference for `{% import %}` pattern
- `sdks/python/apache_beam/yaml/examples/testing/examples_test.py` — shows how examples are registered in preprocessors
- `sdks/python/apache_beam/yaml/examples/testing/input_data.py` — shows what template data functions return for existing examples

## Notes

- All new source files must include the Apache 2.0 license header
- Follow the same Jinja variable naming conventions used by the existing include/import examples
- The child pipeline should demonstrate a practical use case — adding a word-counting aggregation step via the inherited block