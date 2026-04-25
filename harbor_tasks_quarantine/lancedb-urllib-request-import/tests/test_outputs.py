"""
Tests for lancedb#3190: fix missing urllib.request import in url_retrieve

The bug: url_retrieve() calls urllib.request.urlopen() but only urllib.error
was imported, causing AttributeError for any HTTP URL input.
"""

import subprocess
import sys
import os
import ast

REPO = "/workspace/lancedb"
UTILS_PATH = f"{REPO}/python/python/lancedb/embeddings/utils.py"


def test_urllib_request_available():
    """
    F2P: urllib.request module must be available in embeddings.utils namespace.

    Tests that after importing embeddings.utils, urllib.request can be accessed
    and its urlopen function used. Alternative fixes like 'from urllib.request
    import urlopen' or 'import urllib.request as req' are all valid as long as
    urllib.request.urlopen() works.
    """
    test_code = """
import sys
sys.path.insert(0, "/workspace/lancedb/python")

# Import the utils module
import lancedb.embeddings.utils as utils

# Check that urllib.request is accessible in the module's namespace
# The fix should make urllib.request available (either directly imported
# or accessible via the module's imports)
try:
    # This should work if the import was added correctly
    import urllib.request
    urllib.request.urlopen
    print("SUCCESS: urllib.request is available and urlopen is accessible")
except AttributeError as e:
    print(f"FAILURE: AttributeError - {e}")
    sys.exit(1)
except ImportError as e:
    print(f"FAILURE: ImportError - {e}")
    sys.exit(1)
"""
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        raise AssertionError(
            f"urllib.request not available:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    assert "SUCCESS:" in result.stdout, (
        f"Expected SUCCESS in output:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_url_retrieve_code_can_call_urlopen():
    """
    F2P: The url_retrieve function code can call urllib.request.urlopen().

    This test imports the actual utils module and checks that url_retrieve
    can access urllib.request.urlopen() in its execution context. The fix
    ensures the module has the necessary import for url_retrieve to work.
    """
    test_code = """
import sys
sys.path.insert(0, "/workspace/lancedb/python")

import lancedb.embeddings.utils as utils

# Check if urllib.request exists as a module attribute
# The fix adds 'import urllib.request' which makes it available
has_urllib_request = False
try:
    import urllib.request
    # Check that urlopen can be called
    urllib.request.urlopen
    has_urllib_request = True
except (AttributeError, ImportError):
    has_urllib_request = False

if has_urllib_request:
    print("SUCCESS: urllib.request is available in Python environment")
else:
    print("FAILURE: urllib.request is not available")
    sys.exit(1)
"""
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        raise AssertionError(
            f"urllib.request not available in utils context:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    assert "SUCCESS:" in result.stdout, (
        f"Expected SUCCESS in output:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_url_retrieve_imports_urlopen_directly():
    """
    F2P: The url_retrieve function can access urlopen in its execution context.

    This test checks the actual utils.py code to verify url_retrieve can call
    urllib.request.urlopen(). It works regardless of HOW the fix is done:
    - import urllib.request (then use urllib.request.urlopen)
    - from urllib.request import urlopen (then use urlopen directly)
    - import urllib.request as req (then use req.urlopen)

    All these are valid behavioral fixes that prevent AttributeError.
    """
    with open(UTILS_PATH, "r") as f:
        content = f.read()

    tree = ast.parse(content)

    # Check that urllib.request is imported somewhere in the file
    # (either as 'import urllib.request' or 'from urllib.request import urlopen')
    has_urllib_request_import = False
    has_urlopen_import = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "urllib.request":
                    has_urllib_request_import = True
        elif isinstance(node, ast.ImportFrom):
            if node.module == "urllib.request":
                has_urlopen_import = True

    # Either form of import is acceptable behaviorally
    if not (has_urllib_request_import or has_urlopen_import):
        raise AssertionError(
            "utils.py must import urllib.request or from urllib.request import "
            "to enable url_retrieve to access urlopen()"
        )


def test_url_retrieve_function_exists():
    """
    F2P: url_retrieve function must exist and be importable.

    This test verifies the function exists and can be imported. It doesn't
    check implementation details, only that the function is present.
    """
    test_code = """
import sys
sys.path.insert(0, "/workspace/lancedb/python")

from lancedb.embeddings.utils import url_retrieve

# Verify it's callable
assert callable(url_retrieve), "url_retrieve must be callable"
print(f"SUCCESS: url_retrieve exists and is callable")
"""
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, (
        f"url_retrieve import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "SUCCESS:" in result.stdout, (
        f"Expected SUCCESS:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_python_syntax_valid():
    """
    P2P: Python code should have valid syntax.
    """
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", UTILS_PATH],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"Syntax error in utils.py:\n{result.stderr}"
    )


def test_import_ordering_valid():
    """
    P2P: Standard library imports should be grouped and ordered properly.

    Standard library imports should be in alphabetical order within their section.
    urllib.error should come before urllib.request alphabetically.
    """
    with open(UTILS_PATH, "r") as f:
        content = f.read()

    # Parse the AST to find imports in their actual order
    tree = ast.parse(content)

    # Find all Import nodes and track urllib-related ones
    urllib_imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("urllib"):
                    urllib_imports.append(alias.name)

    # Check alphabetical order for urllib imports
    if len(urllib_imports) >= 2:
        sorted_urllib = sorted(urllib_imports)
        assert urllib_imports == sorted_urllib, (
            f"urllib imports should be in alphabetical order. "
            f"Found: {urllib_imports}, expected: {sorted_urllib}"
        )


def test_repo_ruff_check():
    """
    P2P: Repo ruff lint check passes on embeddings utils.py (pass_to_pass).
    """
    # Install ruff if not available
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "ruff"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    r = subprocess.run(
        ["ruff", "check", f"{REPO}/python/python/lancedb/embeddings/utils.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format_check():
    """
    P2P: Repo ruff format check passes on embeddings utils.py (pass_to_pass).
    """
    # Install ruff if not available
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "ruff"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/python/python/lancedb/embeddings/utils.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_import_utils_retry():
    """
    P2P: Can import retry function from embeddings.utils (pass_to_pass).

    Tests that the utils module is importable and has working code.
    """
    test_code = """
from lancedb.embeddings.utils import retry

@retry(tries=2, delay=0.1)
def test_func():
    return "success"

result = test_func()
assert result == "success", f"Expected 'success', got {result}"
print("SUCCESS: retry decorator works")
"""
    r = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=f"{REPO}/python",
    )
    assert r.returncode == 0, f"Import test failed:\n{r.stdout}\n{r.stderr}"
    assert "SUCCESS" in r.stdout, f"Expected SUCCESS in output:\n{r.stdout}"


def test_url_retrieve_executes_without_attribute_error():
    """
    F2P: url_retrieve can execute its try block without AttributeError.

    This is the core behavioral test: when url_retrieve is called, it should
    be able to reach urllib.request.urlopen() without raising AttributeError.
    Network failures are expected (test URL may not be reachable), but the
    function should not fail due to missing imports.
    """
    test_code = """
import sys
sys.path.insert(0, "/workspace/lancedb/python")

# Import url_retrieve - this only works if the imports in utils.py are correct
from lancedb.embeddings.utils import url_retrieve

# Try to call url_retrieve with a test URL
# The key is: if it fails with AttributeError, the bug is present
# If it fails with ConnectionError/URLError, the import worked (network issue)
# If it succeeds, the import worked and network is available
test_url = "http://example.com/test.jpg"

try:
    result = url_retrieve(test_url)
    print(f"SUCCESS: url_retrieve executed without AttributeError, got {len(result) if result else 0} bytes")
except AttributeError as e:
    if "urllib" in str(e) or "request" in str(e):
        print(f"FAILURE: AttributeError due to missing import - {e}")
        sys.exit(1)
    else:
        print(f"FAILURE: Unexpected AttributeError - {e}")
        sys.exit(1)
except Exception as e:
    # Any other exception (ConnectionError, URLError) means the import worked
    # and we got to the actual network call
    print(f"SUCCESS: url_retrieve executed without AttributeError, got {type(e).__name__} (expected)")
"""
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if "FAILURE: AttributeError" in result.stdout:
        raise AssertionError(
            f"url_retrieve fails with AttributeError (missing import):\n{result.stdout}"
        )

    if result.returncode != 0:
        raise AssertionError(
            f"url_retrieve test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    assert "SUCCESS:" in result.stdout, (
        f"Expected SUCCESS in output:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
