#!/usr/bin/env python3
"""
Test that permission checks properly propagate the requesting frame.

The fix ensures that when checking permissions from iframes, the permission
helper uses the iframe's origin (requesting_frame) rather than the main frame's origin.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/electron")


def read_file(path: str) -> str:
    """Read file content from repository."""
    full_path = REPO / path
    with open(full_path, 'r') as f:
        return f.read()


def test_check_permission_signature_updated():
    """
    F2P: CheckPermission must accept requesting_frame as first parameter.

    The base code did not pass the requesting frame, so permission checks
    defaulted to the main frame. The fix adds requesting_frame parameter
    to get the correct origin.
    """
    content = read_file("shell/browser/web_contents_permission_helper.h")

    # Must have requesting_frame as first parameter
    pattern = r'bool\s+CheckPermission\(\s*content::RenderFrameHost\*\s+requesting_frame'
    assert re.search(pattern, content), \
        "CheckPermission signature missing requesting_frame parameter"


def test_check_permission_uses_requesting_frame():
    """
    F2P: CheckPermission must use requesting_frame to get origin.

    The fix changes from using web_contents_->GetLastCommittedURL() to
    requesting_frame->GetLastCommittedOrigin().GetURL().
    """
    content = read_file("shell/browser/web_contents_permission_helper.cc")

    # Must use requesting_frame to get origin
    assert "requesting_frame->GetLastCommittedOrigin().GetURL()" in content, \
        "CheckPermission must use requesting_frame->GetLastCommittedOrigin() for origin"

    # Must NOT use web_contents_->GetLastCommittedURL() (the old pattern)
    old_pattern = "web_contents_->GetLastCommittedURL()"
    assert old_pattern not in content, \
        f"CheckPermission should not use {old_pattern}, must use requesting_frame instead"


def test_check_media_access_signature_updated():
    """
    F2P: CheckMediaAccessPermission must accept requesting_frame parameter.
    """
    content = read_file("shell/browser/web_contents_permission_helper.h")

    # Must have requesting_frame as first parameter, before security_origin
    pattern = r'bool\s+CheckMediaAccessPermission\(\s*content::RenderFrameHost\*\s+requesting_frame'
    assert re.search(pattern, content), \
        "CheckMediaAccessPermission signature missing requesting_frame parameter"


def test_check_media_access_passes_frame():
    """
    F2P: CheckMediaAccessPermission must pass requesting_frame to CheckPermission.
    """
    content = read_file("shell/browser/web_contents_permission_helper.cc")

    # Find CheckMediaAccessPermission function and verify it passes requesting_frame
    func_pattern = r'bool\s+WebContentsPermissionHelper::CheckMediaAccessPermission\([^)]+\)\s*const\s*\{[^}]+CheckPermission\s*\(\s*requesting_frame'
    assert re.search(func_pattern, content, re.DOTALL), \
        "CheckMediaAccessPermission must pass requesting_frame to CheckPermission"


def test_web_contents_passes_render_frame_host():
    """
    F2P: WebContents::CheckMediaAccessPermission must pass render_frame_host.
    """
    content = read_file("shell/browser/api/electron_api_web_contents.cc")

    # Must pass render_frame_host to CheckMediaAccessPermission
    pattern = r'permission_helper->CheckMediaAccessPermission\(\s*render_frame_host'
    assert re.search(pattern, content), \
        "WebContents must pass render_frame_host to CheckMediaAccessPermission"


def test_check_serial_access_signature_updated():
    """
    F2P: CheckSerialAccessPermission must accept requesting_frame parameter instead of origin.
    """
    content = read_file("shell/browser/web_contents_permission_helper.h")

    # Must have requesting_frame parameter
    pattern = r'bool\s+CheckSerialAccessPermission\(\s*content::RenderFrameHost\*\s+requesting_frame\s*\)\s*const'
    assert re.search(pattern, content), \
        "CheckSerialAccessPermission signature must have requesting_frame parameter"

    # Must NOT have the old signature with url::Origin parameter
    old_pattern = r'CheckSerialAccessPermission\(\s*const\s+url::Origin&'
    assert not re.search(old_pattern, content), \
        "CheckSerialAccessPermission should not take url::Origin parameter"


def test_serial_delegate_passes_frame():
    """
    F2P: ElectronSerialDelegate must pass frame to CheckSerialAccessPermission.
    """
    content = read_file("shell/browser/serial/electron_serial_delegate.cc")

    # Must pass frame (not frame->GetLastCommittedOrigin())
    assert "CheckSerialAccessPermission(frame)" in content, \
        "ElectronSerialDelegate must pass frame (not origin) to CheckSerialAccessPermission"

    # Find CanRequestPortPermission function specifically
    func_start = content.find("bool ElectronSerialDelegate::CanRequestPortPermission(")
    assert func_start != -1, "CanRequestPortPermission function not found"

    # Find function body using brace matching
    brace_start = content.find("{", func_start)
    assert brace_start != -1, "Could not find opening brace"

    brace_count = 1
    pos = brace_start + 1
    while brace_count > 0 and pos < len(content):
        if content[pos] == "{":
            brace_count += 1
        elif content[pos] == "}":
            brace_count -= 1
        pos += 1

    func_body = content[func_start:pos]

    # Must pass frame (not frame->GetLastCommittedOrigin()) in CanRequestPortPermission only
    assert "CheckSerialAccessPermission(frame)" in func_body,         "ElectronSerialDelegate must pass frame (not origin) to CheckSerialAccessPermission"

    # Must NOT pass origin extraction in CanRequestPortPermission anymore
    assert "frame->GetLastCommittedOrigin()" not in func_body, \
        "ElectronSerialDelegate should not extract origin from frame"


def test_check_serial_access_uses_requesting_frame():
    """
    F2P: CheckSerialAccessPermission must use requesting_frame for security origin.
    """
    content = read_file("shell/browser/web_contents_permission_helper.cc")

    # In CheckSerialAccessPermission, must use requesting_frame for securityOrigin
    func_start = content.find("bool WebContentsPermissionHelper::CheckSerialAccessPermission(")
    assert func_start != -1, "CheckSerialAccessPermission function not found"

    # Get function body (up to next function or WEB_CONTENTS_USER_DATA_KEY_IMPL)
    next_func = content.find("\nbool WebContentsPermissionHelper::", func_start + 1)
    if next_func == -1:
        next_marker = content.find("WEB_CONTENTS_USER_DATA_KEY_IMPL", func_start)
        func_end = next_marker if next_marker != -1 else len(content)
    else:
        func_end = next_func

    func_body = content[func_start:func_end]

    # Must use requesting_frame to get security origin
    assert "requesting_frame->GetLastCommittedOrigin().GetURL().spec()" in func_body, \
        "CheckSerialAccessPermission must use requesting_frame to get security origin"

    # Must pass requesting_frame to CheckPermission
    assert "CheckPermission(requesting_frame" in func_body, \
        "CheckSerialAccessPermission must pass requesting_frame to CheckPermission"


def test_header_guards_follow_convention():
    """
    P2P: Header guards must follow Electron's naming convention.

    From CLAUDE.md: C++ header guards format:
    #ifndef ELECTRON_SHELL_BROWSER_API_ELECTRON_API_{NAME}_H_
    """
    content = read_file("shell/browser/web_contents_permission_helper.h")

    # Check header guard follows convention
    guard_pattern = r'#ifndef\s+ELECTRON_SHELL_BROWSER_[A-Z_]+_H_'
    assert re.search(guard_pattern, content), \
        "Header guard must follow ELECTRON_SHELL_BROWSER_*_H_ convention"


def test_no_web_contents_primary_main_frame_in_check_permission():
    """
    F2P: CheckPermission must not use GetPrimaryMainFrame.

    The old code used web_contents_->GetPrimaryMainFrame() which always gives
    the main frame. The fix uses the requesting_frame parameter instead.
    """
    content = read_file("shell/browser/web_contents_permission_helper.cc")

    # Must NOT use GetPrimaryMainFrame in CheckPermission
    func_start = content.find("bool WebContentsPermissionHelper::CheckPermission(")
    assert func_start != -1, "CheckPermission function not found"

    # Find function body: starts after opening brace, ends at matching closing brace
    brace_start = content.find("{", func_start)
    assert brace_start != -1, "Could not find opening brace"

    # Count braces to find the end of the function
    brace_count = 1
    pos = brace_start + 1
    while brace_count > 0 and pos < len(content):
        if content[pos] == "{":
            brace_count += 1
        elif content[pos] == "}":
            brace_count -= 1
        pos += 1

    func_body = content[func_start:pos]

    assert "GetPrimaryMainFrame" not in func_body, \
        "CheckPermission must not use GetPrimaryMainFrame, should use requesting_frame parameter"


def test_clang_format():
    """
    P2P: Modified C++ files must follow clang-format rules.

    Repo CI requires all C++ code to pass clang-format checks.
    """
    r = subprocess.run(
        ["python3", "script/run-clang-format.py", "-r", "-c",
         "shell/browser/web_contents_permission_helper.h",
         "shell/browser/web_contents_permission_helper.cc",
         "shell/browser/api/electron_api_web_contents.cc",
         "shell/browser/serial/electron_serial_delegate.cc"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, \
        f"clang-format check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_modified_headers_have_guards():
    """
    P2P: Modified header files must have header guards.

    All C++ headers in the repo must have include guards.
    """
    modified_headers = [
        "shell/browser/web_contents_permission_helper.h",
    ]

    for header in modified_headers:
        content = read_file(header)
        # Check for header guard pattern: #ifndef ELECTRON_..._H_
        guard_pattern = r'#ifndef\s+ELECTRON_[A-Z_]+_H_'
        endif_pattern = r'#endif\s+//\s+ELECTRON_[A-Z_]+_H_'

        assert re.search(guard_pattern, content), \
            f"{header}: Missing or invalid header guard (expected #ifndef ELECTRON_*_H_)"
        assert re.search(endif_pattern, content), \
            f"{header}: Missing or invalid #endif comment (expected // ELECTRON_*_H_)"


def test_cpplint():
    """
    P2P: Modified C++ files must pass cpplint checks.

    Repo CI requires all C++ code to pass cpplint style checks.
    Uses the same filters as Electron's CI (from lint.js).
    """
    # Install cpplint first
    install_r = subprocess.run(
        ["pip", "install", "cpplint", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # cpplint may already be installed, ignore install errors

    # Same filters as used in Electron's lint.js (CPPLINT_FILTERS)
    cpplint_filters = (
        "-build/include,-build/include_order,-build/namespaces,"
        "-readability/casting,-runtime/int,-whitespace/braces,"
        "-build/c++11,-build/header_guard,-readability/todo,"
        "-runtime/references,-whitespace/comma,-whitespace/end_of_line,"
        "-whitespace/forcolon,-whitespace/indent,-whitespace/line_length,"
        "-whitespace/newline,-whitespace/operators,-whitespace/parens,"
        "-whitespace/semicolon,-whitespace/tab"
    )

    modified_files = [
        "shell/browser/web_contents_permission_helper.h",
        "shell/browser/web_contents_permission_helper.cc",
        "shell/browser/api/electron_api_web_contents.cc",
        "shell/browser/serial/electron_serial_delegate.cc",
    ]

    r = subprocess.run(
        ["python3", "/usr/local/lib/python3.12/site-packages/cpplint.py",
         "--filter=" + cpplint_filters] + modified_files,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, \
        f"cpplint check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"
