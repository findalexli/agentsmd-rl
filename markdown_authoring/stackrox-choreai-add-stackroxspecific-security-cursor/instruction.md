# chore(AI): Add stackrox-specific security cursor rules

Source: [stackrox/stackrox#17528](https://github.com/stackrox/stackrox/pull/17528)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/README.md`
- `.cursor/rules/security/common.mdc`
- `.cursor/rules/security/containers.mdc`
- `.cursor/rules/security/databases.mdc`
- `.cursor/rules/security/groovy.mdc`
- `.cursor/rules/security/helm.mdc`
- `.cursor/rules/security/java.mdc`
- `.cursor/rules/security/javascript.mdc`
- `.cursor/rules/security/product-security/security_rules.mdc`
- `.cursor/rules/security/product-security/technology/containers.mdc`
- `.cursor/rules/security/product-security/technology/databases.mdc`
- `.cursor/rules/security/product-security/technology/go.mdc`
- `.cursor/rules/security/product-security/technology/helm.mdc`
- `.cursor/rules/security/product-security/technology/kafka.mdc`
- `.cursor/rules/security/product-security/technology/llm.mdc`
- `.cursor/rules/security/product-security/technology/mcp.mdc`
- `.cursor/rules/security/product-security/technology/operators.mdc`
- `.cursor/rules/security/product-security/technology/python.mdc`
- `.cursor/rules/security/product-security/technology/react.mdc`
- `.cursor/rules/security/product-security/technology/rust.mdc`
- `.cursor/rules/security/shell.mdc`
- `.cursor/rules/security/typescript.mdc`

## What to add / change

## Description

This is a follow-up to [#16213 Add security cursor rules](https://github.com/stackrox/stackrox/pull/16213). While that PR added a verbatim copy of [Product Security's Cursor Rules](https://gitlab.cee.redhat.com/product-security/security-cursor-rules), those don't fully cover Stackrox's use cases.

Here we add rules:

- For other languages we use, e.g. Groovy, Java, Typescript
- For languages already covered by Product Security's rules, but having different patterns for matching the files to which they apply. For example, the existing rules for containers would not get matched against `konflux.bundle.Dockerfile`, so we added [containers.mdc](https://github.com/stackrox/stackrox/pull/17528/files#diff-6da2fe685274d9d155e12baa89327ec7ed3fd9e7159d54e758d1065a09614638) where the regex is `**/*Dockerfile*`

### AI involvement

The new rules are either copied from those made by Product Security or written by Claude Sonnet 4.5. I have reviewed them and made some adjustments but I'm not an expert in many of those areas so a detailed review is appreciated.

## User-facing documentation

- [x] [CHANGELOG.md](https://github.com/stackrox/stackrox/blob/master/CHANGELOG.md) is updated **OR** update is not needed
- [x] [documentation PR](https://spaces.redhat.com/display/StackRox/Submitting+a+User+Documentation+Pull+Request) is created and is linked above **OR** is not needed

## Testing and quality

- [x] the change is production ready: the change is [GA](

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
