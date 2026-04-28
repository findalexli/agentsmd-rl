"""Behavioral checks for claude-007-agents-closing-agents-metadata-section (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-007-agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/ai-analysis/error-detective.md')
    assert '.claude/agents/ai-analysis/error-detective.md' in text, "expected to find: " + '.claude/agents/ai-analysis/error-detective.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/ai-analysis/graphql-architect.md')
    assert '.claude/agents/ai-analysis/graphql-architect.md' in text, "expected to find: " + '.claude/agents/ai-analysis/graphql-architect.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/ai-analysis/prompt-engineer.md')
    assert '.claude/agents/ai-analysis/prompt-engineer.md' in text, "expected to find: " + '.claude/agents/ai-analysis/prompt-engineer.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/ai/machine-learning-engineer.md')
    assert '.claude/agents/ai/machine-learning-engineer.md' in text, "expected to find: " + '.claude/agents/ai/machine-learning-engineer.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/ai/nlp-llm-integration-expert.md')
    assert '.claude/agents/ai/nlp-llm-integration-expert.md' in text, "expected to find: " + '.claude/agents/ai/nlp-llm-integration-expert.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/automation/cicd-pipeline-engineer.md')
    assert '# CI/CD Pipeline Engineer Agent' in text, "expected to find: " + '# CI/CD Pipeline Engineer Agent'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/automation/qa-automation-engineer.md')
    assert '# QA Automation Engineer Agent' in text, "expected to find: " + '# QA Automation Engineer Agent'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/automation/release-manager.md')
    assert '.claude/agents/automation/release-manager.md' in text, "expected to find: " + '.claude/agents/automation/release-manager.md'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/backend/go-resilience-engineer.md')
    assert '.claude/agents/backend/go-resilience-engineer.md' in text, "expected to find: " + '.claude/agents/backend/go-resilience-engineer.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/backend/go-zap-logging.md')
    assert '.claude/agents/backend/go-zap-logging.md' in text, "expected to find: " + '.claude/agents/backend/go-zap-logging.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/backend/resilience-engineer.md')
    assert '.claude/agents/backend/resilience-engineer.md' in text, "expected to find: " + '.claude/agents/backend/resilience-engineer.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/backend/typescript-cockatiel-resilience.md')
    assert '.claude/agents/backend/typescript-cockatiel-resilience.md' in text, "expected to find: " + '.claude/agents/backend/typescript-cockatiel-resilience.md'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/backend/typescript-pino-logging.md')
    assert '.claude/agents/backend/typescript-pino-logging.md' in text, "expected to find: " + '.claude/agents/backend/typescript-pino-logging.md'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/business/business-analyst.md')
    assert '# Business Analyst Agent' in text, "expected to find: " + '# Business Analyst Agent'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/business/healthcare-compliance-agent.md')
    assert '.claude/agents/business/healthcare-compliance-agent.md' in text, "expected to find: " + '.claude/agents/business/healthcare-compliance-agent.md'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/business/payment-integration-agent.md')
    assert '.claude/agents/business/payment-integration-agent.md' in text, "expected to find: " + '.claude/agents/business/payment-integration-agent.md'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/business/product-manager.md')
    assert '# Product Manager Agent' in text, "expected to find: " + '# Product Manager Agent'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/choreography/bug-hunting-tango.md')
    assert '.claude/agents/choreography/bug-hunting-tango.md' in text, "expected to find: " + '.claude/agents/choreography/bug-hunting-tango.md'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/choreography/code-review-waltz.md')
    assert '.claude/agents/choreography/code-review-waltz.md' in text, "expected to find: " + '.claude/agents/choreography/code-review-waltz.md'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/choreography/feature-development-dance.md')
    assert '.claude/agents/choreography/feature-development-dance.md' in text, "expected to find: " + '.claude/agents/choreography/feature-development-dance.md'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/creative/code-archaeologist-time-traveler.md')
    assert '.claude/agents/creative/code-archaeologist-time-traveler.md' in text, "expected to find: " + '.claude/agents/creative/code-archaeologist-time-traveler.md'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/creative/rubber-duck-debugger.md')
    assert '.claude/agents/creative/rubber-duck-debugger.md' in text, "expected to find: " + '.claude/agents/creative/rubber-duck-debugger.md'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/creative/technical-debt-collector.md')
    assert '.claude/agents/creative/technical-debt-collector.md' in text, "expected to find: " + '.claude/agents/creative/technical-debt-collector.md'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/data/analytics-implementation-specialist.md')
    assert '.claude/agents/data/analytics-implementation-specialist.md' in text, "expected to find: " + '.claude/agents/data/analytics-implementation-specialist.md'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/data/business-intelligence-developer.md')
    assert '.claude/agents/data/business-intelligence-developer.md' in text, "expected to find: " + '.claude/agents/data/business-intelligence-developer.md'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/data/data-engineer.md')
    assert '.claude/agents/data/data-engineer.md' in text, "expected to find: " + '.claude/agents/data/data-engineer.md'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/frontend/design-system-architect.md')
    assert '.claude/agents/frontend/design-system-architect.md' in text, "expected to find: " + '.claude/agents/frontend/design-system-architect.md'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/frontend/micro-frontend-architect.md')
    assert '.claude/agents/frontend/micro-frontend-architect.md' in text, "expected to find: " + '.claude/agents/frontend/micro-frontend-architect.md'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/frontend/mobile-developer.md')
    assert '# Mobile Developer Agent' in text, "expected to find: " + '# Mobile Developer Agent'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/frontend/pwa-specialist.md')
    assert '.claude/agents/frontend/pwa-specialist.md' in text, "expected to find: " + '.claude/agents/frontend/pwa-specialist.md'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/frontend/webassembly-specialist.md')
    assert '.claude/agents/frontend/webassembly-specialist.md' in text, "expected to find: " + '.claude/agents/frontend/webassembly-specialist.md'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/infrastructure/cloud-architect.md')
    assert '# Cloud Architect Agent' in text, "expected to find: " + '# Cloud Architect Agent'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/infrastructure/database-admin.md')
    assert '# Database Administrator Agent' in text, "expected to find: " + '# Database Administrator Agent'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/infrastructure/devops-troubleshooter.md')
    assert '.claude/agents/infrastructure/devops-troubleshooter.md' in text, "expected to find: " + '.claude/agents/infrastructure/devops-troubleshooter.md'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/infrastructure/incident-responder.md')
    assert '# Incident Responder Agent' in text, "expected to find: " + '# Incident Responder Agent'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/infrastructure/network-engineer.md')
    assert '.claude/agents/infrastructure/network-engineer.md' in text, "expected to find: " + '.claude/agents/infrastructure/network-engineer.md'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/infrastructure/observability-engineer.md')
    assert '.claude/agents/infrastructure/observability-engineer.md' in text, "expected to find: " + '.claude/agents/infrastructure/observability-engineer.md'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/infrastructure/pulumi-typescript-specialist.md')
    assert '.claude/agents/infrastructure/pulumi-typescript-specialist.md' in text, "expected to find: " + '.claude/agents/infrastructure/pulumi-typescript-specialist.md'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/infrastructure/serverless-architect.md')
    assert '.claude/agents/infrastructure/serverless-architect.md' in text, "expected to find: " + '.claude/agents/infrastructure/serverless-architect.md'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/infrastructure/site-reliability-engineer.md')
    assert '# Site Reliability Engineer (SRE) Agent' in text, "expected to find: " + '# Site Reliability Engineer (SRE) Agent'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/infrastructure/terraform-specialist.md')
    assert '.claude/agents/infrastructure/terraform-specialist.md' in text, "expected to find: " + '.claude/agents/infrastructure/terraform-specialist.md'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/orchestration/learning-system.md')
    assert '.claude/agents/orchestration/learning-system.md' in text, "expected to find: " + '.claude/agents/orchestration/learning-system.md'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/performance-optimizers/session-optimizer.md')
    assert '.claude/agents/performance-optimizers/session-optimizer.md' in text, "expected to find: " + '.claude/agents/performance-optimizers/session-optimizer.md'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/performance-optimizers/tool-batch-optimizer.md')
    assert '.claude/agents/performance-optimizers/tool-batch-optimizer.md' in text, "expected to find: " + '.claude/agents/performance-optimizers/tool-batch-optimizer.md'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/personalities/agent-evolution-system.md')
    assert '.claude/agents/personalities/agent-evolution-system.md' in text, "expected to find: " + '.claude/agents/personalities/agent-evolution-system.md'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/safety-specialists/agent-environment-simulator.md')
    assert '.claude/agents/safety-specialists/agent-environment-simulator.md' in text, "expected to find: " + '.claude/agents/safety-specialists/agent-environment-simulator.md'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/safety-specialists/permission-escalator.md')
    assert '.claude/agents/safety-specialists/permission-escalator.md' in text, "expected to find: " + '.claude/agents/safety-specialists/permission-escalator.md'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/security/devsecops-engineer.md')
    assert '.claude/agents/security/devsecops-engineer.md' in text, "expected to find: " + '.claude/agents/security/devsecops-engineer.md'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/security/privacy-engineer.md')
    assert '.claude/agents/security/privacy-engineer.md' in text, "expected to find: " + '.claude/agents/security/privacy-engineer.md'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/universal/git-expert.md')
    assert '.claude/agents/universal/git-expert.md' in text, "expected to find: " + '.claude/agents/universal/git-expert.md'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/universal/logging-concepts-engineer.md')
    assert '.claude/agents/universal/logging-concepts-engineer.md' in text, "expected to find: " + '.claude/agents/universal/logging-concepts-engineer.md'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/universal/resilience-engineer.md')
    assert '.claude/agents/universal/resilience-engineer.md' in text, "expected to find: " + '.claude/agents/universal/resilience-engineer.md'[:80]

