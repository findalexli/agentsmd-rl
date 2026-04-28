#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-cursorrules

# Idempotency guard
if grep -qF "\"Implement proper navigation using Expo Router\"," "rules/react-native-expo-cursorrules-prompt-file/.cursorrules"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/rules/react-native-expo-cursorrules-prompt-file/.cursorrules b/rules/react-native-expo-cursorrules-prompt-file/.cursorrules
@@ -5,7 +5,7 @@
 const reactNativeExpoBestPractices = [
   "Use functional components with hooks",
   "Utilize Expo SDK features and APIs",
-  "Implement proper navigation using React Navigation",
+  "Implement proper navigation using Expo Router",
   "Use Expo's asset system for images and fonts",
   "Implement proper error handling and crash reporting",
   "Utilize Expo's push notification system",
PATCH

echo "Gold patch applied."
