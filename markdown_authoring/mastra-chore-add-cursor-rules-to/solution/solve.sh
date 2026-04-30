#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mastra

# Idempotency guard
if grep -qF "`packages/playground-ui` provides shared UI and business logic primitives for mu" "packages/playground-ui/.cursor/rules/frontend.mdc" && grep -qF "`packages/playground-ui` provides shared UI and business logic primitives for mu" "packages/playground-ui/CLAUDE.md" && grep -qF "`packages/playground` is a local development studio built with React Router that" "packages/playground/.cursor/rules/frontend.mdc" && grep -qF "`packages/playground` is a local development studio built with React Router that" "packages/playground/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/playground-ui/.cursor/rules/frontend.mdc b/packages/playground-ui/.cursor/rules/frontend.mdc
@@ -0,0 +1,171 @@
+---
+globs: packages/playground-ui/src/**
+alwaysApply: false
+---
+
+# Frontend Component Standards
+
+Standards and conventions for building components in `packages/playground-ui`.
+
+---
+
+## Package Architecture
+
+### Scope
+
+`packages/playground-ui` provides shared UI and business logic primitives for multiple studio environments.
+
+### Target Environments
+
+- **Local Studio**: Development server using React Router
+- **Cloud Studio**: Production SaaS using Next.js
+
+### Responsibilities
+
+- **UI Components**: Reusable presentational components
+- **Business Hooks**: Data-fetching and state management (`src/domains`)
+  - Examples: `useAgents()`, `useWorkflows()`
+- **Business Components**: Domain-specific components (`src/domains`)
+  - Examples: `<AgentsTable>`, `<AgentInformation>`
+
+---
+
+## Styling Guidelines
+
+### Tailwind CSS (v3.x)
+
+- Use Tailwind for all styling
+- **REQUIRED**: Use design tokens from `src/ds/tokens/index.ts`
+- **FORBIDDEN**: Arbitrary values (e.g., `bg-[#1A1A1A]`) unless explicitly requested
+
+#### Examples
+
+```tsx
+// ❌ Bad
+<div className="bg-[#1A1A1A] shadow-[0_4px_12px_rgba(0,0,0,0.5)]" />
+
+// ✅ Good
+<div className="bg-surface4 shadow-lg" />
+```
+
+### Complex Styles
+
+- Prefer Tailwind utilities over custom CSS files for shadows, gradients, etc.
+- Only use CSS files when Tailwind cannot express the style
+
+---
+
+## Coding Conventions
+
+### Naming
+
+- **Components**: PascalCase (e.g., `EntryList`)
+- **Files**: kebab-case (e.g., `entry-list.tsx`)
+
+### Exports
+
+- Use **named exports** only
+- Avoid default exports
+
+```tsx
+// ✅ Good
+export function EntryList() { ... }
+
+// ❌ Bad
+export default function EntryList() { ... }
+```
+
+### Reusability
+
+- Before creating a component, verify it doesn't already exist
+- Reuse existing components instead of duplicating
+
+---
+
+## React Code Style
+
+### Data Fetching
+
+- **REQUIRED**: Use TanStack Query for all data fetching hooks
+- **REQUIRED**: Use `useMastraClient` SDK for API calls
+- **FORBIDDEN**: Direct `fetch()` calls
+
+```tsx
+// ✅ Good
+import { useMastraClient } from '.@mastra/react';
+import { useQuery } from '@tanstack/react-query';
+
+export function useAgents() {
+  const client = useMastraClient();
+  return useQuery({
+    queryKey: ['agents'],
+    queryFn: () => client.getAgents(),
+  });
+}
+
+// ❌ Bad
+export function useAgents() {
+  const [data, setData] = useState(null);
+  useEffect(() => {
+    fetch('/api/agents')
+      .then(r => r.json())
+      .then(setData);
+  }, []);
+  return data;
+}
+```
+
+### Type Definitions
+
+- **REQUIRED**: Export explicit prop types separately
+- Keep type definitions alongside components
+
+```tsx
+// ✅ Good
+export type AppProps = { a: number; b: number };
+export function App({ a, b }: AppProps) {
+  return <div>{a + b}</div>;
+}
+
+// ❌ Bad
+export function App({ a, b }: { a: number; b: number }) {
+  return <div>{a + b}</div>;
+}
+```
+
+### State Management
+
+- Prefer derived values over `useState` + `useEffect`
+- Minimize `useEffect` usage
+- Calculate values directly when possible
+
+```tsx
+// ✅ Good
+export type AppProps = { a: number; b: number };
+export function App({ a, b }: AppProps) {
+  return <div>{a + b}</div>;
+}
+
+// ❌ Bad
+export type AppProps = { a: number; b: number };
+export function App({ a, b }: AppProps) {
+  const [result, setResult] = useState<number>(0);
+
+  useEffect(() => {
+    setResult(a + b);
+  }, [a, b]);
+
+  return <div>{result}</div>;
+}
+```
+
+---
+
+## Key Principles
+
+- All components must work in both React Router and Next.js
+- Keep business logic in `src/domain` sub-folders
+- Maintain environment-agnostic design
+- Prioritize design system tokens for consistency
+- Minimize side effects and state management
+- Use TanStack Query for all server state
diff --git a/packages/playground-ui/CLAUDE.md b/packages/playground-ui/CLAUDE.md
@@ -0,0 +1,166 @@
+# Frontend Component Standards
+
+Standards and conventions for building components in `packages/playground-ui`.
+
+---
+
+## Package Architecture
+
+### Scope
+
+`packages/playground-ui` provides shared UI and business logic primitives for multiple studio environments.
+
+### Target Environments
+
+- **Local Studio**: Development server using React Router
+- **Cloud Studio**: Production SaaS using Next.js
+
+### Responsibilities
+
+- **UI Components**: Reusable presentational components
+- **Business Hooks**: Data-fetching and state management (`src/domains`)
+  - Examples: `useAgents()`, `useWorkflows()`
+- **Business Components**: Domain-specific components (`src/domains`)
+  - Examples: `<AgentsTable>`, `<AgentInformation>`
+
+---
+
+## Styling Guidelines
+
+### Tailwind CSS (v3.x)
+
+- Use Tailwind for all styling
+- **REQUIRED**: Use design tokens from `src/ds/tokens/index.ts`
+- **FORBIDDEN**: Arbitrary values (e.g., `bg-[#1A1A1A]`) unless explicitly requested
+
+#### Examples
+
+```tsx
+// ❌ Bad
+<div className="bg-[#1A1A1A] shadow-[0_4px_12px_rgba(0,0,0,0.5)]" />
+
+// ✅ Good
+<div className="bg-surface4 shadow-lg" />
+```
+
+### Complex Styles
+
+- Prefer Tailwind utilities over custom CSS files for shadows, gradients, etc.
+- Only use CSS files when Tailwind cannot express the style
+
+---
+
+## Coding Conventions
+
+### Naming
+
+- **Components**: PascalCase (e.g., `EntryList`)
+- **Files**: kebab-case (e.g., `entry-list.tsx`)
+
+### Exports
+
+- Use **named exports** only
+- Avoid default exports
+
+```tsx
+// ✅ Good
+export function EntryList() { ... }
+
+// ❌ Bad
+export default function EntryList() { ... }
+```
+
+### Reusability
+
+- Before creating a component, verify it doesn't already exist
+- Reuse existing components instead of duplicating
+
+---
+
+## React Code Style
+
+### Data Fetching
+
+- **REQUIRED**: Use TanStack Query for all data fetching hooks
+- **REQUIRED**: Use `useMastraClient` SDK for API calls
+- **FORBIDDEN**: Direct `fetch()` calls
+
+```tsx
+// ✅ Good
+import { useMastraClient } from '.@mastra/react';
+import { useQuery } from '@tanstack/react-query';
+
+export function useAgents() {
+  const client = useMastraClient();
+  return useQuery({
+    queryKey: ['agents'],
+    queryFn: () => client.getAgents(),
+  });
+}
+
+// ❌ Bad
+export function useAgents() {
+  const [data, setData] = useState(null);
+  useEffect(() => {
+    fetch('/api/agents')
+      .then(r => r.json())
+      .then(setData);
+  }, []);
+  return data;
+}
+```
+
+### Type Definitions
+
+- **REQUIRED**: Export explicit prop types separately
+- Keep type definitions alongside components
+
+```tsx
+// ✅ Good
+export type AppProps = { a: number; b: number };
+export function App({ a, b }: AppProps) {
+  return <div>{a + b}</div>;
+}
+
+// ❌ Bad
+export function App({ a, b }: { a: number; b: number }) {
+  return <div>{a + b}</div>;
+}
+```
+
+### State Management
+
+- Prefer derived values over `useState` + `useEffect`
+- Minimize `useEffect` usage
+- Calculate values directly when possible
+
+```tsx
+// ✅ Good
+export type AppProps = { a: number; b: number };
+export function App({ a, b }: AppProps) {
+  return <div>{a + b}</div>;
+}
+
+// ❌ Bad
+export type AppProps = { a: number; b: number };
+export function App({ a, b }: AppProps) {
+  const [result, setResult] = useState<number>(0);
+
+  useEffect(() => {
+    setResult(a + b);
+  }, [a, b]);
+
+  return <div>{result}</div>;
+}
+```
+
+---
+
+## Key Principles
+
+- All components must work in both React Router and Next.js
+- Keep business logic in `src/domain` sub-folders
+- Maintain environment-agnostic design
+- Prioritize design system tokens for consistency
+- Minimize side effects and state management
+- Use TanStack Query for all server state
diff --git a/packages/playground/.cursor/rules/frontend.mdc b/packages/playground/.cursor/rules/frontend.mdc
@@ -0,0 +1,165 @@
+---
+globs: packages/playground/src/**
+alwaysApply: false
+---
+
+# Local Studio Standards
+
+Standards and conventions for building the local studio in `packages/playground`.
+
+---
+
+## Package Architecture
+
+### Scope
+
+`packages/playground` is a local development studio built with React Router that composes primitives from `packages/playground-ui`.
+
+### Responsibilities
+
+- **Route Configuration**: Define React Router routes and pages
+- **Component Composition**: Assemble pages using `packages/playground-ui` primitives
+- **FORBIDDEN**: Creating new UI components, layouts, or data-fetching logic
+
+### Architecture Principle
+
+This package is a **thin composition layer** only. All reusable logic must live in `packages/playground-ui`.
+
+---
+
+## Component Composition Pattern
+
+Pages should compose high-level components from `packages/playground-ui` with minimal custom logic.
+
+### Examples
+
+```tsx
+// ✅ Good - Compose existing components
+import { useParams } from 'react-router';
+import { AgentsTable, AgentInformation } from '@mastra/playground-ui';
+
+export function AgentsPage() {
+  const { agentId } = useParams();
+
+  return (
+    <div className="grid grid-cols-2">
+      <AgentsTable agentId={agentId} />
+      <AgentInformation agentId={agentId} />
+    </div>
+  );
+}
+```
+
+```tsx
+// ❌ Bad - Reimplementing UI and data fetching
+import { useParams } from 'react-router';
+import { useAgent, useAgents } from '@mastra/playground-ui';
+
+export function AgentsPage() {
+  const { agentId } = useParams();
+  const { data: agent, isLoading } = useAgent(agentId);
+  const { data: agents, isLoading: isLoadingAgents } = useAgents();
+
+  if (isLoading || isLoadingAgents) return <div>Loading...</div>;
+
+  return (
+    <div className="grid grid-cols-2">
+      <div>Agent name: {agent.name}</div>
+      <ul>
+        {agents.map(item => (
+          <li key={item.id}>{item.name}</li>
+        ))}
+      </ul>
+    </div>
+  );
+}
+```
+
+---
+
+## Coding Conventions
+
+### Naming
+
+- **Components**: PascalCase (e.g., `AgentsPage`)
+- **Files**: kebab-case (e.g., `agents-page.tsx`)
+
+### Exports
+
+- Use **named exports** only
+- Avoid default exports
+
+```tsx
+// ✅ Good
+export function AgentsPage() { ... }
+
+// ❌ Bad
+export default function AgentsPage() { ... }
+```
+
+### Reusability
+
+- Before creating a component, check if it exists in `packages/playground-ui`
+- If a component doesn't exist in `playground-ui`, create it there first
+
+---
+
+## React Code Style
+
+### Data Fetching
+
+- **FORBIDDEN**: Data fetching in this package
+- All hooks must be imported from `packages/playground-ui`
+
+### Type Definitions
+
+- **REQUIRED**: Export explicit prop types separately
+
+```tsx
+// ✅ Good
+export type AgentsPageProps = { initialTab?: string };
+export function AgentsPage({ initialTab }: AgentsPageProps) {
+  return <div>{initialTab}</div>;
+}
+
+// ❌ Bad
+export function AgentsPage({ initialTab }: { initialTab?: string }) {
+  return <div>{initialTab}</div>;
+}
+```
+
+### State Management
+
+- Prefer derived values over `useState` + `useEffect`
+- Minimize `useEffect` usage
+- Calculate values directly when possible
+
+```tsx
+// ✅ Good
+export type AppProps = { a: number; b: number };
+export function App({ a, b }: AppProps) {
+  return <div>{a + b}</div>;
+}
+
+// ❌ Bad
+export type AppProps = { a: number; b: number };
+export function App({ a, b }: AppProps) {
+  const [result, setResult] = useState<number>(0);
+
+  useEffect(() => {
+    setResult(a + b);
+  }, [a, b]);
+
+  return <div>{result}</div>;
+}
+```
+
+---
+
+## Key Principles
+
+- This package is **composition only** - no business logic
+- All UI components must come from `packages/playground-ui`
+- All data-fetching hooks must come from `packages/playground-ui`
+- Pages should be thin wrappers around `playground-ui` components
+- When in doubt, add functionality to `playground-ui` instead
diff --git a/packages/playground/CLAUDE.md b/packages/playground/CLAUDE.md
@@ -0,0 +1,162 @@
+
+
+# Local Studio Standards
+
+Standards and conventions for building the local studio in `packages/playground`.
+
+---
+
+## Package Architecture
+
+### Scope
+
+`packages/playground` is a local development studio built with React Router that composes primitives from `packages/playground-ui`.
+
+### Responsibilities
+
+- **Route Configuration**: Define React Router routes and pages
+- **Component Composition**: Assemble pages using `packages/playground-ui` primitives
+- **FORBIDDEN**: Creating new UI components, layouts, or data-fetching logic
+
+### Architecture Principle
+
+This package is a **thin composition layer** only. All reusable logic must live in `packages/playground-ui`.
+
+---
+
+## Component Composition Pattern
+
+Pages should compose high-level components from `packages/playground-ui` with minimal custom logic.
+
+### Examples
+
+```tsx
+// ✅ Good - Compose existing components
+import { useParams } from 'react-router';
+import { AgentsTable, AgentInformation } from '@mastra/playground-ui';
+
+export function AgentsPage() {
+  const { agentId } = useParams();
+
+  return (
+    <div className="grid grid-cols-2">
+      <AgentsTable agentId={agentId} />
+      <AgentInformation agentId={agentId} />
+    </div>
+  );
+}
+```
+
+```tsx
+// ❌ Bad - Reimplementing UI and data fetching
+import { useParams } from 'react-router';
+import { useAgent, useAgents } from '@mastra/playground-ui';
+
+export function AgentsPage() {
+  const { agentId } = useParams();
+  const { data: agent, isLoading } = useAgent(agentId);
+  const { data: agents, isLoading: isLoadingAgents } = useAgents();
+
+  if (isLoading || isLoadingAgents) return <div>Loading...</div>;
+
+  return (
+    <div className="grid grid-cols-2">
+      <div>Agent name: {agent.name}</div>
+      <ul>
+        {agents.map(item => (
+          <li key={item.id}>{item.name}</li>
+        ))}
+      </ul>
+    </div>
+  );
+}
+```
+
+---
+
+## Coding Conventions
+
+### Naming
+
+- **Components**: PascalCase (e.g., `AgentsPage`)
+- **Files**: kebab-case (e.g., `agents-page.tsx`)
+
+### Exports
+
+- Use **named exports** only
+- Avoid default exports
+
+```tsx
+// ✅ Good
+export function AgentsPage() { ... }
+
+// ❌ Bad
+export default function AgentsPage() { ... }
+```
+
+### Reusability
+
+- Before creating a component, check if it exists in `packages/playground-ui`
+- If a component doesn't exist in `playground-ui`, create it there first
+
+---
+
+## React Code Style
+
+### Data Fetching
+
+- **FORBIDDEN**: Data fetching in this package
+- All hooks must be imported from `packages/playground-ui`
+
+### Type Definitions
+
+- **REQUIRED**: Export explicit prop types separately
+
+```tsx
+// ✅ Good
+export type AgentsPageProps = { initialTab?: string };
+export function AgentsPage({ initialTab }: AgentsPageProps) {
+  return <div>{initialTab}</div>;
+}
+
+// ❌ Bad
+export function AgentsPage({ initialTab }: { initialTab?: string }) {
+  return <div>{initialTab}</div>;
+}
+```
+
+### State Management
+
+- Prefer derived values over `useState` + `useEffect`
+- Minimize `useEffect` usage
+- Calculate values directly when possible
+
+```tsx
+// ✅ Good
+export type AppProps = { a: number; b: number };
+export function App({ a, b }: AppProps) {
+  return <div>{a + b}</div>;
+}
+
+// ❌ Bad
+export type AppProps = { a: number; b: number };
+export function App({ a, b }: AppProps) {
+  const [result, setResult] = useState<number>(0);
+
+  useEffect(() => {
+    setResult(a + b);
+  }, [a, b]);
+
+  return <div>{result}</div>;
+}
+```
+
+---
+
+## Key Principles
+
+- This package is **composition only** - no business logic
+- All UI components must come from `packages/playground-ui`
+- All data-fetching hooks must come from `packages/playground-ui`
+- Pages should be thin wrappers around `playground-ui` components
+- When in doubt, add functionality to `playground-ui` instead
PATCH

echo "Gold patch applied."
