#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cloudbase-mcp

# Idempotency guard
if grep -qF "const { data, error } = await auth.signInWithPassword({ username: 'test_user', p" "config/source/skills/auth-web/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/config/source/skills/auth-web/SKILL.md b/config/source/skills/auth-web/SKILL.md
@@ -121,10 +121,35 @@ const { data: loginData, error: loginError } = await data.verifyOtp({ token: '65
 ```
 
 **3. Password**
+
+All auth methods return `{ data, error }`. Always check `error` first:
+```js
+// Login — returns { data: { user, session }, error: null } on success
+const { data, error } = await auth.signInWithPassword({ username: 'test_user', password: 'pass123' })
+if (error) {
+  // Handle login failure (wrong password, user not found, provider not enabled)
+  console.error('Login failed:', error.message)
+  return false
+}
+// data.user.id is the uid; data.session contains the active session
+const uid = data.user.id
+
+// Also works with email or phone:
+// await auth.signInWithPassword({ email: 'user@example.com', password: 'pass123' })
+// await auth.signInWithPassword({ phone: '13800138000', password: 'pass123' })
+```
+
+**Checking login state (for route guards / auth checks):**
 ```js
-const usernameLogin = await auth.signInWithPassword({ username: 'test_user', password: 'pass123' })
-const emailLogin = await auth.signInWithPassword({ email: 'user@example.com', password: 'pass123' })
-const phoneLogin = await auth.signInWithPassword({ phone: '13800138000', password: 'pass123' })
+// Use auth.getLoginState() to get the current session.
+// IMPORTANT: uid alone is NOT enough — when the SDK is initialized with a
+// publishableKey it may create an anonymous session that also has a uid.
+// Route guards must reject anonymous sessions explicitly.
+const loginState = await auth.getLoginState()
+const isRealLogin = !!loginState
+  && !!loginState.uid
+  && loginState.loginType !== 'ANONYMOUS'
+// Use isRealLogin (not just !!uid) to gate protected routes.
 ```
 
 **4. Registration**
@@ -167,11 +192,13 @@ const handleRegister = async () => {
 }
 
 const handleLogin = async () => {
-  const { error } = await auth.signInWithPassword({
+  const { data, error } = await auth.signInWithPassword({
     username,
     password,
   })
   if (error) throw error
+  // Login succeeded — data.user.id is the uid
+  return true
 }
 ```
 
PATCH

echo "Gold patch applied."
