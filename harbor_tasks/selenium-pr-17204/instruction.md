# Bug: Service.stop() Closes Externally-Provided Log Streams

## Problem

When using Selenium's WebDriver services (ChromeService, FirefoxService, etc.), passing an external stream like `sys.stdout` as the `log_output` parameter causes issues when stopping the service.

After calling `Service.stop()`, the provided stream gets closed, making it unusable for subsequent operations. This is particularly problematic when:

1. Running multiple browser sessions sequentially with the same log stream
2. Using standard streams (`sys.stdout`, `sys.stderr`) for logging
3. Sharing a log file handle across multiple services

## Reproduction

```python
import sys
from selenium.webdriver.chrome.service import Service

# First service using stdout for logging
service1 = Service(log_output=sys.stdout)
# ... use service1 ...
service1.stop()  # This closes sys.stdout!

# Second service fails or causes errors
service2 = Service(log_output=sys.stdout)  # sys.stdout is now closed
```

## Expected Behavior

External streams passed to `log_output` should remain open after `Service.stop()` is called. The service should only close streams it created internally (e.g., when given a file path string).

## Required Fix

The fix must track whether the Service owns its log output stream. This requires:

1. An attribute that indicates log output ownership (e.g., `_owns_log_output`)
2. This attribute must be `False` when an external stream is passed to `log_output`
3. This attribute must be `True` when a file path string is passed to `log_output`
4. The `stop()` method must only close the log output stream if the Service owns it

## Location

The issue is in `py/selenium/webdriver/common/service.py`, specifically in the `stop()` method and how log streams are handled during initialization.