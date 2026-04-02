#!/bin/bash
set -euo pipefail

cd /workspace/react/compiler/packages/babel-plugin-react-compiler

# Check if already applied
if ! grep -q "retryErrors" src/Entrypoint/Program.ts 2>/dev/null; then
    echo "Patch already applied or not needed"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/Babel/BabelPlugin.ts b/src/Babel/BabelPlugin.ts
index ed74f4664953..6764e12f025c 100644
--- a/src/Babel/BabelPlugin.ts
+++ b/src/Babel/BabelPlugin.ts
@@ -11,7 +11,6 @@ import {
   injectReanimatedFlag,
   pipelineUsesReanimatedPlugin,
 } from '../Entrypoint/Reanimated';
-import validateNoUntransformedReferences from '../Entrypoint/ValidateNoUntransformedReferences';
 import {CompilerError} from '..';

 const ENABLE_REACT_COMPILER_TIMINGS =
@@ -64,19 +63,12 @@ export default function BabelPluginReactCompiler(
                 },
               };
             }
-            const result = compileProgram(prog, {
+            compileProgram(prog, {
               opts,
               filename: pass.filename ?? null,
               comments: pass.file.ast.comments ?? [],
               code: pass.file.code,
             });
-            validateNoUntransformedReferences(
-              prog,
-              pass.filename ?? null,
-              opts.logger,
-              opts.environment,
-              result,
-            );
             if (ENABLE_REACT_COMPILER_TIMINGS === true) {
               performance.mark(`${filename}:end`, {
                 detail: 'BabelPlugin:Program:end',
diff --git a/src/Entrypoint/Imports.ts b/src/Entrypoint/Imports.ts
index 2fef4cfabe59..15796d77a70e 100644
--- a/src/Entrypoint/Imports.ts
+++ b/src/Entrypoint/Imports.ts
@@ -19,7 +19,7 @@ import {getOrInsertWith} from '../Utils/utils';
 import {ExternalFunction, isHookName} from '../HIR/Environment';
 import {Err, Ok, Result} from '../Utils/Result';
 import {LoggerEvent, ParsedPluginOptions} from './Options';
-import {BabelFn, getReactCompilerRuntimeModule} from './Program';
+import {getReactCompilerRuntimeModule} from './Program';
 import {SuppressionRange} from './Suppression';

 export function validateRestrictedImports(
@@ -84,11 +84,6 @@ export class ProgramContext {
   // generated imports
   imports: Map<string, Map<string, NonLocalImportSpecifier>> = new Map();

-  /**
-   * Metadata from compilation
-   */
-  retryErrors: Array<{fn: BabelFn; error: CompilerError}> = [];
-
   constructor({
     program,
     suppressions,
diff --git a/src/Entrypoint/Options.ts b/src/Entrypoint/Options.ts
index 2e5c9313a935..e7818f82afba 100644
--- a/src/Entrypoint/Options.ts
+++ b/src/Entrypoint/Options.ts
@@ -228,8 +228,6 @@ const CompilerOutputModeSchema = z.enum([
   'ssr',
   // Build optimized for the client, with auto memoization
   'client',
-  // Build optimized for the client without auto memo
-  'client-no-memo',
   // Lint mode, the output is unused but validations should run
   'lint',
 ]);
diff --git a/src/Entrypoint/Program.ts b/src/Entrypoint/Program.ts
index de36ad218f7e..038cf60385bd 100644
--- a/src/Entrypoint/Program.ts
+++ b/src/Entrypoint/Program.ts
@@ -350,9 +350,6 @@ function isFilePartOfSources(
   return false;
 }

-export type CompileProgramMetadata = {
-  retryErrors: Array<{fn: BabelFn; error: CompilerError}>;
-};
 /**
  * Main entrypoint for React Compiler.
  *
@@ -363,7 +360,7 @@ export type CompileProgramMetadata = {
 export function compileProgram(
   program: NodePath<t.Program>,
   pass: CompilerPass,
-): CompileProgramMetadata | null {
+): void {
   /**
    * This is directly invoked by the react-compiler babel plugin, so exceptions
    * thrown by this function will fail the babel build.
@@ -376,7 +373,7 @@ export function compileProgram(
    *   the outlined functions.
    */
   if (shouldSkipCompilation(program, pass)) {
-    return null;
+    return;
   }
   const restrictedImportsErr = validateRestrictedImports(
     program,
@@ -384,7 +381,7 @@ export function compileProgram(
   );
   if (restrictedImportsErr) {
     handleError(restrictedImportsErr, pass, null);
-    return null;
+    return;
   }
   /*
    * Record lint errors and critical errors as depending on Forget's config,
@@ -478,15 +475,11 @@ export function compileProgram(
       );
       handleError(error, programContext, null);
     }
-    return null;
+    return;
   }

   // Insert React Compiler generated functions into the Babel AST
   applyCompiledFunctions(program, compiledFns, pass, programContext);
-
-  return {
-    retryErrors: programContext.retryErrors,
-  };
 }

 type CompileSource = {
diff --git a/src/Entrypoint/ValidateNoUntransformedReferences.ts b/src/Entrypoint/ValidateNoUntransformedReferences.ts
deleted file mode 100644
index f612e1db070d..000000000000
--- a/src/Entrypoint/ValidateNoUntransformedReferences.ts
+++ /dev/null
@@ -1,162 +0,0 @@
-/**
- * Copyright (c) Meta Platforms, Inc. and affiliates.
- *
- * This source code is licensed under the MIT license found in the
- * LICENSE file in the root directory of this source tree.
- */
-
-import {NodePath} from '@babel/core';
-import * as t from '@babel/types';
-
-import {CompilerError, EnvironmentConfig, Logger} from '..';
-import {getOrInsertWith} from '../Utils/utils';
-import {GeneratedSource} from '../HIR';
-import {DEFAULT_EXPORT} from '../HIR/Environment';
-import {CompileProgramMetadata} from './Program';
-export default function validateNoUntransformedReferences(
-  path: NodePath<t.Program>,
-  filename: string | null,
-  logger: Logger | null,
-  env: EnvironmentConfig,
-  compileResult: CompileProgramMetadata | null,
-): void {
-  const moduleLoadChecks = new Map<
-    string,
-    Map<string, CheckInvalidReferenceFn>
-  >();
-  if (moduleLoadChecks.size > 0) {
-    transformProgram(path, moduleLoadChecks, filename, logger, compileResult);
-  }
-}
-
-type TraversalState = {
-  shouldInvalidateScopes: boolean;
-  program: NodePath<t.Program>;
-  logger: Logger | null;
-  filename: string | null;
-  transformErrors: Array<{fn: NodePath<t.Node>; error: CompilerError}>;
-};
-type CheckInvalidReferenceFn = (
-  paths: Array<NodePath<t.Node>>,
-  context: TraversalState,
-) => void;
-
-function validateImportSpecifier(
-  specifier: NodePath<t.ImportSpecifier>,
-  importSpecifierChecks: Map<string, CheckInvalidReferenceFn>,
-  state: TraversalState,
-): void {
-  const imported = specifier.get('imported');
-  const specifierName: string =
-    imported.node.type === 'Identifier'
-      ? imported.node.name
-      : imported.node.value;
-  const checkFn = importSpecifierChecks.get(specifierName);
-  if (checkFn == null) {
-    return;
-  }
-  if (state.shouldInvalidateScopes) {
-    state.shouldInvalidateScopes = false;
-    state.program.scope.crawl();
-  }
-
-  const local = specifier.get('local');
-  const binding = local.scope.getBinding(local.node.name);
-  CompilerError.invariant(binding != null, {
-    reason: 'Expected binding to be found for import specifier',
-    loc: local.node.loc ?? GeneratedSource,
-  });
-  checkFn(binding.referencePaths, state);
-}
-
-function validateNamespacedImport(
-  specifier: NodePath<t.ImportNamespaceSpecifier | t.ImportDefaultSpecifier>,
-  importSpecifierChecks: Map<string, CheckInvalidReferenceFn>,
-  state: TraversalState,
-): void {
-  if (state.shouldInvalidateScopes) {
-    state.shouldInvalidateScopes = false;
-    state.program.scope.crawl();
-  }
-  const local = specifier.get('local');
-  const binding = local.scope.getBinding(local.node.name);
-  const defaultCheckFn = importSpecifierChecks.get(DEFAULT_EXPORT);
-
-  CompilerError.invariant(binding != null, {
-    reason: 'Expected binding to be found for import specifier',
-    loc: local.node.loc ?? GeneratedSource,
-  });
-  const filteredReferences = new Map<
-    CheckInvalidReferenceFn,
-    Array<NodePath<t.Node>>
-  >();
-  for (const reference of binding.referencePaths) {
-    if (defaultCheckFn != null) {
-      getOrInsertWith(filteredReferences, defaultCheckFn, () => []).push(
-        reference,
-      );
-    }
-    const parent = reference.parentPath;
-    if (
-      parent != null &&
-      parent.isMemberExpression() &&
-      parent.get('object') === reference
-    ) {
-      if (parent.node.computed || parent.node.property.type !== 'Identifier') {
-        continue;
-      }
-      const checkFn = importSpecifierChecks.get(parent.node.property.name);
-      if (checkFn != null) {
-        getOrInsertWith(filteredReferences, checkFn, () => []).push(parent);
-      }
-    }
-  }
-
-  for (const [checkFn, references] of filteredReferences) {
-    checkFn(references, state);
-  }
-}
-function transformProgram(
-  path: NodePath<t.Program>,
-
-  moduleLoadChecks: Map<string, Map<string, CheckInvalidReferenceFn>>,
-  filename: string | null,
-  logger: Logger | null,
-  compileResult: CompileProgramMetadata | null,
-): void {
-  const traversalState: TraversalState = {
-    shouldInvalidateScopes: true,
-    program: path,
-    filename,
-    logger,
-    transformErrors: compileResult?.retryErrors ?? [],
-  };
-  path.traverse({
-    ImportDeclaration(path: NodePath<t.ImportDeclaration>) {
-      const importSpecifierChecks = moduleLoadChecks.get(
-        path.node.source.value,
-      );
-      if (importSpecifierChecks == null) {
-        return;
-      }
-      const specifiers = path.get('specifiers');
-      for (const specifier of specifiers) {
-        if (specifier.isImportSpecifier()) {
-          validateImportSpecifier(
-            specifier,
-            importSpecifierChecks,
-            traversalState,
-          );
-        } else {
-          validateNamespacedImport(
-            specifier as NodePath<
-              t.ImportNamespaceSpecifier | t.ImportDefaultSpecifier
-            >,
-            importSpecifierChecks,
-            state: TraversalState,
-          );
-        }
-      }
-    },
-  });
-}
diff --git a/src/HIR/Environment.ts b/src/HIR/Environment.ts
index 80caee2caf43..ba224d352506 100644
--- a/src/HIR/Environment.ts
+++ b/src/HIR/Environment.ts
@@ -629,9 +629,6 @@ export class Environment {
       case 'ssr': {
         return true;
       }
-      case 'client-no-memo': {
-        return false;
-      }
       default: {
         assertExhaustive(
           this.outputMode,
@@ -648,8 +645,7 @@ export class Environment {
         // linting also enables memoization so that we can check if manual memoization is preserved
         return true;
       }
-      case 'ssr':
-      case 'client-no-memo': {
+      case 'ssr': {
         return false;
       }
       default: {
@@ -668,9 +664,6 @@ export class Environment {
       case 'ssr': {
         return true;
       }
-      case 'client-no-memo': {
-        return false;
-      }
       default: {
         assertExhaustive(
           this.outputMode,
PATCH

echo "Patch applied successfully"
