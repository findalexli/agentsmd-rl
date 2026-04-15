# Make GLM-ASR documentation examples runnable

## Problem

The GLM-ASR model documentation at `docs/source/en/model_doc/glmasr.md` contains code examples that crash when executed. The examples have correctness issues and none are configured as runnable doc-builder test blocks.

Additionally, the project's build configuration does not properly support the documentation workflow — there is no `docs` install extra, and the doc-builder dependency is pinned to an outdated source.

## Requirements

### Setup configuration

`setup.py` must define:

- An `extras["docs"]` entry that installs `hf-doc-builder` (use the existing `deps_list()` helper).
- The `extras["testing"]` definition must concatenate its base dependency tuple with the docs extras using this pattern: `extras["testing"] = (...) + extras["docs"]` where the parenthesized group contains the existing testing dependencies.

`src/transformers/dependency_versions_table.py` must use the following value for the `"hf-doc-builder"` key:

```
hf-doc-builder @ git+https://github.com/huggingface/doc-builder.git@main
```

### GLM-ASR documentation examples

All Python code fences in `docs/source/en/model_doc/glmasr.md` should be marked as runnable using doc-builder's `runnable:<label>` syntax. Each runnable block needs a `# pytest-decorator:` line referencing `transformers.testing_utils.slow` and `transformers.testing_utils.require_torch`.

The code examples themselves must be self-contained and execute correctly end-to-end. Several examples currently crash due to bugs — incorrect object construction, missing imports, and incomplete code paths. Fix each example so it runs without errors.

### Contributor documentation

- Update the documentation build section of `CONTRIBUTING.md` to reflect the new install command for doc dependencies and to add guidance on writing and testing runnable doc examples with `pytest`.
- Add a "Run runnable Markdown blocks" subsection to `docs/source/en/testing.md` explaining how to execute runnable code fences from documentation pages using pytest.

## Files to look at

- `docs/source/en/model_doc/glmasr.md` — the GLM-ASR usage examples
- `setup.py` — package extras and dependency definitions
- `src/transformers/dependency_versions_table.py` — the dependency version lookup table
- `CONTRIBUTING.md` — contributor guide (documentation build section)
- `docs/source/en/testing.md` — testing guide for the project
