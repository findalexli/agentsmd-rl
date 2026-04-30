# doc(global): add Cursor rules

Source: [Consensys/linea-attestation-registry#1031](https://github.com/Consensys/linea-attestation-registry/pull/1031)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/00-operating-model.mdc`
- `.cursor/rules/01-principles.mdc`
- `.cursor/rules/02-reliability.mdc`
- `.cursor/rules/05-security.mdc`
- `.cursor/rules/10-solidity.mdc`
- `.cursor/rules/12-foundry.mdc`
- `.cursor/rules/20-wagmi-viem.mdc`
- `.cursor/rules/30-next-react.mdc`
- `.cursor/rules/35-typescript.mdc`
- `.cursor/rules/40-nestjs.mdc`
- `.cursor/rules/42-prisma.mdc`
- `.cursor/rules/45-data-layer.mdc`
- `.cursor/rules/50-testing-ci.mdc`
- `.cursor/rules/55-comments-docs.mdc`
- `.cursor/rules/60-web3-product.mdc`
- `.cursor/rules/65-release-rollout.mdc`
- `.cursor/rules/70-observability-ops.mdc`
- `.cursor/rules/80-accessibility-performance.mdc`
- `.cursor/rules/90-monorepo.mdc`
- `.cursor/rules/92-docker.mdc`
- `.cursor/rules/95-github-actions.mdc`
- `.cursor/rules/99-meta.mdc`

## What to add / change

## What does this PR do?

Adds Cursor AI rules

### Type of change

- [ ] Chore
- [ ] Bug fix
- [ ] New feature
- [X] Documentation update

## Check list

- [ ] My&nbsp;contribution&nbsp;follows&nbsp;the&nbsp;project's&nbsp;[guidelines](https://github.com/Consensys/linea-attestation-registry/blob/dev/CONTRIBUTING.md)
- [ ] I have made corresponding changes to the documentation
- [ ] Unit tests for any smart contract change
- [ ] Contracts and functions are documented

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Documentation-only change that adds editor/AI guidance files; no runtime code, dependencies, or deployment behavior is modified.
> 
> **Overview**
> Adds a new `.cursor/rules/` rule set to govern how Cursor is used in this repo, including an operating model (Planner/Executor/Reviewer), strict Definition of Done, and exception/ownership policies.
> 
> Also introduces cross-cutting and stack-specific guidance for **security**, **reliability/idempotency**, **testing/CI**, and conventions for Solidity/Foundry, wagmi/viem, Next.js/React, TypeScript, NestJS, Prisma, monorepo (pnpm), Docker, and GitHub Actions, plus meta-governance for maintaining these rules.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit 5c7433c67c408fc7396f23b16c07238da2e494a1. Bugbot is set up for automated code reviews on this repo. Configure [here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
