# skill added for RNN android and iOS

Source: [wix/react-native-navigation#8238](https://github.com/wix/react-native-navigation/pull/8238)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/rnn-codebase/SKILL.md`
- `.cursor/skills/rnn-codebase/SKILL.md`
- `.github/skills/rnn-codebase/SKILL.md`

## What to add / change

The RNN skill gives the AI a mental map of the codebase so it doesn't have to discover the architecture from scratch every conversation. Specifically:

- Cross-layer lookup table — When the AI needs to fix something (e.g. "topbar title is cut off"), it can immediately look up that the relevant files are TopBarPresenter.mm on iOS, views/stack/topbar/ on Android, and Options.ts on JS — instead of spending 10 tool calls searching.
- Command flow — It knows the exact path a command takes from Navigation.push() in JS through the processing pipeline, across the TurboModule bridge, to RNNCommandsHandler (iOS) or Navigator (Android). Without this, the AI would trace it from scratch every time.
- Pattern awareness — It knows things like "iOS uses the Presenter pattern for applying options", "Android is View-based not Fragment-based", "overlays use separate UIWindows on iOS". These are the kinds of things that would otherwise lead to wrong assumptions.
- Options resolution order — It knows defaults → parent → component → mergeOptions. Without this it might look in the wrong place for why an option isn't applying.
- Gotchas — Things like passProps never crossing the bridge, lib/ being generated, splitView being iOS-only. Prevents common mistakes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
