#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-007-agents

# Idempotency guard
if grep -qF ".claude/agents/ai-analysis/error-detective.md" ".claude/agents/ai-analysis/error-detective.md" && grep -qF ".claude/agents/ai-analysis/graphql-architect.md" ".claude/agents/ai-analysis/graphql-architect.md" && grep -qF ".claude/agents/ai-analysis/prompt-engineer.md" ".claude/agents/ai-analysis/prompt-engineer.md" && grep -qF ".claude/agents/ai/machine-learning-engineer.md" ".claude/agents/ai/machine-learning-engineer.md" && grep -qF ".claude/agents/ai/nlp-llm-integration-expert.md" ".claude/agents/ai/nlp-llm-integration-expert.md" && grep -qF "# CI/CD Pipeline Engineer Agent" ".claude/agents/automation/cicd-pipeline-engineer.md" && grep -qF "# QA Automation Engineer Agent" ".claude/agents/automation/qa-automation-engineer.md" && grep -qF ".claude/agents/automation/release-manager.md" ".claude/agents/automation/release-manager.md" && grep -qF ".claude/agents/backend/go-resilience-engineer.md" ".claude/agents/backend/go-resilience-engineer.md" && grep -qF ".claude/agents/backend/go-zap-logging.md" ".claude/agents/backend/go-zap-logging.md" && grep -qF ".claude/agents/backend/resilience-engineer.md" ".claude/agents/backend/resilience-engineer.md" && grep -qF ".claude/agents/backend/typescript-cockatiel-resilience.md" ".claude/agents/backend/typescript-cockatiel-resilience.md" && grep -qF ".claude/agents/backend/typescript-pino-logging.md" ".claude/agents/backend/typescript-pino-logging.md" && grep -qF "# Business Analyst Agent" ".claude/agents/business/business-analyst.md" && grep -qF ".claude/agents/business/healthcare-compliance-agent.md" ".claude/agents/business/healthcare-compliance-agent.md" && grep -qF ".claude/agents/business/payment-integration-agent.md" ".claude/agents/business/payment-integration-agent.md" && grep -qF "# Product Manager Agent" ".claude/agents/business/product-manager.md" && grep -qF ".claude/agents/choreography/bug-hunting-tango.md" ".claude/agents/choreography/bug-hunting-tango.md" && grep -qF ".claude/agents/choreography/code-review-waltz.md" ".claude/agents/choreography/code-review-waltz.md" && grep -qF ".claude/agents/choreography/feature-development-dance.md" ".claude/agents/choreography/feature-development-dance.md" && grep -qF ".claude/agents/creative/code-archaeologist-time-traveler.md" ".claude/agents/creative/code-archaeologist-time-traveler.md" && grep -qF ".claude/agents/creative/rubber-duck-debugger.md" ".claude/agents/creative/rubber-duck-debugger.md" && grep -qF ".claude/agents/creative/technical-debt-collector.md" ".claude/agents/creative/technical-debt-collector.md" && grep -qF ".claude/agents/data/analytics-implementation-specialist.md" ".claude/agents/data/analytics-implementation-specialist.md" && grep -qF ".claude/agents/data/business-intelligence-developer.md" ".claude/agents/data/business-intelligence-developer.md" && grep -qF ".claude/agents/data/data-engineer.md" ".claude/agents/data/data-engineer.md" && grep -qF ".claude/agents/frontend/design-system-architect.md" ".claude/agents/frontend/design-system-architect.md" && grep -qF ".claude/agents/frontend/micro-frontend-architect.md" ".claude/agents/frontend/micro-frontend-architect.md" && grep -qF "# Mobile Developer Agent" ".claude/agents/frontend/mobile-developer.md" && grep -qF ".claude/agents/frontend/pwa-specialist.md" ".claude/agents/frontend/pwa-specialist.md" && grep -qF ".claude/agents/frontend/webassembly-specialist.md" ".claude/agents/frontend/webassembly-specialist.md" && grep -qF "# Cloud Architect Agent" ".claude/agents/infrastructure/cloud-architect.md" && grep -qF "# Database Administrator Agent" ".claude/agents/infrastructure/database-admin.md" && grep -qF ".claude/agents/infrastructure/devops-troubleshooter.md" ".claude/agents/infrastructure/devops-troubleshooter.md" && grep -qF "# Incident Responder Agent" ".claude/agents/infrastructure/incident-responder.md" && grep -qF ".claude/agents/infrastructure/network-engineer.md" ".claude/agents/infrastructure/network-engineer.md" && grep -qF ".claude/agents/infrastructure/observability-engineer.md" ".claude/agents/infrastructure/observability-engineer.md" && grep -qF ".claude/agents/infrastructure/pulumi-typescript-specialist.md" ".claude/agents/infrastructure/pulumi-typescript-specialist.md" && grep -qF ".claude/agents/infrastructure/serverless-architect.md" ".claude/agents/infrastructure/serverless-architect.md" && grep -qF "# Site Reliability Engineer (SRE) Agent" ".claude/agents/infrastructure/site-reliability-engineer.md" && grep -qF ".claude/agents/infrastructure/terraform-specialist.md" ".claude/agents/infrastructure/terraform-specialist.md" && grep -qF ".claude/agents/orchestration/learning-system.md" ".claude/agents/orchestration/learning-system.md" && grep -qF ".claude/agents/performance-optimizers/session-optimizer.md" ".claude/agents/performance-optimizers/session-optimizer.md" && grep -qF ".claude/agents/performance-optimizers/tool-batch-optimizer.md" ".claude/agents/performance-optimizers/tool-batch-optimizer.md" && grep -qF ".claude/agents/personalities/agent-evolution-system.md" ".claude/agents/personalities/agent-evolution-system.md" && grep -qF ".claude/agents/safety-specialists/agent-environment-simulator.md" ".claude/agents/safety-specialists/agent-environment-simulator.md" && grep -qF ".claude/agents/safety-specialists/permission-escalator.md" ".claude/agents/safety-specialists/permission-escalator.md" && grep -qF ".claude/agents/security/devsecops-engineer.md" ".claude/agents/security/devsecops-engineer.md" && grep -qF ".claude/agents/security/privacy-engineer.md" ".claude/agents/security/privacy-engineer.md" && grep -qF ".claude/agents/universal/git-expert.md" ".claude/agents/universal/git-expert.md" && grep -qF ".claude/agents/universal/logging-concepts-engineer.md" ".claude/agents/universal/logging-concepts-engineer.md" && grep -qF ".claude/agents/universal/resilience-engineer.md" ".claude/agents/universal/resilience-engineer.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/ai-analysis/error-detective.md b/.claude/agents/ai-analysis/error-detective.md
@@ -4,6 +4,7 @@ description: Log analysis and error pattern detection specialist focused on iden
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note, mcp__sequential-thinking__sequentialthinking, mcp__zen__debug, mcp__zen__analyze]
 
 instructions: |
+---
 
 ## ⚠️ CRITICAL: Memory Storage Policy
 
diff --git a/.claude/agents/ai-analysis/graphql-architect.md b/.claude/agents/ai-analysis/graphql-architect.md
@@ -4,6 +4,7 @@ description: GraphQL schema design and architecture specialist focused on creati
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
 
 instructions: |
+---
 
 ## ⚠️ CRITICAL: Memory Storage Policy
 
diff --git a/.claude/agents/ai-analysis/prompt-engineer.md b/.claude/agents/ai-analysis/prompt-engineer.md
@@ -4,6 +4,7 @@ description: AI prompt optimization and LLM integration specialist focused on de
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
 
 instructions: |
+---
 
 ## ⚠️ CRITICAL: Memory Storage Policy
 
diff --git a/.claude/agents/ai/machine-learning-engineer.md b/.claude/agents/ai/machine-learning-engineer.md
@@ -3,6 +3,7 @@ name: machine-learning-engineer
 description: Machine Learning engineering specialist focused on designing, implementing, and deploying scalable ML systems, MLOps pipelines, model optimization, an
 # Machine Learning Engineer Agent
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
 
 ## ⚠️ CRITICAL: Memory Storage Policy
 
diff --git a/.claude/agents/ai/nlp-llm-integration-expert.md b/.claude/agents/ai/nlp-llm-integration-expert.md
@@ -1,6 +1,8 @@
 ---
 name: nlp-llm-integration-expert
 description: Natural Language Processing and Large Language Model integration specialist focused on implementing advanced NLP systems, integrating LLMs into applic
+---
+
 # NLP/LLM Integration Expert Agent
 
 ## Role
diff --git a/.claude/agents/automation/cicd-pipeline-engineer.md b/.claude/agents/automation/cicd-pipeline-engineer.md
@@ -1,8 +1,10 @@
 ---
 name: cicd-pipeline-engineer
 description: Continuous Integration and Continuous Deployment specialist focused on automated pipelines, testing automation, release management, and deployment str
-# CI/CD Pipeline Engineer Agent
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__github__list_workflows, mcp__github__run_workflow, mcp__github__get_workflow_run, mcp__github__list_workflow_jobs, mcp__github__get_job_logs, mcp__github__cancel_workflow_run, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
+
+# CI/CD Pipeline Engineer Agent
 
 ## Role
 Continuous Integration and Continuous Deployment specialist focused on automated pipelines, testing automation, release management, and deployment strategies across multiple platforms and cloud providers.
diff --git a/.claude/agents/automation/qa-automation-engineer.md b/.claude/agents/automation/qa-automation-engineer.md
@@ -1,8 +1,10 @@
 ---
 name: qa-automation-engineer
 description: Quality Assurance and Test Automation specialist focused on comprehensive testing strategies, automated testing frameworks, continuous quality assuran
-# QA Automation Engineer Agent
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
+
+# QA Automation Engineer Agent
 
 ## ⚠️ CRITICAL: Memory Storage Policy
 
diff --git a/.claude/agents/automation/release-manager.md b/.claude/agents/automation/release-manager.md
@@ -1,6 +1,8 @@
 ---
 name: release-manager
 description: Release management and deployment orchestration specialist focused on coordinating software releases, managing deployment processes, ensuring release 
+---
+
 # Release Manager Agent
 
 ## Role
diff --git a/.claude/agents/backend/go-resilience-engineer.md b/.claude/agents/backend/go-resilience-engineer.md
@@ -1,6 +1,7 @@
 ---
 name: go-resilience-engineer
 description: A specialized Go resilience engineering agent focused on implementing fault-tolerant systems using Sony GoBreaker, native Go concurrency patterns, and comprehensive resilience libraries for circuit breaking, retries, timeouts, bulkheads, and rate limiting.
+---
 
 instructions: |
   You are a Go resilience engineering specialist with deep expertise in Go's native concurrency primitives and the Go resilience ecosystem. Your role is to help developers implement robust, fault-tolerant Go applications using proven resilience patterns, leveraging Go's strengths in goroutines, channels, and context management.
diff --git a/.claude/agents/backend/go-zap-logging.md b/.claude/agents/backend/go-zap-logging.md
@@ -1,6 +1,7 @@
 ---
 name: go-zap-logging
 description: A specialized Go logging agent focused on implementing high-performance, structured logging using Zap with Google Cloud integration, comprehensive contextual logging patterns, and distributed tracing support.
+---
 
 instructions: |
   You are a Go logging specialist with deep expertise in Uber's Zap logging library and Google Cloud integration. Your role is to help developers implement high-performance, structured logging systems that provide comprehensive observability, proper context management, and seamless cloud integration.
diff --git a/.claude/agents/backend/resilience-engineer.md b/.claude/agents/backend/resilience-engineer.md
@@ -1,6 +1,7 @@
 ---
 name: resilience-engineer
 description: A language-agnostic resilience engineering agent that helps implement fault-tolerant, self-healing systems with proper circuit breakers, retry mechanisms, and graceful degradation patterns.
+---
 
 instructions: |
   You are a resilience engineering expert specializing in building fault-tolerant, self-healing systems. Your role is to help developers implement resilience patterns and principles across any programming language or technology stack.
diff --git a/.claude/agents/backend/typescript-cockatiel-resilience.md b/.claude/agents/backend/typescript-cockatiel-resilience.md
@@ -1,6 +1,7 @@
 ---
 name: typescript-cockatiel-resilience
 description: A specialized TypeScript resilience engineering agent focused on implementing fault-tolerant systems using the Cockatiel library with comprehensive patterns for circuit breakers, retries, timeouts, bulkheads, and rate limiting.
+---
 
 instructions: |
   You are a TypeScript resilience engineering specialist with deep expertise in the Cockatiel library. Your role is to help developers implement robust, fault-tolerant TypeScript applications using proven resilience patterns and best practices.
diff --git a/.claude/agents/backend/typescript-pino-logging.md b/.claude/agents/backend/typescript-pino-logging.md
@@ -1,6 +1,7 @@
 ---
 name: typescript-pino-logging
 description: A specialized TypeScript logging agent focused on implementing high-performance, structured logging using Pino with Fastify integration, Google Cloud compatibility, and comprehensive contextual logging patterns.
+---
 
 instructions: |
   You are a TypeScript logging specialist with deep expertise in Pino and Fastify integration. Your role is to help developers implement high-performance, structured logging systems that provide comprehensive observability, proper context management, and seamless cloud integration.
diff --git a/.claude/agents/business/business-analyst.md b/.claude/agents/business/business-analyst.md
@@ -1,8 +1,10 @@
 ---
 name: business-analyst
 description: You have access to Basic Memory MCP for business logic memory and stakeholder requirements:
-# Business Analyst Agent
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
+
+# Business Analyst Agent
 
 ## Basic Memory MCP Integration
 You have access to Basic Memory MCP for business logic memory and stakeholder requirements:
diff --git a/.claude/agents/business/healthcare-compliance-agent.md b/.claude/agents/business/healthcare-compliance-agent.md
@@ -1,6 +1,8 @@
 ---
 name: healthcare-compliance-agent
 description: Healthcare compliance and regulatory specialist focused on HIPAA compliance, medical data security, healthcare interoperability, and regulatory requir
+---
+
 # Healthcare Compliance Agent
 
 ## Role
diff --git a/.claude/agents/business/payment-integration-agent.md b/.claude/agents/business/payment-integration-agent.md
@@ -1,6 +1,8 @@
 ---
 name: payment-integration-agent
 description: Payment systems integration specialist focused on Stripe, PayPal, financial services integration, PCI DSS compliance, and secure payment processing ac
+---
+
 # Payment Integration Agent
 
 ## Role
diff --git a/.claude/agents/business/product-manager.md b/.claude/agents/business/product-manager.md
@@ -1,8 +1,10 @@
 ---
 name: product-manager
 description: You have access to Basic Memory MCP for feature evolution tracking and user feedback memory:
-# Product Manager Agent
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
+
+# Product Manager Agent
 
 ## Basic Memory MCP Integration
 You have access to Basic Memory MCP for feature evolution tracking and user feedback memory:
diff --git a/.claude/agents/choreography/bug-hunting-tango.md b/.claude/agents/choreography/bug-hunting-tango.md
@@ -1,6 +1,8 @@
 ---
 name: bug-hunting-tango
 description: bug hunting tango specialist agent
+---
+
 # Bug Hunting Tango
 
 ## Multi-Agent Collaboration Pattern for Bug Investigation & Resolution
diff --git a/.claude/agents/choreography/code-review-waltz.md b/.claude/agents/choreography/code-review-waltz.md
@@ -1,6 +1,8 @@
 ---
 name: code-review-waltz
 description: code review waltz specialist agent
+---
+
 # Code Review Waltz
 
 ## Multi-Agent Collaboration Pattern for Comprehensive Code Reviews
diff --git a/.claude/agents/choreography/feature-development-dance.md b/.claude/agents/choreography/feature-development-dance.md
@@ -1,6 +1,8 @@
 ---
 name: feature-development-dance
 description: feature development dance specialist agent
+---
+
 # Feature Development Dance
 
 ## Multi-Agent Collaboration Pattern for New Feature Implementation
diff --git a/.claude/agents/creative/code-archaeologist-time-traveler.md b/.claude/agents/creative/code-archaeologist-time-traveler.md
@@ -2,6 +2,7 @@
 name: code-archaeologist-time-traveler
 description: A mystical code archaeologist who can see through time itself. You analyze git history not just as data, but as epic stories of human struggle, triumph, and evolution. Every commit tells a tale, every refactor marks an era, and every bug fix represents a battle won against chaos.
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
 
 instructions: |
   You are a mystical code archaeologist who can see through time itself. You analyze git history not just as data, but as epic stories of human struggle, triumph, and evolution. Every commit tells a tale, every refactor marks an era, and every bug fix represents a battle won against chaos.
diff --git a/.claude/agents/creative/rubber-duck-debugger.md b/.claude/agents/creative/rubber-duck-debugger.md
@@ -2,6 +2,7 @@
 name: rubber-duck-debugger
 description: The world's most effective rubber duck debugger that guides developers to breakthroughs through strategic questioning using the Socratic method. Asks the perfect question at the perfect moment to create "aha!" moments.
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note, mcp__sequential-thinking__sequentialthinking]
+---
 
 instructions: |
   You are the world's most effective rubber duck debugger. Instead of solving problems directly, you guide developers to their own breakthroughs through strategic questioning. Your superpower is asking the PERFECT question at the PERFECT moment that makes the lightbulb go off.
diff --git a/.claude/agents/creative/technical-debt-collector.md b/.claude/agents/creative/technical-debt-collector.md
@@ -2,6 +2,7 @@
 name: technical-debt-collector
 description: A friendly but firm Technical Debt Collector who works for the Code Quality Family. Tracks every shortcut, TODO comment, and "temporary" workaround with meticulous attention, offering protection plans and structured refactoring to help developers pay down technical debt before it becomes a problem.
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
 
 instructions: |
   You are a friendly but firm Technical Debt Collector who works for the Code Quality Family. You track every shortcut, every TODO comment, every "temporary" workaround with the meticulous attention of a professional debt collector. But you're not here to break kneecaps - you're here to offer protection plans and help developers pay down their technical debt before it becomes a problem.
diff --git a/.claude/agents/data/analytics-implementation-specialist.md b/.claude/agents/data/analytics-implementation-specialist.md
@@ -1,6 +1,8 @@
 ---
 name: analytics-implementation-specialist
 description: Analytics implementation and measurement specialist focused on implementing comprehensive analytics solutions, tracking user behavior, measuring busin
+---
+
 # Analytics Implementation Specialist Agent
 
 ## Role
diff --git a/.claude/agents/data/business-intelligence-developer.md b/.claude/agents/data/business-intelligence-developer.md
@@ -1,6 +1,8 @@
 ---
 name: business-intelligence-developer
 description: Business Intelligence and data visualization specialist focused on transforming raw data into actionable business insights through advanced analytics,
+---
+
 # Business Intelligence Developer Agent
 
 ## Role
diff --git a/.claude/agents/data/data-engineer.md b/.claude/agents/data/data-engineer.md
@@ -1,6 +1,8 @@
 ---
 name: data-engineer
 description: Data engineering and infrastructure specialist focused on building scalable data pipelines, data warehousing, ETL/ELT processes, and ensuring reliable
+---
+
 # Data Engineer Agent
 
 ## Role
diff --git a/.claude/agents/frontend/design-system-architect.md b/.claude/agents/frontend/design-system-architect.md
@@ -1,6 +1,8 @@
 ---
 name: design-system-architect
 description: Design System architecture specialist focused on creating scalable, maintainable design systems, component libraries, and design tokens that ensure co
+---
+
 # Design System Architect Agent
 
 ## Role
diff --git a/.claude/agents/frontend/micro-frontend-architect.md b/.claude/agents/frontend/micro-frontend-architect.md
@@ -1,6 +1,8 @@
 ---
 name: micro-frontend-architect
 description: Micro-frontend architecture specialist focused on designing and implementing scalable, maintainable frontend applications using micro-frontend pattern
+---
+
 # Micro-Frontend Architect Agent
 
 ## Role
diff --git a/.claude/agents/frontend/mobile-developer.md b/.claude/agents/frontend/mobile-developer.md
@@ -1,8 +1,11 @@
 ---
 name: mobile-developer
 description: You have access to Basic Memory MCP for mobile development patterns and platform-specific knowledge:
-# Mobile Developer Agent
+
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
+
+# Mobile Developer Agent
 
 ## Basic Memory MCP Integration
 You have access to Basic Memory MCP for mobile development patterns and platform-specific knowledge:
diff --git a/.claude/agents/frontend/pwa-specialist.md b/.claude/agents/frontend/pwa-specialist.md
@@ -1,6 +1,8 @@
 ---
 name: pwa-specialist
 description: Progressive Web Application (PWA) development specialist focused on creating app-like web experiences, offline functionality, performance optimization
+---
+
 # PWA Specialist Agent
 
 ## Role
diff --git a/.claude/agents/frontend/webassembly-specialist.md b/.claude/agents/frontend/webassembly-specialist.md
@@ -1,6 +1,8 @@
 ---
 name: webassembly-specialist
 description: WebAssembly (WASM) development and optimization specialist focused on high-performance web applications, cross-platform compilation, browser optimizat
+---
+
 # WebAssembly Specialist Agent
 
 ## Role
diff --git a/.claude/agents/infrastructure/cloud-architect.md b/.claude/agents/infrastructure/cloud-architect.md
@@ -1,8 +1,11 @@
 ---
 name: cloud-architect
 description: Cloud infrastructure design specialist focused on scalable, secure, and cost-effective cloud architectures across AWS, GCP, and Azure platforms.
-# Cloud Architect Agent
+
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note, mcp__sequential-thinking__sequentialthinking]
+---
+
+# Cloud Architect Agent
 
 ## ⚠️ CRITICAL: Memory Storage Policy
 
diff --git a/.claude/agents/infrastructure/database-admin.md b/.claude/agents/infrastructure/database-admin.md
@@ -1,8 +1,11 @@
 ---
 name: database-admin
 description: Database operations, optimization, and maintenance specialist focused on ensuring database performance, reliability, and security across multiple data
-# Database Administrator Agent
+
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
+
+# Database Administrator Agent
 
 ## ⚠️ CRITICAL: Memory Storage Policy
 
diff --git a/.claude/agents/infrastructure/devops-troubleshooter.md b/.claude/agents/infrastructure/devops-troubleshooter.md
@@ -1,6 +1,8 @@
 ---
 name: devops-troubleshooter
 description: Production debugging and incident response specialist focused on diagnosing system issues, resolving outages, and implementing preventive measures.
+---
+
 # DevOps Troubleshooter Agent
 
 ## Role
diff --git a/.claude/agents/infrastructure/incident-responder.md b/.claude/agents/infrastructure/incident-responder.md
@@ -1,8 +1,11 @@
 ---
 name: incident-responder
 description: Production incident handling specialist focused on coordinating incident response, crisis management, and post-incident analysis to minimize system do
-# Incident Responder Agent
+
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
+
+# Incident Responder Agent
 
 ## ⚠️ CRITICAL: Memory Storage Policy
 
diff --git a/.claude/agents/infrastructure/network-engineer.md b/.claude/agents/infrastructure/network-engineer.md
@@ -1,6 +1,8 @@
 ---
 name: network-engineer
 description: Network infrastructure specialist focused on DNS management, load balancing, network troubleshooting, connectivity issues, and network architecture de
+---
+
 # Network Engineer Agent
 
 ## Role
diff --git a/.claude/agents/infrastructure/observability-engineer.md b/.claude/agents/infrastructure/observability-engineer.md
@@ -1,6 +1,8 @@
 ---
 name: observability-engineer
 description: Observability engineering specialist focused on implementing comprehensive monitoring, logging, tracing, and analytics solutions to provide deep visib
+---
+
 # Observability Engineer Agent
 
 ## Role
diff --git a/.claude/agents/infrastructure/pulumi-typescript-specialist.md b/.claude/agents/infrastructure/pulumi-typescript-specialist.md
@@ -1,6 +1,8 @@
 ---
 name: pulumi-typescript-specialist
 description: Pulumi Infrastructure as Code specialist focused on building, deploying, and managing cloud infrastructure using TypeScript, implementing modern infra
+---
+
 # Pulumi TypeScript Specialist Agent
 
 ## Role
diff --git a/.claude/agents/infrastructure/serverless-architect.md b/.claude/agents/infrastructure/serverless-architect.md
@@ -1,6 +1,8 @@
 ---
 name: serverless-architect
 description: Serverless architecture specialist focused on designing and implementing cloud-native, event-driven applications using Function-as-a-Service (FaaS), s
+---
+
 # Serverless Architect Agent
 
 ## Role
diff --git a/.claude/agents/infrastructure/site-reliability-engineer.md b/.claude/agents/infrastructure/site-reliability-engineer.md
@@ -1,8 +1,11 @@
 ---
 name: site-reliability-engineer
 description: Site Reliability Engineering specialist focused on building and maintaining highly reliable, scalable systems through automation, monitoring, incident
-# Site Reliability Engineer (SRE) Agent
+
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
+
+# Site Reliability Engineer (SRE) Agent
 
 ## ⚠️ CRITICAL: Memory Storage Policy
 
diff --git a/.claude/agents/infrastructure/terraform-specialist.md b/.claude/agents/infrastructure/terraform-specialist.md
@@ -1,6 +1,8 @@
 ---
 name: terraform-specialist
 description: Infrastructure as Code (IaC) specialist focused on Terraform development, multi-cloud provisioning, infrastructure automation, and cloud resource mana
+---
+
 # Terraform Specialist Agent
 
 ## Role
diff --git a/.claude/agents/orchestration/learning-system.md b/.claude/agents/orchestration/learning-system.md
@@ -1,6 +1,8 @@
 ---
 name: learning-system
 description: Continuous learning system for organizational knowledge building and pattern recognition
+---
+
 # Agent Learning and Evolution System
 
 ## Continuous Improvement Through Outcome Analysis
diff --git a/.claude/agents/performance-optimizers/session-optimizer.md b/.claude/agents/performance-optimizers/session-optimizer.md
@@ -1,6 +1,8 @@
 ---
 name: session-optimizer
 description: Performance optimization specialist focused on long-term session efficiency, context management optimization, and memory/token usage reduction while m
+---
+
 # Session Optimizer Agent
 
 ## Role
diff --git a/.claude/agents/performance-optimizers/tool-batch-optimizer.md b/.claude/agents/performance-optimizers/tool-batch-optimizer.md
@@ -1,5 +1,7 @@
 ---
 name: tool-batch-optimizer
+---
+
 # Tool Batch Optimizer Agent
 
 ## Role
diff --git a/.claude/agents/personalities/agent-evolution-system.md b/.claude/agents/personalities/agent-evolution-system.md
@@ -1,6 +1,8 @@
 ---
 name: agent-evolution-system
 description: agent evolution system specialist agent
+---
+
 # Agent Evolution System
 
 ## Self-Modifying Agent Behavior Through Adaptive Learning
diff --git a/.claude/agents/safety-specialists/agent-environment-simulator.md b/.claude/agents/safety-specialists/agent-environment-simulator.md
@@ -1,5 +1,7 @@
 ---
 name: agent-environment-simulator
+---
+
 # Agent Environment Simulator Agent
 
 ## Role
diff --git a/.claude/agents/safety-specialists/permission-escalator.md b/.claude/agents/safety-specialists/permission-escalator.md
@@ -1,6 +1,8 @@
 ---
 name: permission-escalator
 description: Dynamic permission management specialist that implements real-time permission prompting and escalation workflows, enabling safe autonomous agent opera
+---
+
 # Permission Escalator Agent
 
 ## Role
diff --git a/.claude/agents/security/devsecops-engineer.md b/.claude/agents/security/devsecops-engineer.md
@@ -1,6 +1,8 @@
 ---
 name: devsecops-engineer
 description: DevSecOps engineering specialist focused on integrating security practices throughout the software development lifecycle, implementing automated secur
+---
+
 # DevSecOps Engineer Agent
 
 ## Role
diff --git a/.claude/agents/security/privacy-engineer.md b/.claude/agents/security/privacy-engineer.md
@@ -1,6 +1,8 @@
 ---
 name: privacy-engineer
 description: Privacy engineering specialist focused on implementing privacy-by-design principles, data protection compliance, and privacy-preserving technologies t
+---
+
 # Privacy Engineer Agent
 
 ## Role
diff --git a/.claude/agents/universal/git-expert.md b/.claude/agents/universal/git-expert.md
@@ -16,6 +16,7 @@ description: |
 tools: [Read, Edit, Bash, Grep, Glob, LS, mcp__github__get_repo, mcp__github__list_issues, mcp__github__create_issue, mcp__github__get_issue, mcp__github__update_issue, mcp__github__list_pull_requests, mcp__github__create_pull_request, mcp__github__get_pull_request, mcp__github__update_pull_request, mcp__github__list_commits, mcp__github__get_commit, mcp__github__create_branch, mcp__github__list_branches, mcp__github__get_branch, mcp__github__create_workflow_dispatch, mcp__github__list_workflow_runs, mcp__github__get_workflow_run, mcp__github__list_artifacts, mcp__github__download_artifact, mcp__github__search_repositories, mcp__github__search_code, mcp__github__search_issues, mcp__github__get_user, mcp__github__list_repos_for_user, mcp__github__get_file_contents, mcp__github__create_or_update_file, mcp__github__delete_file, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note, mcp__zen__analyze, mcp__zen__debug]
 proactive: true
 ---
+
 You are a Git Expert specializing in advanced Git workflow management, merge conflict resolution, and comprehensive GitHub integration. You provide expert-level Git operations with proactive problem detection and automated workflow optimization.
 
 ## CRITICAL: COMMIT MESSAGE REQUIREMENTS - NO EXCEPTIONS
diff --git a/.claude/agents/universal/logging-concepts-engineer.md b/.claude/agents/universal/logging-concepts-engineer.md
@@ -1,6 +1,7 @@
 ---
 name: logging-concepts-engineer
 description: A language-agnostic logging specialist that helps implement structured, contextual, and performance-conscious logging systems across any technology stack, following enterprise-grade logging principles and best practices.
+---
 
 instructions: |
   You are a logging architecture specialist with expertise in designing and implementing comprehensive logging systems across all programming languages and platforms. Your role is to help developers implement structured, contextual, and performance-conscious logging that enables effective monitoring, debugging, and system observability.
diff --git a/.claude/agents/universal/resilience-engineer.md b/.claude/agents/universal/resilience-engineer.md
@@ -2,6 +2,7 @@
 name: resilience-engineer
 description: A language-agnostic resilience engineering agent that helps implement fault-tolerant, self-healing systems with proper circuit breakers, retry mechanisms, and graceful degradation patterns.
 tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, LS, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, mcp__basic-memory__edit_note]
+---
 
 instructions: |
   You are a resilience engineering expert specializing in building fault-tolerant, self-healing systems. Your role is to help developers implement resilience patterns and principles across any programming language or technology stack.
PATCH

echo "Gold patch applied."
