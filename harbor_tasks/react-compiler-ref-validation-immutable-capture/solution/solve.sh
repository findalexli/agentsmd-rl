#!/bin/bash
set -euo pipefail

# Check if already applied
if grep -q "ImmutableCapture case:" compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

cd /workspace/react

git apply - <<'PATCH'
diff --git a/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts b/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts
index c49c51024bc9..7da564205475 100644
--- a/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts
+++ b/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts
@@ -487,24 +487,26 @@ function validateNoRefAccessInRenderImpl(
              */
             if (!didError) {
               const isRefLValue = isUseRefType(instr.lvalue.identifier);
-              for (const operand of eachInstructionValueOperand(instr.value)) {
-                /**
-                 * By default we check that function call operands are not refs,
-                 * ref values, or functions that can access refs.
-                 */
-                if (
-                  isRefLValue ||
-                  (hookKind != null &&
-                    hookKind !== 'useState' &&
-                    hookKind !== 'useReducer')
-                ) {
+              if (
+                isRefLValue ||
+                (hookKind != null &&
+                  hookKind !== 'useState' &&
+                  hookKind !== 'useReducer')
+              ) {
+                for (const operand of eachInstructionValueOperand(
+                  instr.value,
+                )) {
                   /**
                    * Allow passing refs or ref-accessing functions when:
                    * 1. lvalue is a ref (mergeRefs pattern: `mergeRefs(ref1, ref2)`)
                    * 2. calling hooks (independently validated for ref safety)
                    */
                   validateNoDirectRefValueAccess(errors, operand, env);
-                } else if (interpolatedAsJsx.has(instr.lvalue.identifier.id)) {
+                }
+              } else if (interpolatedAsJsx.has(instr.lvalue.identifier.id)) {
+                for (const operand of eachInstructionValueOperand(
+                  instr.value,
+                )) {
                   /**
                    * Special case: the lvalue is passed as a jsx child
                    *
@@ -513,7 +515,98 @@ function validateNoRefAccessInRenderImpl(
                    * render function which attempts to obey the rules.
                    */
                   validateNoRefValueAccess(errors, env, operand);
-                } else {
+                }
+              } else if (hookKind == null && instr.effects != null) {
+                /**
+                 * For non-hook functions with known aliasing effects, use the
+                 * effects to determine what validation to apply for each place.
+                 * Track visited id:kind pairs to avoid duplicate errors.
+                 */
+                const visitedEffects: Set<string> = new Set();
+                for (const effect of instr.effects) {
+                  let place: Place | null = null;
+                  let validation: 'ref-passed' | 'direct-ref' | 'none' = 'none';
+                  switch (effect.kind) {
+                    case 'Freeze': {
+                      place = effect.value;
+                      validation = 'direct-ref';
+                      break;
+                    }
+                    case 'Mutate':
+                    case 'MutateTransitive':
+                    case 'MutateConditionally':
+                    case 'MutateTransitiveConditionally': {
+                      place = effect.value;
+                      validation = 'ref-passed';
+                      break;
+                    }
+                    case 'Render': {
+                      place = effect.place;
+                      validation = 'ref-passed';
+                      break;
+                    }
+                    case 'Capture':
+                    case 'Alias':
+                    case 'MaybeAlias':
+                    case 'Assign':
+                    case 'CreateFrom': {
+                      place = effect.from;
+                      validation = 'ref-passed';
+                      break;
+                    }
+                    case 'ImmutableCapture': {
+                      /**
+                       * ImmutableCapture can come from two sources:
+                       * 1. A known signature that explicitly freezes the operand
+                       *    (e.g. PanResponder.create) — safe, the function doesn't
+                       *    call callbacks during render.
+                       * 2. Downgraded defaults when the operand is already frozen
+                       *    (e.g. foo(propRef)) — the function is unknown and may
+                       *    access the ref.
+                       *
+                       * We distinguish these by checking whether the same operand
+                       * also has a Freeze effect on this instruction, which only
+                       * comes from known signatures.
+                       */
+                      place = effect.from;
+                      const isFrozen = instr.effects.some(
+                        e =>
+                          e.kind === 'Freeze' &&
+                          e.value.identifier.id === effect.from.identifier.id,
+                      );
+                      validation = isFrozen ? 'direct-ref' : 'ref-passed';
+                      break;
+                    }
+                    case 'Create':
+                    case 'CreateFunction':
+                    case 'Apply':
+                    case 'Impure':
+                    case 'MutateFrozen':
+                    case 'MutateGlobal': {
+                      break;
+                    }
+                  }
+                  if (place !== null && validation !== 'none') {
+                    const key = `${place.identifier.id}:${validation}`;
+                    if (!visitedEffects.has(key)) {
+                      visitedEffects.add(key);
+                      if (validation === 'direct-ref') {
+                        validateNoDirectRefValueAccess(errors, place, env);
+                      } else {
+                        validateNoRefPassedToFunction(
+                          errors,
+                          env,
+                          place,
+                          place.loc,
+                        );
+                      }
+                    }
+                  }
+                }
+              } else {
+                for (const operand of eachInstructionValueOperand(
+                  instr.value,
+                )) {
                   validateNoRefPassedToFunction(
                     errors,
                     env,
PATCH

echo "Patch applied successfully"
