# fix(cli): Use standard A2A protocol structure in fetch & update SKILL.md docs

Source: [EvoMap/evolver#280](https://github.com/EvoMap/evolver/pull/280)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

1. CLI fetch payload structure: Replaced the hardcoded { sender_id } with the standard gep-a2a protocol envelope and properly invokes captureEnvFingerprint() in index.js. This prevents 500 errors caused by missing env_fingerprint.client_version on the Hub.
2. Documentation ([SKILL.md](http://skill.md/)): Added a clear AI Agent Usage Tip to explicitly advise other agents not to construct raw HTTP payloads for /a2a/* endpoints, pointing them instead to the native wrappers in src/gep/*.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
