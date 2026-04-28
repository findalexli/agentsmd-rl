#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "**Read and write models are fundamentally different - they have different shapes" "skills/data/database-performance/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/data/database-performance/SKILL.md b/skills/data/database-performance/SKILL.md
@@ -2,6 +2,7 @@
 name: database-performance
 description: Database access patterns for performance. Separate read/write models, avoid N+1 queries, use AsNoTracking, apply row limits, and never do application-side joins. Works with EF Core and Dapper.
 invocable: false
+tags: [cqrs, performance, patterns]
 ---
 
 # Database Performance Patterns
@@ -27,55 +28,83 @@ Use this skill when:
 
 ---
 
-## Read/Write Model Separation
+## Read/Write Model Separation (CQRS Pattern)
 
-**Don't think of entities as table-scoped.** Separate your read models (queries) from write models (commands).
+**Read and write models are fundamentally different - they have different shapes, columns, and purposes.** Don't create a single "User" entity and reuse it everywhere.
+
+- **Read models** are denormalized, optimized for query efficiency, and return multiple projection types (UserProfile, UserSummary, UserDetailForAdmin)
+- **Write models** are normalized, validation-focused, and accept strongly-typed commands (CreateUserCommand, UpdateUserCommand)
 
 ### Architecture
 
 ```
 src/
   MyApp.Data/
     Users/
-      IUserReadStore.cs      # Read operations
-      IUserWriteStore.cs     # Write operations
+      # Read side - multiple optimized projections
+      IUserReadStore.cs
       PostgresUserReadStore.cs
+
+      # Write side - command handlers
+      IUserWriteStore.cs
       PostgresUserWriteStore.cs
+
+      # Read DTOs - lightweight, denormalized
+      UserProfile.cs
+      UserSummary.cs
+
+      # Write commands - validation-focused
+      CreateUserCommand.cs
+      UpdateUserCommand.cs
     Orders/
       IOrderReadStore.cs
       IOrderWriteStore.cs
-      PostgresOrderReadStore.cs
-      PostgresOrderWriteStore.cs
+      (similar structure...)
 ```
 
 ### Read Store Interface
 
 ```csharp
+// Read models: Multiple specialized projections optimized for different use cases
 public interface IUserReadStore
 {
+    // Returns detailed profile for single-user view
     Task<UserProfile?> GetByIdAsync(UserId id, CancellationToken ct = default);
+
+    // Returns lightweight info for lookups
     Task<UserProfile?> GetByEmailAsync(EmailAddress email, CancellationToken ct = default);
+
+    // Returns paginated summaries - only what the list view needs
     Task<IReadOnlyList<UserSummary>> GetAllAsync(int limit, UserId? cursor = null, CancellationToken ct = default);
+
+    // Boolean query - no entity needed
     Task<bool> EmailExistsAsync(EmailAddress email, CancellationToken ct = default);
 }
 ```
 
 ### Write Store Interface
 
 ```csharp
+// Write model: Accepts strongly-typed commands, minimal return values
 public interface IUserWriteStore
 {
+    // Returns only the created ID - caller doesn't need the full entity
     Task<UserId> CreateAsync(CreateUserCommand command, CancellationToken ct = default);
+
+    // Update validates command, returns void (success or throws)
     Task UpdateAsync(UserId id, UpdateUserCommand command, CancellationToken ct = default);
+
+    // Delete is simple and explicit
     Task DeleteAsync(UserId id, CancellationToken ct = default);
 }
 ```
 
-**Benefits:**
-- Read models are optimized for queries (projections, joins)
-- Write models focus on validation and business rules
-- No confusion about when to track changes
-- Easier to optimize independently
+**Key structural differences illustrated:**
+- Read store returns multiple different DTOs (UserProfile, UserSummary, bool flag)
+- Write store returns minimal data (just UserId on create) or void
+- Read queries are stateless projections - no tracking needed
+- Write operations focus on command validation, not retrieving data afterwards
+- Different databases/tables can back read vs write (eventual consistency pattern)
 
 ---
 
PATCH

echo "Gold patch applied."
