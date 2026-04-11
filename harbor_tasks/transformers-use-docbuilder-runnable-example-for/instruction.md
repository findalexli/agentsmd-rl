# Make GLM-ASR documentation examples runnable

## Problem

The GLM-ASR model documentation at `docs/source/en/model_doc/glmasr.md` has several code examples that are broken and not set up as runnable doc tests:

1. The "advanced" usage example incorrectly uses `GlmAsrForConditionalGeneration.from_pretrained()` to create the **processor** instead of `AutoProcessor.from_pretrained()`. It also never instantiates the model, so the example would crash.
2. The "audio array" example imports `load_dataset` from `datasets` but is missing the `Audio` import it needs.
3. The "batched" example uses a simplified `apply_transcription_request` call pattern that doesn't demonstrate the full chat template workflow.
4. None of the code fences are marked as runnable using doc-builder's `runnable:<label>` syntax, so they cannot be tested with `pytest`.

Additionally, the project has no `docs` install extra in `setup.py`, so there's no clean way to install `hf-doc-builder`. The dependency version table still points to the old PyPI release instead of the current git main branch.

## Expected Behavior

- All Python code fences in the GLM-ASR doc should be marked with `runnable:<label>` and include appropriate `# pytest-decorator:` lines.
- The code examples should be correct and complete — each should work end-to-end if executed.
- `setup.py` should define an `extras["docs"]` entry that installs `hf-doc-builder`, and the `testing` extras should include it.
- The `hf-doc-builder` dependency should point to the git main branch URL.
- After fixing the code and setup, update the relevant project documentation to reflect the new runnable examples workflow — contributors should know how to write and test runnable doc examples.

## Files to Look At

- `docs/source/en/model_doc/glmasr.md` — the broken GLM-ASR usage examples
- `setup.py` — package extras and dependency definitions
- `src/transformers/dependency_versions_table.py` — the dependency version lookup table
- `CONTRIBUTING.md` — contributor guide (documentation build section)
- `docs/source/en/testing.md` — testing guide for the project
