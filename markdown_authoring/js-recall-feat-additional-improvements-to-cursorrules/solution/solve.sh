#!/usr/bin/env bash
set -euo pipefail

cd /workspace/js-recall

# Idempotency guard
if grep -qF "- **Note**: Alert thresholds and alerting rules should be configured in external" ".cursor/rules/api-specific-config.mdc" && grep -qF "\u2013 **Inline Documentation:** Maintain excellent, thorough inline documentation (e" ".cursor/rules/org-general-practices.mdc" && grep -qF "- **Explicit Return Types:** All functions must have explicit return types. Neve" ".cursor/rules/org-typescript-standards.mdc" && grep -qF "- Boolean flags instead of string enums when binary (e.g., `isLong` vs `side: \"l" ".cursor/rules/repo-specific-config.mdc" && grep -qF "- Avoid situations where the number of database queries scales linearly (e.g. fe" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/api-specific-config.mdc b/.cursor/rules/api-specific-config.mdc
@@ -10,11 +10,127 @@ alwaysApply: false
 ### Database Schema Organization
 - All database schemas must be placed in `packages/db/src/schemas/` with appropriate subdirectories (`core/`, `auth/`, etc.)
 - Schema files must export table definitions and be properly imported in `core/defs.ts`
-- Always generate migrations using `pnpm db:generate` after schema changes which will automatically create the sql migration files
-- Repository classes must be placed in `packages/db/src/repositories/`.
+- Always generate migrations using `pnpm db:gen-migrations` after schema changes which will automatically create the sql migration files
+- Repository classes must be placed in `apps/api/src/database/repositories/` and follow the naming pattern `*-repository.ts`
 - Use the established repository pattern with dependency injection into manager services
 - Include proper indexes for foreign keys and frequently queried columns
 
+### Database Computation Patterns
+- **SQL-First Philosophy**: Always prefer database aggregations over in-memory processing
+  - Use SQL `SUM()`, `AVG()`, `COUNT()` instead of fetching all rows and calculating in JavaScript
+  - Use `DISTINCT ON` with proper indexes for latest-record queries
+  - Use database-level `GROUP BY` for grouping operations
+  - Use CTEs (Common Table Expressions) for complex multi-step queries
+  - Use `ORDER BY` in SQL instead of JavaScript `.sort()`
+  - For complex sorts (like `DISTINCT ON` + different `ORDER BY`), use subqueries with `.as()` in Drizzle
+  - Example: Getting latest summaries should use `DISTINCT ON (agent_id)` not fetch all and filter in memory
+- **Response Size Management**:
+  - Never return unbounded result sets for in-memory processing
+  - Always aggregate at database level when only totals are needed
+  - Example: Use `SUM(total_volume)` in SQL vs fetching 1000+ records to sum in JavaScript
+  - Set reasonable LIMIT clauses for safety even on internal queries
+  - Monitor query response sizes in production
+- **Composite Indexes**: Always add indexes for:
+  - Foreign key relationships
+  - Columns used in `WHERE` clauses
+  - Columns used in `ORDER BY` with `DISTINCT ON`
+  - Multi-column patterns that match query patterns (e.g., `(agent_id, competition_id, timestamp DESC)`)
+- **Query Optimization Principles**:
+  - Prevent the linear query scaling problem: Instead of fetching a list then making separate queries per item, use joins or batch fetching
+  - Use database cursors for large result sets
+  - Leverage database window functions for ranking and analytics
+  - Use `EXPLAIN ANALYZE` to verify query performance
+  - Batch operations should process in chunks (e.g., 100 records at a time)
+
+### Migration Best Practices
+- **Migration Generation**: Always use `pnpm --filter api db:gen-migrations` after schema changes
+- **Migration Naming**: Let Drizzle auto-generate names (e.g., `0041_mighty_wolverine.sql`)
+- **Migration Review**: Always review generated SQL before committing
+- **Backward Compatibility**: Migrations must be backward compatible for zero-downtime deployments
+- **Data Migrations**: Use separate scripts in `apps/api/scripts/` for data migrations, never mix schema and data migrations
+- **Rollback Strategy**: Document rollback SQL for destructive changes in PR description
+- **Testing Migrations**: Test migrations on a copy of production data when possible
+- **Index Creation**: Create indexes `CONCURRENTLY` in production to avoid table locks
+
+### Database Type Safety
+- **Function Return Types**: All functions must have explicit return types
+  - Never rely on TypeScript inference for return types
+  - Be especially explicit for async functions (e.g., `Promise<User[]>`)
+- **Named Types**: Prefer named types/interfaces over inline definitions
+  - Extract complex return types into named interfaces
+  - Reuse types when the same shape appears multiple times
+- **JSON Fields**: Never use `any` for jsonb columns
+  - Create type guard functions for runtime validation
+  - Use Zod schemas for complex JSON structures
+  - Example: `isValidPerpsConfig(data): data is PerpsConfig`
+- **Numeric Types**: Always parse database numerics to numbers
+  - Use `Number()` or `parseFloat()` for numeric columns
+  - Never pass numeric strings to frontend
+  - Be explicit about precision requirements
+- **Enum Safety**: Use TypeScript enums or literal unions for database enums
+- **Null Handling**: Explicitly handle nullable columns with proper types
+  - Use `| null` not `| undefined` for nullable database fields
+  - Consider using Result types for operations that may fail
+
+## Atomic Operations & Race Condition Prevention
+
+### Service Layer Atomicity
+- **TOCTOU Prevention**: Avoid Time-Of-Check-Time-Of-Use patterns where state can change between check and action
+  - ❌ Bad: Check participant limit separately from adding agent (race condition):
+    ```typescript
+    // Multiple agents could pass this check simultaneously!
+    const competition = await getCompetition(competitionId);
+    if (competition.registeredParticipants < competition.maxParticipants) {
+      await addAgentToCompetition(competitionId, agentId);  // ⚠️ Limit could be exceeded!
+      await incrementParticipantCount(competitionId);
+    }
+    ```
+  - ✅ Good: Use transactions with row locks (from `competition-repository.ts`):
+    ```typescript
+    await db.transaction(async (tx) => {
+      // Lock the competition row to prevent concurrent modifications
+      const [competition] = await tx
+        .select({ maxParticipants, registeredParticipants })
+        .from(competitions)
+        .where(eq(competitions.id, competitionId))
+        .for("update");  // Row lock prevents other transactions from reading/modifying
+      
+      // Atomic insert with conflict handling
+      const insertResult = await tx
+        .insert(competitionAgents)
+        .values({ competitionId, agentId })
+        .onConflictDoNothing()
+        .returning();
+      
+      // Only check limit if actually inserted (not duplicate)
+      if (insertResult.length > 0) {
+        if (competition.registeredParticipants + 1 > competition.maxParticipants) {
+          throw new Error("Competition full");  // Transaction rollback keeps count accurate
+        }
+        // Update count atomically within same transaction
+        await tx.update(competitions).set({
+          registeredParticipants: sql`${competitions.registeredParticipants} + 1`
+        });
+      }
+    });
+    ```
+- **State Validation**: For operations that depend on current state:
+  - Validate state as close to the action as possible
+  - Use database row locks (`SELECT FOR UPDATE`) for critical sections
+  - Use optimistic locking with version numbers where appropriate
+
+### Repository Layer Atomicity
+- **Transaction Boundaries**: Use database transactions for multi-step operations
+  - Wrap related database operations in `db.transaction()`
+  - Ensure all-or-nothing semantics for data consistency
+  - Example: Balance updates + trade creation must be atomic
+- **Bulk Operations**: Process in transactions with appropriate batch sizes
+  - Use `FOR UPDATE` locks when reading data that will be modified
+  - Consider using `SELECT ... FOR NO KEY UPDATE` for better concurrency
+- **Idempotency**: Design operations to be safely retryable
+  - Use unique constraints and `ON CONFLICT` clauses
+  - Store idempotency keys for critical operations
+
 ## Authentication & Security
 
 ### Authentication Patterns
@@ -47,6 +163,31 @@ alwaysApply: false
 - Authentication flows must be thoroughly tested
 - Performance-critical changes require load testing validation
 
+### Test Coverage Standards
+- **Current Thresholds**: See `coverage.config.json` for current values
+  - Global thresholds and package-specific overrides are defined there
+  - Coverage is calculated across all packages in aggregate
+  - The config file is the single source of truth for coverage requirements
+- **Coverage Migration Strategy**:
+  - New packages must start with 100% coverage requirements
+  - Existing apps (api, comps) will gradually increase thresholds
+  - Any new critical path code must have tests regardless of package thresholds
+- **Critical Path Coverage**: 100% coverage required for:
+  - Authentication flows
+  - Payment/trading operations
+  - Wallet verification
+  - Competition scoring logic
+  - Financial calculations (PnL, portfolio values)
+- **Coverage Reporting**: All PRs must include coverage report via GitHub Actions
+- **Test Data Management**: 
+  - Never use production data in tests
+  - Use factories or builders for test data generation
+  - Maintain test data consistency across test suites
+- **Test Quality Metrics**:
+  - Tests should be deterministic (no flaky tests)
+  - Tests should run in isolation
+  - Tests should complete within reasonable time (< 30s for unit, < 2min for E2E)
+
 ### Running Tests
 - To run tests using the e2e testing suite, you can use a format such as `cd apps/api && pnpm test:e2e name-of-test.test.ts`
 
@@ -57,6 +198,30 @@ alwaysApply: false
 - Error responses must include `error: string` and `status: number` fields
 - Use consistent HTTP status codes (400 for validation, 401 for auth, 409 for conflicts)
 - Success responses should include relevant data fields and descriptive `message` when appropriate
+- **Error Response Format**:
+  ```typescript
+  {
+    success: false,
+    error: string,
+    status: number,
+    details?: object, // Only in development
+    requestId?: string
+  }
+  ```
+- **Success Response Format**:
+  ```typescript
+  {
+    success: true,
+    data: T,
+    message?: string,
+    pagination?: {
+      total: number,
+      limit: number,
+      offset: number,
+      hasMore: boolean
+    }
+  }
+  ```
 
 ### Route Organization
 - Group routes by feature in `apps/api/src/routes/` (e.g., `agent.routes.ts`, `auth.routes.ts`)
@@ -95,6 +260,13 @@ alwaysApply: false
   - Validate inputs and check preconditions at the start of public methods
   - Return early on invalid conditions rather than nesting the entire method body
   - Let helper methods assume valid inputs (since the public method already validated)
+- **Unknown State Handling**:
+  - Throw explicit errors for unexpected states (e.g., unknown enum values)
+  - ❌ Bad: `default: logger.warn('Unknown type'); return;`
+  - ✅ Good: `default: throw new Error(\`Unknown type: ${type}\`);`
+  - Never silently log and continue when encountering invalid states
+  - Makes bugs immediately visible in development/staging
+  - Use exhaustive type checking with TypeScript's `never` type for enums
 
 ### Code Reuse & Method Implementation
 - **Before implementing any new method**: Always search the codebase for similar existing functionality using semantic search or grep
@@ -123,11 +295,93 @@ alwaysApply: false
 - Caching strategy required for frequently accessed data (user sessions, price data)
 - Retry logic with exponential backoff for transient failures
 - Capacity planning and scaling thresholds must be documented
+- **Query Optimization**:
+  - Use `LIMIT` and `OFFSET` for all list endpoints
+  - Default page size: 10-50 items (never unlimited)
+  - Use database cursors for large result sets
+  - Maximum query time: 5000ms before timeout (enforced at both database and application level)
+  - Set statement_timeout in PostgreSQL for query-level enforcement
+  - Use request timeout middleware for HTTP-level enforcement
+- **Caching Considerations**:
+  - **IMPORTANT FOR AI AGENTS**: Always ask the human before implementing caching:
+    - "Should we add caching here? What TTL would be appropriate?"
+    - "Is platform caching (e.g., Vercel) already handling this?"
+    - "What are the staleness tolerance requirements?"
+  - Consider platform-provided caching (e.g., Vercel's automatic caching)
+  - Evaluate need for application-level caching on case-by-case basis
+  - When implementing caching, consider:
+    - Data volatility and staleness tolerance
+    - Cache invalidation complexity
+    - Memory/storage costs vs performance gains
+  - Document caching decisions and TTLs in code comments
+  - AI should NEVER implement caching without explicit human approval
+- **Response Time SLAs**:
+  - P95 < 200ms for reads
+  - P95 < 500ms for writes
+  - P95 < 1000ms for complex aggregations
+  - P99 < 2000ms for all endpoints
+- **Rate Limiting**:
+  - Default: 100 requests per minute per API key
+  - Burst: Allow 20% over limit for 10 seconds
+  - Return `429 Too Many Requests` with `Retry-After` header
 
 ### Monitoring & Observability
 - All API endpoints must include structured logging with request IDs
 - Health check endpoints must validate all dependencies (DB, external APIs)
 - Business metric tracking and performance SLIs/SLOs required
+- **Metrics Collection (Implemented via Prometheus)**:
+  - **Currently Collected**:
+    - HTTP request duration (histogram with buckets: 25, 50, 100, 200, 500, 1000, 2000, 5000ms)
+    - HTTP request counts by method, route, status code
+    - Database query duration and counts by operation, repository, method
+    - Error tracking via Sentry integration
+  - **Metrics Server**: Separate server on port 3003 (configurable via METRICS_PORT)
+  - **Endpoint**: `/metrics` exposed without auth for internal monitoring
+  - **Note**: Alert thresholds and alerting rules should be configured in external monitoring systems (e.g., Datadog, PagerDuty) that consume these metrics - not implemented in application code
+  - **TODO/Aspirational** (not yet implemented):
+    - Cache hit rates
+    - Business metrics (trades/hour, active agents, competition participation)
+- **Error Tracking & APM (Sentry)**:
+  - **Configuration**:
+    - Production sampling: 10% (traces and profiles)
+    - Development sampling: 100%
+    - Automatic sensitive data scrubbing (auth headers, cookies)
+    - Database query monitoring via wrapped Drizzle operations
+  - **IMPORTANT FOR AI AGENTS**: When integrating with external APIs:
+    - Use `Sentry.addBreadcrumb()` for tracking API interactions
+    - Use `Sentry.captureMessage()` with sampling for successful responses (1% sample rate)
+    - Use `Sentry.captureException()` for all errors with context
+    - Example pattern:
+      ```typescript
+      // Sample 1% of successful responses for monitoring
+      const SAMPLING_RATE = 0.01;
+      if (Math.random() < SAMPLING_RATE) {
+        Sentry.captureMessage("External API Success", {
+          level: "info",
+          extra: { responseTime, endpoint, sampleData }
+        });
+      }
+      ```
+    - Mask sensitive data (e.g., wallet addresses, API keys) before logging
+    - Never log full request/response bodies without sampling
+- **Logging Standards**:
+  - Structured JSON logging with trace ID correlation
+  - Request ID propagation through all layers
+  - Log levels: ERROR, WARN, INFO, DEBUG
+  - Separate application and error logs
+  - Never log sensitive data (passwords, API keys, PII)
+  - **Sampling Rates** (for high-volume logging):
+    - HTTP requests: 10% by default (configurable via HTTP_LOG_SAMPLE_RATE)
+    - Repository operations: 10% by default (configurable via REPOSITORY_LOG_SAMPLE_RATE)
+    - Use `Math.random() < sampleRate` pattern for custom sampling
+    - Always log errors regardless of sampling
+- **Health Checks**:
+  - `/health` - Basic liveness check
+  - `/health/ready` - Readiness check including:
+    - Database connectivity
+    - Redis connectivity
+    - External service availability
+    - Disk space and memory usage
 
 ## Code Quality & Documentation
 
@@ -136,5 +390,9 @@ alwaysApply: false
 - Include `@param` and `@returns` documentation
 - Document error conditions and side effects
 - Repository methods should document database operations and constraints
+- **Never use temporal/comparative language in comments**:
+  - Avoid: "new", "optimized", "replaces", "improved", "efficient", "atomic", "better"
+  - Describe what the method DOES, not how it compares to other implementations
+  - Focus on behavior and contract, not implementation quality
 - At the end of implementing a new feature, always check to see if this invalidates content in `apps/api/README.md` that must be updated
 - For any new environment variables, ensure that `apps/api/.env.example`, `apps/api/.env.test`, and `.github/workflows/api-ci.yml` has been updated to include it
diff --git a/.cursor/rules/org-general-practices.mdc b/.cursor/rules/org-general-practices.mdc
@@ -28,6 +28,11 @@ alwaysApply: true
 - **Choose Appropriate Loops:** Use `for` loops when iteration count is known upfront, `while` for conditional iteration. Modern `for` loops are often cleaner than `while` with manual increment.
 - **Early Exit Strategies:** Prefer methods that can exit early (`.some()`, `.every()`, `.find()`) over methods that process everything (`.filter().length`, `.map()`) when you just need a boolean or single result.
 - **Separation of Concerns:** Separate "what failed" (detailed logging) from "should we continue" (control flow) logic. Log details where the failure is detected, make decisions based on simple booleans.
+- **Push Computation to Data Layer:** When working with databases or external services:
+  - Prefer aggregating/sorting/filtering at the source over fetching-then-processing
+  - Example: SQL `SUM()` instead of fetching all rows to sum in JavaScript
+  - Example: API filtering parameters instead of fetching all then filtering
+  - This reduces memory usage, network transfer, and processing time
 
 ## Data Handling
 – **Mocking:** Mock data *only* for automated tests. Never use mocked or stubbed data in development or production environments.
@@ -37,13 +42,63 @@ alwaysApply: true
 – **Non-Interactive Execution:** When using command-line tools or scripts, ensure they run in non-interactive mode to prevent hangs (e.g., append `| cat` to commands like `git log` if needed, use appropriate flags).
 
 ## Documentation
-– **Inline Documentation:** Maintain excellent, thorough inline documentation (e.g., commentsr functions, methods, types, classes, and complex logic.
+– **Inline Documentation:** Maintain excellent, thorough inline documentation (e.g., comments for functions, methods, types, classes, and complex logic).
 – **READMEs:** When editing README files, conform to the [standard-readme](mdc:https:/github.com/RichardLitt/standard-readme) specification.
+– **CRITICAL - No Temporal or Comparative Comments:** 
+  - **NEVER** use words like "new", "optimized", "efficient", "replaces", "improved", "better", "faster", "atomic" in comments or TSDoc
+  - **NEVER** reference what the code replaces or how it compares to previous versions
+  - **NEVER** mention implementation optimizations (e.g., "avoids N+1", "uses atomic operations", "parallelized")
+  - **DO** describe WHAT the method does and its contract/behavior
+  - **DO** focus on the current functionality without historical context
+  - Example: ❌ BAD: "Optimized method that efficiently fetches users avoiding N+1 queries"
+  - Example: ✅ GOOD: "Fetches users with their associated posts in a single query"
 
 ## Security
 - Be mindful of security best practices, especially when handling user input, authentication, authorization, or interacting with external services.
 - Avoid common vulnerabilities (e.g., XSS, CSRF, insecure direct object references).
 
+## Dead Code Prevention
+- **Dead Code Detection**:
+  - Remove unused functions immediately upon discovery
+  - Use `grep` or semantic search to verify function usage before creating new ones
+  - Prefer extending existing functions over creating similar ones
+  - Remove commented-out code blocks (use version control for history)
+  - **AI AGENT REQUIREMENT**: When implementing a new method that replaces an old one, you MUST remove the old implementation in the same changeset
+- **Function Reuse Audit**:
+  - Before implementing: Search for similar functionality using semantic search
+  - Document why existing solutions don't work if creating new functions
+  - Mark deprecated functions with `@deprecated` TSDoc tag
+  - Include migration path in deprecation notice
+- **Immediate Cleanup (Part of Regular Development)**:
+  - **When implementing a replacement**: Remove the old implementation in the same PR
+  - **After refactoring**: Delete the original code immediately, don't leave both versions
+
+## Pull Request Standards
+- **PR Documentation**: Create `.agent/pr-description-[feature].md` for all features
+- **Required Sections**:
+  - Summary of changes (what and why)
+  - API changes (with request/response examples)
+  - Database changes (with migration details)
+  - Frontend changes (with screenshots if UI)
+  - Testing approach
+  - Performance impact analysis
+  - Breaking changes (if any)
+  - Deployment notes (if special steps required)
+- **Review Checklist**:
+  - [ ] Linter passes (`pnpm lint`)
+  - [ ] Tests pass (`pnpm test`) - Note: Coverage thresholds vary by package
+  - [ ] Documentation updated
+  - [ ] No `any` types introduced
+  - [ ] Database queries optimized
+  - [ ] Migration tested (if applicable)
+  - [ ] Performance impact assessed
+  - [ ] New critical code has tests (even if package has 0% threshold)
+- **PR Size Guidelines**:
+  - Ideal: < 400 lines changed
+  - Maximum: < 1000 lines changed
+  - Split larger changes into multiple PRs
+  - Use feature flags for gradual rollout
+
 # Agent Collaboration & Workflow (.agent/ Directory)
 
 The `.agent/` directory is used for maintaining development context and task tracking:
diff --git a/.cursor/rules/org-typescript-standards.mdc b/.cursor/rules/org-typescript-standards.mdc
@@ -17,6 +17,13 @@ alwaysApply: true
   - Provide `@example` blocks for non-obvious usage.
   - Aim for near-complete documentation coverage (e.g., target 99% if tooling allows measurement).
 - **Type Safety:** Utilize TypeScript's type system effectively. Avoid `any` where possible and prefer specific types.
+  - **Explicit Return Types:** All functions must have explicit return types. Never rely on TypeScript's type inference for function returns.
+  - **Named Types over Ad-hoc Types:** Prefer creating named types/interfaces over inline type definitions, especially when:
+    - The type is used in more than one place
+    - The type represents a domain concept
+    - The type is complex (objects with multiple properties)
+  - Example: ❌ BAD: `function getUser(): { id: string; name: string; email: string }`
+  - Example: ✅ GOOD: `interface User { id: string; name: string; email: string }` then `function getUser(): User`
 - **Async/Await:** Use `async/await` consistently for asynchronous operations. Handle errors properly using `try...catch` blocks or promise rejection handling.
 - **Immutability:** Prefer immutable data structures and updates, especially when dealing with state management, to avoid side effects.
 
diff --git a/.cursor/rules/repo-specific-config.mdc b/.cursor/rules/repo-specific-config.mdc
@@ -87,6 +87,37 @@ Commonly used scripts defined in `package.json` or `turbo.json`:
 - `pnpm docs:check`: Verify TSDoc coverage.
 - `pnpm docs:build`: Generate TypeDoc documentation for all packages.
 
+## Frontend-Backend Contract Standards
+- **Response Consistency**:
+  - All numeric values as numbers, not strings
+  - Boolean flags instead of string enums when binary (e.g., `isLong` vs `side: "long" | "short"`)
+  - Consistent field naming across similar endpoints
+  - Embedded relations follow same structure everywhere
+  - Dates as ISO 8601 strings (e.g., `2024-01-01T00:00:00Z`)
+- **Pagination Contract**:
+  ```typescript
+  {
+    data: T[],
+    pagination: {
+      total: number,
+      limit: number,
+      offset: number,
+      hasMore: boolean
+    }
+  }
+  ```
+- **Type Sharing**:
+  - API types defined in `apps/api/src/types/`
+  - Frontend types in `apps/comps/types/`
+  - Shared types in packages when used by multiple apps
+  - Use code generation for API client types when possible
+- **Field Consistency Rules**:
+  - IDs: Always string (UUIDs)
+  - Amounts/Prices: Always number with explicit precision
+  - Timestamps: ISO 8601 strings
+  - Enums: Use TypeScript string literal unions
+  - Optional fields: Use `| null` for API, handle in frontend
+
 ## Additional Resources (Project Context)
 - [Root README](README.md)
 - [Turborepo Documentation](mdc:https:/turbo.build/repo/docs)
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,6 +4,177 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 For complete development guidance including commands, architecture, and patterns, see [AGENTS.md](./AGENTS.md).
 
+## Code Philosophy
+
+### Database-First Architecture
+
+We believe in leveraging PostgreSQL's power rather than reimplementing logic in application code. This means:
+
+- Complex calculations happen in SQL, not JavaScript
+- Aggregations use database functions (`SUM()`, `AVG()`, `COUNT()`), not array methods
+- Sorting happens in SQL (`ORDER BY`), not JavaScript `.sort()`
+- Use `DISTINCT ON` with proper indexes for latest-record queries
+- Data consistency is enforced by database constraints, not application validation alone
+- Performance optimization starts with proper indexes and query design
+- Never fetch all records to filter/aggregate in memory - use SQL WHERE/GROUP BY/HAVING clauses
+
+### Type Safety Without Compromise
+
+- **Zero tolerance for `any` types** in production code
+- All functions must have explicit return types (never rely on inference)
+- Prefer named types/interfaces over inline type definitions
+- All external data must be validated at runtime using type guards or Zod schemas
+- Database types must be properly typed in TypeScript
+- Prefer compile-time safety over runtime assertions when possible
+
+### Performance Through Design
+
+- Every list endpoint must support pagination (no unlimited queries)
+- Caching decisions require human review (consider platform caching like Vercel first)
+- Every query must have appropriate indexes
+- Avoid situations where the number of database queries scales linearly (e.g. fetching a list then making separate queries per item). Use joins or batch fetching instead
+
+### Testing as Documentation
+
+- Tests demonstrate intended behavior better than comments
+- Tests cover edge cases explicitly, not just happy paths
+- Tests use realistic data scenarios, not contrived examples
+- Test names clearly describe what is being tested and why
+- **Test Coverage**: See `coverage.config.json` for current thresholds
+  - Coverage requirements vary by package
+  - New packages start with higher coverage requirements
+  - All new critical path code needs tests regardless of package thresholds
+
+### Clean Architecture Principles
+
+- **Controllers**: Handle HTTP concerns only (serialization, deserialization, status codes)
+- **Services**: Contain all business logic and orchestration
+- **Repositories**: Manage database interactions exclusively
+- **No cross-layer violations**: Controllers never call repositories directly
+
+### Code Reuse Over Duplication
+
+- Search for existing functionality before implementing new features
+- Document why existing solutions don't work when creating alternatives
+- **When implementing a replacement**: Remove the old implementation in the same PR
+- Remove dead code immediately upon discovery
+- Deprecate properly with migration paths
+
+## Working with Claude
+
+### Critical Documentation Rule
+
+**NEVER use temporal or comparative language in code comments or TSDoc**. This is crucial because:
+
+- Comments like "new optimized method" or "replaces old implementation" become misleading over time
+- Future AI reviewers lack the historical context to understand what "new" or "old" means
+- Implementation details like "avoids N+1" or "atomic operation" belong in commit messages, not code
+
+**Instead of:** "Optimized method that efficiently fetches users avoiding N+1 queries"  
+**Write:** "Fetches users with their associated posts in a single query"
+
+Always describe WHAT the code does, never HOW it compares to other code or WHY it's better.
+
+### Key Principles When Using Claude
+
+1. **Be Explicit About Context**: Claude works best when given clear context about the current task, existing patterns, and constraints.
+
+2. **Leverage Existing Patterns**: Always point Claude to existing implementations of similar features in the codebase.
+
+3. **Validate Generated Code**:
+
+   - Check for `any` types
+   - Verify database queries are optimized
+   - Ensure proper error handling
+   - Confirm test coverage
+
+4. **Iterative Refinement**: Use Claude for initial implementation, then refine based on:
+   - Linting results
+   - Type checking
+   - Test failures
+   - Performance profiling
+
+### Best Practices for Prompting
+
+1. **Reference Specific Files**: Point to exact file paths and line numbers when discussing code.
+
+2. **Include Error Messages**: Provide complete error messages and stack traces.
+
+3. **Specify Requirements Clearly**:
+
+   - Performance requirements (response times, throughput)
+   - Type safety requirements
+   - Testing requirements
+   - Documentation needs
+
+4. **Request Explanations**: Ask Claude to explain trade-offs and design decisions.
+
+## Critical Rules Summary
+
+### Never Do These
+
+- ❌ Use `any` type (use proper type guards or generics)
+- ❌ Fetch all records then filter in memory (use SQL WHERE clauses)
+- ❌ Create unbounded queries (always use LIMIT)
+- ❌ Mix authentication patterns (stick to one per endpoint)
+- ❌ Log sensitive data (passwords, API keys, PII)
+- ❌ Skip tests for critical paths (auth, payments, trading)
+- ❌ Implement caching without human review (always discuss caching strategy first)
+- ❌ Leave both old and new implementations when refactoring (remove replaced code immediately)
+- ❌ Use temporal/comparative words in comments ("new", "optimized", "replaces", "efficient")
+
+### Always Do These
+
+- ✅ Use TypeScript strict mode
+- ✅ Specify explicit return types for all functions
+- ✅ Create named types/interfaces instead of inline type definitions
+- ✅ Add indexes for foreign keys and WHERE clause columns
+- ✅ Validate environment variables on startup
+- ✅ Use structured JSON logging with request IDs
+- ✅ Document breaking changes in PR descriptions
+- ✅ Run linter and tests before marking tasks complete
+- ✅ Push computation to the database (aggregations, sorting, filtering)
+- ✅ Use atomic operations to prevent race conditions
+- ✅ Sample high-volume logging and monitoring events (e.g., 1-10%)
+- ✅ Mask sensitive data in logs (wallet addresses, API keys)
+- ✅ Write comments that describe WHAT code does, not HOW it's better than before
+
+## Quick Reference
+
+### Commands
+
+```bash
+# Development
+pnpm dev              # Start all apps
+pnpm build            # Build everything
+pnpm lint             # Check code style
+pnpm format           # Auto-fix formatting
+pnpm test             # Run tests
+
+# Database (API)
+pnpm --filter api db:gen-migrations  # Generate migration
+pnpm --filter api db:migrate   # Run migrations
+pnpm --filter api db:studio    # Open Drizzle Studio
+```
+
+### File Locations
+
+- API Routes: `apps/api/src/routes/`
+- Controllers: `apps/api/src/controllers/`
+- Services: `apps/api/src/services/`
+- Repositories: `apps/api/src/database/repositories/`
+- DB Schemas: `packages/db-schema/src/`
+- Frontend Components: `apps/comps/components/`
+
 ## Claude Code Specific Notes
 
 This project is optimized for AI development assistance. All standard development patterns and commands are documented in the AGENTS.md file above.
+
+When working with Claude Code:
+
+1. The project uses pnpm workspaces - be aware of package boundaries
+2. Database changes require migration generation (`pnpm --filter api db:gen-migrations`)
+3. TSDoc coverage requirements vary by package (see `coverage.config.json`)
+4. E2E tests run against a real database - ensure proper cleanup
+5. Metrics are exposed via Prometheus on port 3003 - alerting is handled externally
+6. Sentry is configured for error tracking with 10% sampling in production
PATCH

echo "Gold patch applied."
