#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opik

# Idempotency guard
if grep -qF "globs: apps/opik-backend/**/*" "apps/opik-backend/.cursor/rules/api_design.mdc" && grep -qF "globs: apps/opik-backend/**/*" "apps/opik-backend/.cursor/rules/architecture.mdc" && grep -qF "globs: apps/opik-backend/**/*" "apps/opik-backend/.cursor/rules/business_logic.mdc" && grep -qF "globs: apps/opik-backend/**/*" "apps/opik-backend/.cursor/rules/code_quality.mdc" && grep -qF "alwaysApply: false" "apps/opik-backend/.cursor/rules/db_migration_script.mdc" && grep -qF "alwaysApply: false" "apps/opik-backend/.cursor/rules/error_handling.mdc" && grep -qF "alwaysApply: false" "apps/opik-backend/.cursor/rules/general.mdc" && grep -qF "alwaysApply: false" "apps/opik-backend/.cursor/rules/logging.mdc" && grep -qF "globs: apps/opik-backend/**/*" "apps/opik-backend/.cursor/rules/mysql.mdc" && grep -qF "globs: apps/opik-backend/**/*" "apps/opik-backend/.cursor/rules/tech_stack.mdc" && grep -qF "globs: apps/opik-backend/**/*" "apps/opik-backend/.cursor/rules/testing.mdc" && grep -qF "globs: apps/opik-frontend/**/*" "apps/opik-frontend/.cursor/rules/accessibility-testing.mdc" && grep -qF "globs: apps/opik-frontend/**/*" "apps/opik-frontend/.cursor/rules/api-data-fetching.mdc" && grep -qF "globs: apps/opik-frontend/**/*" "apps/opik-frontend/.cursor/rules/code-quality.mdc" && grep -qF "globs: apps/opik-frontend/**/*" "apps/opik-frontend/.cursor/rules/forms.mdc" && grep -qF "globs: apps/opik-frontend/**/*" "apps/opik-frontend/.cursor/rules/frontend_rules.mdc" && grep -qF "globs: apps/opik-frontend/**/*" "apps/opik-frontend/.cursor/rules/performance.mdc" && grep -qF "globs: apps/opik-frontend/**/*" "apps/opik-frontend/.cursor/rules/state-management.mdc" && grep -qF "globs: apps/opik-frontend/**/*" "apps/opik-frontend/.cursor/rules/tech-stack.mdc" && grep -qF "globs: apps/opik-frontend/**/*" "apps/opik-frontend/.cursor/rules/ui-components.mdc" && grep -qF "globs: apps/opik-frontend/**/*" "apps/opik-frontend/.cursor/rules/unit-testing.mdc" && grep -qF "alwaysApply: false" "sdks/python/.cursor/rules/api-design.mdc" && grep -qF "alwaysApply: false" "sdks/python/.cursor/rules/architecture.mdc" && grep -qF "alwaysApply: false" "sdks/python/.cursor/rules/code-structure.mdc" && grep -qF "alwaysApply: false" "sdks/python/.cursor/rules/dependencies.mdc" && grep -qF "alwaysApply: false" "sdks/python/.cursor/rules/design-principles.mdc" && grep -qF "alwaysApply: false" "sdks/python/.cursor/rules/documentation-style.mdc" && grep -qF "alwaysApply: false" "sdks/python/.cursor/rules/error-handling.mdc" && grep -qF "alwaysApply: false" "sdks/python/.cursor/rules/logging.mdc" && grep -qF "globs: sdks/python/src/opik/**/*" "sdks/python/.cursor/rules/method-refactoring-patterns.mdc" && grep -qF "alwaysApply: false" "sdks/python/.cursor/rules/test-best-practices.mdc" && grep -qF "alwaysApply: false" "sdks/python/.cursor/rules/test-implementation.mdc" && grep -qF "alwaysApply: false" "sdks/python/.cursor/rules/test-organization.mdc" && grep -qF "alwaysApply: false" "sdks/typescript/.cursor/rules/architecture.mdc" && grep -qF "alwaysApply: false" "sdks/typescript/.cursor/rules/code-structure.mdc" && grep -qF "alwaysApply: false" "sdks/typescript/.cursor/rules/integrations.mdc" && grep -qF "alwaysApply: false" "sdks/typescript/.cursor/rules/logging.mdc" && grep -qF "alwaysApply: false" "sdks/typescript/.cursor/rules/overview.mdc" && grep -qF "globs: sdks/typescript/**/*" "sdks/typescript/.cursor/rules/test-best-practices.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/apps/opik-backend/.cursor/rules/api_design.mdc b/apps/opik-backend/.cursor/rules/api_design.mdc
@@ -1,7 +1,7 @@
 ---
 description: API Design Guidelines
-globs:
-alwaysApply: true
+globs: apps/opik-backend/**/*
+alwaysApply: false
 ---
 
 # API Design Guidelines
diff --git a/apps/opik-backend/.cursor/rules/architecture.mdc b/apps/opik-backend/.cursor/rules/architecture.mdc
@@ -1,7 +1,7 @@
 ---
 description: Architecture guidelines
-globs:
-alwaysApply: true
+globs: apps/opik-backend/**/*
+alwaysApply: false
 ---
 
 # Architecture Guidelines
diff --git a/apps/opik-backend/.cursor/rules/business_logic.mdc b/apps/opik-backend/.cursor/rules/business_logic.mdc
@@ -1,7 +1,7 @@
 ---
 description: Business Logic Guidelines
-globs:
-alwaysApply: true
+globs: apps/opik-backend/**/*
+alwaysApply: false
 ---
 
 # Business Logic Guidelines
diff --git a/apps/opik-backend/.cursor/rules/code_quality.mdc b/apps/opik-backend/.cursor/rules/code_quality.mdc
@@ -1,7 +1,7 @@
 ---
 description: Code Quality guidelines
-globs:
-alwaysApply: true
+globs: apps/opik-backend/**/*
+alwaysApply: false
 ---
 
 # Code Quality Guidelines
diff --git a/apps/opik-backend/.cursor/rules/db_migration_script.mdc b/apps/opik-backend/.cursor/rules/db_migration_script.mdc
@@ -1,7 +1,7 @@
 ---
 description: Database migration script guidelines for Opik backend
 globs: **/migrations/*.sql
-alwaysApply: true
+alwaysApply: false
 ---
 
 # Database Migration Script Guidelines
diff --git a/apps/opik-backend/.cursor/rules/error_handling.mdc b/apps/opik-backend/.cursor/rules/error_handling.mdc
@@ -1,7 +1,7 @@
 ---
 description: Error handling best practices for Opik backend
 globs: **/*.java
-alwaysApply: true
+alwaysApply: false
 ---
 
 # Error Handling Guidelines
diff --git a/apps/opik-backend/.cursor/rules/general.mdc b/apps/opik-backend/.cursor/rules/general.mdc
@@ -1,7 +1,7 @@
 ---
 description: General guidelines for making changes in Opik backend
 globs: **/*.java
-alwaysApply: true
+alwaysApply: false
 ---
 
 # General Development Guidelines
diff --git a/apps/opik-backend/.cursor/rules/logging.mdc b/apps/opik-backend/.cursor/rules/logging.mdc
@@ -1,7 +1,7 @@
 ---
 description: Logging guidelines for Opik backend
 globs: **/*.java
-alwaysApply: true
+alwaysApply: false
 ---
 
 # Logging Guidelines
diff --git a/apps/opik-backend/.cursor/rules/mysql.mdc b/apps/opik-backend/.cursor/rules/mysql.mdc
@@ -1,7 +1,7 @@
 ---
 description: MySQL transaction usage guidelines for opik-backend
-globs:
-alwaysApply: true
+globs: apps/opik-backend/**/*
+alwaysApply: false
 ---
 # MySQL Transaction Guidelines
 
diff --git a/apps/opik-backend/.cursor/rules/tech_stack.mdc b/apps/opik-backend/.cursor/rules/tech_stack.mdc
@@ -1,7 +1,7 @@
 ---
 description: Tech Stack
-globs:
-alwaysApply: true
+globs: apps/opik-backend/**/*
+alwaysApply: false
 ---
 # Opik Java Backend Technology Stack
 
diff --git a/apps/opik-backend/.cursor/rules/testing.mdc b/apps/opik-backend/.cursor/rules/testing.mdc
@@ -1,7 +1,7 @@
 ---
 description: Testing
-globs:
-alwaysApply: true
+globs: apps/opik-backend/**/*
+alwaysApply: false
 ---
 # Testing Guidelines
 
diff --git a/apps/opik-frontend/.cursor/rules/accessibility-testing.mdc b/apps/opik-frontend/.cursor/rules/accessibility-testing.mdc
@@ -1,7 +1,7 @@
 ---
 description: Frontend accessibility guidelines and testing patterns
-globs: "**/*"
-alwaysApply: true
+globs: apps/opik-frontend/**/*
+alwaysApply: false
 ---
 
 # Accessibility & Testing Guidelines
diff --git a/apps/opik-frontend/.cursor/rules/api-data-fetching.mdc b/apps/opik-frontend/.cursor/rules/api-data-fetching.mdc
@@ -1,7 +1,7 @@
 ---
 description: Frontend API and data fetching patterns using React Query
-globs: "**/*"
-alwaysApply: true
+globs: apps/opik-frontend/**/*
+alwaysApply: false
 ---
 
 # API & Data Fetching Patterns
diff --git a/apps/opik-frontend/.cursor/rules/code-quality.mdc b/apps/opik-frontend/.cursor/rules/code-quality.mdc
@@ -1,7 +1,7 @@
 ---
 description: Frontend code quality standards, TypeScript patterns, and naming conventions
-globs: "**/*"
-alwaysApply: true
+globs: apps/opik-frontend/**/*
+alwaysApply: false
 ---
 
 # Frontend Code Quality Standards
diff --git a/apps/opik-frontend/.cursor/rules/forms.mdc b/apps/opik-frontend/.cursor/rules/forms.mdc
@@ -1,7 +1,7 @@
 ---
 description: Frontend form handling patterns using React Hook Form and Zod
-globs: "**/*"
-alwaysApply: true
+globs: apps/opik-frontend/**/*
+alwaysApply: false
 ---
 
 # Form Handling Patterns
diff --git a/apps/opik-frontend/.cursor/rules/frontend_rules.mdc b/apps/opik-frontend/.cursor/rules/frontend_rules.mdc
@@ -1,7 +1,7 @@
 ---
 description: Main frontend development guidelines - references detailed rules
-globs: "**/*"
-alwaysApply: true
+globs: apps/opik-frontend/**/*
+alwaysApply: false
 ---
 
 # Frontend Development Guidelines
diff --git a/apps/opik-frontend/.cursor/rules/performance.mdc b/apps/opik-frontend/.cursor/rules/performance.mdc
@@ -1,7 +1,7 @@
 ---
 description: Frontend performance optimization rules for React hooks and data processing
-globs: "**/*"
-alwaysApply: true
+globs: apps/opik-frontend/**/*
+alwaysApply: false
 ---
 
 # Frontend Performance Guidelines
diff --git a/apps/opik-frontend/.cursor/rules/state-management.mdc b/apps/opik-frontend/.cursor/rules/state-management.mdc
@@ -1,7 +1,7 @@
 ---
 description: Frontend state management patterns using Zustand and local storage
-globs: "**/*"
-alwaysApply: true
+globs: apps/opik-frontend/**/*
+alwaysApply: false
 ---
 
 # State Management Patterns
diff --git a/apps/opik-frontend/.cursor/rules/tech-stack.mdc b/apps/opik-frontend/.cursor/rules/tech-stack.mdc
@@ -1,7 +1,7 @@
 ---
 description: Frontend technology stack and project structure guidelines
-globs: "**/*"
-alwaysApply: true
+globs: apps/opik-frontend/**/*
+alwaysApply: false
 ---
 
 # Frontend Technology Stack & Architecture
diff --git a/apps/opik-frontend/.cursor/rules/ui-components.mdc b/apps/opik-frontend/.cursor/rules/ui-components.mdc
@@ -1,7 +1,7 @@
 ---
 description: Frontend UI component patterns and design system guidelines
-globs: "**/*"
-alwaysApply: true
+globs: apps/opik-frontend/**/*
+alwaysApply: false
 ---
 
 # UI Components & Design System
diff --git a/apps/opik-frontend/.cursor/rules/unit-testing.mdc b/apps/opik-frontend/.cursor/rules/unit-testing.mdc
@@ -1,7 +1,7 @@
 ---
 description: Unit testing guidelines and patterns for complex cases using Vitest
-globs: "**/*"
-alwaysApply: true
+globs: apps/opik-frontend/**/*
+alwaysApply: false
 ---
 
 # Unit Testing Guidelines
diff --git a/sdks/python/.cursor/rules/api-design.mdc b/sdks/python/.cursor/rules/api-design.mdc
@@ -1,7 +1,7 @@
 ---
 description: API design principles and consistency guidelines for the Python SDK
 globs: sdks/python/src/opik/**/*
-alwaysApply: true
+alwaysApply: false
 ---
 # Python SDK API Design Guidelines
 
diff --git a/sdks/python/.cursor/rules/architecture.mdc b/sdks/python/.cursor/rules/architecture.mdc
@@ -1,7 +1,7 @@
 ---
 description: Core library architecture and design patterns for the Python SDK
 globs: sdks/python/src/opik/**/*
-alwaysApply: true
+alwaysApply: false
 ---
 # Python SDK Architecture Guidelines
 
diff --git a/sdks/python/.cursor/rules/code-structure.mdc b/sdks/python/.cursor/rules/code-structure.mdc
@@ -1,7 +1,7 @@
 ---
 description: Import organization and access control guidelines for the Python SDK
 globs: sdks/python/src/opik/**/*
-alwaysApply: true
+alwaysApply: false
 ---
 # Python SDK Code Structure Guidelines
 
diff --git a/sdks/python/.cursor/rules/dependencies.mdc b/sdks/python/.cursor/rules/dependencies.mdc
@@ -1,7 +1,7 @@
 ---
 description: Dependency management and tech stack guidelines for the Python SDK
 globs: sdks/python/src/opik/**/*
-alwaysApply: true
+alwaysApply: false
 ---
 # Python SDK Dependency Management Guidelines
 
diff --git a/sdks/python/.cursor/rules/design-principles.mdc b/sdks/python/.cursor/rules/design-principles.mdc
@@ -1,7 +1,7 @@
 ---
 description: SOLID principles and architectural design guidelines for the Python SDK
 globs: sdks/python/src/opik/**/*
-alwaysApply: true
+alwaysApply: false
 ---
 # Python SDK Design Principles Guidelines
 
diff --git a/sdks/python/.cursor/rules/documentation-style.mdc b/sdks/python/.cursor/rules/documentation-style.mdc
@@ -1,7 +1,7 @@
 ---
 description: Documentation standards and code style guidelines for the Python SDK
 globs: sdks/python/src/opik/**/*
-alwaysApply: true
+alwaysApply: false
 ---
 # Python SDK Documentation and Style Guidelines
 
diff --git a/sdks/python/.cursor/rules/error-handling.mdc b/sdks/python/.cursor/rules/error-handling.mdc
@@ -1,7 +1,7 @@
 ---
 description: Exception handling and error management patterns for the Python SDK
 globs: sdks/python/src/opik/**/*
-alwaysApply: true
+alwaysApply: false
 ---
 # Python SDK Error Handling Guidelines
 
diff --git a/sdks/python/.cursor/rules/logging.mdc b/sdks/python/.cursor/rules/logging.mdc
@@ -1,7 +1,7 @@
 ---
 description: Structured logging patterns and best practices for the Python SDK
 globs: sdks/python/src/opik/**/*
-alwaysApply: true
+alwaysApply: false
 ---
 # Python SDK Logging Guidelines
 
diff --git a/sdks/python/.cursor/rules/method-refactoring-patterns.mdc b/sdks/python/.cursor/rules/method-refactoring-patterns.mdc
@@ -1,7 +1,7 @@
 ---
 description: Patterns for identifying and refactoring methods to improve code quality and maintainability
-globs:
-alwaysApply: true
+globs: sdks/python/src/opik/**/*
+alwaysApply: false
 ---
 # Method Refactoring Patterns
 
diff --git a/sdks/python/.cursor/rules/test-best-practices.mdc b/sdks/python/.cursor/rules/test-best-practices.mdc
@@ -1,7 +1,7 @@
 ---
 description: Test naming conventions and performance guidelines for the Python SDK
 globs: sdks/python/tests/**/*
-alwaysApply: true
+alwaysApply: false
 ---
 # Python SDK Test Best Practices Guidelines
 
diff --git a/sdks/python/.cursor/rules/test-implementation.mdc b/sdks/python/.cursor/rules/test-implementation.mdc
@@ -1,7 +1,7 @@
 ---
 description: Test fixtures, utilities, and implementation patterns for the Python SDK
 globs: sdks/python/tests/**/*
-alwaysApply: true
+alwaysApply: false
 ---
 # Python SDK Test Implementation Guidelines
 
diff --git a/sdks/python/.cursor/rules/test-organization.mdc b/sdks/python/.cursor/rules/test-organization.mdc
@@ -1,7 +1,7 @@
 ---
 description: Test structure, location, and organization guidelines for the Python SDK
 globs: sdks/python/tests/**/*
-alwaysApply: true
+alwaysApply: false
 ---
 # Python SDK Test Organization Guidelines
 
diff --git a/sdks/typescript/.cursor/rules/architecture.mdc b/sdks/typescript/.cursor/rules/architecture.mdc
@@ -1,7 +1,7 @@
 ---
 globs: sdks/typescript/src/**/*.ts
 description: Authoritative architecture rules for the TypeScript SDK. Keep these aligned with real code.
-alwaysApply: true
+alwaysApply: false
 ---
 
 ## Architecture overview
diff --git a/sdks/typescript/.cursor/rules/code-structure.mdc b/sdks/typescript/.cursor/rules/code-structure.mdc
@@ -1,7 +1,7 @@
 ---
 globs: sdks/typescript/src/**/*.ts
 description: Code structure conventions and public API boundaries for the TS SDK
-alwaysApply: true
+alwaysApply: false
 ---
 
 ## Directory map (authoritative)
diff --git a/sdks/typescript/.cursor/rules/integrations.mdc b/sdks/typescript/.cursor/rules/integrations.mdc
@@ -1,7 +1,7 @@
 ---
 globs: sdks/typescript/src/opik/integrations/**/*.ts
 description: Guidance for Opik TypeScript integrations (OpenAI, LangChain, Vercel)
-alwaysApply: true
+alwaysApply: false
 ---
 
 ## Integrations
diff --git a/sdks/typescript/.cursor/rules/logging.mdc b/sdks/typescript/.cursor/rules/logging.mdc
@@ -1,7 +1,7 @@
 ---
 globs: sdks/typescript/src/**/*.ts
 description: Logging practices for the TypeScript SDK
-alwaysApply: true
+alwaysApply: false
 ---
 
 ## Logging
diff --git a/sdks/typescript/.cursor/rules/overview.mdc b/sdks/typescript/.cursor/rules/overview.mdc
@@ -1,7 +1,7 @@
 ---
 globs: sdks/typescript/src/**/*.ts
 description: High-level overview of the Opik TypeScript SDK and how to navigate it
-alwaysApply: true
+alwaysApply: false
 ---
 
 ## Opik TypeScript SDK Overview
diff --git a/sdks/typescript/.cursor/rules/test-best-practices.mdc b/sdks/typescript/.cursor/rules/test-best-practices.mdc
@@ -1,7 +1,7 @@
 ---
-globs: sdks/typescript/**/*.{ts,tsx}
+globs: sdks/typescript/**/*
 description: Testing patterns for the Opik TypeScript SDK (Vitest)
-alwaysApply: true
+alwaysApply: false
 ---
 
 ## Testing Best Practices (TypeScript SDK)
PATCH

echo "Gold patch applied."
