#!/bin/bash
# Gold solution for superset-playwright-timeout task
# Applies the fix that propagates PlaywrightTimeout instead of swallowing it

set -e

cd /workspace/superset

# Idempotency check - skip if already patched
if grep -q "except PlaywrightTimeout:" superset/utils/webdriver.py && \
   grep -A1 "except PlaywrightTimeout:" superset/utils/webdriver.py | grep -q "raise$"; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/superset/utils/webdriver.py b/superset/utils/webdriver.py
index 416d3f0e5bf0..f38c67fd64c7 100644
--- a/superset/utils/webdriver.py
+++ b/superset/utils/webdriver.py
@@ -387,8 +387,7 @@ def get_screenshot(  # pylint: disable=too-many-locals, too-many-statements  # n
                     )

             except PlaywrightTimeout:
-                # raise again for the finally block, but handled above
-                pass
+                raise
             except PlaywrightError:
                 logger.exception(
                     "Encountered an unexpected error when requesting url %s", url
diff --git a/tests/unit_tests/utils/webdriver_test.py b/tests/unit_tests/utils/webdriver_test.py
index ab3490e0956f..ad55f4b68e60 100644
--- a/tests/unit_tests/utils/webdriver_test.py
+++ b/tests/unit_tests/utils/webdriver_test.py
@@ -530,6 +530,7 @@ def test_get_screenshot_handles_playwright_timeout(
                 "SCREENSHOT_PLAYWRIGHT_DEFAULT_TIMEOUT": 30000,
                 "SCREENSHOT_PLAYWRIGHT_WAIT_EVENT": "networkidle",
                 "SCREENSHOT_SELENIUM_HEADSTART": 5,
+                "SCREENSHOT_SELENIUM_ANIMATION_WAIT": 1,
                 "SCREENSHOT_LOCATE_WAIT": 10,
                 "SCREENSHOT_LOAD_WAIT": 10,
                 "SCREENSHOT_WAIT_FOR_ERROR_MODAL_VISIBLE": 10,
@@ -546,8 +547,10 @@ def test_get_screenshot_handles_playwright_timeout(
                     "http://example.com", "test-element", mock_user
                 )

-        # Should handle timeout gracefully and return None
-        assert result is None
+        # page.goto() timeout is caught and logged without aborting; execution
+        # continues to the element waits, which succeed here, so a screenshot
+        # is taken and returned (not None).
+        assert result is not None
         mock_logger.exception.assert_called()
         exception_call = mock_logger.exception.call_args[0][0]
         assert "Web event %s not detected" in exception_call
@@ -640,10 +643,10 @@ def test_find_unexpected_errors_processes_alerts(
     @patch("superset.utils.webdriver.PLAYWRIGHT_AVAILABLE", True)
     @patch("superset.utils.webdriver.sync_playwright")
     @patch("superset.utils.webdriver.logger")
-    def test_get_screenshot_logs_multiple_timeouts(
+    def test_get_screenshot_raises_on_element_wait_timeout(
         self, mock_logger, mock_sync_playwright
     ):
-        """Test that multiple timeout scenarios are logged appropriately."""
+        """Test that PlaywrightTimeout propagates when waiting for page elements."""
         from superset.utils.webdriver import PlaywrightTimeout

         mock_user = MagicMock()
@@ -663,9 +666,10 @@ def test_get_screenshot_logs_multiple_timeouts(
         mock_browser.new_context.return_value = mock_context
         mock_context.new_page.return_value = mock_page

-        # Mock locator to raise timeout on element wait
+        # Keep a reference to the exact instance so we can verify identity below.
+        timeout = PlaywrightTimeout()
         mock_page.locator.return_value = mock_element
-        mock_element.wait_for.side_effect = PlaywrightTimeout()
+        mock_element.wait_for.side_effect = timeout

         with patch("superset.utils.webdriver.app") as mock_app:
             mock_app.config = {
@@ -686,10 +690,15 @@ def test_get_screenshot_logs_multiple_timeouts(
                 mock_auth.return_value = mock_context

                 driver = WebDriverPlaywright("chrome")
-                result = driver.get_screenshot(
-                    "http://example.com", "test-element", mock_user
-                )
-
-        assert result is None
-        # Should log timeout for element wait
-        assert mock_logger.exception.call_count >= 1
+                with pytest.raises(PlaywrightTimeout) as exc_info:
+                    driver.get_screenshot(
+                        "http://example.com", "test-element", mock_user
+                    )
+
+        # The exact injected instance must propagate — guards against the
+        # fallback alias (PlaywrightTimeout = Exception when playwright is
+        # not installed) accepting unrelated exceptions.
+        assert exc_info.value is timeout
+        mock_logger.exception.assert_any_call(
+            "Timed out requesting url %s", "http://example.com"
+        )
PATCH

echo "Gold patch applied successfully."
