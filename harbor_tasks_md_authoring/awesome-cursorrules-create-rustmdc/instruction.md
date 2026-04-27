# Create rust.mdc

Source: [PatrickJS/awesome-cursorrules#129](https://github.com/PatrickJS/awesome-cursorrules/pull/129)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `rules-new/rust.mdc`

## What to add / change

This PR adds a .cursorrules config for Rust-based Solana smart contract development using the Anchor framework.

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added a comprehensive "Rust + Solana (Anchor) Best Practices" guide covering program structure, Anchor usage, manual Solana SDK patterns, serialization, testing, security, performance, developer workflow, documentation standards, wallet/network handling, and CI/CD/deployment recommendations.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
