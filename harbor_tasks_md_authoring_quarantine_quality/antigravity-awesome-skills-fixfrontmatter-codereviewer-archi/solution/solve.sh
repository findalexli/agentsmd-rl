#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "description: Master software architect specializing in modern architecture" "skills/architect-review/SKILL.md" && grep -qF "description: Write efficient C code with proper memory management, pointer" "skills/c-pro/SKILL.md" && grep -qF "description: Elite code review expert specializing in modern AI-powered code" "skills/code-reviewer/SKILL.md" && grep -qF "description:" "skills/design-orchestration/SKILL.md" && grep -qF "description: Expert Haskell engineer specializing in advanced type systems, pure" "skills/haskell-pro/SKILL.md" && grep -qF "description:" "skills/multi-agent-brainstorming/SKILL.md" && grep -qF "description: Expert performance engineer specializing in modern observability," "skills/performance-engineer/SKILL.md" && grep -qF "description: Expert web researcher using advanced search techniques and" "skills/search-specialist/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/architect-review/SKILL.md b/skills/architect-review/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: architect-review
-description: "Master software architect specializing in modern architecture"
+description: Master software architect specializing in modern architecture
   patterns, clean architecture, microservices, event-driven systems, and DDD.
   Reviews system designs and code changes for architectural integrity,
   scalability, and maintainability. Use PROACTIVELY for architectural decisions.
diff --git a/skills/c-pro/SKILL.md b/skills/c-pro/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: c-pro
-description: "Write efficient C code with proper memory management, pointer"
+description: Write efficient C code with proper memory management, pointer
   arithmetic, and system calls. Handles embedded systems, kernel modules, and
   performance-critical code. Use PROACTIVELY for C optimization, memory issues,
   or system programming.
diff --git a/skills/code-reviewer/SKILL.md b/skills/code-reviewer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: code-reviewer
-description: "Elite code review expert specializing in modern AI-powered code"
+description: Elite code review expert specializing in modern AI-powered code
   analysis, security vulnerabilities, performance optimization, and production
   reliability. Masters static analysis tools, security scanning, and
   configuration review with 2024/2025 best practices. Use PROACTIVELY for code
diff --git a/skills/design-orchestration/SKILL.md b/skills/design-orchestration/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: design-orchestration
-description: ">"
+description: 
   Orchestrates design workflows by routing work through
   brainstorming, multi-agent review, and execution readiness
   in the correct order. Prevents premature implementation,
diff --git a/skills/haskell-pro/SKILL.md b/skills/haskell-pro/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: haskell-pro
-description: "Expert Haskell engineer specializing in advanced type systems, pure"
+description: Expert Haskell engineer specializing in advanced type systems, pure
   functional design, and high-reliability software. Use PROACTIVELY for
   type-level programming, concurrency, and architecture guidance.
 metadata:
diff --git a/skills/multi-agent-brainstorming/SKILL.md b/skills/multi-agent-brainstorming/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: multi-agent-brainstorming
-description: ">"
+description: 
   Use this skill when a design or idea requires higher confidence,
   risk reduction, or formal review. This skill orchestrates a
   structured, sequential multi-agent design review where each agent
diff --git a/skills/performance-engineer/SKILL.md b/skills/performance-engineer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: performance-engineer
-description: "Expert performance engineer specializing in modern observability,"
+description: Expert performance engineer specializing in modern observability,
   application optimization, and scalable system performance. Masters
   OpenTelemetry, distributed tracing, load testing, multi-tier caching, Core Web
   Vitals, and performance monitoring. Handles end-to-end optimization, real user
diff --git a/skills/search-specialist/SKILL.md b/skills/search-specialist/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: search-specialist
-description: "Expert web researcher using advanced search techniques and"
+description: Expert web researcher using advanced search techniques and
   synthesis. Masters search operators, result filtering, and multi-source
   verification. Handles competitive analysis and fact-checking. Use PROACTIVELY
   for deep research, information gathering, or trend analysis.
PATCH

echo "Gold patch applied."
