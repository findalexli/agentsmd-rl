#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q "ImmutableCapture can come from two sources:" compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
diff --git a/compiler/CLAUDE.md b/compiler/CLAUDE.md
index 460df2df5..0fade42b2 100644
--- a/compiler/CLAUDE.md
+++ b/compiler/CLAUDE.md
@@ -35,6 +35,20 @@ yarn snap -p <file-basename> -d
 yarn snap -u
 ```

+## Linting
+
+```bash
+# Run lint on the compiler source
+yarn workspace babel-plugin-react-compiler lint
+```
+
+## Formatting
+
+```bash
+# Run prettier on all files (from the react root directory, not compiler/)
+yarn prettier-all
+```
+
 ## Compiling Arbitrary Files

 Use `yarn snap compile` to compile any file (not just fixtures) with the React Compiler:
diff --git a/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts b/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts
index c49c51024..7da564205 100644
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
diff --git a/compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/error.validate-mutate-ref-arg-in-render.js b/compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/error.validate-mutate-ref-arg-in-render.js
index 10218fc61..8e75ec210 100644
--- a/compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/error.validate-mutate-ref-arg-in-render.js
+++ b/compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/error.validate-mutate-ref-arg-in-render.js
@@ -1,6 +1,8 @@
 // @validateRefAccessDuringRender:true
+import {mutate} from 'shared-runtime';
+
 function Foo(props, ref) {
-  console.log(ref.current);
+  mutate(ref.current);
   return <div>{props.bar}</div>;
 }

diff --git a/compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/panresponder-ref-in-callback.js b/compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/panresponder-ref-in-callback.js
new file mode 100644
index 000000000..93614bfee
--- /dev/null
+++ b/compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/panresponder-ref-in-callback.js
@@ -0,0 +1,21 @@
+// @flow
+import {PanResponder, Stringify} from 'shared-runtime';
+
+export default component Playground() {
+  const onDragEndRef = useRef(() => {});
+  useEffect(() => {
+    onDragEndRef.current = () => {
+      console.log('drag ended');
+    };
+  });
+  const panResponder = useMemo(
+    () =>
+      PanResponder.create({
+        onPanResponderTerminate: () => {
+          onDragEndRef.current();
+        },
+      }),
+    []
+  );
+  return <Stringify responder={panResponder} />;
+}
diff --git a/compiler/packages/snap/src/sprout/shared-runtime-type-provider.ts b/compiler/packages/snap/src/sprout/shared-runtime-type-provider.ts
index b01a204e7..229ee45b0 100644
--- a/compiler/packages/snap/src/sprout/shared-runtime-type-provider.ts
+++ b/compiler/packages/snap/src/sprout/shared-runtime-type-provider.ts
@@ -196,6 +196,44 @@ export function makeSharedRuntimeTypeProvider({
               ],
             },
           },
+          PanResponder: {
+            kind: 'object',
+            properties: {
+              create: {
+                kind: 'function',
+                positionalParams: [EffectEnum.Freeze],
+                restParam: null,
+                calleeEffect: EffectEnum.Read,
+                returnType: {kind: 'type', name: 'Any'},
+                returnValueKind: ValueKindEnum.Frozen,
+                aliasing: {
+                  receiver: '@receiver',
+                  params: ['@config'],
+                  rest: null,
+                  returns: '@returns',
+                  temporaries: [],
+                  effects: [
+                    {
+                      kind: 'Freeze',
+                      value: '@config',
+                      reason: ValueReasonEnum.KnownReturnSignature,
+                    },
+                    {
+                      kind: 'Create',
+                      into: '@returns',
+                      value: ValueKindEnum.Frozen,
+                      reason: ValueReasonEnum.KnownReturnSignature,
+                    },
+                    {
+                      kind: 'ImmutableCapture',
+                      from: '@config',
+                      into: '@returns',
+                    },
+                  ],
+                },
+              },
+            },
+          },
         },
       };
     } else if (moduleName === 'ReactCompilerKnownIncompatibleTest') {
diff --git a/compiler/packages/snap/src/sprout/shared-runtime.ts b/compiler/packages/snap/src/sprout/shared-runtime.ts
index f37ca8270..2a2265d70 100644
--- a/compiler/packages/snap/src/sprout/shared-runtime.ts
+++ b/compiler/packages/snap/src/sprout/shared-runtime.ts
@@ -421,4 +421,10 @@ export function typedMutate(x: any, v: any = null): void {
   x.property = v;
 }

+export const PanResponder = {
+  create(obj: any): any {
+    return obj;
+  },
+};
+
 export default typedLog;

PATCH


# Rebuild the snap package to pick up PanResponder type provider
cd /workspace/react/compiler
yarn workspace snap build || true

echo "Patch applied successfully."
