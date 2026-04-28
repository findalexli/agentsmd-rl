# [AI] AGENTS.md update

Source: [firebase/firebase-ios-sdk#15874](https://github.com/firebase/firebase-ios-sdk/pull/15874)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `FirebaseAI/Sources/AGENTS.md`
- `FirebaseAI/Sources/Extensions/Internal/AGENTS.md`

## What to add / change

Update AGENTS.md file for #15872 by the following two prompts:

* Update the AGENTS.md files in the FirebaseAI/Sources directory tree  based on the changes introduced in ah/ai-generative-model-session branch
* There should be a new AGENTS.md added for the new GenerationSchema+Gemini.swift file

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
