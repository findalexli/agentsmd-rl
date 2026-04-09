#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if [ -f "turbopack/crates/turbo-tasks/src/vc/README.md" ]; then
    if grep -q "Value cells represent the pending result" "turbopack/crates/turbo-tasks/src/vc/README.md" 2>/dev/null; then
        echo "Patch already applied."
        exit 0
    fi
fi

# Create the new README.md file first
cat > turbopack/crates/turbo-tasks/src/vc/README.md <<'README_EOF'
**Value cells** represent the pending result of a computation, similar to a cell in a spreadsheet. When a `Vc`'s contents change, the change is propagated by invalidating dependent tasks.

In order to get a reference to the pointed value, you need to `.await` the [`Vc<T>`] to get a [`ReadRef<T>`][`ReadRef`]:

```
let some_vc: Vc<T>;
let some_ref: ReadRef<T> = some_vc.await?;
some_ref.some_method_on_t();
```

The returned [`ReadRef<T>`][`ReadRef`] represents a [reference-counted][triomphe::Arc] snapshot of a cell's value at a given point in time.

## Understanding Cells

A **cell** is a storage location for data associated with a task. Cells provide:

- **Immutability**: Once a value is stored in a cell, it becomes immutable until that task is re-executed.
- **Recomputability**: If invalidated or cache evicted, a cell's contents can be re-computed by re-executing its associated task.
- **Dependency Tracking**: When a cell's contents are read (with `.await`), the reading task is marked as dependent on the cell.
- **Persistence**: Cells owned by persisted tasks are serializable using the [`bincode`] crate.

Cells are stored in arrays associated with the task that constructed them. A `Vc` can either point to a specific cell (this is a *"resolved"* cell), or the return value of a function (this is an *"unresolved"* cell).

<figure style="display: flex; flex-direction: column; justify-content: center;">
<img alt="A diagram showing where cells are stored in tasks" width="850px" src="https://h8dxkfmaphn8o0p3.public.blob.vercel-storage.com/rustdoc-images/RawVc.excalidraw.png">
<figcaption style="font-style: italic; font-size: 80%;">
<tt>TaskOutput</tt>s point to a specific task, and refer to the output cell for that task. <tt>TaskCell</tt>s point to a specific cell within a task. Task cells are stored in a table (conceptually a <tt>Map&lt;ValueTypeId, Vec&lt;SharedReference&gt;&gt</tt>) and are referenced by a pair of a type id and a sequentially allocated index.
</figcaption>
<!-- https://excalidraw.com/#json=Dfb59fd_4hUjwNkoSrL4y,PQ1myzskgKE3IKyESoiYPg -->
</figure>

## Constructing a Cell

Most types using the [`#[turbo_tasks::value]` macro][value-macro] are given a `.cell()` method. This method returns a `Vc` of the type.

Transparent wrapper types that use [`#[turbo_tasks::value(transparent)]`][value-macro] cannot define methods on their wrapped type, so instead the [`Vc::cell`] function can be used to construct these types.

[`Vc::cell`]: /rustdoc/turbo_tasks/struct.Vc.html#method.cell

## Updating a Cell

Every time a task runs, its cells are re-constructed.

When `.cell()` or `Vc::cell` is called, the cell counter for the `ValueTypeId` is incremented, and the value is compared to the previous execution's using `PartialEq`. If the value with that index differs, the cell is updated, and all dependent tasks are invalidated.

The compare-then-update behavior [can be overridden to always update and invalidate using the `cell = "new"` argument][value-macro].

Because cells are keyed by a combination of their type and construction order, **task functions should have a deterministic execution order**. A function with inconsistent ordering may result in wasted work by invalidating additional cells, though it will still give correct results:

- You should use types with deterministic behavior. If you plan to iterate over a collection, use [`IndexMap`], [`BTreeMap`], or [`FrozenMap`] in place of types like [`HashMap`] (which gives randomized iteration order).
- If you perform work in parallel within a single turbo-task, be careful not to construct cells inside the parts of your function that are executed across multiple threads. That can lead to accidentally non-deterministic behavior. Instead, collect results in parallel, and construct cells in the main thread after sorting the results.

[value-macro]: macro@crate::value
[`IndexMap`]: indexmap::IndexMap
[`BTreeMap`]: std::collections::BTreeMap
[`FrozenMap`]: turbo_frozenmap::FrozenMap
[`HashMap`]: std::collections::HashMap

## Reading `Vc`s

`Vc`s implement [`IntoFuture`] and can be `await`ed, but there are few key differences compared to a normal [`Future`]:

- The value pointed to by a `Vc` can be invalidated by changing dependencies or cache evicted, meaning that `await`ing a `Vc` multiple times can give different results. A [`ReadRef`] is snapshot of the underlying cell at a point in time.

- Reading (`await`ing) `Vc`s causes the current task to be tracked a dependent of the `Vc`'s task or task cell. When the read task or task cell changes, the current task may be re-executed.

- `Vc` types are always [`Copy`]. Most [`Future`]s are not. This works because `Vc`s are represented as a few ids or indices into data structures managed by the `turbo-tasks` framework. `Vc` types are not reference counted, but do support [tracing] for a hypothetical (unimplemented) garbage collector.

- An uncached [`turbo_tasks::function`] that returns a `Vc` [begins after being called, even if the `Vc` is not `await`ed](#execution-model).

[`IntoFuture`]: std::future::IntoFuture
[`Future`]: std::future::Future
[`ReadRef`]: crate::ReadRef
[`turbo_tasks::function`]: crate::function

## Subtypes

There are a couple of explicit "subtypes" of `Vc`. These can both be cheaply converted back into a `Vc`.

- **[`ResolvedVc`]:** *(aka [`RawVc::TaskCell`])* A reference to a cell constructed within a task, as part of a [`Vc::cell`] or `value_type.cell()` constructor. As the cell has been constructed at least once, the concrete type of the cell is known (allowing [downcasting][ResolvedVc::try_downcast]). This is stored as a combination of a task id, a type id, and a cell id.

- **[`OperationVc`]:** *(aka [`RawVc::TaskOutput`])* The synchronous return value of a [`turbo_tasks::function`]. Internally, this is stored using a task id. [`OperationVc`]s must first be [`connect`][crate::OperationVc::connect]ed before being read.

[`ResolvedVc`] is almost always preferred over the more awkward [`OperationVc`] API, but [`OperationVc`] can be useful when dealing with [collectibles], when you need to [read the result of a function with strong consistency][crate::OperationVc::read_strongly_consistent], or with [`State`].

These many representations are stored internally using a type-erased [`RawVc`]. Type erasure reduces the [monomorphization] (and therefore binary size and compilation time) required to support `Vc` and its subtypes.

This means that `Vc` often uses the same in-memory representation as a `ResolvedVc` or an `OperationVc`, but it does not expose the same methods (e.g. downcasting) because the exact memory representation is not statically defined.

|                 | Representation                     | Equality        | Downcasting                | Strong Consistency     | Collectibles      | [Non-Local]  |
|-----------------|------------------------------------|-----------------|----------------------------|------------------------|-------------------|--------------|
| [`Vc`]          | [One of many][RawVc]               | ❌ [Broken][eq] | ⚠️  After resolution        | ❌ Eventual            | ❌ No             | ❌ [No][loc] |
| [`ResolvedVc`]  | [Task Id + Type Id + Cell Id][rtc] | ✅ Yes\*        | ✅ [Yes, cheaply][resolve] | ❌ Eventual            | ❌ No             | ✅ Yes       |
| [`OperationVc`] | [Task Id][rto]                     | ✅ Yes\*        | ⚠️  After resolution        | ✅ [Supported][strong] | ✅ [Yes][collect] | ✅ Yes       |

*\* see the type's documentation for details*

[`ResolvedVc`]: crate::ResolvedVc
[`OperationVc`]: crate::OperationVc
[`turbo_tasks::function`]: crate::function
[`State`]: crate::State
[Non-Local]: crate::NonLocalValue
[rtc]: crate::RawVc::TaskCell
[rto]: crate::RawVc::TaskOutput
[loc]: #optimization-local-outputs
[eq]: #equality--hashing
[resolve]: crate::ResolvedVc::try_downcast
[strong]: crate::OperationVc::read_strongly_consistent
[collect]: crate::CollectiblesSource


## Equality & Hashing

Because `Vc`s can be equivalent but have different representation, it's not recommended to compare `Vc`s by equality. Instead, you should convert a `Vc` to an explicit subtype first (likely [`ResolvedVc`]). Future versions of `Vc` may not implement [`Eq`], [`PartialEq`], or [`Hash`].


## Execution Model

While task functions are expected to be side-effect free, their execution behavior is still important for performance reasons, or to code using [collectibles] to represent issues or side-effects.

Even if not awaited, uncached function calls are guaranteed to execute (potentially emitting collectibles) before the root task finishes or before the completion of any strongly consistent read containing their call. However, the exact point when that execution begins is an implementation detail. Functions may execute more than once if one of their dependencies is invalidated.

## Eventual Consistency

Because `turbo_tasks` is [eventually consistent], two adjacent `.await`s of the same `Vc<T>` may return different values. If this happens, the task will eventually be invalidated and re-executed by [a strongly consistent root task][crate::OperationVc::read_strongly_consistent]. Top-level tasks will panic if they attempt to perform an eventually consistent read of a `Vc`.

Tasks affected by a read inconsistency can return errors. These errors will be discarded by the strongly consistent root task. Tasks should never panic due to a potentially-inconsistent value stored in a `Vc`.

Currently, all inconsistent tasks are polled to completion. Future versions of the `turbo_tasks` library may drop tasks that have been identified as inconsistent after some time. As non-root tasks should not perform side-effects, this should be safe, though it may introduce some issues with cross-process resource management.

[eventually consistent]: https://en.wikipedia.org/wiki/Eventual_consistency


## Optimization: Local Outputs

In addition to the potentially-explicit "resolved" and "operation" representations of a `Vc`, there's another internal representation of a `Vc`, known as a "Local `Vc`", or [`RawVc::LocalOutput`].

This is a special case of the synchronous return value of a [`turbo_tasks::function`] when some of its arguments have not yet been resolved. These are stored in task-local state that is freed after their parent non-local task exits.

We prevent potentially-local `Vc`s from escaping the lifetime of a function using the [`NonLocalValue`] marker trait alongside some fallback runtime checks. We do this to avoid some ergonomic challenges that would come from using lifetime annotations with `Vc`.


[tracing]: crate::trace::TraceRawVcs
[`ReadRef`]: crate::ReadRef
[`turbo_tasks::function`]: crate::function
[monomorphization]: https://doc.rust-lang.org/book/ch10-01-syntax.html#performance-of-code-using-generics
[`State`]: crate::State
[book-cells]: https://turbopack-rust-docs.vercel.sh/turbo-engine/cells.html
[collectibles]: crate::CollectiblesSource
README_EOF

# Apply the remaining patches using sed commands

# Update .alexrc - add "dirty" to allowed words
sed -i 's/"dead",/"dead",\n    "dirty",/' .alexrc

# Update turbopack/crates/turbo-tasks/README.md - merge Cells into Vc description
sed -i 's/- \*\*\[Cells\]\[book-cells\]:\*\* The locations associated with tasks where values are stored. The contents of a cell can change after the reexecution of a function due to invalidation./- \*\*\[`Vc`s ("Value Cells")\]\[`Vc`\]:\*\* References to locations associated with tasks where values are stored. The contents of a cell can change after the reexecution of a function due to invalidation. A [`Vc`] can be read to get [a read-only reference][crate::ReadRef] to the stored data, representing a snapshot of that cell at that point in time./' turbopack/crates/turbo-tasks/README.md

# Remove the old separate bullet points from README.md
sed -i '/-\*\*\[`Vc`s ("Value Cells")\]\[`Vc`\]:\*\* A reference to a cell or a return value of a function./d' turbopack/crates/turbo-tasks/README.md
sed -i '/^A \[`Vc`\] can be read to get/d' turbopack/crates/turbo-tasks/README.md

# Update lib.rs - improve Vc description in value macro docs
sed -i 's/A \[`Vc`\] represents a (potentially lazy) memoized computation. Each \[`Vc`\]\'s value is placed/A [`Vc`] represents the result of a computation. Each [`Vc`]'"'"'s value is placed/' turbopack/crates/turbo-tasks/src/lib.rs
sed -i 's/into a cell associated with the current \[`TaskId`\]. That \[`Vc`\] object can be `await`ed to get/into a cell\n\/\/\/ associated with the current [`TaskId`]. That [`Vc`] object can be `await`ed to get/' turbopack/crates/turbo-tasks/src/lib.rs

# Update lib.rs - serialization documentation (bincode instead of serde)
sed -i 's/Affects serialization via \[`serde::Serialize`\] and \[`serde::Deserialize`\]. Serialization is/Affects serialization via [`bincode::Encode`] and [`bincode::Decode`]. Serialization is required/' turbopack/crates/turbo-tasks/src/lib.rs
sed -i 's/required for filesystem cache of tasks./required\n\/\/\/ for the filesystem cache of tasks./' turbopack/crates/turbo-tasks/src/lib.rs
sed -i 's/- \*\*`"auto"` \*\*(default)\*\*:\*\* Derives the serialization traits and enables serialization./- *\*`"auto"` *(default)*:** Derives the bincode traits and enables serialization./' turbopack/crates/turbo-tasks/src/lib.rs
sed -i 's/- \*\*`"custom"`:\*\* Prevents deriving the serialization traits, but still enables serialization/- *\*`"custom"`:** Prevents deriving the bincode traits, but still enables serialization/' turbopack/crates/turbo-tasks/src/lib.rs
sed -i 's/(you must manually implement \[`serde::Serialize`\] and \[`serde::Deserialize`\])./(you must manually implement [`bincode::Encode`] and [`bincode::Decode`])./' turbopack/crates/turbo-tasks/src/lib.rs

# Update lib.rs - shared flag documentation
sed -i 's/Makes the `cell()` method public so everyone can use it./This flag makes the macro-generated `.cell()` method public so everyone can use it./' turbopack/crates/turbo-tasks/src/lib.rs

# Add the additional documentation for non-transparent types
if ! grep -q "Non-transparent types are given a .cell() method" turbopack/crates/turbo-tasks/src/lib.rs; then
    sed -i '/This flag makes the macro-generated/a\/\/\/\n\/\/\/ Non-transparent types are given a `.cell()` method. That method returns a `Vc` of the type.\n\/\/\/\n\/\/\/ This option does not apply to wrapper types that use `transparent`. Those use the public\n\/\/\/ [`Vc::cell`] function for construction.' turbopack/crates/turbo-tasks/src/lib.rs
fi

# Update raw_vc.rs - fix Vc links
sed -i 's/\/\/\/ A type-erased representation of \[`Vc`\]\[crate::Vc\]./\/\/\/ A type-erased representation of [`Vc`]./' turbopack/crates/turbo-tasks/src/raw_vc.rs
sed -i 's/\/\/\/ required to support \[`Vc`\]\[crate::Vc\]./\/\/\/ required to support [`Vc`]./' turbopack/crates/turbo-tasks/src/raw_vc.rs
sed -i 's/\/\/\/ \/\/\/ This type is heavily used within the \[`Backend`\]/\/\/\/ [`Vc`]: crate::Vc\n\/\/\/ \/\/\/ This type is heavily used within the [`Backend`]/' turbopack/crates/turbo-tasks/src/raw_vc.rs

# Add Vc link to LocalOutput variant docs
sed -i 's/\/\/\/ for a fallback runtime assertion./\/\/\/ for a fallback runtime assertion.\n\/\/\/\n\/\/\/ [`Vc`]: crate::Vc/' turbopack/crates/turbo-tasks/src/raw_vc.rs

# Update resolved.rs - add Reading a ResolvedVc section
sed -i 's/\/\/\/ 3. Given a \[`Vc`\], use \[`.to_resolved().await?`\]\[Vc::to_resolved\]./\/\/\/ 3. Given a [`Vc`], use [`.to_resolved().await?`][Vc::to_resolved].\n\/\/\/\n\/\/\/\n\/\/\/ ## Reading a `ResolvedVc`\n\/\/\/\n\/\/\/ Even though a `Vc` may be resolved as a `ResolvedVc`, we must still use `.await?` to read it'"'"'s\n\/\/\/ value, as the value could be invalidated or cache-evicted./' turbopack/crates/turbo-tasks/src/vc/resolved.rs

# Update mod.rs - replace inline docs with include_str! and fix typo
# First, find and replace the doc comment with include_str!
sed -i 's/\/\/\/ A "Value Cell" (`Vc` for short) is a reference to a memoized computation result stored on the/#[doc = include_str!("README.md")]/' turbopack/crates/turbo-tasks/src/vc/mod.rs

# The above doesn't fully work - need to remove all the old inline docs
# Let's use a Python script for this complex modification
python3 << 'PYEOF'
import re

mod_rs_path = "turbopack/crates/turbo-tasks/src/vc/mod.rs"
content = open(mod_rs_path).read()

# Find the old doc comment block (from /// A "Value Cell" to the last line before #[must_use])
old_doc_pattern = r'/// A "Value Cell" \(`Vc` for short\) is a reference to a memoized computation result stored on the\n/// heap.*?\[collectibles\]: crate::CollectiblesSource\n'

new_doc = '#[doc = include_str!("README.md")]\n'

if re.search(old_doc_pattern, content, re.DOTALL):
    content = re.sub(old_doc_pattern, new_doc, content, flags=re.DOTALL)
    print("Replaced old doc comment with include_str!")
else:
    # Check if already replaced
    if '#[doc = include_str!("README.md")]' in content:
        print("Already has include_str!")
    else:
        print("WARNING: Could not find old doc pattern")

# Fix the typo: ResolvedVc<Box<dyn MyTrait>>.  -> ResolvedVc<Box<dyn MyTrait>>`. So
content = content.replace(
    "already had a `ResolvedVc<Box<dyn MyTrait>>.  So this function has a looser type constraint",
    "already had a `ResolvedVc<Box<dyn MyTrait>>`. So this function has a looser type constraint"
)

open(mod_rs_path, 'w').write(content)
print("Fixed typo in mod.rs")
PYEOF

echo "Patch applied successfully."
