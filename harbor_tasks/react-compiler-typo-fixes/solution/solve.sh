#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if fixes already applied
if grep -q "explicitly added/removed" compiler/CLAUDE.md 2>/dev/null; then
    echo "Fixes already applied, skipping"
    exit 0
fi

# Apply typo fixes
git apply - <<'PATCH'
diff --git a/compiler/CLAUDE.md b/compiler/CLAUDE.md
index 8de9c88fcf77..328be2c33f7d 100644
--- a/compiler/CLAUDE.md
+++ b/compiler/CLAUDE.md
@@ -37,7 +37,7 @@ yarn snap -u

 ## Version Control

-This repository uses Sapling (`sl`) for version control. Sapling is similar to Mercurial: there is not staging area, but new/deleted files must be explicitlyu added/removed.
+This repository uses Sapling (`sl`) for version control. Sapling is similar to Mercurial: there is not staging area, but new/deleted files must be explicitly added/removed.

 ```bash
 # Check status
diff --git a/compiler/packages/babel-plugin-react-compiler/src/Inference/InferMutationAliasingEffects.ts b/compiler/packages/babel-plugin-react-compiler/src/Inference/InferMutationAliasingEffects.ts
index ca9166263111..3c29d7260f25 100644
--- a/compiler/packages/babel-plugin-react-compiler/src/Inference/InferMutationAliasingEffects.ts
+++ b/compiler/packages/babel-plugin-react-compiler/src/Inference/InferMutationAliasingEffects.ts
@@ -513,7 +513,7 @@ function inferBlock(
     if (handlerParam != null) {
       CompilerError.invariant(state.kind(handlerParam) != null, {
         reason:
-          'Expected catch binding to be intialized with a DeclareLocal Catch instruction',
+          'Expected catch binding to be initialized with a DeclareLocal Catch instruction',
         loc: terminal.loc,
       });
       const effects: Array<AliasingEffect> = [];
diff --git a/compiler/packages/babel-plugin-react-compiler/src/ReactiveScopes/InferReactiveScopeVariables.ts b/compiler/packages/babel-plugin-react-compiler/src/ReactiveScopes/InferReactiveScopeVariables.ts
index efa8975a78af..cbc973efa8d1 100644
--- a/compiler/packages/babel-plugin-react-compiler/src/ReactiveScopes/InferReactiveScopeVariables.ts
+++ b/compiler/packages/babel-plugin-react-compiler/src/ReactiveScopes/InferReactiveScopeVariables.ts
@@ -143,7 +143,7 @@ export function inferReactiveScopeVariables(fn: HIRFunction): void {
   }

   /*
-   * Validate that all scopes have properly intialized, valid mutable ranges
+   * Validate that all scopes have properly initialized, valid mutable ranges
    * within the span of instructions for this function, ie from 1 to 1 past
    * the last instruction id.
    */
PATCH

echo "Successfully applied typo fixes"
