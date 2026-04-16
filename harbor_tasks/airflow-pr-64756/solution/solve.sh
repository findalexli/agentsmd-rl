#!/bin/bash
set -e

cd /workspace/airflow

# Idempotency check - skip if already patched
if grep -q "shlex.quote(key_path)" providers/git/src/airflow/providers/git/hooks/git.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply --verbose <<'PATCH'
diff --git a/providers/git/src/airflow/providers/git/hooks/git.py b/providers/git/src/airflow/providers/git/hooks/git.py
index 89c0abee82d6d..e9e69367aa772 100644
--- a/providers/git/src/airflow/providers/git/hooks/git.py
+++ b/providers/git/src/airflow/providers/git/hooks/git.py
@@ -25,6 +25,7 @@ import os
 import stat
 import tempfile
 from typing import Any
+from urllib.parse import quote as urlquote

 from airflow.providers.common.compat.sdk import AirflowException, BaseHook

@@ -109,25 +110,32 @@ class GitHook(BaseHook):
             raise AirflowException("Both 'key_file' and 'private_key' cannot be provided at the same time")
         self._process_git_auth_url()

+    _VALID_STRICT_HOST_KEY_CHECKING = frozenset({"yes", "no", "accept-new", "off", "ask"})
+
     def _build_ssh_command(self, key_path: str | None = None) -> str:
         parts = ["ssh"]

         if key_path:
-            parts.append(f"-i {key_path}")
+            parts.append(f"-i {shlex.quote(key_path)}")
             parts.append("-o IdentitiesOnly=yes")

+        if self.strict_host_key_checking not in self._VALID_STRICT_HOST_KEY_CHECKING:
+            raise ValueError(
+                f"Invalid strict_host_key_checking value: {self.strict_host_key_checking!r}. "
+                f"Must be one of {sorted(self._VALID_STRICT_HOST_KEY_CHECKING)}"
+            )
         parts.append(f"-o StrictHostKeyChecking={self.strict_host_key_checking}")

         if self.known_hosts_file:
-            parts.append(f"-o UserKnownHostsFile={self.known_hosts_file}")
+            parts.append(f"-o UserKnownHostsFile={shlex.quote(self.known_hosts_file)}")
         elif self.strict_host_key_checking == "no":
             parts.append("-o UserKnownHostsFile=/dev/null")

         if self.ssh_config_file:
-            parts.append(f"-F {self.ssh_config_file}")
+            parts.append(f"-F {shlex.quote(self.ssh_config_file)}")

         if self.host_proxy_cmd:
-            parts.append(f'-o ProxyCommand="{self.host_proxy_cmd}"')
+            parts.append(f"-o ProxyCommand={shlex.quote(self.host_proxy_cmd)}")

         if self.ssh_port:
             parts.append(f"-p {self.ssh_port}")
@@ -138,13 +146,17 @@ class GitHook(BaseHook):
         if not isinstance(self.repo_url, str):
             return
         if self.auth_token and self.repo_url.startswith("https://"):
-            self.repo_url = self.repo_url.replace("https://", f"https://{self.user_name}:{self.auth_token}@")
+            encoded_user = urlquote(self.user_name, safe="")
+            encoded_token = urlquote(self.auth_token, safe="")
+            self.repo_url = self.repo_url.replace("https://", f"https://{encoded_user}:{encoded_token}@", 1)
         elif self.auth_token and self.repo_url.startswith("http://"):
-            self.repo_url = self.repo_url.replace("http://", f"http://{self.user_name}:{self.auth_token}@")
+            encoded_user = urlquote(self.user_name, safe="")
+            encoded_token = urlquote(self.auth_token, safe="")
+            self.repo_url = self.repo_url.replace("http://", f"http://{encoded_user}:{encoded_token}@", 1)
         elif self.repo_url.startswith("http://"):
             # if no auth token, use the repo url as is
-            self.repo_url = self.repo_url
-        elif not self.repo_url.startswith("git@") or not self.repo_url.startswith("https://"):
+            pass
+        elif not self.repo_url.startswith("git@") and not self.repo_url.startswith("https://"):
             self.repo_url = os.path.expanduser(self.repo_url)

     def set_git_env(self, key: str | None = None) -> None:
diff --git a/providers/git/tests/unit/git/hooks/test_git.py b/providers/git/tests/unit/git/hooks/test_git.py
index f814dec6d37f1..38cc6ed5354f9 100644
--- a/providers/git/tests/unit/git/hooks/test_git.py
+++ b/providers/git/tests/unit/git/hooks/test_git.py
@@ -249,7 +249,7 @@ class TestGitHook:
         hook = GitHook(git_conn_id="git_with_proxy")
         with hook.configure_hook_env():
             cmd = hook.env["GIT_SSH_COMMAND"]
-            assert 'ProxyCommand="ssh -W %h:%p bastion.example.com"' in cmd
+            assert "ProxyCommand='ssh -W %h:%p bastion.example.com'" in cmd

     def test_known_hosts_file(self, create_connection_without_db):
         create_connection_without_db(
PATCH

echo "Patch applied successfully."
