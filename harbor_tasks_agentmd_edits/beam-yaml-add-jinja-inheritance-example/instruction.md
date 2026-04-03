# Add Jinja Inheritance Example for Beam YAML Pipelines

## Problem

The Beam YAML examples already demonstrate two Jinja templating patterns — `{% include %}` and `{% import %}` — with working examples under `sdks/python/apache_beam/yaml/examples/transforms/jinja/`. However, there is no example showing Jinja2 **template inheritance** (`{% extends %}` / `{% block %}`), even though the examples catalog README already mentions "inheritance directives" as a planned pattern.

## What Needs to Be Done

Add a complete Jinja inheritance example, following the same structure as the existing `include/` and `import/` examples:

1. **Create a base pipeline YAML** that defines a full WordCount-style pipeline (Read → Split → Explode → Format → Write) with an extensible injection point where child pipelines can add extra transform steps.

2. **Create a child pipeline YAML** that inherits from the base pipeline and overrides the injection point to insert a `Combine` (word counting) step.

3. **Register the new example in the test framework** so it runs alongside the existing jinja tests. Look at how `wordCountInclude` and `wordCountImport` are registered in the test preprocessors and input data module under `testing/`.

4. **Document the new example** with a README following the same pattern as the sibling `include/README.md` and `import/README.md` — explain the files, what the inheritance pattern does, and how to run the pipeline.

## Files to Look At

- `sdks/python/apache_beam/yaml/examples/transforms/jinja/include/` — reference example using `{% include %}`
- `sdks/python/apache_beam/yaml/examples/transforms/jinja/import/` — reference example using `{% import %}`
- `sdks/python/apache_beam/yaml/examples/testing/examples_test.py` — test preprocessor registrations
- `sdks/python/apache_beam/yaml/examples/testing/input_data.py` — template data for jinja tests

## Notes

- All new source files must include the appropriate Apache 2.0 license header (see `.agent/skills/license-compliance/SKILL.md`).
- The child pipeline should demonstrate a practical use case — adding a word-counting aggregation step is a natural fit.
- Follow the same Jinja variable naming conventions used by the existing include/import examples.
