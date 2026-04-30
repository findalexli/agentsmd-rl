#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fullstack-starter

# Idempotency guard
if grep -qF "description: Comprehensive backend development skill for building scalable backe" ".agent/skills/backend-development/SKILL.md" && grep -qF "**DETECTION**: At the start of a session in a Next.js project, check for `cacheC" ".agent/skills/cache-components/SKILL.md" && grep -qF "**Complexity Threshold**: Components with **cyclomatic complexity > 50** or **li" ".agent/skills/component-refactoring/SKILL.md" && grep -qF "description: Automates the creation of detailed, well-formatted Pull Requests us" ".agent/skills/create-pr/SKILL.md" && grep -qF "description: Expert guidance for designing, implementing, and maintaining cloud " ".agent/skills/devops-iac-engineer/SKILL.md" && grep -qF "description: Guide for creating and organizing FastAPI routes using a file-based" ".agent/skills/fastapi-router-creator/SKILL.md" && grep -qF "description: Production-ready FastAPI project templates and patterns. Use when s" ".agent/skills/fastapi-templates/SKILL.md" && grep -qF "1. **Scan**: Read the code to identify architectural patterns, hooks usage, and " ".agent/skills/frontend-code-review/SKILL.md" && grep -qF "description: Comprehensive software architecture skill for designing scalable, m" ".agent/skills/senior-architect/SKILL.md" && grep -qF "description: Discover, retrieve, and learn about available Agent Skills. key cap" ".agent/skills/skill-lookup/SKILL.md" && grep -qF "description: Helper for scaffolding new Terraform modules. Complements terraform" ".agent/skills/terraform-module-creator/SKILL.md" && grep -qF "description: Expert guidance for creating, managing, and using Terraform modules" ".agent/skills/terraform-module-library/SKILL.md" && grep -qF "description: Manages Terraform state operations such as importing, moving, and r" ".agent/skills/terraform-state-manager/SKILL.md" && grep -qF "description: Advanced design intelligence for professional UI/UX. Use for implem" ".agent/skills/ui-ux-pro-max/SKILL.md" && grep -qF "description: Develop custom native UI libraries based on Flutter widgets for Web" ".agent/skills/webf-native-ui-dev/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/backend-development/SKILL.md b/.agent/skills/backend-development/SKILL.md
@@ -0,0 +1,44 @@
+---
+name: backend-development
+description: Comprehensive backend development skill for building scalable backend systems using Python (FastAPI), Postgres, Redis, and more. Includes API design, database optimization, security implementation, and performance tuning.
+---
+
+# Backend Development
+
+This skill provides expert guidance for building robust, scalable, and secure backend systems, primarily focusing on the Python/FastAPI ecosystem used in this project.
+
+## Core Capabilities
+
+### 1. API Design & Implementation
+- **RESTful Design**: Resource-oriented URLs, proper HTTP methods, and status codes.
+- **FastAPI Best Practices**: Validation with Pydantic, dependency injection, and async handlers.
+- **Documentation**: Automatic OpenAPI generation, clear descriptions, and examples.
+
+### 2. Database Management
+- **Schema Design**: Normalized relationships, indexing strategies, and migration management (Alembic).
+- **ORM Usage**: SQLAlchemy async session management, repository pattern.
+- **Optimization**: N+1 problem avoidance, query analysis, connection pooling.
+
+### 3. Security
+- **Authentication**: JWT/OAuth2 implementation, password hashing (bcrypt/argon2).
+- **Authorization**: Role-Based Access Control (RBAC), scopes.
+- **Data Protection**: Input sanitization, SQL injection prevention (via ORM), secure headers.
+
+### 4. Performance Tuning
+- **Caching**: Redis implementation for specific endpoints or data.
+- **Async I/O**: Non-blocking database and API calls.
+- **Background Tasks**: Offloading heavy processing (Celery/Cloud Tasks).
+
+## Design Patterns
+
+- **Repository Pattern**: Decouple business logic from data access.
+- **Dependency Injection**: Manage dependencies (DB sessions, config) cleanly.
+- **Service Layer**: Encapsulate complex business rules.
+
+## When to Use
+
+- Designing new API endpoints or microservices.
+- Optimizing slow database queries.
+- Implementing complex business logic.
+- Reviewing backend code for security and performance.
+- Setting up authentication and authorization flows.
diff --git a/.agent/skills/cache-components/SKILL.md b/.agent/skills/cache-components/SKILL.md
@@ -0,0 +1,126 @@
+---
+name: cache-components
+description: Expert guidance for Next.js Cache Components and Partial Prerendering (PPR). PROACTIVE ACTIVATION when cacheComponents config is detected.
+---
+
+Expert guidance for Next.js Cache Components and Partial Prerendering (PPR).
+
+**PROACTIVE ACTIVATION**: Use this skill automatically when working in Next.js projects that have `cacheComponents: true` in their `next.config.ts` or `next.config.js`.
+
+**DETECTION**: At the start of a session in a Next.js project, check for `cacheComponents: true` in `next.config`. If enabled, this skill's patterns should guide all component authoring, data fetching, and caching decisions.
+
+**USE CASES**:
+- Implementing `'use cache'` directive
+- Configuring cache lifetimes with `cacheLife()`
+- Tagging cached data with `cacheTag()`
+- Invalidating caches with `updateTag()` / `revalidateTag()`
+- Optimizing static vs dynamic content boundaries
+- Debugging cache issues
+- Reviewing Cache Component implementations
+
+## Project Detection
+
+When starting work in a Next.js project, check if Cache Components are enabled:
+
+```bash
+# Check next.config.ts or next.config.js for cacheComponents
+grep -r "cacheComponents" next.config.* 2>/dev/null
+```
+
+If `cacheComponents: true` is found, apply this skill's patterns proactively when:
+- Writing React Server Components
+- Implementing data fetching
+- Creating Server Actions with mutations
+- Optimizing page performance
+- Reviewing existing component code
+
+## Core Concept: The Caching Decision Tree
+
+When writing a **React Server Component**, ask:
+
+1. **Does it depend on request context?** (cookies, headers, searchParams)
+2. **Can this be cached?** (Is the output the same for all users?)
+   - **YES** -> `'use cache'` + `cacheTag()` + `cacheLife()`
+   - **NO** -> Wrap in `<Suspense>` (dynamic streaming)
+
+## Philosophy: Code Over Configuration
+
+Cache Components represents a shift from segment-based configuration to compositional code:
+
+- **Before (Deprecated)**: `export const revalidate = 3600`
+- **After**: `cacheLife('hours')` inside `'use cache'`
+
+- **Before (Deprecated)**: `export const dynamic = 'force-static'`
+- **After**: Use `'use cache'` and Suspense boundaries
+
+## Quick Start
+
+### 1. Enable Configuration
+```typescript
+// next.config.ts
+import type { NextConfig } from "next";
+
+const nextConfig: NextConfig = {
+  experimental: {
+    ppr: true,
+    dynamicIO: true, // often correlated features
+  },
+  // Ensure basic cache components flag if required by your version
+};
+
+export default nextConfig;
+```
+
+### 2. Basic Usage
+
+```typescript
+import { cacheLife } from 'next/cache';
+
+async function CachedPosts() {
+  'use cache'
+  cacheLife('hours'); // Cache for hours
+
+  const posts = await db.posts.findMany();
+  return <PostList posts={posts} />;
+}
+```
+
+## Core APIs
+
+### `'use cache'`
+Marks a function, component, or file as cacheable. The return value is cached and shared across requests.
+
+### `cacheLife(profile)`
+Control cache duration using semantic profiles:
+- `'seconds'`: Short-lived
+- `'minutes'`: Medium-lived
+- `'hours'`: Long-lived
+- `'days'`: Very long-lived
+- `'weeks'`: Static-like content
+- `'max'`: Permanent cache
+
+### `cacheTag(...tags)`
+Tag cached data for on-demand invalidation.
+
+```typescript
+import { cacheTag } from 'next/cache';
+
+async function getUserProfile(id: string) {
+  'use cache'
+  cacheTag('user-profile', `user-${id}`);
+  // ... fetch logic
+}
+```
+
+### `revalidateTag(tag)` / `expireTag(tag)`
+Invalidate cached data in background or immediately.
+
+```typescript
+'use server'
+import { expireTag } from 'next/cache';
+
+export async function updateUser(id: string, data: any) {
+  await db.user.update({ where: { id }, data });
+  expireTag(`user-${id}`); // Invalidate specific cache
+}
+```
diff --git a/.agent/skills/component-refactoring/SKILL.md b/.agent/skills/component-refactoring/SKILL.md
@@ -0,0 +1,109 @@
+---
+name: component-refactoring
+description: Refactor high-complexity React components. Use when complexity metrics are high or to split monolithic UI.
+---
+
+# Component Refactoring Skill
+
+Refactor high-complexity React components with proven patterns and workflows.
+
+**Complexity Threshold**: Components with **cyclomatic complexity > 50** or **line count > 300** should be candidates for refactoring.
+
+**Use When**:
+- `pnpm analyze-component` shows high complexity.
+- Users ask for "code splitting", "hook extraction", or "cleanup".
+- A component file exceeds 300 lines of code.
+
+## Core Refactoring Patterns
+
+### 1. Extract Custom Hooks
+**Goal**: Separate UI from State/Logic.
+
+**Before**:
+```tsx
+function UserList() {
+  const [users, setUsers] = useState([]);
+  const [loading, setLoading] = useState(false);
+
+  useEffect(() => {
+    setLoading(true);
+    fetch('/api/users').then(data => {
+      setUsers(data);
+      setLoading(false);
+    });
+  }, []);
+
+  if (loading) return <Spinner />;
+  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
+}
+```
+
+**After**:
+```tsx
+// hooks/useUsers.ts
+function useUsers() {
+  return useQuery({ queryKey: ['users'], queryFn: fetchUsers });
+}
+
+// UserList.tsx
+function UserList() {
+  const { data: users, isLoading } = useUsers();
+  if (isLoading) return <Spinner />;
+  return <UserListView users={users} />;
+}
+```
+
+### 2. Extract Sub-Components
+**Goal**: Break down monolithic JSX.
+
+**Before**:
+```tsx
+function Dashboard() {
+  return (
+    <div>
+      <header>...</header>
+      <aside>...</aside>
+      <main>
+        <section className="stats">...</section>
+        <section className="feed">...</section>
+      </main>
+    </div>
+  );
+}
+```
+
+**After**:
+```tsx
+function Dashboard() {
+  return (
+    <Layout>
+      <DashboardHeader />
+      <DashboardSidebar />
+      <DashboardContent>
+        <StatsWidget />
+        <ActivityFeed />
+      </DashboardContent>
+    </Layout>
+  );
+}
+```
+
+### 3. Simplify Conditional Logic
+**Goal**: Reduce nesting and `if/else` checks implementation details.
+
+- Use **Lookup Tables** (Maps/Objects) instead of Switch/If-Else chains.
+- Use **Guard Clauses** (Early Returns) to avoid deep nesting.
+
+### 4. Extract Modal Management
+**Goal**: Centralize modal state and logic.
+
+- Move modal definitions to a generic `<ModalManager />` or context if reused globally.
+- Keep the `isOpen` state locally if specific to a single component, but extract the Modal content to a separate file.
+
+## Workflow
+
+1. **Analyze**: Run complexity analysis or review the file manually.
+2. **Plan**: Identify seam lines (Logic vs UI, Section vs Section).
+3. **Extract**: Create new files for hooks or components.
+4. **Integrate**: Replace original code with imports.
+5. **Verify**: Ensure functionality remains identical and tests pass.
diff --git a/.agent/skills/create-pr/SKILL.md b/.agent/skills/create-pr/SKILL.md
@@ -0,0 +1,38 @@
+---
+name: create-pr
+description: Automates the creation of detailed, well-formatted Pull Requests using the GitHub CLI. Parses conventional commits to generate titles and descriptions.
+---
+
+# Create PR
+
+This skill streamlines the Pull Request process, ensuring consistent and high-quality PR descriptions.
+
+## Prerequisites
+
+- `gh` (GitHub CLI) must be installed and authenticated.
+- The current branch must have commits that are not yet on the remote (or a corresponding remote branch).
+
+## Workflow
+
+1.  **Analyze Context**: Checks the git log to understand the changes (`feat`, `fix`, `chore`).
+2.  **Generate Metadata**:
+    - **Title**: Uses the conventional commit format (e.g., `feat: Implement user login`).
+    - **Body**: Summarizes the changes, links to issues, and provides verification steps.
+3.  **Execute**: Runs `gh pr create`.
+
+## Usage
+
+```bash
+# Standard usage (interactive)
+gh pr create
+
+# Fully automated with flags
+gh pr create --title "feat: Add user profile" --body "Implements user profile page..."
+```
+
+## Best Practices for PRs
+
+- **Small & Focused**: Keep PRs limited to a single logical change.
+- **Linked Issues**: Always link to the task/issue (e.g., `Closes #123`).
+- **Self-Review**: Review your own diff before creating the PR.
+- **Verification**: Explicitly state how you verified the change (screenshots, test output).
diff --git a/.agent/skills/devops-iac-engineer/SKILL.md b/.agent/skills/devops-iac-engineer/SKILL.md
@@ -0,0 +1,57 @@
+---
+name: devops-iac-engineer
+description: Expert guidance for designing, implementing, and maintaining cloud infrastructure using Experience in Infrastructure as Code (IaC) principles. Use this skill for architecting cloud solutions, setting up CI/CD pipelines, implementing observability, and following SRE best practices.
+---
+
+# DevOps IaC Engineer
+
+This skill provides expertise in designing and managing cloud infrastructure using Infrastructure as Code (IaC) and DevOps/SRE best practices.
+
+## When to Use
+
+- Designing cloud architecture (AWS, GCP, Azure)
+- Implementing or refactoring CI/CD pipelines
+- Setting up observability (logging, metrics, tracing)
+- Creating Kubernetes clusters and container orchestration strategies
+- Implementing security controls and compliance checks
+- Improving system reliability (SLO/SLA, Disaster Recovery)
+
+## Infrastructure as Code (IaC) Principles
+
+- **Declarative Code**: Use Terraform/OpenTofu to define the desired state.
+- **GitOps**: Code repository is the single source of truth. Changes are applied via PRs and automated pipelines.
+- **Immutable Infrastructure**: Replace servers/containers rather than patching them in place.
+
+## Core Domains
+
+### 1. Terraform & IaC
+- Use modules for reusability.
+- Separate state by environment (dev, stage, prod) and region.
+- Automate `plan` and `apply` in CI/CD.
+
+### 2. Kubernetes & Containers
+- Build small, stateless containers.
+- Use Helm or Kustomize for resource management.
+- Implement resource limits and requests.
+- Use namespaces for isolation.
+
+### 3. CI/CD Pipelines
+- **CI**: Lint, test, build, and scan (security) on every commit.
+- **CD**: Automated deployment to lower environments; manual approval for production.
+- Use tools like GitHub Actions, Cloud Build, or ArgoCD.
+
+### 4. Observability
+- **Logs**: Centralized logging (e.g., Cloud Logging, ELK).
+- **Metrics**: Prometheus/Grafana or Cloud Monitoring.
+- **Tracing**: OpenTelemetry for distributed tracing.
+
+### 5. Security (DevSecOps)
+- Scan IaC for misconfigurations (e.g., Checkov, Trivy).
+- Manage secrets utilizing Secret Manager or Vault (never in code).
+- Least privilege IAM roles.
+
+## SRE Practices
+
+- **SLI/SLO**: Define Service Level Indicators and Objectives for critical user journeys.
+- **Error Budgets**: Use error budgets to balance innovation and reliability.
+- **Post-Mortems**: Conduct blameless post-mortems for incidents.
diff --git a/.agent/skills/fastapi-router-creator/SKILL.md b/.agent/skills/fastapi-router-creator/SKILL.md
@@ -0,0 +1,69 @@
+---
+name: fastapi-router-creator
+description: Guide for creating and organizing FastAPI routes using a file-based routing system or modular router pattern. Helps organize complex API structures.
+---
+
+# FastAPI Router Creator
+
+This skill guides the creation of modular, organized FastAPI routers, emphasizing maintainability and scalability.
+
+## Routing Strategies
+
+### 1. Modular Router Pattern (Standard)
+
+The most common and recommended approach for FastAPI.
+
+**Structure:**
+```
+src/api/v1/endpoints/
+├── users.py
+├── items.py
+└── auth.py
+```
+
+**Implementation:**
+
+`src/api/v1/endpoints/users.py`:
+```python
+from fastapi import APIRouter
+
+router = APIRouter()
+
+@router.get("/")
+async def get_users():
+    ...
+```
+
+`src/api/v1/api.py` (Aggregator):
+```python
+from fastapi import APIRouter
+from src.api.v1.endpoints import users, items
+
+api_router = APIRouter()
+api_router.include_router(users.router, prefix="/users", tags=["users"])
+api_router.include_router(items.router, prefix="/items", tags=["items"])
+```
+
+### 2. File-Based Routing (fastapi-router)
+
+For a Next.js-like experience where file structure dictates URLs. (Requires `fastapi-router` library or custom walker).
+
+**Structure:**
+```
+src/app/
+├── api/
+│   ├── users/
+│   │   ├── route.py  # Handles /api/users
+│   │   └── [id]/
+│   │       └── route.py # Handles /api/users/{id}
+```
+
+## Best Practices
+
+1.  **Prefixing**: Use prefixes at the router include level, not inside every endpoint decorator.
+2.  **Tags**: Use tags to group endpoints in OpenAPI docs.
+3.  **Dependencies**: Apply dependencies (like auth) at the router level if they apply to all endpoints in that router.
+    ```python
+    router = APIRouter(dependencies=[Depends(get_current_active_user)])
+    ```
+4.  **Version**: Namespace routers by API version (`v1`, `v2`).
diff --git a/.agent/skills/fastapi-templates/SKILL.md b/.agent/skills/fastapi-templates/SKILL.md
@@ -0,0 +1,91 @@
+---
+name: fastapi-templates
+description: Production-ready FastAPI project templates and patterns. Use when starting new FastAPI projects, services, or adding standard components like auth, DB connection, or middleware.
+---
+
+# FastAPI Templates
+
+This skill provides production-ready templates and scaffolding patterns for FastAPI applications.
+
+## When to Use
+
+- Starting a new FastAPI service or project.
+- Adding standard components (Auth, DB, Logging) to an existing app.
+- Standardizing project structure across the team.
+
+## Project Structure Template
+
+Recommended structure for scalable FastAPI apps:
+
+```
+src/
+├── api/
+│   ├── v1/
+│   │   ├── endpoints/  # Route handlers
+│   │   └── api.py      # Router aggregation
+│   └── deps.py         # Dependencies (get_current_user, etc.)
+├── core/
+│   ├── config.py       # Pydantic BaseSettings
+│   └── security.py     # JWT & Password hashing
+├── db/
+│   ├── models/         # SQLAlchemy models
+│   ├── session.py      # DB engine and session factory
+│   └── base.py         # Import all models here
+├── schemas/            # Pydantic models (Request/Response)
+├── services/           # Business logic
+└── main.py             # App entrypoint
+```
+
+## Code Templates
+
+### 1. Standard API Endpoint
+
+```python
+from fastapi import APIRouter, Depends, HTTPException
+from sqlalchemy.ext.asyncio import AsyncSession
+from src.api import deps
+from src.schemas.item import ItemCreate, Item
+from src.services import item_service
+
+router = APIRouter()
+
+@router.post("/", response_model=Item)
+async def create_item(
+    item_in: ItemCreate,
+    db: AsyncSession = Depends(deps.get_db),
+    current_user = Depends(deps.get_current_user),
+) -> Item:
+    """
+    Create a new item.
+    """
+    return await item_service.create(db, obj_in=item_in, owner_id=current_user.id)
+```
+
+### 2. Pydantic Settings
+
+```python
+from pydantic_settings import BaseSettings
+
+class Settings(BaseSettings):
+    PROJECT_NAME: str = "FastAPI App"
+    DATABASE_URL: str
+    SECRET_KEY: str
+
+    class Config:
+        case_sensitive = True
+        env_file = ".env"
+
+settings = Settings()
+```
+
+### 3. SQLAlchemy Async Model
+
+```python
+from sqlalchemy import Column, Integer, String
+from src.db.base_class import Base
+
+class Item(Base):
+    id = Column(Integer, primary_key=True, index=True)
+    title = Column(String, index=True)
+    description = Column(String, nullable=True)
+```
diff --git a/.agent/skills/frontend-code-review/SKILL.md b/.agent/skills/frontend-code-review/SKILL.md
@@ -0,0 +1,67 @@
+---
+name: frontend-code-review
+description: Standardized checklist and process for reviewing frontend code (.tsx, .ts, .js).
+---
+
+# Frontend Code Review Skill
+
+**Intent**: Use whenever requested to review frontend code (React, Next.js, TypeScript).
+
+**Supports**:
+- **Pending-change review**: Reviewing `git diff` or staged files.
+- **File-targeted review**: Reviewing specific existing files.
+
+## Review Process
+
+1. **Scan**: Read the code to identify architectural patterns, hooks usage, and component structure.
+2. **Check**: Apply the [Review Checklist](#review-checklist).
+3. **Report**: Output findings in the [Required Output Format](#required-output-format).
+
+## Review Checklist
+
+### 1. Code Quality & Style
+- [ ] **Naming**: Are variables/functions named descriptively? (e.g., `isLoading` vs `flag`)
+- [ ] **Type Safety**: Is `any` avoided? are interfaces defined clearly?
+- [ ] **Constants**: Are magic numbers/strings extracted to constants?
+- [ ] **Destructuring**: Is consistent destructuring used for props?
+
+### 2. React & Next.js Best Practices
+- [ ] **Hooks**: Are hooks used correctly (dependency arrays, rules of hooks)?
+- [ ] **Server/Client**: Is `'use client'` used only when necessary?
+- [ ] **Memoization**: Are `useMemo`/`useCallback` used appropriately (not prematurely)?
+- [ ] **Keys**: Do lists have stable, unique keys?
+
+### 3. Performance
+- [ ] **Bundle Size**: Are large libraries imported entirely when tree-shaking is possible?
+- [ ] **Images**: Is `next/image` used with proper sizing?
+- [ ] **Renders**: Are there obvious unnecessary re-renders?
+
+### 4. Accessibility (a11y)
+- [ ] **Semantic HTML**: Are `div`s used where `button`, `section`, etc., are needed?
+- [ ] **Attributes**: Do images have `alt` text? Do inputs have labels?
+
+## Required Output Format
+
+```markdown
+# Code Review
+
+Found <N> urgent issues:
+## 1. <Issue Title>
+**File**: `<path>` line `<line>`
+
+```typescript
+<snippet of problematic code>
+```
+
+**Reason**: <Why is this urgent?>
+**Suggested Fix**:
+```typescript
+<snippet of fixed code>
+```
+
+---
+
+Found <M> suggestions:
+- **<Refactor/Style>**: <Description>
+- **<Optimization>**: <Description>
+```
diff --git a/.agent/skills/senior-architect/SKILL.md b/.agent/skills/senior-architect/SKILL.md
@@ -0,0 +1,40 @@
+---
+name: senior-architect
+description: Comprehensive software architecture skill for designing scalable, maintainable systems using ReactJS, NextJS, NodeJS, FastAPI, Flutter, etc. Includes system design patterns, tech stack decision frameworks, and modularity analysis.
+---
+
+# Senior Architect
+
+This skill provides high-level architectural guidance, ensuring the system is scalable, maintainable, and aligned with business goals.
+
+## Core Competencies
+
+### 1. System Design
+- **Microservices vs. Monolith**: Evaluate trade-offs based on team size and domain complexity.
+- **Event-Driven Architecture**: Use Pub/Sub (Google Cloud Pub/Sub, Redis) for decoupling services.
+- **Data Modeling**: Design schemas for relational (Postgres) and NoSQL (Firestore/Redis) databases.
+
+### 2. Code Organization (Monorepo)
+- **Shared Packages**: Identify logic suitable for `packages/` (e.g., UI kit, i18n, types).
+- **Feature Modules**: encapsulate features rather than technical layers.
+- **Dependency Rules**: Enforce strict boundaries (e.g., UI cannot import DB logic directly).
+
+### 3. Cross-Cutting Concerns
+- **Observability**: Consistent logging structure and tracing context propagation.
+- **Security**: centralized auth verification and secret management.
+- **Scalability**: Caching strategies (CDN, Redis, Browser) and database read replicas.
+
+## Decision Framework
+
+When evaluating a new technology or pattern:
+1.  **Problem Fit**: Does it solve a real problem we have?
+2.  **Cost**: What is the maintenance overhead?
+3.  **Team**: Does the team have the skills (or capacity to learn)?
+4.  **Lock-in**: How hard is it to replace later?
+
+## When to Use
+
+- "How should we structure the notification system?"
+- "Review this DB schema for performance."
+- "Should we put this logic in the frontend or backend?"
+- "Design a scalable folder structure for the new module."
diff --git a/.agent/skills/skill-lookup/SKILL.md b/.agent/skills/skill-lookup/SKILL.md
@@ -0,0 +1,32 @@
+---
+name: skill-lookup
+description: Discover, retrieve, and learn about available Agent Skills. key capability for finding tools to solve specific problems.
+---
+
+# Skill Lookup
+
+This skill allows the Agent to introspect its own capabilities and find the right tool for the job.
+
+## Capabilities
+
+### 1. Search Skills
+Find skills by keyword, category, or tag.
+
+- **Query**: "infrastructure", "flutter", "test"
+- **Result**: List of matching skills with descriptions.
+
+### 2. Get Skill Details
+Retrieve the full instructions (`SKILL.md`) for a specific skill.
+
+## When to Use
+
+- User asks "Do you have a skill for X?"
+- Agent is unsure how to perform a specialized task and wants to check if a skill exists.
+- "List all available skills."
+
+## How it Works (Conceptual)
+
+The Agent should:
+1.  Check the `.agent/skills` directory.
+2.  Read the `SKILL.md` frontmatter to match requirements.
+3.  Load the full `SKILL.md` if a match is found to learn the instructions.
diff --git a/.agent/skills/terraform-module-creator/SKILL.md b/.agent/skills/terraform-module-creator/SKILL.md
@@ -0,0 +1,54 @@
+---
+name: terraform-module-creator
+description: Helper for scaffolding new Terraform modules. Complements terraform-module-library by providing structure generation.
+---
+
+# Terraform Module Creator
+
+This skill assists in scaffolding new Terraform modules following the standards defined in `terraform-module-library`.
+
+## Quick Start
+
+To create a new module, you should create the following directory structure:
+
+```bash
+mkdir -p modules/<module-name>
+touch modules/<module-name>/{main,variables,outputs,versions}.tf
+touch modules/<module-name>/README.md
+```
+
+## Template Files
+
+### versions.tf
+```hcl
+terraform {
+  required_version = ">= 1.0"
+  required_providers {
+    google = {
+      source  = "hashicorp/google"
+      version = ">= 4.0"
+    }
+  }
+}
+```
+
+### variables.tf
+```hcl
+variable "project_id" {
+  description = "The project ID"
+  type        = string
+}
+```
+
+### outputs.tf
+```hcl
+output "id" {
+  description = "The ID of the created resource"
+  value       = google_resource.main.id
+}
+```
+
+## Relationship with terraform-module-library
+
+- Use **terraform-module-creator** (this skill) for the initial file creation and setup.
+- Use **terraform-module-library** for design patterns, best practices, and internal code logic.
diff --git a/.agent/skills/terraform-module-library/SKILL.md b/.agent/skills/terraform-module-library/SKILL.md
@@ -0,0 +1,71 @@
+---
+name: terraform-module-library
+description: Expert guidance for creating, managing, and using Terraform modules. Use this skill when the user wants to create reusable infrastructure components, standardize Terraform patterns, or needs help with module structure and best practices for AWS, GCP, or Azure.
+---
+
+# Terraform Module Library
+
+This skill provides standardized patterns and best practices for creating and using Terraform modules.
+
+## When to Use
+
+- Creating new reusable Terraform modules
+- Refactoring existing Terraform code into modules
+- Standardizing infrastructure patterns across the project
+- implement specific infrastructure components (VPC, GKE, RDS, etc.) using best practices
+
+## Module Structure
+
+Standard directory structure for a Terraform module:
+
+```
+module-name/
+├── main.tf       # Primary logic and resources
+├── variables.tf  # Input variable definitions
+├── outputs.tf    # Output value definitions
+├── versions.tf   # Provider and Terraform version constraints
+├── README.md     # Module documentation
+└── examples/     # Example configurations
+    └── complete/ # Full example usage
+```
+
+## Best Practices
+
+### Cloud Providers
+
+#### Google Cloud Platform (GCP)
+- Use `google-beta` provider for beta features if necessary, but prefer GA.
+- Follow Google's "Cloud Foundation Toolkit" patterns where applicable.
+- Resource naming: Use standardized prefixes/suffixes (e.g., `gcp-vpc-{env}`).
+
+#### AWS
+- Use standard `aws` provider resources.
+- Tag all resources with consistent tags (Owner, Environment, Project).
+
+### General
+- **Version Pinning**: Always pin provider and Terraform versions in `versions.tf`.
+- **Variables**: Include `description` and `type` for all variables. Use `validation` blocks for constraints.
+- **Outputs**: Document all outputs.
+- **State**: Do not include backend configuration in modules; state is managed by the root configuration.
+
+## Common Module Patterns
+
+### Private Module Registry
+If using a private registry, ensure source paths follow the registry's convention.
+
+### Local Modules
+For local development or monorepos:
+```hcl
+module "network" {
+  source = "./modules/network"
+  # ...
+}
+```
+
+## Review Checklist
+
+1. [ ] Does the module have a `README.md` with input/output documentation?
+2. [ ] Are all variables typed and described?
+3. [ ] Are resource names deterministic or correctly scoped?
+4. [ ] Does it include `examples/`?
+5. [ ] Is `terraform_remote_state` avoided within the module?
diff --git a/.agent/skills/terraform-state-manager/SKILL.md b/.agent/skills/terraform-state-manager/SKILL.md
@@ -0,0 +1,79 @@
+---
+name: terraform-state-manager
+description: Manages Terraform state operations such as importing, moving, and removing resources. Use this skill when the user needs to refactor Terraform state, import existing infrastructure, fixing state drift, or migrate backends without destroying resources.
+---
+
+# Terraform State Manager
+
+This skill guides you through safe Terraform state manipulation operations.
+
+## When to Use
+
+- Importing existing cloud resources into Terraform management (`terraform import`)
+- Renaming resources or moving them into/out of modules (`terraform state mv`)
+- Removing resources from Terraform control without destroying them (`terraform state rm`)
+- Migrating state between backends (e.g., local to GCS/S3)
+- Fixing state locks or corruption
+
+## Critical Safety Rules
+
+> [!IMPORTANT]
+> **ALWAYS** follow these rules to prevent data loss or service downtime.
+
+1.  **Backup First**: Create a backup of your state file (`.tfstate`) before ANY operation.
+    ```bash
+    terraform state pull > backup.tfstate
+    ```
+2.  **Plan After**: Run `terraform plan` immediately after any state change to verify the result is a "no-op" (no changes detected) or matches expectation.
+3.  **One by One**: Perform operations incrementally rather than in bulk.
+4.  **Communicate**: Ensure no one else is running Terraform during maintenance.
+
+## Common Operations
+
+### 1. Importing Resources
+
+Use when you have a resource in the cloud but not in Terraform state.
+
+1.  **Write Config**: Create the `resource` block in your `.tf` files.
+2.  **Import**:
+    ```bash
+    terraform import <resource_address> <cloud_id>
+    # Example: terraform import google_storage_bucket.my_bucket my-project-bucket-name
+    ```
+3.  **Verify**: Run `terraform plan`. It should be empty or show only minor metadata updates.
+
+### 2. Moving Resources (Refactoring)
+
+Use when renaming resources or moving them into modules.
+
+```bash
+terraform state mv <source_address> <destination_address>
+# Example: terraform state mv google_storage_bucket.old_name module.storage.google_storage_bucket.new_name
+```
+
+### 3. Removing Resources
+
+Use when you want to stop managing a resource with Terraform but keep it running.
+
+```bash
+terraform state rm <resource_address>
+```
+
+### 4. Migrating Backend
+
+Use to change where state is stored.
+
+1.  **Update Config**: Change the `backend` block in `versions.tf` or `backend.tf`.
+2.  **Migrate**:
+    ```bash
+    terraform init -migrate-state
+    ```
+    Answer "yes" to copy the state to the new location.
+
+## Troubleshooting
+
+- **State Lock**: If a process crashed and left a lock:
+    ```bash
+    terraform force-unlock <LOCK_ID>
+    ```
+    *Warning: Be absolutely sure no other process is running.*
diff --git a/.agent/skills/ui-ux-pro-max/SKILL.md b/.agent/skills/ui-ux-pro-max/SKILL.md
@@ -0,0 +1,42 @@
+---
+name: ui-ux-pro-max
+description: Advanced design intelligence for professional UI/UX. Use for implementing modern design patterns (Glassmorphism, Bento Grid), ensuring accessibility, and generating tailored design systems for web and mobile.
+---
+
+# UI/UX Pro Max
+
+This skill provides professional-grade UI/UX design guidance, focusing on modern aesthetics, accessibility, and consistency.
+
+## Capabilities
+
+### 1. Design System Generation
+Can generate a complete design system including:
+- **Colors**: Primary, secondary, semantic, and neutral palettes (OKLCH/HSL).
+- **Typography**: Font pairings, scales, and line heights.
+- **Spacing**: Consistent spacing grids (4px/8px rule).
+- **Components**: Variations for buttons, inputs, cards, etc.
+
+### 2. Design Patterns
+- **Glassmorphism**: Backdrop filters, transluscent layers.
+- **Bento Grid**: Grid-based layouts for dashboards and landing pages.
+- **Neumorphism**: Soft UI shadows (use sparingly).
+- **Dark Mode**: High contrast, desaturated colors for eye comfort.
+
+### 3. Review & Refactor
+- Check for accessibility (WCAG contrast ratios).
+- Identify "generic" designs and suggest premium alternatives.
+- Validate responsive behavior across devices.
+
+## Rules of Thumb
+
+- **Whitespace**: More is usually better. Give content room to breathe.
+- **Consistency**: Use variables for everything (colors, spacing, radius).
+- **Feedback**: Every interaction (hover, click, focus) needs visual feedback.
+- **Motion**: Use subtle micro-animations (200-300ms) to make the UI feel alive.
+
+## When to Use
+
+- "Make this page look more premium."
+- "Design a dashboard for this data."
+- "Improve the UX of this form."
+- "Create a dark mode theme."
diff --git a/.agent/skills/webf-native-ui-dev/SKILL.md b/.agent/skills/webf-native-ui-dev/SKILL.md
@@ -0,0 +1,64 @@
+---
+name: webf-native-ui-dev
+description: Develop custom native UI libraries based on Flutter widgets for WebF. Create reusable component libraries that wrap Flutter widgets as web-accessible custom elements.
+---
+
+# WebF Native UI Dev
+
+This skill guides the development of custom native UI components for **WebF** (Web on Flutter). It bridges Flutter widgets to standard HTML custom elements.
+
+## Concept
+
+WebF allows you to render HTML/CSS using Flutter's rendering engine. This skill helps you expose complex Flutter widgets as `<custom-element>` tags usable in HTML.
+
+## Workflow
+
+1.  **Create Flutter Widget**: Build the widget using standard Flutter code.
+2.  **Define Element Class**: Create a class extending `WidgetElement`.
+3.  **Register Custom Element**: Use `defineCustomElement` to map the tag name to the class.
+
+## Example
+
+```dart
+import 'package:webf/webf.dart';
+import 'package:flutter/material.dart';
+
+// 1. Define the Element
+class FlutterButtonElement extends WidgetElement {
+  FlutterButtonElement(BindingContext? context) : super(context);
+
+  @override
+  Widget build(BuildContext context, List<Widget> children) {
+    return ElevatedButton(
+      onPressed: () {
+        // Dispatch custom event to JS
+        dispatchEvent(Event('click'));
+      },
+      child: Text(getAttribute('label') ?? 'Click Me'),
+    );
+  }
+}
+
+// 2. Register (usually in main.dart)
+void main() {
+  WebF.defineCustomElement('flutter-button', (context) => FlutterButtonElement(context));
+  runApp(MyApp());
+}
+```
+
+## Usage in HTML
+
+```html
+<flutter-button label="Submit Order" id="btn"></flutter-button>
+<script>
+  document.getElementById('btn').addEventListener('click', () => {
+    console.log('Button clicked via Flutter!');
+  });
+</script>
+```
+
+## Best Practices
+
+- **Attributes**: Map HTML attributes to Widget properties.
+- **Events**: Dispatch standard DOM events from Flutter user interactions.
+- **Performance**: Avoid heavy computations in the `build` method; use state management.
PATCH

echo "Gold patch applied."
