#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotent: skip if already applied
if grep -q 'resolve_activated_extras' crates/uv-resolver/src/universal_marker.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-resolver/src/lock/export/mod.rs b/crates/uv-resolver/src/lock/export/mod.rs
index 25cafd363b0c7..e2bcffa6a4269 100644
--- a/crates/uv-resolver/src/lock/export/mod.rs
+++ b/crates/uv-resolver/src/lock/export/mod.rs
@@ -15,13 +15,13 @@ use uv_normalize::{ExtraName, GroupName, PackageName};
 use uv_pep508::MarkerTree;
 use uv_pypi_types::ConflictItem;

-use crate::graph_ops::{Reachable, marker_reachability};
+use crate::graph_ops::Reachable;
 use crate::lock::LockErrorKind;
 pub use crate::lock::export::metadata::Metadata;
 pub(crate) use crate::lock::export::pylock_toml::PylockTomlPackage;
 pub use crate::lock::export::pylock_toml::{PylockToml, PylockTomlErrorKind};
 pub use crate::lock::export::requirements_txt::RequirementsTxtExport;
-use crate::universal_marker::resolve_conflicts;
+use crate::universal_marker::resolve_activated_extras;
 use crate::{Installable, LockError, Package};

 pub mod cyclonedx_json;
@@ -57,16 +57,10 @@ impl<'lock> ExportableRequirements<'lock> {
         let size_guess = target.lock().packages.len();
         let mut graph = Graph::<Node<'lock>, Edge<'lock>>::with_capacity(size_guess, size_guess);
         let mut inverse = FxHashMap::with_capacity_and_hasher(size_guess, FxBuildHasher);
-        let mut selected_extras: FxHashMap<_, Vec<ExtraName>> =
-            FxHashMap::with_capacity_and_hasher(size_guess, FxBuildHasher);

         let mut queue: VecDeque<(&Package, Option<&ExtraName>)> = VecDeque::new();
         let mut seen = FxHashSet::default();
-        let mut conflicts = if target.lock().conflicts.is_empty() {
-            None
-        } else {
-            Some(FxHashMap::default())
-        };
+        let mut activated_items = FxHashMap::default();

         let root = graph.add_node(Node::Root);

@@ -87,39 +81,33 @@ impl<'lock> ExportableRequirements<'lock> {
                 })?;

             // Track the activated package in the list of known conflicts.
-            if let Some(conflicts) = conflicts.as_mut() {
-                conflicts.insert(ConflictItem::from(dist.id.name.clone()), MarkerTree::TRUE);
-            }
+            activated_items.insert(ConflictItem::from(dist.id.name.clone()), MarkerTree::TRUE);

             if groups.prod() {
                 // Add the workspace package to the graph.
                 let index = *inverse
                     .entry(&dist.id)
                     .or_insert_with(|| graph.add_node(Node::Package(dist)));
-                graph.add_edge(root, index, Edge::Prod(MarkerTree::TRUE));
+                graph.add_edge(
+                    root,
+                    index,
+                    Edge::Prod {
+                        marker: MarkerTree::TRUE,
+                        dep_extras: Vec::new(),
+                    },
+                );

                 // Track the activated project in the list of known conflicts.
-                if let Some(conflicts) = conflicts.as_mut() {
-                    conflicts.insert(ConflictItem::from(dist.id.name.clone()), MarkerTree::TRUE);
-                }
+                activated_items.insert(ConflictItem::from(dist.id.name.clone()), MarkerTree::TRUE);

                 // Push its dependencies on the queue.
                 queue.push_back((dist, None));
-                let mut root_extras = Vec::new();
                 for extra in extras.extra_names(dist.optional_dependencies.keys()) {
-                    root_extras.push(extra.clone());
                     queue.push_back((dist, Some(extra)));
-
-                    // Track the activated extra in the list of known conflicts.
-                    if let Some(conflicts) = conflicts.as_mut() {
-                        conflicts.insert(
-                            ConflictItem::from((dist.id.name.clone(), extra.clone())),
-                            MarkerTree::TRUE,
-                        );
-                    }
-                }
-                if !root_extras.is_empty() {
-                    selected_extras.insert(&dist.id, root_extras);
+                    activated_items.insert(
+                        ConflictItem::from((dist.id.name.clone(), extra.clone())),
+                        MarkerTree::TRUE,
+                    );
                 }
             }

@@ -137,12 +125,10 @@ impl<'lock> ExportableRequirements<'lock> {
                 .flatten()
             {
                 // Track the activated group in the list of known conflicts.
-                if let Some(conflicts) = conflicts.as_mut() {
-                    conflicts.insert(
-                        ConflictItem::from((dist.id.name.clone(), group.clone())),
-                        MarkerTree::TRUE,
-                    );
-                }
+                activated_items.insert(
+                    ConflictItem::from((dist.id.name.clone(), group.clone())),
+                    MarkerTree::TRUE,
+                );

                 if prune.contains(&dep.package_id.name) {
                     continue;
@@ -161,7 +147,11 @@ impl<'lock> ExportableRequirements<'lock> {
                 graph.add_edge(
                     root,
                     dep_index,
-                    Edge::Dev(group, dep.simplified_marker.as_simplified_marker_tree()),
+                    Edge::Dev {
+                        group,
+                        marker: dep.simplified_marker.as_simplified_marker_tree(),
+                        dep_extras: dep.extra.iter().collect(),
+                    },
                 );

                 // Push its dependencies on the queue.
@@ -245,7 +235,14 @@ impl<'lock> ExportableRequirements<'lock> {
                         .or_insert_with(|| graph.add_node(Node::Package(dist)));

                     // Add an edge from the root.
-                    graph.add_edge(root, dep_index, Edge::Prod(marker));
+                    graph.add_edge(
+                        root,
+                        dep_index,
+                        Edge::Prod {
+                            marker,
+                            dep_extras: requirement.extras.iter().collect(),
+                        },
+                    );

                     // Push its dependencies on the queue.
                     if seen.insert((&dist.id, None)) {
@@ -289,50 +286,21 @@ impl<'lock> ExportableRequirements<'lock> {
                     .entry(&dep.package_id)
                     .or_insert_with(|| graph.add_node(Node::Package(dep_dist)));

-                // Add an edge from the dependency.
-                let mut active_extras = selected_extras
-                    .get(&package.id)
-                    .cloned()
-                    .unwrap_or_default();
-                if let Some(extra) = extra {
-                    if !active_extras.contains(extra) {
-                        active_extras.push((*extra).clone());
-                    }
-                }
-                if !active_extras.is_empty() {
-                    match selected_extras.entry(&dep.package_id) {
-                        Entry::Occupied(mut entry) => {
-                            for extra in &active_extras {
-                                if !entry.get().contains(extra) {
-                                    entry.get_mut().push(extra.clone());
-                                }
-                            }
-                        }
-                        Entry::Vacant(entry) => {
-                            entry.insert(active_extras.clone());
-                        }
-                    }
-                }
-
+                let dep_extras = dep.extra.iter().collect::<Vec<_>>();
                 graph.add_edge(
                     index,
                     dep_index,
                     if let Some(extra) = extra {
-                        Edge::Optional(
+                        Edge::Optional {
                             extra,
-                            dep.simplified_marker
-                                .as_simplified_marker_tree()
-                                .simplify_extras(std::slice::from_ref(extra)),
-                        )
+                            marker: dep.simplified_marker.as_simplified_marker_tree(),
+                            dep_extras,
+                        }
                     } else {
-                        Edge::Prod(selected_extras.get(&package.id).map_or_else(
-                            || dep.simplified_marker.as_simplified_marker_tree(),
-                            |extras| {
-                                dep.simplified_marker
-                                    .as_simplified_marker_tree()
-                                    .simplify_extras(extras)
-                            },
-                        ))
+                        Edge::Prod {
+                            marker: dep.simplified_marker.as_simplified_marker_tree(),
+                            dep_extras,
+                        }
                     },
                 );

@@ -349,11 +317,7 @@ impl<'lock> ExportableRequirements<'lock> {
         }

         // Determine the reachability of each node in the graph.
-        let mut reachability = if let Some(conflicts) = conflicts.as_ref() {
-            conflict_marker_reachability(&graph, &[], conflicts)
-        } else {
-            marker_reachability(&graph, &[])
-        };
+        let mut reachability = conflict_marker_reachability(&graph, &[], &activated_items);

         // Collect all packages.
         let nodes = graph
@@ -405,18 +369,38 @@ enum Node<'lock> {
 /// An edge in the resolution graph, along with the marker that must be satisfied to traverse it.
 #[derive(Debug, Clone)]
 enum Edge<'lock> {
-    Prod(MarkerTree),
-    Optional(&'lock ExtraName, MarkerTree),
-    Dev(&'lock GroupName, MarkerTree),
+    Prod {
+        marker: MarkerTree,
+        dep_extras: Vec<&'lock ExtraName>,
+    },
+    Optional {
+        extra: &'lock ExtraName,
+        marker: MarkerTree,
+        dep_extras: Vec<&'lock ExtraName>,
+    },
+    Dev {
+        group: &'lock GroupName,
+        marker: MarkerTree,
+        dep_extras: Vec<&'lock ExtraName>,
+    },
 }

 impl Edge<'_> {
     /// Return the [`MarkerTree`] for this edge.
     fn marker(&self) -> &MarkerTree {
         match self {
-            Self::Prod(marker) => marker,
-            Self::Optional(_, marker) => marker,
-            Self::Dev(_, marker) => marker,
+            Self::Prod { marker, .. } => marker,
+            Self::Optional { marker, .. } => marker,
+            Self::Dev { marker, .. } => marker,
+        }
+    }
+
+    /// Return the dependency extras activated by traversing this edge.
+    fn dep_extras(&self) -> &[&ExtraName] {
+        match self {
+            Self::Prod { dep_extras, .. } => dep_extras,
+            Self::Optional { dep_extras, .. } => dep_extras,
+            Self::Dev { dep_extras, .. } => dep_extras,
         }
     }
 }
@@ -495,7 +479,11 @@ fn conflict_marker_reachability<'lock>(
         // Resolve any conflicts in the parent marker.
         reachability.entry(parent_index).and_modify(|marker| {
             let conflict_map = conflict_maps.get(&parent_index).unwrap_or(known_conflicts);
-            *marker = resolve_conflicts(*marker, conflict_map);
+            let scope_package = match &graph[parent_index] {
+                Node::Package(package) => Some(package.name()),
+                Node::Root => None,
+            };
+            *marker = resolve_activated_extras(*marker, scope_package, conflict_map);
         });

         // When we see an edge like `parent [dotenv]> flask`, we should take the reachability
@@ -510,10 +498,22 @@ fn conflict_marker_reachability<'lock>(
                 .cloned()
                 .unwrap_or_else(|| known_conflicts.clone());

+            if let Node::Package(child) = graph[child_edge.target()] {
+                for extra in child_edge.weight().dep_extras() {
+                    let item = ConflictItem::from((child.name().clone(), (*extra).clone()));
+                    parent_map.insert(item, parent_marker);
+                }
+            }
+
+            let scope_package = match &graph[parent_index] {
+                Node::Package(package) => Some(package.name()),
+                Node::Root => None,
+            };
+
             match child_edge.weight() {
-                Edge::Prod(marker) => {
-                    // Resolve any conflicts on the edge.
-                    let marker = resolve_conflicts(*marker, &parent_map);
+                Edge::Prod { marker, .. } => {
+                    // Resolve any active extras on the edge.
+                    let marker = resolve_activated_extras(*marker, scope_package, &parent_map);

                     // Propagate the edge to the known conflicts.
                     for value in parent_map.values_mut() {
@@ -523,9 +523,16 @@ fn conflict_marker_reachability<'lock>(
                     // Propagate the edge to the node itself.
                     parent_marker.and(marker);
                 }
-                Edge::Optional(extra, marker) => {
-                    // Resolve any conflicts on the edge.
-                    let marker = resolve_conflicts(*marker, &parent_map);
+                Edge::Optional { extra, marker, .. } => {
+                    // The optional extra is active for this edge itself, so add it before
+                    // resolving any active extras on the edge.
+                    if let Node::Package(parent) = graph[parent_index] {
+                        let item = ConflictItem::from((parent.name().clone(), (*extra).clone()));
+                        parent_map.insert(item, parent_marker);
+                    }
+
+                    // Resolve any active extras on the edge.
+                    let marker = resolve_activated_extras(*marker, scope_package, &parent_map);

                     // Propagate the edge to the known conflicts.
                     for value in parent_map.values_mut() {
@@ -534,16 +541,17 @@ fn conflict_marker_reachability<'lock>(

                     // Propagate the edge to the node itself.
                     parent_marker.and(marker);
-
-                    // Add a known conflict item for the extra.
+                }
+                Edge::Dev { group, marker, .. } => {
+                    // The dependency group is active for this edge itself, so add it before
+                    // resolving any active extras on the edge.
                     if let Node::Package(parent) = graph[parent_index] {
-                        let item = ConflictItem::from((parent.name().clone(), (*extra).clone()));
+                        let item = ConflictItem::from((parent.name().clone(), (*group).clone()));
                         parent_map.insert(item, parent_marker);
                     }
-                }
-                Edge::Dev(group, marker) => {
-                    // Resolve any conflicts on the edge.
-                    let marker = resolve_conflicts(*marker, &parent_map);
+
+                    // Resolve any active extras on the edge.
+                    let marker = resolve_activated_extras(*marker, scope_package, &parent_map);

                     // Propagate the edge to the known conflicts.
                     for value in parent_map.values_mut() {
@@ -552,12 +560,6 @@ fn conflict_marker_reachability<'lock>(

                     // Propagate the edge to the node itself.
                     parent_marker.and(marker);
-
-                    // Add a known conflict item for the group.
-                    if let Node::Package(parent) = graph[parent_index] {
-                        let item = ConflictItem::from((parent.name().clone(), (*group).clone()));
-                        parent_map.insert(item, parent_marker);
-                    }
                 }
             }

diff --git a/crates/uv-resolver/src/universal_marker.rs b/crates/uv-resolver/src/universal_marker.rs
index 09325384372e6..cf26e4e1857e7 100644
--- a/crates/uv-resolver/src/universal_marker.rs
+++ b/crates/uv-resolver/src/universal_marker.rs
@@ -710,8 +710,15 @@ impl<'a> ParsedRawExtra<'a> {
 ///
 /// If a conflict item isn't present in the map of known conflicts, it's assumed to be false in all
 /// environments.
-pub(crate) fn resolve_conflicts(
+/// Resolve unencoded package extra markers and conflict-encoded extra markers in a
+/// [`MarkerTree`] based on the conditions under which each item is known to be true.
+///
+/// When `scope_package` is set, unencoded package extras like `extra == 'cpu'` are interpreted
+/// relative to that package. Conflict-encoded extras and groups are resolved independent of
+/// `scope_package`.
+pub(crate) fn resolve_activated_extras(
     marker: MarkerTree,
+    scope_package: Option<&PackageName>,
     known_conflicts: &FxHashMap<ConflictItem, MarkerTree>,
 ) -> MarkerTree {
     if marker.is_true() || marker.is_false() {
@@ -805,6 +812,25 @@ pub(crate) fn resolve_conflicts(
                 }
             }

+            // Search for an unencoded package extra in the current package scope.
+            if !found {
+                if let Some(package) = scope_package {
+                    let conflict_item = ConflictItem::from((package.clone(), name.clone()));
+                    if let Some(conflict_marker) = known_conflicts.get(&conflict_item) {
+                        match operator {
+                            ExtraOperator::Equal => {
+                                or.and(*conflict_marker);
+                                found = true;
+                            }
+                            ExtraOperator::NotEqual => {
+                                or.and(conflict_marker.negate());
+                                found = true;
+                            }
+                        }
+                    }
+                }
+            }
+
             // If we didn't find the marker in the list of known conflicts, assume it's always
             // false.
             if !found {
@@ -1014,7 +1040,7 @@ mod tests {
     fn resolve() {
         let known_conflicts = create_known_conflicts([("foo", "sys_platform == 'darwin'")]);
         let cm = MarkerTree::from_str("(python_version >= '3.10' and extra == 'extra-3-pkg-foo') or (python_version < '3.10' and extra != 'extra-3-pkg-foo')").unwrap();
-        let cm = resolve_conflicts(cm, &known_conflicts);
+        let cm = resolve_activated_extras(cm, None, &known_conflicts);
         assert_eq!(
             cm.try_to_string().as_deref(),
             Some(
@@ -1024,7 +1050,7 @@ mod tests {

         let cm = MarkerTree::from_str("python_version >= '3.10' and extra == 'extra-3-pkg-foo'")
             .unwrap();
-        let cm = resolve_conflicts(cm, &known_conflicts);
+        let cm = resolve_activated_extras(cm, None, &known_conflicts);
         assert_eq!(
             cm.try_to_string().as_deref(),
             Some("python_full_version >= '3.10' and sys_platform == 'darwin'")
@@ -1032,7 +1058,31 @@ mod tests {

         let cm = MarkerTree::from_str("python_version >= '3.10' and extra == 'extra-3-pkg-bar'")
             .unwrap();
-        let cm = resolve_conflicts(cm, &known_conflicts);
+        let cm = resolve_activated_extras(cm, None, &known_conflicts);
+        assert!(cm.is_false());
+    }
+
+    #[test]
+    fn resolve_unencoded_package_extras() {
+        let known_conflicts = create_known_conflicts([("foo", "sys_platform == 'darwin'")]);
+        let package = create_package("pkg");
+
+        let cm = MarkerTree::from_str("python_version >= '3.10' and extra == 'foo'").unwrap();
+        let cm = resolve_activated_extras(cm, Some(&package), &known_conflicts);
+        assert_eq!(
+            cm.try_to_string().as_deref(),
+            Some("python_full_version >= '3.10' and sys_platform == 'darwin'")
+        );
+
+        let cm = MarkerTree::from_str("python_version >= '3.10' and extra != 'foo'").unwrap();
+        let cm = resolve_activated_extras(cm, Some(&package), &known_conflicts);
+        assert_eq!(
+            cm.try_to_string().as_deref(),
+            Some("python_full_version >= '3.10' and sys_platform != 'darwin'")
+        );
+
+        let cm = MarkerTree::from_str("python_version >= '3.10' and extra == 'bar'").unwrap();
+        let cm = resolve_activated_extras(cm, Some(&package), &known_conflicts);
         assert!(cm.is_false());
     }
 }

PATCH

echo "Patch applied successfully."
