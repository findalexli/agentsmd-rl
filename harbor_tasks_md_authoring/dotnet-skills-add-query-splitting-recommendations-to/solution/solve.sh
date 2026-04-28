#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "When you load multiple navigation collections via `Include()`, EF Core generates" "skills/data/efcore-patterns/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/data/efcore-patterns/SKILL.md b/skills/data/efcore-patterns/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: efcore-patterns
-description: Entity Framework Core best practices including NoTracking by default, migration management, dedicated migration services, and common pitfalls to avoid.
+description: Entity Framework Core best practices including NoTracking by default, query splitting for navigation collections, migration management, dedicated migration services, and common pitfalls to avoid.
 ---
 
 # Entity Framework Core Patterns
@@ -13,6 +13,7 @@ Use this skill when:
 - Managing database migrations
 - Integrating EF Core with .NET Aspire
 - Debugging change tracking issues
+- Loading multiple navigation collections efficiently (query splitting)
 
 ## Core Principles
 
@@ -544,6 +545,58 @@ builder.Services.AddDbContextFactory<ApplicationDbContext>(options =>
 
 ---
 
+## Pattern 6: Query Splitting to Prevent Cartesian Explosion
+
+When you load multiple navigation collections via `Include()`, EF Core generates a single query that can cause cartesian explosion. If you have 10 orders with 10 items each, you get 100 rows instead of 10 + 10.
+
+### Global Configuration (Recommended for Most Cases)
+
+Enable query splitting globally in your DbContext configuration:
+
+```csharp
+services.AddDbContext<ApplicationDbContext>(options =>
+    options.UseNpgsql(connectionString, npgsqlOptions =>
+        {
+            npgsqlOptions.UseQuerySplittingBehavior(QuerySplittingBehavior.SplitQuery);
+        }));
+```
+
+### Per-Query Override
+
+Use single query when you know it's more efficient:
+
+```csharp
+// Use single query when you know the structure is well-understood
+var orders = await dbContext.Orders
+    .Include(o => o.Items)
+    .Include(o => o.Payments)
+    .AsSingleQuery()  // Override global split behavior
+    .ToListAsync();
+```
+
+### Trade-offs
+
+| Behavior | Pros | Cons |
+|-----------|-------|-------|
+| SplitQuery | No cartesian explosion, better for large collections | Multiple round-trips, potential consistency issues |
+| SingleQuery | Single round-trip, transactional consistency | Cartesian explosion with multiple collections |
+
+**Recommendation**: Default to `SplitQuery` globally, override with `AsSingleQuery()` for specific queries where single-query is known to be better.
+
+### When to Prefer SingleQuery
+
+- Small, well-understood navigation graphs (2-3 levels)
+- Queries where all related data is always needed
+- Performance-critical paths where round-trip cost is lower than cartesian explosion
+
+### When to Prefer SplitQuery
+
+- Large or unpredictable navigation graphs
+- Many-to-many relationships
+- Queries loading collections that may not all be needed
+
+---
+
 ## Testing with EF Core
 
 ### In-Memory Provider (Unit Tests Only)
PATCH

echo "Gold patch applied."
