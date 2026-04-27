#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cloudbase-mcp

# Idempotency guard
if grep -qF "When the project already has `handleSendCode` / `handleRegister` or similar UI h" "config/source/skills/auth-web/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/config/source/skills/auth-web/SKILL.md b/config/source/skills/auth-web/SKILL.md
@@ -28,6 +28,7 @@ alwaysApply: false
 - Skipping publishable key and provider checks.
 - Replacing built-in Web auth with cloud function login logic.
 - Reusing this flow in Flutter, React Native, or native iOS/Android code.
+- Creating a detached helper file with `auth.signUp` / `verifyOtp` but never wiring it into the existing form handlers, so the actual button clicks still do nothing.
 
 ## Overview
 
@@ -102,6 +103,29 @@ const { data, error } = await auth.signUp({ phone: '13800138000', nickname: 'Use
 const { data: loginData, error: loginError } = await data.verifyOtp({ token: '123456' })
 ```
 
+When the project already has `handleSendCode` / `handleRegister` or similar UI handlers, wire the SDK calls there directly instead of leaving them commented out in `App.tsx`.
+
+```tsx
+const handleSendCode = async () => {
+  const { data, error } = await auth.signUp({
+    email,
+    name: username || email.split('@')[0],
+  })
+  if (error) throw error
+  setSignUpData(data)
+}
+
+const handleRegister = async () => {
+  if (!signUpData?.verifyOtp) throw new Error('Please send the code first')
+  const { error } = await signUpData.verifyOtp({
+    email,
+    token: code,
+    type: 'signup',
+  })
+  if (error) throw error
+}
+```
+
 **5. Anonymous**
 - Automatically use `auth-tool-cloudbase` turn on `Anonymous Login`
 ```js
PATCH

echo "Gold patch applied."
