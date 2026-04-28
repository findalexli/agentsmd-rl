# Add Copilot coding agent instructions

Source: [pakerwreah/Calendr#592](https://github.com/pakerwreah/Calendr/pull/592)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

GitHub Copilot coding agent has no repository-specific context, leading to inconsistent code suggestions that may not align with project conventions.

Adds `.github/copilot-instructions.md` covering:

- **Architecture** – MVVM + RxSwift, roles of Models / ViewModels / Providers / Mocks, DI via initializer
- **Coding conventions** – Subject types, `DisposeBag` usage, `Strings.*` constants (swiftgen), factory helpers in tests
- **Build & test commands** – Exact `xcodebuild` invocations matching CI
- **Testing patterns** – `HistoricalScheduler`, mock provider `m_*` properties, `lazy var viewModel` setup
- **File layout** – Annotated folder tree for `Calendr/` and `CalendrTests/`
- **Localization workflow** – Adding strings and regenerating `Strings.generated.swift`
- **Platform constraints** – macOS 14+ requirement, code-signing disabled in CI, entitlements caution

<!-- START COPILOT CODING AGENT TIPS -->
---

✨ Let Copilot coding agent [set things up for you](https://github.com/pakerwreah/Calendr/issues/new?title=✨+Set+up+Copilot+instructions&body=Configure%20instructions%20for%20this%20repository%20as%20documented%20in%20%5BBest%20practices%20for%20Copilot%20coding%20agent%20in%20your%20repository%5D%28https://gh.io/copilot-coding-agent-tips%29%2E%0A%0A%3COnboard%20this%20repo%3E&assignees=copilot) — coding agent works faster and does higher quality work when set up for your repo.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
