#!/bin/bash
# Solution script for selenium-execute-method-backward-compat task
# Applies the gold patch to make ExecuteMethod backward compatible

set -e

cd /workspace/selenium

# Idempotency check - skip if already applied
if grep -q "default <T> T executeAs" java/src/org/openqa/selenium/remote/ExecuteMethod.java 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/java/src/org/openqa/selenium/chromium/AddHasCasting.java b/java/src/org/openqa/selenium/chromium/AddHasCasting.java
index b52d55e50f0dc..7cb789ecf9b8a 100644
--- a/java/src/org/openqa/selenium/chromium/AddHasCasting.java
+++ b/java/src/org/openqa/selenium/chromium/AddHasCasting.java
@@ -18,7 +18,6 @@
 package org.openqa.selenium.chromium;

 import static java.util.Collections.emptyList;
-import static java.util.Objects.requireNonNullElse;

 import java.util.List;
 import java.util.Map;
@@ -56,7 +55,7 @@ public HasCasting getImplementation(Capabilities capabilities, ExecuteMethod exe
     return new HasCasting() {
       @Override
       public List<Map<String, String>> getCastSinks() {
-        return requireNonNullElse(executeMethod.execute(GET_CAST_SINKS, null), emptyList());
+        return executeMethod.execute(GET_CAST_SINKS, null, emptyList());
       }

       @Override
@@ -82,7 +81,7 @@ public void startTabMirroring(String deviceName) {

       @Override
       public String getCastIssueMessage() {
-        return executeMethod.executeRequired(GET_CAST_ISSUE_MESSAGE, null).toString();
+        return executeMethod.execute(GET_CAST_ISSUE_MESSAGE).toString();
       }

       @Override
diff --git a/java/src/org/openqa/selenium/chromium/AddHasCdp.java b/java/src/org/openqa/selenium/chromium/AddHasCdp.java
index e35998388ffb1..08e8225a1ec1b 100644
--- a/java/src/org/openqa/selenium/chromium/AddHasCdp.java
+++ b/java/src/org/openqa/selenium/chromium/AddHasCdp.java
@@ -51,8 +51,7 @@ public HasCdp getImplementation(Capabilities capabilities, ExecuteMethod execute
       Require.nonNull("Command name", commandName);
       Require.nonNull("Parameters", parameters);

-      return executeMethod.executeRequired(
-          EXECUTE_CDP, Map.of("cmd", commandName, "params", parameters));
+      return executeMethod.executeAs(EXECUTE_CDP, Map.of("cmd", commandName, "params", parameters));
     };
   }
 }
diff --git a/java/src/org/openqa/selenium/chromium/AddHasNetworkConditions.java b/java/src/org/openqa/selenium/chromium/AddHasNetworkConditions.java
index 3a045c37d8170..d7774d040297e 100644
--- a/java/src/org/openqa/selenium/chromium/AddHasNetworkConditions.java
+++ b/java/src/org/openqa/selenium/chromium/AddHasNetworkConditions.java
@@ -75,8 +75,7 @@ public HasNetworkConditions getImplementation(
     return new HasNetworkConditions() {
       @Override
       public ChromiumNetworkConditions getNetworkConditions() {
-        @SuppressWarnings("unchecked")
-        Map<String, Object> result = executeMethod.executeRequired(GET_NETWORK_CONDITIONS, null);
+        Map<String, Object> result = executeMethod.execute(GET_NETWORK_CONDITIONS);
         return new ChromiumNetworkConditions()
             .setOffline((Boolean) result.getOrDefault(OFFLINE, false))
             .setLatency(Duration.ofMillis((Long) result.getOrDefault(LATENCY, 0)))
diff --git a/java/src/org/openqa/selenium/firefox/AddHasContext.java b/java/src/org/openqa/selenium/firefox/AddHasContext.java
index 4369ab6cda1d2..bddb8de9e0058 100644
--- a/java/src/org/openqa/selenium/firefox/AddHasContext.java
+++ b/java/src/org/openqa/selenium/firefox/AddHasContext.java
@@ -69,7 +69,7 @@ public void setContext(FirefoxCommandContext context) {

       @Override
       public FirefoxCommandContext getContext() {
-        String context = executeMethod.executeRequired(GET_CONTEXT, null);
+        String context = executeMethod.execute(GET_CONTEXT);
         return FirefoxCommandContext.fromString(context);
       }
     };
diff --git a/java/src/org/openqa/selenium/firefox/AddHasExtensions.java b/java/src/org/openqa/selenium/firefox/AddHasExtensions.java
index 671199bd2e494..32726c6375bb6 100644
--- a/java/src/org/openqa/selenium/firefox/AddHasExtensions.java
+++ b/java/src/org/openqa/selenium/firefox/AddHasExtensions.java
@@ -95,7 +95,7 @@ public String installExtension(Path path, Boolean temporary) {
           throw new InvalidArgumentException(path + " is an invalid path", e);
         }

-        return executeMethod.executeRequired(
+        return executeMethod.executeAs(
             INSTALL_EXTENSION, Map.of("addon", encoded, "temporary", temporary));
       }

diff --git a/java/src/org/openqa/selenium/remote/ExecuteMethod.java b/java/src/org/openqa/selenium/remote/ExecuteMethod.java
index e348e5daf4604..b65238c0d4262 100644
--- a/java/src/org/openqa/selenium/remote/ExecuteMethod.java
+++ b/java/src/org/openqa/selenium/remote/ExecuteMethod.java
@@ -18,6 +18,7 @@
 package org.openqa.selenium.remote;

 import static java.util.Objects.requireNonNull;
+import static java.util.Objects.requireNonNullElse;

 import java.util.Map;
 import org.jspecify.annotations.NullMarked;
@@ -37,9 +38,35 @@ public interface ExecuteMethod {
    * @param parameters The parameters to execute that command with
    * @return The result of {@link Response#getValue()}.
    */
-  @Nullable <T> T execute(String commandName, @Nullable Map<String, ?> parameters);
+  @Nullable Object execute(String commandName, @Nullable Map<String, ?> parameters);

-  default <T> T executeRequired(String commandName, @Nullable Map<String, ?> parameters) {
-    return requireNonNull(execute(commandName, parameters));
+  /**
+   * Execute the given command and return the default value if the command return null.
+   *
+   * @return non-nullable value of type T.
+   */
+  @SuppressWarnings("unchecked")
+  default <T> T execute(String commandName, @Nullable Map<String, ?> parameters, T defaultValue) {
+    return (T) requireNonNullElse(execute(commandName, parameters), defaultValue);
+  }
+
+  /**
+   * Execute the given command and cast the returned value to T.
+   *
+   * @return non-nullable value of type T.
+   */
+  @SuppressWarnings("unchecked")
+  default <T> T executeAs(String commandName, @Nullable Map<String, ?> parameters) {
+    return (T) requireNonNull(execute(commandName, parameters));
+  }
+
+  /**
+   * Execute the given command without parameters and cast the returned value to T.
+   *
+   * @return non-nullable value of type T.
+   */
+  @SuppressWarnings("unchecked")
+  default <T> T execute(String commandName) {
+    return (T) requireNonNull(execute(commandName, null));
   }
 }
diff --git a/java/src/org/openqa/selenium/remote/FedCmDialogImpl.java b/java/src/org/openqa/selenium/remote/FedCmDialogImpl.java
index ed50cfab338fe..19d0ee4295986 100644
--- a/java/src/org/openqa/selenium/remote/FedCmDialogImpl.java
+++ b/java/src/org/openqa/selenium/remote/FedCmDialogImpl.java
@@ -46,7 +46,7 @@ public void selectAccount(int index) {
   @Nullable
   @Override
   public String getDialogType() {
-    return executeMethod.execute(DriverCommand.GET_FEDCM_DIALOG_TYPE, null);
+    return (String) executeMethod.execute(DriverCommand.GET_FEDCM_DIALOG_TYPE, null);
   }

   @Override
@@ -58,21 +58,20 @@ public void clickDialog() {
   @Nullable
   @Override
   public String getTitle() {
-    Map<String, String> result = executeMethod.executeRequired(DriverCommand.GET_FEDCM_TITLE, null);
+    Map<String, String> result = executeMethod.execute(DriverCommand.GET_FEDCM_TITLE);
     return result.get("title");
   }

   @Nullable
   @Override
   public String getSubtitle() {
-    Map<String, String> result = executeMethod.executeRequired(DriverCommand.GET_FEDCM_TITLE, null);
+    Map<String, String> result = executeMethod.execute(DriverCommand.GET_FEDCM_TITLE);
     return result.get("subtitle");
   }

   @Override
   public List<FederatedCredentialManagementAccount> getAccounts() {
-    List<Map<String, String>> accounts =
-        executeMethod.executeRequired(DriverCommand.GET_ACCOUNTS, null);
+    List<Map<String, String>> accounts = executeMethod.execute(DriverCommand.GET_ACCOUNTS);

     return accounts.stream()
         .map(map -> new FederatedCredentialManagementAccount(map))
diff --git a/java/src/org/openqa/selenium/remote/LocalExecuteMethod.java b/java/src/org/openqa/selenium/remote/LocalExecuteMethod.java
index 0d2b4e4cb5c36..84a6093dc8928 100644
--- a/java/src/org/openqa/selenium/remote/LocalExecuteMethod.java
+++ b/java/src/org/openqa/selenium/remote/LocalExecuteMethod.java
@@ -26,7 +26,7 @@
 class LocalExecuteMethod implements ExecuteMethod {
   @Nullable
   @Override
-  public <T> T execute(String commandName, @Nullable Map<String, ?> parameters) {
+  public Object execute(String commandName, @Nullable Map<String, ?> parameters) {
     throw new WebDriverException("Cannot execute remote command: " + commandName);
   }
 }
diff --git a/java/src/org/openqa/selenium/remote/RemoteExecuteMethod.java b/java/src/org/openqa/selenium/remote/RemoteExecuteMethod.java
index 8f28193c5718e..9be7a20bfd2be 100644
--- a/java/src/org/openqa/selenium/remote/RemoteExecuteMethod.java
+++ b/java/src/org/openqa/selenium/remote/RemoteExecuteMethod.java
@@ -31,9 +31,8 @@ public RemoteExecuteMethod(RemoteWebDriver driver) {
     this.driver = Require.nonNull("Remote WebDriver", driver);
   }

-  @SuppressWarnings("unchecked")
   @Override
-  public @Nullable <T> T execute(String commandName, @Nullable Map<String, ?> parameters) {
+  public @Nullable Object execute(String commandName, @Nullable Map<String, ?> parameters) {
     Response response;

     if (parameters == null || parameters.isEmpty()) {
@@ -42,7 +41,7 @@ public RemoteExecuteMethod(RemoteWebDriver driver) {
       response = driver.execute(commandName, parameters);
     }

-    return (T) response.getValue();
+    return response.getValue();
   }

   @Override
diff --git a/java/src/org/openqa/selenium/remote/RemoteLogs.java b/java/src/org/openqa/selenium/remote/RemoteLogs.java
index 7d0f230d6b324..267558e892e14 100644
--- a/java/src/org/openqa/selenium/remote/RemoteLogs.java
+++ b/java/src/org/openqa/selenium/remote/RemoteLogs.java
@@ -149,8 +149,7 @@ private Set<String> getAvailableLocalLogs() {

   @Override
   public Set<String> getAvailableLogTypes() {
-    List<String> rawList =
-        executeMethod.executeRequired(DriverCommand.GET_AVAILABLE_LOG_TYPES, null);
+    List<String> rawList = executeMethod.execute(DriverCommand.GET_AVAILABLE_LOG_TYPES);
     Set<String> builder = new LinkedHashSet<>();
     builder.addAll(rawList);
     builder.addAll(getAvailableLocalLogs());
diff --git a/java/src/org/openqa/selenium/safari/AddHasPermissions.java b/java/src/org/openqa/selenium/safari/AddHasPermissions.java
index 6aa4572387a89..f9edf3496eeea 100644
--- a/java/src/org/openqa/selenium/safari/AddHasPermissions.java
+++ b/java/src/org/openqa/selenium/safari/AddHasPermissions.java
@@ -67,7 +67,7 @@ public void setPermissions(String permission, boolean value) {

       @Override
       public Map<String, Boolean> getPermissions() {
-        Map<?, ?> resultMap = executeMethod.executeRequired(GET_PERMISSIONS, null);
+        Map<?, ?> resultMap = executeMethod.execute(GET_PERMISSIONS);

         Map<String, Boolean> permissionMap = new HashMap<>();
         for (Map.Entry<?, ?> entry : resultMap.entrySet()) {
diff --git a/java/test/org/openqa/selenium/remote/RemoteLogsTest.java b/java/test/org/openqa/selenium/remote/RemoteLogsTest.java
index e9044760a0e93..39631bbabd5c0 100644
--- a/java/test/org/openqa/selenium/remote/RemoteLogsTest.java
+++ b/java/test/org/openqa/selenium/remote/RemoteLogsTest.java
@@ -133,7 +133,7 @@ void throwsOnBogusRemoteLogsResponse() {
   @Test
   void canGetAvailableLogTypes() {
     List<String> remoteAvailableLogTypes = List.of(LogType.PROFILER, LogType.SERVER);
-    when(executeMethod.executeRequired(DriverCommand.GET_AVAILABLE_LOG_TYPES, null))
+    when(executeMethod.execute(DriverCommand.GET_AVAILABLE_LOG_TYPES))
         .thenReturn(remoteAvailableLogTypes);

     Set<String> localAvailableLogTypes = Set.of(LogType.PROFILER, LogType.CLIENT);
PATCH

echo "Patch applied successfully."
