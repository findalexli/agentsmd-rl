#!/usr/bin/env bash
set -euo pipefail

cd /workspace/selenium

# Idempotent: skip if already applied
if grep -q 'BROWSER_TESTS' py/BUILD.bazel 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# === 1. Update py/private/browsers.bzl: --headless=true -> --headless ===
sed -i 's/"--headless=true"/"--headless"/' py/private/browsers.bzl

# === 2. Update py/BUILD.bazel: consolidate browser test targets ===
python3 <<'PYEOF'
import re

path = "py/BUILD.bazel"
with open(path) as f:
    content = f.read()

# Remove marionette refs from test support srcs
content = content.replace(
    '        "test/selenium/webdriver/marionette/__init__.py",\n'
    '        "test/selenium/webdriver/marionette/conftest.py",\n',
    ''
)

# Find the BIDI_TESTS line and insert BROWSER_TESTS dict after it
browser_tests_dict = '''
# Browser-specific test configuration
BROWSER_TESTS = {
    "chrome": {
        "browser_srcs": ["test/selenium/webdriver/chrome/**/*.py"],
        "bidi": True,
    },
    "edge": {
        "browser_srcs": ["test/selenium/webdriver/edge/**/*.py"],
    },
    "firefox": {
        "browser_srcs": [
            "test/selenium/webdriver/firefox/**/*.py",
        ],
        "extra_excludes": ["test/selenium/webdriver/common/devtools_tests.py"],
        "bidi": True,
    },
    "ie": {
        "browser_srcs": ["test/selenium/webdriver/ie/**/*.py"],
    },
    "safari": {
        "browser_srcs": ["test/selenium/webdriver/safari/**/*.py"],
    },
}
'''

bidi_line = 'BIDI_TESTS = glob(["test/selenium/webdriver/common/**/*bidi*_tests.py"])'
content = content.replace(bidi_line, bidi_line + '\n' + browser_tests_dict)

# Replace the common-%s list comprehension with test-%s that includes browser_srcs
old_common = '''[
    py_test_suite(
        name = "common-%s" % browser,
        size = "large",
        srcs = glob(
            [
                "test/selenium/webdriver/common/**/*.py",
                "test/selenium/webdriver/support/**/*.py",
            ],
            exclude = BIDI_TESTS + ["test/selenium/webdriver/common/print_pdf_tests.py"] +
                      (["test/selenium/webdriver/common/devtools_tests.py"] if browser == "chrome-beta" else []),
        ),
        args = [
            "--instafail",
        ] + BROWSERS[browser]["args"],
        data = BROWSERS[browser]["data"],
        env_inherit = ["DISPLAY"],
        tags = ["no-sandbox"] + BROWSERS[browser]["tags"],
        deps = [
            ":init-tree",
            ":selenium",
            ":webserver",
        ] + TEST_DEPS,
    )
    for browser in BROWSERS.keys()
]'''

new_common = '''# Generate test-<browser> targets (non-bidi)
[
    py_test_suite(
        name = "test-%s" % browser,
        size = "large",
        srcs = glob(
            [
                "test/selenium/webdriver/common/**/*.py",
                "test/selenium/webdriver/support/**/*.py",
            ] + BROWSER_TESTS[browser]["browser_srcs"],
            exclude = BIDI_TESTS + ["test/selenium/webdriver/common/print_pdf_tests.py"] +
                      BROWSER_TESTS[browser].get("extra_excludes", []),
        ),
        args = [
            "--instafail",
        ] + BROWSERS[browser]["args"],
        data = BROWSERS[browser]["data"],
        env_inherit = ["DISPLAY"],
        tags = ["no-sandbox"] + BROWSERS[browser]["tags"],
        deps = [
            ":init-tree",
            ":selenium",
            ":webserver",
        ] + TEST_DEPS,
    )
    for browser in BROWSER_TESTS.keys()
]'''

content = content.replace(old_common, new_common)

# Replace common-%s-bidi with test-%s-bidi and add conditional
old_bidi = '''[
    py_test_suite(
        name = "common-%s-bidi" % browser,
        size = "large",
        srcs = glob(
            [
                "test/selenium/webdriver/common/**/*.py",
                "test/selenium/webdriver/support/**/*.py",
            ],
            exclude = ["test/selenium/webdriver/common/print_pdf_tests.py"] +
                      (["test/selenium/webdriver/common/devtools_tests.py"] if browser == "chrome-beta" else []),
        ),
        args = [
            "--instafail",
            "--bidi",
        ] + BROWSERS[browser]["args"],
        data = BROWSERS[browser]["data"],
        env_inherit = ["DISPLAY"],
        tags = ["no-sandbox"] + BROWSERS[browser]["tags"],
        deps = [
            ":init-tree",
            ":selenium",
            ":webserver",
        ] + TEST_DEPS,
    )
    for browser in BROWSERS.keys()
]'''

new_bidi = '''# Generate test-<browser>-bidi targets (only for browsers with bidi=True)
[
    py_test_suite(
        name = "test-%s-bidi" % browser,
        size = "large",
        srcs = glob(
            [
                "test/selenium/webdriver/common/**/*.py",
                "test/selenium/webdriver/support/**/*.py",
            ] + BROWSER_TESTS[browser]["browser_srcs"],
            exclude = ["test/selenium/webdriver/common/print_pdf_tests.py"] +
                      BROWSER_TESTS[browser].get("extra_excludes", []),
        ),
        args = [
            "--instafail",
            "--bidi",
        ] + BROWSERS[browser]["args"],
        data = BROWSERS[browser]["data"],
        env_inherit = ["DISPLAY"],
        tags = ["no-sandbox"] + BROWSERS[browser]["tags"],
        deps = [
            ":init-tree",
            ":selenium",
            ":webserver",
        ] + TEST_DEPS,
    )
    for browser in BROWSER_TESTS.keys()
    if BROWSER_TESTS[browser].get("bidi", False)
]'''

content = content.replace(old_bidi, new_bidi)

# Remove standalone browser test suites (test-chrome, test-chrome-headless,
# test-chrome-beta, test-edge, test-firefox, test-ie, test-safari)
# These are now generated from BROWSER_TESTS dict
standalone_names = [
    "test-chrome",
    "test-chrome-headless",
    "test-chrome-beta",
    "test-edge",
    "test-firefox",
    "test-ie",
    "test-safari",
]

for name in standalone_names:
    # Match py_test_suite block: from 'py_test_suite(' to closing ')' + newline
    pattern = re.compile(
        r'\npy_test_suite\(\s*\n\s*name\s*=\s*"' + re.escape(name) + r'".*?\n\)\n',
        re.DOTALL
    )
    content = pattern.sub('\n', content)

with open(path, 'w') as f:
    f.write(content)
PYEOF

# === 3. Update README.md: update Python test commands ===
python3 <<'PYEOF'
path = "README.md"
with open(path) as f:
    content = f.read()

# Update test target references
content = content.replace(
    'To run common tests with a specific browser:\n\n```shell\nbazel test //py:common-<browsername>\n```',
    'To run all tests with a specific browser:\n\n```shell\nbazel test //py:test-<browsername>\n```'
)

content = content.replace(
    'bazel test //py:common-<browsername>-bidi',
    'bazel test //py:test-<browsername>-bidi'
)

# Replace the old "To run tests with a specific browser" + "To run all Python tests" sections
# with consolidated version + headless instructions
content = content.replace(
    'To run tests with a specific browser:\n\n```shell\nbazel test //py:test-<browsername>\n```\n\nTo run all Python tests:\n\n```shell\nbazel test //py:all\n```',
    'To run all Python tests:\n\n```shell\nbazel test //py:all\n```\n\nTo run tests headless:\n```shell\nbazel test //py:test-<browsername> --//common:headless=true\n```\n'
)

with open(path, 'w') as f:
    f.write(content)
PYEOF

echo "Patch applied successfully."
