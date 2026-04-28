# Add GitHub Copilot instructions for repository

Source: [hiyouga/LlamaFactory#9675](https://github.com/hiyouga/LlamaFactory/pull/9675)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

- [x] Analyze repository structure and documentation
- [x] Create `.github/copilot-instructions.md` with relevant context about:
  - Project overview and purpose (efficient fine-tuning framework)
  - Code structure and organization (v0 and v1 architectures)
  - Development practices and style guide
  - Testing and quality requirements (with GPU context)
  - Common commands for building, testing, and linting
- [x] Address code review feedback:
  - Clarify entry scripts as delegates to main package
  - Update license check command to use Makefile
- [x] Address maintainer feedback:
  - Clarify that training requires GPU and is not tested end-to-end
  - Emphasize using `make test` for file-level validation
  - Document v0/v1 dual architecture with file hierarchies
  - Explain USE_V1 environment variable for version switching
- [x] Review and validate the instructions file

## Key Features Documented

**Architecture Versions**: LLaMA Factory has two parallel architectures (v0 default, v1 optional) that can be switched via the `USE_V1` environment variable:
- **v0 hierarchy**: `api`, `webui` → `chat`, `eval`, `train` → `data`, `model` → `hparams` → `extras`
- **v1 hierarchy**: `trainers` → `core` → `accelerator`, `plugins`, `config` → `utils`

**Project Context**: Clarified as an efficient fine-tuning framework for 100+ large language models with comprehensive details on supported models, training methods, and algorithms.

**Testing Guidelines**: Includes important context that tra

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
