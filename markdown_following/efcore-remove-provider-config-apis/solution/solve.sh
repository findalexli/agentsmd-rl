#!/bin/bash
# Apply gold patch implementing RemoveExtension / WithoutExtension / RemoveDbContext APIs.
set -euo pipefail

cd /workspace/efcore

# Idempotency guard: bail out if the gold patch is already applied.
if grep -q "public abstract DbContextOptions WithoutExtension<TExtension>" \
        src/EFCore/DbContextOptions.cs 2>/dev/null; then
    echo "[solve.sh] gold patch already applied, skipping"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/EFCore/DbContextOptions.cs b/src/EFCore/DbContextOptions.cs
index 90b347ef80d..e18fd17ee31 100644
--- a/src/EFCore/DbContextOptions.cs
+++ b/src/EFCore/DbContextOptions.cs
@@ -93,6 +93,15 @@ public virtual TExtension GetExtension<TExtension>()
     public abstract DbContextOptions WithExtension<TExtension>(TExtension extension)
         where TExtension : class, IDbContextOptionsExtension;

+    /// <summary>
+    ///     Removes the given extension from the underlying options and creates a new
+    ///     <see cref="DbContextOptions" /> with the extension removed.
+    /// </summary>
+    /// <typeparam name="TExtension">The type of extension to be removed.</typeparam>
+    /// <returns>The new options instance with the extension removed.</returns>
+    public abstract DbContextOptions WithoutExtension<TExtension>()
+        where TExtension : class, IDbContextOptionsExtension;
+
     /// <summary>
     ///     This is an internal API that supports the Entity Framework Core infrastructure and not subject to
     ///     the same compatibility standards as public APIs. It may be changed or removed without notice in
diff --git a/src/EFCore/DbContextOptionsBuilder.cs b/src/EFCore/DbContextOptionsBuilder.cs
index 548d8868b8b..ff48245461c 100644
--- a/src/EFCore/DbContextOptionsBuilder.cs
+++ b/src/EFCore/DbContextOptionsBuilder.cs
@@ -786,6 +786,17 @@ public virtual DbContextOptionsBuilder UseAsyncSeeding(Func<DbContext, bool, Can
     void IDbContextOptionsBuilderInfrastructure.AddOrUpdateExtension<TExtension>(TExtension extension)
         => _options = _options.WithExtension(extension);

+    /// <summary>
+    ///     Removes the extension of the given type from the options. If no extension of the given type exists, this is a no-op.
+    /// </summary>
+    /// <remarks>
+    ///     This method is intended for use by extension methods to configure the context. It is not intended to be used in
+    ///     application code.
+    /// </remarks>
+    /// <typeparam name="TExtension">The type of extension to be removed.</typeparam>
+    void IDbContextOptionsBuilderInfrastructure.RemoveExtension<TExtension>()
+        => _options = _options.WithoutExtension<TExtension>();
+
     private DbContextOptionsBuilder WithOption(Func<CoreOptionsExtension, CoreOptionsExtension> withFunc)
     {
         ((IDbContextOptionsBuilderInfrastructure)this).AddOrUpdateExtension(
diff --git a/src/EFCore/DbContextOptions`.cs b/src/EFCore/DbContextOptions`.cs
index 067906b256f..4544c03f13b 100644
--- a/src/EFCore/DbContextOptions`.cs
+++ b/src/EFCore/DbContextOptions`.cs
@@ -57,6 +57,30 @@ public override DbContextOptions WithExtension<TExtension>(TExtension extension)
         return new DbContextOptions<TContext>(ExtensionsMap.SetItem(type, (extension, ordinal)));
     }

+    /// <inheritdoc />
+    public override DbContextOptions WithoutExtension<TExtension>()
+    {
+        var type = typeof(TExtension);
+        if (!ExtensionsMap.TryGetValue(type, out var removedValue))
+        {
+            return this;
+        }
+
+        var removedOrdinal = removedValue.Ordinal;
+        var newMap = ExtensionsMap.Remove(type);
+
+        // Renormalize ordinals for extensions that followed the removed one
+        foreach (var (key, value) in newMap)
+        {
+            if (value.Ordinal > removedOrdinal)
+            {
+                newMap = newMap.SetItem(key, (value.Extension, value.Ordinal - 1));
+            }
+        }
+
+        return new DbContextOptions<TContext>(newMap);
+    }
+
     /// <summary>
     ///     The type of context that these options are for (<typeparamref name="TContext" />).
     /// </summary>
diff --git a/src/EFCore/Extensions/EntityFrameworkServiceCollectionExtensions.cs b/src/EFCore/Extensions/EntityFrameworkServiceCollectionExtensions.cs
index 163a5ece1ff..41d4148ca45 100644
--- a/src/EFCore/Extensions/EntityFrameworkServiceCollectionExtensions.cs
+++ b/src/EFCore/Extensions/EntityFrameworkServiceCollectionExtensions.cs
@@ -1163,6 +1163,66 @@ public static IServiceCollection ConfigureDbContext
         return serviceCollection;
     }

+    /// <summary>
+    ///     Removes services for the given context type from the <see cref="IServiceCollection" />.
+    /// </summary>
+    /// <remarks>
+    ///     <para>
+    ///         This method can be used to remove the context registration in integration testing scenarios
+    ///         where a different database provider is used for tests.
+    ///     </para>
+    ///     <para>
+    ///         See <see href="https://aka.ms/efcore-docs-di">Using DbContext with dependency injection</see> for more information and examples.
+    ///     </para>
+    /// </remarks>
+    /// <typeparam name="TContext">The type of context to be removed.</typeparam>
+    /// <param name="serviceCollection">The <see cref="IServiceCollection" /> to remove services from.</param>
+    /// <param name="removeConfigurationOnly">
+    ///     If <see langword="true" />, only the <see cref="IDbContextOptionsConfiguration{TContext}" /> registrations will be removed;
+    ///     the context itself will remain registered. If <see langword="false" /> (the default), all services related to the context
+    ///     will be removed.
+    /// </param>
+    /// <returns>The same service collection so that multiple calls can be chained.</returns>
+    public static IServiceCollection RemoveDbContext
+        <[DynamicallyAccessedMembers(DbContext.DynamicallyAccessedMemberTypes)] TContext>(
+            this IServiceCollection serviceCollection,
+            bool removeConfigurationOnly = false)
+        where TContext : DbContext
+    {
+        Check.NotNull(serviceCollection);
+
+        if (removeConfigurationOnly)
+        {
+            var configurations = serviceCollection
+                .Where(d => d.ServiceType == typeof(IDbContextOptionsConfiguration<TContext>))
+                .ToList();
+
+            foreach (var descriptor in configurations)
+            {
+                serviceCollection.Remove(descriptor);
+            }
+        }
+        else
+        {
+            var descriptorsToRemove = serviceCollection
+                .Where(d => d.ServiceType == typeof(TContext)
+                    || d.ServiceType == typeof(DbContextOptions<TContext>)
+                    || d.ServiceType == typeof(IDbContextOptionsConfiguration<TContext>)
+                    || d.ServiceType == typeof(IDbContextFactorySource<TContext>)
+                    || d.ServiceType == typeof(IDbContextFactory<TContext>)
+                    || d.ServiceType == typeof(IDbContextPool<TContext>)
+                    || d.ServiceType == typeof(IScopedDbContextLease<TContext>))
+                .ToList();
+
+            foreach (var descriptor in descriptorsToRemove)
+            {
+                serviceCollection.Remove(descriptor);
+            }
+        }
+
+        return serviceCollection;
+    }
+
     private static void AddCoreServices<TContextImplementation>(
         IServiceCollection serviceCollection,
         Action<IServiceProvider, DbContextOptionsBuilder>? optionsAction,
diff --git a/src/EFCore/Infrastructure/IDbContextOptionsBuilderInfrastructure.cs b/src/EFCore/Infrastructure/IDbContextOptionsBuilderInfrastructure.cs
index bcad121c394..e1352df63a4 100644
--- a/src/EFCore/Infrastructure/IDbContextOptionsBuilderInfrastructure.cs
+++ b/src/EFCore/Infrastructure/IDbContextOptionsBuilderInfrastructure.cs
@@ -36,4 +36,21 @@ public interface IDbContextOptionsBuilderInfrastructure
     /// <param name="extension">The extension to be added.</param>
     void AddOrUpdateExtension<TExtension>(TExtension extension)
         where TExtension : class, IDbContextOptionsExtension;
+
+    /// <summary>
+    ///     <para>
+    ///         Removes the extension of the given type from the options. If no extension of the given type exists, this is a no-op.
+    ///     </para>
+    ///     <para>
+    ///         This method is intended for use by extension methods to configure the context. It is not intended to be used in
+    ///         application code.
+    ///     </para>
+    /// </summary>
+    /// <remarks>
+    ///     See <see href="https://aka.ms/efcore-docs-providers">Implementation of database providers and extensions</see>
+    ///     for more information and examples.
+    /// </remarks>
+    /// <typeparam name="TExtension">The type of extension to be removed.</typeparam>
+    void RemoveExtension<TExtension>()
+        where TExtension : class, IDbContextOptionsExtension;
 }
PATCH

echo "[solve.sh] gold patch applied successfully"
