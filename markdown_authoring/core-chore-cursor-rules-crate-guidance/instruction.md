# chore: cursor rules crate guidance

Source: [calimero-network/core#1808](https://github.com/calimero-network/core/pull/1808)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`

## What to add / change

# docs: Improve Cursor rules with crate-specific guidance

## Description

This PR enhances the `.cursorrules` file by adding comprehensive crate-specific guidance. The existing rules lacked detailed context, which made it challenging for AI assistants to effectively navigate the codebase.

This change addresses the bounty "Improve Cursor rules with crate-specific guidance" by providing:
*   Descriptions of key crate purposes and entry points for both binary and library crates.
*   Common debugging workflows for various components (node, storage, WASM, network).
*   Detailed test commands and instructions for building WASM applications and running local nodes.
*   An overview of key architectural concepts, including data flow, core concepts (Context, CRDTs, DAG, Gossipsub), request lifecycle, and storage architecture.

This update aims to significantly improve the AI assistant's ability to understand and interact with the repository.

## Test plan

No functional code changes were made. The verification process involves reviewing the updated `.cursorrules` file for accuracy, clarity, and completeness of the added documentation.

To reproduce:
1.  Open the `.cursorrules` file.
2.  Review the newly added sections for crate purposes, entry points, testing commands, debugging workflows, and architectural concepts.
3.  Confirm that the information is accurate and provides useful context for an AI assistant.

No end-to-end tests or UI changes are applicable.

## Documentation update

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
