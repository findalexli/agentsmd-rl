#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-toolkit

# Idempotency guard
if grep -qF "| **test-driven-development** | User wants RED-GREEN-REFACTOR cycle with strict " "skills/do/references/routing-tables.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/do/references/routing-tables.md b/skills/do/references/routing-tables.md
@@ -18,6 +18,7 @@ Route to these agents based on the user's task domain. Each entry describes what
 | **typescript-frontend-engineer** | User is building or fixing TypeScript frontend code: React components, Next.js pages, UI logic, browser APIs, or frontend state management. |
 | **typescript-debugging-engineer** | User needs to debug TypeScript-specific issues: async bugs, race conditions, type errors at runtime, or hard-to-reproduce frontend failures. |
 | **nodejs-api-engineer** | User is building or maintaining Node.js backends: Express APIs, REST endpoints, middleware, or server-side JavaScript. |
+| **kotlin-general-engineer** | User is working on Kotlin code, coroutines, Ktor, Compose Multiplatform, Gradle KTS, or any Kotlin-language task. NOT: tasks that merely mention Kotlin as context. |
 | **kubernetes-helm-engineer** | User is deploying, configuring, or troubleshooting Kubernetes workloads, Helm charts, k8s manifests, or cluster operations. |
 | **prometheus-grafana-engineer** | User needs monitoring infrastructure: Prometheus scrape configs, alerting rules, Grafana dashboards, or observability setup. |
 | **database-engineer** | User is designing schemas, writing SQL queries, optimizing database performance, or managing migrations. |
@@ -27,9 +28,12 @@ Route to these agents based on the user's task domain. Each entry describes what
 | **opensearch-elasticsearch-engineer** | User needs search cluster work: index management, query optimization, Elasticsearch/OpenSearch operations. |
 | **python-openstack-engineer** | User is developing OpenStack services, plugins, or components — specifically within the OpenStack ecosystem. |
 | **sqlite-peewee-engineer** | User is working with SQLite databases via the Peewee ORM in Python. |
+| **swift-general-engineer** | User is working on Swift code, iOS, macOS, SwiftUI, server-side Swift, or any Swift-language task including concurrency and testing. NOT: tasks that merely mention Swift as context. |
 | **performance-optimization-engineer** | User wants to improve web performance: Core Web Vitals, load times, bundle size, rendering optimization. |
+| **php-general-engineer** | User is working on PHP code, Laravel, Symfony, Composer, or any PHP-language task including modern PHP 8.x patterns and security. NOT: tasks that merely mention PHP as context. |
 | **mcp-local-docs-engineer** | User wants to build an MCP (Model Context Protocol) server or turn a repository into an MCP documentation source. |
 | **research-coordinator-engineer** | User needs systematic research with multiple sources, parallel investigation, or evidence synthesis before acting. NOT: a quick web lookup or single-source check. |
+| **research-subagent-executor** | Subagent that executes delegated research tasks using OODA-loop investigation, intelligence gathering, and source evaluation. Dispatched by research-coordinator-engineer, not invoked directly by users. |
 | **project-coordinator-engineer** | User needs multi-agent coordination for a large project: spawning parallel agents, tracking cross-cutting tasks, or orchestrating a multi-phase effort. |
 | **pipeline-orchestrator-engineer** | User wants to create a new pipeline, scaffold a new structured workflow, or compose pipeline phases. |
 | **hook-development-engineer** | User wants to create or modify Python hooks for Claude Code's event-driven system (SessionStart, PostToolUse, etc.). |
@@ -60,13 +64,19 @@ Route to these agents based on the user's task domain. Each entry describes what
 | **vitest-runner** | User wants to run Vitest tests, parse test results, or check if Vitest tests pass. NOT: running Jest, Mocha, or other test runners. |
 | **github-actions-check** | User wants to know if CI passed, check GitHub Actions status, or see build results. NOT: "check this out" (browsing), "check my work" (review), "check the logic" (analysis) — those do not involve CI. |
 | **read-only-ops** | User explicitly wants read-only operations: browsing, exploring, or examining without any modifications. |
-| **go-patterns** | User wants Go development patterns: testing, concurrency, errors, review, quality checks, or conventions. |
 | **python-quality-gate** | User wants Python quality checks: ruff linting, mypy type checking, or combined Python quality validation. |
 | **condition-based-waiting** | User needs retry logic, backoff strategies, polling loops, or health check patterns in their code. |
+| **distinctive-frontend-design** | User wants context-driven aesthetic exploration for a frontend project with anti-cliche validation: typography exploration, visual identity, design language. |
+| **do** | Primary entry point for all delegated work: classifies user requests and routes to the correct agent + skill combination. |
+| **e2e-testing** | User wants Playwright-based end-to-end testing: page object models, browser tests, test flakiness reduction. NOT: unit tests or integration tests (use test-driven-development or vitest-runner). |
+| **kotlin-coroutines** | User wants Kotlin structured concurrency patterns: coroutineScope, Flow, Channel, SupervisorJob, or dispatchers. Companion skill for kotlin-general-engineer. |
+| **kotlin-testing** | User wants Kotlin testing patterns: JUnit 5, Kotest, coroutine test dispatchers, MockK. Companion skill for kotlin-general-engineer. |
 | **testing-anti-patterns** | User wants to identify or fix flaky tests, or review tests for common anti-patterns. |
 | **subagent-driven-development** | User wants to execute a complex plan using subagents in fresh contexts, or needs a two-stage review/implementation cycle. |
 | **workflow-orchestrator** | User wants to execute an existing plan with structured phases, or says "run the plan", "execute this". |
 | **parallel-code-review** | User wants comprehensive review of a codebase from multiple reviewer perspectives simultaneously. |
+| **php-quality** | User wants PHP code quality checks: PSR standards compliance, strict types enforcement, framework idioms. Companion skill for php-general-engineer. |
+| **php-testing** | User wants PHP testing patterns: PHPUnit, test doubles, database testing. Companion skill for php-general-engineer. |
 | **codex-code-review** | User wants a second-opinion code review from OpenAI Codex CLI (GPT-5.4 xhigh), a cross-model review, or says "codex review", "second opinion", "get another perspective". NOT: a standard Claude-only review (use systematic-code-review or parallel-code-review). |
 | **with-anti-rationalization** | User explicitly requests maximum rigor, thorough verification, or wants anti-rationalization patterns injected. |
 | **plan-manager** | User wants to see the status of plans, audit existing plans, or manage the plan lifecycle. |
@@ -89,8 +99,15 @@ Route to these agents based on the user's task domain. Each entry describes what
 | **plant-seed** | User wants to capture a forward-looking idea with trigger conditions so it surfaces automatically during future feature design. |
 | **install** | User wants to verify Claude Code Toolkit installation, diagnose setup issues, or check if the toolkit is correctly configured. |
 | **skill-creator** | User wants to create or improve a Claude Code skill, workflow automation, or agent configuration. |
+| **swift-concurrency** | User wants Swift concurrency patterns: async/await, Actor, Task, Sendable, structured concurrency. Companion skill for swift-general-engineer. |
+| **swift-testing** | User wants Swift testing patterns: XCTest, Swift Testing framework, async test patterns. Companion skill for swift-general-engineer. |
+| **systematic-code-review** | User wants a structured 4-phase code review: UNDERSTAND changes, VERIFY claims against actual behavior, ASSESS security/performance/architecture risks, DOCUMENT findings with severity classification. |
 | **systematic-debugging** | User wants to diagnose why something is broken or not working as expected — root cause analysis, reproduce-isolate-identify-verify. Common phrasings: "why is this broken", "what's wrong with", "figure out why", "can't figure out", "not working", "slow", "performance", "taking too long", "optimize". NOT: debugging a past session (use forensics), guided self-discovery (use socratic-debugging). |
 | **systematic-refactoring** | User wants to improve existing code structure without changing behavior — extract, rename, simplify, restructure. Common phrasings: "clean this up", "improve this code", "make this better", "code quality". NOT: adding new features (use a domain agent), fixing a bug (use systematic-debugging). |
+| **test-driven-development** | User wants RED-GREEN-REFACTOR cycle with strict phase gates: write failing test first, make it pass with minimal code, then refactor. Common phrasings: "TDD", "test first", "red green refactor", "write tests before code". |
+| **threejs-builder** | User wants to build a Three.js 3D web application: scenes, WebGL, 3D animation, or 3D graphics in the browser. 4-phase workflow: Design, Build, Animate, Polish. |
+| **verification-before-completion** | User wants defense-in-depth verification before declaring a task complete: run full test suite, validate build, check for stub patterns, confirm artifacts exist. |
+| **worktree-agent** | Mandatory rules for agents operating in git worktree isolation: verify working directory, create feature branches, use absolute paths. Not user-invoked directly. |
 
 ---
 
@@ -108,12 +125,15 @@ Route to these agents based on the user's task domain. Each entry describes what
 | **testing-agents-with-subagents** | User wants to validate an agent by running it against real test cases in subagents. |
 | **skill-eval** | User wants to evaluate a skill, test triggers manually, benchmark it against scenarios, or inspect skill quality without running the autoresearch optimizer. |
 | **full-repo-review** | User wants a comprehensive 3-wave review of all source files in the entire repository. |
+| **github-notification-triage** | User wants to triage GitHub notifications: fetch, classify, and report actions needed. Common phrasings: "check notifications", "github inbox", "triage notifications". |
 | **repo-value-analysis** | User wants to systematically analyze an external repository to determine what ideas or patterns are worth adopting. |
+| **roast** | User wants constructive critique of a design doc, idea, or code via 5 HackerNews personas with claim validation. Common phrasings: "roast this", "devil's advocate", "stress test this idea", "poke holes in this". |
 | **data-analysis** | User wants to analyze data: CSV files, metrics, A/B test results, cohort analysis, statistical distributions, KPIs, or funnel data. |
 | **kairos-lite** | User wants a project status briefing, health check, or to see what happened overnight — GitHub notifications, CI status, toolkit health. Common phrasings: "what happened", "morning briefing", "check notifications", "project status", "health check". NOT: specific PR status (use github-actions-check), specific CI debugging (use systematic-debugging). |
 | **pr-workflow** (miner mode) | User wants to extract review comments or learnings from past GitHub PRs, or coordinate batch mining. |
 | **skill-composer** | User wants to compose multiple skills into a multi-skill workflow. |
 | **routing-table-updater** | User wants to update routing tables after adding or changing agents/skills. |
+| **security-threat-model** | User wants a security threat model: scan for attack surface, supply-chain risks, injection vectors, or security posture audit. |
 | **docs-sync-checker** | User wants to check if README files or documentation are in sync with the actual code. |
 | **do-perspectives** | User wants multi-perspective analysis of a problem from 10 different lenses simultaneously. |
 | **do → parallel-analysis** | User wants parallel multi-angle extraction of insights from a document or codebase. Loaded from `skills/do/references/parallel-analysis.md`. |
@@ -150,6 +170,7 @@ Route to these agents based on the user's task domain. Each entry describes what
 |-------|-------------------|
 | **voice-writer** | User wants to write a blog post, article, or long-form content in a specific voice. |
 | **anti-ai-editor** | User wants to edit content to remove AI-sounding patterns, genericness, or sterile phrasing. |
+| **content-engine** | User wants to repurpose source assets (articles, demos, docs) into platform-native social content. Common phrasings: "repurpose this", "adapt for social", "turn this into posts", "platform variants". |
 | **de-ai-pipeline (FORCE)** | User wants to scan and systematically fix AI patterns across documentation or a content repository. |
 | **post-outliner** | User wants a structured outline for a blog post or article before writing. |
 | **topic-brainstormer** | User wants ideas or topics to write about in a domain. |
@@ -168,11 +189,15 @@ Route to these agents based on the user's task domain. Each entry describes what
 | **wordpress-live-validation** | User wants to validate WordPress posts live after upload: check rendering, canonical URLs, or publication status. |
 | **joy-check** | User wants to validate that content has positive, joy-centered framing — not negative or fear-based tone. |
 | **pptx-generator** | User wants to generate a PowerPoint presentation, slide deck, or pitch deck from content or research. |
+| **frontend-slides** | User wants browser-based HTML presentations: reveal-style slide decks, kiosk presentations, or converting PPTX to web format. |
+| **gemini-image-generator** | User wants to generate images from text prompts via Google Gemini: sprites, character art, or AI-generated visuals. |
 | **bluesky-reader** | User wants to read public Bluesky feeds, fetch posts, or interact with the AT Protocol API. |
 | **image-to-video** | User wants to combine a static image with audio to create a video file (album art video, podcast video, music visualization). |
 | **headless-cron-creator** | User wants to generate a headless Claude Code cron job that runs a task on a schedule. |
 | **auto-dream** | User wants to run or configure the background memory consolidation and graduation system: trigger a dream cycle, check dream/graduation status, review the last dream report, check graduation candidates, or configure the nightly cron. Triggers: "dream", "memory consolidation", "consolidate memories", "auto-dream", "last dream", "graduate learnings", "promote learnings". Category: meta-tooling. |
 | **nano-banana-builder** | User wants to build a Next.js web application using Google Gemini Nano Banana image generation APIs. |
+| **video-editing** | User wants to edit video: cut footage, assemble clips, create demo videos, or build screen recordings via FFmpeg and Remotion. |
+| **x-api** | User wants to post tweets, build threads, upload media, read timelines, or search via the X (Twitter) API. |
 
 ---
 
@@ -262,6 +287,8 @@ Workflows that work together in common sequences:
 | Skill | When to Route Here |
 |-------|-------------------|
 | **endpoint-validator** | User wants to validate that API endpoints are reachable and returning expected responses. |
+| **kubernetes-debugging** | User wants to debug Kubernetes pod failures, networking issues, or resource problems using structured triage: describe, logs, events, exec. Companion skill for kubernetes-helm-engineer. |
+| **kubernetes-security** | User wants to harden Kubernetes clusters: RBAC, PodSecurity standards, network policies, secret management, supply chain controls. Companion skill for kubernetes-helm-engineer. |
 | **service-health-check** | User wants to check if a service is healthy or needs restarting. |
 | **cron-job-auditor** | User wants to audit cron jobs or scheduled scripts for reliability and correctness. |
 
@@ -301,7 +328,7 @@ Consolidated reviewer agents, each covering multiple review perspectives:
 | "add worker pool" | **go-patterns (FORCE)** | Go concurrency domain — force-route |
 | "add auth to Python API" | python-general-engineer + workflow-orchestrator | Python domain, multi-step implementation |
 | "review my K8s manifests" | kubernetes-helm-engineer + systematic-code-review | K8s domain, review task |
-| "roast this design doc" | roast skill (5 personas) | Multi-persona critique |
+| "roast this design doc" | roast (5 personas) | Multi-persona critique |
 | "execute plan with subagents" | subagent-driven-development | Explicit subagent execution |
 | "debug TypeScript race condition" | typescript-debugging-engineer + systematic-debugging | TS debugging domain |
 | "write in custom voice" | voice-writer + [your-voice-skill] | Voice generation task |
PATCH

echo "Gold patch applied."
