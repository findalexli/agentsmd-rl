#!/bin/bash
# Gold solution for selenium-py-type-stubs task
# Applies the fix from PR #17165: Add type stubs for lazy imported classes and modules

set -e
cd /workspace/selenium

# Idempotency check - skip if already applied
if grep -q "from selenium.webdriver.common.desired_capabilities import DesiredCapabilities" py/selenium/webdriver/chrome/remote_connection.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Fix Chrome remote_connection.py - change import to direct path and reorder
sed -i 's/from selenium.webdriver import DesiredCapabilities/from selenium.webdriver.common.desired_capabilities import DesiredCapabilities/' py/selenium/webdriver/chrome/remote_connection.py
# Reorder imports: move DesiredCapabilities after ChromiumRemoteConnection
sed -i '/from selenium.webdriver.common.desired_capabilities import DesiredCapabilities/d' py/selenium/webdriver/chrome/remote_connection.py
sed -i '/from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection/a from selenium.webdriver.common.desired_capabilities import DesiredCapabilities' py/selenium/webdriver/chrome/remote_connection.py

# Fix Edge remote_connection.py - same changes
sed -i 's/from selenium.webdriver import DesiredCapabilities/from selenium.webdriver.common.desired_capabilities import DesiredCapabilities/' py/selenium/webdriver/edge/remote_connection.py
sed -i '/from selenium.webdriver.common.desired_capabilities import DesiredCapabilities/d' py/selenium/webdriver/edge/remote_connection.py
sed -i '/from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection/a from selenium.webdriver.common.desired_capabilities import DesiredCapabilities' py/selenium/webdriver/edge/remote_connection.py

# Add *.pyi to pyproject.toml package-data
sed -i '/"\*\.py",/a\    "*.pyi",' py/pyproject.toml

# Create stub files
cat > py/selenium/webdriver/__init__.pyi << 'EOF'
# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Type stub with lazy import mapping from __init__.py.

This stub file is necessary for type checkers and IDEs to automatically have
visibility into lazy modules since they are not imported immediately at runtime.
"""

# ruff: noqa: I001

# Expose runtime version
__version__: str

# Chrome
from selenium.webdriver.chrome.webdriver import WebDriver as Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

# Edge
from selenium.webdriver.edge.webdriver import WebDriver as Edge
from selenium.webdriver.edge.webdriver import WebDriver as ChromiumEdge
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService

# Firefox
from selenium.webdriver.firefox.webdriver import WebDriver as Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

# IE
from selenium.webdriver.ie.webdriver import WebDriver as Ie
from selenium.webdriver.ie.options import Options as IeOptions
from selenium.webdriver.ie.service import Service as IeService

# Safari
from selenium.webdriver.safari.webdriver import WebDriver as Safari
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService

# Remote
from selenium.webdriver.remote.webdriver import WebDriver as Remote

# WebKitGTK
from selenium.webdriver.webkitgtk.webdriver import WebDriver as WebKitGTK
from selenium.webdriver.webkitgtk.options import Options as WebKitGTKOptions
from selenium.webdriver.webkitgtk.service import Service as WebKitGTKService

# WPEWebKit
from selenium.webdriver.wpewebkit.webdriver import WebDriver as WPEWebKit
from selenium.webdriver.wpewebkit.options import Options as WPEWebKitOptions
from selenium.webdriver.wpewebkit.service import Service as WPEWebKitService

# Common utilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy

# Submodules
from . import chrome
from . import chromium
from . import common
from . import edge
from . import firefox
from . import ie
from . import remote
from . import safari
from . import support
from . import webkitgtk
from . import wpewebkit

# Exposed names
__all__ = [
    # Classes
    "ActionChains",
    "Chrome",
    "ChromeOptions",
    "ChromeService",
    "ChromiumEdge",
    "DesiredCapabilities",
    "Edge",
    "EdgeOptions",
    "EdgeService",
    "Firefox",
    "FirefoxOptions",
    "FirefoxProfile",
    "FirefoxService",
    "Ie",
    "IeOptions",
    "IeService",
    "Keys",
    "Proxy",
    "Remote",
    "Safari",
    "SafariOptions",
    "SafariService",
    "WPEWebKit",
    "WPEWebKitOptions",
    "WPEWebKitService",
    "WebKitGTK",
    "WebKitGTKOptions",
    "WebKitGTKService",
    # Submodules
    "chrome",
    "chromium",
    "common",
    "edge",
    "firefox",
    "ie",
    "remote",
    "safari",
    "support",
    "webkitgtk",
    "wpewebkit",
]
EOF

cat > py/selenium/webdriver/chrome/__init__.pyi << 'EOF'
# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Type stub with lazy import mapping from __init__.py.

This stub file is necessary for type checkers and IDEs to automatically have
visibility into lazy modules since they are not imported immediately at runtime.
"""

from . import options, remote_connection, service, webdriver

__all__ = ["options", "remote_connection", "service", "webdriver"]
EOF

cat > py/selenium/webdriver/edge/__init__.pyi << 'EOF'
# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Type stub with lazy import mapping from __init__.py.

This stub file is necessary for type checkers and IDEs to automatically have
visibility into lazy modules since they are not imported immediately at runtime.
"""

from . import options, remote_connection, service, webdriver

__all__ = ["options", "remote_connection", "service", "webdriver"]
EOF

cat > py/selenium/webdriver/firefox/__init__.pyi << 'EOF'
# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Type stub with lazy import mapping from __init__.py.

This stub file is necessary for type checkers and IDEs to automatically have
visibility into lazy modules since they are not imported immediately at runtime.
"""

from . import firefox_profile, options, remote_connection, service, webdriver

__all__ = ["firefox_profile", "options", "remote_connection", "service", "webdriver"]
EOF

cat > py/selenium/webdriver/ie/__init__.pyi << 'EOF'
# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Type stub with lazy import mapping from __init__.py.

This stub file is necessary for type checkers and IDEs to automatically have
visibility into lazy modules since they are not imported immediately at runtime.
"""

from . import options, service, webdriver

__all__ = ["options", "service", "webdriver"]
EOF

cat > py/selenium/webdriver/safari/__init__.pyi << 'EOF'
# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Type stub with lazy import mapping from __init__.py.

This stub file is necessary for type checkers and IDEs to automatically have
visibility into lazy modules since they are not imported immediately at runtime.
"""

from . import options, permissions, remote_connection, service, webdriver

__all__ = ["options", "permissions", "remote_connection", "service", "webdriver"]
EOF

cat > py/selenium/webdriver/webkitgtk/__init__.pyi << 'EOF'
# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Type stub with lazy import mapping from __init__.py.

This stub file is necessary for type checkers and IDEs to automatically have
visibility into lazy modules since they are not imported immediately at runtime.
"""

from . import options, service, webdriver

__all__ = ["options", "service", "webdriver"]
EOF

cat > py/selenium/webdriver/wpewebkit/__init__.pyi << 'EOF'
# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Type stub with lazy import mapping from __init__.py.

This stub file is necessary for type checkers and IDEs to automatically have
visibility into lazy modules since they are not imported immediately at runtime.
"""

from . import options, service, webdriver

__all__ = ["options", "service", "webdriver"]
EOF

echo "Patch applied successfully."
