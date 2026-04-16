#!/bin/bash
set -e

cd /workspace/selenium

# Idempotency check - skip if patch already applied
if grep -q 'platform_name.startswith("freebsd")' py/selenium/webdriver/common/selenium_manager.py; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/py/selenium/webdriver/common/selenium_manager.py b/py/selenium/webdriver/common/selenium_manager.py
index a4a8edd..9dfdbb0 100644
--- a/py/selenium/webdriver/common/selenium_manager.py
+++ b/py/selenium/webdriver/common/selenium_manager.py
@@ -89,18 +89,30 @@ class SeleniumManager:
         else:
             allowed = {
                 ("darwin", "any"): "macos/selenium-manager",
-                ("win32", "any"): "windows/selenium-manager.exe",
-                ("cygwin", "any"): "windows/selenium-manager.exe",
+                ("win32", "x86_64"): "windows/selenium-manager.exe",
+                ("cygwin", "x86_64"): "windows/selenium-manager.exe",
                 ("linux", "x86_64"): "linux/selenium-manager",
                 ("freebsd", "x86_64"): "linux/selenium-manager",
                 ("openbsd", "x86_64"): "linux/selenium-manager",
             }

-            arch = platform.machine() if sys.platform in ("linux", "freebsd", "openbsd") else "any"
-            if sys.platform in ["freebsd", "openbsd"]:
-                logger.warning(f"Selenium Manager binary may not be compatible with {sys.platform}; verify settings")
-
-            location = allowed.get((sys.platform, arch))
+            # some operating systems report x86-64 architecture as amd64/AMD64
+            platform_name = sys.platform
+            arch = "any" if platform_name == "darwin" else platform.machine().lower()
+            arch = "x86_64" if arch == "amd64" else arch
+
+            # in Python < 3.14, sys.platform appends version number to BSD platform names
+            if platform_name.startswith("freebsd"):
+                logger.warning(
+                    "Selenium Manager binary may not be compatible with FreeBSD; you may need to run "
+                    "'brandelf -t linux' on it and load linux64.ko"
+                )
+                platform_name = "freebsd"
+            elif platform_name.startswith("openbsd"):
+                logger.warning("Selenium Manager binary may not be compatible with OpenBSD; verify settings")
+                platform_name = "openbsd"
+
+            location = allowed.get((platform_name, arch))
             if location is None:
                 raise WebDriverException(f"Unsupported platform/architecture combination: {sys.platform}/{arch}")

diff --git a/py/test/unit/selenium/webdriver/common/selenium_manager_tests.py b/py/test/unit/selenium/webdriver/common/selenium_manager_tests.py
index 13edd55..7351f10 100644
--- a/py/test/unit/selenium/webdriver/common/selenium_manager_tests.py
+++ b/py/test/unit/selenium/webdriver/common/selenium_manager_tests.py
@@ -16,6 +16,7 @@
 # under the License.

 import json
+import logging
 import sys
 from pathlib import Path
 from unittest import mock
@@ -36,7 +37,6 @@ def test_gets_results(monkeypatch):
         mock.patch(lib_path + "._run", return_value=expected_output) as mock_run,
     ):
         SeleniumManager().binary_paths([])
-
         mock_get_binary.assert_called_once()
         expected_run_args = ["/path/to/sm", "--language-binding", "python", "--output", "json"]
         mock_run.assert_called_once_with(expected_run_args)
@@ -46,24 +46,28 @@ def test_uses_environment_variable(monkeypatch):
     sm_path = r"\path\to\manager" if sys.platform.startswith("win") else "path/to/manager"
     monkeypatch.setenv("SE_MANAGER_PATH", sm_path)
     monkeypatch.setattr(Path, "is_file", lambda _: True)
-
     binary = SeleniumManager()._get_binary()
-
     assert str(binary) == sm_path


 def test_uses_windows(monkeypatch):
     monkeypatch.setattr(sys, "platform", "win32")
+    monkeypatch.setattr("platform.machine", lambda: "AMD64")
     binary = SeleniumManager()._get_binary()
-
     project_root = Path(selenium.__file__).parent.parent
     assert binary == project_root.joinpath("selenium/webdriver/common/windows/selenium-manager.exe")


+def test_uses_windows_arm64(monkeypatch):
+    monkeypatch.setattr(sys, "platform", "win32")
+    monkeypatch.setattr("platform.machine", lambda: "ARM64")
+    with pytest.raises(WebDriverException, match="Unsupported platform/architecture combination: win32/arm64"):
+        SeleniumManager()._get_binary()
+
+
 def test_uses_linux(monkeypatch):
     monkeypatch.setattr(sys, "platform", "linux")
     monkeypatch.setattr("platform.machine", lambda: "x86_64")
-
     binary = SeleniumManager()._get_binary()
     project_root = Path(selenium.__file__).parent.parent
     assert binary == project_root.joinpath("selenium/webdriver/common/linux/selenium-manager")
@@ -72,7 +76,6 @@ def test_uses_linux(monkeypatch):
 def test_uses_linux_arm64(monkeypatch):
     monkeypatch.setattr(sys, "platform", "linux")
     monkeypatch.setattr("platform.machine", lambda: "arm64")
-
     with pytest.raises(WebDriverException, match="Unsupported platform/architecture combination: linux/arm64"):
         SeleniumManager()._get_binary()

@@ -80,14 +83,28 @@ def test_uses_linux_arm64(monkeypatch):
 def test_uses_mac(monkeypatch):
     monkeypatch.setattr(sys, "platform", "darwin")
     binary = SeleniumManager()._get_binary()
-
     project_root = Path(selenium.__file__).parent.parent
     assert binary == project_root.joinpath("selenium/webdriver/common/macos/selenium-manager")


+def test_uses_freebsd(monkeypatch, caplog):
+    monkeypatch.setattr(sys, "platform", "freebsd15")
+    monkeypatch.setattr("platform.machine", lambda: "amd64")
+    root = logging.getLogger()
+    caplog_handler = caplog.handler
+    old_handlers = root.handlers[:]
+    root.handlers = [caplog_handler]
+    try:
+        binary = SeleniumManager()._get_binary()
+        project_root = Path(selenium.__file__).parent.parent
+        assert binary == project_root.joinpath("selenium/webdriver/common/linux/selenium-manager")
+        assert "Selenium Manager binary may not be compatible with FreeBSD" in caplog.text
+    finally:
+        root.handlers = old_handlers
+
+
 def test_errors_if_not_file(monkeypatch):
     monkeypatch.setattr(Path, "is_file", lambda _: False)
-
     with pytest.raises(WebDriverException) as excinfo:
         SeleniumManager()._get_binary()
     assert "Unable to obtain working Selenium Manager binary" in str(excinfo.value)
@@ -96,7 +113,6 @@ def test_errors_if_not_file(monkeypatch):
 def test_errors_if_invalid_os(monkeypatch):
     monkeypatch.setattr(sys, "platform", "linux")
     monkeypatch.setattr("platform.machine", lambda: "invalid")
-
     with pytest.raises(WebDriverException) as excinfo:
         SeleniumManager()._get_binary()
     assert "Unsupported platform/architecture combination" in str(excinfo.value)
@@ -105,7 +121,6 @@ def test_errors_if_invalid_os(monkeypatch):
 def test_error_if_invalid_env_path(monkeypatch):
     sm_path = r"\path\to\manager" if sys.platform.startswith("win") else "path/to/manager"
     monkeypatch.setenv("SE_MANAGER_PATH", sm_path)
-
     with pytest.raises(WebDriverException) as excinfo:
         SeleniumManager()._get_binary()
     assert f"SE_MANAGER_PATH does not point to a file: {sm_path}" in str(excinfo.value)
PATCH

echo "Patch applied successfully."
