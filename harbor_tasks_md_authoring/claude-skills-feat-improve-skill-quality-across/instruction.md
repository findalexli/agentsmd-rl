# feat: improve skill quality across 65 skills

Source: [Jeffallan/claude-skills#172](https://github.com/Jeffallan/claude-skills/pull/172)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/angular-architect/SKILL.md`
- `skills/api-designer/SKILL.md`
- `skills/architecture-designer/SKILL.md`
- `skills/atlassian-mcp/SKILL.md`
- `skills/chaos-engineer/SKILL.md`
- `skills/cli-developer/SKILL.md`
- `skills/cloud-architect/SKILL.md`
- `skills/code-documenter/SKILL.md`
- `skills/code-reviewer/SKILL.md`
- `skills/cpp-pro/SKILL.md`
- `skills/csharp-developer/SKILL.md`
- `skills/database-optimizer/SKILL.md`
- `skills/debugging-wizard/SKILL.md`
- `skills/devops-engineer/SKILL.md`
- `skills/django-expert/SKILL.md`
- `skills/dotnet-core-expert/SKILL.md`
- `skills/embedded-systems/SKILL.md`
- `skills/fastapi-expert/SKILL.md`
- `skills/feature-forge/SKILL.md`
- `skills/fine-tuning-expert/SKILL.md`
- `skills/flutter-expert/SKILL.md`
- `skills/fullstack-guardian/SKILL.md`
- `skills/game-developer/SKILL.md`
- `skills/golang-pro/SKILL.md`
- `skills/graphql-architect/SKILL.md`
- `skills/java-architect/SKILL.md`
- `skills/javascript-pro/SKILL.md`
- `skills/kotlin-specialist/SKILL.md`
- `skills/kubernetes-specialist/SKILL.md`
- `skills/laravel-specialist/SKILL.md`
- `skills/legacy-modernizer/SKILL.md`
- `skills/mcp-developer/SKILL.md`
- `skills/microservices-architect/SKILL.md`
- `skills/ml-pipeline/SKILL.md`
- `skills/monitoring-expert/SKILL.md`
- `skills/nestjs-expert/SKILL.md`
- `skills/nextjs-developer/SKILL.md`
- `skills/pandas-pro/SKILL.md`
- `skills/php-pro/SKILL.md`
- `skills/playwright-expert/SKILL.md`
- `skills/postgres-pro/SKILL.md`
- `skills/prompt-engineer/SKILL.md`
- `skills/python-pro/SKILL.md`
- `skills/rag-architect/SKILL.md`
- `skills/rails-expert/SKILL.md`
- `skills/react-expert/SKILL.md`
- `skills/react-native-expert/SKILL.md`
- `skills/rust-engineer/SKILL.md`
- `skills/salesforce-developer/SKILL.md`
- `skills/secure-code-guardian/SKILL.md`
- `skills/security-reviewer/SKILL.md`
- `skills/shopify-expert/SKILL.md`
- `skills/spark-engineer/SKILL.md`
- `skills/spec-miner/SKILL.md`
- `skills/spring-boot-engineer/SKILL.md`
- `skills/sql-pro/SKILL.md`
- `skills/sre-engineer/SKILL.md`
- `skills/swift-expert/SKILL.md`
- `skills/terraform-engineer/SKILL.md`
- `skills/test-master/SKILL.md`
- `skills/typescript-pro/SKILL.md`
- `skills/vue-expert-js/SKILL.md`
- `skills/vue-expert/SKILL.md`
- `skills/websocket-engineer/SKILL.md`
- `skills/wordpress-pro/SKILL.md`

## What to add / change

Hullo @Jeffallan 👋

I ran your skills through `tessl skill review` at work and found some targeted improvements. This follows Anthropic's best practices.

<details><summary>A pretty (enormous) score card</summary>

<img width="720" alt="score_card" src="https://github.com/user-attachments/assets/3bee74d0-db84-40f4-b76a-2c1c83a37746" />

</details>

Here's the before/after in text form:

| Skill | Before | After | Change |
|-------|--------|-------|--------|
| ml-pipeline | 45% | 100% | +55% |
| rag-architect | 49% | 100% | +51% |
| test-master | 52% | 100% | +48% |
| javascript-pro | 54% | 100% | +46% |
| legacy-modernizer | 54% | 100% | +46% |
| fine-tuning-expert | 55% | 100% | +45% |
| wordpress-pro | 56% | 100% | +44% |
| angular-architect | 57% | 100% | +43% |
| atlassian-mcp | 57% | 100% | +43% |
| chaos-engineer | 57% | 100% | +43% |
| cloud-architect | 57% | 100% | +43% |
| kotlin-specialist | 57% | 100% | +43% |
| microservices-architect | 57% | 100% | +43% |
| monitoring-expert | 57% | 100% | +43% |
| react-native-expert | 57% | 100% | +43% |
| rust-engineer | 57% | 100% | +43% |
| salesforce-developer | 57% | 100% | +43% |
| spring-boot-engineer | 57% | 100% | +43% |
| sre-engineer | 57% | 100% | +43% |
| swift-expert | 57% | 100% | +43% |
| typescript-pro | 57% | 100% | +43% |
| vue-expert-js | 57% | 100% | +43% |
| code-reviewer | 61% | 100% | +39% |
| prompt-engineer | 61% | 100% | +39% |
| fullstack-guardian | 62% | 100% | 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
