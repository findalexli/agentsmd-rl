# closing agents metadata section

Source: [avivl/claude-007-agents#5](https://github.com/avivl/claude-007-agents/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/ai-analysis/error-detective.md`
- `.claude/agents/ai-analysis/graphql-architect.md`
- `.claude/agents/ai-analysis/prompt-engineer.md`
- `.claude/agents/ai/machine-learning-engineer.md`
- `.claude/agents/ai/nlp-llm-integration-expert.md`
- `.claude/agents/automation/cicd-pipeline-engineer.md`
- `.claude/agents/automation/qa-automation-engineer.md`
- `.claude/agents/automation/release-manager.md`
- `.claude/agents/backend/go-resilience-engineer.md`
- `.claude/agents/backend/go-zap-logging.md`
- `.claude/agents/backend/resilience-engineer.md`
- `.claude/agents/backend/typescript-cockatiel-resilience.md`
- `.claude/agents/backend/typescript-pino-logging.md`
- `.claude/agents/business/business-analyst.md`
- `.claude/agents/business/healthcare-compliance-agent.md`
- `.claude/agents/business/payment-integration-agent.md`
- `.claude/agents/business/product-manager.md`
- `.claude/agents/choreography/bug-hunting-tango.md`
- `.claude/agents/choreography/code-review-waltz.md`
- `.claude/agents/choreography/feature-development-dance.md`
- `.claude/agents/creative/code-archaeologist-time-traveler.md`
- `.claude/agents/creative/rubber-duck-debugger.md`
- `.claude/agents/creative/technical-debt-collector.md`
- `.claude/agents/data/analytics-implementation-specialist.md`
- `.claude/agents/data/business-intelligence-developer.md`
- `.claude/agents/data/data-engineer.md`
- `.claude/agents/frontend/design-system-architect.md`
- `.claude/agents/frontend/micro-frontend-architect.md`
- `.claude/agents/frontend/mobile-developer.md`
- `.claude/agents/frontend/pwa-specialist.md`
- `.claude/agents/frontend/webassembly-specialist.md`
- `.claude/agents/infrastructure/cloud-architect.md`
- `.claude/agents/infrastructure/database-admin.md`
- `.claude/agents/infrastructure/devops-troubleshooter.md`
- `.claude/agents/infrastructure/incident-responder.md`
- `.claude/agents/infrastructure/network-engineer.md`
- `.claude/agents/infrastructure/observability-engineer.md`
- `.claude/agents/infrastructure/pulumi-typescript-specialist.md`
- `.claude/agents/infrastructure/serverless-architect.md`
- `.claude/agents/infrastructure/site-reliability-engineer.md`
- `.claude/agents/infrastructure/terraform-specialist.md`
- `.claude/agents/orchestration/learning-system.md`
- `.claude/agents/performance-optimizers/session-optimizer.md`
- `.claude/agents/performance-optimizers/tool-batch-optimizer.md`
- `.claude/agents/personalities/agent-evolution-system.md`
- `.claude/agents/safety-specialists/agent-environment-simulator.md`
- `.claude/agents/safety-specialists/permission-escalator.md`
- `.claude/agents/security/devsecops-engineer.md`
- `.claude/agents/security/privacy-engineer.md`
- `.claude/agents/universal/git-expert.md`
- `.claude/agents/universal/logging-concepts-engineer.md`
- `.claude/agents/universal/resilience-engineer.md`

## What to add / change

Fixed all the rest.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
