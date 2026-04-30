#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "description: Generates Angular 17+ standalone components, configures advanced ro" "skills/angular-architect/SKILL.md" && grep -qF "2. **Model resources** \u2014 Identify resources, relationships, and operations; sket" "skills/api-designer/SKILL.md" && grep -qF "description: Use when designing new high-level system architecture, reviewing ex" "skills/architecture-designer/SKILL.md" && grep -qF "description: Integrates with Atlassian products to manage project tracking and d" "skills/atlassian-mcp/SKILL.md" && grep -qF "description: Designs chaos experiments, creates failure injection frameworks, an" "skills/chaos-engineer/SKILL.md" && grep -qF "description: Use when building CLI tools, implementing argument parsing, or addi" "skills/cli-developer/SKILL.md" && grep -qF "description: Designs cloud architectures, creates migration plans, generates cos" "skills/cloud-architect/SKILL.md" && grep -qF "description: Generates, formats, and validates technical documentation \u2014 includi" "skills/code-documenter/SKILL.md" && grep -qF "description: Analyzes code diffs and files to identify bugs, security vulnerabil" "skills/code-reviewer/SKILL.md" && grep -qF "description: Writes, optimizes, and debugs C++ applications using modern C++20/2" "skills/cpp-pro/SKILL.md" && grep -qF "description: \"Use when building C# applications with .NET 8+, ASP.NET Core APIs," "skills/csharp-developer/SKILL.md" && grep -qF "description: Optimizes database queries and improves performance across PostgreS" "skills/database-optimizer/SKILL.md" && grep -qF "description: Parses error messages, traces execution flow through stack traces, " "skills/debugging-wizard/SKILL.md" && grep -qF "description: Creates Dockerfiles, configures CI/CD pipelines, writes Kubernetes " "skills/devops-engineer/SKILL.md" && grep -qF "description: \"Use when building Django web applications or REST APIs with Django" "skills/django-expert/SKILL.md" && grep -qF "5. **Test** \u2014 Write comprehensive tests with xUnit and integration testing; run " "skills/dotnet-core-expert/SKILL.md" && grep -qF "description: Use when developing firmware for microcontrollers, implementing RTO" "skills/embedded-systems/SKILL.md" && grep -qF "description: \"Use when building high-performance async Python APIs with FastAPI " "skills/fastapi-expert/SKILL.md" && grep -qF "description: Conducts structured requirements workshops to produce feature speci" "skills/feature-forge/SKILL.md" && grep -qF "description: \"Use when fine-tuning LLMs, training custom models, or adapting fou" "skills/fine-tuning-expert/SKILL.md" && grep -qF "| Jank / dropped frames | Expensive `build()` calls, uncached widgets, heavy mai" "skills/flutter-expert/SKILL.md" && grep -qF "description: Builds security-focused full-stack web applications by implementing" "skills/fullstack-guardian/SKILL.md" && grep -qF "description: \"Use when building game systems, implementing Unity/Unreal Engine f" "skills/game-developer/SKILL.md" && grep -qF "description: Implements concurrent Go patterns using goroutines and channels, de" "skills/golang-pro/SKILL.md" && grep -qF "- _If composition fails:_ review entity `@key` directives, check for missing or " "skills/graphql-architect/SKILL.md" && grep -qF "description: Use when building, configuring, or debugging enterprise Java applic" "skills/java-architect/SKILL.md" && grep -qF "description: Writes, debugs, and refactors JavaScript code using modern ES2023+ " "skills/javascript-pro/SKILL.md" && grep -qF "description: Provides idiomatic Kotlin implementation patterns including corouti" "skills/kotlin-specialist/SKILL.md" && grep -qF "description: Use when deploying or managing Kubernetes workloads. Invoke to crea" "skills/kubernetes-specialist/SKILL.md" && grep -qF "description: Build and configure Laravel 10+ applications, including creating El" "skills/laravel-specialist/SKILL.md" && grep -qF "description: Designs incremental migration strategies, identifies service bounda" "skills/legacy-modernizer/SKILL.md" && grep -qF "5. **Test** \u2014 Run `npx @modelcontextprotocol/inspector` to verify protocol compl" "skills/mcp-developer/SKILL.md" && grep -qF "description: Designs distributed system architectures, decomposes monoliths into" "skills/microservices-architect/SKILL.md" && grep -qF "description: \"Designs and implements production-grade ML pipeline infrastructure" "skills/ml-pipeline/SKILL.md" && grep -qF "description: Configures monitoring systems, implements structured logging pipeli" "skills/monitoring-expert/SKILL.md" && grep -qF "description: Creates and configures NestJS modules, controllers, services, DTOs," "skills/nestjs-expert/SKILL.md" && grep -qF "description: \"Use when building Next.js 14+ applications with App Router, server" "skills/nextjs-developer/SKILL.md" && grep -qF "description: Performs pandas DataFrame operations for data analysis, manipulatio" "skills/pandas-pro/SKILL.md" && grep -qF "description: Use when building PHP applications with modern PHP 8.3+ features, L" "skills/php-pro/SKILL.md" && grep -qF "description: \"Use when writing E2E tests with Playwright, setting up test infras" "skills/playwright-expert/SKILL.md" && grep -qF "5. **Monitor and maintain** \u2014 Track VACUUM, bloat, and autovacuum via `pg_stat` " "skills/postgres-pro/SKILL.md" && grep -qF "description: Writes, refactors, and evaluates prompts for LLMs \u2014 generating opti" "skills/prompt-engineer/SKILL.md" && grep -qF "description: Use when building Python 3.11+ applications requiring type safety, " "skills/python-pro/SKILL.md" && grep -qF "description: Designs and implements production-grade RAG systems by chunking doc" "skills/rag-architect/SKILL.md" && grep -qF "description: Rails 7+ specialist that optimizes Active Record queries with inclu" "skills/rails-expert/SKILL.md" && grep -qF "description: Use when building React 18+ applications in .jsx or .tsx files, Nex" "skills/react-expert/SKILL.md" && grep -qF "description: Builds, optimizes, and debugs cross-platform mobile applications wi" "skills/react-native-expert/SKILL.md" && grep -qF "description: Writes, reviews, and debugs idiomatic Rust code with memory safety " "skills/rust-engineer/SKILL.md" && grep -qF "description: Writes and debugs Apex code, builds Lightning Web Components, optim" "skills/salesforce-developer/SKILL.md" && grep -qF "description: Use when implementing authentication/authorization, securing user i" "skills/secure-code-guardian/SKILL.md" && grep -qF "description: Identifies security vulnerabilities, generates structured audit rep" "skills/security-reviewer/SKILL.md" && grep -qF "description: Builds and debugs Shopify themes (.liquid files, theme.json, sectio" "skills/shopify-expert/SKILL.md" && grep -qF "description: Use when writing Spark jobs, debugging performance issues, or confi" "skills/spark-engineer/SKILL.md" && grep -qF "description: \"Reverse-engineering specialist that extracts specifications from e" "skills/spec-miner/SKILL.md" && grep -qF "description: Generates Spring Boot 3.x configurations, creates REST controllers," "skills/spring-boot-engineer/SKILL.md" && grep -qF "description: Optimizes SQL queries, designs database schemas, and troubleshoots " "skills/sql-pro/SKILL.md" && grep -qF "description: Defines service level objectives, creates error budget policies, de" "skills/sre-engineer/SKILL.md" && grep -qF "description: Builds iOS/macOS/watchOS/tvOS applications, implements SwiftUI view" "skills/swift-expert/SKILL.md" && grep -qF "description: Use when implementing infrastructure as code with Terraform across " "skills/terraform-engineer/SKILL.md" && grep -qF "description: Generates test files, creates mocking strategies, analyzes code cov" "skills/test-master/SKILL.md" && grep -qF "description: Implements advanced TypeScript type systems, creates custom type gu" "skills/typescript-pro/SKILL.md" && grep -qF "description: Creates Vue 3 components, builds vanilla JS composables, configures" "skills/vue-expert-js/SKILL.md" && grep -qF "description: Builds Vue 3 components with Composition API patterns, configures N" "skills/vue-expert/SKILL.md" && grep -qF "4. **Validate locally** \u2014 Test connection handling, auth, and room behavior befo" "skills/websocket-engineer/SKILL.md" && grep -qF "description: Develops custom WordPress themes and plugins, creates and registers" "skills/wordpress-pro/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/angular-architect/SKILL.md b/skills/angular-architect/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: angular-architect
-description: Use when building Angular 17+ applications with standalone components or signals. Invoke for enterprise apps, RxJS patterns, NgRx state management, performance optimization, advanced routing.
+description: Generates Angular 17+ standalone components, configures advanced routing with lazy loading and guards, implements NgRx state management, applies RxJS patterns, and optimizes bundle performance. Use when building Angular 17+ applications with standalone components or signals, setting up NgRx stores, establishing RxJS reactive patterns, performance tuning, or writing Angular tests for enterprise apps.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,27 +17,14 @@ metadata:
 
 Senior Angular architect specializing in Angular 17+ with standalone components, signals, and enterprise-grade application development.
 
-## Role Definition
-
-You are a senior Angular engineer with 10+ years of enterprise application development experience. You specialize in Angular 17+ with standalone components, signals, advanced RxJS patterns, NgRx state management, and micro-frontend architectures. You build scalable, performant, type-safe applications with comprehensive testing.
-
-## When to Use This Skill
-
-- Building Angular 17+ applications with standalone components
-- Implementing reactive patterns with RxJS and signals
-- Setting up NgRx state management
-- Creating advanced routing with lazy loading and guards
-- Optimizing Angular application performance
-- Writing comprehensive Angular tests
-
 ## Core Workflow
 
 1. **Analyze requirements** - Identify components, state needs, routing architecture
 2. **Design architecture** - Plan standalone components, signal usage, state flow
 3. **Implement features** - Build components with OnPush strategy and reactive patterns
-4. **Manage state** - Setup NgRx store, effects, selectors as needed
-5. **Optimize** - Apply performance best practices and bundle optimization
-6. **Test** - Write unit and integration tests with TestBed
+4. **Manage state** - Setup NgRx store, effects, selectors as needed; verify store hydration and action flow with Redux DevTools before proceeding
+5. **Optimize** - Apply performance best practices and bundle optimization; run `ng build --configuration production` to verify bundle size and flag regressions
+6. **Test** - Write unit and integration tests with TestBed; verify >85% coverage threshold is met
 
 ## Reference Guide
 
@@ -51,6 +38,88 @@ Load detailed guidance based on context:
 | Routing | `references/routing.md` | Router config, guards, lazy loading, resolvers |
 | Testing | `references/testing.md` | TestBed, component tests, service tests |
 
+## Key Patterns
+
+### Standalone Component with OnPush and Signals
+
+```typescript
+import { ChangeDetectionStrategy, Component, computed, input, output, signal } from '@angular/core';
+import { CommonModule } from '@angular/common';
+
+@Component({
+  selector: 'app-user-card',
+  standalone: true,
+  imports: [CommonModule],
+  changeDetection: ChangeDetectionStrategy.OnPush,
+  template: `
+    <div class="user-card">
+      <h2>{{ fullName() }}</h2>
+      <button (click)="onSelect()">Select</button>
+    </div>
+  `,
+})
+export class UserCardComponent {
+  firstName = input.required<string>();
+  lastName = input.required<string>();
+  selected = output<string>();
+
+  fullName = computed(() => `${this.firstName()} ${this.lastName()}`);
+
+  onSelect(): void {
+    this.selected.emit(this.fullName());
+  }
+}
+```
+
+### RxJS Subscription Management with `takeUntilDestroyed`
+
+```typescript
+import { Component, OnInit, inject } from '@angular/core';
+import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
+import { UserService } from './user.service';
+
+@Component({ selector: 'app-users', standalone: true, template: `...` })
+export class UsersComponent implements OnInit {
+  private userService = inject(UserService);
+  // DestroyRef is captured at construction time for use in ngOnInit
+  private destroyRef = inject(DestroyRef);
+
+  ngOnInit(): void {
+    this.userService.getUsers()
+      .pipe(takeUntilDestroyed(this.destroyRef))
+      .subscribe({
+        next: (users) => { /* handle */ },
+        error: (err) => console.error('Failed to load users', err),
+      });
+  }
+}
+```
+
+### NgRx Action / Reducer / Selector
+
+```typescript
+// actions
+export const loadUsers = createAction('[Users] Load Users');
+export const loadUsersSuccess = createAction('[Users] Load Users Success', props<{ users: User[] }>());
+export const loadUsersFailure = createAction('[Users] Load Users Failure', props<{ error: string }>());
+
+// reducer
+export interface UsersState { users: User[]; loading: boolean; error: string | null; }
+const initialState: UsersState = { users: [], loading: false, error: null };
+
+export const usersReducer = createReducer(
+  initialState,
+  on(loadUsers, (state) => ({ ...state, loading: true, error: null })),
+  on(loadUsersSuccess, (state, { users }) => ({ ...state, users, loading: false })),
+  on(loadUsersFailure, (state, { error }) => ({ ...state, error, loading: false })),
+);
+
+// selectors
+export const selectUsersState = createFeatureSelector<UsersState>('users');
+export const selectAllUsers = createSelector(selectUsersState, (s) => s.users);
+export const selectUsersLoading = createSelector(selectUsersState, (s) => s.loading);
+```
+
 ## Constraints
 
 ### MUST DO
@@ -59,17 +128,17 @@ Load detailed guidance based on context:
 - Use OnPush change detection strategy
 - Use strict TypeScript configuration
 - Implement proper error handling in RxJS streams
-- Use trackBy functions in *ngFor loops
+- Use `trackBy` functions in `*ngFor` loops
 - Write tests with >85% coverage
 - Follow Angular style guide
 
 ### MUST NOT DO
 - Use NgModule-based components (except when required for compatibility)
-- Forget to unsubscribe from observables
+- Forget to unsubscribe from observables (use `takeUntilDestroyed` or `async` pipe)
 - Use async operations without proper error handling
 - Skip accessibility attributes
 - Expose sensitive data in client-side code
-- Use any type without justification
+- Use `any` type without justification
 - Mutate state directly in NgRx
 - Skip unit tests for critical logic
 
@@ -81,7 +150,3 @@ When implementing Angular features, provide:
 3. State management files if using NgRx
 4. Test file with comprehensive test cases
 5. Brief explanation of architectural decisions
-
-## Knowledge Reference
-
-Angular 17+, standalone components, signals, computed signals, effect(), RxJS 7+, NgRx, Angular Router, Reactive Forms, Angular CDK, OnPush strategy, lazy loading, bundle optimization, Jest/Jasmine, Testing Library
diff --git a/skills/api-designer/SKILL.md b/skills/api-designer/SKILL.md
@@ -15,30 +15,16 @@ metadata:
 
 # API Designer
 
-Senior API architect with expertise in designing scalable, developer-friendly REST and GraphQL APIs with comprehensive OpenAPI specifications.
-
-## Role Definition
-
-You are a senior API designer with 10+ years of experience creating intuitive, scalable API architectures. You specialize in REST design patterns, OpenAPI 3.1 specifications, GraphQL schemas, and creating APIs that developers love to use while ensuring performance, security, and maintainability.
-
-## When to Use This Skill
-
-- Designing new REST or GraphQL APIs
-- Creating OpenAPI 3.1 specifications
-- Modeling resources and relationships
-- Implementing API versioning strategies
-- Designing pagination and filtering
-- Standardizing error responses
-- Planning authentication flows
-- Documenting API contracts
+Senior API architect specializing in REST and GraphQL APIs with comprehensive OpenAPI 3.1 specifications.
 
 ## Core Workflow
 
-1. **Analyze domain** - Understand business requirements, data models, client needs
-2. **Model resources** - Identify resources, relationships, operations
-3. **Design endpoints** - Define URI patterns, HTTP methods, request/response schemas
-4. **Specify contract** - Create OpenAPI 3.1 spec with complete documentation
-5. **Plan evolution** - Design versioning, deprecation, backward compatibility
+1. **Analyze domain** — Understand business requirements, data models, and client needs
+2. **Model resources** — Identify resources, relationships, and operations; sketch entity diagram before writing any spec
+3. **Design endpoints** — Define URI patterns, HTTP methods, request/response schemas
+4. **Specify contract** — Create OpenAPI 3.1 spec; validate before proceeding: `npx @redocly/cli lint openapi.yaml`
+5. **Mock and verify** — Spin up a mock server to test contracts: `npx @stoplight/prism-cli mock openapi.yaml`
+6. **Plan evolution** — Design versioning, deprecation, and backward-compatibility strategy
 
 ## Reference Guide
 
@@ -56,10 +42,10 @@ Load detailed guidance based on context:
 
 ### MUST DO
 - Follow REST principles (resource-oriented, proper HTTP methods)
-- Use consistent naming conventions (snake_case or camelCase)
+- Use consistent naming conventions (snake_case or camelCase — pick one, apply everywhere)
 - Include comprehensive OpenAPI 3.1 specification
-- Design proper error responses with actionable messages
-- Implement pagination for collection endpoints
+- Design proper error responses with actionable messages (RFC 7807)
+- Implement pagination for all collection endpoints
 - Version APIs with clear deprecation policies
 - Document authentication and authorization
 - Provide request/response examples
@@ -69,21 +55,162 @@ Load detailed guidance based on context:
 - Return inconsistent response structures
 - Skip error code documentation
 - Ignore HTTP status code semantics
-- Design APIs without versioning strategy
-- Expose implementation details in API
-- Create breaking changes without migration path
+- Design APIs without a versioning strategy
+- Expose implementation details in the API surface
+- Create breaking changes without a migration path
 - Omit rate limiting considerations
 
-## Output Templates
+## Templates
+
+### OpenAPI 3.1 Resource Endpoint (copy-paste starter)
 
-When designing APIs, provide:
-1. Resource model and relationships
-2. Endpoint specifications with URIs and methods
-3. OpenAPI 3.1 specification (YAML or JSON)
+```yaml
+openapi: "3.1.0"
+info:
+  title: Example API
+  version: "1.0.0"
+paths:
+  /users:
+    get:
+      summary: List users
+      operationId: listUsers
+      tags: [Users]
+      parameters:
+        - name: cursor
+          in: query
+          schema: { type: string }
+          description: Opaque cursor for pagination
+        - name: limit
+          in: query
+          schema: { type: integer, default: 20, maximum: 100 }
+      responses:
+        "200":
+          description: Paginated list of users
+          content:
+            application/json:
+              schema:
+                type: object
+                required: [data, pagination]
+                properties:
+                  data:
+                    type: array
+                    items: { $ref: "#/components/schemas/User" }
+                  pagination:
+                    $ref: "#/components/schemas/CursorPage"
+        "400": { $ref: "#/components/responses/BadRequest" }
+        "401": { $ref: "#/components/responses/Unauthorized" }
+        "429": { $ref: "#/components/responses/TooManyRequests" }
+  /users/{id}:
+    get:
+      summary: Get a user
+      operationId: getUser
+      tags: [Users]
+      parameters:
+        - name: id
+          in: path
+          required: true
+          schema: { type: string, format: uuid }
+      responses:
+        "200":
+          description: User found
+          content:
+            application/json:
+              schema: { $ref: "#/components/schemas/User" }
+        "404": { $ref: "#/components/responses/NotFound" }
+
+components:
+  schemas:
+    User:
+      type: object
+      required: [id, email, created_at]
+      properties:
+        id:    { type: string, format: uuid, readOnly: true }
+        email: { type: string, format: email }
+        name:  { type: string }
+        created_at: { type: string, format: date-time, readOnly: true }
+
+    CursorPage:
+      type: object
+      required: [next_cursor, has_more]
+      properties:
+        next_cursor: { type: string, nullable: true }
+        has_more:    { type: boolean }
+
+    Problem:                       # RFC 7807 Problem Details
+      type: object
+      required: [type, title, status]
+      properties:
+        type:     { type: string, format: uri, example: "https://api.example.com/errors/validation-error" }
+        title:    { type: string, example: "Validation Error" }
+        status:   { type: integer, example: 400 }
+        detail:   { type: string, example: "The 'email' field must be a valid email address." }
+        instance: { type: string, format: uri, example: "/users/req-abc123" }
+
+  responses:
+    BadRequest:
+      description: Invalid request parameters
+      content:
+        application/problem+json:
+          schema: { $ref: "#/components/schemas/Problem" }
+    Unauthorized:
+      description: Missing or invalid authentication
+      content:
+        application/problem+json:
+          schema: { $ref: "#/components/schemas/Problem" }
+    NotFound:
+      description: Resource not found
+      content:
+        application/problem+json:
+          schema: { $ref: "#/components/schemas/Problem" }
+    TooManyRequests:
+      description: Rate limit exceeded
+      headers:
+        Retry-After: { schema: { type: integer } }
+      content:
+        application/problem+json:
+          schema: { $ref: "#/components/schemas/Problem" }
+
+  securitySchemes:
+    BearerAuth:
+      type: http
+      scheme: bearer
+      bearerFormat: JWT
+
+security:
+  - BearerAuth: []
+```
+
+### RFC 7807 Error Response (copy-paste)
+
+```json
+{
+  "type": "https://api.example.com/errors/validation-error",
+  "title": "Validation Error",
+  "status": 422,
+  "detail": "The 'email' field must be a valid email address.",
+  "instance": "/users/req-abc123",
+  "errors": [
+    { "field": "email", "message": "Must be a valid email address." }
+  ]
+}
+```
+
+- Always use `Content-Type: application/problem+json` for error responses.
+- `type` must be a stable, documented URI — never a generic string.
+- `detail` must be human-readable and actionable.
+- Extend with `errors[]` for field-level validation failures.
+
+## Output Checklist
+
+When delivering an API design, provide:
+1. Resource model and relationships (diagram or table)
+2. Endpoint specifications with URIs and HTTP methods
+3. OpenAPI 3.1 specification (YAML)
 4. Authentication and authorization flows
-5. Error response catalog
+5. Error response catalog (all 4xx/5xx with `type` URIs)
 6. Pagination and filtering patterns
 7. Versioning and deprecation strategy
+8. Validation result: `npx @redocly/cli lint openapi.yaml` passes with no errors
 
 ## Knowledge Reference
 
diff --git a/skills/architecture-designer/SKILL.md b/skills/architecture-designer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: architecture-designer
-description: Use when designing new system architecture, reviewing existing designs, or making architectural decisions. Invoke for system design, architecture review, design patterns, ADRs, scalability planning.
+description: Use when designing new high-level system architecture, reviewing existing designs, or making architectural decisions. Invoke to create architecture diagrams, write Architecture Decision Records (ADRs), evaluate technology trade-offs, design component interactions, and plan for scalability. Use for system design, architecture review, microservices structuring, ADR authoring, scalability planning, and infrastructure pattern selection — distinct from code-level design patterns or database-only design tasks.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -19,7 +19,7 @@ Senior software architect specializing in system design, design patterns, and ar
 
 ## Role Definition
 
-You are a principal architect with 15+ years of experience designing scalable systems. You specialize in distributed systems, cloud architecture, and making pragmatic trade-offs. You document decisions with ADRs and consider long-term maintainability.
+You are a principal architect with 15+ years of experience designing scalable, distributed systems. You make pragmatic trade-offs, document decisions with ADRs, and prioritize long-term maintainability.
 
 ## When to Use This Skill
 
@@ -32,11 +32,11 @@ You are a principal architect with 15+ years of experience designing scalable sy
 
 ## Core Workflow
 
-1. **Understand requirements** - Functional, non-functional, constraints
-2. **Identify patterns** - Match requirements to architectural patterns
-3. **Design** - Create architecture with trade-offs documented
-4. **Document** - Write ADRs for key decisions
-5. **Review** - Validate with stakeholders
+1. **Understand requirements** — Gather functional, non-functional, and constraint requirements. _Verify full requirements coverage before proceeding._
+2. **Identify patterns** — Match requirements to architectural patterns (see Reference Guide).
+3. **Design** — Create architecture with trade-offs explicitly documented; produce a diagram.
+4. **Document** — Write ADRs for all key decisions.
+5. **Review** — Validate with stakeholders. _If review fails, return to step 3 with recorded feedback._
 
 ## Reference Guide
 
@@ -71,11 +71,47 @@ Load detailed guidance based on context:
 
 When designing architecture, provide:
 1. Requirements summary (functional + non-functional)
-2. High-level architecture diagram
-3. Key decisions with trade-offs (ADR format)
+2. High-level architecture diagram (Mermaid preferred — see example below)
+3. Key decisions with trade-offs (ADR format — see example below)
 4. Technology recommendations with rationale
 5. Risks and mitigation strategies
 
-## Knowledge Reference
+### Architecture Diagram (Mermaid)
+
+```mermaid
+graph TD
+    Client["Client (Web/Mobile)"] --> Gateway["API Gateway"]
+    Gateway --> AuthSvc["Auth Service"]
+    Gateway --> OrderSvc["Order Service"]
+    OrderSvc --> DB[("Orders DB\n(PostgreSQL)")]
+    OrderSvc --> Queue["Message Queue\n(RabbitMQ)"]
+    Queue --> NotifySvc["Notification Service"]
+```
+
+### ADR Example
+
+```markdown
+# ADR-001: Use PostgreSQL for Order Storage
+
+## Status
+Accepted
+
+## Context
+The Order Service requires ACID-compliant transactions and complex relational queries
+across orders, line items, and customers.
+
+## Decision
+Use PostgreSQL as the primary datastore for the Order Service.
+
+## Alternatives Considered
+- **MongoDB** — flexible schema, but lacks strong ACID guarantees across documents.
+- **DynamoDB** — excellent scalability, but complex query patterns require denormalization.
+
+## Consequences
+- Positive: Strong consistency, mature tooling, complex query support.
+- Negative: Vertical scaling limits; horizontal sharding adds operational complexity.
+
+## Trade-offs
+Consistency and query flexibility are prioritised over unlimited horizontal write scalability.
+```
 
-Distributed systems, microservices, event-driven architecture, CQRS, DDD, CAP theorem, cloud platforms (AWS, GCP, Azure), containers, Kubernetes, message queues, caching, database design
diff --git a/skills/atlassian-mcp/SKILL.md b/skills/atlassian-mcp/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: atlassian-mcp
-description: Use when querying Jira issues, searching Confluence pages, creating tickets, updating documentation, or integrating Atlassian tools via MCP protocol.
+description: Integrates with Atlassian products to manage project tracking and documentation via MCP protocol. Use when querying Jira issues with JQL filters, creating and updating tickets with custom fields, searching or editing Confluence pages with CQL, managing sprints and backlogs, setting up MCP server authentication, syncing documentation, or debugging Atlassian API integrations.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,12 +15,6 @@ metadata:
 
 # Atlassian MCP Expert
 
-Senior integration specialist with deep expertise in connecting Jira, Confluence, and other Atlassian tools to AI systems via Model Context Protocol (MCP).
-
-## Role Definition
-
-You are an expert in Atlassian MCP integration with mastery of both official and open-source MCP servers, JQL/CQL query languages, OAuth 2.0 authentication, and production deployment patterns. You build robust workflows that automate issue triage, documentation sync, sprint planning, and cross-tool integration while respecting permissions and maintaining security.
-
 ## When to Use This Skill
 
 - Querying Jira issues with JQL filters
@@ -36,9 +30,10 @@ You are an expert in Atlassian MCP integration with mastery of both official and
 
 1. **Select server** - Choose official cloud, open-source, or self-hosted MCP server
 2. **Authenticate** - Configure OAuth 2.1, API tokens, or PAT credentials
-3. **Design queries** - Write JQL for Jira, CQL for Confluence, test filters
+3. **Design queries** - Write JQL for Jira, CQL for Confluence; validate with `maxResults=1` before full execution
 4. **Implement workflow** - Build tool calls, handle pagination, error recovery
-5. **Deploy** - Configure IDE integration, test permissions, monitor rate limits
+5. **Verify permissions** - Confirm required scopes with a read-only probe before any write or bulk operation
+6. **Deploy** - Configure IDE integration, test permissions, monitor rate limits
 
 ## Reference Guide
 
@@ -52,17 +47,62 @@ Load detailed guidance based on context:
 | Authentication | `references/authentication-patterns.md` | OAuth 2.0, API tokens, permission scopes |
 | Common Workflows | `references/common-workflows.md` | Issue triage, doc sync, sprint automation |
 
+## Quick-Start Examples
+
+### JQL Query Samples
+```
+# Open issues assigned to current user in a sprint
+project = PROJ AND status = "In Progress" AND assignee = currentUser() ORDER BY priority DESC
+
+# Unresolved bugs created in the last 7 days
+project = PROJ AND issuetype = Bug AND status != Done AND created >= -7d ORDER BY created DESC
+
+# Validate before bulk: test with maxResults=1 first
+project = PROJ AND sprint in openSprints() AND status = Open ORDER BY created DESC
+```
+
+### CQL Query Samples
+```
+# Find pages updated in a specific space recently
+space = "ENG" AND type = page AND lastModified >= "2024-01-01" ORDER BY lastModified DESC
+
+# Search page text for a keyword
+space = "ENG" AND type = page AND text ~ "deployment runbook"
+```
+
+### Minimal MCP Server Configuration
+```json
+{
+  "mcpServers": {
+    "atlassian": {
+      "command": "npx",
+      "args": ["-y", "@sooperset/mcp-atlassian"],
+      "env": {
+        "JIRA_URL": "https://your-domain.atlassian.net",
+        "JIRA_EMAIL": "user@example.com",
+        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}",
+        "CONFLUENCE_URL": "https://your-domain.atlassian.net/wiki",
+        "CONFLUENCE_EMAIL": "user@example.com",
+        "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}"
+      }
+    }
+  }
+}
+```
+> **Note:** Always load `JIRA_API_TOKEN` and `CONFLUENCE_API_TOKEN` from environment variables or a secrets manager — never hardcode credentials.
+
 ## Constraints
 
 ### MUST DO
 - Respect user permissions and workspace access controls
-- Validate JQL/CQL queries before execution
+- Validate JQL/CQL queries before execution (use `maxResults=1` probe first)
 - Handle rate limits with exponential backoff
 - Use pagination for large result sets (50-100 items per page)
 - Implement error recovery for network failures
 - Log API calls for debugging and audit trails
 - Test with read-only operations first
 - Document required permission scopes
+- Confirm before any write or bulk operation against production data
 
 ### MUST NOT DO
 - Hardcode API tokens or OAuth secrets in code
@@ -82,7 +122,3 @@ When implementing Atlassian MCP features, provide:
 3. Tool call implementation with error handling
 4. Authentication setup instructions
 5. Brief explanation of permission requirements
-
-## Knowledge Reference
-
-Atlassian MCP Server (official), mcp-atlassian (sooperset), atlassian-mcp (xuanxt), JQL (Jira Query Language), CQL (Confluence Query Language), OAuth 2.1, API tokens, Personal Access Tokens (PAT), Model Context Protocol, JSON-RPC 2.0, rate limiting, pagination, permission scopes, Jira REST API, Confluence REST API
diff --git a/skills/chaos-engineer/SKILL.md b/skills/chaos-engineer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: chaos-engineer
-description: Use when designing chaos experiments, implementing failure injection frameworks, or conducting game day exercises. Invoke for chaos experiments, resilience testing, blast radius control, game days, antifragile systems.
+description: Designs chaos experiments, creates failure injection frameworks, and facilitates game day exercises for distributed systems — producing runbooks, experiment manifests, rollback procedures, and post-mortem templates. Use when designing chaos experiments, implementing failure injection frameworks, or conducting game day exercises. Invoke for chaos experiments, resilience testing, blast radius control, game days, antifragile systems, fault injection, Chaos Monkey, Litmus Chaos.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,12 +15,6 @@ metadata:
 
 # Chaos Engineer
 
-Senior chaos engineer with deep expertise in controlled failure injection, resilience testing, and building systems that get stronger under stress.
-
-## Role Definition
-
-You are a senior chaos engineer with 10+ years of experience in reliability engineering and resilience testing. You specialize in designing and executing controlled chaos experiments, managing blast radius, and building organizational resilience through scientific experimentation and continuous learning from controlled failures.
-
 ## When to Use This Skill
 
 - Designing and executing chaos experiments
@@ -50,27 +44,16 @@ Load detailed guidance based on context:
 | Tools & Automation | `references/chaos-tools.md` | Chaos Monkey, Gremlin, Pumba, CI/CD integration |
 | Game Days | `references/game-days.md` | Planning, executing, learning from game days |
 
-## Constraints
-
-### MUST DO
-- Define steady state metrics before experiments
-- Document hypothesis clearly
-- Control blast radius (start small, isolate impact)
-- Enable automated rollback under 30 seconds
-- Monitor continuously during experiments
-- Ensure zero customer impact initially
-- Capture all learnings and share
-- Implement improvements from findings
-
-### MUST NOT DO
-- Run experiments without hypothesis
-- Skip blast radius controls
-- Test in production without safety nets
-- Ignore monitoring during experiments
-- Run multiple variables simultaneously (initially)
-- Forget to document learnings
-- Skip team communication
-- Leave systems in degraded state
+## Safety Checklist
+
+Non-obvious constraints that must be enforced on every experiment:
+
+- **Steady state first** — define and verify baseline metrics before injecting any failure
+- **Blast radius cap** — start with the smallest possible impact scope; expand only after validation
+- **Automated rollback ≤ 30 seconds** — abort path must be scripted and tested before the experiment begins
+- **Single variable** — change only one failure condition at a time until behaviour is well understood
+- **No production without safety nets** — customer-facing environments require circuit breakers, feature flags, or canary isolation
+- **Close the loop** — every experiment must produce a written learning summary and at least one tracked improvement
 
 ## Output Templates
 
@@ -81,6 +64,119 @@ When implementing chaos engineering, provide:
 4. Rollback procedures and safety controls
 5. Learning summary and improvement recommendations
 
-## Knowledge Reference
+## Concrete Example: Pod Failure Experiment (Litmus Chaos)
 
-Chaos Monkey, Litmus Chaos, Chaos Mesh, Gremlin, Pumba, toxiproxy, chaos experiments, blast radius control, game days, failure injection, network chaos, infrastructure resilience, Kubernetes chaos, organizational resilience, MTTR reduction, antifragile systems
+The following shows a complete experiment — from hypothesis to rollback — using Litmus Chaos on Kubernetes.
+
+### Step 1 — Define steady state and apply the experiment
+
+```bash
+# Verify baseline: p99 latency < 200ms, error rate < 0.1%
+kubectl get deploy my-service -n production
+kubectl top pods -n production -l app=my-service
+```
+
+### Step 2 — Create and apply a Litmus ChaosEngine manifest
+
+```yaml
+# chaos-pod-delete.yaml
+apiVersion: litmuschaos.io/v1alpha1
+kind: ChaosEngine
+metadata:
+  name: my-service-pod-delete
+  namespace: production
+spec:
+  appinfo:
+    appns: production
+    applabel: "app=my-service"
+    appkind: deployment
+  # Limit blast radius: only 1 replica at a time
+  engineState: active
+  chaosServiceAccount: litmus-admin
+  experiments:
+    - name: pod-delete
+      spec:
+        components:
+          env:
+            - name: TOTAL_CHAOS_DURATION
+              value: "60"          # seconds
+            - name: CHAOS_INTERVAL
+              value: "20"          # delete one pod every 20s
+            - name: FORCE
+              value: "false"
+            - name: PODS_AFFECTED_PERC
+              value: "33"          # max 33% of replicas affected
+```
+
+```bash
+# Apply the experiment
+kubectl apply -f chaos-pod-delete.yaml
+
+# Watch experiment status
+kubectl describe chaosengine my-service-pod-delete -n production
+kubectl get chaosresult my-service-pod-delete-pod-delete -n production -w
+```
+
+### Step 3 — Monitor during the experiment
+
+```bash
+# Tail application logs for errors
+kubectl logs -l app=my-service -n production --since=2m -f
+
+# Check ChaosResult verdict when complete
+kubectl get chaosresult my-service-pod-delete-pod-delete \
+  -n production -o jsonpath='{.status.experimentStatus.verdict}'
+```
+
+### Step 4 — Rollback / abort if steady state is violated
+
+```bash
+# Immediately stop the experiment
+kubectl patch chaosengine my-service-pod-delete \
+  -n production --type merge -p '{"spec":{"engineState":"stop"}}'
+
+# Confirm all pods are healthy
+kubectl rollout status deployment/my-service -n production
+```
+
+## Concrete Example: Network Latency with toxiproxy
+
+```bash
+# Install toxiproxy CLI
+brew install toxiproxy   # macOS; use the binary release on Linux
+
+# Start toxiproxy server (runs alongside your service)
+toxiproxy-server &
+
+# Create a proxy for your downstream dependency
+toxiproxy-cli create -l 0.0.0.0:22222 -u downstream-db:5432 db-proxy
+
+# Inject 300ms latency with 10% jitter — blast radius: this proxy only
+toxiproxy-cli toxic add db-proxy -t latency -a latency=300 -a jitter=30
+
+# Run your load test / observe metrics here ...
+
+# Remove the toxic to restore normal behaviour
+toxiproxy-cli toxic remove db-proxy -n latency_downstream
+```
+
+## Concrete Example: Chaos Monkey (Spinnaker / standalone)
+
+```bash
+# chaos-monkey-config.yml — restrict to a single ASG
+deployment:
+  enabled: true
+  regionIndependence: false
+chaos:
+  enabled: true
+  meanTimeBetweenKillsInWorkDays: 2
+  minTimeBetweenKillsInWorkDays: 1
+  grouping: APP           # kill one instance per app, not per cluster
+  exceptions:
+    - account: production
+      region: us-east-1
+      detail: "*-canary"  # never kill canary instances
+
+# Apply and trigger a manual kill for testing
+chaos-monkey --app my-service --account staging --dry-run false
+```
diff --git a/skills/cli-developer/SKILL.md b/skills/cli-developer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: cli-developer
-description: Use when building CLI tools, implementing argument parsing, or adding interactive prompts. Invoke for CLI design, argument parsing, interactive prompts, progress indicators, shell completions.
+description: Use when building CLI tools, implementing argument parsing, or adding interactive prompts. Invoke for parsing flags and subcommands, displaying progress bars and spinners, generating bash/zsh/fish completion scripts, CLI design, shell completions, and cross-platform terminal applications using commander, click, typer, or cobra.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,28 +15,13 @@ metadata:
 
 # CLI Developer
 
-Senior CLI developer with expertise in building intuitive, cross-platform command-line tools with excellent developer experience.
-
-## Role Definition
-
-You are a senior CLI developer with 10+ years of experience building developer tools. You specialize in creating fast, intuitive command-line interfaces across Node.js, Python, and Go ecosystems. You build tools with <50ms startup time, comprehensive shell completions, and delightful UX.
-
-## When to Use This Skill
-
-- Building CLI tools and terminal applications
-- Implementing argument parsing and subcommands
-- Creating interactive prompts and forms
-- Adding progress bars and spinners
-- Implementing shell completions (bash, zsh, fish)
-- Optimizing CLI performance and startup time
-
 ## Core Workflow
 
-1. **Analyze UX** - Identify user workflows, command hierarchy, common tasks
-2. **Design commands** - Plan subcommands, flags, arguments, configuration
-3. **Implement** - Build with appropriate CLI framework for the language
-4. **Polish** - Add completions, help text, error messages, progress indicators
-5. **Test** - Cross-platform testing, performance benchmarks
+1. **Analyze UX** — Identify user workflows, command hierarchy, common tasks. Validate by listing all commands and their expected `--help` output before writing code.
+2. **Design commands** — Plan subcommands, flags, arguments, configuration. Confirm flag naming is consistent and no existing signatures are broken.
+3. **Implement** — Build with the appropriate CLI framework for the language (see Reference Guide below). After wiring up commands, run `<cli> --help` to verify help text renders correctly and `<cli> --version` to confirm version output.
+4. **Polish** — Add completions, help text, error messages, progress indicators. Verify TTY detection for color output and graceful SIGINT handling.
+5. **Test** — Run cross-platform smoke tests; benchmark startup time (target: <50ms).
 
 ## Reference Guide
 
@@ -50,26 +35,69 @@ Load detailed guidance based on context:
 | Go CLIs | `references/go-cli.md` | cobra, viper, bubbletea |
 | UX Patterns | `references/ux-patterns.md` | Progress bars, colors, help text |
 
+## Quick-Start Example
+
+### Node.js (commander)
+
+```js
+#!/usr/bin/env node
+// npm install commander
+const { program } = require('commander');
+
+program
+  .name('mytool')
+  .description('Example CLI')
+  .version('1.0.0');
+
+program
+  .command('greet <name>')
+  .description('Greet a user')
+  .option('-l, --loud', 'uppercase the greeting')
+  .action((name, opts) => {
+    const msg = `Hello, ${name}!`;
+    console.log(opts.loud ? msg.toUpperCase() : msg);
+  });
+
+program.parse();
+```
+
+For Python (click/typer) and Go (cobra) quick-start examples, see `references/python-cli.md` and `references/go-cli.md`.
+
 ## Constraints
 
 ### MUST DO
 - Keep startup time under 50ms
 - Provide clear, actionable error messages
-- Support --help and --version flags
+- Support `--help` and `--version` flags
 - Use consistent flag naming conventions
 - Handle SIGINT (Ctrl+C) gracefully
 - Validate user input early
 - Support both interactive and non-interactive modes
 - Test on Windows, macOS, and Linux
 
 ### MUST NOT DO
-- Block on synchronous I/O unnecessarily
-- Print to stdout if output will be piped
-- Use colors when output is not a TTY
-- Break existing command signatures (breaking changes)
-- Require interactive input in CI/CD environments
-- Hardcode paths or platform-specific logic
-- Ship without shell completions
+
+- **Block on synchronous I/O unnecessarily** — use async reads or stream processing instead.
+- **Print to stdout when output will be piped** — write logs/diagnostics to stderr.
+- **Use colors when output is not a TTY** — detect before applying color:
+  ```js
+  // Node.js
+  const useColor = process.stdout.isTTY;
+  ```
+  ```python
+  # Python
+  import sys
+  use_color = sys.stdout.isatty()
+  ```
+  ```go
+  // Go
+  import "golang.org/x/term"
+  useColor := term.IsTerminal(int(os.Stdout.Fd()))
+  ```
+- **Break existing command signatures** — treat flag/subcommand renames as breaking changes.
+- **Require interactive input in CI/CD environments** — always provide non-interactive fallbacks via flags or env vars.
+- **Hardcode paths or platform-specific logic** — use `os.homedir()` / `os.UserHomeDir()` / `Path.home()` instead.
+- **Ship without shell completions** — all three frameworks above have built-in completion generation.
 
 ## Output Templates
 
diff --git a/skills/cloud-architect/SKILL.md b/skills/cloud-architect/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: cloud-architect
-description: Use when designing cloud architectures, planning migrations, or optimizing multi-cloud deployments. Invoke for Well-Architected Framework, cost optimization, disaster recovery, landing zones, security architecture, serverless design.
+description: Designs cloud architectures, creates migration plans, generates cost optimization recommendations, and produces disaster recovery strategies across AWS, Azure, and GCP. Use when designing cloud architectures, planning migrations, or optimizing multi-cloud deployments. Invoke for Well-Architected Framework, cost optimization, disaster recovery, landing zones, security architecture, serverless design.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,31 +15,39 @@ metadata:
 
 # Cloud Architect
 
-Senior cloud architect specializing in multi-cloud strategies, migration patterns, cost optimization, and cloud-native architectures across AWS, Azure, and GCP.
+## Core Workflow
 
-## Role Definition
+1. **Discovery** — Assess current state, requirements, constraints, compliance needs
+2. **Design** — Select services, design topology, plan data architecture
+3. **Security** — Implement zero-trust, identity federation, encryption
+4. **Cost Model** — Right-size resources, reserved capacity, auto-scaling
+5. **Migration** — Apply 6Rs framework, define waves, validate connectivity before cutover
+6. **Operate** — Set up monitoring, automation, continuous optimization
 
-You are a senior cloud architect with 15+ years of experience designing enterprise cloud solutions. You specialize in multi-cloud architectures, migration strategies (6Rs), cost optimization, security by design, and operational excellence. You design highly available, secure, and cost-effective cloud infrastructures following Well-Architected Framework principles.
+### Workflow Validation Checkpoints
 
-## When to Use This Skill
+**After Design:** Confirm every component has a redundancy strategy and no single points of failure exist in the topology.
 
-- Designing cloud architectures (AWS, Azure, GCP)
-- Planning cloud migrations and modernization
-- Implementing multi-cloud and hybrid cloud strategies
-- Optimizing cloud costs (right-sizing, reserved instances, spot)
-- Designing for high availability and disaster recovery
-- Implementing cloud security and compliance
-- Setting up landing zones and governance
-- Architecting serverless and container platforms
+**Before Migration cutover:** Validate VPC peering or connectivity is fully established:
+```bash
+# AWS: confirm peering connection is Active before proceeding
+aws ec2 describe-vpc-peering-connections \
+  --filters "Name=status-code,Values=active"
 
-## Core Workflow
+# Azure: confirm VNet peering state
+az network vnet peering list \
+  --resource-group myRG --vnet-name myVNet \
+  --query "[].{Name:name,State:peeringState}"
+```
+
+**After Migration:** Verify application health and routing:
+```bash
+# AWS: check target group health in ALB
+aws elbv2 describe-target-health \
+  --target-group-arn arn:aws:elasticloadbalancing:...
+```
 
-1. **Discovery** - Assess current state, requirements, constraints, compliance needs
-2. **Design** - Select services, design topology, plan data architecture
-3. **Security** - Implement zero-trust, identity federation, encryption
-4. **Cost Model** - Right-size resources, reserved capacity, auto-scaling
-5. **Migration** - Apply 6Rs framework, define waves, test failover
-6. **Operate** - Set up monitoring, automation, continuous optimization
+**After DR test:** Confirm RTO/RPO targets were met; document actual recovery times.
 
 ## Reference Guide
 
@@ -75,6 +83,129 @@ Load detailed guidance based on context:
 - Ignore compliance requirements
 - Skip disaster recovery testing
 
+## Common Patterns with Examples
+
+### Least-Privilege IAM (Zero-Trust)
+
+Rather than broad policies, scope permissions to specific resources and actions:
+
+```bash
+# AWS: create a scoped role for an application
+aws iam create-role \
+  --role-name AppRole \
+  --assume-role-policy-document file://trust-policy.json
+
+aws iam put-role-policy \
+  --role-name AppRole \
+  --policy-name AppInlinePolicy \
+  --policy-document '{
+    "Version": "2012-10-17",
+    "Statement": [{
+      "Effect": "Allow",
+      "Action": ["s3:GetObject", "s3:PutObject"],
+      "Resource": "arn:aws:s3:::my-app-bucket/*"
+    }]
+  }'
+```
+
+```hcl
+# Terraform equivalent
+resource "aws_iam_role" "app_role" {
+  name               = "AppRole"
+  assume_role_policy = data.aws_iam_policy_document.trust.json
+}
+
+resource "aws_iam_role_policy" "app_policy" {
+  role = aws_iam_role.app_role.id
+  policy = jsonencode({
+    Version = "2012-10-17"
+    Statement = [{
+      Effect   = "Allow"
+      Action   = ["s3:GetObject", "s3:PutObject"]
+      Resource = "${aws_s3_bucket.app.arn}/*"
+    }]
+  })
+}
+```
+
+### VPC with Public/Private Subnets (Terraform)
+
+```hcl
+resource "aws_vpc" "main" {
+  cidr_block           = "10.0.0.0/16"
+  enable_dns_hostnames = true
+  tags = { Name = "main", CostCenter = var.cost_center }
+}
+
+resource "aws_subnet" "private" {
+  count             = 2
+  vpc_id            = aws_vpc.main.id
+  cidr_block        = cidrsubnet("10.0.0.0/16", 8, count.index)
+  availability_zone = data.aws_availability_zones.available.names[count.index]
+}
+
+resource "aws_subnet" "public" {
+  count                   = 2
+  vpc_id                  = aws_vpc.main.id
+  cidr_block              = cidrsubnet("10.0.0.0/16", 8, count.index + 10)
+  availability_zone       = data.aws_availability_zones.available.names[count.index]
+  map_public_ip_on_launch = true
+}
+```
+
+### Auto-Scaling Group (Terraform)
+
+```hcl
+resource "aws_autoscaling_group" "app" {
+  desired_capacity    = 2
+  min_size            = 1
+  max_size            = 10
+  vpc_zone_identifier = aws_subnet.private[*].id
+
+  launch_template {
+    id      = aws_launch_template.app.id
+    version = "$Latest"
+  }
+
+  tag {
+    key                 = "CostCenter"
+    value               = var.cost_center
+    propagate_at_launch = true
+  }
+}
+
+resource "aws_autoscaling_policy" "cpu_target" {
+  autoscaling_group_name = aws_autoscaling_group.app.name
+  policy_type            = "TargetTrackingScaling"
+  target_tracking_configuration {
+    predefined_metric_specification {
+      predefined_metric_type = "ASGAverageCPUUtilization"
+    }
+    target_value = 60.0
+  }
+}
+```
+
+### Cost Analysis CLI
+
+```bash
+# AWS: identify top cost drivers for the last 30 days
+aws ce get-cost-and-usage \
+  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
+  --granularity MONTHLY \
+  --metrics "UnblendedCost" \
+  --group-by Type=DIMENSION,Key=SERVICE \
+  --query 'ResultsByTime[0].Groups[*].{Service:Keys[0],Cost:Metrics.UnblendedCost.Amount}' \
+  --output table
+
+# Azure: review spend by resource group
+az consumption usage list \
+  --start-date $(date -d '30 days ago' +%Y-%m-%d) \
+  --end-date $(date +%Y-%m-%d) \
+  --query "[].{ResourceGroup:resourceGroup,Cost:pretaxCost,Currency:currency}" \
+  --output table
+```
+
 ## Output Templates
 
 When designing cloud architecture, provide:
@@ -83,7 +214,3 @@ When designing cloud architecture, provide:
 3. Security architecture (IAM, network segmentation, encryption)
 4. Cost estimation and optimization strategy
 5. Deployment approach and rollback plan
-
-## Knowledge Reference
-
-AWS (EC2, S3, Lambda, RDS, VPC, CloudFront), Azure (VMs, Blob Storage, Functions, SQL Database, VNet), GCP (Compute Engine, Cloud Storage, Cloud Functions, Cloud SQL), Kubernetes, Docker, Terraform, CloudFormation, ARM templates, CI/CD, disaster recovery, cost optimization, security best practices, compliance frameworks (SOC2, HIPAA, PCI-DSS)
diff --git a/skills/code-documenter/SKILL.md b/skills/code-documenter/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: code-documenter
-description: Use when adding docstrings, creating API documentation, or building documentation sites. Invoke for OpenAPI/Swagger specs, JSDoc, doc portals, tutorials, user guides.
+description: Generates, formats, and validates technical documentation — including docstrings, OpenAPI/Swagger specs, JSDoc annotations, doc portals, and user guides. Use when adding docstrings to functions or classes, creating API documentation, building documentation sites, or writing tutorials and user guides. Invoke for OpenAPI/Swagger specs, JSDoc, doc portals, getting started guides.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,28 +17,88 @@ metadata:
 
 Documentation specialist for inline documentation, API specs, documentation sites, and developer guides.
 
-## Role Definition
-
-You are a senior technical writer with 8+ years of experience documenting software. You specialize in language-specific docstring formats, OpenAPI/Swagger specifications, interactive documentation portals, static site generation, and creating comprehensive guides that developers actually use.
-
 ## When to Use This Skill
 
-- Adding docstrings to functions and classes
-- Creating OpenAPI/Swagger documentation
-- Building documentation sites (Docusaurus, MkDocs, VitePress)
-- Documenting APIs with framework-specific patterns
-- Creating interactive API portals (Swagger UI, Redoc, Stoplight)
-- Writing getting started guides and tutorials
-- Documenting multi-protocol APIs (REST, GraphQL, WebSocket, gRPC)
-- Generating documentation reports and coverage metrics
+Applies to any task involving code documentation, API specs, or developer-facing guides. See the reference table below for specific sub-topics.
 
 ## Core Workflow
 
 1. **Discover** - Ask for format preference and exclusions
 2. **Detect** - Identify language and framework
 3. **Analyze** - Find undocumented code
 4. **Document** - Apply consistent format
-5. **Report** - Generate coverage summary
+5. **Validate** - Test all code examples compile/run:
+   - Python: `python -m doctest file.py` for doctest blocks; `pytest --doctest-modules` for module-wide checks
+   - TypeScript/JavaScript: `tsc --noEmit` to confirm typed examples compile
+   - OpenAPI: validate spec with `npx @redocly/cli lint openapi.yaml`
+   - If validation fails: fix examples and re-validate before proceeding to the Report step
+6. **Report** - Generate coverage summary
+
+## Quick-Reference Examples
+
+### Google-style Docstring (Python)
+```python
+def fetch_user(user_id: int, active_only: bool = True) -> dict:
+    """Fetch a single user record by ID.
+
+    Args:
+        user_id: Unique identifier for the user.
+        active_only: When True, raise an error for inactive users.
+
+    Returns:
+        A dict containing user fields (id, name, email, created_at).
+
+    Raises:
+        ValueError: If user_id is not a positive integer.
+        UserNotFoundError: If no matching user exists.
+    """
+```
+
+### NumPy-style Docstring (Python)
+```python
+def compute_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
+    """Compute cosine similarity between two vectors.
+
+    Parameters
+    ----------
+    vec_a : np.ndarray
+        First input vector, shape (n,).
+    vec_b : np.ndarray
+        Second input vector, shape (n,).
+
+    Returns
+    -------
+    float
+        Cosine similarity in the range [-1, 1].
+
+    Raises
+    ------
+    ValueError
+        If vectors have different lengths.
+    """
+```
+
+### JSDoc (TypeScript)
+```typescript
+/**
+ * Fetches a paginated list of products from the catalog.
+ *
+ * @param {string} categoryId - The category to filter by.
+ * @param {number} [page=1] - Page number (1-indexed).
+ * @param {number} [limit=20] - Maximum items per page.
+ * @returns {Promise<ProductPage>} Resolves to a page of product records.
+ * @throws {NotFoundError} If the category does not exist.
+ *
+ * @example
+ * const page = await fetchProducts('electronics', 2, 10);
+ * console.log(page.items);
+ */
+async function fetchProducts(
+  categoryId: string,
+  page = 1,
+  limit = 20
+): Promise<ProductPage> { ... }
+```
 
 ## Reference Guide
 
diff --git a/skills/code-reviewer/SKILL.md b/skills/code-reviewer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: code-reviewer
-description: Use when reviewing pull requests, conducting code quality audits, or identifying security vulnerabilities. Invoke for PR reviews, code quality checks, refactoring suggestions.
+description: Analyzes code diffs and files to identify bugs, security vulnerabilities (SQL injection, XSS, insecure deserialization), code smells, N+1 queries, naming issues, and architectural concerns, then produces a structured review report with prioritized, actionable feedback. Use when reviewing pull requests, conducting code quality audits, identifying refactoring opportunities, or checking for security issues. Invoke for PR reviews, code quality checks, refactoring suggestions, review code, code quality. Complements specialized skills (security-reviewer, test-master) by providing broad-scope review across correctness, performance, maintainability, and test coverage in a single pass.
 license: MIT
 allowed-tools: Read, Grep, Glob
 metadata:
@@ -18,10 +18,6 @@ metadata:
 
 Senior engineer conducting thorough, constructive code reviews that improve quality and share knowledge.
 
-## Role Definition
-
-You are a principal engineer with 12+ years of experience across multiple languages. You review code for correctness, security, performance, and maintainability. You provide actionable feedback that helps developers grow.
-
 ## When to Use This Skill
 
 - Reviewing pull requests
@@ -32,11 +28,13 @@ You are a principal engineer with 12+ years of experience across multiple langua
 
 ## Core Workflow
 
-1. **Context** - Read PR description, understand the problem
-2. **Structure** - Review architecture and design decisions
-3. **Details** - Check code quality, security, performance
-4. **Tests** - Validate test coverage and quality
-5. **Feedback** - Provide categorized, actionable feedback
+1. **Context** — Read PR description, understand the problem being solved. **Checkpoint:** Summarize the PR's intent in one sentence before proceeding. If you cannot, ask the author to clarify.
+2. **Structure** — Review architecture and design decisions. Ask: Does this follow existing patterns in the codebase? Are new abstractions justified?
+3. **Details** — Check code quality, security, and performance. Apply the checks in the Reference Guide below. Ask: Are there N+1 queries, hardcoded secrets, or injection risks?
+4. **Tests** — Validate test coverage and quality. Ask: Are edge cases covered? Do tests assert behavior, not implementation?
+5. **Feedback** — Produce a categorized report using the Output Template. If critical issues are found in step 3, note them immediately and do not wait until the end.
+
+> **Disagreement handling:** If the author has left comments explaining a non-obvious choice, acknowledge their reasoning before suggesting an alternative. Never block on style preferences when a linter or formatter is configured.
 
 ## Reference Guide
 
@@ -53,16 +51,49 @@ Load detailed guidance based on context:
 | Spec Compliance | `references/spec-compliance-review.md` | Reviewing implementations, PR review, spec verification |
 | Receiving Feedback | `references/receiving-feedback.md` | Responding to review comments, handling feedback |
 
+## Review Patterns (Quick Reference)
+
+### N+1 Query — Bad vs Good
+```python
+# BAD: query inside loop
+for user in users:
+    orders = Order.objects.filter(user=user)  # N+1
+
+# GOOD: prefetch in bulk
+users = User.objects.prefetch_related('orders').all()
+```
+
+### Magic Number — Bad vs Good
+```python
+# BAD
+if status == 3:
+    ...
+
+# GOOD
+ORDER_STATUS_SHIPPED = 3
+if status == ORDER_STATUS_SHIPPED:
+    ...
+```
+
+### Security: SQL Injection — Bad vs Good
+```python
+# BAD: string interpolation in query
+cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
+
+# GOOD: parameterized query
+cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
+```
+
 ## Constraints
 
 ### MUST DO
-- Understand context before reviewing
+- Summarize PR intent before reviewing (see Workflow step 1)
 - Provide specific, actionable feedback
 - Include code examples in suggestions
 - Praise good patterns
 - Prioritize feedback (critical → minor)
 - Review tests as thoroughly as code
-- Check for security issues
+- Check for security issues (OWASP Top 10 as baseline)
 
 ### MUST NOT DO
 - Be condescending or rude
@@ -72,16 +103,16 @@ Load detailed guidance based on context:
 - Review without understanding the why
 - Skip praising good work
 
-## Output Templates
+## Output Template
 
-Code review report should include:
-1. Summary (overall assessment)
-2. Critical issues (must fix)
-3. Major issues (should fix)
-4. Minor issues (nice to have)
-5. Positive feedback
-6. Questions for author
-7. Verdict (approve/request changes/comment)
+Code review report must include:
+1. **Summary** — One-sentence intent recap + overall assessment
+2. **Critical issues** — Must fix before merge (bugs, security, data loss)
+3. **Major issues** — Should fix (performance, design, maintainability)
+4. **Minor issues** — Nice to have (naming, readability)
+5. **Positive feedback** — Specific patterns done well
+6. **Questions for author** — Clarifications needed
+7. **Verdict** — Approve / Request Changes / Comment
 
 ## Knowledge Reference
 
diff --git a/skills/cpp-pro/SKILL.md b/skills/cpp-pro/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: cpp-pro
-description: Use when building C++ applications requiring modern C++20/23 features, template metaprogramming, or high-performance systems. Invoke for concepts, ranges, coroutines, SIMD optimization, memory management.
+description: Writes, optimizes, and debugs C++ applications using modern C++20/23 features, template metaprogramming, and high-performance systems techniques. Use when building or refactoring C++ code requiring concepts, ranges, coroutines, SIMD optimization, or careful memory management — or when addressing performance bottlenecks, concurrency issues, and build system configuration with CMake.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,13 @@ metadata:
 
 Senior C++ developer with deep expertise in modern C++20/23, systems programming, high-performance computing, and zero-overhead abstractions.
 
-## Role Definition
-
-You are a senior C++ engineer with 15+ years of systems programming experience. You specialize in modern C++20/23, template metaprogramming, performance optimization, and building production-grade systems with emphasis on safety, efficiency, and maintainability. You follow C++ Core Guidelines and leverage cutting-edge language features.
-
-## When to Use This Skill
-
-- Building high-performance C++ applications
-- Implementing template metaprogramming solutions
-- Optimizing memory-critical systems
-- Developing concurrent and parallel algorithms
-- Creating custom allocators and memory pools
-- Systems programming and embedded development
-
 ## Core Workflow
 
-1. **Analyze architecture** - Review build system, compiler flags, performance requirements
-2. **Design with concepts** - Create type-safe interfaces using C++20 concepts
-3. **Implement zero-cost** - Apply RAII, constexpr, and zero-overhead abstractions
-4. **Verify quality** - Run sanitizers, static analysis, and performance benchmarks
-5. **Optimize** - Profile, measure, and apply targeted optimizations
+1. **Analyze architecture** — Review build system, compiler flags, performance requirements
+2. **Design with concepts** — Create type-safe interfaces using C++20 concepts
+3. **Implement zero-cost** — Apply RAII, constexpr, and zero-overhead abstractions
+4. **Verify quality** — Run sanitizers and static analysis; if AddressSanitizer or UndefinedBehaviorSanitizer report issues, fix all memory and UB errors before proceeding
+5. **Benchmark** — Profile with real workloads; if performance targets are not met, apply targeted optimizations (SIMD, cache layout, move semantics) and re-measure
 
 ## Reference Guide
 
@@ -72,6 +59,52 @@ Load detailed guidance based on context:
 - Ignore undefined behavior
 - Skip move semantics for expensive types
 
+## Key Patterns
+
+### Concept Definition (C++20)
+```cpp
+// Define a reusable, self-documenting constraint
+template<typename T>
+concept Numeric = std::integral<T> || std::floating_point<T>;
+
+template<Numeric T>
+T clamp(T value, T lo, T hi) {
+    return std::clamp(value, lo, hi);
+}
+```
+
+### RAII Resource Wrapper
+```cpp
+// Wraps a raw handle; no manual cleanup needed at call sites
+class FileHandle {
+public:
+    explicit FileHandle(const char* path)
+        : handle_(std::fopen(path, "r")) {
+        if (!handle_) throw std::runtime_error("Cannot open file");
+    }
+    ~FileHandle() { if (handle_) std::fclose(handle_); }
+
+    // Non-copyable, movable
+    FileHandle(const FileHandle&) = delete;
+    FileHandle& operator=(const FileHandle&) = delete;
+    FileHandle(FileHandle&& other) noexcept
+        : handle_(std::exchange(other.handle_, nullptr)) {}
+
+    std::FILE* get() const noexcept { return handle_; }
+private:
+    std::FILE* handle_;
+};
+```
+
+### Smart Pointer Ownership
+```cpp
+// Prefer make_unique / make_shared; avoid raw new/delete
+auto buffer = std::make_unique<std::array<std::byte, 4096>>();
+
+// Shared ownership only when genuinely needed
+auto config = std::make_shared<Config>(parseArgs(argc, argv));
+```
+
 ## Output Templates
 
 When implementing C++ features, provide:
@@ -80,7 +113,3 @@ When implementing C++ features, provide:
 3. CMakeLists.txt updates (if applicable)
 4. Test file demonstrating usage
 5. Brief explanation of design decisions and performance characteristics
-
-## Knowledge Reference
-
-C++20/23, concepts, ranges, coroutines, modules, template metaprogramming, SFINAE, type traits, CRTP, smart pointers, custom allocators, move semantics, RAII, SIMD, atomics, lock-free programming, CMake, Conan, sanitizers, clang-tidy, cppcheck, Catch2, GoogleTest
diff --git a/skills/csharp-developer/SKILL.md b/skills/csharp-developer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: csharp-developer
-description: "Use when building C# applications with .NET 8+, ASP.NET Core APIs, or Blazor web apps. Invoke for Entity Framework Core, minimal APIs, async patterns, CQRS with MediatR."
+description: "Use when building C# applications with .NET 8+, ASP.NET Core APIs, or Blazor web apps. Builds REST APIs using minimal or controller-based routing, configures database access with Entity Framework Core, implements async patterns and cancellation, structures applications with CQRS via MediatR, and scaffolds Blazor components with state management. Invoke for C#, .NET, ASP.NET Core, Blazor, Entity Framework, EF Core, Minimal API, MAUI, SignalR."
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,10 +17,6 @@ metadata:
 
 Senior C# developer with mastery of .NET 8+ and Microsoft ecosystem. Specializes in high-performance web APIs, cloud-native solutions, and modern C# language features.
 
-## Role Definition
-
-You are a senior C# developer with 10+ years of .NET experience. You specialize in ASP.NET Core, Blazor, Entity Framework Core, and modern C# 12 features. You build scalable, type-safe applications with clean architecture patterns and focus on performance optimization.
-
 ## When to Use This Skill
 
 - Building ASP.NET Core APIs (Minimal or Controller-based)
@@ -32,11 +28,13 @@ You are a senior C# developer with 10+ years of .NET experience. You specialize
 
 ## Core Workflow
 
-1. **Analyze solution** - Review .csproj files, NuGet packages, architecture
-2. **Design models** - Create domain models, DTOs, validation
-3. **Implement** - Write endpoints, repositories, services with DI
-4. **Optimize** - Apply async patterns, caching, performance tuning
-5. **Test** - Write xUnit tests with TestServer, achieve 80%+ coverage
+1. **Analyze solution** — Review .csproj files, NuGet packages, architecture
+2. **Design models** — Create domain models, DTOs, validation
+3. **Implement** — Write endpoints, repositories, services with DI
+4. **Optimize** — Apply async patterns, caching, performance tuning
+5. **Test** — Write xUnit tests with TestServer; verify 80%+ coverage
+
+> **EF Core checkpoint (after step 3):** Run `dotnet ef migrations add <Name>` and review the generated migration file before applying. Confirm no unintended table/column drops. Roll back with `dotnet ef migrations remove` if needed.
 
 ## Reference Guide
 
@@ -55,17 +53,36 @@ Load detailed guidance based on context:
 ### MUST DO
 - Enable nullable reference types in all projects
 - Use file-scoped namespaces and primary constructors (C# 12)
-- Apply async/await for all I/O operations
+- Apply async/await for all I/O operations — always accept and forward `CancellationToken`:
+  ```csharp
+  // Correct
+  app.MapGet("/items/{id}", async (int id, IItemService svc, CancellationToken ct) =>
+      await svc.GetByIdAsync(id, ct) is { } item ? Results.Ok(item) : Results.NotFound());
+  ```
 - Use dependency injection for all services
 - Include XML documentation for public APIs
-- Implement proper error handling with Result pattern
-- Use strongly-typed configuration with IOptions<T>
+- Implement proper error handling with Result pattern:
+  ```csharp
+  public readonly record struct Result<T>(T? Value, string? Error, bool IsSuccess)
+  {
+      public static Result<T> Ok(T value) => new(value, null, true);
+      public static Result<T> Fail(string error) => new(default, error, false);
+  }
+  ```
+- Use strongly-typed configuration with `IOptions<T>`
 
 ### MUST NOT DO
-- Use blocking calls (.Result, .Wait()) in async code
+- Use blocking calls (`.Result`, `.Wait()`) in async code:
+  ```csharp
+  // Wrong — blocks thread and risks deadlock
+  var data = service.GetDataAsync().Result;
+
+  // Correct
+  var data = await service.GetDataAsync(ct);
+  ```
 - Disable nullable warnings without proper justification
 - Skip cancellation token support in async methods
-- Expose EF Core entities directly in API responses
+- Expose EF Core entities directly in API responses — always map to DTOs
 - Use string-based configuration keys
 - Skip input validation
 - Ignore code analysis warnings
@@ -79,6 +96,30 @@ When implementing .NET features, provide:
 4. Configuration setup (Program.cs, appsettings.json)
 5. Brief explanation of architectural decisions
 
+## Example: Minimal API Endpoint
+
+```csharp
+// Program.cs (file-scoped, .NET 8 minimal API)
+var builder = WebApplication.CreateBuilder(args);
+builder.Services.AddScoped<IProductService, ProductService>();
+
+var app = builder.Build();
+
+app.MapGet("/products/{id:int}", async (
+    int id,
+    IProductService service,
+    CancellationToken ct) =>
+{
+    var result = await service.GetByIdAsync(id, ct);
+    return result.IsSuccess ? Results.Ok(result.Value) : Results.NotFound(result.Error);
+})
+.WithName("GetProduct")
+.Produces<ProductDto>()
+.ProducesProblem(404);
+
+app.Run();
+```
+
 ## Knowledge Reference
 
 C# 12, .NET 8, ASP.NET Core, Minimal APIs, Blazor (Server/WASM), Entity Framework Core, MediatR, xUnit, Moq, Benchmark.NET, SignalR, gRPC, Azure SDK, Polly, FluentValidation, Serilog
diff --git a/skills/database-optimizer/SKILL.md b/skills/database-optimizer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: database-optimizer
-description: Use when investigating slow queries, analyzing execution plans, or optimizing database performance. Invoke for index design, query rewrites, configuration tuning, partitioning strategies, lock contention resolution.
+description: Optimizes database queries and improves performance across PostgreSQL and MySQL systems. Use when investigating slow queries, analyzing execution plans, or optimizing database performance. Invoke for index design, query rewrites, configuration tuning, partitioning strategies, lock contention resolution.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,10 +17,6 @@ metadata:
 
 Senior database optimizer with expertise in performance tuning, query optimization, and scalability across multiple database systems.
 
-## Role Definition
-
-You are a senior database performance engineer with 10+ years of experience optimizing high-traffic databases. You specialize in PostgreSQL and MySQL optimization, execution plan analysis, strategic indexing, and achieving sub-100ms query performance at scale.
-
 ## When to Use This Skill
 
 - Analyzing slow queries and execution plans
@@ -32,11 +28,13 @@ You are a senior database performance engineer with 10+ years of experience opti
 
 ## Core Workflow
 
-1. **Analyze Performance** - Review slow queries, execution plans, system metrics
-2. **Identify Bottlenecks** - Find inefficient queries, missing indexes, config issues
-3. **Design Solutions** - Create index strategies, query rewrites, schema improvements
-4. **Implement Changes** - Apply optimizations incrementally with monitoring
-5. **Validate Results** - Measure improvements, ensure stability, document changes
+1. **Analyze Performance** — Capture baseline metrics and run `EXPLAIN ANALYZE` before any changes
+2. **Identify Bottlenecks** — Find inefficient queries, missing indexes, config issues
+3. **Design Solutions** — Create index strategies, query rewrites, schema improvements
+4. **Implement Changes** — Apply optimizations incrementally with monitoring; validate each change before proceeding to the next
+5. **Validate Results** — Re-run `EXPLAIN ANALYZE`, compare costs, measure wall-clock improvement, document changes
+
+> ⚠️ Always test changes in non-production first. Revert immediately if write performance degrades or replication lag increases.
 
 ## Reference Guide
 
@@ -50,36 +48,100 @@ Load detailed guidance based on context:
 | MySQL Tuning | `references/mysql-tuning.md` | MySQL-specific optimizations |
 | Monitoring & Analysis | `references/monitoring-analysis.md` | Performance metrics, diagnostics |
 
+## Common Operations & Examples
+
+### Identify Top Slow Queries (PostgreSQL)
+```sql
+-- Requires pg_stat_statements extension
+SELECT query,
+       calls,
+       round(total_exec_time::numeric, 2)  AS total_ms,
+       round(mean_exec_time::numeric, 2)   AS mean_ms,
+       round(stddev_exec_time::numeric, 2) AS stddev_ms,
+       rows
+FROM   pg_stat_statements
+ORDER  BY mean_exec_time DESC
+LIMIT  20;
+```
+
+### Capture an Execution Plan
+```sql
+-- Use BUFFERS to expose cache hit vs. disk read ratio
+EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
+SELECT o.id, c.name
+FROM   orders o
+JOIN   customers c ON c.id = o.customer_id
+WHERE  o.status = 'pending'
+  AND  o.created_at > now() - interval '7 days';
+```
+
+### Reading EXPLAIN Output — Key Patterns to Find
+
+| Pattern | Symptom | Typical Remedy |
+|---------|---------|----------------|
+| `Seq Scan` on large table | High row estimate, no filter selectivity | Add B-tree index on filter column |
+| `Nested Loop` with large outer set | Exponential row growth in inner loop | Consider Hash Join; index inner join key |
+| `cost=... rows=1` but actual rows=50000 | Stale statistics | Run `ANALYZE <table>;` |
+| `Buffers: hit=10 read=90000` | Low buffer cache hit rate | Increase `shared_buffers`; add covering index |
+| `Sort Method: external merge` | Sort spilling to disk | Increase `work_mem` for the session |
+
+### Create a Covering Index
+```sql
+-- Covers the filter AND the projected columns, eliminating a heap fetch
+CREATE INDEX CONCURRENTLY idx_orders_status_created_covering
+    ON orders (status, created_at)
+    INCLUDE (customer_id, total_amount);
+```
+
+### Validate Improvement
+```sql
+-- Before optimization: save plan & timing
+EXPLAIN (ANALYZE, BUFFERS) <query>;   -- note "Execution Time: X ms"
+
+-- After optimization: compare
+EXPLAIN (ANALYZE, BUFFERS) <query>;   -- target meaningful reduction in cost & time
+
+-- Confirm index is actually used
+SELECT indexname, idx_scan, idx_tup_read, idx_tup_fetch
+FROM   pg_stat_user_indexes
+WHERE  relname = 'orders';
+```
+
+### MySQL: Find Slow Queries
+```sql
+-- Inspect slow query log candidates
+SELECT * FROM performance_schema.events_statements_summary_by_digest
+ORDER  BY SUM_TIMER_WAIT DESC
+LIMIT  20;
+
+-- Execution plan
+EXPLAIN FORMAT=JSON
+SELECT * FROM orders WHERE status = 'pending' AND created_at > NOW() - INTERVAL 7 DAY;
+```
+
 ## Constraints
 
 ### MUST DO
-- Analyze EXPLAIN plans before optimizing
-- Measure performance before and after changes
-- Create indexes strategically (avoid over-indexing)
-- Test changes in non-production first
-- Document all optimization decisions
-- Monitor impact on write performance
-- Consider replication lag for distributed systems
+- Capture `EXPLAIN (ANALYZE, BUFFERS)` output **before** optimizing — this is the baseline
+- Measure performance before and after every change
+- Create indexes with `CONCURRENTLY` (PostgreSQL) to avoid table locks
+- Test in non-production; roll back if write performance or replication lag worsens
+- Document all optimization decisions with before/after metrics
+- Run `ANALYZE` after bulk data changes to refresh statistics
 
 ### MUST NOT DO
-- Apply optimizations without measurement
+- Apply optimizations without a measured baseline
 - Create redundant or unused indexes
-- Skip execution plan analysis
-- Ignore write performance impact
-- Make multiple changes simultaneously
-- Optimize without understanding query patterns
-- Neglect statistics updates (ANALYZE/VACUUM)
+- Make multiple changes simultaneously (impossible to attribute impact)
+- Ignore write amplification caused by new indexes
+- Neglect `VACUUM` / statistics maintenance
 
 ## Output Templates
 
 When optimizing database performance, provide:
-1. Performance analysis with baseline metrics
-2. Identified bottlenecks and root causes
+1. Performance analysis with baseline metrics (query time, cost, buffer hit ratio)
+2. Identified bottlenecks and root causes (with EXPLAIN evidence)
 3. Optimization strategy with specific changes
-4. Implementation SQL/config changes
+4. Implementation SQL / config changes
 5. Validation queries to measure improvement
 6. Monitoring recommendations
-
-## Knowledge Reference
-
-PostgreSQL (pg_stat_statements, EXPLAIN ANALYZE, indexes, VACUUM, partitioning), MySQL (slow query log, EXPLAIN, InnoDB, query cache), query optimization, index design, execution plans, configuration tuning, replication, sharding, caching strategies
diff --git a/skills/debugging-wizard/SKILL.md b/skills/debugging-wizard/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: debugging-wizard
-description: Use when investigating errors, analyzing stack traces, or finding root causes of unexpected behavior. Invoke for error investigation, troubleshooting, log analysis, root cause analysis.
+description: Parses error messages, traces execution flow through stack traces, correlates log entries to identify failure points, and applies systematic hypothesis-driven methodology to isolate and resolve bugs. Use when investigating errors, analyzing stack traces, finding root causes of unexpected behavior, troubleshooting crashes, or performing log analysis, error investigation, or root cause analysis.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,19 +17,6 @@ metadata:
 
 Expert debugger applying systematic methodology to isolate and resolve issues in any codebase.
 
-## Role Definition
-
-You are a senior engineer with 15+ years debugging experience across multiple languages and frameworks. You apply scientific methodology to isolate root causes efficiently. You never guess - you test hypotheses systematically.
-
-## When to Use This Skill
-
-- Investigating errors, exceptions, or unexpected behavior
-- Analyzing stack traces and error messages
-- Finding root causes of intermittent issues
-- Performance debugging and profiling
-- Memory leak investigation
-- Race condition diagnosis
-
 ## Core Workflow
 
 1. **Reproduce** - Establish consistent reproduction steps
@@ -70,14 +57,49 @@ Load detailed guidance based on context:
 - Debug in production without safeguards
 - Leave console.log/debugger statements in code
 
+## Common Debugging Commands
+
+**Python (pdb)**
+```bash
+python -m pdb script.py          # launch debugger
+# inside pdb:
+# b 42          — set breakpoint at line 42
+# n             — step over
+# s             — step into
+# p some_var    — print variable
+# bt            — print full traceback
+```
+
+**JavaScript (Node.js)**
+```bash
+node --inspect-brk script.js     # pause at first line, attach Chrome DevTools
+# In Chrome: open chrome://inspect → click "inspect"
+# Sources panel: add breakpoints, watch expressions, step through
+```
+
+**Git bisect (regression hunting)**
+```bash
+git bisect start
+git bisect bad                   # current commit is broken
+git bisect good v1.2.0           # last known good tag/commit
+# Git checks out midpoint — test, then:
+git bisect good   # or: git bisect bad
+# Repeat until git identifies the first bad commit
+git bisect reset
+```
+
+**Go (delve)**
+```bash
+dlv debug ./cmd/server           # build & attach
+# (dlv) break main.go:55
+# (dlv) continue
+# (dlv) print myVar
+```
+
 ## Output Templates
 
 When debugging, provide:
 1. **Root Cause**: What specifically caused the issue
 2. **Evidence**: Stack trace, logs, or test that proves it
 3. **Fix**: Code change that resolves it
 4. **Prevention**: Test or safeguard to prevent recurrence
-
-## Knowledge Reference
-
-Debuggers (Chrome DevTools, VS Code, pdb, delve), profilers, log aggregation, distributed tracing, memory analysis, git bisect, error tracking (Sentry)
diff --git a/skills/devops-engineer/SKILL.md b/skills/devops-engineer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: devops-engineer
-description: Use when setting up CI/CD pipelines, containerizing applications, or managing infrastructure as code. Invoke for pipelines, Docker, Kubernetes, cloud platforms, GitOps.
+description: Creates Dockerfiles, configures CI/CD pipelines, writes Kubernetes manifests, and generates Terraform/Pulumi infrastructure templates. Handles deployment automation, GitOps configuration, incident response runbooks, and internal developer platform tooling. Use when setting up CI/CD pipelines, containerizing applications, managing infrastructure as code, deploying to Kubernetes clusters, configuring cloud platforms, automating releases, or responding to production incidents. Invoke for pipelines, Docker, Kubernetes, GitOps, Terraform, GitHub Actions, on-call, or platform engineering.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -41,8 +41,9 @@ You are a senior DevOps engineer with 10+ years of experience. You operate with
 1. **Assess** - Understand application, environments, requirements
 2. **Design** - Pipeline structure, deployment strategy
 3. **Implement** - IaC, Dockerfiles, CI/CD configs
-4. **Deploy** - Roll out with verification
-5. **Monitor** - Set up observability, alerts
+4. **Validate** - Run `terraform plan`, lint configs, execute unit/integration tests; confirm no destructive changes before proceeding
+5. **Deploy** - Roll out with verification; run smoke tests post-deployment
+6. **Monitor** - Set up observability, alerts; confirm rollback procedure is ready before going live
 
 ## Reference Guide
 
@@ -81,6 +82,63 @@ Load detailed guidance based on context:
 
 Provide: CI/CD pipeline config, Dockerfile, K8s/Terraform files, deployment verification, rollback procedure
 
+### Minimal GitHub Actions Example
+
+```yaml
+name: CI
+on:
+  push:
+    branches: [main]
+jobs:
+  build-test-push:
+    runs-on: ubuntu-latest
+    steps:
+      - uses: actions/checkout@v4
+      - name: Build image
+        run: docker build -t myapp:${{ github.sha }} .
+      - name: Run tests
+        run: docker run --rm myapp:${{ github.sha }} pytest
+      - name: Scan image
+        uses: aquasecurity/trivy-action@master
+        with:
+          image-ref: myapp:${{ github.sha }}
+      - name: Push to registry
+        run: |
+          docker tag myapp:${{ github.sha }} ghcr.io/org/myapp:${{ github.sha }}
+          docker push ghcr.io/org/myapp:${{ github.sha }}
+```
+
+### Minimal Dockerfile Example
+
+```dockerfile
+FROM python:3.12-slim AS builder
+WORKDIR /app
+COPY requirements.txt .
+RUN pip install --no-cache-dir -r requirements.txt
+
+FROM python:3.12-slim
+WORKDIR /app
+COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
+COPY . .
+USER nonroot
+HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8080/health || exit 1
+CMD ["python", "main.py"]
+```
+
+### Rollback Procedure Example
+
+```bash
+# Kubernetes: roll back to previous deployment revision
+kubectl rollout undo deployment/myapp -n production
+kubectl rollout status deployment/myapp -n production
+
+# Verify rollback succeeded
+kubectl get pods -n production -l app=myapp
+curl -f https://myapp.example.com/health
+```
+
+Always document the rollback command and verification step in the PR or change ticket before deploying.
+
 ## Knowledge Reference
 
 GitHub Actions, GitLab CI, Jenkins, CircleCI, Docker, Kubernetes, Helm, ArgoCD, Flux, Terraform, Pulumi, Crossplane, AWS/GCP/Azure, Prometheus, Grafana, PagerDuty, Backstage, LaunchDarkly, Flagger
diff --git a/skills/django-expert/SKILL.md b/skills/django-expert/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: django-expert
-description: Use when building Django web applications or REST APIs with Django REST Framework. Invoke for Django models, ORM optimization, DRF serializers, viewsets, authentication with JWT.
+description: "Use when building Django web applications or REST APIs with Django REST Framework. Invoke when working with settings.py, models.py, manage.py, or any Django project file. Creates Django models with proper indexes, optimizes ORM queries using select_related/prefetch_related, builds DRF serializers and viewsets, and configures JWT authentication. Trigger terms: Django, DRF, Django REST Framework, Django ORM, Django model, serializer, viewset, Python web."
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,10 +17,6 @@ metadata:
 
 Senior Django specialist with deep expertise in Django 5.0, Django REST Framework, and production-grade web applications.
 
-## Role Definition
-
-You are a senior Python engineer with 10+ years of Django experience. You specialize in Django 5.0 with async views, DRF API development, and ORM optimization. You build scalable, secure applications following Django best practices.
-
 ## When to Use This Skill
 
 - Building Django web applications or REST APIs
@@ -32,11 +28,12 @@ You are a senior Python engineer with 10+ years of Django experience. You specia
 
 ## Core Workflow
 
-1. **Analyze requirements** - Identify models, relationships, API endpoints
-2. **Design models** - Create models with proper fields, indexes, managers
-3. **Implement views** - DRF viewsets or Django 5.0 async views
-4. **Add auth** - Permissions, JWT authentication
-5. **Test** - Django TestCase, APITestCase
+1. **Analyze requirements** — Identify models, relationships, API endpoints
+2. **Design models** — Create models with proper fields, indexes, managers → run `manage.py makemigrations` and `manage.py migrate`; verify schema before proceeding
+3. **Implement views** — DRF viewsets or Django 5.0 async views
+4. **Validate endpoints** — Confirm each endpoint returns expected status codes with a quick `APITestCase` or `curl` check before adding auth
+5. **Add auth** — Permissions, JWT authentication
+6. **Test** — Django TestCase, APITestCase
 
 ## Reference Guide
 
@@ -50,6 +47,90 @@ Load detailed guidance based on context:
 | Authentication | `references/authentication.md` | JWT, permissions, SimpleJWT |
 | Testing | `references/testing-django.md` | APITestCase, fixtures, factories |
 
+## Minimal Working Example
+
+The snippet below demonstrates the core MUST DO constraints: indexed fields, `select_related`, serializer validation, and endpoint permissions.
+
+```python
+# models.py
+from django.db import models
+
+class Article(models.Model):
+    title = models.CharField(max_length=255, db_index=True)
+    author = models.ForeignKey(
+        "auth.User", on_delete=models.CASCADE, related_name="articles"
+    )
+    published_at = models.DateTimeField(auto_now_add=True, db_index=True)
+
+    class Meta:
+        ordering = ["-published_at"]
+        indexes = [models.Index(fields=["author", "published_at"])]
+
+    def __str__(self):
+        return self.title
+
+
+# serializers.py
+from rest_framework import serializers
+from .models import Article
+
+class ArticleSerializer(serializers.ModelSerializer):
+    author_username = serializers.CharField(source="author.username", read_only=True)
+
+    class Meta:
+        model = Article
+        fields = ["id", "title", "author_username", "published_at"]
+
+    def validate_title(self, value):
+        if len(value.strip()) < 3:
+            raise serializers.ValidationError("Title must be at least 3 characters.")
+        return value.strip()
+
+
+# views.py
+from rest_framework import viewsets, permissions
+from .models import Article
+from .serializers import ArticleSerializer
+
+class ArticleViewSet(viewsets.ModelViewSet):
+    """
+    Uses select_related to avoid N+1 on author lookups.
+    IsAuthenticatedOrReadOnly: safe methods are public, writes require auth.
+    """
+    serializer_class = ArticleSerializer
+    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
+
+    def get_queryset(self):
+        return Article.objects.select_related("author").all()
+
+    def perform_create(self, serializer):
+        serializer.save(author=self.request.user)
+```
+
+```python
+# tests.py
+from rest_framework.test import APITestCase
+from rest_framework import status
+from django.contrib.auth.models import User
+
+class ArticleAPITest(APITestCase):
+    def setUp(self):
+        self.user = User.objects.create_user("alice", password="pass")
+
+    def test_list_public(self):
+        res = self.client.get("/api/articles/")
+        self.assertEqual(res.status_code, status.HTTP_200_OK)
+
+    def test_create_requires_auth(self):
+        res = self.client.post("/api/articles/", {"title": "Test"})
+        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
+
+    def test_create_authenticated(self):
+        self.client.force_authenticate(self.user)
+        res = self.client.post("/api/articles/", {"title": "Hello Django"})
+        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
+```
+
 ## Constraints
 
 ### MUST DO
diff --git a/skills/dotnet-core-expert/SKILL.md b/skills/dotnet-core-expert/SKILL.md
@@ -15,28 +15,13 @@ metadata:
 
 # .NET Core Expert
 
-Senior .NET Core specialist with deep expertise in .NET 8, modern C#, minimal APIs, and cloud-native application development.
-
-## Role Definition
-
-You are a senior .NET engineer with 10+ years of experience building enterprise applications. You specialize in .NET 8, C# 12, minimal APIs, Entity Framework Core, and cloud-native patterns. You build high-performance, scalable applications with clean architecture.
-
-## When to Use This Skill
-
-- Building minimal APIs with .NET 8
-- Implementing clean architecture with CQRS/MediatR
-- Setting up Entity Framework Core with async patterns
-- Creating microservices with cloud-native patterns
-- Implementing JWT authentication and authorization
-- Optimizing performance with AOT compilation
-
 ## Core Workflow
 
-1. **Analyze requirements** - Identify architecture pattern, data models, API design
-2. **Design solution** - Create clean architecture layers with proper separation
-3. **Implement** - Write high-performance code with modern C# features
-4. **Secure** - Add authentication, authorization, and security best practices
-5. **Test** - Write comprehensive tests with xUnit and integration testing
+1. **Analyze requirements** — Identify architecture pattern, data models, API design
+2. **Design solution** — Create clean architecture layers with proper separation
+3. **Implement** — Write high-performance code with modern C# features; run `dotnet build` to verify compilation — if build fails, review errors, fix issues, and rebuild before proceeding
+4. **Secure** — Add authentication, authorization, and security best practices
+5. **Test** — Write comprehensive tests with xUnit and integration testing; run `dotnet test` to confirm all tests pass — if tests fail, diagnose failures, fix the implementation, and re-run before continuing; verify endpoints with `curl` or a REST client
 
 ## Reference Guide
 
@@ -54,24 +39,95 @@ Load detailed guidance based on context:
 
 ### MUST DO
 - Use .NET 8 and C# 12 features
-- Enable nullable reference types
-- Use async/await for all I/O operations
+- Enable nullable reference types: `<Nullable>enable</Nullable>` in the `.csproj`
+- Use async/await for all I/O operations — e.g., `await dbContext.Users.ToListAsync()`
 - Implement proper dependency injection
-- Use record types for DTOs
+- Use record types for DTOs — e.g., `public record UserDto(int Id, string Name);`
 - Follow clean architecture principles
-- Write integration tests with WebApplicationFactory
+- Write integration tests with `WebApplicationFactory<Program>`
 - Configure OpenAPI/Swagger documentation
 
 ### MUST NOT DO
 - Use synchronous I/O operations
 - Expose entities directly in API responses
-- Store secrets in code or appsettings.json
 - Skip input validation
 - Use legacy .NET Framework patterns
-- Ignore compiler warnings
 - Mix concerns across architectural layers
 - Use deprecated EF Core patterns
 
+## Code Examples
+
+### Minimal API Endpoint
+```csharp
+// Program.cs
+var builder = WebApplication.CreateBuilder(args);
+builder.Services.AddEndpointsApiExplorer();
+builder.Services.AddSwaggerGen();
+builder.Services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof(Program).Assembly));
+
+var app = builder.Build();
+app.UseSwagger();
+app.UseSwaggerUI();
+
+app.MapGet("/users/{id}", async (int id, ISender sender, CancellationToken ct) =>
+{
+    var result = await sender.Send(new GetUserQuery(id), ct);
+    return result is null ? Results.NotFound() : Results.Ok(result);
+})
+.WithName("GetUser")
+.Produces<UserDto>()
+.ProducesProblem(404);
+
+app.Run();
+```
+
+### MediatR Query Handler
+```csharp
+// Application/Users/GetUserQuery.cs
+public record GetUserQuery(int Id) : IRequest<UserDto?>;
+
+public sealed class GetUserQueryHandler : IRequestHandler<GetUserQuery, UserDto?>
+{
+    private readonly AppDbContext _db;
+
+    public GetUserQueryHandler(AppDbContext db) => _db = db;
+
+    public async Task<UserDto?> Handle(GetUserQuery request, CancellationToken ct) =>
+        await _db.Users
+            .AsNoTracking()
+            .Where(u => u.Id == request.Id)
+            .Select(u => new UserDto(u.Id, u.Name))
+            .FirstOrDefaultAsync(ct);
+}
+```
+
+### EF Core DbContext with Async Query
+```csharp
+// Infrastructure/AppDbContext.cs
+public sealed class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
+{
+    public DbSet<User> Users => Set<User>();
+
+    protected override void OnModelCreating(ModelBuilder modelBuilder)
+    {
+        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
+    }
+}
+
+// Usage in a service
+public async Task<IReadOnlyList<UserDto>> GetAllAsync(CancellationToken ct) =>
+    await _db.Users
+        .AsNoTracking()
+        .Select(u => new UserDto(u.Id, u.Name))
+        .ToListAsync(ct);
+```
+
+### DTO with Record Type
+```csharp
+public record UserDto(int Id, string Name);
+public record CreateUserRequest(string Name, string Email);
+```
+
 ## Output Templates
 
 When implementing .NET features, provide:
@@ -80,7 +136,3 @@ When implementing .NET features, provide:
 3. API endpoints or service implementations
 4. Database context and migrations if applicable
 5. Brief explanation of architectural decisions
-
-## Knowledge Reference
-
-.NET 8, C# 12, ASP.NET Core, minimal APIs, Entity Framework Core, MediatR, CQRS, clean architecture, dependency injection, JWT authentication, xUnit, Docker, Kubernetes, AOT compilation, OpenAPI/Swagger
diff --git a/skills/embedded-systems/SKILL.md b/skills/embedded-systems/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: embedded-systems
-description: Use when developing firmware for microcontrollers, implementing RTOS applications, or optimizing power consumption. Invoke for STM32, ESP32, FreeRTOS, bare-metal, power optimization, real-time systems.
+description: Use when developing firmware for microcontrollers, implementing RTOS applications, or optimizing power consumption. Invoke for STM32, ESP32, FreeRTOS, bare-metal, power optimization, real-time systems, configure peripherals, write interrupt handlers, implement DMA transfers, debug timing issues.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,14 @@ metadata:
 
 Senior embedded systems engineer with deep expertise in microcontroller programming, RTOS implementation, and hardware-software integration for resource-constrained devices.
 
-## Role Definition
-
-You are a senior embedded systems engineer with 10+ years of firmware development experience. You specialize in ARM Cortex-M, ESP32, FreeRTOS, bare-metal programming, and real-time systems. You build reliable, efficient firmware that meets strict timing, power, and resource constraints.
-
-## When to Use This Skill
-
-- Developing firmware for microcontrollers (STM32, ESP32, Nordic, etc.)
-- Implementing RTOS-based applications (FreeRTOS, Zephyr)
-- Creating hardware drivers and HAL layers
-- Optimizing power consumption and memory usage
-- Building real-time systems with strict timing requirements
-- Implementing communication protocols (I2C, SPI, UART, CAN)
-
 ## Core Workflow
 
 1. **Analyze constraints** - Identify MCU specs, memory limits, timing requirements, power budget
 2. **Design architecture** - Plan task structure, interrupts, peripherals, memory layout
 3. **Implement drivers** - Write HAL, peripheral drivers, RTOS integration
-4. **Optimize resources** - Minimize code size, RAM usage, power consumption
-5. **Test and verify** - Validate timing, test edge cases, measure performance
+4. **Validate implementation** - Compile with `-Wall -Werror`, verify no warnings; run static analysis (e.g. `cppcheck`); confirm correct register bit-field usage against datasheet
+5. **Optimize resources** - Minimize code size, RAM usage, power consumption
+6. **Test and verify** - Validate timing with logic analyzer or oscilloscope; check stack usage with `uxTaskGetStackHighWaterMark()`; measure ISR latency; confirm no missed deadlines under worst-case load; if issues found, return to step 4
 
 ## Reference Guide
 
@@ -54,8 +42,8 @@ Load detailed guidance based on context:
 
 ### MUST DO
 - Optimize for code size and RAM usage
-- Use volatile for hardware registers
-- Implement proper interrupt handling (short ISRs)
+- Use `volatile` for hardware registers and ISR-shared variables
+- Implement proper interrupt handling (short ISRs, defer work to tasks)
 - Add watchdog timer for reliability
 - Use proper synchronization primitives
 - Document resource usage (flash, RAM, power)
@@ -72,6 +60,103 @@ Load detailed guidance based on context:
 - Hardcode hardware-specific values
 - Ignore power consumption requirements
 
+## Code Templates
+
+### Minimal ISR Pattern (ARM Cortex-M / STM32 HAL)
+
+```c
+/* Flag shared between ISR and task — must be volatile */
+static volatile uint8_t g_uart_rx_flag = 0;
+static volatile uint8_t g_uart_rx_byte = 0;
+
+/* Keep ISR short: read hardware, set flag, exit */
+void USART2_IRQHandler(void) {
+    if (USART2->SR & USART_SR_RXNE) {
+        g_uart_rx_byte = (uint8_t)(USART2->DR & 0xFF); /* clears RXNE */
+        g_uart_rx_flag = 1;
+    }
+}
+
+/* Main loop or RTOS task processes the flag */
+void process_uart(void) {
+    if (g_uart_rx_flag) {
+        __disable_irq();                   /* enter critical section */
+        uint8_t byte = g_uart_rx_byte;
+        g_uart_rx_flag = 0;
+        __enable_irq();                    /* exit critical section  */
+        handle_byte(byte);
+    }
+}
+```
+
+### FreeRTOS Task Creation Skeleton
+
+```c
+#include "FreeRTOS.h"
+#include "task.h"
+#include "queue.h"
+
+#define SENSOR_TASK_STACK  256   /* words */
+#define SENSOR_TASK_PRIO   2
+
+static QueueHandle_t xSensorQueue;
+
+static void vSensorTask(void *pvParameters) {
+    TickType_t xLastWakeTime = xTaskGetTickCount();
+    const TickType_t xPeriod  = pdMS_TO_TICKS(10); /* 10 ms period */
+
+    for (;;) {
+        /* Periodic, deadline-driven read */
+        uint16_t raw = adc_read_channel(ADC_CH0);
+        xQueueSend(xSensorQueue, &raw, 0); /* non-blocking send */
+
+        /* Check stack headroom in debug builds */
+        configASSERT(uxTaskGetStackHighWaterMark(NULL) > 32);
+
+        vTaskDelayUntil(&xLastWakeTime, xPeriod);
+    }
+}
+
+void app_init(void) {
+    xSensorQueue = xQueueCreate(8, sizeof(uint16_t));
+    configASSERT(xSensorQueue != NULL);
+
+    xTaskCreate(vSensorTask, "Sensor", SENSOR_TASK_STACK,
+                NULL, SENSOR_TASK_PRIO, NULL);
+    vTaskStartScheduler();
+}
+```
+
+### GPIO + Timer-Interrupt Blink (Bare-Metal STM32)
+
+```c
+/* Demonstrates: clock enable, register-level GPIO, TIM2 interrupt */
+#include "stm32f4xx.h"
+
+void TIM2_IRQHandler(void) {
+    if (TIM2->SR & TIM_SR_UIF) {
+        TIM2->SR &= ~TIM_SR_UIF;           /* clear update flag */
+        GPIOA->ODR ^= GPIO_ODR_OD5;        /* toggle LED on PA5  */
+    }
+}
+
+void blink_init(void) {
+    /* GPIO */
+    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
+    GPIOA->MODER |= GPIO_MODER_MODER5_0;  /* PA5 output */
+
+    /* TIM2 @ ~1 Hz (84 MHz APB1 × 2 = 84 MHz timer clock) */
+    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;
+    TIM2->PSC  = 8399;   /* /8400  → 10 kHz  */
+    TIM2->ARR  = 9999;   /* /10000 → 1 Hz    */
+    TIM2->DIER |= TIM_DIER_UIE;
+    TIM2->CR1  |= TIM_CR1_CEN;
+
+    NVIC_SetPriority(TIM2_IRQn, 6);
+    NVIC_EnableIRQ(TIM2_IRQn);
+}
+```
+
 ## Output Templates
 
 When implementing embedded features, provide:
@@ -80,7 +165,3 @@ When implementing embedded features, provide:
 3. Application code (RTOS tasks or main loop)
 4. Resource usage summary (flash, RAM, power estimate)
 5. Brief explanation of timing and optimization decisions
-
-## Knowledge Reference
-
-ARM Cortex-M, STM32, ESP32, Nordic nRF, FreeRTOS, Zephyr, bare-metal, interrupts, DMA, timers, ADC/DAC, I2C, SPI, UART, CAN, low-power modes, JTAG/SWD, memory-mapped I/O, bootloaders, OTA updates
diff --git a/skills/fastapi-expert/SKILL.md b/skills/fastapi-expert/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: fastapi-expert
-description: Use when building high-performance async Python APIs with FastAPI and Pydantic V2. Invoke for async SQLAlchemy, JWT authentication, WebSockets, OpenAPI documentation.
+description: "Use when building high-performance async Python APIs with FastAPI and Pydantic V2. Invoke to create REST endpoints, define Pydantic models, implement authentication flows, set up async SQLAlchemy database operations, add JWT authentication, build WebSocket endpoints, or generate OpenAPI documentation. Trigger terms: FastAPI, Pydantic, async Python, Python API, REST API Python, SQLAlchemy async, JWT authentication, OpenAPI, Swagger Python."
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,11 +15,7 @@ metadata:
 
 # FastAPI Expert
 
-Senior FastAPI specialist with deep expertise in async Python, Pydantic V2, and production-grade API development.
-
-## Role Definition
-
-You are a senior Python engineer with 10+ years of API development experience. You specialize in FastAPI with Pydantic V2, async SQLAlchemy, and modern Python 3.11+ patterns. You build scalable, type-safe APIs with automatic documentation.
+Deep expertise in async Python, Pydantic V2, and production-grade API development with FastAPI.
 
 ## When to Use This Skill
 
@@ -32,11 +28,116 @@ You are a senior Python engineer with 10+ years of API development experience. Y
 
 ## Core Workflow
 
-1. **Analyze requirements** - Identify endpoints, data models, auth needs
-2. **Design schemas** - Create Pydantic V2 models for validation
-3. **Implement** - Write async endpoints with proper dependency injection
-4. **Secure** - Add authentication, authorization, rate limiting
-5. **Test** - Write async tests with pytest and httpx
+1. **Analyze requirements** — Identify endpoints, data models, auth needs
+2. **Design schemas** — Create Pydantic V2 models for validation
+3. **Implement** — Write async endpoints with proper dependency injection
+4. **Secure** — Add authentication, authorization, rate limiting
+5. **Test** — Write async tests with pytest and httpx; run `pytest` after each endpoint group and verify OpenAPI docs at `/docs`
+
+> **Checkpoint after each step:** confirm schemas validate correctly, endpoints return expected HTTP status codes, and `/docs` reflects the intended API surface before proceeding.
+
+## Minimal Complete Example
+
+Schema + endpoint + dependency injection in one cohesive unit:
+
+```python
+# schemas.py
+from pydantic import BaseModel, EmailStr, field_validator, model_config
+
+class UserCreate(BaseModel):
+    model_config = model_config(str_strip_whitespace=True)
+
+    email: EmailStr
+    password: str
+    name: str | None = None
+
+    @field_validator("password")
+    @classmethod
+    def password_strength(cls, v: str) -> str:
+        if len(v) < 8:
+            raise ValueError("Password must be at least 8 characters")
+        return v
+
+class UserResponse(BaseModel):
+    model_config = model_config(from_attributes=True)
+
+    id: int
+    email: EmailStr
+    name: str | None = None
+```
+
+```python
+# routers/users.py
+from fastapi import APIRouter, Depends, HTTPException, status
+from sqlalchemy.ext.asyncio import AsyncSession
+from typing import Annotated
+
+from app.database import get_db
+from app.schemas import UserCreate, UserResponse
+from app import crud
+
+router = APIRouter(prefix="/users", tags=["users"])
+
+DbDep = Annotated[AsyncSession, Depends(get_db)]
+
+@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
+async def create_user(payload: UserCreate, db: DbDep) -> UserResponse:
+    existing = await crud.get_user_by_email(db, payload.email)
+    if existing:
+        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
+    return await crud.create_user(db, payload)
+```
+
+```python
+# crud.py
+from sqlalchemy import select
+from sqlalchemy.ext.asyncio import AsyncSession
+from app.models import User
+from app.schemas import UserCreate
+from app.security import hash_password
+
+async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
+    result = await db.execute(select(User).where(User.email == email))
+    return result.scalar_one_or_none()
+
+async def create_user(db: AsyncSession, payload: UserCreate) -> User:
+    user = User(email=payload.email, hashed_password=hash_password(payload.password), name=payload.name)
+    db.add(user)
+    await db.commit()
+    await db.refresh(user)
+    return user
+```
+
+## JWT Authentication Snippet
+
+```python
+# security.py
+from datetime import datetime, timedelta, timezone
+from jose import JWTError, jwt
+from fastapi import Depends, HTTPException, status
+from fastapi.security import OAuth2PasswordBearer
+from typing import Annotated
+
+SECRET_KEY = "read-from-env"  # use os.environ / settings
+ALGORITHM = "HS256"
+oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
+
+def create_access_token(subject: str, expires_delta: timedelta = timedelta(minutes=30)) -> str:
+    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + expires_delta}
+    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
+
+async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
+    try:
+        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
+        subject: str | None = data.get("sub")
+        if subject is None:
+            raise ValueError
+        return subject
+    except (JWTError, ValueError):
+        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
+
+CurrentUser = Annotated[str, Depends(get_current_user)]
+```
 
 ## Reference Guide
 
diff --git a/skills/feature-forge/SKILL.md b/skills/feature-forge/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: feature-forge
-description: Use when defining new features, gathering requirements, or writing specifications. Invoke for feature definition, requirements gathering, user stories, EARS format specs.
+description: Conducts structured requirements workshops to produce feature specifications, user stories, EARS-format functional requirements, acceptance criteria, and implementation checklists. Use when defining new features, gathering requirements, or writing specifications. Invoke for feature definition, requirements gathering, user stories, EARS format specs, PRDs, acceptance criteria, or requirement matrices.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -19,7 +19,7 @@ Requirements specialist conducting structured workshops to define comprehensive
 
 ## Role Definition
 
-You are a senior product analyst with 10+ years of experience. You operate with two perspectives:
+Operate with two perspectives:
 - **PM Hat**: Focused on user value, business goals, success metrics
 - **Dev Hat**: Focused on technical feasibility, security, performance, edge cases
 
@@ -81,8 +81,18 @@ The final specification must include:
 5. Error handling table
 6. Implementation TODO checklist
 
-Save as: `specs/{feature_name}.spec.md`
+**Inline EARS format examples** (load `references/ears-syntax.md` for full syntax):
+```
+When <trigger>, the <system> shall <response>.
+Where <feature> is active, the <system> shall <behaviour>.
+The <system> shall <action> within <measure>.
+```
 
-## Knowledge Reference
+**Inline acceptance criteria example** (load `references/acceptance-criteria.md` for full format):
+```
+Given a registered user is on the login page,
+When they submit valid credentials,
+Then they are redirected to the dashboard within 2 seconds.
+```
 
-EARS syntax, user stories, acceptance criteria, Given-When-Then, INVEST criteria, MoSCoW prioritization, OWASP security requirements
+Save as: `specs/{feature_name}.spec.md`
diff --git a/skills/fine-tuning-expert/SKILL.md b/skills/fine-tuning-expert/SKILL.md
@@ -1,12 +1,12 @@
 ---
 name: fine-tuning-expert
-description: Use when fine-tuning LLMs, training custom models, or optimizing model performance for specific tasks. Invoke for parameter-efficient methods, dataset preparation, or model adaptation.
+description: "Use when fine-tuning LLMs, training custom models, or adapting foundation models for specific tasks. Invoke for configuring LoRA/QLoRA adapters, preparing JSONL training datasets, setting hyperparameters for fine-tuning runs, adapter training, transfer learning, finetuning with Hugging Face PEFT, OpenAI fine-tuning, instruction tuning, RLHF, DPO, or quantizing and deploying fine-tuned models. Trigger terms include: LoRA, QLoRA, PEFT, finetuning, fine-tuning, adapter tuning, LLM training, model training, custom model."
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
   version: "1.0.0"
   domain: data-ml
-  triggers: fine-tuning, fine tuning, LoRA, QLoRA, PEFT, adapter tuning, transfer learning, model training, custom model, LLM training, instruction tuning, RLHF, model optimization, quantization
+  triggers: fine-tuning, fine tuning, finetuning, LoRA, QLoRA, PEFT, adapter tuning, transfer learning, model training, custom model, LLM training, instruction tuning, RLHF, model optimization, quantization
   role: expert
   scope: implementation
   output-format: code
@@ -17,27 +17,17 @@ metadata:
 
 Senior ML engineer specializing in LLM fine-tuning, parameter-efficient methods, and production model optimization.
 
-## Role Definition
-
-You are a senior ML engineer with deep experience in model training and fine-tuning. You specialize in parameter-efficient fine-tuning (PEFT) methods like LoRA/QLoRA, instruction tuning, and optimizing models for production deployment. You understand training dynamics, dataset quality, and evaluation methodologies.
-
-## When to Use This Skill
-
-- Fine-tuning foundation models for specific tasks
-- Implementing LoRA, QLoRA, or other PEFT methods
-- Preparing and validating training datasets
-- Optimizing hyperparameters for training
-- Evaluating fine-tuned models
-- Merging adapters and quantizing models
-- Deploying fine-tuned models to production
-
 ## Core Workflow
 
-1. **Dataset preparation** - Collect, format, validate training data quality
-2. **Method selection** - Choose PEFT technique based on resources and task
-3. **Training** - Configure hyperparameters, monitor loss, prevent overfitting
-4. **Evaluation** - Benchmark against baselines, test edge cases
-5. **Deployment** - Merge/quantize model, optimize inference, serve
+1. **Dataset preparation** — Validate and format data; run quality checks before training starts
+   - Checkpoint: `python validate_dataset.py --input data.jsonl` — fix all errors before proceeding
+2. **Method selection** — Choose PEFT technique based on GPU memory and task requirements
+   - Use LoRA for most tasks; QLoRA (4-bit) when GPU memory is constrained; full fine-tune only for small models
+3. **Training** — Configure hyperparameters, monitor loss curves, checkpoint regularly
+   - Checkpoint: validation loss must decrease; plateau or increase signals overfitting
+4. **Evaluation** — Benchmark against the base model; test on held-out set and edge cases
+   - Checkpoint: collect perplexity, task-specific metrics (BLEU/ROUGE), and latency numbers
+5. **Deployment** — Merge adapter weights, quantize, measure inference throughput before serving
 
 ## Reference Guide
 
@@ -51,34 +41,122 @@ Load detailed guidance based on context:
 | Evaluation | `references/evaluation-metrics.md` | Benchmarking, metrics, model comparison |
 | Deployment | `references/deployment-optimization.md` | Model merging, quantization, serving |
 
+## Minimal Working Example — LoRA Fine-Tuning with Hugging Face PEFT
+
+```python
+from datasets import load_dataset
+from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
+from peft import LoraConfig, get_peft_model, TaskType
+from trl import SFTTrainer
+import torch
+
+# 1. Load base model and tokenizer
+model_id = "meta-llama/Llama-3-8B"
+tokenizer = AutoTokenizer.from_pretrained(model_id)
+tokenizer.pad_token = tokenizer.eos_token
+
+model = AutoModelForCausalLM.from_pretrained(
+    model_id,
+    torch_dtype=torch.bfloat16,
+    device_map="auto",
+)
+
+# 2. Configure LoRA adapter
+lora_config = LoraConfig(
+    task_type=TaskType.CAUSAL_LM,
+    r=16,               # rank — increase for more capacity, decrease to save memory
+    lora_alpha=32,      # scaling factor; typically 2× rank
+    target_modules=["q_proj", "v_proj"],
+    lora_dropout=0.05,
+    bias="none",
+)
+model = get_peft_model(model, lora_config)
+model.print_trainable_parameters()  # verify: should be ~0.1–1% of total params
+
+# 3. Load and format dataset (Alpaca-style JSONL)
+dataset = load_dataset("json", data_files={"train": "train.jsonl", "test": "test.jsonl"})
+
+def format_prompt(example):
+    return {"text": f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['output']}"}
+
+dataset = dataset.map(format_prompt)
+
+# 4. Training arguments
+training_args = TrainingArguments(
+    output_dir="./checkpoints",
+    num_train_epochs=3,
+    per_device_train_batch_size=4,
+    gradient_accumulation_steps=4,     # effective batch size = 16
+    learning_rate=2e-4,
+    lr_scheduler_type="cosine",
+    warmup_ratio=0.03,                 # always use warmup
+    fp16=False,
+    bf16=True,
+    logging_steps=10,
+    eval_strategy="steps",
+    eval_steps=100,
+    save_steps=200,
+    load_best_model_at_end=True,
+)
+
+# 5. Train
+trainer = SFTTrainer(
+    model=model,
+    args=training_args,
+    train_dataset=dataset["train"],
+    eval_dataset=dataset["test"],
+    dataset_text_field="text",
+    max_seq_length=2048,
+)
+trainer.train()
+
+# 6. Save adapter weights only
+model.save_pretrained("./lora-adapter")
+tokenizer.save_pretrained("./lora-adapter")
+```
+
+**QLoRA variant** — add these lines before loading the model to enable 4-bit quantization:
+```python
+from transformers import BitsAndBytesConfig
+
+bnb_config = BitsAndBytesConfig(
+    load_in_4bit=True,
+    bnb_4bit_quant_type="nf4",
+    bnb_4bit_compute_dtype=torch.bfloat16,
+    bnb_4bit_use_double_quant=True,
+)
+model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config, device_map="auto")
+```
+
+**Merge adapter into base model for deployment:**
+```python
+from peft import PeftModel
+
+base = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16)
+merged = PeftModel.from_pretrained(base, "./lora-adapter").merge_and_unload()
+merged.save_pretrained("./merged-model")
+```
+
 ## Constraints
 
 ### MUST DO
 - Validate dataset quality before training
 - Use parameter-efficient methods for large models (>7B)
 - Monitor training/validation loss curves
-- Test on held-out evaluation set
 - Document hyperparameters and training config
 - Version datasets and model checkpoints
-- Measure inference latency and throughput
+- Always include a learning rate warmup
 
 ### MUST NOT DO
-- Train on test data
 - Skip data quality validation
-- Use learning rate without warmup
-- Overfit on small datasets
-- Merge incompatible adapters
-- Deploy without evaluation
-- Ignore GPU memory constraints
+- Overfit on small datasets — use regularisation (dropout, weight decay) and early stopping
+- Merge incompatible adapters (mismatched rank, base model, or target modules)
+- Deploy without evaluation against a held-out set and latency benchmark
 
 ## Output Templates
 
-When implementing fine-tuning, provide:
-1. Dataset preparation script with validation
-2. Training configuration file
-3. Evaluation script with metrics
-4. Brief explanation of design choices
-
-## Knowledge Reference
-
-Hugging Face Transformers, PEFT library, bitsandbytes, LoRA/QLoRA, Axolotl, DeepSpeed, FSDP, instruction tuning, RLHF, DPO, dataset formatting (Alpaca, ShareGPT), evaluation (perplexity, BLEU, ROUGE), quantization (GPTQ, AWQ, GGUF), vLLM, TGI
+When implementing fine-tuning, always provide:
+1. **Dataset preparation script** with validation logic (schema checks, token-length histogram, deduplication)
+2. **Training configuration** (full `TrainingArguments` + `LoraConfig` block, commented)
+3. **Evaluation script** reporting perplexity, task-specific metrics, and latency
+4. **Brief design rationale** — why this PEFT method, rank, and learning rate were chosen for this task
diff --git a/skills/flutter-expert/SKILL.md b/skills/flutter-expert/SKILL.md
@@ -17,10 +17,6 @@ metadata:
 
 Senior mobile engineer building high-performance cross-platform applications with Flutter 3 and Dart.
 
-## Role Definition
-
-You are a senior Flutter developer with 6+ years of experience. You specialize in Flutter 3.19+, Riverpod 2.0, GoRouter, and building apps for iOS, Android, Web, and Desktop. You write performant, maintainable Dart code with proper state management.
-
 ## When to Use This Skill
 
 - Building cross-platform Flutter applications
@@ -32,11 +28,15 @@ You are a senior Flutter developer with 6+ years of experience. You specialize i
 
 ## Core Workflow
 
-1. **Setup** - Project structure, dependencies, routing
-2. **State** - Riverpod providers or Bloc setup
-3. **Widgets** - Reusable, const-optimized components
-4. **Test** - Widget tests, integration tests
-5. **Optimize** - Profile, reduce rebuilds
+1. **Setup** — Scaffold project, add dependencies (`flutter pub get`), configure routing
+2. **State** — Define Riverpod providers or Bloc/Cubit classes; verify with `flutter analyze`
+   - If `flutter analyze` reports issues: fix all lints and warnings before proceeding; re-run until clean
+3. **Widgets** — Build reusable, const-optimized components; run `flutter test` after each feature
+   - If tests fail: inspect widget tree with Flutter DevTools, fix failing assertions, re-run `flutter test`
+4. **Test** — Write widget and integration tests; confirm with `flutter test --coverage`
+   - If coverage drops or tests fail: identify untested branches, add targeted tests, re-run before merging
+5. **Optimize** — Profile with Flutter DevTools (`flutter run --profile`), eliminate jank, reduce rebuilds
+   - If jank persists: check rebuild counts in the Performance overlay, isolate expensive `build()` calls, apply `const` or move state closer to consumers
 
 ## Reference Guide
 
@@ -51,32 +51,88 @@ Load detailed guidance based on context:
 | Structure | `references/project-structure.md` | Setting up project, architecture |
 | Performance | `references/performance.md` | Optimization, profiling, jank fixes |
 
+## Code Examples
+
+### Riverpod Provider + ConsumerWidget (correct pattern)
+
+```dart
+// provider definition
+final counterProvider = StateNotifierProvider<CounterNotifier, int>(
+  (ref) => CounterNotifier(),
+);
+
+class CounterNotifier extends StateNotifier<int> {
+  CounterNotifier() : super(0);
+  void increment() => state = state + 1; // new instance, never mutate
+}
+
+// consuming widget — use ConsumerWidget, not StatefulWidget
+class CounterView extends ConsumerWidget {
+  const CounterView({super.key});
+
+  @override
+  Widget build(BuildContext context, WidgetRef ref) {
+    final count = ref.watch(counterProvider);
+    return Text('$count');
+  }
+}
+```
+
+### Before / After — State Management
+
+```dart
+// ❌ WRONG: app-wide state in setState
+class _BadCounterState extends State<BadCounter> {
+  int _count = 0;
+  void _inc() => setState(() => _count++); // causes full subtree rebuild
+}
+
+// ✅ CORRECT: scoped Riverpod consumer
+class GoodCounter extends ConsumerWidget {
+  const GoodCounter({super.key});
+  @override
+  Widget build(BuildContext context, WidgetRef ref) {
+    final count = ref.watch(counterProvider);
+    return IconButton(
+      onPressed: () => ref.read(counterProvider.notifier).increment(),
+      icon: const Icon(Icons.add), // const on static widgets
+    );
+  }
+}
+```
+
 ## Constraints
 
 ### MUST DO
-- Use const constructors wherever possible
+- Use `const` constructors wherever possible
 - Implement proper keys for lists
-- Use Consumer/ConsumerWidget for state (not StatefulWidget)
+- Use `Consumer`/`ConsumerWidget` for state (not `StatefulWidget`)
 - Follow Material/Cupertino design guidelines
 - Profile with DevTools, fix jank
-- Test widgets with flutter_test
+- Test widgets with `flutter_test`
 
 ### MUST NOT DO
-- Build widgets inside build() method
+- Build widgets inside `build()` method
 - Mutate state directly (always create new instances)
-- Use setState for app-wide state
-- Skip const on static widgets
+- Use `setState` for app-wide state
+- Skip `const` on static widgets
 - Ignore platform-specific behavior
-- Block UI thread with heavy computation (use compute())
+- Block UI thread with heavy computation (use `compute()`)
+
+## Troubleshooting Common Failures
+
+| Symptom | Likely Cause | Recovery |
+|---------|-------------|----------|
+| `flutter analyze` errors | Unresolved imports, missing `const`, type mismatches | Fix flagged lines; run `flutter pub get` if imports are missing |
+| Widget test assertion failures | Widget tree mismatch or async state not settled | Use `tester.pumpAndSettle()` after state changes; verify finder selectors |
+| Build fails after adding package | Incompatible dependency version | Run `flutter pub upgrade --major-versions`; check pub.dev compatibility |
+| Jank / dropped frames | Expensive `build()` calls, uncached widgets, heavy main-thread work | Use `RepaintBoundary`, move heavy work to `compute()`, add `const` |
+| Hot reload not reflecting changes | State held in `StateNotifier` not reset | Use hot restart (`R` in terminal) to reset full app state |
 
 ## Output Templates
 
 When implementing Flutter features, provide:
-1. Widget code with proper const usage
+1. Widget code with proper `const` usage
 2. Provider/Bloc definitions
 3. Route configuration if needed
 4. Test file structure
-
-## Knowledge Reference
-
-Flutter 3.19+, Dart 3.3+, Riverpod 2.0, Bloc 8.x, GoRouter, freezed, json_serializable, Dio, flutter_hooks
diff --git a/skills/fullstack-guardian/SKILL.md b/skills/fullstack-guardian/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: fullstack-guardian
-description: Use when implementing features across frontend and backend, building APIs with UI, or creating end-to-end data flows. Invoke for feature implementation, API development, UI building, cross-stack work.
+description: Builds security-focused full-stack web applications by implementing integrated frontend and backend components with layered security at every level. Covers the complete stack from database to UI, enforcing auth, input validation, output encoding, and parameterized queries across all layers. Use when implementing features across frontend and backend, building REST APIs with corresponding UI, connecting frontend components to backend endpoints, creating end-to-end data flows from database to UI, or implementing CRUD operations with UI forms. Distinct from frontend-only, backend-only, or API-only skills in that it simultaneously addresses all three perspectives—Frontend, Backend, and Security—within a single implementation workflow. Invoke for full-stack feature work, web app development, authenticated API routes with views, microservices, real-time features, monorepo architecture, or technology selection decisions.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,25 +17,14 @@ metadata:
 
 Security-focused full-stack developer implementing features across the entire application stack.
 
-## Role Definition
-
-You are a senior full-stack engineer with 12+ years of experience. You think in three layers: **[Frontend]** for user experience, **[Backend]** for data and logic, **[Security]** for protection. You implement features end-to-end with security built-in from the start.
-
-## When to Use This Skill
-
-- Implementing new features across frontend and backend
-- Building APIs with corresponding UI
-- Creating data flows from database to UI
-- Features requiring authentication/authorization
-- Cross-cutting concerns (logging, caching, validation)
-
 ## Core Workflow
 
 1. **Gather requirements** - Understand feature scope and acceptance criteria
 2. **Design solution** - Consider all three perspectives (Frontend/Backend/Security)
 3. **Write technical design** - Document approach in `specs/{feature}_design.md`
-4. **Implement** - Build incrementally, testing as you go
-5. **Hand off** - Pass to Test Master for QA, DevOps for deployment
+4. **Security checkpoint** - Run through `references/security-checklist.md` before writing any code; confirm auth, authz, validation, and output encoding are addressed
+5. **Implement** - Build incrementally, testing each component as you go
+6. **Hand off** - Pass to Test Master for QA, DevOps for deployment
 
 ## Reference Guide
 
@@ -74,6 +63,39 @@ Load detailed guidance based on context:
 - Implement features without acceptance criteria
 - Skip error handling for "happy path only"
 
+## Three-Perspective Example
+
+A minimal authenticated endpoint illustrating all three layers:
+
+**[Backend]** — Authenticated route with parameterized query and scoped response:
+```python
+@router.get("/users/{user_id}/profile", dependencies=[Depends(require_auth)])
+async def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
+    if current_user.id != user_id:
+        raise HTTPException(status_code=403, detail="Forbidden")
+    # Parameterized query — no raw string interpolation
+    row = await db.fetchone("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
+    if not row:
+        raise HTTPException(status_code=404, detail="Not found")
+    return ProfileResponse(**row)   # explicit schema — no password/token leakage
+```
+
+**[Frontend]** — Component calls the endpoint and handles errors gracefully:
+```typescript
+async function fetchProfile(userId: number): Promise<Profile> {
+  const res = await apiFetch(`/users/${userId}/profile`);   // apiFetch attaches auth header
+  if (!res.ok) throw new Error(await res.text());
+  return res.json();
+}
+// Client-side input guard (never the only guard)
+if (!Number.isInteger(userId) || userId <= 0) throw new Error("Invalid user ID");
+```
+
+**[Security]**
+- Auth enforced server-side via `require_auth` dependency; client header is a convenience, not the gate.
+- Response schema (`ProfileResponse`) explicitly excludes sensitive fields.
+- 403 returned before any DB access when IDs don't match — no timing leak via 404.
+
 ## Output Templates
 
 When implementing features, provide:
diff --git a/skills/game-developer/SKILL.md b/skills/game-developer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: game-developer
-description: Use when building game systems, implementing Unity/Unreal features, or optimizing game performance. Invoke for Unity, Unreal, game patterns, ECS, physics, networking, performance optimization.
+description: "Use when building game systems, implementing Unity/Unreal Engine features, or optimizing game performance. Invoke to implement ECS architecture, configure physics systems and colliders, set up multiplayer networking with lag compensation, optimize frame rates to 60+ FPS targets, develop shaders, or apply game design patterns such as object pooling and state machines. Trigger keywords: Unity, Unreal Engine, game development, ECS architecture, game physics, multiplayer networking, game optimization, shader programming, game AI."
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,28 +15,15 @@ metadata:
 
 # Game Developer
 
-Senior game developer with expertise in creating high-performance gaming experiences across Unity, Unreal, and custom engines.
-
-## Role Definition
-
-You are a senior game developer with 10+ years of experience in game engine programming, graphics optimization, and multiplayer systems. You specialize in Unity C#, Unreal C++, ECS architecture, and cross-platform optimization. You build engaging, performant games that run smoothly across all target platforms.
-
-## When to Use This Skill
-
-- Building game systems (ECS, physics, AI, networking)
-- Implementing Unity or Unreal Engine features
-- Optimizing game performance (60+ FPS targets)
-- Creating multiplayer/networking architecture
-- Developing shaders and graphics pipelines
-- Implementing game design patterns (object pooling, state machines)
-
 ## Core Workflow
 
-1. **Analyze requirements** - Identify genre, platforms, performance targets, multiplayer needs
-2. **Design architecture** - Plan ECS/component systems, optimize for target platforms
-3. **Implement** - Build core mechanics, graphics, physics, AI, networking
-4. **Optimize** - Profile and optimize for 60+ FPS, minimize memory/battery usage
-5. **Test** - Cross-platform testing, performance validation, multiplayer stress tests
+1. **Analyze requirements** — Identify genre, platforms, performance targets, multiplayer needs
+2. **Design architecture** — Plan ECS/component systems, optimize for target platforms
+3. **Implement** — Build core mechanics, graphics, physics, AI, networking
+4. **Optimize** — Profile and optimize for 60+ FPS, minimize memory/battery usage
+   - ✅ **Validation checkpoint:** Run Unity Profiler or Unreal Insights; verify frame time ≤16 ms (60 FPS) before proceeding. Identify and resolve CPU/GPU bottlenecks iteratively.
+5. **Test** — Cross-platform testing, performance validation, multiplayer stress tests
+   - ✅ **Validation checkpoint:** Confirm stable frame rate under stress load; run multiplayer latency/desync tests before shipping.
 
 ## Reference Guide
 
@@ -79,6 +66,96 @@ When implementing game features, provide:
 3. Performance considerations and optimizations
 4. Brief explanation of architecture decisions
 
-## Knowledge Reference
-
-Unity C#, Unreal C++, Entity Component System (ECS), object pooling, state machines, command pattern, observer pattern, physics optimization, shader programming (HLSL/GLSL), multiplayer networking, client-server architecture, lag compensation, client prediction, performance profiling, LOD systems, occlusion culling, draw call batching
+## Key Code Patterns
+
+### Object Pooling (Unity C#)
+```csharp
+public class ObjectPool<T> where T : Component
+{
+    private readonly Queue<T> _pool = new();
+    private readonly T _prefab;
+    private readonly Transform _parent;
+
+    public ObjectPool(T prefab, int initialSize, Transform parent = null)
+    {
+        _prefab = prefab;
+        _parent = parent;
+        for (int i = 0; i < initialSize; i++)
+            Release(Create());
+    }
+
+    public T Get()
+    {
+        T obj = _pool.Count > 0 ? _pool.Dequeue() : Create();
+        obj.gameObject.SetActive(true);
+        return obj;
+    }
+
+    public void Release(T obj)
+    {
+        obj.gameObject.SetActive(false);
+        _pool.Enqueue(obj);
+    }
+
+    private T Create() => Object.Instantiate(_prefab, _parent);
+}
+```
+
+### Component Caching (Unity C#)
+```csharp
+public class PlayerController : MonoBehaviour
+{
+    // Cache all component references in Awake — never call GetComponent in Update
+    private Rigidbody _rb;
+    private Animator _animator;
+    private PlayerInput _input;
+
+    private void Awake()
+    {
+        _rb = GetComponent<Rigidbody>();
+        _animator = GetComponent<Animator>();
+        _input = GetComponent<PlayerInput>();
+    }
+
+    private void FixedUpdate()
+    {
+        // Use cached references; use deltaTime for frame-independence
+        Vector3 move = _input.MoveDirection * (speed * Time.fixedDeltaTime);
+        _rb.MovePosition(_rb.position + move);
+    }
+}
+```
+
+### State Machine (Unity C#)
+```csharp
+public abstract class State
+{
+    public abstract void Enter();
+    public abstract void Tick(float deltaTime);
+    public abstract void Exit();
+}
+
+public class StateMachine
+{
+    private State _current;
+
+    public void TransitionTo(State next)
+    {
+        _current?.Exit();
+        _current = next;
+        _current.Enter();
+    }
+
+    public void Tick(float deltaTime) => _current?.Tick(deltaTime);
+}
+
+// Usage example
+public class IdleState : State
+{
+    private readonly Animator _animator;
+    public IdleState(Animator animator) => _animator = animator;
+    public override void Enter() => _animator.SetTrigger("Idle");
+    public override void Tick(float deltaTime) { /* poll transitions */ }
+    public override void Exit() { }
+}
+```
diff --git a/skills/golang-pro/SKILL.md b/skills/golang-pro/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: golang-pro
-description: Use when building Go applications requiring concurrent programming, microservices architecture, or high-performance systems. Invoke for goroutines, channels, Go generics, gRPC integration.
+description: Implements concurrent Go patterns using goroutines and channels, designs and builds microservices with gRPC or REST, optimizes Go application performance with pprof, and enforces idiomatic Go with generics, interfaces, and robust error handling. Use when building Go applications requiring concurrent programming, microservices architecture, or high-performance systems. Invoke for goroutines, channels, Go generics, gRPC integration, CLI tools, benchmarks, or table-driven testing.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,14 @@ metadata:
 
 Senior Go developer with deep expertise in Go 1.21+, concurrent programming, and cloud-native microservices. Specializes in idiomatic patterns, performance optimization, and production-grade systems.
 
-## Role Definition
-
-You are a senior Go engineer with 8+ years of systems programming experience. You specialize in Go 1.21+ with generics, concurrent patterns, gRPC microservices, and cloud-native applications. You build efficient, type-safe systems following Go proverbs.
-
-## When to Use This Skill
-
-- Building concurrent Go applications with goroutines and channels
-- Implementing microservices with gRPC or REST APIs
-- Creating CLI tools and system utilities
-- Optimizing Go code for performance and memory efficiency
-- Designing interfaces and using Go generics
-- Setting up testing with table-driven tests and benchmarks
-
 ## Core Workflow
 
-1. **Analyze architecture** - Review module structure, interfaces, concurrency patterns
-2. **Design interfaces** - Create small, focused interfaces with composition
-3. **Implement** - Write idiomatic Go with proper error handling and context propagation
-4. **Optimize** - Profile with pprof, write benchmarks, eliminate allocations
-5. **Test** - Table-driven tests, race detector, fuzzing, 80%+ coverage
+1. **Analyze architecture** — Review module structure, interfaces, and concurrency patterns
+2. **Design interfaces** — Create small, focused interfaces with composition
+3. **Implement** — Write idiomatic Go with proper error handling and context propagation; run `go vet ./...` before proceeding
+4. **Lint & validate** — Run `golangci-lint run` and fix all reported issues before proceeding
+5. **Optimize** — Profile with pprof, write benchmarks, eliminate allocations
+6. **Test** — Table-driven tests with `-race` flag, fuzzing, 80%+ coverage; confirm race detector passes before committing
 
 ## Reference Guide
 
@@ -50,6 +38,56 @@ Load detailed guidance based on context:
 | Testing | `references/testing.md` | Table-driven tests, benchmarks, fuzzing |
 | Project Structure | `references/project-structure.md` | Module layout, internal packages, go.mod |
 
+## Core Pattern Example
+
+Goroutine with proper context cancellation and error propagation:
+
+```go
+// worker runs until ctx is cancelled or an error occurs.
+// Errors are returned via the errCh channel; the caller must drain it.
+func worker(ctx context.Context, jobs <-chan Job, errCh chan<- error) {
+    for {
+        select {
+        case <-ctx.Done():
+            errCh <- fmt.Errorf("worker cancelled: %w", ctx.Err())
+            return
+        case job, ok := <-jobs:
+            if !ok {
+                return // jobs channel closed; clean exit
+            }
+            if err := process(ctx, job); err != nil {
+                errCh <- fmt.Errorf("process job %v: %w", job.ID, err)
+                return
+            }
+        }
+    }
+}
+
+func runPipeline(ctx context.Context, jobs []Job) error {
+    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
+    defer cancel()
+
+    jobCh := make(chan Job, len(jobs))
+    errCh := make(chan error, 1)
+
+    go worker(ctx, jobCh, errCh)
+
+    for _, j := range jobs {
+        jobCh <- j
+    }
+    close(jobCh)
+
+    select {
+    case err := <-errCh:
+        return err
+    case <-ctx.Done():
+        return fmt.Errorf("pipeline timed out: %w", ctx.Err())
+    }
+}
+```
+
+Key properties demonstrated: bounded goroutine lifetime via `ctx`, error propagation with `%w`, no goroutine leak on cancellation.
+
 ## Constraints
 
 ### MUST DO
diff --git a/skills/graphql-architect/SKILL.md b/skills/graphql-architect/SKILL.md
@@ -17,26 +17,16 @@ metadata:
 
 Senior GraphQL architect specializing in schema design and distributed graph architectures with deep expertise in Apollo Federation 2.5+, GraphQL subscriptions, and performance optimization.
 
-## Role Definition
-
-You are a senior GraphQL architect with 10+ years of API design experience. You specialize in Apollo Federation, schema-first design, and building type-safe API graphs that scale across teams and services. You master resolvers, DataLoader patterns, and real-time subscriptions.
-
-## When to Use This Skill
-
-- Designing GraphQL schemas and type systems
-- Implementing Apollo Federation architectures
-- Building resolvers with DataLoader optimization
-- Creating real-time GraphQL subscriptions
-- Optimizing query complexity and performance
-- Setting up authentication and authorization
-
 ## Core Workflow
 
 1. **Domain Modeling** - Map business domains to GraphQL type system
 2. **Design Schema** - Create types, interfaces, unions with federation directives
-3. **Implement Resolvers** - Write efficient resolvers with DataLoader patterns
-4. **Secure** - Add query complexity limits, depth limiting, field-level auth
-5. **Optimize** - Performance tune with caching, persisted queries, monitoring
+3. **Validate Schema** - Run schema composition check; confirm all `@key` entities resolve correctly
+   - _If composition fails:_ review entity `@key` directives, check for missing or mismatched type definitions across subgraphs, resolve any `@external` field inconsistencies, then re-run composition
+4. **Implement Resolvers** - Write efficient resolvers with DataLoader patterns
+5. **Secure** - Add query complexity limits, depth limiting, field-level auth; validate complexity thresholds before deployment
+   - _If complexity threshold is exceeded:_ identify the highest-cost fields, add pagination limits, restructure nested queries, or raise the threshold with documented justification
+6. **Optimize** - Performance tune with caching, persisted queries, monitoring
 
 ## Reference Guide
 
@@ -73,6 +63,76 @@ Load detailed guidance based on context:
 - Hardcode authorization logic
 - Ignore schema validation
 
+## Code Examples
+
+### Federation Schema (SDL)
+
+```graphql
+# products subgraph
+type Product @key(fields: "id") {
+  id: ID!
+  name: String!
+  price: Float!
+  inStock: Boolean!
+}
+
+# reviews subgraph — extends Product from products subgraph
+type Product @key(fields: "id") {
+  id: ID! @external
+  reviews: [Review!]!
+}
+
+type Review {
+  id: ID!
+  rating: Int!
+  body: String
+  author: User! @shareable
+}
+
+type User @shareable {
+  id: ID!
+  username: String!
+}
+```
+
+### Resolver with DataLoader (N+1 Prevention)
+
+```js
+// context setup — one DataLoader instance per request
+const context = ({ req }) => ({
+  loaders: {
+    user: new DataLoader(async (userIds) => {
+      const users = await db.users.findMany({ where: { id: { in: userIds } } });
+      // return results in same order as input keys
+      return userIds.map((id) => users.find((u) => u.id === id) ?? null);
+    }),
+  },
+});
+
+// resolver — batches all user lookups in a single query
+const resolvers = {
+  Review: {
+    author: (review, _args, { loaders }) => loaders.user.load(review.authorId),
+  },
+};
+```
+
+### Query Complexity Validation
+
+```js
+import { createComplexityRule } from 'graphql-query-complexity';
+
+const server = new ApolloServer({
+  schema,
+  validationRules: [
+    createComplexityRule({
+      maximumComplexity: 1000,
+      onComplete: (complexity) => console.log('Query complexity:', complexity),
+    }),
+  ],
+});
+```
+
 ## Output Templates
 
 When implementing GraphQL features, provide:
diff --git a/skills/java-architect/SKILL.md b/skills/java-architect/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: java-architect
-description: Use when building enterprise Java applications with Spring Boot 3.x, microservices, or reactive programming. Invoke for WebFlux, JPA optimization, Spring Security, cloud-native patterns.
+description: Use when building, configuring, or debugging enterprise Java applications with Spring Boot 3.x, microservices, or reactive programming. Invoke to implement WebFlux endpoints, optimize JPA queries and database performance, configure Spring Security with OAuth2/JWT, or resolve authentication issues and async processing challenges in cloud-native Spring applications.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,28 +15,16 @@ metadata:
 
 # Java Architect
 
-Senior Java architect with deep expertise in enterprise-grade Spring Boot applications, microservices architecture, and cloud-native development.
-
-## Role Definition
-
-You are a senior Java architect with 15+ years of enterprise Java experience. You specialize in Spring Boot 3.x, Java 21 LTS, reactive programming with Project Reactor, and building scalable microservices. You apply Clean Architecture, SOLID principles, and production-ready patterns.
-
-## When to Use This Skill
-
-- Building Spring Boot microservices
-- Implementing reactive WebFlux applications
-- Optimizing JPA/Hibernate performance
-- Designing event-driven architectures
-- Setting up Spring Security with OAuth2/JWT
-- Creating cloud-native applications
+Enterprise Java specialist focused on Spring Boot 3.x, microservices architecture, and cloud-native development using Java 21 LTS.
 
 ## Core Workflow
 
 1. **Architecture analysis** - Review project structure, dependencies, Spring config
-2. **Domain design** - Create models following DDD and Clean Architecture
+2. **Domain design** - Create models following DDD and Clean Architecture; verify domain boundaries before proceeding. If boundaries are unclear, resolve ambiguities before moving to implementation.
 3. **Implementation** - Build services with Spring Boot best practices
-4. **Data layer** - Optimize JPA queries, implement repositories
-5. **Quality assurance** - Test with JUnit 5, TestContainers, achieve 85%+ coverage
+4. **Data layer** - Optimize JPA queries, implement repositories; run `./mvnw verify -pl <module>` to confirm query correctness. If integration tests fail: review Hibernate SQL logs, fix queries or mappings, re-run before proceeding.
+5. **Security & config** - Apply Spring Security, externalize configuration, add observability; run `./mvnw verify` after security changes to confirm filter chain and JWT wiring. If tests fail: check `SecurityFilterChain` bean order and token validation config, then re-run.
+6. **Quality assurance** - Run `./mvnw verify` (Maven) or `./gradlew check` (Gradle) to confirm all tests pass and coverage reaches 85%+ before closing. If coverage is below threshold: identify untested branches via JaCoCo report (`target/site/jacoco/index.html`), add missing test cases, re-run.
 
 ## Reference Guide
 
@@ -54,21 +42,17 @@ Load detailed guidance based on context:
 
 ### MUST DO
 - Use Java 21 LTS features (records, sealed classes, pattern matching)
-- Apply Clean Architecture and SOLID principles
-- Use Spring Boot 3.x with proper dependency injection
-- Write comprehensive tests (JUnit 5, Mockito, TestContainers)
+- Apply database migrations (Flyway/Liquibase)
 - Document APIs with OpenAPI/Swagger
 - Use proper exception handling hierarchy
-- Apply database migrations (Flyway/Liquibase)
+- Externalize all configuration (never hardcode values)
 
 ### MUST NOT DO
 - Use deprecated Spring APIs
 - Skip input validation
 - Store sensitive data unencrypted
 - Use blocking code in reactive applications
 - Ignore transaction boundaries
-- Hardcode configuration values
-- Skip proper logging and monitoring
 
 ## Output Templates
 
@@ -80,6 +64,69 @@ When implementing Java features, provide:
 5. Test classes with comprehensive coverage
 6. Brief explanation of architectural decisions
 
+## Code Examples
+
+### Minimal WebFlux REST Endpoint
+
+```java
+@RestController
+@RequestMapping("/api/v1/orders")
+@RequiredArgsConstructor
+public class OrderController {
+
+    private final OrderService orderService;
+
+    @GetMapping("/{id}")
+    public Mono<ResponseEntity<OrderDto>> getOrder(@PathVariable UUID id) {
+        return orderService.findById(id)
+                .map(ResponseEntity::ok)
+                .defaultIfEmpty(ResponseEntity.notFound().build());
+    }
+
+    @PostMapping
+    @ResponseStatus(HttpStatus.CREATED)
+    public Mono<OrderDto> createOrder(@Valid @RequestBody CreateOrderRequest request) {
+        return orderService.create(request);
+    }
+}
+```
+
+### JPA Repository with Optimized Query
+
+```java
+public interface OrderRepository extends JpaRepository<Order, UUID> {
+
+    // Avoid N+1: fetch association in one query
+    @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.customerId = :customerId")
+    List<Order> findByCustomerIdWithItems(@Param("customerId") UUID customerId);
+
+    // Projection to limit fetched columns
+    @Query("SELECT new com.example.dto.OrderSummary(o.id, o.status, o.total) FROM Order o WHERE o.status = :status")
+    Page<OrderSummary> findSummariesByStatus(@Param("status") OrderStatus status, Pageable pageable);
+}
+```
+
+### Spring Security OAuth2 JWT Configuration
+
+```java
+@Configuration
+@EnableMethodSecurity
+public class SecurityConfig {
+
+    @Bean
+    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
+        return http
+                .csrf(AbstractHttpConfigurer::disable)
+                .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
+                .authorizeHttpRequests(auth -> auth
+                        .requestMatchers("/actuator/health").permitAll()
+                        .anyRequest().authenticated())
+                .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
+                .build();
+    }
+}
+```
+
 ## Knowledge Reference
 
 Spring Boot 3.x, Java 21, Spring WebFlux, Project Reactor, Spring Data JPA, Spring Security, OAuth2/JWT, Hibernate, R2DBC, Spring Cloud, Resilience4j, Micrometer, JUnit 5, TestContainers, Mockito, Maven/Gradle
diff --git a/skills/javascript-pro/SKILL.md b/skills/javascript-pro/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: javascript-pro
-description: Use when building JavaScript applications with modern ES2023+ features, async patterns, or Node.js development. Invoke for vanilla JavaScript, browser APIs, performance optimization, module systems.
+description: Writes, debugs, and refactors JavaScript code using modern ES2023+ features, async/await patterns, ESM module systems, and Node.js APIs. Use when building vanilla JavaScript applications, implementing Promise-based async flows, optimising browser or Node.js performance, working with Web Workers or Fetch API, or reviewing .js/.mjs/.cjs files for correctness and best practices.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,12 +15,6 @@ metadata:
 
 # JavaScript Pro
 
-Senior JavaScript developer with 10+ years mastering modern ES2023+ features, asynchronous patterns, and full-stack JavaScript development.
-
-## Role Definition
-
-You are a senior JavaScript engineer with 10+ years of experience. You specialize in modern ES2023+ JavaScript, Node.js 20+, asynchronous programming, functional patterns, and performance optimization. You build clean, maintainable code following modern best practices.
-
 ## When to Use This Skill
 
 - Building vanilla JavaScript applications
@@ -32,11 +26,11 @@ You are a senior JavaScript engineer with 10+ years of experience. You specializ
 
 ## Core Workflow
 
-1. **Analyze requirements** - Review package.json, module system, Node version, browser targets
-2. **Design architecture** - Plan modules, async flows, error handling strategies
-3. **Implement** - Write ES2023+ code with proper patterns and optimizations
-4. **Optimize** - Profile performance, reduce bundle size, prevent memory leaks
-5. **Test** - Write comprehensive tests with Jest achieving 85%+ coverage
+1. **Analyze requirements** — Review `package.json`, module system, Node version, browser targets; confirm `.js`/`.mjs`/`.cjs` conventions
+2. **Design architecture** — Plan modules, async flows, and error handling strategies
+3. **Implement** — Write ES2023+ code with proper patterns and optimisations
+4. **Validate** — Run linter (`eslint --fix`); if linter fails, fix all reported issues and re-run before proceeding. Check for memory leaks with DevTools or `--inspect`, verify bundle size; if leaks are found, resolve them before continuing
+5. **Test** — Write comprehensive tests with Jest achieving 85%+ coverage; if coverage falls short, add missing cases and re-run. Confirm no unhandled Promise rejections
 
 ## Reference Guide
 
@@ -65,12 +59,69 @@ Load detailed guidance based on context:
 ### MUST NOT DO
 - Use `var` (always use `const` or `let`)
 - Use callback-based patterns (prefer Promises)
-- Mix CommonJS and ESM in same module
+- Mix CommonJS and ESM in the same module
 - Ignore memory leaks or performance issues
 - Skip error handling in async functions
 - Use synchronous I/O in Node.js
 - Mutate function parameters
-- Create blocking operations in browser
+- Create blocking operations in the browser
+
+## Key Patterns with Examples
+
+### Async/Await Error Handling
+```js
+// ✅ Correct — always handle async errors explicitly
+async function fetchUser(id) {
+  try {
+    const response = await fetch(`/api/users/${id}`);
+    if (!response.ok) throw new Error(`HTTP ${response.status}`);
+    return await response.json();
+  } catch (err) {
+    console.error("fetchUser failed:", err);
+    return null;
+  }
+}
+
+// ❌ Incorrect — unhandled rejection, no null guard
+async function fetchUser(id) {
+  const response = await fetch(`/api/users/${id}`);
+  return response.json();
+}
+```
+
+### Optional Chaining & Nullish Coalescing
+```js
+// ✅ Correct
+const city = user?.address?.city ?? "Unknown";
+
+// ❌ Incorrect — throws if address is undefined
+const city = user.address.city || "Unknown";
+```
+
+### ESM Module Structure
+```js
+// ✅ Correct — named exports, no default-only exports for libraries
+// utils/math.mjs
+export const add = (a, b) => a + b;
+export const multiply = (a, b) => a * b;
+
+// consumer.mjs
+import { add } from "./utils/math.mjs";
+
+// ❌ Incorrect — mixing require() with ESM
+const { add } = require("./utils/math.mjs");
+```
+
+### Avoid var / Prefer const
+```js
+// ✅ Correct
+const MAX_RETRIES = 3;
+let attempts = 0;
+
+// ❌ Incorrect
+var MAX_RETRIES = 3;
+var attempts = 0;
+```
 
 ## Output Templates
 
@@ -79,7 +130,3 @@ When implementing JavaScript features, provide:
 2. Test file with comprehensive coverage
 3. JSDoc documentation for public APIs
 4. Brief explanation of patterns used
-
-## Knowledge Reference
-
-ES2023, optional chaining, nullish coalescing, private fields, top-level await, Promise patterns, async/await, event loop, ESM/CJS, dynamic imports, Fetch API, Web Workers, Service Workers, Node.js streams, EventEmitter, memory optimization, functional programming
diff --git a/skills/kotlin-specialist/SKILL.md b/skills/kotlin-specialist/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: kotlin-specialist
-description: Use when building Kotlin applications requiring coroutines, multiplatform development, or Android with Compose. Invoke for Flow API, KMP projects, Ktor servers, DSL design, sealed classes.
+description: Provides idiomatic Kotlin implementation patterns including coroutine concurrency, Flow stream handling, multiplatform architecture, Compose UI construction, Ktor server setup, and type-safe DSL design. Use when building Kotlin applications requiring coroutines, multiplatform development, or Android with Compose. Invoke for Flow API, KMP projects, Ktor servers, DSL design, sealed classes, suspend function, Android Kotlin, Kotlin Multiplatform.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,16 @@ metadata:
 
 Senior Kotlin developer with deep expertise in coroutines, Kotlin Multiplatform (KMP), and modern Kotlin 1.9+ patterns.
 
-## Role Definition
-
-You are a senior Kotlin engineer with 10+ years of JVM experience and mastery of Kotlin 1.9+ features. You specialize in coroutines, Flow API, multiplatform development, Android/Compose, Ktor servers, and functional programming patterns. You write expressive, type-safe code leveraging Kotlin's DSL capabilities.
-
-## When to Use This Skill
-
-- Building Kotlin Multiplatform (KMP) libraries or apps
-- Implementing coroutine-based async operations
-- Creating Android apps with Jetpack Compose
-- Developing Ktor server applications
-- Designing type-safe DSLs and builders
-- Optimizing Kotlin performance and compilation
-
 ## Core Workflow
 
 1. **Analyze architecture** - Identify platform targets, coroutine patterns, shared code strategy
 2. **Design models** - Create sealed classes, data classes, type hierarchies
 3. **Implement** - Write idiomatic Kotlin with coroutines, Flow, extension functions
-4. **Optimize** - Apply inline classes, sequence operations, compilation strategies
-5. **Test** - Write multiplatform tests with coroutine test support
+   - *Checkpoint:* Verify coroutine cancellation is handled (parent scope cancelled on teardown) and null safety is enforced before proceeding
+4. **Validate** - Run `detekt` and `ktlint`; verify coroutine cancellation handling and null safety
+   - *If detekt/ktlint fails:* Fix all reported issues and re-run both tools before proceeding to step 5
+5. **Optimize** - Apply inline classes, sequence operations, compilation strategies
+6. **Test** - Write multiplatform tests with coroutine test support (`runTest`, Turbine)
 
 ## Reference Guide
 
@@ -50,23 +40,95 @@ Load detailed guidance based on context:
 | Ktor Server | `references/ktor-server.md` | Routing, plugins, authentication, serialization |
 | DSL & Idioms | `references/dsl-idioms.md` | Type-safe builders, scope functions, delegates |
 
+## Key Patterns
+
+### Sealed Classes for State Modeling
+
+```kotlin
+sealed class UiState<out T> {
+    data object Loading : UiState<Nothing>()
+    data class Success<T>(val data: T) : UiState<T>()
+    data class Error(val message: String, val cause: Throwable? = null) : UiState<Nothing>()
+}
+
+// Consume exhaustively — compiler enforces all branches
+fun render(state: UiState<User>) = when (state) {
+    is UiState.Loading  -> showSpinner()
+    is UiState.Success  -> showUser(state.data)
+    is UiState.Error    -> showError(state.message)
+}
+```
+
+### Coroutines & Flow
+
+```kotlin
+// Use structured concurrency — never GlobalScope
+class UserRepository(private val api: UserApi, private val scope: CoroutineScope) {
+
+    fun userUpdates(id: String): Flow<UiState<User>> = flow {
+        emit(UiState.Loading)
+        try {
+            emit(UiState.Success(api.fetchUser(id)))
+        } catch (e: IOException) {
+            emit(UiState.Error("Network error", e))
+        }
+    }.flowOn(Dispatchers.IO)
+
+    private val _user = MutableStateFlow<UiState<User>>(UiState.Loading)
+    val user: StateFlow<UiState<User>> = _user.asStateFlow()
+}
+
+// Anti-pattern — blocks the calling thread; avoid in production
+// runBlocking { api.fetchUser(id) }
+```
+
+### Null Safety
+
+```kotlin
+// Prefer safe calls and elvis operator
+val displayName = user?.profile?.name ?: "Anonymous"
+
+// Use let to scope nullable operations
+user?.email?.let { email -> sendNotification(email) }
+
+// !! only when the null case is a true contract violation and documented
+val config = requireNotNull(System.getenv("APP_CONFIG")) { "APP_CONFIG must be set" }
+```
+
+### Scope Functions
+
+```kotlin
+// apply — configure an object, returns receiver
+val request = HttpRequest().apply {
+    url = "https://api.example.com/users"
+    headers["Authorization"] = "Bearer $token"
+}
+
+// let — transform nullable / introduce a local scope
+val length = name?.let { it.trim().length } ?: 0
+
+// also — side-effects without changing the chain
+val user = createUser(form).also { logger.info("Created user ${it.id}") }
+```
+
 ## Constraints
 
 ### MUST DO
-- Use null safety (`?`, `?.`, `?:`, `!!` only when safe)
+- Use null safety (`?`, `?.`, `?:`, `!!` only when contract guarantees non-null)
 - Prefer `sealed class` for state modeling
 - Use `suspend` functions for async operations
 - Leverage type inference but be explicit when needed
 - Use `Flow` for reactive streams
 - Apply scope functions appropriately (`let`, `run`, `apply`, `also`, `with`)
 - Document public APIs with KDoc
 - Use explicit API mode for libraries
+- Run `detekt` and `ktlint` before committing
+- Verify coroutine cancellation is handled (cancel parent scope on teardown)
 
 ### MUST NOT DO
 - Block coroutines with `runBlocking` in production code
-- Use `!!` without justification (prefer safe calls)
+- Use `!!` without documented justification
 - Mix platform-specific code in common modules
-- Use Pydantic V1-style patterns (wrong language!)
 - Skip null safety checks
 - Use `GlobalScope.launch` (use structured concurrency)
 - Ignore coroutine cancellation
diff --git a/skills/kubernetes-specialist/SKILL.md b/skills/kubernetes-specialist/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: kubernetes-specialist
-description: Use when deploying or managing Kubernetes workloads requiring cluster configuration, security hardening, or troubleshooting. Invoke for Helm charts, RBAC policies, NetworkPolicies, storage configuration, performance optimization.
+description: Use when deploying or managing Kubernetes workloads. Invoke to create deployment manifests, configure pod security policies, set up service accounts, define network isolation rules, debug pod crashes, analyze resource limits, inspect container logs, or right-size workloads. Use for Helm charts, RBAC policies, NetworkPolicies, storage configuration, performance optimization, GitOps pipelines, and multi-cluster management.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,12 +15,6 @@ metadata:
 
 # Kubernetes Specialist
 
-Senior Kubernetes specialist with deep expertise in production cluster management, security hardening, and cloud-native architectures.
-
-## Role Definition
-
-You are a senior Kubernetes engineer with 10+ years of container orchestration experience. You specialize in production-grade K8s deployments, security hardening (RBAC, NetworkPolicies, Pod Security Standards), and performance optimization. You build scalable, reliable, and secure Kubernetes platforms.
-
 ## When to Use This Skill
 
 - Deploying workloads (Deployments, StatefulSets, DaemonSets, Jobs)
@@ -33,11 +27,11 @@ You are a senior Kubernetes engineer with 10+ years of container orchestration e
 
 ## Core Workflow
 
-1. **Analyze requirements** - Understand workload characteristics, scaling needs, security requirements
-2. **Design architecture** - Choose workload types, networking patterns, storage solutions
-3. **Implement manifests** - Create declarative YAML with proper resource limits, health checks
-4. **Secure** - Apply RBAC, NetworkPolicies, Pod Security Standards, least privilege
-5. **Test & validate** - Verify deployments, test failure scenarios, validate security posture
+1. **Analyze requirements** — Understand workload characteristics, scaling needs, security requirements
+2. **Design architecture** — Choose workload types, networking patterns, storage solutions
+3. **Implement manifests** — Create declarative YAML with proper resource limits, health checks
+4. **Secure** — Apply RBAC, NetworkPolicies, Pod Security Standards, least privilege
+5. **Validate** — Run `kubectl rollout status`, `kubectl get pods -w`, and `kubectl describe pod <name>` to confirm health; roll back with `kubectl rollout undo` if needed
 
 ## Reference Guide
 
@@ -80,14 +74,168 @@ Load detailed guidance based on context:
 - Use latest tag for production images
 - Expose unnecessary ports or services
 
+## Common YAML Patterns
+
+### Deployment with resource limits, probes, and security context
+
+```yaml
+apiVersion: apps/v1
+kind: Deployment
+metadata:
+  name: my-app
+  namespace: my-namespace
+  labels:
+    app: my-app
+    version: "1.2.3"
+spec:
+  replicas: 3
+  selector:
+    matchLabels:
+      app: my-app
+  template:
+    metadata:
+      labels:
+        app: my-app
+        version: "1.2.3"
+    spec:
+      serviceAccountName: my-app-sa   # never use default SA
+      securityContext:
+        runAsNonRoot: true
+        runAsUser: 1000
+        fsGroup: 2000
+      containers:
+        - name: my-app
+          image: my-registry/my-app:1.2.3   # never use latest
+          ports:
+            - containerPort: 8080
+          resources:
+            requests:
+              cpu: "100m"
+              memory: "128Mi"
+            limits:
+              cpu: "500m"
+              memory: "512Mi"
+          livenessProbe:
+            httpGet:
+              path: /healthz
+              port: 8080
+            initialDelaySeconds: 15
+            periodSeconds: 20
+          readinessProbe:
+            httpGet:
+              path: /ready
+              port: 8080
+            initialDelaySeconds: 5
+            periodSeconds: 10
+          securityContext:
+            allowPrivilegeEscalation: false
+            readOnlyRootFilesystem: true
+            capabilities:
+              drop: ["ALL"]
+          envFrom:
+            - secretRef:
+                name: my-app-secret   # pull credentials from Secret, not ConfigMap
+```
+
+### Minimal RBAC (least privilege)
+
+```yaml
+apiVersion: v1
+kind: ServiceAccount
+metadata:
+  name: my-app-sa
+  namespace: my-namespace
+---
+apiVersion: rbac.authorization.k8s.io/v1
+kind: Role
+metadata:
+  name: my-app-role
+  namespace: my-namespace
+rules:
+  - apiGroups: [""]
+    resources: ["configmaps"]
+    verbs: ["get", "list"]   # grant only what is needed
+---
+apiVersion: rbac.authorization.k8s.io/v1
+kind: RoleBinding
+metadata:
+  name: my-app-rolebinding
+  namespace: my-namespace
+subjects:
+  - kind: ServiceAccount
+    name: my-app-sa
+    namespace: my-namespace
+roleRef:
+  kind: Role
+  name: my-app-role
+  apiGroup: rbac.authorization.k8s.io
+```
+
+### NetworkPolicy (default-deny + explicit allow)
+
+```yaml
+# Deny all ingress and egress by default
+apiVersion: networking.k8s.io/v1
+kind: NetworkPolicy
+metadata:
+  name: default-deny-all
+  namespace: my-namespace
+spec:
+  podSelector: {}
+  policyTypes: ["Ingress", "Egress"]
+---
+# Allow only specific traffic
+apiVersion: networking.k8s.io/v1
+kind: NetworkPolicy
+metadata:
+  name: allow-my-app
+  namespace: my-namespace
+spec:
+  podSelector:
+    matchLabels:
+      app: my-app
+  policyTypes: ["Ingress"]
+  ingress:
+    - from:
+        - podSelector:
+            matchLabels:
+              app: frontend
+      ports:
+        - protocol: TCP
+          port: 8080
+```
+
+## Validation Commands
+
+After deploying, verify health and security posture:
+
+```bash
+# Watch rollout complete
+kubectl rollout status deployment/my-app -n my-namespace
+
+# Stream pod events to catch crash loops or image pull errors
+kubectl get pods -n my-namespace -w
+
+# Inspect a specific pod for failures
+kubectl describe pod <pod-name> -n my-namespace
+
+# Check container logs
+kubectl logs <pod-name> -n my-namespace --previous   # use --previous for crashed containers
+
+# Verify resource usage vs. limits
+kubectl top pods -n my-namespace
+
+# Audit RBAC permissions for a service account
+kubectl auth can-i --list --as=system:serviceaccount:my-namespace:my-app-sa
+
+# Roll back a failed deployment
+kubectl rollout undo deployment/my-app -n my-namespace
+```
+
 ## Output Templates
 
 When implementing Kubernetes resources, provide:
 1. Complete YAML manifests with proper structure
 2. RBAC configuration if needed (ServiceAccount, Role, RoleBinding)
 3. NetworkPolicy for network isolation
 4. Brief explanation of design decisions and security considerations
-
-## Knowledge Reference
-
-Kubernetes API, kubectl, Helm 3, Kustomize, RBAC, NetworkPolicies, Pod Security Standards, CNI, CSI, Ingress controllers, Service mesh basics, GitOps principles, monitoring/logging integration
diff --git a/skills/laravel-specialist/SKILL.md b/skills/laravel-specialist/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: laravel-specialist
-description: Use when building Laravel 10+ applications requiring Eloquent ORM, API resources, or queue systems. Invoke for Laravel models, Livewire components, Sanctum authentication, Horizon queues.
+description: Build and configure Laravel 10+ applications, including creating Eloquent models and relationships, implementing Sanctum authentication, configuring Horizon queues, designing RESTful APIs with API resources, and building reactive interfaces with Livewire. Use when creating Laravel models, setting up queue workers, implementing Sanctum auth flows, building Livewire components, optimising Eloquent queries, or writing Pest/PHPUnit tests for Laravel features.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,28 +17,13 @@ metadata:
 
 Senior Laravel specialist with deep expertise in Laravel 10+, Eloquent ORM, and modern PHP 8.2+ development.
 
-## Role Definition
-
-You are a senior PHP engineer with 10+ years of Laravel experience. You specialize in Laravel 10+ with PHP 8.2+, Eloquent ORM, API resources, queue systems, and modern Laravel patterns. You build elegant, scalable applications with powerful features.
-
-## When to Use This Skill
-
-- Building Laravel 10+ applications
-- Implementing Eloquent models and relationships
-- Creating RESTful APIs with API resources
-- Setting up queue systems and jobs
-- Building reactive interfaces with Livewire
-- Implementing authentication with Sanctum
-- Optimizing database queries and performance
-- Writing comprehensive tests with Pest/PHPUnit
-
 ## Core Workflow
 
-1. **Analyze requirements** - Identify models, relationships, APIs, queue needs
-2. **Design architecture** - Plan database schema, service layers, job queues
-3. **Implement models** - Create Eloquent models with relationships, scopes, casts
-4. **Build features** - Develop controllers, services, API resources, jobs
-5. **Test thoroughly** - Write feature and unit tests with >85% coverage
+1. **Analyse requirements** — Identify models, relationships, APIs, and queue needs
+2. **Design architecture** — Plan database schema, service layers, and job queues
+3. **Implement models** — Create Eloquent models with relationships, scopes, and casts; run `php artisan make:model` and verify with `php artisan migrate:status`
+4. **Build features** — Develop controllers, services, API resources, and jobs; run `php artisan route:list` to verify routing
+5. **Test thoroughly** — Write feature and unit tests; run `php artisan test` before considering any step complete (target >85% coverage)
 
 ## Reference Guide
 
@@ -57,7 +42,7 @@ Load detailed guidance based on context:
 ### MUST DO
 - Use PHP 8.2+ features (readonly, enums, typed properties)
 - Type hint all method parameters and return types
-- Use Eloquent relationships properly (avoid N+1)
+- Use Eloquent relationships properly (avoid N+1 with eager loading)
 - Implement API resources for transforming data
 - Queue long-running tasks
 - Write comprehensive tests (>85% coverage)
@@ -74,15 +59,203 @@ Load detailed guidance based on context:
 - Use deprecated Laravel features
 - Ignore queue failures
 
-## Output Templates
+## Code Templates
+
+Use these as starting points for every implementation.
+
+### Eloquent Model
+
+```php
+<?php
+
+declare(strict_types=1);
+
+namespace App\Models;
+
+use Illuminate\Database\Eloquent\Factories\HasFactory;
+use Illuminate\Database\Eloquent\Model;
+use Illuminate\Database\Eloquent\Relations\BelongsTo;
+use Illuminate\Database\Eloquent\Relations\HasMany;
+use Illuminate\Database\Eloquent\SoftDeletes;
+
+final class Post extends Model
+{
+    use HasFactory, SoftDeletes;
+
+    protected $fillable = ['title', 'body', 'status', 'user_id'];
+
+    protected $casts = [
+        'status' => PostStatus::class, // backed enum
+        'published_at' => 'immutable_datetime',
+    ];
+
+    // Relationships — always eager-load via ::with() at call site
+    public function author(): BelongsTo
+    {
+        return $this->belongsTo(User::class, 'user_id');
+    }
+
+    public function comments(): HasMany
+    {
+        return $this->hasMany(Comment::class);
+    }
+
+    // Local scope
+    public function scopePublished(Builder $query): Builder
+    {
+        return $query->where('status', PostStatus::Published);
+    }
+}
+```
+
+### Migration
+
+```php
+<?php
+
+use Illuminate\Database\Migrations\Migration;
+use Illuminate\Database\Schema\Blueprint;
+use Illuminate\Support\Facades\Schema;
+
+return new class extends Migration
+{
+    public function up(): void
+    {
+        Schema::create('posts', function (Blueprint $table): void {
+            $table->id();
+            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
+            $table->string('title');
+            $table->text('body');
+            $table->string('status')->default('draft');
+            $table->timestamp('published_at')->nullable();
+            $table->softDeletes();
+            $table->timestamps();
+        });
+    }
+
+    public function down(): void
+    {
+        Schema::dropIfExists('posts');
+    }
+};
+```
+
+### API Resource
+
+```php
+<?php
+
+declare(strict_types=1);
+
+namespace App\Http\Resources;
+
+use Illuminate\Http\Request;
+use Illuminate\Http\Resources\Json\JsonResource;
+
+final class PostResource extends JsonResource
+{
+    public function toArray(Request $request): array
+    {
+        return [
+            'id'           => $this->id,
+            'title'        => $this->title,
+            'body'         => $this->body,
+            'status'       => $this->status->value,
+            'published_at' => $this->published_at?->toIso8601String(),
+            'author'       => new UserResource($this->whenLoaded('author')),
+            'comments'     => CommentResource::collection($this->whenLoaded('comments')),
+        ];
+    }
+}
+```
+
+### Queued Job
+
+```php
+<?php
+
+declare(strict_types=1);
+
+namespace App\Jobs;
+
+use App\Models\Post;
+use Illuminate\Bus\Queueable;
+use Illuminate\Contracts\Queue\ShouldQueue;
+use Illuminate\Foundation\Bus\Dispatchable;
+use Illuminate\Queue\InteractsWithQueue;
+use Illuminate\Queue\SerializesModels;
+
+final class PublishPost implements ShouldQueue
+{
+    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;
+
+    public int $tries = 3;
+    public int $backoff = 60;
+
+    public function __construct(
+        private readonly Post $post,
+    ) {}
+
+    public function handle(): void
+    {
+        $this->post->update([
+            'status'       => PostStatus::Published,
+            'published_at' => now(),
+        ]);
+    }
+
+    public function failed(\Throwable $e): void
+    {
+        // Log or notify — never silently swallow failures
+        logger()->error('PublishPost failed', ['post' => $this->post->id, 'error' => $e->getMessage()]);
+    }
+}
+```
+
+### Feature Test (Pest)
+
+```php
+<?php
+
+use App\Models\Post;
+use App\Models\User;
+
+it('returns a published post for authenticated users', function (): void {
+    $user = User::factory()->create();
+    $post = Post::factory()->published()->for($user, 'author')->create();
+
+    $response = $this->actingAs($user)
+        ->getJson("/api/posts/{$post->id}");
+
+    $response->assertOk()
+        ->assertJsonPath('data.status', 'published')
+        ->assertJsonPath('data.author.id', $user->id);
+});
+
+it('queues a publish job when a draft is submitted', function (): void {
+    Queue::fake();
+    $user = User::factory()->create();
+    $post = Post::factory()->draft()->for($user, 'author')->create();
+
+    $this->actingAs($user)
+        ->postJson("/api/posts/{$post->id}/publish")
+        ->assertAccepted();
+
+    Queue::assertPushed(PublishPost::class, fn ($job) => $job->post->is($post));
+});
+```
+
+## Validation Checkpoints
+
+Run these at each workflow stage to confirm correctness before proceeding:
 
-When implementing Laravel features, provide:
-1. Model file (Eloquent model with relationships)
-2. Migration file (database schema)
-3. Controller/API resource (if applicable)
-4. Service class (business logic)
-5. Test file (feature/unit tests)
-6. Brief explanation of design decisions
+| Stage | Command | Expected Result |
+|-------|---------|-----------------|
+| After migration | `php artisan migrate:status` | All migrations show `Ran` |
+| After routing | `php artisan route:list --path=api` | New routes appear with correct verbs |
+| After job dispatch | `php artisan queue:work --once` | Job processes without exception |
+| After implementation | `php artisan test --coverage` | >85% coverage, 0 failures |
+| Before PR | `./vendor/bin/pint --test` | PSR-12 linting passes |
 
 ## Knowledge Reference
 
diff --git a/skills/legacy-modernizer/SKILL.md b/skills/legacy-modernizer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: legacy-modernizer
-description: Use when modernizing legacy systems, implementing incremental migration strategies, or reducing technical debt. Invoke for strangler fig pattern, monolith decomposition, framework upgrades.
+description: Designs incremental migration strategies, identifies service boundaries, produces dependency maps and migration roadmaps, and generates API facade designs for aging codebases. Use when modernizing legacy systems, implementing strangler fig pattern or branch by abstraction, decomposing monoliths, upgrading frameworks or languages, or reducing technical debt without disrupting business operations.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,28 +15,22 @@ metadata:
 
 # Legacy Modernizer
 
-Senior legacy modernization specialist with expertise in transforming aging systems into modern architectures without disrupting business operations.
-
-## Role Definition
+## Core Workflow
 
-You are a senior legacy modernization expert with 15+ years of experience in incremental migration strategies. You specialize in strangler fig pattern, branch by abstraction, and risk-free modernization approaches. You transform legacy systems while maintaining zero downtime and ensuring business continuity.
+1. **Assess system** — Analyze codebase, dependencies, risks, and business constraints. Produce a dependency map and risk register before proceeding.
+   - *Validation checkpoint:* Confirm all external integrations and data contracts are documented before moving to step 2.
 
-## When to Use This Skill
+2. **Plan migration** — Design an incremental roadmap with explicit rollback strategies per phase. Reference `references/system-assessment.md` for code analysis templates.
+   - *Validation checkpoint:* Confirm each phase has a defined rollback trigger and owner.
 
-- Modernizing legacy codebases and outdated technology stacks
-- Implementing strangler fig or branch by abstraction patterns
-- Migrating from monoliths to microservices incrementally
-- Refactoring legacy code with comprehensive safety nets
-- Upgrading frameworks, languages, or infrastructure safely
-- Reducing technical debt while maintaining business continuity
+3. **Build safety net** — Create characterization tests and monitoring before touching production code. Target 80%+ coverage of existing behavior.
+   - *Validation checkpoint:* Run the characterization test suite and confirm it passes green on the unmodified legacy system before proceeding.
 
-## Core Workflow
+4. **Migrate incrementally** — Apply strangler fig pattern with feature flags. Route traffic via a facade; shift load gradually.
+   - *Validation checkpoint:* Verify error rates and latency metrics remain within baseline thresholds after each traffic increment (e.g., 5% → 25% → 50% → 100%).
 
-1. **Assess system** - Analyze codebase, dependencies, risks, and business constraints
-2. **Plan migration** - Design incremental roadmap with rollback strategies
-3. **Build safety net** - Create characterization tests and monitoring
-4. **Migrate incrementally** - Apply strangler fig pattern with feature flags
-5. **Validate & iterate** - Test thoroughly, monitor metrics, adjust approach
+5. **Validate & iterate** — Run full test suite, review monitoring dashboards, and confirm business behavior is preserved before retiring legacy code.
+   - *Validation checkpoint:* New code must be proven stable at 100% traffic for at least one release cycle before legacy path is removed.
 
 ## Reference Guide
 
@@ -50,6 +44,65 @@ Load detailed guidance based on context:
 | Testing | `references/legacy-testing.md` | Characterization tests, golden master, approval |
 | Assessment | `references/system-assessment.md` | Code analysis, dependency mapping, risk evaluation |
 
+## Code Examples
+
+### Strangler Fig Facade (Python)
+```python
+# facade.py — routes requests to legacy or new service based on a feature flag
+import os
+from legacy_service import LegacyOrderService
+from new_service import NewOrderService
+
+class OrderServiceFacade:
+    def __init__(self):
+        self._legacy = LegacyOrderService()
+        self._new = NewOrderService()
+
+    def get_order(self, order_id: str):
+        if os.getenv("USE_NEW_ORDER_SERVICE", "false").lower() == "true":
+            return self._new.fetch(order_id)
+        return self._legacy.get(order_id)
+```
+
+### Feature Flag Wrapper
+```python
+# feature_flags.py — thin wrapper around an environment or config-based flag store
+import os
+
+def flag_enabled(flag_name: str, default: bool = False) -> bool:
+    """Check whether a migration feature flag is active."""
+    return os.getenv(flag_name, str(default)).lower() == "true"
+
+# Usage
+if flag_enabled("USE_NEW_PAYMENT_GATEWAY"):
+    result = new_gateway.charge(order)
+else:
+    result = legacy_gateway.charge(order)
+```
+
+### Characterization Test Template (pytest)
+```python
+# test_characterization_orders.py
+# Captures existing legacy behavior as a golden-master safety net.
+import pytest
+from legacy_service import LegacyOrderService
+
+service = LegacyOrderService()
+
+@pytest.mark.parametrize("order_id,expected_status", [
+    ("ORD-001", "SHIPPED"),
+    ("ORD-002", "PENDING"),
+    ("ORD-003", "CANCELLED"),
+])
+def test_order_status_golden_master(order_id, expected_status):
+    """Fail loudly if legacy behavior changes unexpectedly."""
+    result = service.get(order_id)
+    assert result["status"] == expected_status, (
+        f"Characterization broken for {order_id}: "
+        f"expected {expected_status}, got {result['status']}"
+    )
+```
+
 ## Constraints
 
 ### MUST DO
diff --git a/skills/mcp-developer/SKILL.md b/skills/mcp-developer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: mcp-developer
-description: Use when building MCP servers or clients that connect AI systems with external tools and data sources. Invoke for MCP protocol compliance, TypeScript/Python SDKs, resource providers, tool functions.
+description: Use when building, debugging, or extending MCP servers or clients that connect AI systems with external tools and data sources. Invoke to implement tool handlers, configure resource providers, set up stdio/HTTP/SSE transport layers, validate schemas with Zod or Pydantic, debug protocol compliance issues, or scaffold complete MCP server/client projects using TypeScript or Python SDKs.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,14 @@ metadata:
 
 Senior MCP (Model Context Protocol) developer with deep expertise in building servers and clients that connect AI systems with external tools and data sources.
 
-## Role Definition
-
-You are a senior MCP developer with expertise in protocol implementation, SDK usage (TypeScript/Python), and production deployment. You build robust MCP servers that expose resources, tools, and prompts to Claude and other AI systems while maintaining security, performance, and developer experience standards.
-
-## When to Use This Skill
-
-- Building MCP servers for data source integration
-- Implementing tool functions for AI assistants
-- Creating resource providers with URI schemes
-- Setting up MCP clients for Claude integration
-- Debugging protocol compliance issues
-- Optimizing MCP performance and security
-
 ## Core Workflow
 
-1. **Analyze requirements** - Identify data sources, tools needed, client apps
-2. **Design protocol** - Define resources, tools, prompts, schemas
-3. **Implement** - Build server/client with SDK, add security controls
-4. **Test** - Verify protocol compliance, performance, error handling
-5. **Deploy** - Package, configure, monitor in production
+1. **Analyze requirements** — Identify data sources, tools needed, and client apps
+2. **Initialize project** — `npx @modelcontextprotocol/create-server my-server` (TypeScript) or `pip install mcp` + scaffold (Python)
+3. **Design protocol** — Define resource URIs, tool schemas (Zod/Pydantic), and prompt templates
+4. **Implement** — Register tools and resource handlers; configure transport (stdio/SSE/HTTP)
+5. **Test** — Run `npx @modelcontextprotocol/inspector` to verify protocol compliance interactively; confirm tools appear, schemas accept valid inputs, and error responses are well-formed JSON-RPC 2.0. **Feedback loop:** if schema validation fails → inspect Zod/Pydantic error output → fix schema definition → re-run inspector. If a tool call returns a malformed response → check transport serialisation → fix handler → re-test.
+6. **Deploy** — Package, add auth/rate-limiting, configure env vars, monitor
 
 ## Reference Guide
 
@@ -50,6 +38,80 @@ Load detailed guidance based on context:
 | Tools | `references/tools.md` | Tool definitions, schemas, execution |
 | Resources | `references/resources.md` | Resource providers, URIs, templates |
 
+## Minimal Working Example
+
+### TypeScript — Tool with Zod Validation
+
+```typescript
+import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
+import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
+import { z } from "zod";
+
+const server = new McpServer({ name: "my-server", version: "1.0.0" });
+
+// Register a tool with validated input schema
+server.tool(
+  "get_weather",
+  "Fetch current weather for a location",
+  {
+    location: z.string().min(1).describe("City name or coordinates"),
+    units: z.enum(["celsius", "fahrenheit"]).default("celsius"),
+  },
+  async ({ location, units }) => {
+    // Implementation: call external API, transform response
+    const data = await fetchWeather(location, units); // your fetch logic
+    return {
+      content: [{ type: "text", text: JSON.stringify(data) }],
+    };
+  }
+);
+
+// Register a resource provider
+server.resource(
+  "config://app",
+  "Application configuration",
+  async (uri) => ({
+    contents: [{ uri: uri.href, text: JSON.stringify(getConfig()), mimeType: "application/json" }],
+  })
+);
+
+const transport = new StdioServerTransport();
+await server.connect(transport);
+```
+
+### Python — Tool with Pydantic Validation
+
+```python
+from mcp.server.fastmcp import FastMCP
+from pydantic import BaseModel, Field
+
+mcp = FastMCP("my-server")
+
+class WeatherInput(BaseModel):
+    location: str = Field(..., min_length=1, description="City name or coordinates")
+    units: str = Field("celsius", pattern="^(celsius|fahrenheit)$")
+
+@mcp.tool()
+async def get_weather(location: str, units: str = "celsius") -> str:
+    """Fetch current weather for a location."""
+    data = await fetch_weather(location, units)  # your fetch logic
+    return str(data)
+
+@mcp.resource("config://app")
+async def app_config() -> str:
+    """Expose application configuration as a resource."""
+    return json.dumps(get_config())
+
+if __name__ == "__main__":
+    mcp.run()  # defaults to stdio transport
+```
+
+**Expected tool call flow:**
+```
+Client → { "method": "tools/call", "params": { "name": "get_weather", "arguments": { "location": "Berlin" } } }
+Server → { "result": { "content": [{ "type": "text", "text": "{\"temp\": 18, \"units\": \"celsius\"}" }] } }
+```
+
 ## Constraints
 
 ### MUST DO
@@ -79,7 +141,3 @@ When implementing MCP features, provide:
 2. Schema definitions (tools, resources, prompts)
 3. Configuration file (transport, auth, etc.)
 4. Brief explanation of design decisions
-
-## Knowledge Reference
-
-Model Context Protocol (MCP), JSON-RPC 2.0, TypeScript SDK (@modelcontextprotocol/sdk), Python SDK (mcp), Zod schemas, Pydantic validation, stdio transport, SSE transport, resource URIs, tool functions, prompt templates, authentication, rate limiting
diff --git a/skills/microservices-architect/SKILL.md b/skills/microservices-architect/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: microservices-architect
-description: Use when designing distributed systems, decomposing monoliths, or implementing microservices patterns. Invoke for service boundaries, DDD, saga patterns, event sourcing, service mesh, distributed tracing.
+description: Designs distributed system architectures, decomposes monoliths into bounded-context services, recommends communication patterns, and produces service boundary diagrams and resilience strategies. Use when designing distributed systems, decomposing monoliths, or implementing microservices patterns — including service boundaries, DDD, saga patterns, event sourcing, CQRS, service mesh, or distributed tracing.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,29 +17,20 @@ metadata:
 
 Senior distributed systems architect specializing in cloud-native microservices architectures, resilience patterns, and operational excellence.
 
-## Role Definition
-
-You are a senior microservices architect with 15+ years of experience designing distributed systems. You specialize in service decomposition, domain-driven design, resilience patterns, service mesh technologies, and cloud-native architectures. You design systems that scale, self-heal, and enable autonomous teams.
-
-## When to Use This Skill
-
-- Decomposing monoliths into microservices
-- Defining service boundaries and bounded contexts
-- Designing inter-service communication patterns
-- Implementing resilience patterns (circuit breakers, retries, bulkheads)
-- Setting up service mesh (Istio, Linkerd)
-- Designing event-driven architectures
-- Implementing distributed transactions (Saga, CQRS)
-- Establishing observability (tracing, metrics, logging)
-
 ## Core Workflow
 
-1. **Domain Analysis** - Apply DDD to identify bounded contexts and service boundaries
-2. **Communication Design** - Choose sync/async patterns, protocols (REST, gRPC, events)
-3. **Data Strategy** - Database per service, event sourcing, eventual consistency
-4. **Resilience** - Circuit breakers, retries, timeouts, bulkheads, fallbacks
-5. **Observability** - Distributed tracing, correlation IDs, centralized logging
-6. **Deployment** - Container orchestration, service mesh, progressive delivery
+1. **Domain Analysis** — Apply DDD to identify bounded contexts and service boundaries.
+   - *Validation checkpoint:* Each candidate service owns its data exclusively, has a clear public API contract, and can be deployed independently.
+2. **Communication Design** — Choose sync/async patterns and protocols (REST, gRPC, events).
+   - *Validation checkpoint:* Long-running or cross-aggregate operations use async messaging; only query/command pairs with sub-100 ms SLA use synchronous calls.
+3. **Data Strategy** — Database per service, event sourcing, eventual consistency.
+   - *Validation checkpoint:* No shared database schema exists between services; consistency boundaries align with bounded contexts.
+4. **Resilience** — Circuit breakers, retries, timeouts, bulkheads, fallbacks.
+   - *Validation checkpoint:* Every external call has an explicit timeout, retry budget, and graceful degradation path.
+5. **Observability** — Distributed tracing, correlation IDs, centralized logging.
+   - *Validation checkpoint:* A single request can be traced end-to-end using its correlation ID across all services.
+6. **Deployment** — Container orchestration, service mesh, progressive delivery.
+   - *Validation checkpoint:* Health and readiness probes are defined; canary or blue-green rollout strategy is documented.
 
 ## Reference Guide
 
@@ -53,6 +44,90 @@ Load detailed guidance based on context:
 | Data Management | `references/data.md` | Database per service, event sourcing, CQRS |
 | Observability | `references/observability.md` | Distributed tracing, correlation IDs, metrics |
 
+## Implementation Examples
+
+### Correlation ID Middleware (Node.js / Express)
+```js
+const { v4: uuidv4 } = require('uuid');
+
+function correlationMiddleware(req, res, next) {
+  req.correlationId = req.headers['x-correlation-id'] || uuidv4();
+  res.setHeader('x-correlation-id', req.correlationId);
+  // Attach to logger context so every log line includes the ID
+  req.log = logger.child({ correlationId: req.correlationId });
+  next();
+}
+```
+Propagate `x-correlation-id` in every outbound HTTP call and Kafka message header.
+
+### Circuit Breaker (Python / `pybreaker`)
+```python
+import pybreaker
+
+# Opens after 5 failures; resets after 30 s in half-open state
+breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)
+
+@breaker
+def call_inventory_service(order_id: str):
+    response = requests.get(f"{INVENTORY_URL}/stock/{order_id}", timeout=2)
+    response.raise_for_status()
+    return response.json()
+
+def get_inventory(order_id: str):
+    try:
+        return call_inventory_service(order_id)
+    except pybreaker.CircuitBreakerError:
+        return {"status": "unavailable", "fallback": True}
+```
+
+### Saga Orchestration Skeleton (TypeScript)
+```ts
+// Each step defines execute() and compensate() so rollback is automatic.
+interface SagaStep<T> {
+  execute(ctx: T): Promise<T>;
+  compensate(ctx: T): Promise<void>;
+}
+
+async function runSaga<T>(steps: SagaStep<T>[], initialCtx: T): Promise<T> {
+  const completed: SagaStep<T>[] = [];
+  let ctx = initialCtx;
+  for (const step of steps) {
+    try {
+      ctx = await step.execute(ctx);
+      completed.push(step);
+    } catch (err) {
+      for (const done of completed.reverse()) {
+        await done.compensate(ctx).catch(console.error);
+      }
+      throw err;
+    }
+  }
+  return ctx;
+}
+
+// Usage: order creation saga
+const orderSaga = [reserveInventoryStep, chargePaymentStep, scheduleShipmentStep];
+await runSaga(orderSaga, { orderId, customerId, items });
+```
+
+### Health & Readiness Probe (Kubernetes)
+```yaml
+livenessProbe:
+  httpGet:
+    path: /health/live
+    port: 8080
+  initialDelaySeconds: 10
+  periodSeconds: 15
+readinessProbe:
+  httpGet:
+    path: /health/ready
+    port: 8080
+  initialDelaySeconds: 5
+  periodSeconds: 10
+```
+`/health/live` — returns 200 if the process is running.  
+`/health/ready` — returns 200 only when the service can serve traffic (DB connected, caches warm).
+
 ## Constraints
 
 ### MUST DO
diff --git a/skills/ml-pipeline/SKILL.md b/skills/ml-pipeline/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: ml-pipeline
-description: Use when building ML pipelines, orchestrating training workflows, automating model lifecycle, implementing feature stores, or managing experiment tracking systems.
+description: "Designs and implements production-grade ML pipeline infrastructure: configures experiment tracking with MLflow or Weights & Biases, creates Kubeflow or Airflow DAGs for training orchestration, builds feature store schemas with Feast, deploys model registries, and automates retraining and validation workflows. Use when building ML pipelines, orchestrating training workflows, automating model lifecycle, implementing feature stores, managing experiment tracking systems, setting up DVC for data versioning, tuning hyperparameters, or configuring MLOps tooling like Kubeflow, Airflow, MLflow, or Prefect."
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,29 +17,14 @@ metadata:
 
 Senior ML pipeline engineer specializing in production-grade machine learning infrastructure, orchestration systems, and automated training workflows.
 
-## Role Definition
-
-You are a senior ML pipeline expert specializing in end-to-end machine learning workflows. You design and implement scalable feature engineering pipelines, orchestrate distributed training jobs, manage experiment tracking, and automate the complete model lifecycle from data ingestion to production deployment. You build robust, reproducible, and observable ML systems.
-
-## When to Use This Skill
-
-- Building feature engineering pipelines and feature stores
-- Orchestrating training workflows with Kubeflow, Airflow, or custom systems
-- Implementing experiment tracking with MLflow, Weights & Biases, or Neptune
-- Creating automated hyperparameter tuning pipelines
-- Setting up model registries and versioning systems
-- Designing data validation and preprocessing workflows
-- Implementing model evaluation and validation strategies
-- Building reproducible training environments
-- Automating model retraining and deployment pipelines
-
 ## Core Workflow
 
-1. **Design pipeline architecture** - Map data flow, identify stages, define interfaces between components
-2. **Implement feature engineering** - Build transformation pipelines, feature stores, validation checks
-3. **Orchestrate training** - Configure distributed training, hyperparameter tuning, resource allocation
-4. **Track experiments** - Log metrics, parameters, artifacts; enable comparison and reproducibility
-5. **Validate and deploy** - Implement model validation, A/B testing, automated deployment workflows
+1. **Design pipeline architecture** — Map data flow, identify stages, define interfaces between components
+2. **Validate data schema** — Run schema checks and distribution validation before any training begins; halt and report on failures
+3. **Implement feature engineering** — Build transformation pipelines, feature stores, and validation checks
+4. **Orchestrate training** — Configure distributed training, hyperparameter tuning, and resource allocation
+5. **Track experiments** — Log metrics, parameters, and artifacts; enable comparison and reproducibility
+6. **Validate and deploy** — Run model evaluation gates; implement A/B testing or shadow deployment before promotion
 
 ## Reference Guide
 
@@ -53,40 +38,120 @@ Load detailed guidance based on context:
 | Pipeline Orchestration | `references/pipeline-orchestration.md` | Kubeflow Pipelines, Airflow, Prefect, DAG design, workflow automation |
 | Model Validation | `references/model-validation.md` | Evaluation strategies, validation workflows, A/B testing, shadow deployment |
 
+## Code Templates
+
+### MLflow Experiment Logging (minimal reproducible example)
+
+```python
+import mlflow
+import mlflow.sklearn
+from sklearn.ensemble import RandomForestClassifier
+from sklearn.model_selection import train_test_split
+from sklearn.metrics import accuracy_score, f1_score
+import numpy as np
+
+# Pin random state for reproducibility
+SEED = 42
+np.random.seed(SEED)
+
+mlflow.set_experiment("my-classifier-experiment")
+
+with mlflow.start_run():
+    # Log all hyperparameters — never hardcode silently
+    params = {"n_estimators": 100, "max_depth": 5, "random_state": SEED}
+    mlflow.log_params(params)
+
+    model = RandomForestClassifier(**params)
+    model.fit(X_train, y_train)
+    preds = model.predict(X_test)
+
+    # Log metrics
+    mlflow.log_metric("accuracy", accuracy_score(y_test, preds))
+    mlflow.log_metric("f1", f1_score(y_test, preds, average="weighted"))
+
+    # Log and register the model artifact
+    mlflow.sklearn.log_model(model, artifact_path="model",
+                             registered_model_name="my-classifier")
+```
+
+### Kubeflow Pipeline Component (single-step template)
+
+```python
+from kfp.v2 import dsl
+from kfp.v2.dsl import component, Input, Output, Dataset, Model, Metrics
+
+@component(base_image="python:3.10", packages_to_install=["scikit-learn", "mlflow"])
+def train_model(
+    train_data: Input[Dataset],
+    model_output: Output[Model],
+    metrics_output: Output[Metrics],
+    n_estimators: int = 100,
+    max_depth: int = 5,
+):
+    import pandas as pd
+    from sklearn.ensemble import RandomForestClassifier
+    import pickle, json
+
+    df = pd.read_csv(train_data.path)
+    X, y = df.drop("label", axis=1), df["label"]
+
+    model = RandomForestClassifier(n_estimators=n_estimators,
+                                   max_depth=max_depth, random_state=42)
+    model.fit(X, y)
+
+    with open(model_output.path, "wb") as f:
+        pickle.dump(model, f)
+
+    metrics_output.log_metric("train_samples", len(df))
+
+
+@dsl.pipeline(name="training-pipeline")
+def training_pipeline(data_path: str, n_estimators: int = 100):
+    train_step = train_model(n_estimators=n_estimators)
+    # Chain additional steps (validate, register, deploy) here
+```
+
+### Data Validation Checkpoint (Great Expectations style)
+
+```python
+import great_expectations as ge
+
+def validate_training_data(df):
+    """Run schema and distribution checks. Raise on failure — never skip."""
+    gdf = ge.from_pandas(df)
+    results = gdf.expect_column_values_to_not_be_null("label")
+    results &= gdf.expect_column_values_to_be_between("feature_1", 0, 1)
+
+    if not results["success"]:
+        raise ValueError(f"Data validation failed: {results['result']}")
+    return df  # safe to proceed to training
+```
+
 ## Constraints
 
-### MUST DO
-- Version all data, code, and models explicitly
-- Implement reproducible training environments (pinned dependencies, seeds)
-- Log all hyperparameters and metrics to experiment tracking
-- Validate data quality before training (schema checks, distribution validation)
-- Use containerized environments for training jobs
-- Implement proper error handling and retry logic
-- Store artifacts in versioned object storage
-- Enable pipeline monitoring and alerting
-- Document pipeline dependencies and data lineage
-- Implement automated testing for pipeline components
-
-### MUST NOT DO
-- Run training without experiment tracking
-- Deploy models without validation metrics
-- Hardcode hyperparameters in training scripts
-- Skip data validation and quality checks
-- Use non-reproducible random states
-- Store credentials in pipeline code
-- Train on production data without proper access controls
-- Deploy models without versioning
-- Ignore pipeline failures silently
-- Mix training and inference code without clear separation
-
-## Output Templates
-
-When implementing ML pipelines, provide:
-1. Complete pipeline definition (Kubeflow/Airflow DAG or equivalent)
-2. Feature engineering code with data validation
-3. Training script with experiment logging
-4. Model evaluation and validation code
-5. Deployment configuration
+**Always:**
+- Version all data, code, and models explicitly (DVC, Git tags, model registry)
+- Pin dependencies and random seeds for reproducible training environments
+- Log all hyperparameters, metrics, and artifacts to experiment tracking
+- Validate data schema and distribution before training begins
+- Use containerized environments; store credentials in secrets managers, never in code
+- Implement error handling, retry logic, and pipeline alerting
+- Separate training and inference code clearly
+
+**Never:**
+- Run training without experiment tracking or without logging hyperparameters
+- Deploy a model without recorded validation metrics
+- Use non-reproducible random states or skip data validation
+- Ignore pipeline failures silently or mix credentials into pipeline code
+
+## Output Format
+
+When implementing a pipeline, provide:
+1. Complete pipeline definition (Kubeflow DAG, Airflow DAG, or equivalent) — use the templates above as starting structure
+2. Feature engineering code with inline data validation calls
+3. Training script with MLflow (or equivalent) experiment logging
+4. Model evaluation code with explicit pass/fail thresholds
+5. Deployment configuration and rollback strategy
 6. Brief explanation of architecture decisions and reproducibility measures
 
 ## Knowledge Reference
diff --git a/skills/monitoring-expert/SKILL.md b/skills/monitoring-expert/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: monitoring-expert
-description: Use when setting up monitoring systems, logging, metrics, tracing, or alerting. Invoke for dashboards, Prometheus/Grafana, load testing, profiling, capacity planning.
+description: Configures monitoring systems, implements structured logging pipelines, creates Prometheus/Grafana dashboards, defines alerting rules, and instruments distributed tracing. Implements Prometheus/Grafana stacks, conducts load testing, performs application profiling, and plans infrastructure capacity. Use when setting up application monitoring, adding observability to services, debugging production issues with logs/metrics/traces, running load tests with k6 or Artillery, profiling CPU/memory bottlenecks, or forecasting capacity needs.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,29 +17,132 @@ metadata:
 
 Observability and performance specialist implementing comprehensive monitoring, alerting, tracing, and performance testing systems.
 
-## Role Definition
-
-You are a senior SRE with 10+ years of experience in production systems. You specialize in the three pillars of observability: logs, metrics, and traces. You build monitoring systems that enable quick incident response, proactive issue detection, and performance optimization.
-
-## When to Use This Skill
-
-- Setting up application monitoring
-- Implementing structured logging
-- Creating metrics and dashboards
-- Configuring alerting rules
-- Implementing distributed tracing
-- Debugging production issues with observability
-- Performance testing and load testing
-- Application profiling and bottleneck analysis
-- Capacity planning and resource forecasting
-
 ## Core Workflow
 
-1. **Assess** - Identify what needs monitoring
-2. **Instrument** - Add logging, metrics, traces
-3. **Collect** - Set up aggregation and storage
-4. **Visualize** - Create dashboards
-5. **Alert** - Configure meaningful alerts
+1. **Assess** — Identify what needs monitoring (SLIs, critical paths, business metrics)
+2. **Instrument** — Add logging, metrics, and traces to the application (see examples below)
+3. **Collect** — Configure aggregation and storage (Prometheus scrape, log shipper, OTLP endpoint); verify data arrives before proceeding
+4. **Visualize** — Build dashboards using RED (Rate/Errors/Duration) or USE (Utilization/Saturation/Errors) methods
+5. **Alert** — Define threshold and anomaly alerts on critical paths; validate no false-positive flood before shipping
+
+## Quick-Start Examples
+
+### Structured Logging (Node.js / Pino)
+```js
+import pino from 'pino';
+
+const logger = pino({ level: 'info' });
+
+// Good — structured fields, includes correlation ID
+logger.info({ requestId: req.id, userId: req.user.id, durationMs: elapsed }, 'order.created');
+
+// Bad — string interpolation, no correlation
+console.log(`Order created for user ${userId}`);
+```
+
+### Prometheus Metrics (Node.js)
+```js
+import { Counter, Histogram, register } from 'prom-client';
+
+const httpRequests = new Counter({
+  name: 'http_requests_total',
+  help: 'Total HTTP requests',
+  labelNames: ['method', 'route', 'status'],
+});
+
+const httpDuration = new Histogram({
+  name: 'http_request_duration_seconds',
+  help: 'HTTP request latency',
+  labelNames: ['method', 'route'],
+  buckets: [0.05, 0.1, 0.3, 0.5, 1, 2, 5],
+});
+
+// Instrument a route
+app.use((req, res, next) => {
+  const end = httpDuration.startTimer({ method: req.method, route: req.path });
+  res.on('finish', () => {
+    httpRequests.inc({ method: req.method, route: req.path, status: res.statusCode });
+    end();
+  });
+  next();
+});
+
+// Expose scrape endpoint
+app.get('/metrics', async (req, res) => {
+  res.set('Content-Type', register.contentType);
+  res.end(await register.metrics());
+});
+```
+
+### OpenTelemetry Tracing (Node.js)
+```js
+import { NodeSDK } from '@opentelemetry/sdk-node';
+import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
+import { trace } from '@opentelemetry/api';
+
+const sdk = new NodeSDK({
+  traceExporter: new OTLPTraceExporter({ url: 'http://jaeger:4318/v1/traces' }),
+});
+sdk.start();
+
+// Manual span around a critical operation
+const tracer = trace.getTracer('order-service');
+async function processOrder(orderId) {
+  const span = tracer.startSpan('order.process');
+  span.setAttribute('order.id', orderId);
+  try {
+    const result = await db.saveOrder(orderId);
+    span.setStatus({ code: SpanStatusCode.OK });
+    return result;
+  } catch (err) {
+    span.recordException(err);
+    span.setStatus({ code: SpanStatusCode.ERROR });
+    throw err;
+  } finally {
+    span.end();
+  }
+}
+```
+
+### Prometheus Alerting Rule
+```yaml
+groups:
+  - name: api.rules
+    rules:
+      - alert: HighErrorRate
+        expr: |
+          rate(http_requests_total{status=~"5.."}[5m])
+          / rate(http_requests_total[5m]) > 0.05
+        for: 2m
+        labels:
+          severity: critical
+        annotations:
+          summary: "Error rate above 5% on {{ $labels.route }}"
+```
+
+### k6 Load Test
+```js
+import http from 'k6/http';
+import { check, sleep } from 'k6';
+
+export const options = {
+  stages: [
+    { duration: '1m', target: 50 },   // ramp up
+    { duration: '5m', target: 50 },   // sustained load
+    { duration: '1m', target: 0 },    // ramp down
+  ],
+  thresholds: {
+    http_req_duration: ['p(95)<500'],  // 95th percentile < 500 ms
+    http_req_failed:   ['rate<0.01'],  // error rate < 1%
+  },
+};
+
+export default function () {
+  const res = http.get('https://api.example.com/orders');
+  check(res, { 'status is 200': (r) => r.status === 200 });
+  sleep(1);
+}
+```
 
 ## Reference Guide
 
@@ -71,7 +174,3 @@ Load detailed guidance based on context:
 - Alert on every error (alert fatigue)
 - Use string interpolation in logs (use structured fields)
 - Skip correlation IDs in distributed systems
-
-## Knowledge Reference
-
-Prometheus, Grafana, ELK Stack, Loki, Jaeger, OpenTelemetry, DataDog, New Relic, CloudWatch, structured logging, RED metrics, USE method, k6, Artillery, Locust, JMeter, clinic.js, pprof, py-spy, async-profiler, capacity planning
diff --git a/skills/nestjs-expert/SKILL.md b/skills/nestjs-expert/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: nestjs-expert
-description: Use when building NestJS applications requiring modular architecture, dependency injection, or TypeScript backend development. Invoke for modules, controllers, services, DTOs, guards, interceptors, TypeORM/Prisma.
+description: Creates and configures NestJS modules, controllers, services, DTOs, guards, and interceptors for enterprise-grade TypeScript backend applications. Use when building NestJS REST APIs or GraphQL services, implementing dependency injection, scaffolding modular architecture, adding JWT/Passport authentication, integrating TypeORM or Prisma, or working with .module.ts, .controller.ts, and .service.ts files. Invoke for guards, interceptors, pipes, validation, Swagger documentation, and unit/E2E testing in NestJS projects.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,14 @@ metadata:
 
 Senior NestJS specialist with deep expertise in enterprise-grade, scalable TypeScript backend applications.
 
-## Role Definition
-
-You are a senior Node.js engineer with 10+ years of backend experience. You specialize in NestJS architecture, dependency injection, and enterprise patterns. You build modular, testable applications with proper separation of concerns.
-
-## When to Use This Skill
-
-- Building NestJS REST APIs or GraphQL services
-- Implementing modules, controllers, and services
-- Creating DTOs with validation
-- Setting up authentication (JWT, Passport)
-- Implementing guards, interceptors, and pipes
-- Database integration with TypeORM or Prisma
-
 ## Core Workflow
 
-1. **Analyze requirements** - Identify modules, endpoints, entities
-2. **Design structure** - Plan module organization and dependencies
-3. **Implement** - Create modules, services, controllers with DI
-4. **Secure** - Add guards, validation, authentication
-5. **Test** - Write unit tests and E2E tests
+1. **Analyze requirements** — Identify modules, endpoints, entities, and relationships
+2. **Design structure** — Plan module organization and inter-module dependencies
+3. **Implement** — Create modules, services, and controllers with proper DI wiring
+4. **Secure** — Add guards, validation pipes, and authentication
+5. **Verify** — Run `npm run lint`, `npm run test`, and confirm DI graph with `nest info`
+6. **Test** — Write unit tests for services and E2E tests for controllers
 
 ## Reference Guide
 
@@ -51,33 +39,167 @@ Load detailed guidance based on context:
 | Testing | `references/testing-patterns.md` | Unit tests, E2E tests, mocking |
 | Express Migration | `references/migration-from-express.md` | Migrating from Express.js to NestJS |
 
+## Code Examples
+
+### Controller with DTO Validation and Swagger
+
+```typescript
+// create-user.dto.ts
+import { IsEmail, IsString, MinLength } from 'class-validator';
+import { ApiProperty } from '@nestjs/swagger';
+
+export class CreateUserDto {
+  @ApiProperty({ example: 'user@example.com' })
+  @IsEmail()
+  email: string;
+
+  @ApiProperty({ example: 'strongPassword123', minLength: 8 })
+  @IsString()
+  @MinLength(8)
+  password: string;
+}
+
+// users.controller.ts
+import { Body, Controller, Post, HttpCode, HttpStatus } from '@nestjs/common';
+import { ApiCreatedResponse, ApiTags } from '@nestjs/swagger';
+import { UsersService } from './users.service';
+import { CreateUserDto } from './dto/create-user.dto';
+
+@ApiTags('users')
+@Controller('users')
+export class UsersController {
+  constructor(private readonly usersService: UsersService) {}
+
+  @Post()
+  @HttpCode(HttpStatus.CREATED)
+  @ApiCreatedResponse({ description: 'User created successfully.' })
+  create(@Body() createUserDto: CreateUserDto) {
+    return this.usersService.create(createUserDto);
+  }
+}
+```
+
+### Service with Dependency Injection and Error Handling
+
+```typescript
+// users.service.ts
+import { Injectable, ConflictException, NotFoundException } from '@nestjs/common';
+import { InjectRepository } from '@nestjs/typeorm';
+import { Repository } from 'typeorm';
+import { User } from './entities/user.entity';
+import { CreateUserDto } from './dto/create-user.dto';
+
+@Injectable()
+export class UsersService {
+  constructor(
+    @InjectRepository(User)
+    private readonly usersRepository: Repository<User>,
+  ) {}
+
+  async create(createUserDto: CreateUserDto): Promise<User> {
+    const existing = await this.usersRepository.findOneBy({ email: createUserDto.email });
+    if (existing) {
+      throw new ConflictException('Email already registered');
+    }
+    const user = this.usersRepository.create(createUserDto);
+    return this.usersRepository.save(user);
+  }
+
+  async findOne(id: number): Promise<User> {
+    const user = await this.usersRepository.findOneBy({ id });
+    if (!user) {
+      throw new NotFoundException(`User #${id} not found`);
+    }
+    return user;
+  }
+}
+```
+
+### Module Definition
+
+```typescript
+// users.module.ts
+import { Module } from '@nestjs/common';
+import { TypeOrmModule } from '@nestjs/typeorm';
+import { UsersController } from './users.controller';
+import { UsersService } from './users.service';
+import { User } from './entities/user.entity';
+
+@Module({
+  imports: [TypeOrmModule.forFeature([User])],
+  controllers: [UsersController],
+  providers: [UsersService],
+  exports: [UsersService], // export only when other modules need this service
+})
+export class UsersModule {}
+```
+
+### Unit Test for Service
+
+```typescript
+// users.service.spec.ts
+import { Test, TestingModule } from '@nestjs/testing';
+import { getRepositoryToken } from '@nestjs/typeorm';
+import { ConflictException } from '@nestjs/common';
+import { UsersService } from './users.service';
+import { User } from './entities/user.entity';
+
+const mockRepo = {
+  findOneBy: jest.fn(),
+  create: jest.fn(),
+  save: jest.fn(),
+};
+
+describe('UsersService', () => {
+  let service: UsersService;
+
+  beforeEach(async () => {
+    const module: TestingModule = await Test.createTestingModule({
+      providers: [
+        UsersService,
+        { provide: getRepositoryToken(User), useValue: mockRepo },
+      ],
+    }).compile();
+    service = module.get<UsersService>(UsersService);
+    jest.clearAllMocks();
+  });
+
+  it('throws ConflictException when email already exists', async () => {
+    mockRepo.findOneBy.mockResolvedValue({ id: 1, email: 'user@example.com' });
+    await expect(
+      service.create({ email: 'user@example.com', password: 'pass1234' }),
+    ).rejects.toThrow(ConflictException);
+  });
+});
+```
+
 ## Constraints
 
 ### MUST DO
-- Use dependency injection for all services
-- Validate all inputs with class-validator
-- Use DTOs for request/response bodies
-- Implement proper error handling with HTTP exceptions
-- Document APIs with Swagger decorators
-- Write unit tests for services
-- Use environment variables for configuration
+- Use `@Injectable()` and constructor injection for all services — never instantiate services with `new`
+- Validate all inputs with `class-validator` decorators on DTOs and enable `ValidationPipe` globally
+- Use DTOs for all request/response bodies; never pass raw `req.body` to services
+- Throw typed HTTP exceptions (`NotFoundException`, `ConflictException`, etc.) in services
+- Document all endpoints with `@ApiTags`, `@ApiOperation`, and response decorators
+- Write unit tests for every service method using `Test.createTestingModule`
+- Store all config values via `ConfigModule` and `process.env`; never hardcode them
 
 ### MUST NOT DO
-- Expose passwords or secrets in responses
-- Trust user input without validation
-- Use `any` type unless absolutely necessary
-- Create circular dependencies between modules
-- Hardcode configuration values
-- Skip error handling
+- Expose passwords, secrets, or internal stack traces in responses
+- Accept unvalidated user input — always apply `ValidationPipe`
+- Use `any` type unless absolutely necessary and documented
+- Create circular dependencies between modules — use `forwardRef()` only as a last resort
+- Hardcode hostnames, ports, or credentials in source files
+- Skip error handling in service methods
 
 ## Output Templates
 
-When implementing NestJS features, provide:
-1. Module definition
-2. Controller with Swagger decorators
-3. Service with error handling
-4. DTOs with validation
-5. Tests for service methods
+When implementing a NestJS feature, provide in this order:
+1. Module definition (`.module.ts`)
+2. Controller with Swagger decorators (`.controller.ts`)
+3. Service with typed error handling (`.service.ts`)
+4. DTOs with `class-validator` decorators (`dto/*.dto.ts`)
+5. Unit tests for service methods (`*.service.spec.ts`)
 
 ## Knowledge Reference
 
diff --git a/skills/nextjs-developer/SKILL.md b/skills/nextjs-developer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: nextjs-developer
-description: Use when building Next.js 14+ applications with App Router, server components, or server actions. Invoke for full-stack features, performance optimization, SEO implementation, production deployment.
+description: "Use when building Next.js 14+ applications with App Router, server components, or server actions. Invoke to configure route handlers, implement middleware, set up API routes, add streaming SSR, write generateMetadata for SEO, scaffold loading.tsx/error.tsx boundaries, or deploy to Vercel. Triggers on: Next.js, Next.js 14, App Router, RSC, use server, Server Components, Server Actions, React Server Components, generateMetadata, loading.tsx, Next.js deployment, Vercel, Next.js performance."
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,14 @@ metadata:
 
 Senior Next.js developer with expertise in Next.js 14+ App Router, server components, and full-stack deployment with focus on performance and SEO excellence.
 
-## Role Definition
-
-You are a senior full-stack developer with 10+ years of React/Next.js experience. You specialize in Next.js 14+ App Router (NOT Pages Router), React Server Components, server actions, and production-grade deployment. You build blazing-fast, SEO-optimized applications achieving Core Web Vitals scores > 90.
-
-## When to Use This Skill
-
-- Building Next.js 14+ applications with App Router
-- Implementing server components and server actions
-- Setting up data fetching, caching, and revalidation
-- Optimizing performance (images, fonts, bundles)
-- Implementing SEO with Metadata API
-- Deploying to Vercel or self-hosting
-
 ## Core Workflow
 
-1. **Architecture planning** - Define app structure, routes, layouts, rendering strategy
-2. **Implement routing** - Create App Router structure with layouts, templates, loading states
-3. **Data layer** - Setup server components, data fetching, caching, revalidation
-4. **Optimize** - Images, fonts, bundles, streaming, edge runtime
-5. **Deploy** - Production build, environment setup, monitoring
+1. **Architecture planning** — Define app structure, routes, layouts, rendering strategy
+2. **Implement routing** — Create App Router structure with layouts, templates, loading/error states
+3. **Data layer** — Set up server components, data fetching, caching, revalidation
+4. **Optimize** — Images, fonts, bundles, streaming, edge runtime
+5. **Deploy** — Production build, environment setup, monitoring
+   - Validate: run `next build` locally, confirm zero type errors, check `NEXT_PUBLIC_*` and server-only env vars are set, run Lighthouse/PageSpeed to confirm Core Web Vitals > 90
 
 ## Reference Guide
 
@@ -52,35 +40,103 @@ Load detailed guidance based on context:
 
 ## Constraints
 
-### MUST DO
-- Use App Router (NOT Pages Router)
-- Use TypeScript with strict mode
-- Use Server Components by default
-- Mark Client Components with 'use client'
-- Use native fetch with caching options
-- Use Metadata API for SEO
-- Optimize images with next/image
-- Use proper loading and error boundaries
-- Target Core Web Vitals > 90
+### MUST DO (Next.js-specific)
+- Use App Router (`app/` directory), never Pages Router (`pages/`)
+- Keep components as Server Components by default; add `'use client'` only at the leaf boundary where interactivity is required
+- Use native `fetch` with explicit `cache` / `next.revalidate` options — do not rely on implicit caching
+- Use `generateMetadata` (or the static `metadata` export) for all SEO — never hardcode `<title>` or `<meta>` tags in JSX
+- Optimize every image with `next/image`; never use a plain `<img>` tag for content images
+- Add `loading.tsx` and `error.tsx` at every route segment that performs async data fetching
 
 ### MUST NOT DO
-- Use Pages Router (pages/ directory)
-- Make all components client components
-- Fetch data in client components unnecessarily
-- Skip image optimization
-- Hardcode metadata in components
-- Use external state managers without need
-- Skip error boundaries
-- Deploy without build optimization
+- Convert components to Client Components just to access data — fetch server-side first
+- Skip `loading.tsx`/`error.tsx` boundaries on async route segments
+- Deploy without running `next build` to confirm zero errors
+
+## Code Examples
+
+### Server Component with data fetching and caching
+```tsx
+// app/products/page.tsx
+import { Suspense } from 'react'
+
+async function ProductList() {
+  // Revalidate every 60 seconds (ISR)
+  const res = await fetch('https://api.example.com/products', {
+    next: { revalidate: 60 },
+  })
+  if (!res.ok) throw new Error('Failed to fetch products')
+  const products: Product[] = await res.json()
+
+  return (
+    <ul>
+      {products.map((p) => (
+        <li key={p.id}>{p.name}</li>
+      ))}
+    </ul>
+  )
+}
+
+export default function Page() {
+  return (
+    <Suspense fallback={<p>Loading…</p>}>
+      <ProductList />
+    </Suspense>
+  )
+}
+```
+
+### Server Action with form handling and revalidation
+```tsx
+// app/products/actions.ts
+'use server'
+
+import { revalidatePath } from 'next/cache'
+
+export async function createProduct(formData: FormData) {
+  const name = formData.get('name') as string
+  await db.product.create({ data: { name } })
+  revalidatePath('/products')
+}
+
+// app/products/new/page.tsx
+import { createProduct } from '../actions'
+
+export default function NewProductPage() {
+  return (
+    <form action={createProduct}>
+      <input name="name" placeholder="Product name" required />
+      <button type="submit">Create</button>
+    </form>
+  )
+}
+```
+
+### generateMetadata for dynamic SEO
+```tsx
+// app/products/[id]/page.tsx
+import type { Metadata } from 'next'
+
+export async function generateMetadata(
+  { params }: { params: { id: string } }
+): Promise<Metadata> {
+  const product = await fetchProduct(params.id)
+  return {
+    title: product.name,
+    description: product.description,
+    openGraph: { title: product.name, images: [product.imageUrl] },
+  }
+}
+```
 
 ## Output Templates
 
 When implementing Next.js features, provide:
 1. App structure (route organization)
 2. Layout/page components with proper data fetching
 3. Server actions if mutations needed
-4. Configuration (next.config.js, TypeScript)
-5. Brief explanation of rendering strategy
+4. Configuration (`next.config.js`, TypeScript)
+5. Brief explanation of rendering strategy chosen
 
 ## Knowledge Reference
 
diff --git a/skills/pandas-pro/SKILL.md b/skills/pandas-pro/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: pandas-pro
-description: Use when working with pandas DataFrames, data cleaning, aggregation, merging, or time series analysis. Invoke for data manipulation, missing value handling, groupby operations, or performance optimization.
+description: Performs pandas DataFrame operations for data analysis, manipulation, and transformation. Use when working with pandas DataFrames, data cleaning, aggregation, merging, or time series analysis. Invoke for data manipulation tasks such as joining DataFrames on multiple keys, pivoting tables, resampling time series, handling NaN values with interpolation or forward-fill, groupby aggregations, type conversion, or performance optimization of large datasets.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,27 +17,24 @@ metadata:
 
 Expert pandas developer specializing in efficient data manipulation, analysis, and transformation workflows with production-grade performance patterns.
 
-## Role Definition
-
-You are a senior data engineer with deep expertise in pandas library for Python. You write efficient, vectorized code for data cleaning, transformation, aggregation, and analysis. You understand memory optimization, performance patterns, and best practices for large-scale data processing.
-
-## When to Use This Skill
-
-- Loading, cleaning, and transforming tabular data
-- Handling missing values and data quality issues
-- Performing groupby aggregations and pivot operations
-- Merging, joining, and concatenating datasets
-- Time series analysis and resampling
-- Optimizing pandas code for memory and performance
-- Converting between data formats (CSV, Excel, SQL, JSON)
-
 ## Core Workflow
 
-1. **Assess data structure** - Examine dtypes, memory usage, missing values, data quality
-2. **Design transformation** - Plan vectorized operations, avoid loops, identify indexing strategy
-3. **Implement efficiently** - Use vectorized methods, method chaining, proper indexing
-4. **Validate results** - Check dtypes, shapes, edge cases, null handling
-5. **Optimize** - Profile memory usage, apply categorical types, use chunking if needed
+1. **Assess data structure** — Examine dtypes, memory usage, missing values, data quality:
+   ```python
+   print(df.dtypes)
+   print(df.memory_usage(deep=True).sum() / 1e6, "MB")
+   print(df.isna().sum())
+   print(df.describe(include="all"))
+   ```
+2. **Design transformation** — Plan vectorized operations, avoid loops, identify indexing strategy
+3. **Implement efficiently** — Use vectorized methods, method chaining, proper indexing
+4. **Validate results** — Check dtypes, shapes, null counts, and row counts:
+   ```python
+   assert result.shape[0] == expected_rows, f"Row count mismatch: {result.shape[0]}"
+   assert result.isna().sum().sum() == 0, "Unexpected nulls after transform"
+   assert set(result.columns) == expected_cols
+   ```
+5. **Optimize** — Profile memory, apply categorical types, use chunking if needed
 
 ## Reference Guide
 
@@ -51,6 +48,106 @@ Load detailed guidance based on context:
 | Merging & Joining | `references/merging-joining.md` | Merge, join, concat, combine strategies |
 | Performance Optimization | `references/performance-optimization.md` | Memory usage, vectorization, chunking |
 
+## Code Patterns
+
+### Vectorized Operations (before/after)
+
+```python
+# ❌ AVOID: row-by-row iteration
+for i, row in df.iterrows():
+    df.at[i, 'tax'] = row['price'] * 0.2
+
+# ✅ USE: vectorized assignment
+df['tax'] = df['price'] * 0.2
+```
+
+### Safe Subsetting with `.copy()`
+
+```python
+# ❌ AVOID: chained indexing triggers SettingWithCopyWarning
+df['A']['B'] = 1
+
+# ✅ USE: .loc[] with explicit copy when mutating a subset
+subset = df.loc[df['status'] == 'active', :].copy()
+subset['score'] = subset['score'].fillna(0)
+```
+
+### GroupBy Aggregation
+
+```python
+summary = (
+    df.groupby(['region', 'category'], observed=True)
+    .agg(
+        total_sales=('revenue', 'sum'),
+        avg_price=('price', 'mean'),
+        order_count=('order_id', 'nunique'),
+    )
+    .reset_index()
+)
+```
+
+### Merge with Validation
+
+```python
+merged = pd.merge(
+    left_df, right_df,
+    on=['customer_id', 'date'],
+    how='left',
+    validate='m:1',          # asserts right key is unique
+    indicator=True,
+)
+unmatched = merged[merged['_merge'] != 'both']
+print(f"Unmatched rows: {len(unmatched)}")
+merged.drop(columns=['_merge'], inplace=True)
+```
+
+### Missing Value Handling
+
+```python
+# Forward-fill then interpolate numeric gaps
+df['price'] = df['price'].ffill().interpolate(method='linear')
+
+# Fill categoricals with mode, numerics with median
+for col in df.select_dtypes(include='object'):
+    df[col] = df[col].fillna(df[col].mode()[0])
+for col in df.select_dtypes(include='number'):
+    df[col] = df[col].fillna(df[col].median())
+```
+
+### Time Series Resampling
+
+```python
+daily = (
+    df.set_index('timestamp')
+    .resample('D')
+    .agg({'revenue': 'sum', 'sessions': 'count'})
+    .fillna(0)
+)
+```
+
+### Pivot Table
+
+```python
+pivot = df.pivot_table(
+    values='revenue',
+    index='region',
+    columns='product_line',
+    aggfunc='sum',
+    fill_value=0,
+    margins=True,
+)
+```
+
+### Memory Optimization
+
+```python
+# Downcast numerics and convert low-cardinality strings to categorical
+df['category'] = df['category'].astype('category')
+df['count'] = pd.to_numeric(df['count'], downcast='integer')
+df['score'] = pd.to_numeric(df['score'], downcast='float')
+print(df.memory_usage(deep=True).sum() / 1e6, "MB after optimization")
+```
+
 ## Constraints
 
 ### MUST DO
@@ -65,10 +162,10 @@ Load detailed guidance based on context:
 
 ### MUST NOT DO
 - Iterate over DataFrame rows with `.iterrows()` unless absolutely necessary
-- Use chained indexing (`df['A']['B']`) - use `.loc[]` or `.iloc[]`
+- Use chained indexing (`df['A']['B']`) — use `.loc[]` or `.iloc[]`
 - Ignore SettingWithCopyWarning messages
 - Load entire large datasets without chunking
-- Use deprecated methods (`.ix`, `.append()` - use `pd.concat()`)
+- Use deprecated methods (`.ix`, `.append()` — use `pd.concat()`)
 - Convert to Python lists for operations possible in pandas
 - Assume data is clean without validation
 
@@ -79,7 +176,3 @@ When implementing pandas solutions, provide:
 2. Comments explaining complex transformations
 3. Memory/performance considerations if dataset is large
 4. Data validation checks (dtypes, nulls, shapes)
-
-## Knowledge Reference
-
-pandas 2.0+, NumPy, datetime handling, categorical types, MultiIndex, memory optimization, vectorization, method chaining, merge strategies, time series resampling, pivot tables, groupby aggregations
diff --git a/skills/php-pro/SKILL.md b/skills/php-pro/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: php-pro
-description: Use when building PHP applications with modern PHP 8.3+ features, Laravel, or Symfony frameworks. Invoke for strict typing, PHPStan level 9, async patterns with Swoole, PSR standards.
+description: Use when building PHP applications with modern PHP 8.3+ features, Laravel, or Symfony frameworks. Invokes strict typing, PHPStan level 9, async patterns with Swoole, and PSR standards. Creates controllers, configures middleware, generates migrations, writes PHPUnit/Pest tests, defines typed DTOs and value objects, sets up dependency injection, and scaffolds REST/GraphQL APIs. Use when working with Eloquent, Doctrine, Composer, Psalm, ReactPHP, or any PHP API development.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,13 @@ metadata:
 
 Senior PHP developer with deep expertise in PHP 8.3+, Laravel, Symfony, and modern PHP patterns with strict typing and enterprise architecture.
 
-## Role Definition
-
-You are a senior PHP developer with 10+ years of experience building enterprise applications. You specialize in PHP 8.3+ with strict typing, Laravel/Symfony frameworks, async patterns (Swoole, ReactPHP), and PSR standards. You build scalable, maintainable applications with PHPStan level 9 compliance and 80%+ test coverage.
-
-## When to Use This Skill
-
-- Building Laravel or Symfony applications
-- Implementing strict type systems with PHPStan
-- Creating async PHP applications with Swoole/ReactPHP
-- Designing clean architecture with DDD patterns
-- Optimizing performance (OpCache, JIT, queries)
-- Writing comprehensive PHPUnit tests
-
 ## Core Workflow
 
-1. **Analyze architecture** - Review framework, PHP version, dependencies, patterns
-2. **Design models** - Create typed domain models, value objects, DTOs
-3. **Implement** - Write strict-typed code with PSR compliance, DI, repositories
-4. **Secure** - Add validation, authentication, XSS/SQL injection protection
-5. **Test & optimize** - PHPUnit tests, PHPStan level 9, performance tuning
+1. **Analyze architecture** — Review framework, PHP version, dependencies, and patterns
+2. **Design models** — Create typed domain models, value objects, DTOs
+3. **Implement** — Write strict-typed code with PSR compliance, DI, repositories
+4. **Secure** — Add validation, authentication, XSS/SQL injection protection
+5. **Verify** — Run `vendor/bin/phpstan analyse --level=9`; fix all errors before proceeding. Run `vendor/bin/phpunit` or `vendor/bin/pest`; enforce 80%+ coverage. Only deliver when both pass clean.
 
 ## Reference Guide
 
@@ -71,13 +58,147 @@ Load detailed guidance based on context:
 - Deploy without running tests and static analysis
 - Use var_dump in production code
 
+## Code Patterns
+
+Every complete implementation delivers: a typed entity/DTO, a service class, and a test. Use these as the baseline structure.
+
+### Readonly DTO / Value Object
+
+```php
+<?php
+
+declare(strict_types=1);
+
+namespace App\DTO;
+
+final readonly class CreateUserDTO
+{
+    public function __construct(
+        public string $name,
+        public string $email,
+        public string $password,
+    ) {}
+
+    public static function fromArray(array $data): self
+    {
+        return new self(
+            name: $data['name'],
+            email: $data['email'],
+            password: $data['password'],
+        );
+    }
+}
+```
+
+### Typed Service with Constructor DI
+
+```php
+<?php
+
+declare(strict_types=1);
+
+namespace App\Services;
+
+use App\DTO\CreateUserDTO;
+use App\Models\User;
+use App\Repositories\UserRepositoryInterface;
+use Illuminate\Support\Facades\Hash;
+
+final class UserService
+{
+    public function __construct(
+        private readonly UserRepositoryInterface $users,
+    ) {}
+
+    public function create(CreateUserDTO $dto): User
+    {
+        return $this->users->create([
+            'name'     => $dto->name,
+            'email'    => $dto->email,
+            'password' => Hash::make($dto->password),
+        ]);
+    }
+}
+```
+
+### PHPUnit Test Structure
+
+```php
+<?php
+
+declare(strict_types=1);
+
+namespace Tests\Unit\Services;
+
+use App\DTO\CreateUserDTO;
+use App\Models\User;
+use App\Repositories\UserRepositoryInterface;
+use App\Services\UserService;
+use PHPUnit\Framework\MockObject\MockObject;
+use PHPUnit\Framework\TestCase;
+
+final class UserServiceTest extends TestCase
+{
+    private UserRepositoryInterface&MockObject $users;
+    private UserService $service;
+
+    protected function setUp(): void
+    {
+        parent::setUp();
+        $this->users   = $this->createMock(UserRepositoryInterface::class);
+        $this->service = new UserService($this->users);
+    }
+
+    public function testCreateHashesPassword(): void
+    {
+        $dto  = new CreateUserDTO('Alice', 'alice@example.com', 'secret');
+        $user = new User(['name' => 'Alice', 'email' => 'alice@example.com']);
+
+        $this->users
+            ->expects($this->once())
+            ->method('create')
+            ->willReturn($user);
+
+        $result = $this->service->create($dto);
+
+        $this->assertSame('Alice', $result->name);
+    }
+}
+```
+
+### Enum (PHP 8.1+)
+
+```php
+<?php
+
+declare(strict_types=1);
+
+namespace App\Enums;
+
+enum UserStatus: string
+{
+    case Active   = 'active';
+    case Inactive = 'inactive';
+    case Banned   = 'banned';
+
+    public function label(): string
+    {
+        return match($this) {
+            self::Active   => 'Active',
+            self::Inactive => 'Inactive',
+            self::Banned   => 'Banned',
+        };
+    }
+}
+```
+
 ## Output Templates
 
-When implementing PHP features, provide:
-1. Domain models (entities, value objects)
+When implementing a feature, deliver in this order:
+1. Domain models (entities, value objects, enums)
 2. Service/repository classes
 3. Controller/API endpoints
-4. Test files (PHPUnit)
+4. Test files (PHPUnit/Pest)
 5. Brief explanation of architecture decisions
 
 ## Knowledge Reference
diff --git a/skills/playwright-expert/SKILL.md b/skills/playwright-expert/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: playwright-expert
-description: Use when writing E2E tests with Playwright, setting up test infrastructure, or debugging flaky browser tests. Invoke for browser automation, E2E tests, Page Object Model, test flakiness, visual testing.
+description: "Use when writing E2E tests with Playwright, setting up test infrastructure, or debugging flaky browser tests. Invoke to write test scripts, create page objects, configure test fixtures, set up reporters, add CI integration, implement API mocking, or perform visual regression testing. Trigger terms: Playwright, E2E test, end-to-end, browser testing, automation, UI testing, visual testing, Page Object Model, test flakiness."
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,27 +15,14 @@ metadata:
 
 # Playwright Expert
 
-Senior E2E testing specialist with deep expertise in Playwright for robust, maintainable browser automation.
-
-## Role Definition
-
-You are a senior QA automation engineer with 8+ years of browser testing experience. You specialize in Playwright test architecture, Page Object Model, and debugging flaky tests. You write reliable, fast tests that run in CI/CD.
-
-## When to Use This Skill
-
-- Writing E2E tests with Playwright
-- Setting up Playwright test infrastructure
-- Debugging flaky browser tests
-- Implementing Page Object Model
-- API mocking in browser tests
-- Visual regression testing
+E2E testing specialist with deep expertise in Playwright for robust, maintainable browser automation.
 
 ## Core Workflow
 
 1. **Analyze requirements** - Identify user flows to test
 2. **Setup** - Configure Playwright with proper settings
 3. **Write tests** - Use POM pattern, proper selectors, auto-waiting
-4. **Debug** - Fix flaky tests, use traces
+4. **Debug** - Run test → check trace → identify issue → fix → verify fix
 5. **Integrate** - Add to CI/CD pipeline
 
 ## Reference Guide
@@ -67,6 +54,108 @@ Load detailed guidance based on context:
 - Ignore flaky tests
 - Use `first()`, `nth()` without good reason
 
+## Code Examples
+
+### Selector: Role-based (correct) vs CSS class (brittle)
+
+```typescript
+// ✅ Role-based selector — resilient to styling changes
+await page.getByRole('button', { name: 'Submit' }).click();
+await page.getByLabel('Email address').fill('user@example.com');
+
+// ❌ CSS class selector — breaks on refactor
+await page.locator('.btn-primary.submit-btn').click();
+await page.locator('.email-input').fill('user@example.com');
+```
+
+### Page Object Model + Test File
+
+```typescript
+// pages/LoginPage.ts
+import { type Page, type Locator } from '@playwright/test';
+
+export class LoginPage {
+  readonly page: Page;
+  readonly emailInput: Locator;
+  readonly passwordInput: Locator;
+  readonly submitButton: Locator;
+  readonly errorMessage: Locator;
+
+  constructor(page: Page) {
+    this.page = page;
+    this.emailInput = page.getByLabel('Email address');
+    this.passwordInput = page.getByLabel('Password');
+    this.submitButton = page.getByRole('button', { name: 'Sign in' });
+    this.errorMessage = page.getByRole('alert');
+  }
+
+  async goto() {
+    await this.page.goto('/login');
+  }
+
+  async login(email: string, password: string) {
+    await this.emailInput.fill(email);
+    await this.passwordInput.fill(password);
+    await this.submitButton.click();
+  }
+}
+```
+
+```typescript
+// tests/login.spec.ts
+import { test, expect } from '@playwright/test';
+import { LoginPage } from '../pages/LoginPage';
+
+test.describe('Login', () => {
+  let loginPage: LoginPage;
+
+  test.beforeEach(async ({ page }) => {
+    loginPage = new LoginPage(page);
+    await loginPage.goto();
+  });
+
+  test('successful login redirects to dashboard', async ({ page }) => {
+    await loginPage.login('user@example.com', 'correct-password');
+    await expect(page).toHaveURL('/dashboard');
+  });
+
+  test('invalid credentials shows error', async () => {
+    await loginPage.login('user@example.com', 'wrong-password');
+    await expect(loginPage.errorMessage).toBeVisible();
+    await expect(loginPage.errorMessage).toContainText('Invalid credentials');
+  });
+});
+```
+
+### Debugging Workflow for Flaky Tests
+
+```typescript
+// 1. Run failing test with trace enabled
+// playwright.config.ts
+use: {
+  trace: 'on-first-retry',
+  screenshot: 'only-on-failure',
+}
+
+// 2. Re-run with retries to capture trace
+// npx playwright test --retries=2
+
+// 3. Open trace viewer to inspect timeline
+// npx playwright show-trace test-results/.../trace.zip
+
+// 4. Common fix — replace arbitrary timeout with proper wait
+// ❌ Flaky
+await page.waitForTimeout(2000);
+await page.getByRole('button', { name: 'Save' }).click();
+
+// ✅ Reliable — waits for element state
+await page.getByRole('button', { name: 'Save' }).waitFor({ state: 'visible' });
+await page.getByRole('button', { name: 'Save' }).click();
+
+// 5. Verify fix — run test 10x to confirm stability
+// npx playwright test --repeat-each=10
+```
+
 ## Output Templates
 
 When implementing Playwright tests, provide:
diff --git a/skills/postgres-pro/SKILL.md b/skills/postgres-pro/SKILL.md
@@ -17,10 +17,6 @@ metadata:
 
 Senior PostgreSQL expert with deep expertise in database administration, performance optimization, and advanced PostgreSQL features.
 
-## Role Definition
-
-You are a senior PostgreSQL DBA with 10+ years of production experience. You specialize in query optimization, replication strategies, JSONB operations, extension usage, and database maintenance. You build reliable, high-performance PostgreSQL systems that scale.
-
 ## When to Use This Skill
 
 - Analyzing and optimizing slow queries with EXPLAIN
@@ -33,11 +29,39 @@ You are a senior PostgreSQL DBA with 10+ years of production experience. You spe
 
 ## Core Workflow
 
-1. **Analyze performance** - Use EXPLAIN ANALYZE, pg_stat_statements
-2. **Design indexes** - B-tree, GIN, GiST, BRIN based on workload
-3. **Optimize queries** - Rewrite inefficient queries, update statistics
-4. **Setup replication** - Streaming or logical based on requirements
-5. **Monitor and maintain** - VACUUM, ANALYZE, bloat tracking
+1. **Analyze performance** — Run `EXPLAIN (ANALYZE, BUFFERS)` to identify bottlenecks
+2. **Design indexes** — Choose B-tree, GIN, GiST, or BRIN based on workload; verify with `EXPLAIN` before deploying
+3. **Optimize queries** — Rewrite inefficient queries, run `ANALYZE` to refresh statistics
+4. **Setup replication** — Streaming or logical based on requirements; monitor lag continuously
+5. **Monitor and maintain** — Track VACUUM, bloat, and autovacuum via `pg_stat` views; verify improvements after each change
+
+### End-to-End Example: Slow Query → Fix → Verification
+
+```sql
+-- Step 1: Identify slow queries
+SELECT query, mean_exec_time, calls
+FROM pg_stat_statements
+ORDER BY mean_exec_time DESC
+LIMIT 10;
+
+-- Step 2: Analyze a specific slow query
+EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
+SELECT * FROM orders WHERE customer_id = 42 AND status = 'pending';
+-- Look for: Seq Scan (bad on large tables), high Buffers hit, nested loops on large sets
+
+-- Step 3: Create a targeted index
+CREATE INDEX CONCURRENTLY idx_orders_customer_status
+  ON orders (customer_id, status)
+  WHERE status = 'pending';  -- partial index reduces size
+
+-- Step 4: Verify the index is used
+EXPLAIN (ANALYZE, BUFFERS)
+SELECT * FROM orders WHERE customer_id = 42 AND status = 'pending';
+-- Confirm: Index Scan on idx_orders_customer_status, lower actual time
+
+-- Step 5: Update statistics if needed after bulk changes
+ANALYZE orders;
+```
 
 ## Reference Guide
 
@@ -51,33 +75,74 @@ Load detailed guidance based on context:
 | Replication | `references/replication.md` | Streaming replication, logical replication, failover |
 | Maintenance | `references/maintenance.md` | VACUUM, ANALYZE, pg_stat views, monitoring, bloat |
 
+## Common Patterns
+
+### JSONB — GIN Index and Query
+
+```sql
+-- Create GIN index for containment queries
+CREATE INDEX idx_events_payload ON events USING GIN (payload);
+
+-- Efficient JSONB containment query (uses GIN index)
+SELECT * FROM events WHERE payload @> '{"type": "login", "success": true}';
+
+-- Extract nested value
+SELECT payload->>'user_id', payload->'meta'->>'ip'
+FROM events
+WHERE payload @> '{"type": "login"}';
+```
+
+### VACUUM and Bloat Monitoring
+
+```sql
+-- Check tables with high dead tuple counts
+SELECT relname, n_dead_tup, n_live_tup,
+       round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_pct,
+       last_autovacuum
+FROM pg_stat_user_tables
+ORDER BY n_dead_tup DESC
+LIMIT 20;
+
+-- Manually vacuum a high-churn table and verify
+VACUUM (ANALYZE, VERBOSE) orders;
+```
+
+### Replication Lag Monitoring
+
+```sql
+-- On primary: check standby lag
+SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
+       (sent_lsn - replay_lsn) AS replication_lag_bytes
+FROM pg_stat_replication;
+```
+
 ## Constraints
 
 ### MUST DO
-- Use EXPLAIN ANALYZE for query optimization
-- Create appropriate indexes (B-tree, GIN, GiST, BRIN)
-- Update statistics with ANALYZE after bulk changes
-- Monitor autovacuum and tune if needed
+- Use `EXPLAIN (ANALYZE, BUFFERS)` for query optimization
+- Verify indexes are actually used with `EXPLAIN` before and after creation
+- Use `CREATE INDEX CONCURRENTLY` to avoid table locks in production
+- Run `ANALYZE` after bulk data changes to refresh statistics
+- Monitor autovacuum; tune `autovacuum_vacuum_scale_factor` for high-churn tables
 - Use connection pooling (pgBouncer, pgPool)
-- Setup replication for high availability
-- Monitor with pg_stat_statements, pg_stat_user_tables
+- Monitor replication lag via `pg_stat_replication`
 - Use prepared statements to prevent SQL injection
+- Use `uuid` type for UUIDs, not `text`
 
 ### MUST NOT DO
 - Disable autovacuum globally
-- Create indexes without analyzing query patterns
-- Use SELECT * in production queries
-- Ignore replication lag monitoring
+- Create indexes without first analyzing query patterns
+- Use `SELECT *` in production queries
+- Ignore replication lag alerts
 - Skip VACUUM on high-churn tables
-- Use text for UUID storage (use uuid type)
-- Store large BLOBs in database (use object storage)
-- Ignore pg_stat_statements warnings
+- Store large BLOBs in the database (use object storage)
+- Deploy index changes without verifying the planner uses them
 
 ## Output Templates
 
 When implementing PostgreSQL solutions, provide:
-1. Query with EXPLAIN ANALYZE output
-2. Index definitions with rationale
+1. Query with `EXPLAIN (ANALYZE, BUFFERS)` output and interpretation
+2. Index definitions with rationale and pre/post verification
 3. Configuration changes with before/after values
 4. Monitoring queries for ongoing health checks
 5. Brief explanation of performance impact
diff --git a/skills/prompt-engineer/SKILL.md b/skills/prompt-engineer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: prompt-engineer
-description: Use when designing prompts for LLMs, optimizing model performance, building evaluation frameworks, or implementing advanced prompting techniques like chain-of-thought, few-shot learning, or structured outputs.
+description: Writes, refactors, and evaluates prompts for LLMs — generating optimized prompt templates, structured output schemas, evaluation rubrics, and test suites. Use when designing prompts for new LLM applications, refactoring existing prompts for better accuracy or token efficiency, implementing chain-of-thought or few-shot learning, creating system prompts with personas and guardrails, building JSON/function-calling schemas, or developing prompt evaluation frameworks to measure and improve model performance.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,10 +17,6 @@ metadata:
 
 Expert prompt engineer specializing in designing, optimizing, and evaluating prompts that maximize LLM performance across diverse use cases.
 
-## Role Definition
-
-You are an expert prompt engineer with deep knowledge of LLM capabilities, limitations, and prompting techniques. You design prompts that achieve reliable, high-quality outputs while considering token efficiency, latency, and cost. You build evaluation frameworks to measure prompt performance and iterate systematically toward optimal results.
-
 ## When to Use This Skill
 
 - Designing prompts for new LLM applications
@@ -34,11 +30,12 @@ You are an expert prompt engineer with deep knowledge of LLM capabilities, limit
 
 ## Core Workflow
 
-1. **Understand requirements** - Define task, success criteria, constraints, edge cases
-2. **Design initial prompt** - Choose pattern (zero-shot, few-shot, CoT), write clear instructions
-3. **Test and evaluate** - Run diverse test cases, measure quality metrics
-4. **Iterate and optimize** - Refine based on failures, reduce tokens, improve reliability
-5. **Document and deploy** - Version prompts, document behavior, monitor production
+1. **Understand requirements** — Define task, success criteria, constraints, and edge cases
+2. **Design initial prompt** — Choose pattern (zero-shot, few-shot, CoT), write clear instructions
+3. **Test and evaluate** — Run diverse test cases, measure quality metrics
+   - **Validation checkpoint:** If accuracy < 80% on the test set, identify failure patterns before iterating (e.g., ambiguous instructions, missing examples, edge case gaps)
+4. **Iterate and optimize** — Make one change at a time; refine based on failures, reduce tokens, improve reliability
+5. **Document and deploy** — Version prompts, document behavior, monitor production
 
 ## Reference Guide
 
@@ -52,6 +49,54 @@ Load detailed guidance based on context:
 | Structured Outputs | `references/structured-outputs.md` | JSON mode, function calling, schema design |
 | System Prompts | `references/system-prompts.md` | Persona design, guardrails, context management |
 
+## Prompt Examples
+
+### Zero-shot vs. Few-shot
+
+**Zero-shot (baseline):**
+```
+Classify the sentiment of the following review as Positive, Negative, or Neutral.
+
+Review: {{review}}
+Sentiment:
+```
+
+**Few-shot (improved reliability):**
+```
+Classify the sentiment of the following review as Positive, Negative, or Neutral.
+
+Review: "The battery life is incredible, lasts all day."
+Sentiment: Positive
+
+Review: "Stopped working after two weeks. Very disappointed."
+Sentiment: Negative
+
+Review: "It arrived on time and matches the description."
+Sentiment: Neutral
+
+Review: {{review}}
+Sentiment:
+```
+
+### Before/After Optimization
+
+**Before (vague, inconsistent outputs):**
+```
+Summarize this document.
+
+{{document}}
+```
+
+**After (structured, token-efficient):**
+```
+Summarize the document below in exactly 3 bullet points. Each bullet must be one sentence and start with an action verb. Do not include opinions or information not present in the document.
+
+Document:
+{{document}}
+
+Summary:
+```
+
 ## Constraints
 
 ### MUST DO
@@ -83,6 +128,6 @@ When delivering prompt work, provide:
 4. Performance metrics and comparison with baselines
 5. Known limitations and edge cases
 
-## Knowledge Reference
+## Coverage Note
 
-Prompt engineering techniques, chain-of-thought prompting, few-shot learning, zero-shot prompting, ReAct pattern, tree-of-thoughts, constitutional AI, prompt injection defense, system message design, JSON mode, function calling, structured generation, evaluation metrics, LLM capabilities (GPT-4, Claude, Gemini), token optimization, temperature tuning, output parsing
+Reference files cover major prompting techniques (zero-shot, few-shot, CoT, ReAct, tree-of-thoughts), structured output patterns (JSON mode, function calling), and model-specific guidance for GPT-4, Claude, and Gemini families. Consult the relevant reference before designing for a specific model or pattern.
diff --git a/skills/python-pro/SKILL.md b/skills/python-pro/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: python-pro
-description: Use when building Python 3.11+ applications requiring type safety, async programming, or production-grade patterns. Invoke for type hints, pytest, async/await, dataclasses, mypy configuration.
+description: Use when building Python 3.11+ applications requiring type safety, async programming, or robust error handling. Generates type-annotated Python code, configures mypy in strict mode, writes pytest test suites with fixtures and mocking, and validates code with black and ruff. Invoke for type hints, async/await patterns, dataclasses, dependency injection, logging configuration, and structured error handling.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,11 +15,7 @@ metadata:
 
 # Python Pro
 
-Senior Python developer with 10+ years experience specializing in type-safe, async-first, production-ready Python 3.11+ code.
-
-## Role Definition
-
-You are a senior Python engineer mastering modern Python 3.11+ and its ecosystem. You write idiomatic, type-safe, performant code across web development, data science, automation, and system programming with focus on production best practices.
+Modern Python 3.11+ specialist focused on type-safe, async-first, production-ready code.
 
 ## When to Use This Skill
 
@@ -32,11 +28,14 @@ You are a senior Python engineer mastering modern Python 3.11+ and its ecosystem
 
 ## Core Workflow
 
-1. **Analyze codebase** - Review structure, dependencies, type coverage, test suite
-2. **Design interfaces** - Define protocols, dataclasses, type aliases
-3. **Implement** - Write Pythonic code with full type hints and error handling
-4. **Test** - Create comprehensive pytest suite with >90% coverage
-5. **Validate** - Run mypy, black, ruff; ensure quality standards met
+1. **Analyze codebase** — Review structure, dependencies, type coverage, test suite
+2. **Design interfaces** — Define protocols, dataclasses, type aliases
+3. **Implement** — Write Pythonic code with full type hints and error handling
+4. **Test** — Create comprehensive pytest suite with >90% coverage
+5. **Validate** — Run `mypy --strict`, `black`, `ruff`
+   - If mypy fails: fix type errors reported and re-run before proceeding
+   - If tests fail: debug assertions, update fixtures, and iterate until green
+   - If ruff/black reports issues: apply auto-fixes, then re-validate
 
 ## Reference Guide
 
@@ -71,6 +70,100 @@ Load detailed guidance based on context:
 - Hardcode secrets or configuration
 - Use deprecated stdlib modules (use pathlib not os.path)
 
+## Code Examples
+
+### Type-annotated function with error handling
+```python
+from pathlib import Path
+
+def read_config(path: Path) -> dict[str, str]:
+    """Read configuration from a file.
+
+    Args:
+        path: Path to the configuration file.
+
+    Returns:
+        Parsed key-value configuration entries.
+
+    Raises:
+        FileNotFoundError: If the config file does not exist.
+        ValueError: If a line cannot be parsed.
+    """
+    config: dict[str, str] = {}
+    with path.open() as f:
+        for line in f:
+            key, _, value = line.partition("=")
+            if not key.strip():
+                raise ValueError(f"Invalid config line: {line!r}")
+            config[key.strip()] = value.strip()
+    return config
+```
+
+### Dataclass with validation
+```python
+from dataclasses import dataclass, field
+
+@dataclass
+class AppConfig:
+    host: str
+    port: int
+    debug: bool = False
+    allowed_origins: list[str] = field(default_factory=list)
+
+    def __post_init__(self) -> None:
+        if not (1 <= self.port <= 65535):
+            raise ValueError(f"Invalid port: {self.port}")
+```
+
+### Async pattern
+```python
+import asyncio
+import httpx
+
+async def fetch_all(urls: list[str]) -> list[bytes]:
+    """Fetch multiple URLs concurrently."""
+    async with httpx.AsyncClient() as client:
+        tasks = [client.get(url) for url in urls]
+        responses = await asyncio.gather(*tasks)
+        return [r.content for r in responses]
+```
+
+### pytest fixture and parametrize
+```python
+import pytest
+from pathlib import Path
+
+@pytest.fixture
+def config_file(tmp_path: Path) -> Path:
+    cfg = tmp_path / "config.txt"
+    cfg.write_text("host=localhost\nport=8080\n")
+    return cfg
+
+@pytest.mark.parametrize("port,valid", [(8080, True), (0, False), (99999, False)])
+def test_app_config_port_validation(port: int, valid: bool) -> None:
+    if valid:
+        AppConfig(host="localhost", port=port)
+    else:
+        with pytest.raises(ValueError):
+            AppConfig(host="localhost", port=port)
+```
+
+### mypy strict configuration (pyproject.toml)
+```toml
+[tool.mypy]
+python_version = "3.11"
+strict = true
+warn_return_any = true
+warn_unused_configs = true
+disallow_untyped_defs = true
+```
+
+Clean `mypy --strict` output looks like:
+```
+Success: no issues found in 12 source files
+```
+Any reported error (e.g., `error: Function is missing a return type annotation`) must be resolved before the implementation is considered complete.
+
 ## Output Templates
 
 When implementing Python features, provide:
diff --git a/skills/rag-architect/SKILL.md b/skills/rag-architect/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: rag-architect
-description: Use when building RAG systems, vector databases, or knowledge-grounded AI applications requiring semantic search, document retrieval, or context augmentation.
+description: Designs and implements production-grade RAG systems by chunking documents, generating embeddings, configuring vector stores, building hybrid search pipelines, applying reranking, and evaluating retrieval quality. Use when building RAG systems, vector databases, or knowledge-grounded AI applications requiring semantic search, document retrieval, context augmentation, similarity search, or embedding-based indexing.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,30 +15,15 @@ metadata:
 
 # RAG Architect
 
-Senior AI systems architect specializing in Retrieval-Augmented Generation (RAG), vector databases, and knowledge-grounded AI applications.
-
-## Role Definition
-
-You are a senior RAG architect with expertise in building production-grade retrieval systems. You specialize in vector databases, embedding models, chunking strategies, hybrid search, retrieval optimization, and RAG evaluation. You design systems that ground LLM outputs in factual knowledge while balancing latency, accuracy, and cost.
-
-## When to Use This Skill
-
-- Building RAG systems for chatbots, Q&A, or knowledge retrieval
-- Selecting and configuring vector databases
-- Designing document ingestion and chunking pipelines
-- Implementing semantic search or similarity matching
-- Optimizing retrieval quality and relevance
-- Evaluating and debugging RAG performance
-- Integrating knowledge bases with LLMs
-- Scaling vector search infrastructure
-
 ## Core Workflow
 
-1. **Requirements Analysis** - Identify retrieval needs, latency constraints, accuracy requirements, scale
-2. **Vector Store Design** - Select database, schema design, indexing strategy, sharding approach
-3. **Chunking Strategy** - Document splitting, overlap, semantic boundaries, metadata enrichment
-4. **Retrieval Pipeline** - Embedding selection, query transformation, hybrid search, reranking
-5. **Evaluation & Iteration** - Metrics tracking, retrieval debugging, continuous optimization
+1. **Requirements Analysis** — Identify retrieval needs, latency constraints, accuracy requirements, and scale
+2. **Vector Store Design** — Select database, schema design, indexing strategy, sharding approach
+3. **Chunking Strategy** — Document splitting, overlap, semantic boundaries, metadata enrichment
+4. **Retrieval Pipeline** — Embedding selection, query transformation, hybrid search, reranking
+5. **Evaluation & Iteration** — Metrics tracking, retrieval debugging, continuous optimization
+
+For each step, validate before moving on (see checkpoints below).
 
 ## Reference Guide
 
@@ -52,37 +37,158 @@ Load detailed guidance based on context:
 | Retrieval Optimization | `references/retrieval-optimization.md` | Hybrid search, reranking, query expansion, filtering |
 | RAG Evaluation | `references/rag-evaluation.md` | Metrics, evaluation frameworks, debugging retrieval |
 
+## Implementation Examples
+
+### 1. Chunking Documents
+
+```python
+from langchain.text_splitter import RecursiveCharacterTextSplitter
+
+# Evaluate chunk_size on your domain data — never use 512 blindly
+splitter = RecursiveCharacterTextSplitter(
+    chunk_size=800,
+    chunk_overlap=100,
+    separators=["\n\n", "\n", ". ", " "],
+)
+
+chunks = splitter.create_documents(
+    texts=[doc.page_content for doc in raw_docs],
+    metadatas=[{"source": doc.metadata["source"], "timestamp": doc.metadata.get("timestamp")} for doc in raw_docs],
+)
+```
+
+**Checkpoint:** `assert all(c.metadata.get("source") for c in chunks), "Missing source metadata"`
+
+### 2. Generating Embeddings & Indexing
+
+```python
+from openai import OpenAI
+import qdrant_client
+from qdrant_client.models import VectorParams, Distance, PointStruct
+
+client = OpenAI()
+qdrant = qdrant_client.QdrantClient("localhost", port=6333)
+
+# Create collection
+qdrant.recreate_collection(
+    collection_name="knowledge_base",
+    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
+)
+
+def embed_chunks(chunks: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
+    response = client.embeddings.create(input=chunks, model=model)
+    return [r.embedding for r in response.data]
+
+# Idempotent upsert with deduplication via deterministic IDs
+import hashlib, uuid
+
+points = []
+for i, chunk in enumerate(chunks):
+    doc_id = str(uuid.UUID(hashlib.md5(chunk.page_content.encode()).hexdigest()))
+    embedding = embed_chunks([chunk.page_content])[0]
+    points.append(PointStruct(id=doc_id, vector=embedding, payload=chunk.metadata))
+
+qdrant.upsert(collection_name="knowledge_base", points=points)
+```
+
+**Checkpoint:** `assert qdrant.count("knowledge_base").count == len(set(p.id for p in points)), "Deduplication failed"`
+
+### 3. Hybrid Search (Vector + BM25)
+
+```python
+from qdrant_client.models import Filter, FieldCondition, MatchValue, SparseVector
+from rank_bm25 import BM25Okapi
+
+def hybrid_search(query: str, tenant_id: str, top_k: int = 20) -> list:
+    # Dense retrieval
+    query_embedding = embed_chunks([query])[0]
+    tenant_filter = Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))])
+    dense_results = qdrant.search(
+        collection_name="knowledge_base",
+        query_vector=query_embedding,
+        query_filter=tenant_filter,
+        limit=top_k,
+    )
+
+    # Sparse retrieval (BM25)
+    corpus = [r.payload.get("text", "") for r in dense_results]
+    bm25 = BM25Okapi([doc.split() for doc in corpus])
+    bm25_scores = bm25.get_scores(query.split())
+
+    # Reciprocal Rank Fusion
+    ranked = sorted(
+        zip(dense_results, bm25_scores),
+        key=lambda x: 0.6 * x[0].score + 0.4 * x[1],
+        reverse=True,
+    )
+    return [r for r, _ in ranked[:top_k]]
+```
+
+**Checkpoint:** `assert len(hybrid_search("test query", tenant_id="demo")) > 0, "Hybrid search returned no results"`
+
+### 4. Reranking Top-K Results
+
+```python
+import cohere
+
+co = cohere.Client("YOUR_API_KEY")
+
+def rerank(query: str, results: list, top_n: int = 5) -> list:
+    docs = [r.payload.get("text", "") for r in results]
+    reranked = co.rerank(query=query, documents=docs, top_n=top_n, model="rerank-english-v3.0")
+    return [results[r.index] for r in reranked.results]
+```
+
+### 5. Retrieval Evaluation
+
+```python
+# Run precision@k and recall@k against a labeled evaluation set
+# python evaluate.py --metrics precision@10 recall@10 mrr --collection knowledge_base
+
+from ragas import evaluate
+from ragas.metrics import context_precision, context_recall, faithfulness, answer_relevancy
+from datasets import Dataset
+
+eval_dataset = Dataset.from_dict({
+    "question": questions,
+    "contexts": retrieved_contexts,
+    "answer": generated_answers,
+    "ground_truth": ground_truth_answers,
+})
+
+results = evaluate(eval_dataset, metrics=[context_precision, context_recall, faithfulness, answer_relevancy])
+print(results)
+```
+
+**Checkpoint:** Target `context_precision >= 0.7` and `context_recall >= 0.6` before moving to LLM integration.
+
 ## Constraints
 
 ### MUST DO
-- Evaluate multiple embedding models on your domain data
+- Evaluate multiple embedding models on your domain data before committing
 - Implement hybrid search (vector + keyword) for production systems
 - Add metadata filters for multi-tenant or domain-specific retrieval
 - Measure retrieval metrics (precision@k, recall@k, MRR, NDCG)
-- Use reranking for top-k results before LLM context
-- Implement idempotent ingestion with deduplication
+- Use reranking for top-k results before passing context to LLM
+- Implement idempotent ingestion with deduplication (deterministic IDs)
 - Monitor retrieval latency and quality over time
-- Version embeddings and handle model migration
+- Version embeddings and plan for model migration
 
 ### MUST NOT DO
-- Use default chunk size (512) without evaluation
+- Use default chunk size (512) without evaluation on your domain data
 - Skip metadata enrichment (source, timestamp, section)
-- Ignore retrieval quality metrics in favor of only LLM output
+- Ignore retrieval quality metrics in favor of only LLM output quality
 - Store raw documents without preprocessing/cleaning
-- Use cosine similarity alone for complex domains
-- Deploy without testing on production-like data volume
+- Use cosine similarity alone for complex multi-domain retrieval
+- Deploy without testing on production-like data volumes
 - Forget to handle edge cases (empty results, malformed docs)
-- Couple embedding model tightly to application code
+- Couple the embedding model tightly to application code
 
 ## Output Templates
 
-When designing RAG architecture, provide:
+When designing RAG architecture, deliver:
 1. System architecture diagram (ingestion + retrieval pipelines)
 2. Vector database selection with trade-off analysis
 3. Chunking strategy with examples and rationale
-4. Retrieval pipeline design (query -> results flow)
-5. Evaluation plan with metrics and benchmarks
-
-## Knowledge Reference
-
-Vector databases (Pinecone, Weaviate, Chroma, Qdrant, Milvus, pgvector), embedding models (OpenAI, Cohere, Sentence Transformers, BGE, E5), chunking algorithms, semantic search, hybrid search, BM25, reranking (Cohere, Cross-Encoder), query expansion, HyDE, metadata filtering, HNSW indexes, quantization, embedding fine-tuning, RAG evaluation frameworks (RAGAS, TruLens)
+4. Retrieval pipeline design (query → results flow)
+5. Evaluation plan with metrics, benchmarks, and pass/fail thresholds
diff --git a/skills/rails-expert/SKILL.md b/skills/rails-expert/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: rails-expert
-description: Use when building Rails 7+ web applications with Hotwire, real-time features, or background job processing. Invoke for Active Record optimization, Turbo Frames/Streams, Action Cable, Sidekiq.
+description: Rails 7+ specialist that optimizes Active Record queries with includes/eager_load, implements Turbo Frames and Turbo Streams for partial page updates, configures Action Cable for WebSocket connections, sets up Sidekiq workers for background job processing, and writes comprehensive RSpec test suites. Use when building Rails 7+ web applications with Hotwire, real-time features, or background job processing. Invoke for Active Record optimization, Turbo Frames/Streams, Action Cable, Sidekiq, RSpec Rails.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,28 +15,17 @@ metadata:
 
 # Rails Expert
 
-Senior Rails specialist with deep expertise in Rails 7+, Hotwire, and modern Ruby web development patterns.
-
-## Role Definition
-
-You are a senior Ruby on Rails engineer with 10+ years of Rails development experience. You specialize in Rails 7+ with Hotwire/Turbo, convention over configuration, and building maintainable applications. You prioritize developer happiness and rapid development.
-
-## When to Use This Skill
-
-- Building Rails 7+ applications with modern patterns
-- Implementing Hotwire/Turbo for reactive UIs
-- Setting up Action Cable for real-time features
-- Implementing background jobs with Sidekiq
-- Optimizing Active Record queries and performance
-- Writing comprehensive RSpec test suites
-
 ## Core Workflow
 
-1. **Analyze requirements** - Identify models, routes, real-time needs, background jobs
-2. **Design architecture** - Plan MVC structure, associations, service objects
-3. **Implement** - Generate resources, write controllers, add Hotwire
-4. **Optimize** - Prevent N+1 queries, add caching, optimize assets
-5. **Test** - Write model/request/system specs with high coverage
+1. **Analyze requirements** — Identify models, routes, real-time needs, background jobs
+2. **Scaffold resources** — `rails generate model User name:string email:string`, `rails generate controller Users`
+3. **Run migrations** — `rails db:migrate` and verify schema with `rails db:schema:dump`
+   - If migration fails: inspect `db/schema.rb` for conflicts, rollback with `rails db:rollback`, fix and retry
+4. **Implement** — Write controllers, models, add Hotwire (see Reference Guide below)
+5. **Validate** — `bundle exec rspec` must pass; `bundle exec rubocop` for style
+   - If specs fail: check error output, fix failing examples, re-run with `--format documentation` for detail
+   - If N+1 queries surface during review: add `includes`/`eager_load` (see Common Patterns) and re-run specs
+6. **Optimize** — Audit for N+1 queries, add missing indexes, add caching
 
 ## Reference Guide
 
@@ -50,38 +39,116 @@ Load detailed guidance based on context:
 | Testing | `references/rspec-testing.md` | Model/request/system specs, factories |
 | API Development | `references/api-development.md` | API-only mode, serialization, authentication |
 
+## Common Patterns
+
+### N+1 Prevention with includes/eager_load
+
+```ruby
+# BAD — triggers N+1
+posts = Post.all
+posts.each { |post| puts post.author.name }
+
+# GOOD — eager load association
+posts = Post.includes(:author).all
+posts.each { |post| puts post.author.name }
+
+# GOOD — eager_load forces a JOIN (useful when filtering on association)
+posts = Post.eager_load(:author).where(authors: { verified: true })
+```
+
+### Turbo Frame Setup (partial page update)
+
+```erb
+<%# app/views/posts/index.html.erb %>
+<%= turbo_frame_tag "posts" do %>
+  <%= render @posts %>
+  <%= link_to "Load More", posts_path(page: @next_page) %>
+<% end %>
+
+<%# app/views/posts/_post.html.erb %>
+<%= turbo_frame_tag dom_id(post) do %>
+  <h2><%= post.title %></h2>
+  <%= link_to "Edit", edit_post_path(post) %>
+<% end %>
+```
+
+```ruby
+# app/controllers/posts_controller.rb
+def index
+  @posts = Post.includes(:author).page(params[:page])
+  @next_page = @posts.next_page
+end
+```
+
+### Sidekiq Worker Template
+
+```ruby
+# app/jobs/send_welcome_email_job.rb
+class SendWelcomeEmailJob < ApplicationJob
+  queue_as :default
+  sidekiq_options retry: 3, dead: false
+
+  def perform(user_id)
+    user = User.find(user_id)
+    UserMailer.welcome(user).deliver_now
+  rescue ActiveRecord::RecordNotFound => e
+    Rails.logger.warn("SendWelcomeEmailJob: user #{user_id} not found — #{e.message}")
+    # Do not re-raise; record is gone, no point retrying
+  end
+end
+
+# Enqueue from controller or model callback
+SendWelcomeEmailJob.perform_later(user.id)
+```
+
+### Strong Parameters (controller template)
+
+```ruby
+# app/controllers/posts_controller.rb
+class PostsController < ApplicationController
+  before_action :set_post, only: %i[show edit update destroy]
+
+  def create
+    @post = Post.new(post_params)
+    if @post.save
+      redirect_to @post, notice: "Post created."
+    else
+      render :new, status: :unprocessable_entity
+    end
+  end
+
+  private
+
+  def set_post
+    @post = Post.find(params[:id])
+  end
+
+  def post_params
+    params.require(:post).permit(:title, :body, :published_at)
+  end
+end
+```
+
 ## Constraints
 
 ### MUST DO
-- Follow Rails conventions (convention over configuration)
-- Use RESTful routing and resourceful controllers
-- Prevent N+1 queries (use includes/eager_load)
-- Write comprehensive specs (aim for >95% coverage)
-- Use strong parameters for mass assignment protection
-- Implement proper error handling and validations
-- Use service objects for complex business logic
-- Keep controllers thin, models focused
+- Prevent N+1 queries with `includes`/`eager_load` on every collection query involving associations
+- Write comprehensive specs targeting >95% coverage
+- Use service objects for complex business logic; keep controllers thin
+- Add database indexes for every column used in `WHERE`, `ORDER BY`, or `JOIN`
+- Offload slow operations to Sidekiq — never run them synchronously in a request cycle
 
 ### MUST NOT DO
 - Skip migrations for schema changes
-- Store sensitive data unencrypted
-- Use raw SQL without sanitization
-- Skip CSRF protection
+- Use raw SQL without sanitization (`sanitize_sql` or parameterized queries only)
 - Expose internal IDs in URLs without consideration
-- Use synchronous operations for slow tasks
-- Skip database indexes for queried columns
-- Mix business logic in controllers
 
 ## Output Templates
 
 When implementing Rails features, provide:
 1. Migration file (if schema changes needed)
 2. Model file with associations and validations
-3. Controller with RESTful actions
+3. Controller with RESTful actions and strong parameters
 4. View files or Hotwire setup
 5. Spec files for models and requests
 6. Brief explanation of architectural decisions
-
-## Knowledge Reference
-
-Rails 7+, Hotwire/Turbo, Stimulus, Action Cable, Active Record, Sidekiq, RSpec, FactoryBot, Capybara, ViewComponent, Kredis, Import Maps, Tailwind CSS, PostgreSQL
diff --git a/skills/react-expert/SKILL.md b/skills/react-expert/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: react-expert
-description: Use when building React 18+ applications requiring component architecture, hooks patterns, or state management. Invoke for Server Components, performance optimization, Suspense boundaries, React 19 features.
+description: Use when building React 18+ applications in .jsx or .tsx files, Next.js App Router projects, or create-react-app setups. Creates components, implements custom hooks, debugs rendering issues, migrates class components to functional, and implements state management. Invoke for Server Components, Suspense boundaries, useActionState forms, performance optimization, or React 19 features.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,10 +17,6 @@ metadata:
 
 Senior React specialist with deep expertise in React 19, Server Components, and production-grade application architecture.
 
-## Role Definition
-
-You are a senior React engineer with 10+ years of frontend experience. You specialize in React 19 patterns including Server Components, the `use()` hook, and form actions. You build accessible, performant applications with TypeScript and modern state management.
-
 ## When to Use This Skill
 
 - Building new React components or features
@@ -36,8 +32,9 @@ You are a senior React engineer with 10+ years of frontend experience. You speci
 1. **Analyze requirements** - Identify component hierarchy, state needs, data flow
 2. **Choose patterns** - Select appropriate state management, data fetching approach
 3. **Implement** - Write TypeScript components with proper types
-4. **Optimize** - Apply memoization where needed, ensure accessibility
-5. **Test** - Write tests with React Testing Library
+4. **Validate** - Run `tsc --noEmit`; if it fails, review reported errors, fix all type issues, and re-run until clean before proceeding
+5. **Optimize** - Apply memoization where needed, ensure accessibility; if new type errors are introduced, return to step 4
+6. **Test** - Write tests with React Testing Library; if any assertions fail, debug and fix before submitting
 
 ## Reference Guide
 
@@ -53,6 +50,74 @@ Load detailed guidance based on context:
 | Testing | `references/testing-react.md` | Testing Library, mocking |
 | Class Migration | `references/migration-class-to-modern.md` | Converting class components to hooks/RSC |
 
+## Key Patterns
+
+### Server Component (Next.js App Router)
+```tsx
+// app/users/page.tsx — Server Component, no "use client"
+import { db } from '@/lib/db';
+
+interface User {
+  id: string;
+  name: string;
+}
+
+export default async function UsersPage() {
+  const users: User[] = await db.user.findMany();
+
+  return (
+    <ul>
+      {users.map((user) => (
+        <li key={user.id}>{user.name}</li>
+      ))}
+    </ul>
+  );
+}
+```
+
+### React 19 Form with `useActionState`
+```tsx
+'use client';
+import { useActionState } from 'react';
+
+async function submitForm(_prev: string, formData: FormData): Promise<string> {
+  const name = formData.get('name') as string;
+  // perform server action or fetch
+  return `Hello, ${name}!`;
+}
+
+export function GreetForm() {
+  const [message, action, isPending] = useActionState(submitForm, '');
+
+  return (
+    <form action={action}>
+      <input name="name" required />
+      <button type="submit" disabled={isPending}>
+        {isPending ? 'Submitting…' : 'Submit'}
+      </button>
+      {message && <p>{message}</p>}
+    </form>
+  );
+}
+```
+
+### Custom Hook with Cleanup
+```tsx
+import { useState, useEffect } from 'react';
+
+function useWindowWidth(): number {
+  const [width, setWidth] = useState(() => window.innerWidth);
+
+  useEffect(() => {
+    const handler = () => setWidth(window.innerWidth);
+    window.addEventListener('resize', handler);
+    return () => window.removeEventListener('resize', handler); // cleanup
+  }, []);
+
+  return width;
+}
+```
+
 ## Constraints
 
 ### MUST DO
diff --git a/skills/react-native-expert/SKILL.md b/skills/react-native-expert/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: react-native-expert
-description: Use when building cross-platform mobile applications with React Native or Expo. Invoke for navigation patterns, platform-specific code, native modules, FlatList optimization.
+description: Builds, optimizes, and debugs cross-platform mobile applications with React Native and Expo. Implements navigation hierarchies (tabs, stacks, drawers), configures native modules, optimizes FlatList rendering with memo and useCallback, and handles platform-specific code for iOS and Android. Use when building a React Native or Expo mobile app, setting up navigation, integrating native modules, improving scroll performance, handling SafeArea or keyboard input, or configuring Expo SDK projects.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,19 @@ metadata:
 
 Senior mobile engineer building production-ready cross-platform applications with React Native and Expo.
 
-## Role Definition
-
-You are a senior mobile developer with 8+ years of React Native experience. You specialize in Expo SDK 50+, React Navigation 7, and performance optimization for mobile. You build apps that feel truly native on both iOS and Android.
-
-## When to Use This Skill
-
-- Building cross-platform mobile applications
-- Implementing navigation (tabs, stacks, drawers)
-- Handling platform-specific code (iOS/Android)
-- Optimizing FlatList performance
-- Integrating native modules
-- Setting up Expo or bare React Native projects
-
 ## Core Workflow
 
-1. **Setup** - Expo Router or React Navigation, TypeScript config
-2. **Structure** - Feature-based organization
-3. **Implement** - Components with platform handling
-4. **Optimize** - FlatList, images, memory
-5. **Test** - Both platforms, real devices
+1. **Setup** — Expo Router or React Navigation, TypeScript config → _run `npx expo doctor` to verify environment and SDK compatibility; fix any reported issues before proceeding_
+2. **Structure** — Feature-based organization
+3. **Implement** — Components with platform handling → _verify on iOS simulator and Android emulator; check Metro bundler output for errors before moving on_
+4. **Optimize** — FlatList, images, memory → _profile with Flipper or React DevTools_
+5. **Test** — Both platforms, real devices
+
+### Error Recovery
+- **Metro bundler errors** → clear cache with `npx expo start --clear`, then restart
+- **iOS build fails** → check Xcode logs → resolve native dependency or provisioning issue → rebuild with `npx expo run:ios`
+- **Android build fails** → check `adb logcat` or Gradle output → resolve SDK/NDK version mismatch → rebuild with `npx expo run:android`
+- **Native module not found** → run `npx expo install <module>` to ensure compatible version, then rebuild native layers
 
 ## Reference Guide
 
@@ -68,13 +61,124 @@ Load detailed guidance based on context:
 - Skip platform-specific testing
 - Use waitFor/setTimeout for animations (use Reanimated)
 
-## Output Templates
-
-When implementing React Native features, provide:
-1. Component code with TypeScript
-2. Platform-specific handling
-3. Navigation integration
-4. Performance considerations noted
+## Code Examples
+
+### Optimized FlatList with memo + useCallback
+
+```tsx
+import React, { memo, useCallback } from 'react';
+import { FlatList, View, Text, StyleSheet } from 'react-native';
+
+type Item = { id: string; title: string };
+
+const ListItem = memo(({ title, onPress }: { title: string; onPress: () => void }) => (
+  <View style={styles.item}>
+    <Text onPress={onPress}>{title}</Text>
+  </View>
+));
+
+export function ItemList({ data }: { data: Item[] }) {
+  const handlePress = useCallback((id: string) => {
+    console.log('pressed', id);
+  }, []);
+
+  const renderItem = useCallback(
+    ({ item }: { item: Item }) => (
+      <ListItem title={item.title} onPress={() => handlePress(item.id)} />
+    ),
+    [handlePress]
+  );
+
+  return (
+    <FlatList
+      data={data}
+      keyExtractor={(item) => item.id}
+      renderItem={renderItem}
+      removeClippedSubviews
+      maxToRenderPerBatch={10}
+      windowSize={5}
+    />
+  );
+}
+
+const styles = StyleSheet.create({
+  item: { padding: 16, borderBottomWidth: StyleSheet.hairlineWidth },
+});
+```
+
+### KeyboardAvoidingView Form
+
+```tsx
+import React from 'react';
+import {
+  KeyboardAvoidingView,
+  Platform,
+  ScrollView,
+  TextInput,
+  StyleSheet,
+  SafeAreaView,
+} from 'react-native';
+
+export function LoginForm() {
+  return (
+    <SafeAreaView style={styles.safe}>
+      <KeyboardAvoidingView
+        style={styles.flex}
+        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
+      >
+        <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
+          <TextInput style={styles.input} placeholder="Email" autoCapitalize="none" />
+          <TextInput style={styles.input} placeholder="Password" secureTextEntry />
+        </ScrollView>
+      </KeyboardAvoidingView>
+    </SafeAreaView>
+  );
+}
+
+const styles = StyleSheet.create({
+  safe: { flex: 1 },
+  flex: { flex: 1 },
+  content: { padding: 16, gap: 12 },
+  input: { borderWidth: 1, borderRadius: 8, padding: 12, fontSize: 16 },
+});
+```
+
+### Platform-Specific Component
+
+```tsx
+import { Platform, StyleSheet, View, Text } from 'react-native';
+
+export function StatusChip({ label }: { label: string }) {
+  return (
+    <View style={styles.chip}>
+      <Text style={styles.label}>{label}</Text>
+    </View>
+  );
+}
+
+const styles = StyleSheet.create({
+  chip: {
+    paddingHorizontal: 12,
+    paddingVertical: 4,
+    borderRadius: 999,
+    backgroundColor: '#0a7ea4',
+    // Platform-specific shadow
+    ...Platform.select({
+      ios: { shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.2, shadowRadius: 4 },
+      android: { elevation: 3 },
+    }),
+  },
+  label: { color: '#fff', fontSize: 13, fontWeight: '600' },
+});
+```
+
+## Output Format
+
+When implementing React Native features, deliver:
+1. **Component code** — TypeScript, with prop types defined
+2. **Platform handling** — `Platform.select` or `.ios.tsx` / `.android.tsx` splits as needed
+3. **Navigation integration** — route params typed, back-button handling included
+4. **Performance notes** — memo boundaries, key extractor strategy, image caching
 
 ## Knowledge Reference
 
diff --git a/skills/rust-engineer/SKILL.md b/skills/rust-engineer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: rust-engineer
-description: Use when building Rust applications requiring memory safety, systems programming, or zero-cost abstractions. Invoke for ownership patterns, lifetimes, traits, async/await with tokio.
+description: Writes, reviews, and debugs idiomatic Rust code with memory safety and zero-cost abstractions. Implements ownership patterns, manages lifetimes, designs trait hierarchies, builds async applications with tokio, and structures error handling with Result/Option. Use when building Rust applications, solving ownership or borrowing issues, designing trait-based APIs, implementing async/await concurrency, creating FFI bindings, or optimizing for performance and memory safety. Invoke for Rust, Cargo, ownership, borrowing, lifetimes, async Rust, tokio, zero-cost abstractions, memory safety, systems programming.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,13 @@ metadata:
 
 Senior Rust engineer with deep expertise in Rust 2021 edition, systems programming, memory safety, and zero-cost abstractions. Specializes in building reliable, high-performance software leveraging Rust's ownership system.
 
-## Role Definition
-
-You are a senior Rust engineer with 10+ years of systems programming experience. You specialize in Rust's ownership model, async programming with tokio, trait-based design, and performance optimization. You build memory-safe, concurrent systems with zero-cost abstractions.
-
-## When to Use This Skill
-
-- Building systems-level applications in Rust
-- Implementing ownership and borrowing patterns
-- Designing trait hierarchies and generic APIs
-- Setting up async/await with tokio or async-std
-- Optimizing for performance and memory safety
-- Creating FFI bindings and unsafe abstractions
-
 ## Core Workflow
 
-1. **Analyze ownership** - Design lifetime relationships and borrowing patterns
-2. **Design traits** - Create trait hierarchies with generics and associated types
-3. **Implement safely** - Write idiomatic Rust with minimal unsafe code
-4. **Handle errors** - Use Result/Option with ? operator and custom error types
-5. **Test thoroughly** - Unit tests, integration tests, property testing, benchmarks
+1. **Analyze ownership** — Design lifetime relationships and borrowing patterns; annotate lifetimes explicitly where inference is insufficient
+2. **Design traits** — Create trait hierarchies with generics and associated types
+3. **Implement safely** — Write idiomatic Rust with minimal unsafe code; document every `unsafe` block with its safety invariants
+4. **Handle errors** — Use `Result`/`Option` with `?` operator and custom error types via `thiserror`
+5. **Validate** — Run `cargo clippy --all-targets --all-features`, `cargo fmt --check`, and `cargo test`; fix all warnings before finalising
 
 ## Reference Guide
 
@@ -50,26 +37,120 @@ Load detailed guidance based on context:
 | Async | `references/async.md` | async/await, tokio, futures, streams, concurrency |
 | Testing | `references/testing.md` | Unit/integration tests, proptest, benchmarks |
 
+## Key Patterns with Examples
+
+### Ownership & Lifetimes
+
+```rust
+// Explicit lifetime annotation — borrow lives as long as the input slice
+fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
+    if x.len() > y.len() { x } else { y }
+}
+
+// Prefer borrowing over cloning
+fn process(data: &[u8]) -> usize {   // &[u8] not Vec<u8>
+    data.iter().filter(|&&b| b != 0).count()
+}
+```
+
+### Trait-Based Design
+
+```rust
+use std::fmt;
+
+trait Summary {
+    fn summarise(&self) -> String;
+    fn preview(&self) -> String {          // default implementation
+        format!("{}...", &self.summarise()[..50])
+    }
+}
+
+#[derive(Debug)]
+struct Article { title: String, body: String }
+
+impl Summary for Article {
+    fn summarise(&self) -> String {
+        format!("{}: {}", self.title, self.body)
+    }
+}
+```
+
+### Error Handling with `thiserror`
+
+```rust
+use thiserror::Error;
+
+#[derive(Debug, Error)]
+pub enum AppError {
+    #[error("I/O error: {0}")]
+    Io(#[from] std::io::Error),
+    #[error("parse error for value `{value}`: {reason}")]
+    Parse { value: String, reason: String },
+}
+
+// ? propagates errors ergonomically
+fn read_config(path: &str) -> Result<String, AppError> {
+    let content = std::fs::read_to_string(path)?;  // Io variant via #[from]
+    Ok(content)
+}
+```
+
+### Async / Await with Tokio
+
+```rust
+use tokio::time::{sleep, Duration};
+
+#[tokio::main]
+async fn main() -> Result<(), Box<dyn std::error::Error>> {
+    let result = fetch_data("https://example.com").await?;
+    println!("{result}");
+    Ok(())
+}
+
+async fn fetch_data(url: &str) -> Result<String, reqwest::Error> {
+    let body = reqwest::get(url).await?.text().await?;
+    Ok(body)
+}
+
+// Spawn concurrent tasks — never mix blocking calls into async context
+async fn parallel_work() {
+    let (a, b) = tokio::join!(
+        sleep(Duration::from_millis(100)),
+        sleep(Duration::from_millis(100)),
+    );
+}
+```
+
+### Validation Commands
+
+```bash
+cargo fmt --check                          # style check
+cargo clippy --all-targets --all-features  # lints
+cargo test                                 # unit + integration tests
+cargo test --doc                           # doctests
+cargo bench                                # criterion benchmarks (if present)
+```
+
 ## Constraints
 
 ### MUST DO
 - Use ownership and borrowing for memory safety
-- Minimize unsafe code (document all unsafe blocks)
+- Minimize unsafe code (document all unsafe blocks with safety invariants)
 - Use type system for compile-time guarantees
-- Handle all errors explicitly (Result/Option)
+- Handle all errors explicitly (`Result`/`Option`)
 - Add comprehensive documentation with examples
-- Run clippy and fix all warnings
-- Use cargo fmt for consistent formatting
+- Run `cargo clippy` and fix all warnings
+- Use `cargo fmt` for consistent formatting
 - Write tests including doctests
 
 ### MUST NOT DO
-- Use unwrap() in production code (prefer expect() with messages)
+- Use `unwrap()` in production code (prefer `expect()` with messages)
 - Create memory leaks or dangling pointers
-- Use unsafe without documenting safety invariants
+- Use `unsafe` without documenting safety invariants
 - Ignore clippy warnings
 - Mix blocking and async code incorrectly
 - Skip error handling
-- Use String when &str suffices
+- Use `String` when `&str` suffices
 - Clone unnecessarily (use borrowing)
 
 ## Output Templates
diff --git a/skills/salesforce-developer/SKILL.md b/skills/salesforce-developer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: salesforce-developer
-description: Use when developing Salesforce applications, Apex code, Lightning Web Components, SOQL queries, triggers, integrations, or CRM customizations. Invoke for governor limits, bulk processing, platform events, Salesforce DX.
+description: Writes and debugs Apex code, builds Lightning Web Components, optimizes SOQL queries, implements triggers, batch jobs, platform events, and integrations on the Salesforce platform. Use when developing Salesforce applications, customizing CRM workflows, managing governor limits, bulk processing, or setting up Salesforce DX and CI/CD pipelines.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,30 +15,14 @@ metadata:
 
 # Salesforce Developer
 
-Senior Salesforce developer with expertise in Apex, Lightning Web Components, declarative automation, and enterprise CRM integrations built on the Salesforce platform.
-
-## Role Definition
-
-You are a senior Salesforce developer with deep experience building enterprise-grade solutions on the Salesforce platform. You specialize in Apex development, Lightning Web Components, SOQL optimization, governor limit management, integration patterns, and Salesforce DX. You build scalable, maintainable solutions following Salesforce best practices and platform limitations.
-
-## When to Use This Skill
-
-- Building custom Apex classes and triggers
-- Developing Lightning Web Components (LWC)
-- Optimizing SOQL/SOSL queries for performance
-- Implementing platform events and integrations
-- Creating batch, queueable, and scheduled Apex
-- Setting up Salesforce DX and CI/CD pipelines
-- Managing governor limits in bulk operations
-- Integrating Salesforce with external systems
-
 ## Core Workflow
 
 1. **Analyze requirements** - Understand business needs, data model, governor limits, scalability
 2. **Design solution** - Choose declarative vs programmatic, plan bulkification, design integrations
 3. **Implement** - Write Apex classes, LWC components, SOQL queries with best practices
-4. **Test thoroughly** - Write test classes with 90%+ coverage, test bulk scenarios
-5. **Deploy** - Use Salesforce DX, scratch orgs, CI/CD for metadata deployment
+4. **Validate governor limits** - Verify SOQL/DML counts, heap size, and CPU time stay within platform limits before proceeding
+5. **Test thoroughly** - Write test classes with 90%+ coverage, test bulk scenarios (200-record batches)
+6. **Deploy** - Use Salesforce DX, scratch orgs, CI/CD for metadata deployment
 
 ## Reference Guide
 
@@ -55,36 +39,165 @@ Load detailed guidance based on context:
 ## Constraints
 
 ### MUST DO
-- Always bulkify Apex code for governor limit compliance
-- Write test classes with minimum 90% code coverage
-- Use SOQL best practices (selective queries, relationship queries)
-- Handle governor limits (SOQL queries, DML statements, heap size)
-- Follow Lightning Web Components best practices
-- Use appropriate async processing (batch, queueable, future)
-- Implement proper error handling and logging
-- Use Salesforce DX for source-driven development
+- Bulkify Apex code — collect IDs/records before loops, query/DML outside loops
+- Write test classes with minimum 90% code coverage, including bulk scenarios
+- Use selective SOQL queries with indexed fields; leverage relationship queries
+- Use appropriate async processing (batch, queueable, future) for long-running work
+- Implement proper error handling and logging; use `Database.update(scope, false)` for partial success
+- Use Salesforce DX for source-driven development and metadata deployment
 
 ### MUST NOT DO
-- Execute SOQL/DML inside loops (causes governor limit violations)
-- Use hard-coded IDs or credentials in code
-- Skip bulkification in triggers and batch processes
-- Ignore test coverage requirements (<90%)
-- Mix declarative and programmatic solutions unnecessarily
+- Execute SOQL/DML inside loops (governor limit violation — see bulkified trigger pattern below)
+- Hard-code IDs or credentials in code
 - Create recursive triggers without safeguards
 - Skip field-level security and sharing rules checks
 - Use deprecated Salesforce APIs or components
 
-## Output Templates
-
-When implementing Salesforce features, provide:
-1. Apex classes with proper structure and documentation
-2. Trigger handlers following best practices
-3. Lightning Web Components (HTML, JS, meta.xml)
-4. Test classes with comprehensive scenarios
-5. SOQL queries optimized for performance
-6. Integration code with error handling
-7. Brief explanation of governor limit considerations
-
-## Knowledge Reference
-
-Apex, Lightning Web Components (LWC), SOQL/SOSL, Salesforce DX, Triggers, Batch Apex, Queueable Apex, Platform Events, REST/SOAP APIs, Process Builder, Flow, Visualforce, Governor Limits, Test Classes, Metadata API, Deployment, CI/CD, Jest Testing
+## Code Patterns
+
+### Bulkified Trigger (Correct Pattern)
+
+```apex
+// CORRECT: collect IDs, query once outside the loop
+trigger AccountTrigger on Account (before insert, before update) {
+    AccountTriggerHandler.handleBeforeInsert(Trigger.new);
+}
+
+public class AccountTriggerHandler {
+    public static void handleBeforeInsert(List<Account> newAccounts) {
+        Set<Id> parentIds = new Set<Id>();
+        for (Account acc : newAccounts) {
+            if (acc.ParentId != null) parentIds.add(acc.ParentId);
+        }
+        Map<Id, Account> parentMap = new Map<Id, Account>(
+            [SELECT Id, Name FROM Account WHERE Id IN :parentIds]
+        );
+        for (Account acc : newAccounts) {
+            if (acc.ParentId != null && parentMap.containsKey(acc.ParentId)) {
+                acc.Description = 'Child of: ' + parentMap.get(acc.ParentId).Name;
+            }
+        }
+    }
+}
+```
+
+```apex
+// INCORRECT: SOQL inside loop — governor limit violation
+trigger AccountTrigger on Account (before insert) {
+    for (Account acc : Trigger.new) {
+        Account parent = [SELECT Id, Name FROM Account WHERE Id = :acc.ParentId]; // BAD
+        acc.Description = 'Child of: ' + parent.Name;
+    }
+}
+```
+
+### Batch Apex
+
+```apex
+public class ContactBatchUpdate implements Database.Batchable<SObject> {
+    public Database.QueryLocator start(Database.BatchableContext bc) {
+        return Database.getQueryLocator([SELECT Id, Email FROM Contact WHERE Email = null]);
+    }
+    public void execute(Database.BatchableContext bc, List<Contact> scope) {
+        for (Contact c : scope) {
+            c.Email = 'unknown@example.com';
+        }
+        Database.update(scope, false); // partial success allowed
+    }
+    public void finish(Database.BatchableContext bc) {
+        // Send notification or chain next batch
+    }
+}
+// Execute: Database.executeBatch(new ContactBatchUpdate(), 200);
+```
+
+### Test Class
+
+```apex
+@IsTest
+private class AccountTriggerHandlerTest {
+    @TestSetup
+    static void makeData() {
+        Account parent = new Account(Name = 'Parent Co');
+        insert parent;
+        Account child = new Account(Name = 'Child Co', ParentId = parent.Id);
+        insert child;
+    }
+
+    @IsTest
+    static void testBulkInsert() {
+        Account parent = [SELECT Id FROM Account WHERE Name = 'Parent Co' LIMIT 1];
+        List<Account> children = new List<Account>();
+        for (Integer i = 0; i < 200; i++) {
+            children.add(new Account(Name = 'Child ' + i, ParentId = parent.Id));
+        }
+        Test.startTest();
+        insert children;
+        Test.stopTest();
+
+        List<Account> updated = [SELECT Description FROM Account WHERE ParentId = :parent.Id];
+        System.assert(!updated.isEmpty(), 'Children should have descriptions set');
+        System.assert(updated[0].Description.startsWith('Child of:'), 'Description format mismatch');
+    }
+}
+```
+
+### SOQL Best Practices
+
+```apex
+// Selective query — use indexed fields in WHERE clause
+List<Opportunity> opps = [
+    SELECT Id, Name, Amount, StageName
+    FROM Opportunity
+    WHERE AccountId IN :accountIds      // indexed field
+      AND CloseDate >= :Date.today()    // indexed field
+    ORDER BY CloseDate ASC
+    LIMIT 200
+];
+
+// Relationship query to avoid extra round-trips
+List<Account> accounts = [
+    SELECT Id, Name,
+           (SELECT Id, LastName, Email FROM Contacts WHERE Email != null)
+    FROM Account
+    WHERE Id IN :accountIds
+];
+```
+
+### Lightning Web Component (Counter Example)
+
+```html
+<!-- counterComponent.html -->
+<template>
+    <lightning-card title="Counter">
+        <div class="slds-p-around_medium">
+            <p>Count: {count}</p>
+            <lightning-button label="Increment" onclick={handleIncrement}></lightning-button>
+        </div>
+    </lightning-card>
+</template>
+```
+
+```javascript
+// counterComponent.js
+import { LightningElement, track } from 'lwc';
+export default class CounterComponent extends LightningElement {
+    @track count = 0;
+    handleIncrement() {
+        this.count += 1;
+    }
+}
+```
+
+```xml
+<!-- counterComponent.js-meta.xml -->
+<?xml version="1.0" encoding="UTF-8"?>
+<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
+    <apiVersion>59.0</apiVersion>
+    <isExposed>true</isExposed>
+    <targets>
+        <target>lightning__AppPage</target>
+        <target>lightning__RecordPage</target>
+    </targets>
+</LightningComponentBundle>
+```
diff --git a/skills/secure-code-guardian/SKILL.md b/skills/secure-code-guardian/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: secure-code-guardian
-description: Use when implementing authentication/authorization, securing user input, or preventing OWASP Top 10 vulnerabilities. Invoke for authentication, authorization, input validation, encryption, OWASP Top 10 prevention.
+description: Use when implementing authentication/authorization, securing user input, or preventing OWASP Top 10 vulnerabilities — including custom security implementations such as hashing passwords with bcrypt/argon2, sanitizing SQL queries with parameterized statements, configuring CORS/CSP headers, validating input with Zod, and setting up JWT tokens. Invoke for authentication, authorization, input validation, encryption, OWASP Top 10 prevention, secure session management, and security hardening. For pre-built OAuth/SSO integrations or standalone security audits, consider a more specialized skill.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,28 +15,22 @@ metadata:
 
 # Secure Code Guardian
 
-Security-focused developer specializing in writing secure code and preventing vulnerabilities.
-
-## Role Definition
-
-You are a senior security engineer with 10+ years of application security experience. You specialize in secure coding practices, OWASP Top 10 prevention, and implementing authentication/authorization. You think defensively and assume all input is malicious.
+## Core Workflow
 
-## When to Use This Skill
+1. **Threat model** — Identify attack surface and threats
+2. **Design** — Plan security controls
+3. **Implement** — Write secure code with defense in depth; see code examples below
+4. **Validate** — Test security controls with explicit checkpoints (see below)
+5. **Document** — Record security decisions
 
-- Implementing authentication/authorization
-- Securing user input handling
-- Implementing encryption
-- Preventing OWASP Top 10 vulnerabilities
-- Security hardening existing code
-- Implementing secure session management
+### Validation Checkpoints
 
-## Core Workflow
+After each implementation step, verify:
 
-1. **Threat model** - Identify attack surface and threats
-2. **Design** - Plan security controls
-3. **Implement** - Write secure code with defense in depth
-4. **Validate** - Test security controls
-5. **Document** - Record security decisions
+- **Authentication**: Test brute-force protection (lockout/rate limit triggers), session fixation resistance, token expiration, and invalid-credential error messages (must not leak user existence).
+- **Authorization**: Verify horizontal and vertical privilege escalation paths are blocked; test with tokens belonging to different roles/users.
+- **Input handling**: Confirm SQL injection payloads (`' OR 1=1--`) are rejected; confirm XSS payloads (`<script>alert(1)</script>`) are escaped or rejected.
+- **Headers/CORS**: Validate with a security scanner (e.g., `curl -I`, Mozilla Observatory) that security headers are present and CORS origin allowlist is correct.
 
 ## Reference Guide
 
@@ -53,22 +47,136 @@ Load detailed guidance based on context:
 ## Constraints
 
 ### MUST DO
-- Hash passwords with bcrypt/argon2 (never plaintext)
-- Use parameterized queries (prevent SQL injection)
-- Validate and sanitize all user input
+- Hash passwords with bcrypt/argon2 (never MD5/SHA-1/unsalted hashes)
+- Use parameterized queries (never string-interpolated SQL)
+- Validate and sanitize all user input before use
 - Implement rate limiting on auth endpoints
-- Use HTTPS everywhere
-- Set security headers
-- Log security events
-- Store secrets in environment/secret managers
+- Set security headers (CSP, HSTS, X-Frame-Options)
+- Log security events (failed auth, privilege escalation attempts)
+- Store secrets in environment variables or secret managers (never in source code)
 
 ### MUST NOT DO
-- Store passwords in plaintext
+- Store passwords in plaintext or reversibly encrypted form
 - Trust user input without validation
-- Expose sensitive data in logs or errors
-- Use weak encryption algorithms
-- Hardcode secrets in code
-- Disable security features for convenience
+- Expose sensitive data in logs or error responses
+- Use weak or deprecated algorithms (MD5, SHA-1, DES, ECB mode)
+- Hardcode secrets or credentials in code
+
+## Code Examples
+
+### Password Hashing (bcrypt)
+
+```typescript
+import bcrypt from 'bcrypt';
+
+const SALT_ROUNDS = 12; // minimum 10; 12 balances security and performance
+
+export async function hashPassword(plaintext: string): Promise<string> {
+  return bcrypt.hash(plaintext, SALT_ROUNDS);
+}
+
+export async function verifyPassword(plaintext: string, hash: string): Promise<boolean> {
+  return bcrypt.compare(plaintext, hash);
+}
+```
+
+### Parameterized SQL Query (Node.js / pg)
+
+```typescript
+// NEVER: `SELECT * FROM users WHERE email = '${email}'`
+// ALWAYS: use positional parameters
+import { Pool } from 'pg';
+const pool = new Pool();
+
+export async function getUserByEmail(email: string) {
+  const { rows } = await pool.query(
+    'SELECT id, email, role FROM users WHERE email = $1',
+    [email]  // value passed separately — never interpolated
+  );
+  return rows[0] ?? null;
+}
+```
+
+### Input Validation with Zod
+
+```typescript
+import { z } from 'zod';
+
+const LoginSchema = z.object({
+  email: z.string().email().max(254),
+  password: z.string().min(8).max(128),
+});
+
+export function validateLoginInput(raw: unknown) {
+  const result = LoginSchema.safeParse(raw);
+  if (!result.success) {
+    // Return generic error — never echo raw input back
+    throw new Error('Invalid credentials format');
+  }
+  return result.data;
+}
+```
+
+### JWT Validation
+
+```typescript
+import jwt from 'jsonwebtoken';
+
+const JWT_SECRET = process.env.JWT_SECRET!; // never hardcode
+
+export function verifyToken(token: string): jwt.JwtPayload {
+  // Throws if expired, tampered, or wrong algorithm
+  const payload = jwt.verify(token, JWT_SECRET, {
+    algorithms: ['HS256'],   // explicitly allowlist algorithm
+    issuer: 'your-app',
+    audience: 'your-app',
+  });
+  if (typeof payload === 'string') throw new Error('Invalid token payload');
+  return payload;
+}
+```
+
+### Securing an Endpoint — Full Flow
+
+```typescript
+import express from 'express';
+import rateLimit from 'express-rate-limit';
+import helmet from 'helmet';
+
+const app = express();
+app.use(helmet()); // sets CSP, HSTS, X-Frame-Options, etc.
+app.use(express.json({ limit: '10kb' })); // limit payload size
+
+const authLimiter = rateLimit({
+  windowMs: 15 * 60 * 1000, // 15 minutes
+  max: 10,                   // 10 attempts per window per IP
+  standardHeaders: true,
+  legacyHeaders: false,
+});
+
+app.post('/api/login', authLimiter, async (req, res) => {
+  // 1. Validate input
+  const { email, password } = validateLoginInput(req.body);
+
+  // 2. Authenticate — parameterized query, constant-time compare
+  const user = await getUserByEmail(email);
+  if (!user || !(await verifyPassword(password, user.passwordHash))) {
+    // Generic message — do not reveal whether email exists
+    return res.status(401).json({ error: 'Invalid credentials' });
+  }
+
+  // 3. Authorize — issue scoped, short-lived token
+  const token = jwt.sign(
+    { sub: user.id, role: user.role },
+    JWT_SECRET,
+    { algorithm: 'HS256', expiresIn: '15m', issuer: 'your-app', audience: 'your-app' }
+  );
+
+  // 4. Secure response — token in httpOnly cookie, not body
+  res.cookie('token', token, { httpOnly: true, secure: true, sameSite: 'strict' });
+  return res.json({ message: 'Authenticated' });
+});
+```
 
 ## Output Templates
 
diff --git a/skills/security-reviewer/SKILL.md b/skills/security-reviewer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: security-reviewer
-description: Use when conducting security audits, reviewing code for vulnerabilities, or analyzing infrastructure security. Invoke for SAST scans, penetration testing, DevSecOps practices, cloud security reviews.
+description: Identifies security vulnerabilities, generates structured audit reports with severity ratings, and provides actionable remediation guidance. Use when conducting security audits, reviewing code for vulnerabilities, or analyzing infrastructure security. Invoke for SAST scans, penetration testing, DevSecOps practices, cloud security reviews, dependency audits, secrets scanning, or compliance checks. Produces vulnerability reports, prioritized recommendations, and compliance checklists.
 license: MIT
 allowed-tools: Read, Grep, Glob, Bash
 metadata:
@@ -18,10 +18,6 @@ metadata:
 
 Security analyst specializing in code review, vulnerability identification, penetration testing, and infrastructure security.
 
-## Role Definition
-
-You are a senior security analyst with 10+ years of application security experience. You specialize in identifying vulnerabilities through code review, SAST tools, active penetration testing, and infrastructure hardening. You produce actionable reports with severity ratings and remediation guidance.
-
 ## When to Use This Skill
 
 - Code review and SAST scanning
@@ -33,11 +29,16 @@ You are a senior security analyst with 10+ years of application security experie
 
 ## Core Workflow
 
-1. **Scope** - Map attack surface and critical paths
-2. **Scan** - Run SAST, dependency, and secrets tools
-3. **Review** - Manual review of auth, input handling, crypto
-4. **Test and classify** - Validate findings, rate severity (Critical/High/Medium/Low)
-5. **Report** - Document findings with remediation guidance
+1. **Scope** — Map attack surface and critical paths. Confirm written authorization and rules of engagement before proceeding.
+2. **Scan** — Run SAST, dependency, and secrets tools. Example commands:
+   - `semgrep --config=auto .`
+   - `bandit -r ./src`
+   - `gitleaks detect --source=.`
+   - `npm audit --audit-level=moderate`
+   - `trivy fs .`
+3. **Review** — Manual review of auth, input handling, and crypto. Tools miss context — manual review is mandatory.
+4. **Test and classify** — **Verify written scope authorization before active testing.** Validate findings, rate severity (Critical/High/Medium/Low/Info) using CVSS. Confirm exploitability with proof-of-concept only; do not exceed it.
+5. **Report** — Confirm findings with stakeholder before finalizing. Document with location, impact, and remediation. Report critical findings immediately.
 
 ## Reference Guide
 
@@ -83,6 +84,20 @@ Load detailed guidance based on context:
 3. Detailed findings with location, impact, and remediation
 4. Prioritized recommendations
 
+### Example Finding Entry
+
+```
+ID: FIND-001
+Severity: High (CVSS 8.1)
+Title: SQL Injection in user search endpoint
+File: src/api/users.py, line 42
+Description: User-supplied input is concatenated directly into a SQL query without parameterization.
+Impact: An attacker can read, modify, or delete database contents.
+Remediation: Use parameterized queries or an ORM. Replace `cursor.execute(f"SELECT * FROM users WHERE name='{name}'")`
+             with `cursor.execute("SELECT * FROM users WHERE name=%s", (name,))`.
+References: CWE-89, OWASP A03:2021
+```
+
 ## Knowledge Reference
 
 OWASP Top 10, CWE, Semgrep, Bandit, ESLint Security, gosec, npm audit, gitleaks, trufflehog, CVSS scoring, nmap, Burp Suite, sqlmap, Trivy, Checkov, HashiCorp Vault, AWS Security Hub, CIS benchmarks, SOC2, ISO27001
diff --git a/skills/shopify-expert/SKILL.md b/skills/shopify-expert/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: shopify-expert
-description: Use when building Shopify themes, apps, custom storefronts, or e-commerce solutions. Invoke for Liquid templating, Storefront API, app development, checkout customization, Shopify Plus features.
+description: Builds and debugs Shopify themes (.liquid files, theme.json, sections), develops custom Shopify apps (shopify.app.toml, OAuth, webhooks), and implements Storefront API integrations for headless storefronts. Use when building or customizing Shopify themes, creating Hydrogen or custom React storefronts, developing Shopify apps, implementing checkout UI extensions or Shopify Functions, optimizing performance, or integrating third-party services. Invoke for Liquid templating, Storefront API, app development, checkout customization, Shopify Plus features, App Bridge, Polaris, or Shopify CLI workflows.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,27 +17,13 @@ metadata:
 
 Senior Shopify developer with expertise in theme development, headless commerce, app architecture, and custom checkout solutions.
 
-## Role Definition
-
-You are a senior Shopify developer with deep e-commerce experience. You specialize in Shopify theme development with Liquid, headless commerce with Storefront API, custom Shopify app development, and checkout extensibility. You build high-performing stores achieving sub-2s load times and conversion-optimized checkout flows.
-
-## When to Use This Skill
-
-- Building or customizing Shopify themes
-- Creating headless storefronts with Hydrogen or custom React
-- Developing Shopify apps with OAuth and webhooks
-- Implementing checkout UI extensions or Shopify Functions
-- Optimizing theme performance and conversion rates
-- Integrating third-party services with Shopify
-- Building Shopify Plus merchant solutions
-
 ## Core Workflow
 
-1. **Requirements analysis** - Identify if theme, app, or headless approach fits needs
-2. **Architecture setup** - Configure theme structure, app scaffolding, or API integration
-3. **Implementation** - Build Liquid templates, GraphQL queries, or app features
-4. **Optimization** - Performance tuning, asset optimization, checkout flow refinement
-5. **Deploy and test** - Theme deployment, app submission, production monitoring
+1. **Requirements analysis** — Identify if theme, app, or headless approach fits needs
+2. **Architecture setup** — Scaffold with `shopify theme init` or `shopify app create`; configure `shopify.app.toml` and theme schema
+3. **Implementation** — Build Liquid templates, write GraphQL queries, or develop app features (see examples below)
+4. **Validation** — Run `shopify theme check` for Liquid linting; if errors are found, fix them and re-run before proceeding. Run `shopify app dev` to verify app locally; test checkout extensions in sandbox. If validation fails at any step, resolve all reported issues before moving to deployment
+5. **Deploy and monitor** — `shopify theme push` for themes; `shopify app deploy` for apps; watch Shopify error logs and performance metrics post-deploy
 
 ## Reference Guide
 
@@ -51,6 +37,114 @@ Load detailed guidance based on context:
 | Checkout Extensions | `references/checkout-customization.md` | Checkout UI extensions, Shopify Functions |
 | Performance | `references/performance-optimization.md` | Theme speed, asset optimization, caching |
 
+## Code Examples
+
+### Liquid — Product template with metafield access
+```liquid
+{% comment %} templates/product.liquid {% endcomment %}
+<h1>{{ product.title }}</h1>
+<p>{{ product.metafields.custom.care_instructions.value }}</p>
+
+{% for variant in product.variants %}
+  <option
+    value="{{ variant.id }}"
+    {% unless variant.available %}disabled{% endunless %}
+  >
+    {{ variant.title }} — {{ variant.price | money }}
+  </option>
+{% endfor %}
+
+{{ product.description | metafield_tag }}
+```
+
+### Liquid — Collection filtering (Online Store 2.0)
+```liquid
+{% comment %} sections/collection-filters.liquid {% endcomment %}
+{% for filter in collection.filters %}
+  <details>
+    <summary>{{ filter.label }}</summary>
+    {% for value in filter.values %}
+      <label>
+        <input
+          type="checkbox"
+          name="{{ value.param_name }}"
+          value="{{ value.value }}"
+          {% if value.active %}checked{% endif %}
+        >
+        {{ value.label }} ({{ value.count }})
+      </label>
+    {% endfor %}
+  </details>
+{% endfor %}
+```
+
+### Storefront API — GraphQL product query
+```graphql
+query ProductByHandle($handle: String!) {
+  product(handle: $handle) {
+    id
+    title
+    descriptionHtml
+    featuredImage {
+      url(transform: { maxWidth: 800, preferredContentType: WEBP })
+      altText
+    }
+    variants(first: 10) {
+      edges {
+        node {
+          id
+          title
+          price { amount currencyCode }
+          availableForSale
+          selectedOptions { name value }
+        }
+      }
+    }
+    metafield(namespace: "custom", key: "care_instructions") {
+      value
+      type
+    }
+  }
+}
+```
+
+### Shopify CLI — Common commands
+```bash
+# Theme development
+shopify theme dev --store=your-store.myshopify.com   # Live preview with hot reload
+shopify theme check                                   # Lint Liquid for errors/warnings
+shopify theme push --only templates/ sections/        # Partial push
+shopify theme pull                                    # Sync remote changes locally
+
+# App development
+shopify app create node                               # Scaffold Node.js app
+shopify app dev                                       # Local dev with ngrok tunnel
+shopify app deploy                                    # Submit app version
+shopify app generate extension                        # Add checkout UI extension
+
+# GraphQL
+shopify app generate graphql                          # Generate typed GraphQL hooks
+```
+
+### App — Authenticated Admin API fetch (TypeScript)
+```typescript
+import { authenticate } from "../shopify.server";
+import type { LoaderFunctionArgs } from "@remix-run/node";
+
+export const loader = async ({ request }: LoaderFunctionArgs) => {
+  const { admin } = await authenticate.admin(request);
+
+  const response = await admin.graphql(`
+    query {
+      shop { name myshopifyDomain plan { displayName } }
+    }
+  `);
+
+  const { data } = await response.json();
+  return data.shop;
+};
+```
+
 ## Constraints
 
 ### MUST DO
@@ -64,6 +158,7 @@ Load detailed guidance based on context:
 - Follow Shopify theme architecture patterns
 - Use TypeScript for app development
 - Test checkout extensions in sandbox
+- Run `shopify theme check` before every theme deployment
 
 ### MUST NOT DO
 - Hardcode API credentials in theme code
diff --git a/skills/spark-engineer/SKILL.md b/skills/spark-engineer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: spark-engineer
-description: Use when building Apache Spark applications, distributed data processing pipelines, or optimizing big data workloads. Invoke for DataFrame API, Spark SQL, RDD operations, performance tuning, streaming analytics.
+description: Use when writing Spark jobs, debugging performance issues, or configuring cluster settings for Apache Spark applications, distributed data processing pipelines, or big data workloads. Invoke to write DataFrame transformations, optimize Spark SQL queries, implement RDD pipelines, tune shuffle operations, configure executor memory, process .parquet files, handle data partitioning, or build structured streaming analytics.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,27 +17,13 @@ metadata:
 
 Senior Apache Spark engineer specializing in high-performance distributed data processing, optimizing large-scale ETL pipelines, and building production-grade Spark applications.
 
-## Role Definition
-
-You are a senior Apache Spark engineer with deep big data experience. You specialize in building scalable data processing pipelines using DataFrame API, Spark SQL, and RDD operations. You optimize Spark applications for performance through partitioning strategies, caching, and cluster tuning. You build production-grade systems processing petabyte-scale data.
-
-## When to Use This Skill
-
-- Building distributed data processing pipelines with Spark
-- Optimizing Spark application performance and resource usage
-- Implementing complex transformations with DataFrame API and Spark SQL
-- Processing streaming data with Structured Streaming
-- Designing partitioning and caching strategies
-- Troubleshooting memory issues, shuffle operations, and skew
-- Migrating from RDD to DataFrame/Dataset APIs
-
 ## Core Workflow
 
 1. **Analyze requirements** - Understand data volume, transformations, latency requirements, cluster resources
 2. **Design pipeline** - Choose DataFrame vs RDD, plan partitioning strategy, identify broadcast opportunities
 3. **Implement** - Write Spark code with optimized transformations, appropriate caching, proper error handling
 4. **Optimize** - Analyze Spark UI, tune shuffle partitions, eliminate skew, optimize joins and aggregations
-5. **Validate** - Test with production-scale data, monitor resource usage, verify performance targets
+5. **Validate** - Check Spark UI for shuffle spill before proceeding; verify partition count with `df.rdd.getNumPartitions()`; if spill or skew detected, return to step 4; test with production-scale data, monitor resource usage, verify performance targets
 
 ## Reference Guide
 
@@ -51,6 +37,81 @@ Load detailed guidance based on context:
 | Performance Tuning | `references/performance-tuning.md` | Configuration, memory tuning, shuffle optimization, skew handling |
 | Streaming Patterns | `references/streaming-patterns.md` | Structured Streaming, watermarks, stateful operations, sinks |
 
+## Code Examples
+
+### Quick-Start Mini-Pipeline (PySpark)
+
+```python
+from pyspark.sql import SparkSession
+from pyspark.sql import functions as F
+from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType
+
+spark = SparkSession.builder \
+    .appName("example-pipeline") \
+    .config("spark.sql.shuffle.partitions", "400") \
+    .config("spark.sql.adaptive.enabled", "true") \
+    .getOrCreate()
+
+# Always define explicit schemas in production
+schema = StructType([
+    StructField("user_id", StringType(), False),
+    StructField("event_ts", LongType(), False),
+    StructField("amount", DoubleType(), True),
+])
+
+df = spark.read.schema(schema).parquet("s3://bucket/events/")
+
+result = df \
+    .filter(F.col("amount").isNotNull()) \
+    .groupBy("user_id") \
+    .agg(F.sum("amount").alias("total_amount"), F.count("*").alias("event_count"))
+
+# Verify partition count before writing
+print(f"Partition count: {result.rdd.getNumPartitions()}")
+
+result.write.mode("overwrite").parquet("s3://bucket/output/")
+```
+
+### Broadcast Join (small dimension table < 200 MB)
+
+```python
+from pyspark.sql.functions import broadcast
+
+# Spark will automatically broadcast dim_table; hint makes intent explicit
+enriched = large_fact_df.join(broadcast(dim_df), on="product_id", how="left")
+```
+
+### Handling Data Skew with Salting
+
+```python
+import pyspark.sql.functions as F
+
+SALT_BUCKETS = 50
+
+# Add salt to the skewed key on both sides
+skewed_df = skewed_df.withColumn("salt", (F.rand() * SALT_BUCKETS).cast("int")) \
+    .withColumn("salted_key", F.concat(F.col("skewed_key"), F.lit("_"), F.col("salt")))
+
+other_df = other_df.withColumn("salt", F.explode(F.array([F.lit(i) for i in range(SALT_BUCKETS)]))) \
+    .withColumn("salted_key", F.concat(F.col("skewed_key"), F.lit("_"), F.col("salt")))
+
+result = skewed_df.join(other_df, on="salted_key", how="inner") \
+    .drop("salt", "salted_key")
+```
+
+### Correct Caching Pattern
+
+```python
+# Cache ONLY when the DataFrame is reused multiple times
+df_cleaned = df.filter(...).withColumn(...).cache()
+df_cleaned.count()  # Materialize immediately; check Spark UI for spill
+
+report_a = df_cleaned.groupBy("region").agg(...)
+report_b = df_cleaned.groupBy("product").agg(...)
+
+df_cleaned.unpersist()  # Release when done
+```
+
 ## Constraints
 
 ### MUST DO
diff --git a/skills/spec-miner/SKILL.md b/skills/spec-miner/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: spec-miner
-description: Use when understanding legacy or undocumented systems, creating documentation for existing code, or extracting specifications from implementations. Invoke for legacy analysis, code archaeology, undocumented features.
+description: "Reverse-engineering specialist that extracts specifications from existing codebases. Use when working with legacy or undocumented systems, inherited projects, or old codebases with no documentation. Invoke to map code dependencies, generate API documentation from source, identify undocumented business logic, figure out what code does, or create architecture documentation from implementation. Trigger phrases: reverse engineer, old codebase, no docs, no documentation, figure out how this works, inherited project, legacy analysis, code archaeology, undocumented features."
 license: MIT
 allowed-tools: Read, Grep, Glob, Bash
 metadata:
@@ -20,7 +20,7 @@ Reverse-engineering specialist who extracts specifications from existing codebas
 
 ## Role Definition
 
-You are a senior software archaeologist with 10+ years of experience. You operate with two perspectives: **Arch Hat** for system architecture and data flows, and **QA Hat** for observable behaviors and edge cases.
+You operate with two perspectives: **Arch Hat** for system architecture and data flows, and **QA Hat** for observable behaviors and edge cases.
 
 ## When to Use This Skill
 
@@ -34,10 +34,40 @@ You are a senior software archaeologist with 10+ years of experience. You operat
 
 1. **Scope** - Identify analysis boundaries (full system or specific feature)
 2. **Explore** - Map structure using Glob, Grep, Read tools
+   - _Validation checkpoint:_ Confirm sufficient file coverage before proceeding. If key entry points, configuration files, or core modules remain unread, continue exploration before writing documentation.
 3. **Trace** - Follow data flows and request paths
 4. **Document** - Write observed requirements in EARS format
 5. **Flag** - Mark areas needing clarification
 
+### Example Exploration Patterns
+
+```
+# Find entry points and public interfaces
+Glob('**/*.py', exclude=['**/test*', '**/__pycache__/**'])
+
+# Locate technical debt markers
+Grep('TODO|FIXME|HACK|XXX', include='*.py')
+
+# Discover configuration and environment usage
+Grep('os\.environ|config\[|settings\.', include='*.py')
+
+# Map API route definitions (Flask/Django/Express examples)
+Grep('@app\.route|@router\.|router\.get|router\.post', include='*.py')
+```
+
+### EARS Format Quick Reference
+
+EARS (Easy Approach to Requirements Syntax) structures observed behavior as:
+
+| Type | Pattern | Example |
+|------|---------|---------|
+| Ubiquitous | The `<system>` shall `<action>`. | The API shall return JSON responses. |
+| Event-driven | When `<trigger>`, the `<system>` shall `<action>`. | When a request lacks an auth token, the system shall return HTTP 401. |
+| State-driven | While `<state>`, the `<system>` shall `<action>`. | While in maintenance mode, the system shall reject all write operations. |
+| Optional | Where `<feature>` is supported, the `<system>` shall `<action>`. | Where caching is enabled, the system shall store responses for 60 seconds. |
+
+> See `references/ears-format.md` for the complete EARS reference.
+
 ## Reference Guide
 
 Load detailed guidance based on context:
@@ -76,7 +106,3 @@ Include:
 5. Inferred acceptance criteria
 6. Uncertainties and questions
 7. Recommendations
-
-## Knowledge Reference
-
-Code archaeology, static analysis, design patterns, architectural patterns, EARS syntax, API documentation inference
diff --git a/skills/spring-boot-engineer/SKILL.md b/skills/spring-boot-engineer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: spring-boot-engineer
-description: Use when building Spring Boot 3.x applications, microservices, or reactive Java applications. Invoke for Spring Data JPA, Spring Security 6, WebFlux, Spring Cloud integration.
+description: Generates Spring Boot 3.x configurations, creates REST controllers, implements Spring Security 6 authentication flows, sets up Spring Data JPA repositories, and configures reactive WebFlux endpoints. Use when building Spring Boot 3.x applications, microservices, or reactive Java applications; invoke for Spring Data JPA, Spring Security 6, WebFlux, Spring Cloud integration, Java REST API design, or Microservices Java architecture.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,30 +15,14 @@ metadata:
 
 # Spring Boot Engineer
 
-Senior Spring Boot engineer with expertise in Spring Boot 3+, cloud-native Java development, and enterprise microservices architecture.
-
-## Role Definition
-
-You are a senior Spring Boot engineer with 10+ years of enterprise Java experience. You specialize in Spring Boot 3.x with Java 17+, reactive programming, Spring Cloud ecosystem, and building production-grade microservices. You focus on creating scalable, secure, and maintainable applications with comprehensive testing and observability.
-
-## When to Use This Skill
-
-- Building REST APIs with Spring Boot
-- Implementing reactive applications with WebFlux
-- Setting up Spring Data JPA repositories
-- Implementing Spring Security 6 authentication
-- Creating microservices with Spring Cloud
-- Optimizing Spring Boot performance
-- Writing comprehensive tests with Spring Boot Test
-
 ## Core Workflow
 
-1. **Analyze requirements** - Identify service boundaries, APIs, data models, security needs
-2. **Design architecture** - Plan microservices, data access, cloud integration, security
-3. **Implement** - Create services with proper dependency injection and layered architecture
-4. **Secure** - Add Spring Security, OAuth2, method security, CORS configuration
-5. **Test** - Write unit, integration, and slice tests with high coverage
-6. **Deploy** - Configure for cloud deployment with health checks and observability
+1. **Analyze requirements** — Identify service boundaries, APIs, data models, security needs
+2. **Design architecture** — Plan microservices, data access, cloud integration, security; confirm design before coding
+3. **Implement** — Create services with constructor injection and layered architecture (see Quick Start below)
+4. **Secure** — Add Spring Security, OAuth2, method security, CORS configuration; verify security rules compile and pass tests. If compilation or tests fail: review error output, fix the failing rule or configuration, and re-run before proceeding
+5. **Test** — Write unit, integration, and slice tests; run `./mvnw test` (or `./gradlew test`) and confirm all pass before proceeding. If tests fail: review the stack trace, isolate the failing assertion or component, fix the issue, and re-run the full suite
+6. **Deploy** — Configure health checks and observability via Actuator; validate `/actuator/health` returns `UP`. If health is `DOWN`: check the `components` detail in the response, resolve the failing component (e.g., datasource, broker), and re-validate
 
 ## Reference Guide
 
@@ -52,43 +36,160 @@ Load detailed guidance based on context:
 | Cloud Native | `references/cloud.md` | Spring Cloud, Config, Discovery, Gateway, resilience |
 | Testing | `references/testing.md` | @SpringBootTest, MockMvc, Testcontainers, test slices |
 
+## Quick Start — Minimal Working Structure
+
+A standard Spring Boot feature consists of these layers. Use these as copy-paste starting points.
+
+### Entity
+
+```java
+@Entity
+@Table(name = "products")
+public class Product {
+    @Id
+    @GeneratedValue(strategy = GenerationType.IDENTITY)
+    private Long id;
+
+    @NotBlank
+    private String name;
+
+    @DecimalMin("0.0")
+    private BigDecimal price;
+
+    // getters / setters or use @Data (Lombok)
+}
+```
+
+### Repository
+
+```java
+public interface ProductRepository extends JpaRepository<Product, Long> {
+    List<Product> findByNameContainingIgnoreCase(String name);
+}
+```
+
+### Service (constructor injection)
+
+```java
+@Service
+public class ProductService {
+    private final ProductRepository repo;
+
+    public ProductService(ProductRepository repo) { // constructor injection — no @Autowired
+        this.repo = repo;
+    }
+
+    @Transactional(readOnly = true)
+    public List<Product> search(String name) {
+        return repo.findByNameContainingIgnoreCase(name);
+    }
+
+    @Transactional
+    public Product create(ProductRequest request) {
+        var product = new Product();
+        product.setName(request.name());
+        product.setPrice(request.price());
+        return repo.save(product);
+    }
+}
+```
+
+### REST Controller
+
+```java
+@RestController
+@RequestMapping("/api/v1/products")
+@Validated
+public class ProductController {
+    private final ProductService service;
+
+    public ProductController(ProductService service) {
+        this.service = service;
+    }
+
+    @GetMapping
+    public List<Product> search(@RequestParam(defaultValue = "") String name) {
+        return service.search(name);
+    }
+
+    @PostMapping
+    @ResponseStatus(HttpStatus.CREATED)
+    public Product create(@Valid @RequestBody ProductRequest request) {
+        return service.create(request);
+    }
+}
+```
+
+### DTO (record)
+
+```java
+public record ProductRequest(
+    @NotBlank String name,
+    @DecimalMin("0.0") BigDecimal price
+) {}
+```
+
+### Global Exception Handler
+
+```java
+@RestControllerAdvice
+public class GlobalExceptionHandler {
+    @ExceptionHandler(MethodArgumentNotValidException.class)
+    @ResponseStatus(HttpStatus.BAD_REQUEST)
+    public Map<String, String> handleValidation(MethodArgumentNotValidException ex) {
+        return ex.getBindingResult().getFieldErrors().stream()
+            .collect(Collectors.toMap(FieldError::getField, FieldError::getDefaultMessage));
+    }
+
+    @ExceptionHandler(EntityNotFoundException.class)
+    @ResponseStatus(HttpStatus.NOT_FOUND)
+    public Map<String, String> handleNotFound(EntityNotFoundException ex) {
+        return Map.of("error", ex.getMessage());
+    }
+}
+```
+
+### Test Slice
+
+```java
+@WebMvcTest(ProductController.class)
+class ProductControllerTest {
+    @Autowired MockMvc mockMvc;
+    @MockBean ProductService service;
+
+    @Test
+    void createProduct_validRequest_returns201() throws Exception {
+        var product = new Product(); product.setName("Widget"); product.setPrice(BigDecimal.TEN);
+        when(service.create(any())).thenReturn(product);
+
+        mockMvc.perform(post("/api/v1/products")
+                .contentType(MediaType.APPLICATION_JSON)
+                .content("""{"name":"Widget","price":10.0}"""))
+            .andExpect(status().isCreated())
+            .andExpect(jsonPath("$.name").value("Widget"));
+    }
+}
+```
+
 ## Constraints
 
 ### MUST DO
-- Use Spring Boot 3.x with Java 17+ features
-- Apply dependency injection via constructor injection
-- Use @RestController for REST APIs with proper HTTP methods
-- Implement validation with @Valid and constraint annotations
-- Use Spring Data repositories for data access
-- Apply @Transactional appropriately for transaction management
-- Write tests with @SpringBootTest and test slices
-- Configure application.yml/properties properly
-- Use @ConfigurationProperties for type-safe configuration
-- Implement proper exception handling with @ControllerAdvice
+
+| Rule | Correct Pattern |
+|------|----------------|
+| Constructor injection | `public MyService(Dep dep) { this.dep = dep; }` |
+| Validate API input | `@Valid @RequestBody MyRequest req` on every mutating endpoint |
+| Type-safe config | `@ConfigurationProperties(prefix = "app")` bound to a record/class |
+| Appropriate stereotype | `@Service` for business logic, `@Repository` for data, `@RestController` for HTTP |
+| Transaction scope | `@Transactional` on multi-step writes; `@Transactional(readOnly = true)` on reads |
+| Hide internals | Catch domain exceptions in `@RestControllerAdvice`; return problem details, not stack traces |
+| Externalize secrets | Use environment variables or Spring Cloud Config — never `application.properties` |
 
 ### MUST NOT DO
-- Use field injection (@Autowired on fields)
+- Use field injection (`@Autowired` on fields)
 - Skip input validation on API endpoints
-- Expose internal exceptions to API clients
-- Use @Component when @Service/@Repository/@Controller applies
-- Mix blocking and reactive code improperly
-- Store secrets in application.properties
-- Skip transaction management for multi-step operations
-- Use deprecated Spring Boot 2.x patterns
-- Hardcode URLs, credentials, or configuration
-
-## Output Templates
-
-When implementing Spring Boot features, provide:
-1. Entity/model classes with JPA annotations
-2. Repository interfaces extending Spring Data
-3. Service layer with business logic
-4. Controller with REST endpoints
-5. DTO classes for API requests/responses
-6. Configuration classes if needed
-7. Test classes with appropriate test slices
-8. Brief explanation of architecture decisions
-
-## Knowledge Reference
-
-Spring Boot 3.x, Spring Framework 6, Spring Data JPA, Spring Security 6, Spring Cloud, Project Reactor (WebFlux), JPA/Hibernate, Bean Validation, RestTemplate/WebClient, Actuator, Micrometer, JUnit 5, Mockito, Testcontainers, Docker, Kubernetes
+- Use `@Component` when `@Service`/`@Repository`/`@Controller` applies
+- Mix blocking and reactive code (e.g., calling `.block()` inside a WebFlux chain)
+- Store secrets or credentials in `application.properties`/`application.yml`
+- Hardcode URLs, credentials, or environment-specific values
+- Use deprecated Spring Boot 2.x patterns (e.g., `WebSecurityConfigurerAdapter`)
diff --git a/skills/sql-pro/SKILL.md b/skills/sql-pro/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: sql-pro
-description: Use when optimizing SQL queries, designing database schemas, or tuning database performance. Invoke for complex queries, window functions, CTEs, indexing strategies, query plan analysis.
+description: Optimizes SQL queries, designs database schemas, and troubleshoots performance issues. Use when a user asks why their query is slow, needs help writing complex joins or aggregations, mentions database performance issues, or wants to design or migrate a schema. Invoke for complex queries, window functions, CTEs, indexing strategies, query plan analysis, covering index creation, recursive queries, EXPLAIN/ANALYZE interpretation, before/after query benchmarking, or migrating queries between database dialects (PostgreSQL, MySQL, SQL Server, Oracle).
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,27 +15,12 @@ metadata:
 
 # SQL Pro
 
-Senior SQL developer with mastery across major database systems, specializing in complex query design, performance optimization, and database architecture.
-
-## Role Definition
-
-You are a senior SQL developer with 10+ years of experience across PostgreSQL, MySQL, SQL Server, and Oracle. You specialize in complex query optimization, advanced SQL patterns (CTEs, window functions, recursive queries), indexing strategies, and performance tuning. You build efficient, scalable database solutions with sub-100ms query targets.
-
-## When to Use This Skill
-
-- Optimizing slow queries and execution plans
-- Designing complex queries with CTEs, window functions, recursive patterns
-- Creating and optimizing database indexes
-- Implementing data warehousing and ETL patterns
-- Migrating queries between database platforms
-- Analyzing and tuning database performance
-
 ## Core Workflow
 
 1. **Schema Analysis** - Review database structure, indexes, query patterns, performance bottlenecks
 2. **Design** - Create set-based operations using CTEs, window functions, appropriate joins
 3. **Optimize** - Analyze execution plans, implement covering indexes, eliminate table scans
-4. **Verify** - Test with production data volume, ensure linear scalability, confirm sub-100ms targets
+4. **Verify** - Run `EXPLAIN ANALYZE` and confirm no sequential scans on large tables; if query does not meet sub-100ms target, iterate on index selection or query rewrite before proceeding
 5. **Document** - Provide query explanations, index rationale, performance metrics
 
 ## Reference Guide
@@ -50,27 +35,89 @@ Load detailed guidance based on context:
 | Database Design | `references/database-design.md` | Normalization, keys, constraints, schemas |
 | Dialect Differences | `references/dialect-differences.md` | PostgreSQL vs MySQL vs SQL Server specifics |
 
+## Quick-Reference Examples
+
+### CTE Pattern
+```sql
+-- Isolate expensive subquery logic for reuse and readability
+WITH ranked_orders AS (
+    SELECT
+        customer_id,
+        order_id,
+        total_amount,
+        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
+    FROM orders
+    WHERE status = 'completed'          -- filter early, before the join
+)
+SELECT customer_id, order_id, total_amount
+FROM ranked_orders
+WHERE rn = 1;                           -- latest completed order per customer
+```
+
+### Window Function Pattern
+```sql
+-- Running total and rank within partition — no self-join required
+SELECT
+    department_id,
+    employee_id,
+    salary,
+    SUM(salary)  OVER (PARTITION BY department_id ORDER BY hire_date) AS running_payroll,
+    RANK()       OVER (PARTITION BY department_id ORDER BY salary DESC) AS salary_rank
+FROM employees;
+```
+
+### EXPLAIN ANALYZE Interpretation
+```sql
+-- PostgreSQL: always use ANALYZE to see actual row counts vs. estimates
+EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
+SELECT *
+FROM orders o
+JOIN customers c ON c.id = o.customer_id
+WHERE o.created_at > NOW() - INTERVAL '30 days';
+```
+Key things to check in the output:
+- **Seq Scan on large table** → add or fix an index
+- **actual rows ≫ estimated rows** → run `ANALYZE <table>` to refresh statistics
+- **Buffers: shared hit** vs **read** → high `read` count signals missing cache / index
+
+### Before / After Optimization Example
+```sql
+-- BEFORE: correlated subquery, one execution per row (slow)
+SELECT order_id,
+       (SELECT SUM(quantity) FROM order_items oi WHERE oi.order_id = o.id) AS item_count
+FROM orders o;
+
+-- AFTER: single aggregation join (fast)
+SELECT o.order_id, COALESCE(agg.item_count, 0) AS item_count
+FROM orders o
+LEFT JOIN (
+    SELECT order_id, SUM(quantity) AS item_count
+    FROM order_items
+    GROUP BY order_id
+) agg ON agg.order_id = o.id;
+
+-- Supporting covering index (includes all columns touched by the query)
+CREATE INDEX idx_order_items_order_qty
+    ON order_items (order_id)
+    INCLUDE (quantity);
+```
+
 ## Constraints
 
 ### MUST DO
-- Analyze execution plans before optimization
+- Analyze execution plans before recommending optimizations
 - Use set-based operations over row-by-row processing
-- Apply filtering early in query execution
+- Apply filtering early in query execution (before joins where possible)
 - Use EXISTS over COUNT for existence checks
-- Handle NULLs explicitly
+- Handle NULLs explicitly in comparisons and aggregations
 - Create covering indexes for frequent queries
 - Test with production-scale data volumes
-- Document query intent and performance targets
 
 ### MUST NOT DO
 - Use SELECT * in production queries
-- Create queries without analyzing execution plans
-- Ignore index usage and table scans
 - Use cursors when set-based operations work
-- Skip NULL handling in comparisons
-- Implement solutions without considering data volume
-- Ignore platform-specific optimizations
-- Leave queries undocumented
+- Ignore platform-specific optimizations when targeting a specific dialect
+- Implement solutions without considering data volume and cardinality
 
 ## Output Templates
 
@@ -80,7 +127,3 @@ When implementing SQL solutions, provide:
 3. Execution plan analysis
 4. Performance metrics (before/after)
 5. Platform-specific notes if applicable
-
-## Knowledge Reference
-
-CTEs, window functions, recursive queries, EXPLAIN/ANALYZE, covering indexes, query hints, partitioning, materialized views, OLAP patterns, star schema, slowly changing dimensions, isolation levels, deadlock prevention, temporal tables, JSONB operations
diff --git a/skills/sre-engineer/SKILL.md b/skills/sre-engineer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: sre-engineer
-description: Use when defining SLIs/SLOs, managing error budgets, or building reliable systems at scale. Invoke for incident management, chaos engineering, toil reduction, capacity planning.
+description: Defines service level objectives, creates error budget policies, designs incident response procedures, develops capacity models, and produces monitoring configurations and automation scripts for production systems. Use when defining SLIs/SLOs, managing error budgets, building reliable systems at scale, incident management, chaos engineering, toil reduction, or capacity planning.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,29 +15,14 @@ metadata:
 
 # SRE Engineer
 
-Senior Site Reliability Engineer with expertise in building highly reliable, scalable systems through SLI/SLO management, error budgets, capacity planning, and automation.
-
-## Role Definition
-
-You are a senior SRE with 10+ years of experience building and maintaining production systems at scale. You specialize in defining meaningful SLOs, managing error budgets, reducing toil through automation, and building resilient systems. Your focus is on sustainable reliability that enables feature velocity.
-
-## When to Use This Skill
-
-- Defining SLIs/SLOs and error budgets
-- Implementing reliability monitoring and alerting
-- Reducing operational toil through automation
-- Designing chaos engineering experiments
-- Managing incidents and postmortems
-- Building capacity planning models
-- Establishing on-call practices
-
 ## Core Workflow
 
 1. **Assess reliability** - Review architecture, SLOs, incidents, toil levels
 2. **Define SLOs** - Identify meaningful SLIs and set appropriate targets
-3. **Implement monitoring** - Build golden signal dashboards and alerting
-4. **Automate toil** - Identify repetitive tasks and build automation
-5. **Test resilience** - Design and execute chaos experiments
+3. **Verify alignment** - Confirm SLO targets reflect user expectations before proceeding
+4. **Implement monitoring** - Build golden signal dashboards and alerting
+5. **Automate toil** - Identify repetitive tasks and build automation
+6. **Test resilience** - Design and execute chaos experiments; verify recovery meets RTO/RPO targets before marking the experiment complete; validate recovery behavior end-to-end
 
 ## Reference Guide
 
@@ -82,6 +67,115 @@ When implementing SRE practices, provide:
 4. Runbooks with clear remediation steps
 5. Brief explanation of reliability impact
 
-## Knowledge Reference
-
-SLO/SLI design, error budgets, golden signals (latency/traffic/errors/saturation), Prometheus/Grafana, chaos engineering (Chaos Monkey, Gremlin), toil reduction, incident management, blameless postmortems, capacity planning, on-call best practices
+## Concrete Examples
+
+### SLO Definition & Error Budget Calculation
+
+```
+# 99.9% availability SLO over a 30-day window
+# Allowed downtime: (1 - 0.999) * 30 * 24 * 60 = 43.2 minutes/month
+# Error budget (request-based): 0.001 * total_requests
+
+# Example: 10M requests/month → 10,000 error budget requests
+# If 5,000 errors consumed in week 1 → 50% budget burned in 25% of window
+# → Trigger error budget policy: freeze non-critical releases
+```
+
+### Prometheus SLO Alerting Rule (Multiwindow Burn Rate)
+
+```yaml
+groups:
+  - name: slo_availability
+    rules:
+      # Fast burn: 2% budget in 1h (14.4x burn rate)
+      - alert: HighErrorBudgetBurn
+        expr: |
+          (
+            sum(rate(http_requests_total{status=~"5.."}[1h]))
+            /
+            sum(rate(http_requests_total[1h]))
+          ) > 0.014400
+          and
+          (
+            sum(rate(http_requests_total{status=~"5.."}[5m]))
+            /
+            sum(rate(http_requests_total[5m]))
+          ) > 0.014400
+        for: 2m
+        labels:
+          severity: critical
+        annotations:
+          summary: "High error budget burn rate detected"
+          runbook: "https://wiki.internal/runbooks/high-error-burn"
+
+      # Slow burn: 5% budget in 6h (1x burn rate sustained)
+      - alert: SlowErrorBudgetBurn
+        expr: |
+          (
+            sum(rate(http_requests_total{status=~"5.."}[6h]))
+            /
+            sum(rate(http_requests_total[6h]))
+          ) > 0.001
+        for: 15m
+        labels:
+          severity: warning
+        annotations:
+          summary: "Sustained error budget consumption"
+          runbook: "https://wiki.internal/runbooks/slow-error-burn"
+```
+
+### PromQL Golden Signal Queries
+
+```promql
+# Latency — 99th percentile request duration
+histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
+
+# Traffic — requests per second by service
+sum(rate(http_requests_total[5m])) by (service)
+
+# Errors — error rate ratio
+sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
+  /
+sum(rate(http_requests_total[5m])) by (service)
+
+# Saturation — CPU throttling ratio
+sum(rate(container_cpu_cfs_throttled_seconds_total[5m])) by (pod)
+  /
+sum(rate(container_cpu_cfs_periods_total[5m])) by (pod)
+```
+
+### Toil Automation Script (Python)
+
+```python
+#!/usr/bin/env python3
+"""Auto-remediation: restart pods exceeding error threshold."""
+import subprocess, sys, json
+
+ERROR_THRESHOLD = 0.05  # 5% error rate triggers restart
+
+def get_error_rate(service: str) -> float:
+    """Query Prometheus for current error rate."""
+    import urllib.request
+    query = f'sum(rate(http_requests_total{{status=~"5..",service="{service}"}}[5m])) / sum(rate(http_requests_total{{service="{service}"}}[5m]))'
+    url = f"http://prometheus:9090/api/v1/query?query={urllib.request.quote(query)}"
+    with urllib.request.urlopen(url) as resp:
+        data = json.load(resp)
+    results = data["data"]["result"]
+    return float(results[0]["value"][1]) if results else 0.0
+
+def restart_deployment(namespace: str, deployment: str) -> None:
+    subprocess.run(
+        ["kubectl", "rollout", "restart", f"deployment/{deployment}", "-n", namespace],
+        check=True
+    )
+    print(f"Restarted {namespace}/{deployment}")
+
+if __name__ == "__main__":
+    service, namespace, deployment = sys.argv[1], sys.argv[2], sys.argv[3]
+    rate = get_error_rate(service)
+    print(f"Error rate for {service}: {rate:.2%}")
+    if rate > ERROR_THRESHOLD:
+        restart_deployment(namespace, deployment)
+    else:
+        print("Within SLO threshold — no action required")
+```
diff --git a/skills/swift-expert/SKILL.md b/skills/swift-expert/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: swift-expert
-description: Use when building iOS/macOS applications with Swift 5.9+, SwiftUI, or async/await concurrency. Invoke for protocol-oriented programming, SwiftUI state management, actors, server-side Swift.
+description: Builds iOS/macOS/watchOS/tvOS applications, implements SwiftUI views and state management, designs protocol-oriented architectures, handles async/await concurrency, implements actors for thread safety, and debugs Swift-specific issues. Use when building iOS/macOS applications with Swift 5.9+, SwiftUI, or async/await concurrency. Invoke for protocol-oriented programming, SwiftUI state management, actors, server-side Swift, UIKit integration, Combine, or Vapor.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,21 +15,6 @@ metadata:
 
 # Swift Expert
 
-Senior Swift developer with mastery of Swift 5.9+, Apple's development ecosystem, SwiftUI, async/await concurrency, and protocol-oriented programming.
-
-## Role Definition
-
-You are a senior Swift engineer with 10+ years of Apple platform development. You specialize in Swift 5.9+, SwiftUI, async/await concurrency, protocol-oriented design, and server-side Swift. You build type-safe, performant applications following Apple's API design guidelines.
-
-## When to Use This Skill
-
-- Building iOS/macOS/watchOS/tvOS applications
-- Implementing SwiftUI interfaces and state management
-- Setting up async/await concurrency and actors
-- Creating protocol-oriented architectures
-- Optimizing memory and performance
-- Integrating UIKit with SwiftUI
-
 ## Core Workflow
 
 1. **Architecture Analysis** - Identify platform targets, dependencies, design patterns
@@ -38,6 +23,8 @@ You are a senior Swift engineer with 10+ years of Apple platform development. Yo
 4. **Optimize** - Profile with Instruments, ensure thread safety
 5. **Test** - Write comprehensive tests with XCTest and async patterns
 
+> **Validation checkpoints:** After step 3, run `swift build` to verify compilation. After step 4, run `swift build -warnings-as-errors` to surface actor isolation and Sendable warnings. After step 5, run `swift test` and confirm all async tests pass.
+
 ## Reference Guide
 
 Load detailed guidance based on context:
@@ -50,20 +37,114 @@ Load detailed guidance based on context:
 | Memory | `references/memory-performance.md` | ARC, weak/unowned, performance optimization |
 | Testing | `references/testing-patterns.md` | XCTest, async tests, mocking strategies |
 
+## Code Patterns
+
+### async/await — Correct vs. Incorrect
+
+```swift
+// ✅ DO: async/await with structured error handling
+func fetchUser(id: String) async throws -> User {
+    let url = URL(string: "https://api.example.com/users/\(id)")!
+    let (data, _) = try await URLSession.shared.data(from: url)
+    return try JSONDecoder().decode(User.self, from: data)
+}
+
+// ❌ DON'T: mixing completion handlers with async context
+func fetchUser(id: String) async throws -> User {
+    return try await withCheckedThrowingContinuation { continuation in
+        // Avoid wrapping existing async APIs this way when a native async version exists
+        legacyFetch(id: id) { result in
+            continuation.resume(with: result)
+        }
+    }
+}
+```
+
+### SwiftUI State Management
+
+```swift
+// ✅ DO: use @Observable (Swift 5.9+) for view models
+@Observable
+final class CounterViewModel {
+    var count = 0
+    func increment() { count += 1 }
+}
+
+struct CounterView: View {
+    @State private var vm = CounterViewModel()
+
+    var body: some View {
+        VStack {
+            Text("\(vm.count)")
+            Button("Increment", action: vm.increment)
+        }
+    }
+}
+
+// ❌ DON'T: reach for ObservableObject/Published when @Observable suffices
+class LegacyViewModel: ObservableObject {
+    @Published var count = 0  // Unnecessary boilerplate in Swift 5.9+
+}
+```
+
+### Protocol-Oriented Architecture
+
+```swift
+// ✅ DO: define capability protocols with associated types
+protocol Repository<Entity> {
+    associatedtype Entity: Identifiable
+    func fetch(id: Entity.ID) async throws -> Entity
+    func save(_ entity: Entity) async throws
+}
+
+struct UserRepository: Repository {
+    typealias Entity = User
+    func fetch(id: UUID) async throws -> User { /* … */ }
+    func save(_ user: User) async throws { /* … */ }
+}
+
+// ❌ DON'T: use classes as base types when a protocol fits
+class BaseRepository {  // Avoid class inheritance for shared behavior
+    func fetch(id: UUID) async throws -> Any { fatalError("Override required") }
+}
+```
+
+### Actor for Thread Safety
+
+```swift
+// ✅ DO: isolate mutable shared state in an actor
+actor ImageCache {
+    private var cache: [URL: UIImage] = [:]
+
+    func image(for url: URL) -> UIImage? { cache[url] }
+    func store(_ image: UIImage, for url: URL) { cache[url] = image }
+}
+
+// ❌ DON'T: use a class with manual locking
+class UnsafeImageCache {
+    private var cache: [URL: UIImage] = [:]
+    private let lock = NSLock()  // Error-prone; prefer actor isolation
+    func image(for url: URL) -> UIImage? {
+        lock.lock(); defer { lock.unlock() }
+        return cache[url]
+    }
+}
+```
+
 ## Constraints
 
 ### MUST DO
 - Use type hints and inference appropriately
 - Follow Swift API Design Guidelines
-- Use async/await for asynchronous operations
-- Ensure Sendable compliance for concurrency
-- Use value types (struct/enum) by default
-- Document APIs with markup comments
+- Use `async/await` for asynchronous operations (see pattern above)
+- Ensure `Sendable` compliance for concurrency
+- Use value types (`struct`/`enum`) by default
+- Document APIs with markup comments (`/// …`)
 - Use property wrappers for cross-cutting concerns
 - Profile with Instruments before optimizing
 
 ### MUST NOT DO
-- Use force unwrapping (!) without justification
+- Use force unwrapping (`!`) without justification
 - Create retain cycles in closures
 - Mix synchronous and asynchronous code improperly
 - Ignore actor isolation warnings
@@ -80,7 +161,3 @@ When implementing Swift features, provide:
 3. View implementations (SwiftUI) or view controllers
 4. Tests demonstrating usage
 5. Brief explanation of architectural decisions
-
-## Knowledge Reference
-
-Swift 5.9+, SwiftUI, UIKit, async/await, actors, structured concurrency, Combine, property wrappers, result builders, protocol-oriented programming, generics, type erasure, ARC, Instruments, XCTest, Swift Package Manager, Vapor
diff --git a/skills/terraform-engineer/SKILL.md b/skills/terraform-engineer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: terraform-engineer
-description: Use when implementing infrastructure as code with Terraform across AWS, Azure, or GCP. Invoke for module development, state management, provider configuration, multi-environment workflows, infrastructure testing.
+description: Use when implementing infrastructure as code with Terraform across AWS, Azure, or GCP. Invoke for module development (create reusable modules, manage module versioning), state management (migrate backends, import existing resources, resolve state conflicts), provider configuration, multi-environment workflows, and infrastructure testing.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,25 @@ metadata:
 
 Senior Terraform engineer specializing in infrastructure as code across AWS, Azure, and GCP with expertise in modular design, state management, and production-grade patterns.
 
-## Role Definition
+## Core Workflow
 
-You are a senior DevOps engineer with 10+ years of infrastructure automation experience. You specialize in Terraform 1.5+ with multi-cloud providers, focusing on reusable modules, secure state management, and enterprise compliance. You build scalable, maintainable infrastructure code.
+1. **Analyze infrastructure** — Review requirements, existing code, cloud platforms
+2. **Design modules** — Create composable, validated modules with clear interfaces
+3. **Implement state** — Configure remote backends with locking and encryption
+4. **Secure infrastructure** — Apply security policies, least privilege, encryption
+5. **Validate** — Run `terraform fmt` and `terraform validate`, then `tflint`; if any errors are reported, fix them and re-run until all checks pass cleanly before proceeding
+6. **Plan and apply** — Run `terraform plan -out=tfplan`, review output carefully, then `terraform apply tfplan`; if the plan fails, see error recovery below
 
-## When to Use This Skill
+### Error Recovery
 
-- Building Terraform modules for reusability
-- Implementing remote state with locking
-- Configuring AWS, Azure, or GCP providers
-- Setting up multi-environment workflows
-- Implementing infrastructure testing
-- Migrating to Terraform or refactoring IaC
+**Validation failures (step 5):** Fix reported errors → re-run `terraform validate` → repeat until clean. For `tflint` warnings, address rule violations before proceeding.
 
-## Core Workflow
+**Plan failures (step 6):**
+- *State drift* — Run `terraform refresh` to reconcile state with real resources, or use `terraform state rm` / `terraform import` to realign specific resources, then re-plan.
+- *Provider auth errors* — Verify credentials, environment variables, and provider configuration blocks; re-run `terraform init` if provider plugins are stale, then re-plan.
+- *Dependency / ordering errors* — Add explicit `depends_on` references or restructure module outputs to resolve unknown values, then re-plan.
 
-1. **Analyze infrastructure** - Review requirements, existing code, cloud platforms
-2. **Design modules** - Create composable, validated modules with clear interfaces
-3. **Implement state** - Configure remote backends with locking and encryption
-4. **Secure infrastructure** - Apply security policies, least privilege, encryption
-5. **Test and validate** - Run terraform plan, policy checks, automated tests
+After any fix, return to step 5 to re-validate before re-running the plan.
 
 ## Reference Guide
 
@@ -53,34 +52,92 @@ Load detailed guidance based on context:
 ## Constraints
 
 ### MUST DO
-- Use semantic versioning for modules
-- Enable remote state with locking
+- Use semantic versioning and pin provider versions
+- Enable remote state with locking and encryption
 - Validate inputs with validation blocks
-- Use consistent naming conventions
-- Tag all resources for cost tracking
+- Use consistent naming conventions and tag all resources
 - Document module interfaces
-- Pin provider versions
-- Run terraform fmt and validate
+- Run `terraform fmt` and `terraform validate`
 
 ### MUST NOT DO
-- Store secrets in plain text
-- Use local state for production
-- Skip state locking
-- Hardcode environment-specific values
+- Store secrets in plain text or hardcode environment-specific values
+- Use local state for production or skip state locking
 - Mix provider versions without constraints
-- Create circular module dependencies
-- Skip input validation
-- Commit .terraform directories
-
-## Output Templates
-
-When implementing Terraform solutions, provide:
-1. Module structure (main.tf, variables.tf, outputs.tf)
-2. Backend configuration for state
-3. Provider configuration with versions
-4. Example usage with tfvars
-5. Brief explanation of design decisions
-
-## Knowledge Reference
-
-Terraform 1.5+, HCL syntax, AWS/Azure/GCP providers, remote backends (S3, Azure Blob, GCS), state locking (DynamoDB, Azure Blob leases), workspaces, modules, dynamic blocks, for_each/count, terraform plan/apply, terratest, tflint, Open Policy Agent, cost estimation
+- Create circular module dependencies or skip input validation
+- Commit `.terraform` directories
+
+## Code Examples
+
+### Minimal Module Structure
+
+**`main.tf`**
+```hcl
+resource "aws_s3_bucket" "this" {
+  bucket = var.bucket_name
+  tags   = var.tags
+}
+```
+
+**`variables.tf`**
+```hcl
+variable "bucket_name" {
+  description = "Name of the S3 bucket"
+  type        = string
+
+  validation {
+    condition     = length(var.bucket_name) > 3
+    error_message = "bucket_name must be longer than 3 characters."
+  }
+}
+
+variable "tags" {
+  description = "Tags to apply to all resources"
+  type        = map(string)
+  default     = {}
+}
+```
+
+**`outputs.tf`**
+```hcl
+output "bucket_id" {
+  description = "ID of the created S3 bucket"
+  value       = aws_s3_bucket.this.id
+}
+```
+
+### Remote Backend Configuration (S3 + DynamoDB)
+
+```hcl
+terraform {
+  backend "s3" {
+    bucket         = "my-tf-state"
+    key            = "env/prod/terraform.tfstate"
+    region         = "us-east-1"
+    encrypt        = true
+    dynamodb_table = "terraform-lock"
+  }
+}
+```
+
+### Provider Version Pinning
+
+```hcl
+terraform {
+  required_version = ">= 1.5.0"
+
+  required_providers {
+    aws = {
+      source  = "hashicorp/aws"
+      version = "~> 5.0"
+    }
+    azurerm = {
+      source  = "hashicorp/azurerm"
+      version = "~> 3.0"
+    }
+  }
+}
+```
+
+## Output Format
+
+When implementing Terraform solutions, provide: module structure (`main.tf`, `variables.tf`, `outputs.tf`), backend and provider configuration, example usage with tfvars, and a brief explanation of design decisions.
diff --git a/skills/test-master/SKILL.md b/skills/test-master/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: test-master
-description: Use when writing tests, creating test strategies, or building automation frameworks. Invoke for unit tests, integration tests, E2E, coverage analysis, performance testing, security testing.
+description: Generates test files, creates mocking strategies, analyzes code coverage, designs test architectures, and produces test plans and defect reports across functional, performance, and security testing disciplines. Use when writing unit tests, integration tests, or E2E tests; creating test strategies or automation frameworks; analyzing coverage gaps; performance testing with k6 or Artillery; security testing with OWASP methods; debugging flaky tests; or working on QA, regression, test automation, quality gates, shift-left testing, or test maintenance.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,30 +17,37 @@ metadata:
 
 Comprehensive testing specialist ensuring software quality through functional, performance, and security testing.
 
-## Role Definition
+## Core Workflow
 
-You are a senior QA engineer with 12+ years of testing experience. You think in three testing modes: **[Test]** for functional correctness, **[Perf]** for performance, **[Security]** for vulnerability testing. You ensure features work correctly, perform well, and are secure.
+1. **Define scope** — Identify what to test and which testing types apply
+2. **Create strategy** — Plan the test approach across functional, performance, and security perspectives
+3. **Write tests** — Implement tests with proper assertions (see example below)
+4. **Execute** — Run tests and collect results
+   - If tests fail: classify the failure (assertion error vs. environment/flakiness), fix root cause, re-run
+   - If tests are flaky: isolate ordering dependencies, check async handling, add retry or stabilization logic
+5. **Report** — Document findings with severity ratings and actionable fix recommendations
+   - Verify coverage targets are met before closing; flag gaps explicitly
 
-## When to Use This Skill
+## Quick-Start Example
 
-- Writing unit, integration, or E2E tests
-- Creating test strategies and plans
-- Analyzing test coverage and quality metrics
-- Building test automation frameworks
-- Performance testing and benchmarking
-- Security testing for vulnerabilities
-- Managing defects and test reporting
-- Debugging test failures
-- Manual testing (exploratory, usability, accessibility)
-- Scaling test automation and CI/CD integration
+A minimal Jest unit test illustrating the key patterns this skill enforces:
 
-## Core Workflow
+```js
+// ✅ Good: meaningful description, specific assertion, isolated dependency
+describe('calculateDiscount', () => {
+  it('applies 10% discount for premium users', () => {
+    const result = calculateDiscount({ price: 100, userTier: 'premium' });
+    expect(result).toBe(90); // specific outcome, not just truthy
+  });
+
+  it('throws on negative price', () => {
+    expect(() => calculateDiscount({ price: -1, userTier: 'standard' }))
+      .toThrow('Price must be non-negative');
+  });
+});
+```
 
-1. **Define scope** - Identify what to test and testing types needed
-2. **Create strategy** - Plan test approach using all three perspectives
-3. **Write tests** - Implement tests with proper assertions
-4. **Execute** - Run tests and collect results
-5. **Report** - Document findings with actionable recommendations
+Apply the same structure for pytest (`def test_…`, `assert result == expected`) and other frameworks.
 
 ## Reference Guide
 
@@ -63,9 +70,19 @@ Load detailed guidance based on context:
 
 ## Constraints
 
-**MUST DO**: Test happy paths AND error cases, mock external dependencies, use meaningful descriptions, assert specific outcomes, test edge cases, run in CI/CD, document coverage gaps
+**MUST DO**
+- Test happy paths AND error/edge cases (e.g., empty input, null, boundary values)
+- Mock external dependencies — never call real APIs or databases in unit tests
+- Use meaningful `it('…')` descriptions that read as plain-English specifications
+- Assert specific outcomes (`expect(result).toBe(90)`), not just truthiness
+- Run tests in CI/CD; document and remediate coverage gaps
 
-**MUST NOT**: Skip error testing, use production data, create order-dependent tests, ignore flaky tests, test implementation details, leave debug code
+**MUST NOT**
+- Skip error-path testing (e.g., don't test only the success branch of a try/catch)
+- Use production data in tests — use fixtures or factories instead
+- Create order-dependent tests — each test must be independently runnable
+- Ignore flaky tests — quarantine and fix them; don't just re-run until green
+- Test implementation details (internal method calls) — test observable behaviour
 
 ## Output Templates
 
@@ -75,7 +92,3 @@ When creating test plans, provide:
 3. Coverage analysis
 4. Findings with severity (Critical/High/Medium/Low)
 5. Specific fix recommendations
-
-## Knowledge Reference
-
-Jest, Vitest, pytest, React Testing Library, Supertest, Playwright, Cypress, k6, Artillery, OWASP testing, code coverage, mocking, fixtures, test automation frameworks, CI/CD integration, quality metrics, defect management, BDD, page object model, screenplay pattern, exploratory testing, accessibility (WCAG), usability testing, shift-left testing, quality gates
diff --git a/skills/typescript-pro/SKILL.md b/skills/typescript-pro/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: typescript-pro
-description: Use when building TypeScript applications requiring advanced type systems, generics, or full-stack type safety. Invoke for type guards, utility types, tRPC integration, monorepo setup.
+description: Implements advanced TypeScript type systems, creates custom type guards, utility types, and branded types, and configures tRPC for end-to-end type safety. Use when building TypeScript applications requiring advanced generics, conditional or mapped types, discriminated unions, monorepo setup, or full-stack type safety with tRPC.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -15,28 +15,13 @@ metadata:
 
 # TypeScript Pro
 
-Senior TypeScript specialist with deep expertise in advanced type systems, full-stack type safety, and production-grade TypeScript development.
-
-## Role Definition
-
-You are a senior TypeScript developer with 10+ years of experience. You specialize in TypeScript 5.0+ advanced type system features, full-stack type safety, and build optimization. You create type-safe APIs with zero runtime type errors.
-
-## When to Use This Skill
-
-- Building type-safe full-stack applications
-- Implementing advanced generics and conditional types
-- Setting up tsconfig and build tooling
-- Creating discriminated unions and type guards
-- Implementing end-to-end type safety with tRPC
-- Optimizing TypeScript compilation and bundle size
-
 ## Core Workflow
 
 1. **Analyze type architecture** - Review tsconfig, type coverage, build performance
 2. **Design type-first APIs** - Create branded types, generics, utility types
-3. **Implement with type safety** - Write type guards, discriminated unions, conditional types
-4. **Optimize build** - Configure project references, incremental compilation, tree shaking
-5. **Test types** - Verify type coverage, test type logic, ensure zero runtime errors
+3. **Implement with type safety** - Write type guards, discriminated unions, conditional types; run `tsc --noEmit` to catch type errors before proceeding
+4. **Optimize build** - Configure project references, incremental compilation, tree shaking; re-run `tsc --noEmit` to confirm zero errors after changes
+5. **Test types** - Confirm type coverage with a tool like `type-coverage`; validate that all public APIs have explicit return types; iterate on steps 3–4 until all checks pass
 
 ## Reference Guide
 
@@ -50,6 +35,81 @@ Load detailed guidance based on context:
 | Configuration | `references/configuration.md` | tsconfig options, strict mode, project references |
 | Patterns | `references/patterns.md` | Builder pattern, factory pattern, type-safe APIs |
 
+## Code Examples
+
+### Branded Types
+```typescript
+// Branded type for domain modeling
+type Brand<T, B extends string> = T & { readonly __brand: B };
+type UserId  = Brand<string, "UserId">;
+type OrderId = Brand<number, "OrderId">;
+
+const toUserId  = (id: string): UserId  => id as UserId;
+const toOrderId = (id: number): OrderId => id as OrderId;
+
+// Usage — prevents accidental id mix-ups at compile time
+function getOrder(userId: UserId, orderId: OrderId) { /* ... */ }
+```
+
+### Discriminated Unions & Type Guards
+```typescript
+type LoadingState = { status: "loading" };
+type SuccessState = { status: "success"; data: string[] };
+type ErrorState   = { status: "error";   error: Error };
+type RequestState = LoadingState | SuccessState | ErrorState;
+
+// Type predicate guard
+function isSuccess(state: RequestState): state is SuccessState {
+  return state.status === "success";
+}
+
+// Exhaustive switch with discriminated union
+function renderState(state: RequestState): string {
+  switch (state.status) {
+    case "loading": return "Loading…";
+    case "success": return state.data.join(", ");
+    case "error":   return state.error.message;
+    default: {
+      const _exhaustive: never = state;
+      throw new Error(`Unhandled state: ${_exhaustive}`);
+    }
+  }
+}
+```
+
+### Custom Utility Types
+```typescript
+// Deep readonly — immutable nested objects
+type DeepReadonly<T> = {
+  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
+};
+
+// Require exactly one of a set of keys
+type RequireExactlyOne<T, Keys extends keyof T = keyof T> =
+  Pick<T, Exclude<keyof T, Keys>> &
+  { [K in Keys]-?: Required<Pick<T, K>> & Partial<Record<Exclude<Keys, K>, never>> }[Keys];
+```
+
+### Recommended tsconfig.json
+```json
+{
+  "compilerOptions": {
+    "target": "ES2022",
+    "module": "NodeNext",
+    "moduleResolution": "NodeNext",
+    "strict": true,
+    "noUncheckedIndexedAccess": true,
+    "noImplicitOverride": true,
+    "exactOptionalPropertyTypes": true,
+    "isolatedModules": true,
+    "declaration": true,
+    "declarationMap": true,
+    "incremental": true,
+    "skipLibCheck": false
+  }
+}
+```
+
 ## Constraints
 
 ### MUST DO
diff --git a/skills/vue-expert-js/SKILL.md b/skills/vue-expert-js/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: vue-expert-js
-description: Use when building Vue 3 applications with JavaScript only (no TypeScript). Invoke for JSDoc typing, vanilla JS composables, .mjs modules.
+description: Creates Vue 3 components, builds vanilla JS composables, configures Vite projects, and sets up routing and state management using JavaScript only — no TypeScript. Generates JSDoc-typed code with @typedef, @param, and @returns annotations for full type coverage without a TS compiler. Use when building Vue 3 applications with JavaScript only (no TypeScript), when projects require JSDoc-based type hints, when migrating from Vue 2 Options API to Composition API in JS, or when teams prefer vanilla JavaScript, .mjs modules, or need quick prototypes without TypeScript setup.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,26 +17,12 @@ metadata:
 
 Senior Vue specialist building Vue 3 applications with JavaScript and JSDoc typing instead of TypeScript.
 
-## Role Definition
-
-You are a senior frontend engineer specializing in Vue 3 with Composition API using JavaScript only. You use JSDoc for type safety, ESM modules, and follow modern patterns without requiring TypeScript compilation.
-
-## When to Use This Skill
-
-- Building Vue 3 applications without TypeScript
-- Projects requiring JSDoc-based type hints
-- Migrating from Vue 2 Options API to Composition API (JS)
-- Teams preferring JavaScript over TypeScript
-- Quick prototypes that need Vue patterns without TS setup
-- Legacy projects that cannot adopt TypeScript
-
 ## Core Workflow
 
-1. **Analyze requirements** - Identify if JS-only is appropriate for the project
-2. **Design architecture** - Plan composables with JSDoc type annotations
-3. **Implement** - Build with `<script setup>` (no `lang="ts"`)
-4. **Document** - Add comprehensive JSDoc comments for type safety
-5. **Test** - Use Vitest with JavaScript files
+1. **Design architecture** — Plan component structure and composables with JSDoc type annotations
+2. **Implement** — Build with `<script setup>` (no `lang="ts"`), `.mjs` modules where needed
+3. **Annotate** — Add comprehensive JSDoc comments (`@typedef`, `@param`, `@returns`, `@type`) for full type coverage; then run ESLint with the JSDoc plugin (`eslint-plugin-jsdoc`) to verify coverage — fix any missing or malformed annotations before proceeding
+4. **Test** — Verify with Vitest using JavaScript files; confirm JSDoc coverage on all public APIs; if tests fail, revisit the relevant composable or component, correct the logic or annotation, and re-run until the suite is green
 
 ## Reference Guide
 
@@ -55,16 +41,109 @@ Load detailed guidance based on context:
 - `vue-expert/references/components.md` - Props, emits, slots
 - `vue-expert/references/state-management.md` - Pinia stores
 
+## Code Patterns
+
+### Component with JSDoc-typed props and emits
+
+```vue
+<script setup>
+/**
+ * @typedef {Object} UserCardProps
+ * @property {string} name - Display name of the user
+ * @property {number} age - User's age
+ * @property {boolean} [isAdmin=false] - Whether the user has admin rights
+ */
+
+/** @type {UserCardProps} */
+const props = defineProps({
+  name:    { type: String,  required: true },
+  age:     { type: Number,  required: true },
+  isAdmin: { type: Boolean, default: false },
+})
+
+/**
+ * @typedef {Object} UserCardEmits
+ * @property {(id: string) => void} select - Emitted when the card is selected
+ */
+const emit = defineEmits(['select'])
+
+/** @param {string} id */
+function handleSelect(id) {
+  emit('select', id)
+}
+</script>
+
+<template>
+  <div @click="handleSelect(props.name)">
+    {{ props.name }} ({{ props.age }})
+  </div>
+</template>
+```
+
+### Composable with @typedef, @param, and @returns
+
+```js
+// composables/useCounter.mjs
+import { ref, computed } from 'vue'
+
+/**
+ * @typedef {Object} CounterState
+ * @property {import('vue').Ref<number>} count - Reactive count value
+ * @property {import('vue').ComputedRef<boolean>} isPositive - True when count > 0
+ * @property {() => void} increment - Increases count by step
+ * @property {() => void} reset - Resets count to initial value
+ */
+
+/**
+ * Composable for a simple counter with configurable step.
+ * @param {number} [initial=0] - Starting value
+ * @param {number} [step=1]    - Amount to increment per call
+ * @returns {CounterState}
+ */
+export function useCounter(initial = 0, step = 1) {
+  /** @type {import('vue').Ref<number>} */
+  const count = ref(initial)
+
+  const isPositive = computed(() => count.value > 0)
+
+  function increment() {
+    count.value += step
+  }
+
+  function reset() {
+    count.value = initial
+  }
+
+  return { count, isPositive, increment, reset }
+}
+```
+
+### @typedef for a complex object used across files
+
+```js
+// types/user.mjs
+
+/**
+ * @typedef {Object} User
+ * @property {string}   id       - UUID
+ * @property {string}   name     - Full display name
+ * @property {string}   email    - Contact email
+ * @property {'admin'|'viewer'} role - Access level
+ */
+
+// Import in other files with:
+// /** @type {import('./types/user.mjs').User} */
+```
+
 ## Constraints
 
 ### MUST DO
 - Use Composition API with `<script setup>`
 - Use JSDoc comments for type documentation
-- Use .mjs extension for ES modules when needed
-- Document function parameters with `@param`
-- Document return types with `@returns`
-- Use `@typedef` for complex object shapes
-- Use `@type` annotations for variables
+- Use `.mjs` extension for ES modules when needed
+- Annotate every public function with `@param` and `@returns`
+- Use `@typedef` for complex object shapes shared across files
+- Use `@type` annotations for reactive variables
 - Follow vue-expert patterns adapted for JavaScript
 
 ### MUST NOT DO
@@ -73,14 +152,14 @@ Load detailed guidance based on context:
 - Skip JSDoc types for public APIs
 - Use CommonJS `require()` in Vue files
 - Ignore type safety entirely
-- Mix TypeScript files with JavaScript in same component
+- Mix TypeScript files with JavaScript in the same component
 
 ## Output Templates
 
 When implementing Vue features in JavaScript:
-1. Component file with `<script setup>` (no lang attribute)
-2. JSDoc type definitions for complex props
-3. Composable with `@typedef` and `@param` annotations
+1. Component file with `<script setup>` (no lang attribute) and JSDoc-typed props/emits
+2. `@typedef` definitions for complex prop or state shapes
+3. Composable with `@param` and `@returns` annotations
 4. Brief note on type coverage
 
 ## Knowledge Reference
diff --git a/skills/vue-expert/SKILL.md b/skills/vue-expert/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: vue-expert
-description: Use when building Vue 3 applications with Composition API, Nuxt 3, or Quasar. Invoke for Pinia, TypeScript, PWA, Capacitor mobile apps, Vite configuration.
+description: Builds Vue 3 components with Composition API patterns, configures Nuxt 3 SSR/SSG projects, sets up Pinia stores, scaffolds Quasar/Capacitor mobile apps, implements PWA features, and optimises Vite builds. Use when creating Vue 3 applications with Composition API, writing reusable composables, managing state with Pinia, building hybrid mobile apps with Quasar or Capacitor, configuring service workers, or tuning Vite configuration and TypeScript integration.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,30 +17,14 @@ metadata:
 
 Senior Vue specialist with deep expertise in Vue 3 Composition API, reactivity system, and modern Vue ecosystem.
 
-## Role Definition
-
-You are a senior frontend engineer with 10+ years of JavaScript framework experience. You specialize in Vue 3 with Composition API, Nuxt 3, Pinia state management, and TypeScript integration. You build elegant, reactive applications with optimal performance.
-
-## When to Use This Skill
-
-- Building Vue 3 applications with Composition API
-- Creating reusable composables
-- Setting up Nuxt 3 projects with SSR/SSG
-- Implementing Pinia stores for state management
-- Optimizing reactivity and performance
-- TypeScript integration with Vue components
-- Building mobile/hybrid apps with Quasar and Capacitor
-- Implementing PWA features and service workers
-- Configuring Vite builds and optimizations
-- Custom SSR setups with Fastify or other servers
-
 ## Core Workflow
 
 1. **Analyze requirements** - Identify component hierarchy, state needs, routing
 2. **Design architecture** - Plan composables, stores, component structure
 3. **Implement** - Build components with Composition API and proper reactivity
-4. **Optimize** - Minimize re-renders, optimize computed properties, lazy load
-5. **Test** - Write component tests with Vue Test Utils and Vitest
+4. **Validate** - Run `vue-tsc --noEmit` for type errors; verify reactivity with Vue DevTools. If type errors are found: fix each issue and re-run `vue-tsc --noEmit` until the output is clean before proceeding
+5. **Optimize** - Minimize re-renders, optimize computed properties, lazy load
+6. **Test** - Write component tests with Vue Test Utils and Vitest. If tests fail: inspect failure output, identify whether the root cause is a component bug or an incorrect test assertion, fix accordingly, and re-run until all tests pass
 
 ## Reference Guide
 
@@ -56,6 +40,29 @@ Load detailed guidance based on context:
 | Mobile & Hybrid | `references/mobile-hybrid.md` | Quasar, Capacitor, PWA, service worker, mobile |
 | Build Tooling | `references/build-tooling.md` | Vite config, sourcemaps, optimization, bundling |
 
+## Quick Example
+
+Minimal component demonstrating preferred patterns:
+
+```vue
+<script setup lang="ts">
+import { ref, computed } from 'vue'
+
+const props = defineProps<{ initialCount?: number }>()
+
+const count = ref(props.initialCount ?? 0)
+const doubled = computed(() => count.value * 2)
+
+function increment() {
+  count.value++
+}
+</script>
+
+<template>
+  <button @click="increment">Count: {{ count }} (doubled: {{ doubled }})</button>
+</template>
+```
+
 ## Constraints
 
 ### MUST DO
diff --git a/skills/websocket-engineer/SKILL.md b/skills/websocket-engineer/SKILL.md
@@ -15,28 +15,14 @@ metadata:
 
 # WebSocket Engineer
 
-Senior WebSocket specialist with expertise in real-time bidirectional communication, Socket.IO, and scalable messaging architectures supporting millions of concurrent connections.
-
-## Role Definition
-
-You are a senior real-time systems engineer with 10+ years building WebSocket infrastructure. You specialize in Socket.IO, native WebSockets, horizontal scaling with Redis pub/sub, and low-latency messaging systems. You design for sub-10ms p99 latency with 99.99% uptime.
-
-## When to Use This Skill
-
-- Building WebSocket servers (Socket.IO, ws, uWebSockets)
-- Implementing real-time features (chat, notifications, live updates)
-- Scaling WebSocket infrastructure horizontally
-- Setting up presence systems and room management
-- Optimizing message throughput and latency
-- Migrating from polling to WebSockets
-
 ## Core Workflow
 
-1. **Analyze requirements** - Identify connection scale, message volume, latency needs
-2. **Design architecture** - Plan clustering, pub/sub, state management, failover
-3. **Implement** - Build WebSocket server with authentication, rooms, events
-4. **Scale** - Configure Redis adapter, sticky sessions, load balancing
-5. **Monitor** - Track connections, latency, throughput, error rates
+1. **Analyze requirements** — Identify connection scale, message volume, latency needs
+2. **Design architecture** — Plan clustering, pub/sub, state management, failover
+3. **Implement** — Build WebSocket server with authentication, rooms, events
+4. **Validate locally** — Test connection handling, auth, and room behavior before scaling (e.g., `npx wscat -c ws://localhost:3000`); confirm auth rejection on missing/invalid tokens, room join/leave events, and message delivery
+5. **Scale** — Verify Redis connection and pub/sub round-trip before enabling the adapter; configure sticky sessions and confirm with test connections across multiple instances; set up load balancing
+6. **Monitor** — Track connections, latency, throughput, error rates; add alerts for connection-count spikes and error-rate thresholds
 
 ## Reference Guide
 
@@ -50,27 +36,124 @@ Load detailed guidance based on context:
 | Security | `references/security.md` | Authentication, authorization, rate limiting, CORS |
 | Alternatives | `references/alternatives.md` | SSE, long polling, when to choose WebSockets |
 
+## Code Examples
+
+### Server Setup (Socket.IO with Auth and Room Management)
+
+```js
+import { createServer } from "http";
+import { Server } from "socket.io";
+import { createAdapter } from "@socket.io/redis-adapter";
+import { createClient } from "redis";
+import jwt from "jsonwebtoken";
+
+const httpServer = createServer();
+const io = new Server(httpServer, {
+  cors: { origin: process.env.ALLOWED_ORIGIN, credentials: true },
+  pingTimeout: 20000,
+  pingInterval: 25000,
+});
+
+// Authentication middleware — runs before connection is established
+io.use((socket, next) => {
+  const token = socket.handshake.auth.token;
+  if (!token) return next(new Error("Authentication required"));
+  try {
+    socket.data.user = jwt.verify(token, process.env.JWT_SECRET);
+    next();
+  } catch {
+    next(new Error("Invalid token"));
+  }
+});
+
+// Redis adapter for horizontal scaling
+const pubClient = createClient({ url: process.env.REDIS_URL });
+const subClient = pubClient.duplicate();
+await Promise.all([pubClient.connect(), subClient.connect()]);
+io.adapter(createAdapter(pubClient, subClient));
+
+io.on("connection", (socket) => {
+  const { userId } = socket.data.user;
+  console.log(`connected: ${userId} (${socket.id})`);
+
+  // Presence: mark user online
+  pubClient.hSet("presence", userId, socket.id);
+
+  socket.on("join-room", (roomId) => {
+    socket.join(roomId);
+    socket.to(roomId).emit("user-joined", { userId });
+  });
+
+  socket.on("message", ({ roomId, text }) => {
+    io.to(roomId).emit("message", { userId, text, ts: Date.now() });
+  });
+
+  socket.on("disconnect", () => {
+    pubClient.hDel("presence", userId);
+    console.log(`disconnected: ${userId}`);
+  });
+});
+
+httpServer.listen(3000);
+```
+
+### Client-Side Reconnection with Exponential Backoff
+
+```js
+import { io } from "socket.io-client";
+
+const socket = io("wss://api.example.com", {
+  auth: { token: getAuthToken() },
+  reconnection: true,
+  reconnectionAttempts: 10,
+  reconnectionDelay: 1000,       // initial delay (ms)
+  reconnectionDelayMax: 30000,   // cap at 30 s
+  randomizationFactor: 0.5,      // jitter to avoid thundering herd
+});
+
+// Queue messages while disconnected
+let messageQueue = [];
+
+socket.on("connect", () => {
+  console.log("connected:", socket.id);
+  // Flush queued messages
+  messageQueue.forEach((msg) => socket.emit("message", msg));
+  messageQueue = [];
+});
+
+socket.on("disconnect", (reason) => {
+  console.warn("disconnected:", reason);
+  if (reason === "io server disconnect") socket.connect(); // manual reconnect
+});
+
+socket.on("connect_error", (err) => {
+  console.error("connection error:", err.message);
+});
+
+function sendMessage(roomId, text) {
+  const msg = { roomId, text };
+  if (socket.connected) {
+    socket.emit("message", msg);
+  } else {
+    messageQueue.push(msg); // buffer until reconnected
+  }
+}
+```
+
 ## Constraints
 
 ### MUST DO
-- Implement automatic reconnection with exponential backoff
-- Use sticky sessions for load balancing
-- Handle connection state properly (connecting, connected, disconnecting)
-- Implement heartbeat/ping-pong to detect dead connections
-- Authenticate connections before allowing events
-- Use rooms/namespaces for message scoping
-- Queue messages during disconnection
-- Log connection metrics (count, latency, errors)
+- Use sticky sessions for load balancing (WebSocket connections are stateful — requests must route to the same server instance)
+- Implement heartbeat/ping-pong to detect dead connections (TCP keepalive alone is insufficient)
+- Use rooms/namespaces for message scoping rather than filtering in application logic
+- Queue messages during disconnection windows to avoid silent data loss
+- Plan connection limits per instance before scaling horizontally
 
 ### MUST NOT DO
-- Skip connection authentication
-- Broadcast sensitive data to all clients
-- Store large state in memory without clustering strategy
-- Ignore connection limit planning
-- Mix WebSocket and HTTP on same port without proper config
-- Forget to handle connection cleanup
-- Use polling when WebSockets are appropriate
-- Skip load testing before production
+- Store large state in memory without a clustering strategy (use Redis or an external store)
+- Mix WebSocket and HTTP on the same port without explicit upgrade handling
+- Forget to handle connection cleanup (presence records, room membership, in-flight timers)
+- Skip load testing before production — connection-count spikes behave differently from HTTP traffic spikes
 
 ## Output Templates
 
diff --git a/skills/wordpress-pro/SKILL.md b/skills/wordpress-pro/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: wordpress-pro
-description: Use when developing WordPress themes, plugins, customizing Gutenberg blocks, implementing WooCommerce features, or optimizing WordPress performance and security.
+description: Develops custom WordPress themes and plugins, creates and registers Gutenberg blocks and block patterns, configures WooCommerce stores, implements WordPress REST API endpoints, applies security hardening (nonces, sanitization, escaping, capability checks), and optimizes performance through caching and query tuning. Use when building WordPress themes, writing plugins, customizing Gutenberg blocks, extending WooCommerce, working with ACF, using the WordPress REST API, applying hooks and filters, or improving WordPress performance and security.
 license: MIT
 metadata:
   author: https://github.com/Jeffallan
@@ -17,28 +17,14 @@ metadata:
 
 Expert WordPress developer specializing in custom themes, plugins, Gutenberg blocks, WooCommerce, and WordPress performance optimization.
 
-## Role Definition
-
-You are a senior WordPress developer with deep experience building custom themes, plugins, and WordPress solutions. You specialize in modern WordPress development with PHP 8.1+, Gutenberg block development, WooCommerce customization, REST API integration, and performance optimization. You build secure, scalable WordPress sites following WordPress coding standards and best practices.
-
-## When to Use This Skill
-
-- Building custom WordPress themes with template hierarchy
-- Developing WordPress plugins with proper architecture
-- Creating custom Gutenberg blocks and block patterns
-- Customizing WooCommerce functionality
-- Implementing WordPress REST API endpoints
-- Optimizing WordPress performance and security
-- Working with Advanced Custom Fields (ACF)
-- Full Site Editing (FSE) and block themes
-
 ## Core Workflow
 
-1. **Analyze requirements** - Understand WordPress context, existing setup, goals
-2. **Design architecture** - Plan theme/plugin structure, hooks, data flow
-3. **Implement** - Build using WordPress standards, security best practices
-4. **Optimize** - Cache, query optimization, asset optimization
-5. **Test & secure** - Security audit, performance testing, compatibility checks
+1. **Analyze requirements** — Understand WordPress context, existing setup, and goals.
+2. **Design architecture** — Plan theme/plugin structure, hooks, and data flow.
+3. **Implement** — Build using WordPress coding standards and security best practices.
+4. **Validate** — Run `phpcs --standard=WordPress` to catch WPCS violations; verify nonce handling and capability checks manually.
+5. **Optimize** — Apply transient/object caching, query optimization, and asset enqueuing.
+6. **Test & secure** — Confirm sanitization/escaping on all I/O, test across target WordPress versions, and run a security audit checklist.
 
 ## Reference Guide
 
@@ -52,30 +38,101 @@ Load detailed guidance based on context:
 | Hooks & Filters | `references/hooks-filters.md` | Actions, filters, custom hooks, priorities |
 | Performance & Security | `references/performance-security.md` | Caching, optimization, hardening, backups |
 
+## Key Implementation Patterns
+
+### Nonce Verification (form submissions)
+```php
+// Output nonce field in form
+wp_nonce_field( 'my_action', 'my_nonce' );
+
+// Verify on submission — bail early if invalid
+if ( ! isset( $_POST['my_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['my_nonce'] ) ), 'my_action' ) ) {
+    wp_die( esc_html__( 'Security check failed.', 'my-textdomain' ) );
+}
+```
+
+### Sanitization & Escaping
+```php
+// Sanitize input (store)
+$title   = sanitize_text_field( wp_unslash( $_POST['title'] ?? '' ) );
+$content = wp_kses_post( wp_unslash( $_POST['content'] ?? '' ) );
+$url     = esc_url_raw( wp_unslash( $_POST['url'] ?? '' ) );
+
+// Escape output (display)
+echo esc_html( $title );
+echo wp_kses_post( $content );
+echo '<a href="' . esc_url( $url ) . '">' . esc_html__( 'Link', 'my-textdomain' ) . '</a>';
+```
+
+### Enqueuing Scripts & Styles
+```php
+add_action( 'wp_enqueue_scripts', 'my_theme_assets' );
+function my_theme_assets(): void {
+    wp_enqueue_style(
+        'my-theme-style',
+        get_stylesheet_uri(),
+        [],
+        wp_get_theme()->get( 'Version' )
+    );
+    wp_enqueue_script(
+        'my-theme-script',
+        get_template_directory_uri() . '/assets/js/main.js',
+        [ 'jquery' ],
+        '1.0.0',
+        true // load in footer
+    );
+    // Pass server data to JS safely
+    wp_localize_script( 'my-theme-script', 'MyTheme', [
+        'ajaxUrl' => admin_url( 'admin-ajax.php' ),
+        'nonce'   => wp_create_nonce( 'my_ajax_nonce' ),
+    ] );
+}
+```
+
+### Prepared Database Queries
+```php
+global $wpdb;
+$results = $wpdb->get_results(
+    $wpdb->prepare(
+        "SELECT * FROM {$wpdb->prefix}my_table WHERE user_id = %d AND status = %s",
+        absint( $user_id ),
+        sanitize_text_field( $status )
+    )
+);
+```
+
+### Capability Checks
+```php
+// Always check capabilities before sensitive operations
+if ( ! current_user_can( 'manage_options' ) ) {
+    wp_die( esc_html__( 'You do not have permission to do this.', 'my-textdomain' ) );
+}
+```
+
 ## Constraints
 
 ### MUST DO
-- Follow WordPress Coding Standards (WPCS)
-- Use nonces for form submissions
-- Sanitize all user inputs with appropriate functions
-- Escape all outputs (esc_html, esc_url, esc_attr)
-- Use prepared statements for database queries
-- Implement proper capability checks
-- Enqueue scripts/styles properly (wp_enqueue_*)
+- Follow WordPress Coding Standards (WPCS); validate with `phpcs --standard=WordPress`
+- Use nonces for all form submissions and AJAX requests
+- Sanitize all user inputs with appropriate functions (`sanitize_text_field`, `wp_kses_post`, etc.)
+- Escape all outputs (`esc_html`, `esc_url`, `esc_attr`, `wp_kses_post`)
+- Use prepared statements for all database queries (`$wpdb->prepare`)
+- Implement proper capability checks before privileged operations
+- Enqueue scripts/styles via `wp_enqueue_scripts` / `admin_enqueue_scripts` hooks
 - Use WordPress hooks instead of modifying core
-- Write translatable strings with text domains
-- Test across multiple WordPress versions
+- Write translatable strings with text domains (`__()`, `esc_html__()`, etc.)
+- Test across target WordPress versions
 
 ### MUST NOT DO
 - Modify WordPress core files
 - Use PHP short tags or deprecated functions
 - Trust user input without sanitization
 - Output data without escaping
-- Hardcode database table names (use $wpdb->prefix)
+- Hardcode database table names (use `$wpdb->prefix`)
 - Skip capability checks in admin functions
-- Ignore SQL injection vulnerabilities
-- Bundle unnecessary libraries (use WordPress APIs)
-- Create security vulnerabilities through file uploads
+- Ignore SQL injection vectors
+- Bundle unnecessary libraries when WordPress APIs suffice
+- Allow unsafe file upload handling
 - Skip internationalization (i18n)
 
 ## Output Templates
PATCH

echo "Gold patch applied."
