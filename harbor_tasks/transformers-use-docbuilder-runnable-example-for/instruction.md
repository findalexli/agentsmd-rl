# Make GLM-ASR documentation examples runnable

## Problem

The GLM-ASR model documentation at `docs/source/en/model_doc/glmasr.md` contains code examples that crash when executed. The examples have correctness issues and none are configured as runnable doc-builder test blocks.

Additionally, the project's build configuration does not properly support the documentation workflow — there is no `docs` install extra, and the doc-builder dependency is pinned to an outdated version instead of using the current development branch.

## Requirements

### Setup configuration

`setup.py` must:

- Define an `extras["docs"]` entry that installs `hf-doc-builder`.
- Ensure `extras["testing"]` includes all dependencies from `extras["docs"]` so that documentation tests run in CI.

`src/transformers/dependency_versions_table.py` must reference `hf-doc-builder` using a git+ URL pointing to the `main` branch of `https://github.com/huggingface/doc-builder.git`.

### GLM-ASR documentation examples

All Python code fences in `docs/source/en/model_doc/glmasr.md` should be marked as runnable using doc-builder's `runnable:<label>` syntax. Each runnable block needs a `# pytest-decorator:` line referencing `transformers.testing_utils.slow` and `transformers.testing_utils.require_torch`.

The code examples themselves crash due to bugs — incorrect object construction (one example incorrectly calls `.from_pretrained()` on a processor class instead of a model class), missing imports, and incomplete code paths. Fix each example so it runs without errors and produces the expected output.

### Contributor documentation

- Update the documentation build section of `CONTRIBUTING.md` to reference the new `pip install ".[docs]"` command for documentation dependencies, and add guidance on writing and testing runnable doc examples with `pytest`.
- Add a subsection to `docs/source/en/testing.md` explaining how to execute runnable code fences from documentation pages using pytest.

## Files to look at

- `docs/source/en/model_doc/glmasr.md` — the GLM-ASR usage examples with bugs
- `setup.py` — package extras and dependency definitions
- `src/transformers/dependency_versions_table.py` — the dependency version lookup table
- `CONTRIBUTING.md` — contributor guide (documentation build section around line 390-410)
- `docs/source/en/testing.md` — testing guide for the project

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
