# fix(skills): align Datadog skills with current pup CLI commands

Source: [datadog-labs/pup#428](https://github.com/datadog-labs/pup/pull/428)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/dd-code-generation/SKILL.md`
- `skills/dd-logs/SKILL.md`
- `skills/dd-monitors/SKILL.md`
- `skills/dd-pup/SKILL.md`

## What to add / change

## What does this PR do?
This PR updates multiple Datadog skill documents so agents use commands and flags that are currently supported by the `pup` CLI.

Several skill examples had drifted from the real CLI surface (deprecated flags, renamed command groups, or examples for subcommands not currently exposed). This change aligns those examples to reduce agent command failures and retries.

<!-- A brief description of the change being made with this pull request. -->

## What Changed
- Updated `skills/dd-monitors/SKILL.md`:
  - Replaced `pup monitors list --status "Alert"` with `pup monitors search --query "status:Alert"`.
  - Removed `--json` usage from monitor examples.
  - Updated create/mute/unmute/downtime examples to supported file/update-based command patterns currently used in docs.
- Updated `skills/dd-logs/SKILL.md`:
  - Removed `--json` flag usage where JSON is already default.
  - Replaced `pup logs pipelines ...` with `pup obs-pipelines ...`.
  - Removed unsupported `logs rehydrate create` and `logs metrics create` examples; kept only exposed commands.
- Updated `skills/dd-code-generation/SKILL.md`:
  - Replaced `--tag` with `--tags` in monitor list examples.
- Updated `skills/dd-pup/SKILL.md`:
  - Added required `--query` in generic `security signals list` example.
  - Replaced ambiguous `--count` usage with `--count 100` for infrastructure hosts list.

## Additional Notes
This PR is documentation-only and focused on CLI compatibility for sk

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
