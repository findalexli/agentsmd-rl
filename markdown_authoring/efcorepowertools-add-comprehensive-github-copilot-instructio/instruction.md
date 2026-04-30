# Add comprehensive GitHub Copilot instructions for EF Core Power Tools development

Source: [ErikEJ/EFCorePowerTools#3139](https://github.com/ErikEJ/EFCorePowerTools/pull/3139)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

- [x] Explore repository structure and understand codebase
- [x] Identify .NET SDK version requirements (requires .NET 10 preview or .NET 8 for core components)
- [x] Test building core components (CLI tools and reverse engineering tools)
- [x] Verify existing test infrastructure works
- [x] Understand project structure (Visual Studio extension + CLI tools + core libraries)
- [x] Validate build times and document timeouts needed for long builds
- [x] Test installation of CLI tools via dotnet tool install
- [x] Create comprehensive validation scenarios for typical workflows
- [x] Test the Visual Studio extension build process limitations (requires Windows/VS)
- [x] Document manual validation scenarios for post-build verification
- [x] Write comprehensive GitHub Copilot instructions file
- [x] Validate instructions by following them step-by-step
- [x] Revert global.json changes as requested

## Comprehensive GitHub Copilot Instructions Created ✅

Created `.github/copilot-instructions.md` with complete development guidelines including:

### Key Features:
- **Exact build commands and timing expectations** (CLI: 15-20s, Tests: 20-25s, Dacpac: 7-10s)
- **NEVER CANCEL warnings** with specific timeout values for all operations
- **Step-by-step validation workflows** for CLI tool testing and reverse engineering
- **Comprehensive timing table** with recommended timeout settings
- **Platform-specific guidance** (Linux vs Windows development capabilities)
- **End-to-end scenarios** from 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
