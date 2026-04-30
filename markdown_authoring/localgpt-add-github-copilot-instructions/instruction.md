# Add GitHub Copilot instructions

Source: [localgpt-app/localgpt#41](https://github.com/localgpt-app/localgpt/pull/41)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds `.github/copilot-instructions.md` to provide Copilot with repository-specific guidance.

## Coverage

- **Architecture**: 6-crate workspace structure, dependency graph, feature flags
- **Critical constraints**: `localgpt-core` must compile for iOS/Android (zero platform-specific deps)
- **Design patterns**: Tool safety split, thread safety (Agent not `Send+Sync`), Bevy main thread requirements
- **Commands**: Build, test, lint, cross-compile checks
- **Security**: Sandbox rules, protected files, prompt injection defenses
- **Common tasks**: Adding tools/providers/commands, mobile changes workflow
- **Validation**: Pre-PR checklist including cross-compilation verification

Based on existing `CLAUDE.md` but adapted for Copilot's format per GitHub best practices.

> [!WARNING]
>
> <details>
> <summary>Firewall rules blocked me from connecting to one or more addresses (expand for details)</summary>
>
> #### I tried to connect to the following addresses, but was blocked by firewall rules:
>
> - `gh.io`
>   - Triggering command: `/home/REDACTED/work/_temp/ghcca-node/node/bin/node /home/REDACTED/work/_temp/ghcca-node/node/bin/node --enable-source-maps /home/REDACTED/work/_temp/copilot-developer-action-main/dist/index.js` (dns block)
>
> If you need me to access, download, or install something from one of these locations, you can either:
>
> - Configure [Actions setup steps](https://gh.io/copilot/actions-setup-steps) to set up my environment, which run before the firewall is ena

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
