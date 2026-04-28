#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotency guard
if grep -qF "description: Use when working with Payload CMS projects, payload.config.ts, coll" ".claude/skills/payload-cms/SKILL.md" && grep -qF "Advanced access control patterns including context-aware access, time-based rest" ".claude/skills/payload-cms/reference/ACCESS-CONTROL-ADVANCED.md" && grep -qF "For advanced access control patterns including context-aware access, time-based " ".claude/skills/payload-cms/reference/ACCESS-CONTROL.md" && grep -qF "**Critical**: When performing nested operations in hooks, always pass `req` to m" ".claude/skills/payload-cms/reference/ADAPTERS.md" && grep -qF "- **[All Commonly-Used Types](https://github.com/payloadcms/payload/blob/main/pa" ".claude/skills/payload-cms/reference/ADVANCED.md" && grep -qF "Payload maintains version history and supports draft/publish workflows." ".claude/skills/payload-cms/reference/COLLECTIONS.md" && grep -qF "Join fields create reverse relationships, allowing you to access related documen" ".claude/skills/payload-cms/reference/FIELDS.md" && grep -qF "- Pass `req` to nested operations for transaction safety (see [ADAPTERS.md#threa" ".claude/skills/payload-cms/reference/HOOKS.md" && grep -qF "**Important**: Local API bypasses access control by default (`overrideAccess: tr" ".claude/skills/payload-cms/reference/QUERIES.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/payload-cms/SKILL.md b/.claude/skills/payload-cms/SKILL.md
@@ -0,0 +1,212 @@
+---
+name: payload-cms
+description: Use when working with Payload CMS projects, payload.config.ts, collections, fields, hooks, access control, or Payload API. Provides TypeScript patterns and examples for Payload 3.x development.
+version: '2.0.0'
+payload-version: '3.x'
+last-updated: '2025-01-27'
+---
+
+# Payload CMS Application Development
+
+Payload 3.x is a Next.js native CMS with TypeScript-first architecture, providing admin panel, database management, REST/GraphQL APIs, authentication, and file storage.
+
+## Quick Reference
+
+| Task                     | Solution                                  | Details                                                                                                                          |
+| ------------------------ | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
+| Auto-generate slugs      | `slugField()`                             | [FIELDS.md#slug-field-helper](reference/FIELDS.md#slug-field-helper)                                                             |
+| Restrict content by user | Access control with query                 | [ACCESS-CONTROL.md#row-level-security-with-complex-queries](reference/ACCESS-CONTROL.md#row-level-security-with-complex-queries) |
+| Local API user ops       | `user` + `overrideAccess: false`          | [QUERIES.md#access-control-in-local-api](reference/QUERIES.md#access-control-in-local-api)                                       |
+| Draft/publish workflow   | `versions: { drafts: true }`              | [COLLECTIONS.md#versioning--drafts](reference/COLLECTIONS.md#versioning--drafts)                                                 |
+| Computed fields          | `virtual: true` with afterRead            | [FIELDS.md#virtual-fields](reference/FIELDS.md#virtual-fields)                                                                   |
+| Conditional fields       | `admin.condition`                         | [FIELDS.md#conditional-fields](reference/FIELDS.md#conditional-fields)                                                           |
+| Geospatial queries       | `point` field with `near`/`within`        | [FIELDS.md#point-geolocation](reference/FIELDS.md#point-geolocation)                                                             |
+| Reverse relationships    | `join` field type                         | [FIELDS.md#join-fields](reference/FIELDS.md#join-fields)                                                                         |
+| Next.js revalidation     | Context control in afterChange            | [HOOKS.md#nextjs-revalidation-with-context-control](reference/HOOKS.md#nextjs-revalidation-with-context-control)                 |
+| Query by relationship    | Nested property syntax                    | [QUERIES.md#nested-properties](reference/QUERIES.md#nested-properties)                                                           |
+| Complex queries          | AND/OR logic                              | [QUERIES.md#andor-logic](reference/QUERIES.md#andor-logic)                                                                       |
+| Transactions             | Pass `req` to operations                  | [ADAPTERS.md#threading-req-through-operations](reference/ADAPTERS.md#threading-req-through-operations)                           |
+| Background jobs          | Jobs queue with tasks                     | [ADVANCED.md#jobs-queue](reference/ADVANCED.md#jobs-queue)                                                                       |
+| Custom API routes        | Collection/root endpoints                 | [ADVANCED.md#custom-endpoints](reference/ADVANCED.md#custom-endpoints)                                                           |
+| Cloud storage            | Storage adapter plugins                   | [ADAPTERS.md#storage-adapters](reference/ADAPTERS.md#storage-adapters)                                                           |
+| Multi-language           | `localization` config + `localized: true` | [ADVANCED.md#localization](reference/ADVANCED.md#localization)                                                                   |
+
+## Quick Start
+
+```bash
+npx create-payload-app@latest my-app
+cd my-app
+pnpm dev
+```
+
+### Minimal Config
+
+```ts
+import { buildConfig } from 'payload'
+import { mongooseAdapter } from '@payloadcms/db-mongodb'
+import { lexicalEditor } from '@payloadcms/richtext-lexical'
+import path from 'path'
+import { fileURLToPath } from 'url'
+
+const filename = fileURLToPath(import.meta.url)
+const dirname = path.dirname(filename)
+
+export default buildConfig({
+  admin: {
+    user: 'users',
+    importMap: {
+      baseDir: path.resolve(dirname),
+    },
+  },
+  collections: [Users, Media],
+  editor: lexicalEditor(),
+  secret: process.env.PAYLOAD_SECRET,
+  typescript: {
+    outputFile: path.resolve(dirname, 'payload-types.ts'),
+  },
+  db: mongooseAdapter({
+    url: process.env.DATABASE_URI,
+  }),
+})
+```
+
+## Essential Patterns
+
+### Basic Collection
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  admin: {
+    useAsTitle: 'title',
+    defaultColumns: ['title', 'author', 'status', 'createdAt'],
+  },
+  fields: [
+    { name: 'title', type: 'text', required: true },
+    { name: 'slug', type: 'text', unique: true, index: true },
+    { name: 'content', type: 'richText' },
+    { name: 'author', type: 'relationship', relationTo: 'users' },
+  ],
+  timestamps: true,
+}
+```
+
+For more collection patterns (auth, upload, drafts, live preview), see [COLLECTIONS.md](reference/COLLECTIONS.md).
+
+### Common Fields
+
+```ts
+// Text field
+{ name: 'title', type: 'text', required: true }
+
+// Relationship
+{ name: 'author', type: 'relationship', relationTo: 'users', required: true }
+
+// Rich text
+{ name: 'content', type: 'richText', required: true }
+
+// Select
+{ name: 'status', type: 'select', options: ['draft', 'published'], defaultValue: 'draft' }
+
+// Upload
+{ name: 'image', type: 'upload', relationTo: 'media' }
+```
+
+For all field types (array, blocks, point, join, virtual, conditional, etc.), see [FIELDS.md](reference/FIELDS.md).
+
+### Hook Example
+
+```ts
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  hooks: {
+    beforeChange: [
+      async ({ data, operation }) => {
+        if (operation === 'create') {
+          data.slug = slugify(data.title)
+        }
+        return data
+      },
+    ],
+  },
+  fields: [{ name: 'title', type: 'text' }],
+}
+```
+
+For all hook patterns, see [HOOKS.md](reference/HOOKS.md). For access control, see [ACCESS-CONTROL.md](reference/ACCESS-CONTROL.md).
+
+### Query Example
+
+```ts
+// Local API
+const posts = await payload.find({
+  collection: 'posts',
+  where: {
+    status: { equals: 'published' },
+    'author.name': { contains: 'john' },
+  },
+  depth: 2,
+  limit: 10,
+  sort: '-createdAt',
+})
+```
+
+For all query operators and REST/GraphQL examples, see [QUERIES.md](reference/QUERIES.md).
+
+## Project Structure
+
+```txt
+src/
+├── app/
+│   ├── (frontend)/
+│   │   └── page.tsx
+│   └── (payload)/
+│       └── admin/[[...segments]]/page.tsx
+├── collections/
+│   ├── Posts.ts
+│   ├── Media.ts
+│   └── Users.ts
+├── globals/
+│   └── Header.ts
+├── components/
+│   └── CustomField.tsx
+├── hooks/
+│   └── slugify.ts
+└── payload.config.ts
+```
+
+## Type Generation
+
+```ts
+// payload.config.ts
+export default buildConfig({
+  typescript: {
+    outputFile: path.resolve(dirname, 'payload-types.ts'),
+  },
+  // ...
+})
+
+// Usage
+import type { Post, User } from '@/payload-types'
+```
+
+## Reference Documentation
+
+- **[FIELDS.md](reference/FIELDS.md)** - All field types, validation, admin options
+- **[COLLECTIONS.md](reference/COLLECTIONS.md)** - Collection configs, auth, upload, drafts, live preview
+- **[HOOKS.md](reference/HOOKS.md)** - Collection hooks, field hooks, context patterns
+- **[ACCESS-CONTROL.md](reference/ACCESS-CONTROL.md)** - Collection, field, global access control, RBAC, multi-tenant
+- **[ACCESS-CONTROL-ADVANCED.md](reference/ACCESS-CONTROL-ADVANCED.md)** - Context-aware, time-based, subscription-based access, factory functions, templates
+- **[QUERIES.md](reference/QUERIES.md)** - Query operators, Local/REST/GraphQL APIs
+- **[ADAPTERS.md](reference/ADAPTERS.md)** - Database, storage, email adapters, transactions
+- **[ADVANCED.md](reference/ADVANCED.md)** - Authentication, jobs, endpoints, components, plugins, localization
+
+## Resources
+
+- llms-full.txt: <https://payloadcms.com/llms-full.txt>
+- Docs: <https://payloadcms.com/docs>
+- GitHub: <https://github.com/payloadcms/payload>
+- Examples: <https://github.com/payloadcms/payload/tree/main/examples>
+- Templates: <https://github.com/payloadcms/payload/tree/main/templates>
diff --git a/.claude/skills/payload-cms/reference/ACCESS-CONTROL-ADVANCED.md b/.claude/skills/payload-cms/reference/ACCESS-CONTROL-ADVANCED.md
@@ -0,0 +1,704 @@
+# Payload CMS Access Control - Advanced Patterns
+
+Advanced access control patterns including context-aware access, time-based restrictions, factory functions, and production templates.
+
+## Context-Aware Access Patterns
+
+### Locale-Specific Access
+
+Control access based on user locale for internationalized content.
+
+```ts
+import type { Access } from 'payload'
+
+export const localeSpecificAccess: Access = ({ req: { user, locale } }) => {
+  // Authenticated users can access all locales
+  if (user) return true
+
+  // Public users can only access English content
+  if (locale === 'en') return true
+
+  return false
+}
+
+// Usage in collection
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  access: {
+    read: localeSpecificAccess,
+  },
+  fields: [{ name: 'title', type: 'text', localized: true }],
+}
+```
+
+**Source**: `docs/access-control/overview.mdx` (req.locale argument)
+
+### Device-Specific Access
+
+Restrict access based on device type or user agent.
+
+```ts
+import type { Access } from 'payload'
+
+export const mobileOnlyAccess: Access = ({ req: { headers } }) => {
+  const userAgent = headers?.get('user-agent') || ''
+  return /mobile|android|iphone/i.test(userAgent)
+}
+
+export const desktopOnlyAccess: Access = ({ req: { headers } }) => {
+  const userAgent = headers?.get('user-agent') || ''
+  return !/mobile|android|iphone/i.test(userAgent)
+}
+
+// Usage
+export const MobileContent: CollectionConfig = {
+  slug: 'mobile-content',
+  access: {
+    read: mobileOnlyAccess,
+  },
+  fields: [{ name: 'title', type: 'text' }],
+}
+```
+
+**Source**: Synthesized (headers pattern)
+
+### IP-Based Access
+
+Restrict access from specific IP addresses (requires middleware/proxy headers).
+
+```ts
+import type: Access } from 'payload'
+
+export const restrictedIpAccess = (allowedIps: string[]): Access => {
+  return ({ req: { headers } }) => {
+    const ip = headers?.get('x-forwarded-for') || headers?.get('x-real-ip')
+    return allowedIps.includes(ip || '')
+  }
+}
+
+// Usage
+const internalIps = ['192.168.1.0/24', '10.0.0.5']
+
+export const InternalDocs: CollectionConfig = {
+  slug: 'internal-docs',
+  access: {
+    read: restrictedIpAccess(internalIps),
+  },
+  fields: [{ name: 'content', type: 'richText' }],
+}
+```
+
+**Note**: Requires your server to pass IP address via headers (common with proxies/load balancers).
+
+**Source**: Synthesized (headers pattern)
+
+## Time-Based Access Patterns
+
+### Today's Records Only
+
+```ts
+import type { Access } from 'payload'
+
+export const todayOnlyAccess: Access = ({ req: { user } }) => {
+  if (!user) return false
+
+  const now = new Date()
+  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())
+  const endOfDay = new Date(startOfDay.getTime() + 24 * 60 * 60 * 1000)
+
+  return {
+    createdAt: {
+      greater_than_equal: startOfDay.toISOString(),
+      less_than: endOfDay.toISOString(),
+    },
+  }
+}
+```
+
+**Source**: `test/access-control/config.ts` (query constraint patterns)
+
+### Recent Records (Last N Days)
+
+```ts
+import type { Access } from 'payload'
+
+export const recentRecordsAccess = (days: number): Access => {
+  return ({ req: { user } }) => {
+    if (!user) return false
+    if (user.roles?.includes('admin')) return true
+
+    const cutoff = new Date()
+    cutoff.setDate(cutoff.getDate() - days)
+
+    return {
+      createdAt: {
+        greater_than_equal: cutoff.toISOString(),
+      },
+    }
+  }
+}
+
+// Usage: Users see only last 30 days, admins see all
+export const Logs: CollectionConfig = {
+  slug: 'logs',
+  access: {
+    read: recentRecordsAccess(30),
+  },
+  fields: [{ name: 'message', type: 'text' }],
+}
+```
+
+### Scheduled Content (Publish Date Range)
+
+```ts
+import type { Access } from 'payload'
+
+export const scheduledContentAccess: Access = ({ req: { user } }) => {
+  // Editors see all content
+  if (user?.roles?.includes('admin') || user?.roles?.includes('editor')) {
+    return true
+  }
+
+  const now = new Date().toISOString()
+
+  // Public sees only content within publish window
+  return {
+    and: [
+      { publishDate: { less_than_equal: now } },
+      {
+        or: [{ unpublishDate: { exists: false } }, { unpublishDate: { greater_than: now } }],
+      },
+    ],
+  }
+}
+```
+
+**Source**: Synthesized (query constraint + date patterns)
+
+## Subscription-Based Access
+
+### Active Subscription Required
+
+```ts
+import type { Access } from 'payload'
+
+export const activeSubscriptionAccess: Access = async ({ req: { user } }) => {
+  if (!user) return false
+  if (user.roles?.includes('admin')) return true
+
+  try {
+    const subscription = await req.payload.findByID({
+      collection: 'subscriptions',
+      id: user.subscriptionId,
+    })
+
+    return subscription?.status === 'active'
+  } catch {
+    return false
+  }
+}
+
+// Usage
+export const PremiumContent: CollectionConfig = {
+  slug: 'premium-content',
+  access: {
+    read: activeSubscriptionAccess,
+  },
+  fields: [{ name: 'title', type: 'text' }],
+}
+```
+
+### Subscription Tier-Based Access
+
+```ts
+import type { Access } from 'payload'
+
+export const tierBasedAccess = (requiredTier: string): Access => {
+  const tierHierarchy = ['free', 'basic', 'pro', 'enterprise']
+
+  return async ({ req: { user } }) => {
+    if (!user) return false
+    if (user.roles?.includes('admin')) return true
+
+    try {
+      const subscription = await req.payload.findByID({
+        collection: 'subscriptions',
+        id: user.subscriptionId,
+      })
+
+      if (subscription?.status !== 'active') return false
+
+      const userTierIndex = tierHierarchy.indexOf(subscription.tier)
+      const requiredTierIndex = tierHierarchy.indexOf(requiredTier)
+
+      return userTierIndex >= requiredTierIndex
+    } catch {
+      return false
+    }
+  }
+}
+
+// Usage
+export const EnterpriseFeatures: CollectionConfig = {
+  slug: 'enterprise-features',
+  access: {
+    read: tierBasedAccess('enterprise'),
+  },
+  fields: [{ name: 'feature', type: 'text' }],
+}
+```
+
+**Source**: Synthesized (async + cross-collection pattern)
+
+## Factory Functions
+
+Reusable functions that generate access control configurations.
+
+### createRoleBasedAccess
+
+Generate access control for specific roles.
+
+```ts
+import type { Access } from 'payload'
+
+export function createRoleBasedAccess(roles: string[]): Access {
+  return ({ req: { user } }) => {
+    if (!user) return false
+    return roles.some((role) => user.roles?.includes(role))
+  }
+}
+
+// Usage
+const adminOrEditor = createRoleBasedAccess(['admin', 'editor'])
+const moderatorAccess = createRoleBasedAccess(['admin', 'moderator'])
+
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  access: {
+    create: adminOrEditor,
+    update: adminOrEditor,
+    delete: moderatorAccess,
+  },
+  fields: [{ name: 'title', type: 'text' }],
+}
+```
+
+**Source**: `test/access-control/config.ts`
+
+### createOrgScopedAccess
+
+Generate organization-scoped access with optional admin bypass.
+
+```ts
+import type { Access } from 'payload'
+
+export function createOrgScopedAccess(allowAdmin = true): Access {
+  return ({ req: { user } }) => {
+    if (!user) return false
+    if (allowAdmin && user.roles?.includes('admin')) return true
+
+    return {
+      organizationId: { in: user.organizationIds || [] },
+    }
+  }
+}
+
+// Usage
+const orgScoped = createOrgScopedAccess() // Admins bypass
+const strictOrgScoped = createOrgScopedAccess(false) // Admins also scoped
+
+export const Projects: CollectionConfig = {
+  slug: 'projects',
+  access: {
+    read: orgScoped,
+    update: orgScoped,
+    delete: strictOrgScoped,
+  },
+  fields: [
+    { name: 'title', type: 'text' },
+    { name: 'organizationId', type: 'text', required: true },
+  ],
+}
+```
+
+**Source**: `test/access-control/config.ts`
+
+### createTeamBasedAccess
+
+Generate team-scoped access with configurable field name.
+
+```ts
+import type { Access } from 'payload'
+
+export function createTeamBasedAccess(teamField = 'teamId'): Access {
+  return ({ req: { user } }) => {
+    if (!user) return false
+    if (user.roles?.includes('admin')) return true
+
+    return {
+      [teamField]: { in: user.teamIds || [] },
+    }
+  }
+}
+
+// Usage with custom field name
+const projectTeamAccess = createTeamBasedAccess('projectTeam')
+
+export const Tasks: CollectionConfig = {
+  slug: 'tasks',
+  access: {
+    read: projectTeamAccess,
+    update: projectTeamAccess,
+  },
+  fields: [
+    { name: 'title', type: 'text' },
+    { name: 'projectTeam', type: 'text', required: true },
+  ],
+}
+```
+
+**Source**: Synthesized (org pattern variation)
+
+### createTimeLimitedAccess
+
+Generate access limited to records within specified days.
+
+```ts
+import type { Access } from 'payload'
+
+export function createTimeLimitedAccess(daysAccess: number): Access {
+  return ({ req: { user } }) => {
+    if (!user) return false
+    if (user.roles?.includes('admin')) return true
+
+    const cutoff = new Date()
+    cutoff.setDate(cutoff.getDate() - daysAccess)
+
+    return {
+      createdAt: {
+        greater_than_equal: cutoff.toISOString(),
+      },
+    }
+  }
+}
+
+// Usage: Users see 90 days, admins see all
+export const ActivityLogs: CollectionConfig = {
+  slug: 'activity-logs',
+  access: {
+    read: createTimeLimitedAccess(90),
+  },
+  fields: [{ name: 'action', type: 'text' }],
+}
+```
+
+**Source**: Synthesized (time + query pattern)
+
+## Configuration Templates
+
+Complete collection configurations for common scenarios.
+
+### Basic Authenticated Collection
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+export const BasicCollection: CollectionConfig = {
+  slug: 'basic-collection',
+  access: {
+    create: ({ req: { user } }) => Boolean(user),
+    read: ({ req: { user } }) => Boolean(user),
+    update: ({ req: { user } }) => Boolean(user),
+    delete: ({ req: { user } }) => Boolean(user),
+  },
+  fields: [
+    { name: 'title', type: 'text', required: true },
+    { name: 'content', type: 'richText' },
+  ],
+}
+```
+
+**Source**: `docs/access-control/collections.mdx`
+
+### Public + Authenticated Collection
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+export const PublicAuthCollection: CollectionConfig = {
+  slug: 'posts',
+  access: {
+    // Only admins/editors can create
+    create: ({ req: { user } }) => {
+      return user?.roles?.some((role) => ['admin', 'editor'].includes(role)) || false
+    },
+
+    // Authenticated users see all, public sees only published
+    read: ({ req: { user } }) => {
+      if (user) return true
+      return { _status: { equals: 'published' } }
+    },
+
+    // Only admins/editors can update
+    update: ({ req: { user } }) => {
+      return user?.roles?.some((role) => ['admin', 'editor'].includes(role)) || false
+    },
+
+    // Only admins can delete
+    delete: ({ req: { user } }) => {
+      return user?.roles?.includes('admin') || false
+    },
+  },
+  versions: {
+    drafts: true,
+  },
+  fields: [
+    { name: 'title', type: 'text', required: true },
+    { name: 'content', type: 'richText', required: true },
+    { name: 'author', type: 'relationship', relationTo: 'users' },
+  ],
+}
+```
+
+**Source**: `templates/website/src/collections/Posts/index.ts`
+
+### Multi-User/Self-Service Collection
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+export const SelfServiceCollection: CollectionConfig = {
+  slug: 'users',
+  auth: true,
+  access: {
+    // Admins can create users
+    create: ({ req: { user } }) => user?.roles?.includes('admin') || false,
+
+    // Anyone can read user profiles
+    read: () => true,
+
+    // Users can update self, admins can update anyone
+    update: ({ req: { user }, id }) => {
+      if (!user) return false
+      if (user.roles?.includes('admin')) return true
+      return user.id === id
+    },
+
+    // Only admins can delete
+    delete: ({ req: { user } }) => user?.roles?.includes('admin') || false,
+  },
+  fields: [
+    { name: 'name', type: 'text', required: true },
+    { name: 'email', type: 'email', required: true },
+    {
+      name: 'roles',
+      type: 'select',
+      hasMany: true,
+      options: ['admin', 'editor', 'user'],
+      access: {
+        // Only admins can read/update roles
+        read: ({ req: { user } }) => user?.roles?.includes('admin') || false,
+        update: ({ req: { user } }) => user?.roles?.includes('admin') || false,
+      },
+    },
+  ],
+}
+```
+
+**Source**: `templates/website/src/collections/Users/index.ts`
+
+## Debugging Tips
+
+### Log Access Check Execution
+
+```ts
+export const debugAccess: Access = ({ req: { user }, id }) => {
+  console.log('Access check:', {
+    userId: user?.id,
+    userRoles: user?.roles,
+    docId: id,
+    timestamp: new Date().toISOString(),
+  })
+  return true
+}
+```
+
+### Verify Arguments Availability
+
+```ts
+export const checkArgsAccess: Access = (args) => {
+  console.log('Available arguments:', {
+    hasReq: 'req' in args,
+    hasUser: args.req?.user ? 'yes' : 'no',
+    hasId: args.id ? 'provided' : 'undefined',
+    hasData: args.data ? 'provided' : 'undefined',
+  })
+  return true
+}
+```
+
+### Measure Async Operation Timing
+
+```ts
+export const timedAsyncAccess: Access = async ({ req }) => {
+  const start = Date.now()
+
+  const result = await fetch('https://auth-service.example.com/validate', {
+    headers: { userId: req.user?.id },
+  })
+
+  console.log(`Access check took ${Date.now() - start}ms`)
+
+  return result.ok
+}
+```
+
+### Test Access Without User
+
+```ts
+// In test/development
+const testAccess = await payload.find({
+  collection: 'posts',
+  overrideAccess: false, // Enforce access control
+  user: undefined, // Simulate no user
+})
+
+console.log('Public access result:', testAccess.docs.length)
+```
+
+**Source**: Synthesized (debugging best practices)
+
+## Performance Considerations
+
+### Async Operations Impact
+
+```ts
+// ❌ Slow: Multiple sequential async calls
+export const slowAccess: Access = async ({ req: { user } }) => {
+  const org = await req.payload.findByID({ collection: 'orgs', id: user.orgId })
+  const team = await req.payload.findByID({ collection: 'teams', id: user.teamId })
+  const subscription = await req.payload.findByID({ collection: 'subs', id: user.subId })
+
+  return org.active && team.active && subscription.active
+}
+
+// ✅ Fast: Use query constraints or cache in context
+export const fastAccess: Access = ({ req: { user, context } }) => {
+  // Cache expensive lookups
+  if (!context.orgStatus) {
+    context.orgStatus = checkOrgStatus(user.orgId)
+  }
+
+  return context.orgStatus
+}
+```
+
+### Query Constraint Optimization
+
+```ts
+// ❌ Avoid: Non-indexed fields in constraints
+export const slowQuery: Access = () => ({
+  'metadata.internalCode': { equals: 'ABC123' }, // Slow if not indexed
+})
+
+// ✅ Better: Use indexed fields
+export const fastQuery: Access = () => ({
+  status: { equals: 'active' }, // Indexed field
+  organizationId: { in: ['org1', 'org2'] }, // Indexed field
+})
+```
+
+### Field Access on Large Arrays
+
+```ts
+// ❌ Slow: Complex access on array fields
+const arrayField: ArrayField = {
+  name: 'items',
+  type: 'array',
+  fields: [
+    {
+      name: 'secretData',
+      type: 'text',
+      access: {
+        read: async ({ req }) => {
+          // Async call runs for EVERY array item
+          const result = await expensiveCheck()
+          return result
+        },
+      },
+    },
+  ],
+}
+
+// ✅ Fast: Simple checks or cache result
+const optimizedArrayField: ArrayField = {
+  name: 'items',
+  type: 'array',
+  fields: [
+    {
+      name: 'secretData',
+      type: 'text',
+      access: {
+        read: ({ req: { user }, context }) => {
+          // Cache once, reuse for all items
+          if (context.canReadSecret === undefined) {
+            context.canReadSecret = user?.roles?.includes('admin')
+          }
+          return context.canReadSecret
+        },
+      },
+    },
+  ],
+}
+```
+
+### Avoid N+1 Queries
+
+```ts
+// ❌ N+1 Problem: Query per access check
+export const n1Access: Access = async ({ req, id }) => {
+  // Runs for EACH document in list
+  const doc = await req.payload.findByID({ collection: 'docs', id })
+  return doc.isPublic
+}
+
+// ✅ Better: Use query constraint to filter at DB level
+export const efficientAccess: Access = () => {
+  return { isPublic: { equals: true } }
+}
+```
+
+**Performance Best Practices:**
+
+1. **Minimize Async Operations**: Use query constraints over async lookups when possible
+2. **Cache Expensive Checks**: Store results in `req.context` for reuse
+3. **Index Query Fields**: Ensure fields in query constraints are indexed
+4. **Avoid Complex Logic in Array Fields**: Simple boolean checks preferred
+5. **Use Query Constraints**: Let database filter rather than loading all records
+
+**Source**: Synthesized (operational best practices)
+
+## Enhanced Best Practices
+
+Comprehensive security and implementation guidelines:
+
+1. **Default Deny**: Start with restrictive access, gradually add permissions
+2. **Type Guards**: Use TypeScript for user type safety and better IDE support
+3. **Validate Data**: Never trust frontend-provided IDs or data
+4. **Async for Critical Checks**: Use async operations for important security decisions
+5. **Consistent Logic**: Apply same rules at field and collection levels
+6. **Test Edge Cases**: Test with no user, wrong user, admin user scenarios
+7. **Monitor Access**: Log failed access attempts for security review
+8. **Regular Audit**: Review access rules quarterly or after major changes
+9. **Cache Wisely**: Use `req.context` for expensive operations
+10. **Document Intent**: Add comments explaining complex access rules
+11. **Avoid Secrets in Client**: Never expose sensitive logic to client-side
+12. **Rate Limit External Calls**: Protect against DoS on external validation services
+13. **Handle Errors Gracefully**: Access functions should return `false` on error, not throw
+14. **Use Environment Vars**: Store configuration (IPs, API keys) in env vars
+15. **Test Local API**: Remember to set `overrideAccess: false` when testing
+16. **Consider Performance**: Measure impact of async operations on login time
+17. **Version Control**: Track access control changes in git history
+18. **Principle of Least Privilege**: Grant minimum access required for functionality
+
+**Sources**: `docs/access-control/*.mdx`, synthesized best practices
diff --git a/.claude/skills/payload-cms/reference/ACCESS-CONTROL.md b/.claude/skills/payload-cms/reference/ACCESS-CONTROL.md
@@ -0,0 +1,697 @@
+# Payload CMS Access Control Reference
+
+Complete reference for access control patterns across collections, fields, and globals.
+
+## At a Glance
+
+| Feature               | Scope                                                     | Returns                | Use Case                           |
+| --------------------- | --------------------------------------------------------- | ---------------------- | ---------------------------------- |
+| **Collection Access** | create, read, update, delete, admin, unlock, readVersions | boolean \| Where query | Document-level permissions         |
+| **Field Access**      | create, read, update                                      | boolean only           | Field-level visibility/editability |
+| **Global Access**     | read, update, readVersions                                | boolean \| Where query | Global document permissions        |
+
+## Three Layers of Access Control
+
+Payload provides three distinct access control layers:
+
+1. **Collection-Level**: Controls operations on entire documents (create, read, update, delete, admin, unlock, readVersions)
+2. **Field-Level**: Controls access to individual fields (create, read, update)
+3. **Global-Level**: Controls access to global documents (read, update, readVersions)
+
+## Return Value Types
+
+Access control functions can return:
+
+- **Boolean**: `true` (allow) or `false` (deny)
+- **Query Constraint**: `Where` object for row-level security (collection-level only)
+
+Field-level access does NOT support query constraints - only boolean returns.
+
+## Operation Decision Tree
+
+```txt
+User makes request
+    │
+    ├─ Collection access check
+    │   ├─ Returns false? → Deny entire operation
+    │   ├─ Returns true? → Continue
+    │   └─ Returns Where? → Apply query constraint
+    │
+    ├─ Field access check (if applicable)
+    │   ├─ Returns false? → Field omitted from result
+    │   └─ Returns true? → Include field
+    │
+    └─ Operation completed
+```
+
+## Collection Access Control
+
+### Basic Patterns
+
+```ts
+import type { CollectionConfig, Access } from 'payload'
+
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  access: {
+    // Boolean: Only authenticated users can create
+    create: ({ req: { user } }) => Boolean(user),
+
+    // Query constraint: Public sees published, users see all
+    read: ({ req: { user } }) => {
+      if (user) return true
+      return { status: { equals: 'published' } }
+    },
+
+    // User-specific: Admins or document owner
+    update: ({ req: { user }, id }) => {
+      if (user?.roles?.includes('admin')) return true
+      return { author: { equals: user?.id } }
+    },
+
+    // Async: Check related data
+    delete: async ({ req, id }) => {
+      const hasComments = await req.payload.count({
+        collection: 'comments',
+        where: { post: { equals: id } },
+      })
+      return hasComments === 0
+    },
+
+    // Admin panel visibility
+    admin: ({ req: { user } }) => {
+      return user?.roles?.includes('admin') || user?.roles?.includes('editor')
+    },
+  },
+  fields: [
+    { name: 'title', type: 'text' },
+    { name: 'status', type: 'select', options: ['draft', 'published'] },
+    { name: 'author', type: 'relationship', relationTo: 'users' },
+  ],
+}
+```
+
+### Role-Based Access Control (RBAC) Pattern
+
+Payload does NOT provide a roles system by default. The following is a commonly accepted pattern for implementing role-based access control in auth collections:
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+export const Users: CollectionConfig = {
+  slug: 'users',
+  auth: true,
+  fields: [
+    { name: 'name', type: 'text', required: true },
+    { name: 'email', type: 'email', required: true },
+    {
+      name: 'roles',
+      type: 'select',
+      hasMany: true,
+      options: ['admin', 'editor', 'user'],
+      defaultValue: ['user'],
+      required: true,
+      // Save roles to JWT for access control without database lookups
+      saveToJWT: true,
+      access: {
+        // Only admins can update roles
+        update: ({ req: { user } }) => user?.roles?.includes('admin'),
+      },
+    },
+  ],
+}
+```
+
+**Important Notes:**
+
+1. **Not Built-In**: Payload does not provide a roles system out of the box. You must add a `roles` field to your auth collection.
+2. **Save to JWT**: Use `saveToJWT: true` to include roles in the JWT token, enabling role checks without database queries.
+3. **Default Value**: Set a `defaultValue` to automatically assign new users a default role.
+4. **Access Control**: Restrict who can modify roles (typically only admins).
+5. **Role Options**: Define your own role hierarchy based on your application needs.
+
+**Using Roles in Access Control:**
+
+```ts
+import type { Access } from 'payload'
+
+// Check for specific role
+export const adminOnly: Access = ({ req: { user } }) => {
+  return user?.roles?.includes('admin')
+}
+
+// Check for multiple roles
+export const adminOrEditor: Access = ({ req: { user } }) => {
+  return Boolean(user?.roles?.some((role) => ['admin', 'editor'].includes(role)))
+}
+
+// Role hierarchy check
+export const hasMinimumRole: Access = ({ req: { user } }, minRole: string) => {
+  const roleHierarchy = ['user', 'editor', 'admin']
+  const userHighestRole = Math.max(...(user?.roles?.map((r) => roleHierarchy.indexOf(r)) || [-1]))
+  const requiredRoleIndex = roleHierarchy.indexOf(minRole)
+
+  return userHighestRole >= requiredRoleIndex
+}
+```
+
+### Reusable Access Functions
+
+```ts
+import type { Access } from 'payload'
+
+// Anyone (public)
+export const anyone: Access = () => true
+
+// Authenticated only
+export const authenticated: Access = ({ req: { user } }) => Boolean(user)
+
+// Authenticated or published content
+export const authenticatedOrPublished: Access = ({ req: { user } }) => {
+  if (user) return true
+  return { _status: { equals: 'published' } }
+}
+
+// Admin only
+export const admins: Access = ({ req: { user } }) => {
+  return user?.roles?.includes('admin')
+}
+
+// Admin or editor
+export const adminsOrEditors: Access = ({ req: { user } }) => {
+  return Boolean(user?.roles?.some((role) => ['admin', 'editor'].includes(role)))
+}
+
+// Self or admin
+export const adminsOrSelf: Access = ({ req: { user } }) => {
+  if (user?.roles?.includes('admin')) return true
+  return { id: { equals: user?.id } }
+}
+
+// Usage
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  access: {
+    create: authenticated,
+    read: authenticatedOrPublished,
+    update: adminsOrEditors,
+    delete: admins,
+  },
+  fields: [{ name: 'title', type: 'text' }],
+}
+```
+
+### Row-Level Security with Complex Queries
+
+```ts
+import type { Access } from 'payload'
+
+// Organization-scoped access
+export const organizationScoped: Access = ({ req: { user } }) => {
+  if (user?.roles?.includes('admin')) return true
+
+  // Users see only their organization's data
+  return {
+    organization: {
+      equals: user?.organization,
+    },
+  }
+}
+
+// Multiple conditions with AND
+export const complexAccess: Access = ({ req: { user } }) => {
+  return {
+    and: [
+      { status: { equals: 'published' } },
+      { 'author.isActive': { equals: true } },
+      {
+        or: [{ visibility: { equals: 'public' } }, { author: { equals: user?.id } }],
+      },
+    ],
+  }
+}
+
+// Team-based access
+export const teamMemberAccess: Access = ({ req: { user } }) => {
+  if (!user) return false
+  if (user.roles?.includes('admin')) return true
+
+  return {
+    'team.members': {
+      contains: user.id,
+    },
+  }
+}
+```
+
+### Header-Based Access (API Keys)
+
+```ts
+import type { Access } from 'payload'
+
+export const apiKeyAccess: Access = ({ req }) => {
+  const apiKey = req.headers.get('x-api-key')
+
+  if (!apiKey) return false
+
+  // Validate against stored keys
+  return apiKey === process.env.VALID_API_KEY
+}
+
+// Bearer token validation
+export const bearerTokenAccess: Access = async ({ req }) => {
+  const auth = req.headers.get('authorization')
+
+  if (!auth?.startsWith('Bearer ')) return false
+
+  const token = auth.slice(7)
+  const isValid = await validateToken(token)
+
+  return isValid
+}
+```
+
+## Field Access Control
+
+Field access does NOT support query constraints - only boolean returns.
+
+### Basic Field Access
+
+```ts
+import type { NumberField, FieldAccess } from 'payload'
+
+const salaryReadAccess: FieldAccess = ({ req: { user }, doc }) => {
+  // Self can read own salary
+  if (user?.id === doc?.id) return true
+  // Admin can read all salaries
+  return user?.roles?.includes('admin')
+}
+
+const salaryUpdateAccess: FieldAccess = ({ req: { user } }) => {
+  // Only admins can update salary
+  return user?.roles?.includes('admin')
+}
+
+const salaryField: NumberField = {
+  name: 'salary',
+  type: 'number',
+  access: {
+    read: salaryReadAccess,
+    update: salaryUpdateAccess,
+  },
+}
+```
+
+### Sibling Data Access
+
+```ts
+import type { ArrayField, FieldAccess } from 'payload'
+
+const contentReadAccess: FieldAccess = ({ req: { user }, siblingData }) => {
+  // Authenticated users see all
+  if (user) return true
+  // Public sees only if marked public
+  return siblingData?.isPublic === true
+}
+
+const arrayField: ArrayField = {
+  name: 'sections',
+  type: 'array',
+  fields: [
+    {
+      name: 'isPublic',
+      type: 'checkbox',
+      defaultValue: false,
+    },
+    {
+      name: 'content',
+      type: 'text',
+      access: {
+        read: contentReadAccess,
+      },
+    },
+  ],
+}
+```
+
+### Nested Field Access
+
+```ts
+import type { GroupField, FieldAccess } from 'payload'
+
+const internalOnlyAccess: FieldAccess = ({ req: { user } }) => {
+  return user?.roles?.includes('admin') || user?.roles?.includes('internal')
+}
+
+const groupField: GroupField = {
+  name: 'internalMetadata',
+  type: 'group',
+  access: {
+    read: internalOnlyAccess,
+    update: internalOnlyAccess,
+  },
+  fields: [
+    { name: 'internalNotes', type: 'textarea' },
+    { name: 'priority', type: 'select', options: ['low', 'medium', 'high'] },
+  ],
+}
+```
+
+### Hiding Admin Fields
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+export const Users: CollectionConfig = {
+  slug: 'users',
+  auth: true,
+  fields: [
+    { name: 'name', type: 'text', required: true },
+    { name: 'email', type: 'email', required: true },
+    {
+      name: 'roles',
+      type: 'select',
+      hasMany: true,
+      options: ['admin', 'editor', 'user'],
+      access: {
+        // Hide from UI, but still saved/queried
+        read: ({ req: { user } }) => user?.roles?.includes('admin'),
+        // Only admins can update roles
+        update: ({ req: { user } }) => user?.roles?.includes('admin'),
+      },
+    },
+  ],
+}
+```
+
+## Global Access Control
+
+```ts
+import type { GlobalConfig, Access } from 'payload'
+
+const adminOnly: Access = ({ req: { user } }) => {
+  return user?.roles?.includes('admin')
+}
+
+export const SiteSettings: GlobalConfig = {
+  slug: 'site-settings',
+  access: {
+    read: () => true, // Anyone can read settings
+    update: adminOnly, // Only admins can update
+    readVersions: adminOnly, // Only admins can see version history
+  },
+  fields: [
+    { name: 'siteName', type: 'text' },
+    { name: 'maintenanceMode', type: 'checkbox' },
+  ],
+}
+```
+
+## Multi-Tenant Access Control
+
+```ts
+import type { Access, CollectionConfig } from 'payload'
+
+// Add tenant field to user type
+interface User {
+  id: string
+  tenantId: string
+  roles?: string[]
+}
+
+// Tenant-scoped access
+const tenantAccess: Access = ({ req: { user } }) => {
+  // No user = no access
+  if (!user) return false
+
+  // Super admin sees all
+  if (user.roles?.includes('super-admin')) return true
+
+  // Users see only their tenant's data
+  return {
+    tenant: {
+      equals: (user as User).tenantId,
+    },
+  }
+}
+
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  access: {
+    create: tenantAccess,
+    read: tenantAccess,
+    update: tenantAccess,
+    delete: tenantAccess,
+  },
+  fields: [
+    { name: 'title', type: 'text' },
+    {
+      name: 'tenant',
+      type: 'text',
+      required: true,
+      access: {
+        // Tenant field hidden from non-admins
+        update: ({ req: { user } }) => user?.roles?.includes('super-admin'),
+      },
+      hooks: {
+        // Auto-set tenant on create
+        beforeChange: [
+          ({ req, operation, value }) => {
+            if (operation === 'create' && !value) {
+              return (req.user as User)?.tenantId
+            }
+            return value
+          },
+        ],
+      },
+    },
+  ],
+}
+```
+
+## Auth Collection Patterns
+
+### Self or Admin Pattern
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+export const Users: CollectionConfig = {
+  slug: 'users',
+  auth: true,
+  access: {
+    // Anyone can read user profiles
+    read: () => true,
+
+    // Users can update themselves, admins can update anyone
+    update: ({ req: { user }, id }) => {
+      if (user?.roles?.includes('admin')) return true
+      return user?.id === id
+    },
+
+    // Only admins can delete
+    delete: ({ req: { user } }) => user?.roles?.includes('admin'),
+  },
+  fields: [
+    { name: 'name', type: 'text' },
+    { name: 'email', type: 'email' },
+  ],
+}
+```
+
+### Restrict Self-Updates
+
+```ts
+import type { CollectionConfig, FieldAccess } from 'payload'
+
+const preventSelfRoleChange: FieldAccess = ({ req: { user }, id }) => {
+  // Admins can change anyone's roles
+  if (user?.roles?.includes('admin')) return true
+  // Users cannot change their own roles
+  if (user?.id === id) return false
+  return false
+}
+
+export const Users: CollectionConfig = {
+  slug: 'users',
+  auth: true,
+  fields: [
+    {
+      name: 'roles',
+      type: 'select',
+      hasMany: true,
+      options: ['admin', 'editor', 'user'],
+      access: {
+        update: preventSelfRoleChange,
+      },
+    },
+  ],
+}
+```
+
+## Cross-Collection Validation
+
+```ts
+import type { Access } from 'payload'
+
+// Check if user is a project member before allowing access
+export const projectMemberAccess: Access = async ({ req, id }) => {
+  const { user, payload } = req
+
+  if (!user) return false
+  if (user.roles?.includes('admin')) return true
+
+  // Check if document exists and user is member
+  const project = await payload.findByID({
+    collection: 'projects',
+    id: id as string,
+    depth: 0,
+  })
+
+  return project.members?.includes(user.id)
+}
+
+// Prevent deletion if document has dependencies
+export const preventDeleteWithDependencies: Access = async ({ req, id }) => {
+  const { payload } = req
+
+  const dependencyCount = await payload.count({
+    collection: 'related-items',
+    where: {
+      parent: { equals: id },
+    },
+  })
+
+  return dependencyCount === 0
+}
+```
+
+## Access Control Function Arguments
+
+### Collection Create
+
+```ts
+create: ({ req, data }) => boolean | Where
+
+// req: PayloadRequest
+//   - req.user: Authenticated user (if any)
+//   - req.payload: Payload instance for queries
+//   - req.headers: Request headers
+//   - req.locale: Current locale
+// data: The data being created
+```
+
+### Collection Read
+
+```ts
+read: ({ req, id }) => boolean | Where
+
+// req: PayloadRequest
+// id: Document ID being read
+//   - undefined during Access Operation (login check)
+//   - string when reading specific document
+```
+
+### Collection Update
+
+```ts
+update: ({ req, id, data }) => boolean | Where
+
+// req: PayloadRequest
+// id: Document ID being updated
+// data: New values being applied
+```
+
+### Collection Delete
+
+```ts
+delete: ({ req, id }) => boolean | Where
+
+// req: PayloadRequest
+// id: Document ID being deleted
+```
+
+### Field Create
+
+```ts
+access: {
+  create: ({ req, data, siblingData }) => boolean
+}
+
+// req: PayloadRequest
+// data: Full document data
+// siblingData: Adjacent field values at same level
+```
+
+### Field Read
+
+```ts
+access: {
+  read: ({ req, id, doc, siblingData }) => boolean
+}
+
+// req: PayloadRequest
+// id: Document ID
+// doc: Full document
+// siblingData: Adjacent field values
+```
+
+### Field Update
+
+```ts
+access: {
+  update: ({ req, id, data, doc, siblingData }) => boolean
+}
+
+// req: PayloadRequest
+// id: Document ID
+// data: New values
+// doc: Current document
+// siblingData: Adjacent field values
+```
+
+## Important Notes
+
+1. **Local API Default**: Access control is **skipped by default** in Local API (`overrideAccess: true`). When passing a `user` parameter, you almost always want to set `overrideAccess: false` to respect that user's permissions:
+
+   ```ts
+   // ❌ WRONG: Passes user but bypasses access control (default behavior)
+   await payload.find({
+     collection: 'posts',
+     user: someUser, // User is ignored for access control!
+   })
+
+   // ✅ CORRECT: Respects the user's permissions
+   await payload.find({
+     collection: 'posts',
+     user: someUser,
+     overrideAccess: false, // Required to enforce access control
+   })
+   ```
+
+   **Why this matters**: If you pass `user` without `overrideAccess: false`, the operation runs with admin privileges regardless of the user's actual permissions. This is a common security mistake.
+
+2. **Field Access Limitations**: Field-level access does NOT support query constraints - only boolean returns.
+
+3. **Admin Panel Visibility**: The `admin` access control determines if a collection appears in the admin panel for a user.
+
+4. **Access Before Hooks**: Access control executes BEFORE hooks run, so hooks cannot modify access behavior.
+
+5. **Query Constraints**: Only collection-level `read` access supports query constraints. All other operations and field-level access require boolean returns.
+
+## Best Practices
+
+1. **Reusable Functions**: Create named access functions for common patterns
+2. **Fail Secure**: Default to `false` for sensitive operations
+3. **Cache Checks**: Use `req.context` to cache expensive validation
+4. **Type Safety**: Type your user object for better IDE support
+5. **Test Thoroughly**: Write tests for complex access control logic
+6. **Document Intent**: Add comments explaining access rules
+7. **Audit Logs**: Track access control decisions for security review
+8. **Performance**: Avoid N+1 queries in access functions
+9. **Error Handling**: Access functions should not throw - return `false` instead
+10. **Tenant Hooks**: Auto-set tenant fields in `beforeChange` hooks
+
+## Advanced Patterns
+
+For advanced access control patterns including context-aware access, time-based restrictions, subscription-based access, factory functions, configuration templates, debugging tips, and performance optimization, see [ACCESS-CONTROL-ADVANCED.md](ACCESS-CONTROL-ADVANCED.md).
diff --git a/.claude/skills/payload-cms/reference/ADAPTERS.md b/.claude/skills/payload-cms/reference/ADAPTERS.md
@@ -0,0 +1,326 @@
+# Payload CMS Adapters Reference
+
+Complete reference for database, storage, and email adapters.
+
+## Database Adapters
+
+### MongoDB
+
+```ts
+import { mongooseAdapter } from '@payloadcms/db-mongodb'
+
+export default buildConfig({
+  db: mongooseAdapter({
+    url: process.env.DATABASE_URI,
+  }),
+})
+```
+
+### Postgres
+
+```ts
+import { postgresAdapter } from '@payloadcms/db-postgres'
+
+export default buildConfig({
+  db: postgresAdapter({
+    pool: {
+      connectionString: process.env.DATABASE_URI,
+    },
+    push: false, // Don't auto-push schema changes
+    migrationDir: './migrations',
+  }),
+})
+```
+
+### SQLite
+
+```ts
+import { sqliteAdapter } from '@payloadcms/db-sqlite'
+
+export default buildConfig({
+  db: sqliteAdapter({
+    client: {
+      url: 'file:./payload.db',
+    },
+    transactionOptions: {}, // Enable transactions (disabled by default)
+  }),
+})
+```
+
+## Transactions
+
+Payload automatically uses transactions for all-or-nothing database operations. Pass `req` to include operations in the same transaction.
+
+```ts
+import type { CollectionAfterChangeHook } from 'payload'
+
+const afterChange: CollectionAfterChangeHook = async ({ req, doc }) => {
+  // This will be part of the same transaction
+  await req.payload.create({
+    req, // Pass req to use same transaction
+    collection: 'audit-log',
+    data: { action: 'created', docId: doc.id },
+  })
+}
+
+// Manual transaction control
+const transactionID = await payload.db.beginTransaction()
+try {
+  await payload.create({
+    collection: 'orders',
+    data: orderData,
+    req: { transactionID },
+  })
+  await payload.update({
+    collection: 'inventory',
+    id: itemId,
+    data: { stock: newStock },
+    req: { transactionID },
+  })
+  await payload.db.commitTransaction(transactionID)
+} catch (error) {
+  await payload.db.rollbackTransaction(transactionID)
+  throw error
+}
+```
+
+**Note**: MongoDB requires replicaset for transactions. SQLite requires `transactionOptions: {}` to enable.
+
+### Threading req Through Operations
+
+**Critical**: When performing nested operations in hooks, always pass `req` to maintain transaction context. Failing to do so breaks atomicity and can cause partial updates.
+
+```ts
+import type { CollectionAfterChangeHook } from 'payload'
+
+// ✅ CORRECT: Thread req through nested operations
+const resaveChildren: CollectionAfterChangeHook = async ({ collection, doc, req }) => {
+  // Find children - pass req
+  const children = await req.payload.find({
+    collection: 'children',
+    where: { parent: { equals: doc.id } },
+    req, // Maintains transaction context
+  })
+
+  // Update each child - pass req
+  for (const child of children.docs) {
+    await req.payload.update({
+      id: child.id,
+      collection: 'children',
+      data: { updatedField: 'value' },
+      req, // Same transaction as parent operation
+    })
+  }
+}
+
+// ❌ WRONG: Missing req breaks transaction
+const brokenHook: CollectionAfterChangeHook = async ({ collection, doc, req }) => {
+  const children = await req.payload.find({
+    collection: 'children',
+    where: { parent: { equals: doc.id } },
+    // Missing req - separate transaction or no transaction
+  })
+
+  for (const child of children.docs) {
+    await req.payload.update({
+      id: child.id,
+      collection: 'children',
+      data: { updatedField: 'value' },
+      // Missing req - if parent operation fails, these updates persist
+    })
+  }
+}
+```
+
+**Why This Matters:**
+
+- **MongoDB (with replica sets)**: Creates atomic session across operations
+- **PostgreSQL**: All operations use same Drizzle transaction
+- **SQLite (with transactions enabled)**: Ensures rollback on errors
+- **Without req**: Each operation runs independently, breaking atomicity
+
+**When req is Required:**
+
+- All mutating operations in hooks (create, update, delete)
+- Operations that must succeed/fail together
+- When using MongoDB replica sets or Postgres
+- Any operation that relies on `req.context` or `req.user`
+
+**When req is Optional:**
+
+- Read-only lookups independent of current transaction
+- Operations with `disableTransaction: true`
+- Administrative operations with `overrideAccess: true`
+
+## Storage Adapters
+
+Available storage adapters:
+
+- **@payloadcms/storage-s3** - AWS S3
+- **@payloadcms/storage-azure** - Azure Blob Storage
+- **@payloadcms/storage-gcs** - Google Cloud Storage
+- **@payloadcms/storage-r2** - Cloudflare R2
+- **@payloadcms/storage-vercel-blob** - Vercel Blob
+- **@payloadcms/storage-uploadthing** - Uploadthing
+
+### AWS S3
+
+```ts
+import { s3Storage } from '@payloadcms/storage-s3'
+
+export default buildConfig({
+  plugins: [
+    s3Storage({
+      collections: {
+        media: true,
+      },
+      bucket: process.env.S3_BUCKET,
+      config: {
+        credentials: {
+          accessKeyId: process.env.S3_ACCESS_KEY_ID,
+          secretAccessKey: process.env.S3_SECRET_ACCESS_KEY,
+        },
+        region: process.env.S3_REGION,
+      },
+    }),
+  ],
+})
+```
+
+### Azure Blob Storage
+
+```ts
+import { azureStorage } from '@payloadcms/storage-azure'
+
+export default buildConfig({
+  plugins: [
+    azureStorage({
+      collections: {
+        media: true,
+      },
+      connectionString: process.env.AZURE_STORAGE_CONNECTION_STRING,
+      containerName: process.env.AZURE_STORAGE_CONTAINER_NAME,
+    }),
+  ],
+})
+```
+
+### Google Cloud Storage
+
+```ts
+import { gcsStorage } from '@payloadcms/storage-gcs'
+
+export default buildConfig({
+  plugins: [
+    gcsStorage({
+      collections: {
+        media: true,
+      },
+      bucket: process.env.GCS_BUCKET,
+      options: {
+        projectId: process.env.GCS_PROJECT_ID,
+        credentials: JSON.parse(process.env.GCS_CREDENTIALS),
+      },
+    }),
+  ],
+})
+```
+
+### Cloudflare R2
+
+```ts
+import { r2Storage } from '@payloadcms/storage-r2'
+
+export default buildConfig({
+  plugins: [
+    r2Storage({
+      collections: {
+        media: true,
+      },
+      bucket: process.env.R2_BUCKET,
+      config: {
+        credentials: {
+          accessKeyId: process.env.R2_ACCESS_KEY_ID,
+          secretAccessKey: process.env.R2_SECRET_ACCESS_KEY,
+        },
+        region: 'auto',
+        endpoint: process.env.R2_ENDPOINT,
+      },
+    }),
+  ],
+})
+```
+
+### Vercel Blob
+
+```ts
+import { vercelBlobStorage } from '@payloadcms/storage-vercel-blob'
+
+export default buildConfig({
+  plugins: [
+    vercelBlobStorage({
+      collections: {
+        media: true,
+      },
+      token: process.env.BLOB_READ_WRITE_TOKEN,
+    }),
+  ],
+})
+```
+
+### Uploadthing
+
+```ts
+import { uploadthingStorage } from '@payloadcms/storage-uploadthing'
+
+export default buildConfig({
+  plugins: [
+    uploadthingStorage({
+      collections: {
+        media: true,
+      },
+      options: {
+        token: process.env.UPLOADTHING_TOKEN,
+        acl: 'public-read',
+      },
+    }),
+  ],
+})
+```
+
+## Email Adapters
+
+### Nodemailer (SMTP)
+
+```ts
+import { nodemailerAdapter } from '@payloadcms/email-nodemailer'
+
+export default buildConfig({
+  email: nodemailerAdapter({
+    defaultFromAddress: 'noreply@example.com',
+    defaultFromName: 'My App',
+    transportOptions: {
+      host: process.env.SMTP_HOST,
+      port: 587,
+      auth: {
+        user: process.env.SMTP_USER,
+        pass: process.env.SMTP_PASS,
+      },
+    },
+  }),
+})
+```
+
+### Resend
+
+```ts
+import { resendAdapter } from '@payloadcms/email-resend'
+
+export default buildConfig({
+  email: resendAdapter({
+    defaultFromAddress: 'noreply@example.com',
+    defaultFromName: 'My App',
+    apiKey: process.env.RESEND_API_KEY,
+  }),
+})
+```
diff --git a/.claude/skills/payload-cms/reference/ADVANCED.md b/.claude/skills/payload-cms/reference/ADVANCED.md
@@ -0,0 +1,384 @@
+# Payload CMS Advanced Features
+
+Complete reference for authentication, jobs, custom endpoints, components, plugins, and localization.
+
+## Authentication
+
+### Login
+
+```ts
+// REST API
+const response = await fetch('/api/users/login', {
+  method: 'POST',
+  headers: { 'Content-Type': 'application/json' },
+  body: JSON.stringify({
+    email: 'user@example.com',
+    password: 'password',
+  }),
+})
+
+// Local API
+const result = await payload.login({
+  collection: 'users',
+  data: {
+    email: 'user@example.com',
+    password: 'password',
+  },
+})
+```
+
+### Forgot Password
+
+```ts
+await payload.forgotPassword({
+  collection: 'users',
+  data: {
+    email: 'user@example.com',
+  },
+})
+```
+
+### Custom Strategy
+
+```ts
+import type { CollectionConfig, Strategy } from 'payload'
+
+const customStrategy: Strategy = {
+  name: 'custom',
+  authenticate: async ({ payload, headers }) => {
+    const token = headers.get('authorization')?.split(' ')[1]
+    if (!token) return { user: null }
+
+    const user = await verifyToken(token)
+    return { user }
+  },
+}
+
+export const Users: CollectionConfig = {
+  slug: 'users',
+  auth: {
+    strategies: [customStrategy],
+  },
+  fields: [],
+}
+```
+
+### API Keys
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+export const APIKeys: CollectionConfig = {
+  slug: 'api-keys',
+  auth: {
+    disableLocalStrategy: true,
+    useAPIKey: true,
+  },
+  fields: [],
+}
+```
+
+## Jobs Queue
+
+Offload long-running or scheduled tasks to background workers.
+
+### Tasks
+
+```ts
+import { buildConfig } from 'payload'
+import type { TaskConfig } from 'payload'
+
+export default buildConfig({
+  jobs: {
+    tasks: [
+      {
+        slug: 'sendWelcomeEmail',
+        inputSchema: [
+          { name: 'userEmail', type: 'text', required: true },
+          { name: 'userName', type: 'text', required: true },
+        ],
+        outputSchema: [{ name: 'emailSent', type: 'checkbox', required: true }],
+        retries: 2, // Retry up to 2 times on failure
+        handler: async ({ input, req }) => {
+          await sendEmail({
+            to: input.userEmail,
+            subject: `Welcome ${input.userName}`,
+          })
+          return { output: { emailSent: true } }
+        },
+      } as TaskConfig<'sendWelcomeEmail'>,
+    ],
+  },
+})
+```
+
+### Queueing Jobs
+
+```ts
+// In a hook or endpoint
+await req.payload.jobs.queue({
+  task: 'sendWelcomeEmail',
+  input: {
+    userEmail: 'user@example.com',
+    userName: 'John',
+  },
+  waitUntil: new Date('2024-12-31'), // Optional: schedule for future
+})
+```
+
+### Workflows
+
+Multi-step jobs that run in sequence:
+
+```ts
+{
+  slug: 'onboardUser',
+  inputSchema: [{ name: 'userId', type: 'text' }],
+  handler: async ({ job, req }) => {
+    const results = await job.runInlineTask({
+      task: async ({ input }) => {
+        // Step 1: Send welcome email
+        await sendEmail(input.userId)
+        return { output: { emailSent: true } }
+      },
+    })
+
+    await job.runInlineTask({
+      task: async () => {
+        // Step 2: Create onboarding tasks
+        await createTasks()
+        return { output: { tasksCreated: true } }
+      },
+    })
+  },
+}
+```
+
+## Custom Endpoints
+
+### Root Endpoints
+
+```ts
+import { buildConfig } from 'payload'
+import type { Endpoint } from 'payload'
+
+const helloEndpoint: Endpoint = {
+  path: '/hello',
+  method: 'get',
+  handler: () => {
+    return Response.json({ message: 'Hello!' })
+  },
+}
+
+const greetEndpoint: Endpoint = {
+  path: '/greet/:name',
+  method: 'get',
+  handler: (req) => {
+    return Response.json({
+      message: `Hello ${req.routeParams.name}!`,
+    })
+  },
+}
+
+export default buildConfig({
+  endpoints: [helloEndpoint, greetEndpoint],
+  collections: [],
+  secret: process.env.PAYLOAD_SECRET || '',
+})
+```
+
+### Collection Endpoints
+
+```ts
+import type { CollectionConfig, Endpoint } from 'payload'
+
+const featuredEndpoint: Endpoint = {
+  path: '/featured',
+  method: 'get',
+  handler: async (req) => {
+    const posts = await req.payload.find({
+      collection: 'posts',
+      where: { featured: { equals: true } },
+    })
+    return Response.json(posts)
+  },
+}
+
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  endpoints: [featuredEndpoint],
+  fields: [
+    { name: 'title', type: 'text' },
+    { name: 'featured', type: 'checkbox' },
+  ],
+}
+```
+
+## Custom Components
+
+### Field Component (Client)
+
+```tsx
+'use client'
+import { useField } from '@payloadcms/ui'
+import type { TextFieldClientComponent } from 'payload'
+
+export const CustomField: TextFieldClientComponent = () => {
+  const { value, setValue } = useField()
+
+  return <input value={value || ''} onChange={(e) => setValue(e.target.value)} />
+}
+```
+
+### Custom View
+
+```tsx
+'use client'
+import { DefaultTemplate } from '@payloadcms/next/templates'
+
+export const CustomView = () => {
+  return (
+    <DefaultTemplate>
+      <h1>Custom Dashboard</h1>
+      {/* Your content */}
+    </DefaultTemplate>
+  )
+}
+```
+
+### Admin Config
+
+```ts
+import { buildConfig } from 'payload'
+
+export default buildConfig({
+  admin: {
+    components: {
+      beforeDashboard: ['/components/BeforeDashboard'],
+      beforeLogin: ['/components/BeforeLogin'],
+      views: {
+        custom: {
+          Component: '/views/Custom',
+          path: '/custom',
+        },
+      },
+    },
+  },
+  collections: [],
+  secret: process.env.PAYLOAD_SECRET || '',
+})
+```
+
+## Plugins
+
+### Available Plugins
+
+- **@payloadcms/plugin-seo** - SEO fields with meta title/description, Open Graph, preview generation
+- **@payloadcms/plugin-redirects** - Manage URL redirects (301/302) for Next.js apps
+- **@payloadcms/plugin-nested-docs** - Hierarchical document structures with breadcrumbs
+- **@payloadcms/plugin-form-builder** - Dynamic form builder with submissions and validation
+- **@payloadcms/plugin-search** - Full-text search integration (Algolia support)
+- **@payloadcms/plugin-stripe** - Stripe payments, subscriptions, webhooks
+- **@payloadcms/plugin-ecommerce** - Complete ecommerce solution (products, variants, carts, orders)
+- **@payloadcms/plugin-import-export** - Import/export data via CSV
+- **@payloadcms/plugin-multi-tenant** - Multi-tenancy with tenant isolation
+- **@payloadcms/plugin-sentry** - Sentry error tracking integration
+- **@payloadcms/plugin-mcp** - Model Context Protocol for AI integrations
+
+### Using Plugins
+
+```ts
+import { buildConfig } from 'payload'
+import { seoPlugin } from '@payloadcms/plugin-seo'
+import { redirectsPlugin } from '@payloadcms/plugin-redirects'
+
+export default buildConfig({
+  plugins: [
+    seoPlugin({
+      collections: ['posts', 'pages'],
+    }),
+    redirectsPlugin({
+      collections: ['pages'],
+    }),
+  ],
+  collections: [],
+  secret: process.env.PAYLOAD_SECRET || '',
+})
+```
+
+### Creating Plugins
+
+```ts
+import type { Config } from 'payload'
+
+interface PluginOptions {
+  enabled?: boolean
+}
+
+export const myPlugin =
+  (options: PluginOptions) =>
+  (config: Config): Config => ({
+    ...config,
+    collections: [
+      ...(config.collections || []),
+      {
+        slug: 'plugin-collection',
+        fields: [{ name: 'title', type: 'text' }],
+      },
+    ],
+    onInit: async (payload) => {
+      if (config.onInit) await config.onInit(payload)
+      // Plugin initialization
+    },
+  })
+```
+
+## Localization
+
+```ts
+import { buildConfig } from 'payload'
+import type { Field, Payload } from 'payload'
+
+export default buildConfig({
+  localization: {
+    locales: ['en', 'es', 'de'],
+    defaultLocale: 'en',
+    fallback: true,
+  },
+  collections: [],
+  secret: process.env.PAYLOAD_SECRET || '',
+})
+
+// Localized field
+const localizedField: TextField = {
+  name: 'title',
+  type: 'text',
+  localized: true,
+}
+
+// Query with locale
+const posts = await payload.find({
+  collection: 'posts',
+  locale: 'es',
+})
+```
+
+## TypeScript Type References
+
+For complete TypeScript type definitions and signatures, reference these files from the Payload source:
+
+### Core Configuration Types
+
+- **[All Commonly-Used Types](https://github.com/payloadcms/payload/blob/main/packages/payload/src/index.ts)** - Check here first for commonly used types and interfaces. All core types are exported from this file.
+
+### Database & Adapters
+
+- **[Database Adapter Types](https://github.com/payloadcms/payload/blob/main/packages/payload/src/database/types.ts)** - Base adapter interface
+- **[MongoDB Adapter](https://github.com/payloadcms/payload/blob/main/packages/db-mongodb/src/index.ts)** - MongoDB-specific options
+- **[Postgres Adapter](https://github.com/payloadcms/payload/blob/main/packages/db-postgres/src/index.ts)** - Postgres-specific options
+
+### Rich Text & Plugins
+
+- **[Lexical Types](https://github.com/payloadcms/payload/blob/main/packages/richtext-lexical/src/exports/server/index.ts)** - Lexical editor configuration
+
+When users need detailed type information, fetch these URLs to provide complete signatures and optional parameters.
diff --git a/.claude/skills/payload-cms/reference/COLLECTIONS.md b/.claude/skills/payload-cms/reference/COLLECTIONS.md
@@ -0,0 +1,303 @@
+# Payload CMS Collections Reference
+
+Complete reference for collection configurations and patterns.
+
+## Basic Collection
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  labels: {
+    singular: 'Post',
+    plural: 'Posts',
+  },
+  admin: {
+    useAsTitle: 'title',
+    defaultColumns: ['title', 'author', 'status', 'createdAt'],
+    group: 'Content', // Organize in admin sidebar
+    description: 'Blog posts and articles',
+    listSearchableFields: ['title', 'slug'],
+  },
+  fields: [
+    {
+      name: 'title',
+      type: 'text',
+      required: true,
+      index: true,
+    },
+    {
+      name: 'slug',
+      type: 'text',
+      unique: true,
+      index: true,
+      admin: { position: 'sidebar' },
+    },
+    {
+      name: 'status',
+      type: 'select',
+      options: ['draft', 'published'],
+      defaultValue: 'draft',
+    },
+  ],
+  defaultSort: '-createdAt',
+  timestamps: true,
+}
+```
+
+## Auth Collection
+
+```ts
+export const Users: CollectionConfig = {
+  slug: 'users',
+  auth: {
+    tokenExpiration: 7200, // 2 hours
+    verify: true,
+    maxLoginAttempts: 5,
+    lockTime: 600000, // 10 minutes
+    useAPIKey: true,
+  },
+  admin: {
+    useAsTitle: 'email',
+  },
+  fields: [
+    {
+      name: 'roles',
+      type: 'select',
+      hasMany: true,
+      options: ['admin', 'editor', 'user'],
+      required: true,
+      defaultValue: ['user'],
+      saveToJWT: true,
+    },
+    {
+      name: 'name',
+      type: 'text',
+      required: true,
+    },
+  ],
+}
+```
+
+## Upload Collection
+
+```ts
+export const Media: CollectionConfig = {
+  slug: 'media',
+  upload: {
+    staticDir: 'media',
+    mimeTypes: ['image/*'],
+    imageSizes: [
+      {
+        name: 'thumbnail',
+        width: 400,
+        height: 300,
+        position: 'centre',
+      },
+      {
+        name: 'card',
+        width: 768,
+        height: 1024,
+      },
+    ],
+    adminThumbnail: 'thumbnail',
+    focalPoint: true,
+    crop: true,
+  },
+  access: {
+    read: () => true,
+  },
+  fields: [
+    {
+      name: 'alt',
+      type: 'text',
+      required: true,
+    },
+    {
+      name: 'caption',
+      type: 'text',
+      localized: true,
+    },
+  ],
+}
+```
+
+## Live Preview
+
+Enable real-time content preview during editing.
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+const generatePreviewPath = ({
+  slug,
+  collection,
+  req,
+}: {
+  slug: string
+  collection: string
+  req: any
+}) => {
+  const baseUrl = process.env.NEXT_PUBLIC_SERVER_URL
+  return `${baseUrl}/api/preview?slug=${slug}&collection=${collection}`
+}
+
+export const Pages: CollectionConfig = {
+  slug: 'pages',
+  admin: {
+    useAsTitle: 'title',
+    // Live preview during editing
+    livePreview: {
+      url: ({ data, req }) =>
+        generatePreviewPath({
+          slug: data?.slug as string,
+          collection: 'pages',
+          req,
+        }),
+    },
+    // Static preview button
+    preview: (data, { req }) =>
+      generatePreviewPath({
+        slug: data?.slug as string,
+        collection: 'pages',
+        req,
+      }),
+  },
+  fields: [
+    { name: 'title', type: 'text' },
+    { name: 'slug', type: 'text' },
+  ],
+}
+```
+
+## Versioning & Drafts
+
+Payload maintains version history and supports draft/publish workflows.
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+// Basic versioning (audit log only)
+export const Users: CollectionConfig = {
+  slug: 'users',
+  versions: true, // or { maxPerDoc: 100 }
+  fields: [{ name: 'name', type: 'text' }],
+}
+
+// Drafts enabled (draft/publish workflow)
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  versions: {
+    drafts: true, // Enables _status field
+    maxPerDoc: 50,
+  },
+  fields: [{ name: 'title', type: 'text' }],
+}
+
+// Full configuration with autosave and scheduled publish
+export const Pages: CollectionConfig = {
+  slug: 'pages',
+  versions: {
+    drafts: {
+      autosave: true, // Auto-save while editing
+      schedulePublish: true, // Schedule future publish/unpublish
+      validate: false, // Don't validate drafts (default)
+    },
+    maxPerDoc: 100, // Keep last 100 versions (0 = unlimited)
+  },
+  fields: [{ name: 'title', type: 'text' }],
+}
+```
+
+### Draft API Usage
+
+```ts
+// Create draft
+await payload.create({
+  collection: 'posts',
+  data: { title: 'Draft Post' },
+  draft: true, // Saves as draft, skips required field validation
+})
+
+// Update as draft
+await payload.update({
+  collection: 'posts',
+  id: '123',
+  data: { title: 'Updated Draft' },
+  draft: true,
+})
+
+// Read with drafts (returns newest draft if available)
+const post = await payload.findByID({
+  collection: 'posts',
+  id: '123',
+  draft: true, // Returns draft version if exists
+})
+
+// Query only published (REST API)
+// GET /api/posts (returns only _status: 'published')
+
+// Access control for drafts
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  versions: { drafts: true },
+  access: {
+    read: ({ req: { user } }) => {
+      // Public can only see published
+      if (!user) return { _status: { equals: 'published' } }
+      // Authenticated can see all
+      return true
+    },
+  },
+  fields: [{ name: 'title', type: 'text' }],
+}
+```
+
+### Document Status
+
+The `_status` field is auto-injected when drafts are enabled:
+
+- `draft` - Never published
+- `published` - Published with no newer drafts
+- `changed` - Published but has newer unpublished drafts
+
+## Globals
+
+Globals are single-instance documents (not collections).
+
+```ts
+import type { GlobalConfig } from 'payload'
+
+export const Header: GlobalConfig = {
+  slug: 'header',
+  label: 'Header',
+  admin: {
+    group: 'Settings',
+  },
+  fields: [
+    {
+      name: 'logo',
+      type: 'upload',
+      relationTo: 'media',
+      required: true,
+    },
+    {
+      name: 'nav',
+      type: 'array',
+      maxRows: 8,
+      fields: [
+        {
+          name: 'link',
+          type: 'relationship',
+          relationTo: 'pages',
+        },
+        {
+          name: 'label',
+          type: 'text',
+        },
+      ],
+    },
+  ],
+}
+```
diff --git a/.claude/skills/payload-cms/reference/FIELDS.md b/.claude/skills/payload-cms/reference/FIELDS.md
@@ -0,0 +1,700 @@
+# Payload CMS Field Types Reference
+
+Complete reference for all Payload field types with examples.
+
+## Text Field
+
+```ts
+import type { TextField } from 'payload'
+
+const textField: TextField = {
+  name: 'title',
+  type: 'text',
+  required: true,
+  unique: true,
+  minLength: 5,
+  maxLength: 100,
+  index: true,
+  localized: true,
+  defaultValue: 'Default Title',
+  validate: (value) => Boolean(value) || 'Required',
+  admin: {
+    placeholder: 'Enter title...',
+    position: 'sidebar',
+    condition: (data) => data.showTitle === true,
+  },
+}
+```
+
+### Slug Field Helper
+
+Built-in helper for auto-generating slugs:
+
+```ts
+import { slugField } from 'payload'
+import type { CollectionConfig } from 'payload'
+
+export const Pages: CollectionConfig = {
+  slug: 'pages',
+  fields: [
+    { name: 'title', type: 'text', required: true },
+    slugField({
+      name: 'slug', // defaults to 'slug'
+      fieldToUse: 'title', // defaults to 'title'
+      checkboxName: 'generateSlug', // defaults to 'generateSlug'
+      localized: true,
+      required: true,
+      overrides: (defaultField) => {
+        // Customize the generated fields if needed
+        return defaultField
+      },
+    }),
+  ],
+}
+```
+
+## Rich Text (Lexical)
+
+```ts
+import type { RichTextField } from 'payload'
+import { lexicalEditor } from '@payloadcms/richtext-lexical'
+import { HeadingFeature, LinkFeature } from '@payloadcms/richtext-lexical'
+
+const richTextField: RichTextField = {
+  name: 'content',
+  type: 'richText',
+  required: true,
+  localized: true,
+  editor: lexicalEditor({
+    features: ({ defaultFeatures }) => [
+      ...defaultFeatures,
+      HeadingFeature({
+        enabledHeadingSizes: ['h1', 'h2', 'h3'],
+      }),
+      LinkFeature({
+        enabledCollections: ['posts', 'pages'],
+      }),
+    ],
+  }),
+}
+```
+
+### Advanced Lexical Configuration
+
+```ts
+import {
+  BoldFeature,
+  EXPERIMENTAL_TableFeature,
+  FixedToolbarFeature,
+  HeadingFeature,
+  IndentFeature,
+  InlineToolbarFeature,
+  ItalicFeature,
+  LinkFeature,
+  OrderedListFeature,
+  UnderlineFeature,
+  UnorderedListFeature,
+  lexicalEditor,
+} from '@payloadcms/richtext-lexical'
+
+// Global editor config with full features
+export default buildConfig({
+  editor: lexicalEditor({
+    features: () => {
+      return [
+        UnderlineFeature(),
+        BoldFeature(),
+        ItalicFeature(),
+        OrderedListFeature(),
+        UnorderedListFeature(),
+        LinkFeature({
+          enabledCollections: ['pages'],
+          fields: ({ defaultFields }) => {
+            const defaultFieldsWithoutUrl = defaultFields.filter((field) => {
+              if ('name' in field && field.name === 'url') return false
+              return true
+            })
+
+            return [
+              ...defaultFieldsWithoutUrl,
+              {
+                name: 'url',
+                type: 'text',
+                admin: {
+                  condition: ({ linkType }) => linkType !== 'internal',
+                },
+                label: ({ t }) => t('fields:enterURL'),
+                required: true,
+              },
+            ]
+          },
+        }),
+        IndentFeature(),
+        EXPERIMENTAL_TableFeature(),
+      ]
+    },
+  }),
+})
+
+// Field-specific editor with custom toolbar
+const richTextWithToolbars: RichTextField = {
+  name: 'richText',
+  type: 'richText',
+  editor: lexicalEditor({
+    features: ({ rootFeatures }) => {
+      return [
+        ...rootFeatures,
+        HeadingFeature({ enabledHeadingSizes: ['h2', 'h3', 'h4'] }),
+        FixedToolbarFeature(),
+        InlineToolbarFeature(),
+      ]
+    },
+  }),
+  label: false,
+}
+```
+
+## Relationship
+
+```ts
+import type { RelationshipField } from 'payload'
+
+// Single relationship
+const singleRelationship: RelationshipField = {
+  name: 'author',
+  type: 'relationship',
+  relationTo: 'users',
+  required: true,
+  maxDepth: 2,
+}
+
+// Multiple relationships (hasMany)
+const multipleRelationship: RelationshipField = {
+  name: 'categories',
+  type: 'relationship',
+  relationTo: 'categories',
+  hasMany: true,
+  filterOptions: {
+    active: { equals: true },
+  },
+}
+
+// Polymorphic relationship
+const polymorphicRelationship: PolymorphicRelationshipField = {
+  name: 'relatedContent',
+  type: 'relationship',
+  relationTo: ['posts', 'pages'],
+  hasMany: true,
+}
+```
+
+## Array
+
+```ts
+import type { ArrayField } from 'payload'
+
+const arrayField: ArrayField = {
+  name: 'slides',
+  type: 'array',
+  minRows: 2,
+  maxRows: 10,
+  labels: {
+    singular: 'Slide',
+    plural: 'Slides',
+  },
+  fields: [
+    {
+      name: 'title',
+      type: 'text',
+      required: true,
+    },
+    {
+      name: 'image',
+      type: 'upload',
+      relationTo: 'media',
+    },
+  ],
+  admin: {
+    initCollapsed: true,
+  },
+}
+```
+
+## Blocks
+
+```ts
+import type { BlocksField, Block } from 'payload'
+
+const HeroBlock: Block = {
+  slug: 'hero',
+  interfaceName: 'HeroBlock',
+  fields: [
+    {
+      name: 'heading',
+      type: 'text',
+      required: true,
+    },
+    {
+      name: 'background',
+      type: 'upload',
+      relationTo: 'media',
+    },
+  ],
+}
+
+const ContentBlock: Block = {
+  slug: 'content',
+  fields: [
+    {
+      name: 'text',
+      type: 'richText',
+    },
+  ],
+}
+
+const blocksField: BlocksField = {
+  name: 'layout',
+  type: 'blocks',
+  blocks: [HeroBlock, ContentBlock],
+}
+```
+
+## Select
+
+```ts
+import type { SelectField } from 'payload'
+
+const selectField: SelectField = {
+  name: 'status',
+  type: 'select',
+  options: [
+    { label: 'Draft', value: 'draft' },
+    { label: 'Published', value: 'published' },
+  ],
+  defaultValue: 'draft',
+  required: true,
+}
+
+// Multiple select
+const multiSelectField: SelectField = {
+  name: 'tags',
+  type: 'select',
+  hasMany: true,
+  options: ['tech', 'news', 'sports'],
+}
+```
+
+## Upload
+
+```ts
+import type { UploadField } from 'payload'
+
+const uploadField: UploadField = {
+  name: 'featuredImage',
+  type: 'upload',
+  relationTo: 'media',
+  required: true,
+  filterOptions: {
+    mimeType: { contains: 'image' },
+  },
+}
+```
+
+## Point (Geolocation)
+
+Point fields store geographic coordinates with automatic 2dsphere indexing for geospatial queries.
+
+```ts
+import type { PointField } from 'payload'
+
+const locationField: PointField = {
+  name: 'location',
+  type: 'point',
+  label: 'Location',
+  required: true,
+}
+
+// Returns [longitude, latitude]
+// Example: [-122.4194, 37.7749] for San Francisco
+```
+
+### Geospatial Queries
+
+```ts
+// Query by distance (sorted by nearest first)
+const nearbyLocations = await payload.find({
+  collection: 'stores',
+  where: {
+    location: {
+      near: [10, 20], // [longitude, latitude]
+      maxDistance: 5000, // in meters
+      minDistance: 1000,
+    },
+  },
+})
+
+// Query within polygon area
+const polygon: Point[] = [
+  [9.0, 19.0], // bottom-left
+  [9.0, 21.0], // top-left
+  [11.0, 21.0], // top-right
+  [11.0, 19.0], // bottom-right
+  [9.0, 19.0], // closing point
+]
+
+const withinArea = await payload.find({
+  collection: 'stores',
+  where: {
+    location: {
+      within: {
+        type: 'Polygon',
+        coordinates: [polygon],
+      },
+    },
+  },
+})
+
+// Query intersecting area
+const intersecting = await payload.find({
+  collection: 'stores',
+  where: {
+    location: {
+      intersects: {
+        type: 'Polygon',
+        coordinates: [polygon],
+      },
+    },
+  },
+})
+```
+
+**Note**: Point fields are not supported in SQLite.
+
+## Join Fields
+
+Join fields create reverse relationships, allowing you to access related documents from the "other side" of a relationship.
+
+```ts
+import type { JoinField } from 'payload'
+
+// From Users collection - show user's orders
+const ordersJoinField: JoinField = {
+  name: 'orders',
+  type: 'join',
+  collection: 'orders',
+  on: 'customer', // The field in 'orders' that references this user
+  admin: {
+    allowCreate: false,
+    defaultColumns: ['id', 'createdAt', 'total', 'currency', 'items'],
+  },
+}
+
+// From Users collection - show user's cart
+const cartJoinField: JoinField = {
+  name: 'cart',
+  type: 'join',
+  collection: 'carts',
+  on: 'customer',
+  admin: {
+    allowCreate: false,
+    defaultColumns: ['id', 'createdAt', 'total', 'currency'],
+  },
+}
+```
+
+## Virtual Fields
+
+```ts
+import type { TextField } from 'payload'
+
+// Computed from siblings
+const computedVirtualField: TextField = {
+  name: 'fullName',
+  type: 'text',
+  virtual: true,
+  hooks: {
+    afterRead: [({ siblingData }) => `${siblingData.firstName} ${siblingData.lastName}`],
+  },
+}
+
+// From relationship path
+const pathVirtualField: TextField = {
+  name: 'authorName',
+  type: 'text',
+  virtual: 'author.name',
+}
+```
+
+## Conditional Fields
+
+```ts
+import type { UploadField, CheckboxField } from 'payload'
+
+// Simple boolean condition
+const enableFeatureField: CheckboxField = {
+  name: 'enableFeature',
+  type: 'checkbox',
+}
+
+const conditionalField: TextField = {
+  name: 'featureText',
+  type: 'text',
+  admin: {
+    condition: (data) => data.enableFeature === true,
+  },
+}
+
+// Sibling data condition (from hero field pattern)
+const typeField: SelectField = {
+  name: 'type',
+  type: 'select',
+  options: ['none', 'highImpact', 'mediumImpact', 'lowImpact'],
+  defaultValue: 'lowImpact',
+}
+
+const mediaField: UploadField = {
+  name: 'media',
+  type: 'upload',
+  relationTo: 'media',
+  admin: {
+    condition: (_, { type } = {}) => ['highImpact', 'mediumImpact'].includes(type),
+  },
+  required: true,
+}
+```
+
+## Radio
+
+Radio fields present options as radio buttons for single selection.
+
+```ts
+import type { RadioField } from 'payload'
+
+const radioField: RadioField = {
+  name: 'priority',
+  type: 'radio',
+  options: [
+    { label: 'Low', value: 'low' },
+    { label: 'Medium', value: 'medium' },
+    { label: 'High', value: 'high' },
+  ],
+  defaultValue: 'medium',
+  admin: {
+    layout: 'horizontal', // or 'vertical'
+  },
+}
+```
+
+## Row (Layout)
+
+Row fields arrange fields horizontally in the admin panel (presentational only).
+
+```ts
+import type { RowField } from 'payload'
+
+const rowField: RowField = {
+  type: 'row',
+  fields: [
+    {
+      name: 'firstName',
+      type: 'text',
+      admin: { width: '50%' },
+    },
+    {
+      name: 'lastName',
+      type: 'text',
+      admin: { width: '50%' },
+    },
+  ],
+}
+```
+
+## Collapsible (Layout)
+
+Collapsible fields group fields in an expandable/collapsible section.
+
+```ts
+import type { CollapsibleField } from 'payload'
+
+const collapsibleField: CollapsibleField = {
+  label: ({ data }) => data?.title || 'Advanced Options',
+  type: 'collapsible',
+  admin: {
+    initCollapsed: true,
+  },
+  fields: [
+    { name: 'customCSS', type: 'textarea' },
+    { name: 'customJS', type: 'code' },
+  ],
+}
+```
+
+## UI (Custom Components)
+
+UI fields allow fully custom React components in the admin (no data stored).
+
+```ts
+import type { UIField } from 'payload'
+
+const uiField: UIField = {
+  name: 'customMessage',
+  type: 'ui',
+  admin: {
+    components: {
+      Field: '/path/to/CustomFieldComponent',
+      Cell: '/path/to/CustomCellComponent', // For list view
+    },
+  },
+}
+```
+
+## Tabs & Groups
+
+```ts
+import type { TabsField, GroupField } from 'payload'
+
+// Tabs
+const tabsField: TabsField = {
+  type: 'tabs',
+  tabs: [
+    {
+      label: 'Content',
+      fields: [
+        { name: 'title', type: 'text' },
+        { name: 'body', type: 'richText' },
+      ],
+    },
+    {
+      label: 'SEO',
+      fields: [
+        { name: 'metaTitle', type: 'text' },
+        { name: 'metaDescription', type: 'textarea' },
+      ],
+    },
+  ],
+}
+
+// Group (named)
+const groupField: GroupField = {
+  name: 'meta',
+  type: 'group',
+  fields: [
+    { name: 'title', type: 'text' },
+    { name: 'description', type: 'textarea' },
+  ],
+}
+```
+
+## Reusable Field Factories
+
+Create composable field patterns that can be customized with overrides.
+
+```ts
+import type { Field, GroupField } from 'payload'
+
+// Utility for deep merging
+const deepMerge = <T>(target: T, source: Partial<T>): T => {
+  // Implementation would deeply merge objects
+  return { ...target, ...source }
+}
+
+// Reusable link field factory
+type LinkType = (options?: {
+  appearances?: ('default' | 'outline')[] | false
+  disableLabel?: boolean
+  overrides?: Record<string, unknown>
+}) => GroupField
+
+export const link: LinkType = ({ appearances, disableLabel = false, overrides = {} } = {}) => {
+  const linkField: GroupField = {
+    name: 'link',
+    type: 'group',
+    admin: {
+      hideGutter: true,
+    },
+    fields: [
+      {
+        type: 'row',
+        fields: [
+          {
+            name: 'type',
+            type: 'radio',
+            options: [
+              { label: 'Internal link', value: 'reference' },
+              { label: 'Custom URL', value: 'custom' },
+            ],
+            defaultValue: 'reference',
+            admin: {
+              layout: 'horizontal',
+              width: '50%',
+            },
+          },
+          {
+            name: 'newTab',
+            type: 'checkbox',
+            label: 'Open in new tab',
+            admin: {
+              width: '50%',
+              style: {
+                alignSelf: 'flex-end',
+              },
+            },
+          },
+        ],
+      },
+      {
+        name: 'reference',
+        type: 'relationship',
+        relationTo: ['pages'],
+        required: true,
+        maxDepth: 1,
+        admin: {
+          condition: (_, siblingData) => siblingData?.type === 'reference',
+        },
+      },
+      {
+        name: 'url',
+        type: 'text',
+        label: 'Custom URL',
+        required: true,
+        admin: {
+          condition: (_, siblingData) => siblingData?.type === 'custom',
+        },
+      },
+    ],
+  }
+
+  if (!disableLabel) {
+    linkField.fields.push({
+      name: 'label',
+      type: 'text',
+      required: true,
+    })
+  }
+
+  if (appearances !== false) {
+    linkField.fields.push({
+      name: 'appearance',
+      type: 'select',
+      defaultValue: 'default',
+      options: [
+        { label: 'Default', value: 'default' },
+        { label: 'Outline', value: 'outline' },
+      ],
+    })
+  }
+
+  return deepMerge(linkField, overrides) as GroupField
+}
+
+// Usage
+const navItem = link({ appearances: false })
+const ctaButton = link({
+  overrides: {
+    name: 'cta',
+    admin: {
+      description: 'Call to action button',
+    },
+  },
+})
+```
diff --git a/.claude/skills/payload-cms/reference/HOOKS.md b/.claude/skills/payload-cms/reference/HOOKS.md
@@ -0,0 +1,186 @@
+# Payload CMS Hooks Reference
+
+Complete reference for collection hooks, field hooks, and hook context patterns.
+
+## Collection Hooks
+
+```ts
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  hooks: {
+    // Before validation
+    beforeValidate: [
+      async ({ data, operation }) => {
+        if (operation === 'create') {
+          data.slug = slugify(data.title)
+        }
+        return data
+      },
+    ],
+
+    // Before save
+    beforeChange: [
+      async ({ data, req, operation, originalDoc }) => {
+        if (operation === 'update' && data.status === 'published') {
+          data.publishedAt = new Date()
+        }
+        return data
+      },
+    ],
+
+    // After save
+    afterChange: [
+      async ({ doc, req, operation, previousDoc }) => {
+        if (operation === 'create') {
+          await sendNotification(doc)
+        }
+        return doc
+      },
+    ],
+
+    // After read
+    afterRead: [
+      async ({ doc, req }) => {
+        doc.viewCount = await getViewCount(doc.id)
+        return doc
+      },
+    ],
+
+    // Before delete
+    beforeDelete: [
+      async ({ req, id }) => {
+        await cleanupRelatedData(id)
+      },
+    ],
+  },
+}
+```
+
+## Field Hooks
+
+```ts
+import type { EmailField, FieldHook } from 'payload'
+
+const beforeValidateHook: FieldHook = ({ value }) => {
+  return value.trim().toLowerCase()
+}
+
+const afterReadHook: FieldHook = ({ value, req }) => {
+  // Hide email from non-admins
+  if (!req.user?.roles?.includes('admin')) {
+    return value.replace(/(.{2})(.*)(@.*)/, '$1***$3')
+  }
+  return value
+}
+
+const emailField: EmailField = {
+  name: 'email',
+  type: 'email',
+  hooks: {
+    beforeValidate: [beforeValidateHook],
+    afterRead: [afterReadHook],
+  },
+}
+```
+
+## Hook Context
+
+Share data between hooks or control hook behavior using request context:
+
+```ts
+import type { CollectionConfig } from 'payload'
+
+export const Posts: CollectionConfig = {
+  slug: 'posts',
+  hooks: {
+    beforeChange: [
+      async ({ context }) => {
+        context.expensiveData = await fetchExpensiveData()
+      },
+    ],
+    afterChange: [
+      async ({ context, doc }) => {
+        // Reuse from previous hook
+        await processData(doc, context.expensiveData)
+      },
+    ],
+  },
+  fields: [{ name: 'title', type: 'text' }],
+}
+```
+
+## Next.js Revalidation with Context Control
+
+```ts
+import type { CollectionAfterChangeHook, CollectionAfterDeleteHook } from 'payload'
+import { revalidatePath } from 'next/cache'
+import type { Page } from '../payload-types'
+
+export const revalidatePage: CollectionAfterChangeHook<Page> = ({
+  doc,
+  previousDoc,
+  req: { payload, context },
+}) => {
+  if (!context.disableRevalidate) {
+    if (doc._status === 'published') {
+      const path = doc.slug === 'home' ? '/' : `/${doc.slug}`
+      payload.logger.info(`Revalidating page at path: ${path}`)
+      revalidatePath(path)
+    }
+
+    // Revalidate old path if unpublished
+    if (previousDoc?._status === 'published' && doc._status !== 'published') {
+      const oldPath = previousDoc.slug === 'home' ? '/' : `/${previousDoc.slug}`
+      payload.logger.info(`Revalidating old page at path: ${oldPath}`)
+      revalidatePath(oldPath)
+    }
+  }
+  return doc
+}
+
+export const revalidateDelete: CollectionAfterDeleteHook<Page> = ({ doc, req: { context } }) => {
+  if (!context.disableRevalidate) {
+    const path = doc?.slug === 'home' ? '/' : `/${doc?.slug}`
+    revalidatePath(path)
+  }
+  return doc
+}
+```
+
+## Date Field Auto-Set
+
+Automatically set date when document is published:
+
+```ts
+import type { DateField } from 'payload'
+
+const publishedOnField: DateField = {
+  name: 'publishedOn',
+  type: 'date',
+  admin: {
+    date: {
+      pickerAppearance: 'dayAndTime',
+    },
+    position: 'sidebar',
+  },
+  hooks: {
+    beforeChange: [
+      ({ siblingData, value }) => {
+        if (siblingData._status === 'published' && !value) {
+          return new Date()
+        }
+        return value
+      },
+    ],
+  },
+}
+```
+
+## Hook Patterns Best Practices
+
+- Use `beforeValidate` for data formatting
+- Use `beforeChange` for business logic
+- Use `afterChange` for side effects
+- Use `afterRead` for computed fields
+- Store expensive operations in `context`
+- Pass `req` to nested operations for transaction safety (see [ADAPTERS.md#threading-req-through-operations](ADAPTERS.md#threading-req-through-operations))
diff --git a/.claude/skills/payload-cms/reference/QUERIES.md b/.claude/skills/payload-cms/reference/QUERIES.md
@@ -0,0 +1,274 @@
+# Payload CMS Querying Reference
+
+Complete reference for querying data across Local API, REST, and GraphQL.
+
+## Query Operators
+
+```ts
+import type { Where } from 'payload'
+
+// Equals
+const equalsQuery: Where = { color: { equals: 'blue' } }
+
+// Not equals
+const notEqualsQuery: Where = { status: { not_equals: 'draft' } }
+
+// Greater/less than
+const greaterThanQuery: Where = { price: { greater_than: 100 } }
+const lessThanEqualQuery: Where = { age: { less_than_equal: 65 } }
+
+// Contains (case-insensitive)
+const containsQuery: Where = { title: { contains: 'payload' } }
+
+// Like (all words present)
+const likeQuery: Where = { description: { like: 'cms headless' } }
+
+// In/not in
+const inQuery: Where = { category: { in: ['tech', 'news'] } }
+
+// Exists
+const existsQuery: Where = { image: { exists: true } }
+
+// Near (point fields)
+const nearQuery: Where = { location: { near: '-122.4194,37.7749,10000' } }
+```
+
+## AND/OR Logic
+
+```ts
+import type { Where } from 'payload'
+
+const complexQuery: Where = {
+  or: [
+    { color: { equals: 'mint' } },
+    {
+      and: [{ color: { equals: 'white' } }, { featured: { equals: false } }],
+    },
+  ],
+}
+```
+
+## Nested Properties
+
+```ts
+import type { Where } from 'payload'
+
+const nestedQuery: Where = {
+  'author.role': { equals: 'editor' },
+  'meta.featured': { exists: true },
+}
+```
+
+## Local API
+
+```ts
+// Find documents
+const posts = await payload.find({
+  collection: 'posts',
+  where: {
+    status: { equals: 'published' },
+    'author.name': { contains: 'john' },
+  },
+  depth: 2,
+  limit: 10,
+  page: 1,
+  sort: '-createdAt',
+  locale: 'en',
+  select: {
+    title: true,
+    author: true,
+  },
+})
+
+// Find by ID
+const post = await payload.findByID({
+  collection: 'posts',
+  id: '123',
+  depth: 2,
+})
+
+// Create
+const post = await payload.create({
+  collection: 'posts',
+  data: {
+    title: 'New Post',
+    status: 'draft',
+  },
+})
+
+// Update
+await payload.update({
+  collection: 'posts',
+  id: '123',
+  data: {
+    status: 'published',
+  },
+})
+
+// Delete
+await payload.delete({
+  collection: 'posts',
+  id: '123',
+})
+
+// Count
+const count = await payload.count({
+  collection: 'posts',
+  where: {
+    status: { equals: 'published' },
+  },
+})
+```
+
+### Threading req Parameter
+
+When performing operations in hooks or nested operations, pass the `req` parameter to maintain transaction context:
+
+```ts
+// ✅ CORRECT: Pass req for transaction safety
+const afterChange: CollectionAfterChangeHook = async ({ doc, req }) => {
+  await req.payload.create({
+    collection: 'audit-log',
+    data: { action: 'created', docId: doc.id },
+    req, // Maintains transaction atomicity
+  })
+}
+
+// ❌ WRONG: Missing req breaks transaction
+const afterChange: CollectionAfterChangeHook = async ({ doc, req }) => {
+  await req.payload.create({
+    collection: 'audit-log',
+    data: { action: 'created', docId: doc.id },
+    // Missing req - runs in separate transaction
+  })
+}
+```
+
+This is critical for MongoDB replica sets and Postgres. See [ADAPTERS.md#threading-req-through-operations](ADAPTERS.md#threading-req-through-operations) for details.
+
+### Access Control in Local API
+
+**Important**: Local API bypasses access control by default (`overrideAccess: true`). When passing a `user` parameter, you must explicitly set `overrideAccess: false` to respect that user's permissions.
+
+```ts
+// ❌ WRONG: User is passed but access control is bypassed
+const posts = await payload.find({
+  collection: 'posts',
+  user: currentUser,
+  // Missing: overrideAccess: false
+  // Result: Operation runs with ADMIN privileges, ignoring user's permissions
+})
+
+// ✅ CORRECT: Respects user's access control permissions
+const posts = await payload.find({
+  collection: 'posts',
+  user: currentUser,
+  overrideAccess: false, // Required to enforce access control
+  // Result: User only sees posts they have permission to read
+})
+
+// Administrative operation (intentionally bypass access control)
+const allPosts = await payload.find({
+  collection: 'posts',
+  // No user parameter
+  // overrideAccess defaults to true
+  // Result: Returns all posts regardless of access control
+})
+```
+
+**When to use `overrideAccess: false`:**
+
+- Performing operations on behalf of a user
+- Testing access control logic
+- API routes that should respect user permissions
+- Any operation where `user` parameter is provided
+
+**When `overrideAccess: true` is appropriate:**
+
+- Administrative operations (migrations, seeds, cron jobs)
+- Internal system operations
+- Operations explicitly intended to bypass access control
+
+See [ACCESS-CONTROL.md#important-notes](ACCESS-CONTROL.md#important-notes) for more details.
+
+## REST API
+
+```ts
+import { stringify } from 'qs-esm'
+
+const query = {
+  status: { equals: 'published' },
+}
+
+const queryString = stringify(
+  {
+    where: query,
+    depth: 2,
+    limit: 10,
+  },
+  { addQueryPrefix: true },
+)
+
+const response = await fetch(`https://api.example.com/api/posts${queryString}`)
+const data = await response.json()
+```
+
+### REST Endpoints
+
+```txt
+GET    /api/{collection}           - Find documents
+GET    /api/{collection}/{id}      - Find by ID
+POST   /api/{collection}           - Create
+PATCH  /api/{collection}/{id}      - Update
+DELETE /api/{collection}/{id}      - Delete
+GET    /api/{collection}/count     - Count documents
+
+GET    /api/globals/{slug}         - Get global
+POST   /api/globals/{slug}         - Update global
+```
+
+## GraphQL
+
+```graphql
+query {
+  Posts(where: { status: { equals: published } }, limit: 10, sort: "-createdAt") {
+    docs {
+      id
+      title
+      author {
+        name
+      }
+    }
+    totalDocs
+    hasNextPage
+  }
+}
+
+mutation {
+  createPost(data: { title: "New Post", status: draft }) {
+    id
+    title
+  }
+}
+
+mutation {
+  updatePost(id: "123", data: { status: published }) {
+    id
+    status
+  }
+}
+
+mutation {
+  deletePost(id: "123") {
+    id
+  }
+}
+```
+
+## Performance Best Practices
+
+- Set `maxDepth` on relationships to prevent over-fetching
+- Use `select` to limit returned fields
+- Index frequently queried fields
+- Use `virtual` fields for computed data
+- Cache expensive operations in hook `context`
PATCH

echo "Gold patch applied."
