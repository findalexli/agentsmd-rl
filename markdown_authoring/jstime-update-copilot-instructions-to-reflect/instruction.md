# Update Copilot instructions to reflect latest repository changes

Source: [jstime/jstime#349](https://github.com/jstime/jstime/pull/349)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR updates the `.github/copilot-instructions.md` file to reflect the current state of the jstime repository, incorporating recent architectural changes, new features, and updated dependencies.

## Overview

The Copilot instructions were outdated and didn't reflect several major improvements to the project. This update ensures that GitHub Copilot has accurate, comprehensive information about the codebase structure and development practices.

## Key Updates

### Architecture & Organization
- **Built-in APIs reorganized** by standards body into `whatwg/`, `w3c/`, and `node/` subdirectories
- Added **WebAssembly support** documentation
- Added **JSON modules** support (e.g., `import data from './data.json'`)
- Updated REPL features to include command history

### New Built-in APIs
Added documentation for recently implemented APIs:
- **Events**: `Event` and `EventTarget` classes (WHATWG DOM Standard)
- **Base64**: `atob()` and `btoa()` functions (WHATWG HTML Standard)
- **Structured Clone**: `structuredClone()` for deep cloning (HTML Standard)
- **File System**: Complete Node.js-compatible `fs/promises` API with 20+ functions

### Rust & Dependencies
- **Edition**: Updated from Rust 2021 to Rust 2024
- **ureq**: Updated from 2.10 to 3.1 with connection pooling support
- **New dependencies**: `rustc-hash` (2.1), `filetime` (0.2), `urlencoding` (2.1), `dirs` (6.0.0)
- **Updated versions**: `rustyline` to 17.0.2

### Testing Infrastructure
- Documented comprehensive **conformanc

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
