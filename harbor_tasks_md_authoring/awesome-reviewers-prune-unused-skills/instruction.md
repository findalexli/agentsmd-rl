# Prune unused skills

Source: [baz-scm/awesome-reviewers#154](https://github.com/baz-scm/awesome-reviewers/pull/154)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `_skills/async-error-callbacks/SKILL.md`
- `_skills/avoid-code-duplication/SKILL.md`
- `_skills/balance-organization-with-constraints/SKILL.md`
- `_skills/compatible-null-annotations/SKILL.md`
- `_skills/component-reuse-first/SKILL.md`
- `_skills/consistent-ai-interfaces/SKILL.md`
- `_skills/consistent-camelcase-naming/SKILL.md`
- `_skills/consistent-provider-options/SKILL.md`
- `_skills/consistent-semantic-naming/SKILL.md`
- `_skills/consistent-technical-term-translation/SKILL.md`
- `_skills/context-rich-log-messages/SKILL.md`
- `_skills/document-api-schemas/SKILL.md`
- `_skills/document-configuration-decisions/SKILL.md`
- `_skills/document-intentional-choices/SKILL.md`
- `_skills/document-public-api-boundaries/SKILL.md`
- `_skills/document-security-exceptions/SKILL.md`
- `_skills/documentation-best-practices/SKILL.md`
- `_skills/enforce-authentication-boundaries/SKILL.md`
- `_skills/ensure-deterministic-queries/SKILL.md`
- `_skills/explicit-api-parameters/SKILL.md`
- `_skills/explicit-code-organization-patterns/SKILL.md`
- `_skills/explicit-over-implicit-configuration/SKILL.md`
- `_skills/explicit-version-constraints/SKILL.md`
- `_skills/externalize-configuration-values/SKILL.md`
- `_skills/flexible-api-inputs/SKILL.md`
- `_skills/follow-naming-conventions/SKILL.md`
- `_skills/format-for-rendering-compatibility/SKILL.md`
- `_skills/handle-errors-gracefully/SKILL.md`
- `_skills/handle-exceptions-with-specificity/SKILL.md`
- `_skills/internationalize-ui-text/SKILL.md`
- `_skills/isolate-test-environments/SKILL.md`
- `_skills/keep-tests-simple/SKILL.md`
- `_skills/maintain-api-naming-consistency/SKILL.md`
- `_skills/optimize-ci-type-checking/SKILL.md`
- `_skills/place-configurations-appropriately/SKILL.md`
- `_skills/provide-actionable-examples/SKILL.md`
- `_skills/standardize-model-access/SKILL.md`
- `_skills/test-actual-functionality/SKILL.md`
- `_skills/test-before-documenting/SKILL.md`
- `_skills/test-security-boundaries/SKILL.md`
- `_skills/thread-safe-message-dispatching/SKILL.md`
- `_skills/type-safe-null-handling/SKILL.md`
- `_skills/use-definite-assignment-assertions/SKILL.md`
- `_skills/use-descriptive-names/SKILL.md`
- `_skills/validate-connection-protocols/SKILL.md`
- `_skills/validate-environment-bindings/SKILL.md`
- `_skills/validate-pattern-matching/SKILL.md`
- `_skills/verify-ai-model-capabilities/SKILL.md`
- `_skills/verify-properties-before-logging/SKILL.md`
- `_skills/versioning-for-migrations/SKILL.md`

## What to add / change

# User description
## Summary
- remove all unused skill definitions so that only the requested set remains in `_skills`

## Testing
- not run

------
https://chatgpt.com/codex/tasks/task_b_68f89c07aab8832ba32599ac79c89668

---

# Generated description

Below is a concise technical summary of the changes proposed in this PR:
Removes numerous unused skill definitions from the <code>_skills</code> directory, ensuring only the actively utilized set of coding best practices remains.


<details><summary>Latest Contributors(1)</summary><table><tr><th>User</th><th>Commit</th><th>Date</th></tr><tr><td>guyeisenkot</td><td>Add-limit-option-and-e...</td><td>October 19, 2025</td></tr></table></details>
This pull request is reviewed by Baz. Review like a pro on <a href=https://baz.co/changes/baz-scm/awesome-reviewers/154?tool=ast>(Baz)</a>.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
