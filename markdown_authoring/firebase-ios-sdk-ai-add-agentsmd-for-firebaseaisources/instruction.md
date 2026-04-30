# [AI] Add AGENTS.md for FirebaseAI/Sources

Source: [firebase/firebase-ios-sdk#15871](https://github.com/firebase/firebase-ios-sdk/pull/15871)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `FirebaseAI/Sources/AGENTS.md`
- `FirebaseAI/Sources/Protocols/AGENTS.md`
- `FirebaseAI/Sources/Protocols/Internal/AGENTS.md`
- `FirebaseAI/Sources/Types/AGENTS.md`
- `FirebaseAI/Sources/Types/Internal/AGENTS.md`
- `FirebaseAI/Sources/Types/Internal/Errors/AGENTS.md`
- `FirebaseAI/Sources/Types/Internal/Imagen/AGENTS.md`
- `FirebaseAI/Sources/Types/Internal/Live/AGENTS.md`
- `FirebaseAI/Sources/Types/Internal/Requests/AGENTS.md`
- `FirebaseAI/Sources/Types/Internal/Tools/AGENTS.md`
- `FirebaseAI/Sources/Types/Public/AGENTS.md`
- `FirebaseAI/Sources/Types/Public/Imagen/AGENTS.md`
- `FirebaseAI/Sources/Types/Public/Live/AGENTS.md`
- `FirebaseAI/Sources/Types/Public/Tools/AGENTS.md`

## What to add / change

This pull request significantly enhances the documentation of the FirebaseAI library by introducing a series of `AGENTS.md` files throughout its source code. This initiative aims to provide clear, structured explanations of the library's architecture, making it easier for developers to navigate, understand, and contribute to the codebase. By detailing the contents and purpose of various directories and files, especially distinguishing between public and internal components, the PR improves maintainability and onboarding for new contributors.

### Highlights

* **New Documentation Files**: Added multiple `AGENTS.md` files across the `FirebaseAI/Sources` directory to provide detailed overviews and documentation for the codebase structure.
* **Codebase Clarity**: Each `AGENTS.md` file describes the purpose of its respective directory, lists the Swift files contained within, and distinguishes between public and internal APIs for better understanding.
* **Structured Information**: The documentation categorizes protocols and data types, offering insights into error handling, Imagen features, live streaming capabilities, API requests, and tool-related functionalities.

#no-changelog

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
