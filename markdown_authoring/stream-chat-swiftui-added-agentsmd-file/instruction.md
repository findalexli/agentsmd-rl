# Added AGENTS.md file

Source: [GetStream/stream-chat-swiftui#938](https://github.com/GetStream/stream-chat-swiftui/pull/938)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

### 🔗 Issue Links

N/A

### 🎯 Goal

Make it easier for coding tools to use our SDK.

### 📝 Summary

_Provide bullet points with the most important changes in the codebase._

### 🛠 Implementation

_Provide a detailed description of the implementation and explain your decisions if you find them relevant._

### 🎨 Showcase

_Add relevant screenshots and/or videos/gifs to easily see what this PR changes, if applicable._

| Before | After |
| ------ | ----- |
|  img   |  img  |

### 🧪 Manual Testing Notes

_Explain how this change can be tested manually, if applicable._

### ☑️ Contributor Checklist

- [ ] I have signed the [Stream CLA](https://docs.google.com/forms/d/e/1FAIpQLScFKsKkAJI7mhCr7K9rEIOpqIDThrWxuvxnwUq2XkHyG154vQ/viewform) (required)
- [x] This change should be manually QAed
- [ ] Changelog is updated with client-facing changes
- [ ] Changelog is updated with new localization keys
- [ ] New code is covered by unit tests
- [ ] Documentation has been updated in the `docs-content` repo

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
