# Add a checked-in solution file for cDAC development

## Problem

The cDAC README (`src/native/managed/cdac/README.md`) currently asks developers to manually create a `cdac.slnx` solution file at the repo root by copy-pasting an XML template. This has two problems:

1. The template is **incomplete** — it's missing some cDAC projects (the Legacy library and the dump tests), so developers who follow it get an incomplete IDE experience.
2. Manual copy-paste of XML is error-prone and unnecessary when the file could just be checked into the repo.

## Expected Behavior

There should be a proper `cdac.slnx` solution file checked into `src/native/managed/cdac/` that includes **all** cDAC library projects and **all** test projects. The README should be updated to point developers to this checked-in file instead of asking them to create one manually.

## Files to Look At

- `src/native/managed/cdac/README.md` — contains the current manual setup instructions under "Unit testing"
- `src/native/managed/cdac/` — browse the subdirectories to discover all library and test projects that should be in the solution
- `.github/copilot-instructions.md` — repo coding conventions (especially markdown formatting rules)
