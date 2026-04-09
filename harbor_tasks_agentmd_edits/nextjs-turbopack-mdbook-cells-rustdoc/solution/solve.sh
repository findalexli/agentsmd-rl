#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied (check for the include_str! line)
if grep -q '#\[doc = include_str!("README.md")\]' turbopack/crates/turbo-tasks/src/vc/mod.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/.alexrc b/.alexrc
index c5ad31fed33a7a..c66d234aed6c59 100644
--- a/.alexrc
+++ b/.alexrc
@@ -3,6 +3,7 @@
     "attacks",
     "color",
     "dead",
+    "dirty",
     "execute",
     "executed",
     "executes",
diff --git a/turbopack/crates/turbo-tasks/README.md b/turbopack/crates/turbo-tasks/README.md
index 00cdd124b4e2d0..66ea929406169e 100644
--- a/turbopack/crates/turbo-tasks/README.md
+++ b/turbopack/crates/turbo-tasks/README.md
@@ -12,10 +12,7 @@ Turbo Tasks defines 4 primitives:

 It defines some derived elements from that:
 - **[Tasks][book-tasks]:** An instance of a function together with its arguments.
-- **[Cells][book-cells]:** The locations associated with tasks where values are stored. The contents of a cell can change after the reexecution of a function due to invalidation.
-- **[`Vc`s ("Value Cells")][`Vc`]:** A reference to a cell or a return value of a function.
-
-A [`Vc`] can be read to get [a read-only reference][crate::ReadRef] to the stored data, representing a snapshot of that cell at that point in time.
+- **[`Vc`s ("Value Cells")][`Vc`]:** References to locations associated with tasks where values are stored. The contents of a cell can change after the reexecution of a function due to invalidation. A [`Vc`] can be read to get [a read-only reference][crate::ReadRef] to the stored data, representing a snapshot of that cell at that point in time.

 [blog-post]: https://nextjs.org/blog/turbopack-incremental-computation
 [cell id equality]: crate::ResolvedVc#equality--hashing
diff --git a/turbopack/crates/turbo-tasks/src/lib.rs b/turbopack/crates/turbo-tasks/src/lib.rs
index d18851172d9e27..27894e8e6c4fec 100644
--- a/turbopack/crates/turbo-tasks/src/lib.rs
+++ b/turbopack/crates/turbo-tasks/src/lib.rs
@@ -162,9 +162,9 @@ macro_rules! fxindexset {
 /// Implements [`VcValueType`] for the given `struct` or `enum`. These value types can be used
 /// inside of a "value cell" as [`Vc<...>`][Vc].
 ///
-/// A [`Vc`] represents a (potentially lazy) memoized computation. Each [`Vc`]'s value is placed
-/// into a cell associated with the current [`TaskId`]. That [`Vc`] object can be `await`ed to get
-/// [a read-only reference to the value contained in the cell][ReadRef].
+/// A [`Vc`] represents the result of a computation. Each [`Vc`]'s value is placed into a cell
+/// associated with the current [`TaskId`]. That [`Vc`] object can be `await`ed to get [a read-only
+/// reference to the value contained in the cell][ReadRef].
 ///
 /// This macro accepts multiple comma-separated arguments. For example:
 ///
@@ -200,17 +200,22 @@ macro_rules! fxindexset {
 ///
 /// ## `serialization = "..."`
 ///
-/// Affects serialization via [`serde::Serialize`] and [`serde::Deserialize`]. Serialization is
-/// required for filesystem cache of tasks.
+/// Affects serialization via [`bincode::Encode`] and [`bincode::Decode`]. Serialization is required
+/// for the filesystem cache of tasks.
 ///
-/// - **`"auto"` *(default)*:** Derives the serialization traits and enables serialization.
-/// - **`"custom"`:** Prevents deriving the serialization traits, but still enables serialization
-///   (you must manually implement [`serde::Serialize`] and [`serde::Deserialize`]).
+/// - **`"auto"` *(default)*:** Derives the bincode traits and enables serialization.
+/// - **`"custom"`:** Prevents deriving the bincode traits, but still enables serialization
+///   (you must manually implement [`bincode::Encode`] and [`bincode::Decode`]).
 /// - **`"none"`:** Disables serialization and prevents deriving the traits.
 ///
 /// ## `shared`
 ///
-/// Makes the `cell()` method public so everyone can use it.
+/// This flag makes the macro-generated `.cell()` method public so everyone can use it.
+///
+/// Non-transparent types are given a `.cell()` method. That method returns a `Vc` of the type.
+///
+/// This option does not apply to wrapper types that use `transparent`. Those use the public
+/// [`Vc::cell`] function for construction.
 ///
 /// ## `transparent`
 ///
diff --git a/turbopack/crates/turbo-tasks/src/raw_vc.rs b/turbopack/crates/turbo-tasks/src/raw_vc.rs
index 7c1949fb26ea5f..44b340372301a6 100644
--- a/turbopack/crates/turbo-tasks/src/raw_vc.rs
+++ b/turbopack/crates/turbo-tasks/src/raw_vc.rs
@@ -42,14 +42,15 @@ impl Display for CellId {
     }
 }

-/// A type-erased representation of [`Vc`][crate::Vc].
+/// A type-erased representation of [`Vc`].
 ///
 /// Type erasure reduces the [monomorphization] (and therefore binary size and compilation time)
-/// required to support [`Vc`][crate::Vc].
+/// required to support [`Vc`].
 ///
 /// This type is heavily used within the [`Backend`][crate::backend::Backend] trait, but should
 /// otherwise be treated as an internal implementation detail of `turbo-tasks`.
 ///
+/// [`Vc`]: crate::Vc
 /// [monomorphization]: https://doc.rust-lang.org/book/ch10-01-syntax.html#performance-of-code-using-generics
 #[derive(Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize, Encode, Decode)]
 pub enum RawVc {
@@ -68,6 +69,8 @@ pub enum RawVc {
     /// Local outputs are only valid within the context of their parent "non-local" task. Turbo
     /// Task's APIs are designed to prevent escapes of local [`Vc`]s, but [`ExecutionId`] is used
     /// for a fallback runtime assertion.
+    ///
+    /// [`Vc`]: crate::Vc
     LocalOutput(ExecutionId, LocalTaskId, TaskPersistence),
 }

diff --git a/turbopack/crates/turbo-tasks/src/vc/README.md b/turbopack/crates/turbo-tasks/src/vc/README.md
new file mode 100644
index 00000000000000..b4908a81ebe5c2
--- /dev/null
+++ b/turbopack/crates/turbo-tasks/src/vc/README.md
@@ -0,0 +1,149 @@
+**Value cells** represent the pending result of a computation, similar to a cell in a spreadsheet. When a `Vc`'s contents change, the change is propagated by invalidating dependent tasks.
+
+In order to get a reference to the pointed value, you need to `.await` the [`Vc<T>`] to get a [`ReadRef<T>`][`ReadRef`]:
+
+```
+let some_vc: Vc<T>;
+let some_ref: ReadRef<T> = some_vc.await?;
+some_ref.some_method_on_t();
+```
+
+The returned [`ReadRef<T>`][`ReadRef`] represents a [reference-counted][triomphe::Arc] snapshot of a cell's value at a given point in time.
+
+## Understanding Cells
+
+A **cell** is a storage location for data associated with a task. Cells provide:
+
+- **Immutability**: Once a value is stored in a cell, it becomes immutable until that task is re-executed.
+- **Recomputability**: If invalidated or cache evicted, a cell's contents can be re-computed by re-executing its associated task.
+- **Dependency Tracking**: When a cell's contents are read (with `.await`), the reading task is marked as dependent on the cell.
+- **Persistence**: Cells owned by persisted tasks are serializable using the [`bincode`] crate.
+
+Cells are stored in arrays associated with the task that constructed them. A `Vc` can either point to a specific cell (this is a *"resolved"* cell), or the return value of a function (this is an *"unresolved"* cell).
+
+<figure style="display: flex; flex-direction: column; justify-content: center;">
+<img alt="A diagram showing where cells are stored in tasks" width="850px" src="https://h8dxkfmaphn8o0p3.public.blob.vercel-storage.com/rustdoc-images/RawVc.excalidraw.png">
+<figcaption style="font-style: italic; font-size: 80%;">
+<tt>TaskOutput</tt>s point to a specific task, and refer to the output cell for that task. <tt>TaskCell</tt>s point to a specific cell within a task. Task cells are stored in a table (conceptually a <tt>Map&lt;ValueTypeId, Vec&lt;SharedReference&gt;&gt</tt>) and are referenced by a pair of a type id and a sequentially allocated index.
+</figcaption>
+<!-- https://excalidraw.com/#json=Dfb59fd_4hUjwNkoSrL4y,PQ1myzskgKE3IKyESoiYPg -->
+</figure>
+
+## Constructing a Cell
+
+Most types using the [`#[turbo_tasks::value]` macro][value-macro] are given a `.cell()` method. This method returns a `Vc` of the type.
+
+Transparent wrapper types that use [`#[turbo_tasks::value(transparent)]`][value-macro] cannot define methods on their wrapped type, so instead the [`Vc::cell`] function can be used to construct these types.
+
+[`Vc::cell`]: /rustdoc/turbo_tasks/struct.Vc.html#method.cell
+
+## Updating a Cell
+
+Every time a task runs, its cells are re-constructed.
+
+When `.cell()` or `Vc::cell` is called, the cell counter for the `ValueTypeId` is incremented, and the value is compared to the previous execution's using `PartialEq`. If the value with that index differs, the cell is updated, and all dependent tasks are invalidated.
+
+The compare-then-update behavior [can be overridden to always update and invalidate using the `cell = "new"` argument][value-macro].
+
+Because cells are keyed by a combination of their type and construction order, **task functions should have a deterministic execution order**. A function with inconsistent ordering may result in wasted work by invalidating additional cells, though it will still give correct results:
+
+- You should use types with deterministic behavior. If you plan to iterate over a collection, use [`IndexMap`], [`BTreeMap`], or [`FrozenMap`] in place of types like [`HashMap`] (which gives randomized iteration order).
+- If you perform work in parallel within a single turbo-task, be careful not to construct cells inside the parts of your function that are executed across multiple threads. That can lead to accidentally non-deterministic behavior. Instead, collect results in parallel, and construct cells in the main thread after sorting the results.
+
+[value-macro]: macro@crate::value
+[`IndexMap`]: indexmap::IndexMap
+[`BTreeMap`]: std::collections::BTreeMap
+[`FrozenMap`]: turbo_frozenmap::FrozenMap
+[`HashMap`]: std::collections::HashMap
+
+## Reading `Vc`s
+
+`Vc`s implement [`IntoFuture`] and can be `await`ed, but there are few key differences compared to a normal [`Future`]:
+
+- The value pointed to by a `Vc` can be invalidated by changing dependencies or cache evicted, meaning that `await`ing a `Vc` multiple times can give different results. A [`ReadRef`] is snapshot of the underlying cell at a point in time.
+
+- Reading (`await`ing) `Vc`s causes the current task to be tracked a dependent of the `Vc`'s task or task cell. When the read task or task cell changes, the current task may be re-executed.
+
+- `Vc` types are always [`Copy`]. Most [`Future`]s are not. This works because `Vc`s are represented as a few ids or indices into data structures managed by the `turbo-tasks` framework. `Vc` types are not reference counted, but do support [tracing] for a hypothetical (unimplemented) garbage collector.
+
+- An uncached [`turbo_tasks::function`] that returns a `Vc` [begins after being called, even if the `Vc` is not `await`ed](#execution-model).
+
+[`IntoFuture`]: std::future::IntoFuture
+[`Future`]: std::future::Future
+[`ReadRef`]: crate::ReadRef
+[`turbo_tasks::function`]: crate::function
+
+## Subtypes
+
+There are a couple of explicit "subtypes" of `Vc`. These can both be cheaply converted back into a `Vc`.
+
+- **[`ResolvedVc`]:** *(aka [`RawVc::TaskCell`])* A reference to a cell constructed within a task, as part of a [`Vc::cell`] or `value_type.cell()` constructor. As the cell has been constructed at least once, the concrete type of the cell is known (allowing [downcasting][ResolvedVc::try_downcast]). This is stored as a combination of a task id, a type id, and a cell id.
+
+- **[`OperationVc`]:** *(aka [`RawVc::TaskOutput`])* The synchronous return value of a [`turbo_tasks::function`]. Internally, this is stored using a task id. [`OperationVc`]s must first be [`connect`][crate::OperationVc::connect]ed before being read.
+
+[`ResolvedVc`] is almost always preferred over the more awkward [`OperationVc`] API, but [`OperationVc`] can be useful when dealing with [collectibles], when you need to [read the result of a function with strong consistency][crate::OperationVc::read_strongly_consistent], or with [`State`].
+
+These many representations are stored internally using a type-erased [`RawVc`]. Type erasure reduces the [monomorphization] (and therefore binary size and compilation time) required to support `Vc` and its subtypes.
+
+This means that `Vc` often uses the same in-memory representation as a `ResolvedVc` or an `OperationVc`, but it does not expose the same methods (e.g. downcasting) because the exact memory representation is not statically defined.
+
+|                 | Representation                     | Equality        | Downcasting                | Strong Consistency     | Collectibles      | [Non-Local]  |
+|-----------------|------------------------------------|-----------------|----------------------------|------------------------|-------------------|--------------|
+| [`Vc`]          | [One of many][RawVc]               | ❌ [Broken][eq] | ⚠️  After resolution        | ❌ Eventual            | ❌ No             | ❌ [No][loc] |
+| [`ResolvedVc`]  | [Task Id + Type Id + Cell Id][rtc] | ✅ Yes\*        | ✅ [Yes, cheaply][resolve] | ❌ Eventual            | ❌ No             | ✅ Yes       |
+| [`OperationVc`] | [Task Id][rto]                     | ✅ Yes\*        | ⚠️  After resolution        | ✅ [Supported][strong] | ✅ [Yes][collect] | ✅ Yes       |
+
+*\* see the type's documentation for details*
+
+[`ResolvedVc`]: crate::ResolvedVc
+[`OperationVc`]: crate::OperationVc
+[`turbo_tasks::function`]: crate::function
+[`State`]: crate::State
+[Non-Local]: crate::NonLocalValue
+[rtc]: crate::RawVc::TaskCell
+[rto]: crate::RawVc::TaskOutput
+[loc]: #optimization-local-outputs
+[eq]: #equality--hashing
+[resolve]: crate::ResolvedVc::try_downcast
+[strong]: crate::OperationVc::read_strongly_consistent
+[collect]: crate::CollectiblesSource
+
+
+## Equality & Hashing
+
+Because `Vc`s can be equivalent but have different representation, it's not recommended to compare `Vc`s by equality. Instead, you should convert a `Vc` to an explicit subtype first (likely [`ResolvedVc`]). Future versions of `Vc` may not implement [`Eq`], [`PartialEq`], or [`Hash`].
+
+
+## Execution Model
+
+While task functions are expected to be side-effect free, their execution behavior is still important for performance reasons, or to code using [collectibles] to represent issues or side-effects.
+
+Even if not awaited, uncached function calls are guaranteed to execute (potentially emitting collectibles) before the root task finishes or before the completion of any strongly consistent read containing their call. However, the exact point when that execution begins is an implementation detail. Functions may execute more than once if one of their dependencies is invalidated.
+
+## Eventual Consistency
+
+Because `turbo_tasks` is [eventually consistent], two adjacent `.await`s of the same `Vc<T>` may return different values. If this happens, the task will eventually be invalidated and re-executed by [a strongly consistent root task][crate::OperationVc::read_strongly_consistent]. Top-level tasks will panic if they attempt to perform an eventually consistent read of a `Vc`.
+
+Tasks affected by a read inconsistency can return errors. These errors will be discarded by the strongly consistent root task. Tasks should never panic due to a potentially-inconsistent value stored in a `Vc`.
+
+Currently, all inconsistent tasks are polled to completion. Future versions of the `turbo_tasks` library may drop tasks that have been identified as inconsistent after some time. As non-root tasks should not perform side-effects, this should be safe, though it may introduce some issues with cross-process resource management.
+
+[eventually consistent]: https://en.wikipedia.org/wiki/Eventual_consistency
+
+
+## Optimization: Local Outputs
+
+In addition to the potentially-explicit "resolved" and "operation" representations of a `Vc`, there's another internal representation of a `Vc`, known as a "Local `Vc`", or [`RawVc::LocalOutput`].
+
+This is a special case of the synchronous return value of a [`turbo_tasks::function`] when some of its arguments have not yet been resolved. These are stored in task-local state that is freed after their parent non-local task exits.
+
+We prevent potentially-local `Vc`s from escaping the lifetime of a function using the [`NonLocalValue`] marker trait alongside some fallback runtime checks. We do this to avoid some ergonomic challenges that would come from using lifetime annotations with `Vc`.
+
+
+[tracing]: crate::trace::TraceRawVcs
+[`ReadRef`]: crate::ReadRef
+[`turbo_tasks::function`]: crate::function
+[monomorphization]: https://doc.rust-lang.org/book/ch10-01-syntax.html#performance-of-code-using-generics
+[`State`]: crate::State
+[book-cells]: https://turbopack-rust-docs.vercel.sh/turbo-engine/cells.html
+[collectibles]: crate::CollectiblesSource
+diff --git a/turbopack/crates/turbo-tasks/src/vc/mod.rs b/turbopack/crates/turbo-tasks/src/vc/mod.rs
index 18beaba6e9571f..03ae3f13be67b8 100644
--- a/turbopack/crates/turbo-tasks/src/vc/mod.rs
+++ b/turbopack/crates/turbo-tasks/src/vc/mod.rs
@@ -42,127 +42,7 @@ use crate::{

 type VcReadTarget<T> = <<T as VcValueType>::Read as VcRead<T>>::Target;

-/// A "Value Cell" (`Vc` for short) is a reference to a memoized computation result stored on the
-/// heap or in filesystem cache, depending on the Turbo Engine backend implementation.
-///
-/// In order to get a reference to the pointed value, you need to `.await` the [`Vc<T>`] to get a
-/// [`ReadRef<T>`][`ReadRef`]:
-///
-/// ```
-/// let some_vc: Vc<T>;
-/// let some_ref: ReadRef<T> = some_vc.await?;
-/// some_ref.some_method_on_t();
-/// ```
-///
-/// `Vc`s are similar to a [`Future`] or a Promise with a few key differences:
-///
-/// - The value pointed to by a `Vc` can be invalidated by changing dependencies or cache evicted,
-///   meaning that `await`ing a `Vc` multiple times can give different results. A [`ReadRef`] is
-///   snapshot of the underlying cell at a point in time.
-///
-/// - Reading (`await`ing) `Vc`s causes the current task to be tracked a dependent of the `Vc`'s
-///   task or task cell. When the read task or task cell changes, the current task may be
-///   re-executed.
-///
-/// - `Vc` types are always [`Copy`]. Most [`Future`]s are not. This works because `Vc`s are
-///   represented as a few ids or indices into data structures managed by the `turbo-tasks`
-///   framework. `Vc` types are not reference counted, but do support [tracing] for a hypothetical
-///   (unimplemented) garbage collector.
-///
-/// - Unlike futures (but like promises), the work that a `Vc` represents [begins execution even if
-///   the `Vc` is not `await`ed](#execution-model).
-///
-/// For a more in-depth explanation of the concepts behind value cells, [refer to the Turbopack
-/// book][book-cells].
-///
-///
-/// ## Subtypes
-///
-/// There are a couple of explicit "subtypes" of `Vc`. These can both be cheaply converted back into
-/// a `Vc`.
-///
-/// - **[`ResolvedVc`]:** *(aka [`RawVc::TaskCell`])* A reference to a cell constructed within a
-///   task, as part of a [`Vc::cell`] or `value_type.cell()` constructor. As the cell has been
-///   constructed at least once, the concrete type of the cell is known (allowing
-///   [downcasting][ResolvedVc::try_downcast]). This is stored as a combination of a task id, a type
-///   id, and a cell id.
-///
-/// - **[`OperationVc`]:** *(aka [`RawVc::TaskOutput`])* The synchronous return value of a
-///   [`turbo_tasks::function`]. Internally, this is stored using a task id. Exact type information
-///   of trait types (i.e. `Vc<Box<dyn Trait>>`) is not known because the function may not have
-///   finished execution yet. [`OperationVc`]s must first be [`connect`][OperationVc::connect]ed
-///   before being read.
-///
-/// [`ResolvedVc`] is almost always preferred over the more awkward [`OperationVc`] API, but
-/// [`OperationVc`] can be useful when dealing with [collectibles], when you need to [read the
-/// result of a function with strong consistency][OperationVc::read_strongly_consistent], or with
-/// [`State`].
-///
-/// These many representations are stored internally using a type-erased [`RawVc`]. Type erasure
-/// reduces the [monomorphization] (and therefore binary size and compilation time) required to
-/// support `Vc` and its subtypes.
-///
-/// |                 | Representation                     | Equality        | Downcasting                | Strong Consistency     | Collectibles      | [Non-Local]  |
-/// |-----------------|------------------------------------|-----------------|----------------------------|------------------------|-------------------|--------------|
-/// | [`Vc`]          | [One of many][RawVc]               | ❌ [Broken][eq] | ⚠️  After resolution        | ❌ Eventual            | ❌ No             | ❌ [No][loc] |
-/// | [`ResolvedVc`]  | [Task Id + Type Id + Cell Id][rtc] | ✅ Yes\*        | ✅ [Yes, cheaply][resolve] | ❌ Eventual            | ❌ No             | ✅ Yes       |
-/// | [`OperationVc`] | [Task Id][rto]                     | ✅ Yes\*        | ⚠️  After resolution        | ✅ [Supported][strong] | ✅ [Yes][collect] | ✅ Yes       |
-///
-/// *\* see the type's documentation for details*
-///
-/// [Non-Local]: NonLocalValue
-/// [rtc]: RawVc::TaskCell
-/// [rto]: RawVc::TaskOutput
-/// [loc]: #optimization-local-outputs
-/// [eq]: #equality--hashing
-/// [resolve]: ResolvedVc::try_downcast
-/// [strong]: OperationVc::read_strongly_consistent
-/// [collect]: crate::CollectiblesSource
-///
-///
-/// ## Execution Model
-///
-/// While task functions are expected to be side-effect free, their execution behavior is still
-/// important for performance reasons, or to code using [collectibles] to represent issues or
-/// side-effects.
-///
-/// Function calls are neither "eager", nor "lazy". Even if not awaited, they are guaranteed to
-/// execute (potentially emitting collectibles) before the root task of any strongly consistent
-/// read containing their call. However, the exact point when that execution begins is an
-/// implementation detail. Functions may execute more than once due to dirty task invalidation.
-///
-///
-/// ## Equality & Hashing
-///
-/// Because `Vc`s can be equivalent but have different representation, it's not recommended to
-/// compare `Vc`s by equality. Instead, you should convert a `Vc` to an explicit subtype first
-/// (likely [`ResolvedVc`]). Future versions of `Vc` may not implement [`Eq`], [`PartialEq`], or
-/// [`Hash`].
-///
-///
-/// ## Optimization: Local Outputs
-///
-/// In addition to the potentially-explicit "resolved" and "operation" representations of a `Vc`,
-/// there's another internal representation of a `Vc`, known as a "Local `Vc`", or
-/// [`RawVc::LocalOutput`].
-///
-/// This is a special path of the synchronous return value of a [`turbo_tasks::function`] when some
-/// of its arguments have not yet been resolved. These are stored in task-local state that is freed
-/// after their parent non-local task exits.
-///
-/// We prevent potentially-local `Vc`s from escaping the lifetime of a function using the
-/// [`NonLocalValue`] marker trait alongside some fallback runtime checks. We do this to avoid some
-/// ergonomic challenges that would come from using lifetime annotations with `Vc`.
-///
-///
-/// [tracing]: crate::trace::TraceRawVcs
-/// [`ReadRef`]: crate::ReadRef
-/// [`turbo_tasks::function`]: crate::function
-/// [monomorphization]: https://doc.rust-lang.org/book/ch10-01-syntax.html#performance-of-code-using-generics
-/// [`State`]: crate::State
-/// [book-cells]: https://turbopack-rust-docs.vercel.sh/turbo-engine/cells.html
-/// [collectibles]: crate::CollectiblesSource
+#[doc = include_str!("README.md")]
 #[must_use]
 #[derive(Serialize, Deserialize, Encode, Decode)]
 #[serde(transparent, bound = "")]
@@ -437,7 +317,7 @@ where
     /// ```
     /// Using generics you could allow users to pass any compatible type, but if you specified
     /// `UpcastStrict<...>` instead of `Upcast<...>` you would disallow calling this function if you
-    /// already had a `ResolvedVc<Box<dyn MyTrait>>.  So this function has a looser type constraint
+    /// already had a `ResolvedVc<Box<dyn MyTrait>>`. So this function has a looser type constraint
     /// to make these functions easier to write and use.
     #[inline(always)]
     pub fn upcast_non_strict<K>(vc: Self) -> Vc<K>
diff --git a/turbopack/crates/turbo-tasks/src/vc/resolved.rs b/turbopack/crates/turbo-tasks/src/vc/resolved.rs
index ba6792bc0a8496..26ccf8836224a8 100644
--- a/turbopack/crates/turbo-tasks/src/vc/resolved.rs
+++ b/turbopack/crates/turbo-tasks/src/vc/resolved.rs
@@ -49,6 +49,12 @@ use crate::{
 /// 3. Given a [`Vc`], use [`.to_resolved().await?`][Vc::to_resolved].
 ///
 ///
+/// ## Reading a `ResolvedVc`
+///
+/// Even though a `Vc` may be resolved as a `ResolvedVc`, we must still use `.await?` to read it's
+/// value, as the value could be invalidated or cache-evicted.
+///
+///
 /// ## Equality & Hashing
 ///
 /// Equality between two `ResolvedVc`s means that both have an identical in-memory representation

PATCH

echo "Patch applied successfully."
