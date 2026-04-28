#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uniwind

# Idempotency guard
if grep -qF "**Supported group parents**: `Pressable` (press + focus), `Text` (press \u2014 requir" "skills/uniwind/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/uniwind/SKILL.md b/skills/uniwind/SKILL.md
@@ -1650,10 +1650,11 @@ Paid upgrade with 100% API compatibility. Built on a 2nd-generation C++ engine f
 
 - **C++ style engine**: Forged on the 2nd-gen Unistyles C++ engine. Injects styles directly into the ShadowTree without triggering React re-renders — a direct, optimized highway between classNames and the native layer
 - **Performance**: Benchmarked at ~55ms (vs StyleSheet 49ms, traditional Uniwind 81ms, NativeWind 197ms) — near-native speed
-- **40+ className props** update without re-renders (all component bindings listed above)
+- **55+ className props** update without re-renders across 20 components (all component bindings listed above)
 - **Reanimated animations**: `animate-*` and `transition-*` via className (Reanimated v4)
 - **Native insets & runtime values**: Automatic safe area injection, device rotation, and font size updates — no `SafeAreaListener` setup needed
 - **Theme transitions**: Native animated transitions when switching themes (fade, slide, circle mask)
+- **Group variants**: Tailwind `group-active:*` / `group-focus:*` propagate parent interaction state through the C++ shadow tree with zero re-renders
 - **Priority support**: Don't let technical hurdles slow your team down
 
 Package: `"uniwind": "npm:uniwind-pro@latest"` in `package.json`.
@@ -1843,6 +1844,33 @@ import Animated, { FadeIn, FlipInXUp, LinearTransition } from 'react-native-rean
 
 No code changes needed — props connect directly to C++ engine, eliminating re-renders automatically.
 
+### Group Variants
+
+Tailwind `group` variants propagate parent interaction state to descendants through the C++ shadow tree. No re-renders, no context providers.
+
+```tsx
+// Basic group — descendants react to parent press
+<Pressable className="group p-4 bg-base rounded-xl">
+  <Text className="text-default group-active:text-primary">Press the card</Text>
+  <View className="size-8 bg-blue-500 rounded group-active:bg-red-500" />
+</Pressable>
+
+// Named groups — descendants pick which ancestor to follow
+<Pressable className="group/card p-4 bg-base rounded-xl">
+  <Pressable className="group/button px-3 py-1 bg-primary rounded">
+    <Text className="text-white group-active/card:opacity-50 group-active/button:font-bold">
+      Nested groups
+    </Text>
+  </Pressable>
+</Pressable>
+```
+
+**Supported variants**: `group-active:*` (press), `group-focus:*` (focus). Named variants: `group-active/{name}:*`, `group-focus/{name}:*`.
+
+**Supported group parents**: `Pressable` (press + focus), `Text` (press — requires `onPress`, even empty). `TouchableOpacity`, `TouchableHighlight`, `TouchableWithoutFeedback`, and `TextInput` do **not** act as group parents — wrap in a `Pressable` marked `group`.
+
+**Not supported**: `group-hover:*` (no pointer hover on native), `group-disabled:*` (parsed but no shadow tree trigger), arbitrary `group-[.selector]:*` variants, implicit `in-*` variants.
+
 ### Suspense Support
 
 Components inside React `Suspense` boundaries are handled correctly. While a subtree is suspended, Uniwind keeps the C++ shadow entries alive so theme updates and runtime changes (dark mode, orientation, etc.) still reach suspended nodes. When the tree unsuspends, styles are already up to date — no flash of stale theme.
PATCH

echo "Gold patch applied."
