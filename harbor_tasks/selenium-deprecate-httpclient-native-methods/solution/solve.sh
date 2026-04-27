#!/usr/bin/env bash
# Apply the gold patch from PR SeleniumHQ/selenium#17340.
# Patch is inlined as a HEREDOC — never fetched from the network.
set -euo pipefail

cd /workspace/selenium

# Idempotency: if the distinctive change is already applied, exit cleanly.
if grep -q "Interfaces must not expose the native classes" java/AGENTS.md 2>/dev/null; then
  echo "Patch already applied; nothing to do."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/java/AGENTS.md b/java/AGENTS.md
index a619c8e65210f..054894e1aa1a6 100644
--- a/java/AGENTS.md
+++ b/java/AGENTS.md
@@ -12,6 +12,9 @@
 See `java/TESTING.md`

 ## Code conventions
+### Interfaces
+- New methods added to existing interfaces must provide a default implementation, if possible.
+- Interfaces must not expose the native classes of their implementations.

 ### Logging
 ```java
diff --git a/java/src/org/openqa/selenium/remote/http/HttpClient.java b/java/src/org/openqa/selenium/remote/http/HttpClient.java
index 458909441724b..3ab3a73069f9d 100644
--- a/java/src/org/openqa/selenium/remote/http/HttpClient.java
+++ b/java/src/org/openqa/selenium/remote/http/HttpClient.java
@@ -46,7 +46,9 @@ default void close() {}
    * @param request the HTTP request to send
    * @param handler the BodyHandler that determines how to handle the response body
    * @return a CompletableFuture containing the HTTP response
+   * @deprecated use JdkHttpClient#httpClient() instead.
    */
+  @Deprecated(forRemoval = true)
   <T> CompletableFuture<java.net.http.HttpResponse<T>> sendAsyncNative(
       java.net.http.HttpRequest request, java.net.http.HttpResponse.BodyHandler<T> handler);

@@ -59,7 +61,9 @@ <T> CompletableFuture<java.net.http.HttpResponse<T>> sendAsyncNative(
    * @return the HTTP response
    * @throws java.io.IOException if an I/O error occurs
    * @throws InterruptedException if the operation is interrupted
+   * @deprecated use JdkHttpClient#httpClient() instead.
    */
+  @Deprecated(forRemoval = true)
   <T> java.net.http.HttpResponse<T> sendNative(
       java.net.http.HttpRequest request, java.net.http.HttpResponse.BodyHandler<T> handler)
       throws java.io.IOException, InterruptedException;
diff --git a/java/src/org/openqa/selenium/remote/http/jdk/JdkHttpClient.java b/java/src/org/openqa/selenium/remote/http/jdk/JdkHttpClient.java
index a9120c69328bc..e02a9613d8a1c 100644
--- a/java/src/org/openqa/selenium/remote/http/jdk/JdkHttpClient.java
+++ b/java/src/org/openqa/selenium/remote/http/jdk/JdkHttpClient.java
@@ -158,6 +158,11 @@ protected PasswordAuthentication getPasswordAuthentication() {
     this.client = builder.build();
   }

+  /** Will expose the underlying native HttpClient used. */
+  public java.net.http.HttpClient client() {
+    return client;
+  }
+
   @Override
   public WebSocket openSocket(HttpRequest request, WebSocket.Listener listener) {
     URI uri;
PATCH

echo "Gold patch applied."
