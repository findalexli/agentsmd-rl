# Expo Cursor Rules: Update navigation guideline to use Expo Router

Source: [PatrickJS/awesome-cursorrules#141](https://github.com/PatrickJS/awesome-cursorrules/pull/141)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `rules/react-native-expo-cursorrules-prompt-file/.cursorrules`

## What to add / change

Expo Router is preferred over React Navigation as of SDK 52.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
