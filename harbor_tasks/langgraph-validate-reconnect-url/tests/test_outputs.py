#!/usr/bin/env python3
"""
Test suite for langgraph-sdk reconnect URL validation fix.

This tests that the SDK properly validates reconnect Location headers
to prevent credential leakage to external servers.
"""

import re
import subprocess
import sys

REPO = "/workspace/langgraph/libs/sdk-py"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def test_cross_origin_reconnect_blocked():
    """Cross-origin reconnect Location headers should raise ValueError (f2p)."""
    test_cases = [
        ("https://api.example.com", "https://attacker.com/redirect"),
        ("https://api.example.com/v1", "https://evil.com/path"),
        ("https://api.example.com", "http://api.example.com/path"),
        ("http://api.example.com", "https://api.example.com/path"),
        ("https://api.example.com", "https://api.example.com:8443/path"),
        ("http://api.example.com", "http://api.example.com:8080/path"),
        ("https://api.example.com:8080", "https://other.example.com:9090/path"),
    ]

    cases_str = ",\n    ".join(
        f'("{base_url}", "{location}")' for base_url, location in test_cases
    )

    template = '''
import asyncio
import httpx
from langgraph_sdk._async.http import HttpClient
from langgraph_sdk._sync.http import SyncHttpClient

test_cases = [
    CASES_STR
]

def mock_handler_req(request):
    loc = request.headers.get("_test_location")
    return httpx.Response(200, headers={"location": loc}, content=b\'{"ok":true}\')

def mock_handler_stream(request):
    loc = request.headers.get("_test_location")
    return httpx.Response(200, headers={
        "location": loc,
        "content-type": "text/event-stream",
    }, content=b"data: {}\\n\\n")

async def test_async_req(base_url, location):
    transport = httpx.MockTransport(mock_handler_req)
    client = httpx.AsyncClient(transport=transport, base_url=base_url)
    client.headers["_test_location"] = location
    http = HttpClient(client)
    try:
        await http.request_reconnect("/path", "GET")
        return False, "no error"
    except ValueError as e:
        msg = str(e).lower()
        return ("cross-origin" in msg or "refusing" in msg), str(e)

async def test_async_stream(base_url, location):
    transport = httpx.MockTransport(mock_handler_stream)
    client = httpx.AsyncClient(transport=transport, base_url=base_url)
    client.headers["_test_location"] = location
    http = HttpClient(client)
    try:
        async for _ in http.stream("/path", "GET"):
            pass
        return False, "no error"
    except ValueError as e:
        msg = str(e).lower()
        return ("cross-origin" in msg or "refusing" in msg), str(e)

def test_sync_req(base_url, location):
    transport = httpx.MockTransport(mock_handler_req)
    client = httpx.Client(transport=transport, base_url=base_url)
    client.headers["_test_location"] = location
    http = SyncHttpClient(client)
    try:
        http.request_reconnect("/path", "GET")
        return False, "no error"
    except ValueError as e:
        msg = str(e).lower()
        return ("cross-origin" in msg or "refusing" in msg), str(e)

def test_sync_stream(base_url, location):
    transport = httpx.MockTransport(mock_handler_stream)
    client = httpx.Client(transport=transport, base_url=base_url)
    client.headers["_test_location"] = location
    http = SyncHttpClient(client)
    try:
        for _ in http.stream("/path", "GET"):
            pass
        return False, "no error"
    except ValueError as e:
        msg = str(e).lower()
        return ("cross-origin" in msg or "refusing" in msg), str(e)

async def main():
    all_ok = True
    for base_url, location in test_cases:
        results = [
            ("async_req", await test_async_req(base_url, location)),
            ("async_stream", await test_async_stream(base_url, location)),
            ("sync_req", test_sync_req(base_url, location)),
            ("sync_stream", test_sync_stream(base_url, location)),
        ]
        for name, (passed, detail) in results:
            if passed:
                print(f"PASS {base_url} {location} {name}")
            else:
                print(f"FAIL {base_url} {location} {name}: {detail}")
                all_ok = False
    print("ALL_OK" if all_ok else "SOME_FAILED")

asyncio.run(main())
'''
    code = template.replace("CASES_STR", cases_str)
    r = _run_py(code, timeout=60)
    assert r.returncode == 0, f"Subprocess failed: {r.stderr}"
    assert "ALL_OK" in r.stdout, f"Expected all cross-origin cases to be blocked:\n{r.stdout}\n{r.stderr}"


def test_same_origin_reconnect_allowed():
    """Same-origin reconnect Location headers should be allowed (f2p)."""
    test_cases = [
        ("https://api.example.com", "https://api.example.com/redirect"),
        ("https://api.example.com/v1", "https://api.example.com/v1/runs"),
        ("https://api.example.com", "https://api.example.com:443/redirect"),
        ("https://api.example.com:443", "https://api.example.com/redirect"),
        ("http://api.example.com", "http://api.example.com:80/redirect"),
        ("http://api.example.com:80", "http://api.example.com/redirect"),
    ]

    for base_url, location in test_cases:
        template = '''
import httpx
from langgraph_sdk._sync.http import SyncHttpClient

def mock_handler(request):
    return httpx.Response(200, headers={"location": "LOCATION"}, content=b\'{"ok":true}\')

client = httpx.Client(transport=httpx.MockTransport(mock_handler), base_url="BASE_URL")
http = SyncHttpClient(client)
result = http.request_reconnect("/path", "GET")
print("ALLOWED")
'''
        code = template.replace("LOCATION", location).replace("BASE_URL", base_url)
        r = _run_py(code)
        assert r.returncode == 0, f"Test failed for {location}: {r.stderr}"
        assert "ALLOWED" in r.stdout, f"Expected ALLOWED for {location}, got: {r.stdout}"


def test_relative_url_allowed():
    """Relative URLs should be allowed as they resolve against the base (f2p)."""
    test_cases = [
        ("https://api.example.com", "/redirect"),
        ("https://api.example.com/v1", "/v1/reconnect"),
        ("https://api.example.com", "/v1/threads/thread123/runs"),
    ]

    for base_url, location in test_cases:
        template = '''
import httpx
from langgraph_sdk._sync.http import SyncHttpClient

def mock_handler(request):
    return httpx.Response(200, headers={"location": "LOCATION"}, content=b\'{"ok":true}\')

client = httpx.Client(transport=httpx.MockTransport(mock_handler), base_url="BASE_URL")
http = SyncHttpClient(client)
result = http.request_reconnect("/path", "GET")
print("ALLOWED")
'''
        code = template.replace("LOCATION", location).replace("BASE_URL", base_url)
        r = _run_py(code)
        assert r.returncode == 0, f"Test failed for {location}: {r.stderr}"
        assert "ALLOWED" in r.stdout, f"Expected ALLOWED for {location}, got: {r.stdout}"


def test_default_port_handling():
    """Default ports (https=443, http=80) are handled correctly (f2p)."""
    allowed_cases = [
        ("https://api.example.com", "https://api.example.com:443/path"),
        ("https://api.example.com:443", "https://api.example.com/path"),
        ("http://api.example.com", "http://api.example.com:80/path"),
        ("http://api.example.com:80", "http://api.example.com/path"),
    ]

    for base_url, location in allowed_cases:
        template = '''
import httpx
from langgraph_sdk._sync.http import SyncHttpClient

def mock_handler(request):
    return httpx.Response(200, headers={"location": "LOCATION"}, content=b\'{"ok":true}\')

client = httpx.Client(transport=httpx.MockTransport(mock_handler), base_url="BASE_URL")
http = SyncHttpClient(client)
result = http.request_reconnect("/path", "GET")
print("ALLOWED")
'''
        code = template.replace("LOCATION", location).replace("BASE_URL", base_url)
        r = _run_py(code)
        assert r.returncode == 0, f"Test failed for {location}: {r.stderr}"
        assert "ALLOWED" in r.stdout, f"Expected ALLOWED for {location}, got: {r.stdout}"

    blocked_cases = [
        ("https://api.example.com", "https://api.example.com:8443/path"),
        ("http://api.example.com", "http://api.example.com:8080/path"),
    ]

    for base_url, location in blocked_cases:
        template = '''
import httpx
from langgraph_sdk._sync.http import SyncHttpClient

def mock_handler(request):
    return httpx.Response(200, headers={"location": "LOCATION"}, content=b\'{"ok":true}\')

client = httpx.Client(transport=httpx.MockTransport(mock_handler), base_url="BASE_URL")
http = SyncHttpClient(client)
try:
    http.request_reconnect("/path", "GET")
    print("NO_ERROR")
except ValueError as e:
    msg = str(e).lower()
    if "cross-origin" in msg or "refusing" in msg:
        print("BLOCKED")
    else:
        print(f"WRONG_MSG: {e}")
'''
        code = template.replace("LOCATION", location).replace("BASE_URL", base_url)
        r = _run_py(code)
        assert r.returncode == 0, f"Test failed for {location}: {r.stderr}"
        assert "BLOCKED" in r.stdout, f"Expected BLOCKED for {location}, got: {r.stdout}"


def test_version_updated():
    """Version should be updated to 0.3.13 (f2p)."""
    from langgraph_sdk import __version__
    assert __version__ == "0.3.13", f"Expected version 0.3.13, got {__version__}"


def test_repo_format():
    """Repo code passes format check (p2p)."""
    r = subprocess.run(
        ["make", "format"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_lint():
    """Repo code passes lint check (p2p)."""
    r = subprocess.run(
        ["make", "lint"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Lint check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_tests():
    """Repo tests pass (p2p)."""
    r = subprocess.run(
        ["make", "test"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_type():
    """Repo type checking passes (p2p)."""
    r = subprocess.run(
        ["make", "type"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Type check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_stream_tests():
    """Repo client stream tests pass (p2p)."""
    r = subprocess.run(
        ["uv", "run", "pytest", "tests/test_client_stream.py", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Stream tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_error_tests():
    """Repo error handling tests pass (p2p)."""
    r = subprocess.run(
        ["uv", "run", "pytest", "tests/test_errors.py", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Error tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_client_export_tests():
    """Repo client export tests pass (p2p)."""
    r = subprocess.run(
        ["uv", "run", "pytest", "tests/test_client_exports.py", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Client export tests failed:\n{r.stdout}\n{r.stderr}"


def test_no_double_backticks():
    """Do NOT use Sphinx-style double backtick formatting (agent config check)."""
    import pathlib

    files_to_check = list(pathlib.Path(REPO).rglob("*.py"))
    double_backtick_pattern = re.compile(r"`{4}[^`]+`{4}")

    for filepath in files_to_check:
        try:
            content = filepath.read_text()
            matches = double_backtick_pattern.findall(content)
            assert len(matches) == 0, f"Found double backticks in {filepath}"
        except (FileNotFoundError, UnicodeDecodeError):
            pass


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
