#!/usr/bin/env python3
"""
Test that permission checks properly propagate the requesting frame.
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
    """F2P: CheckPermission must accept requesting_frame as first parameter."""
    content = read_file("shell/browser/web_contents_permission_helper.h")
    pattern = r'bool\s+CheckPermission\(\s*content::RenderFrameHost\*\s+requesting_frame'
    assert re.search(pattern, content),         "CheckPermission signature missing requesting_frame parameter"


def test_check_permission_uses_requesting_frame():
    """F2P: CheckPermission must use requesting_frame to get origin."""
    content = read_file("shell/browser/web_contents_permission_helper.cc")
    assert "requesting_frame->GetLastCommittedOrigin().GetURL()" in content,         "CheckPermission must use requesting_frame->GetLastCommittedOrigin() for origin"
    old_pattern = "web_contents_->GetLastCommittedURL()"
    assert old_pattern not in content,         f"CheckPermission should not use {old_pattern}, must use requesting_frame instead"


def test_check_media_access_signature_updated():
    """F2P: CheckMediaAccessPermission must accept requesting_frame parameter."""
    content = read_file("shell/browser/web_contents_permission_helper.h")
    pattern = r'bool\s+CheckMediaAccessPermission\(\s*content::RenderFrameHost\*\s+requesting_frame'
    assert re.search(pattern, content),         "CheckMediaAccessPermission signature missing requesting_frame parameter"


def test_check_media_access_passes_frame():
    """F2P: CheckMediaAccessPermission must pass requesting_frame to CheckPermission."""
    content = read_file("shell/browser/web_contents_permission_helper.cc")
    func_pattern = r'bool\s+WebContentsPermissionHelper::CheckMediaAccessPermission\([^)]+\)\s*const\s*\{[^}]+CheckPermission\s*\(\s*requesting_frame'
    assert re.search(func_pattern, content, re.DOTALL),         "CheckMediaAccessPermission must pass requesting_frame to CheckPermission"


def test_web_contents_passes_render_frame_host():
    """F2P: WebContents::CheckMediaAccessPermission must pass render_frame_host."""
    content = read_file("shell/browser/api/electron_api_web_contents.cc")
    pattern = r'permission_helper->CheckMediaAccessPermission\(\s*render_frame_host'
    assert re.search(pattern, content),         "WebContents must pass render_frame_host to CheckMediaAccessPermission"


def test_check_serial_access_signature_updated():
    """F2P: CheckSerialAccessPermission must accept requesting_frame parameter instead of origin."""
    content = read_file("shell/browser/web_contents_permission_helper.h")
    pattern = r'bool\s+CheckSerialAccessPermission\(\s*content::RenderFrameHost\*\s+requesting_frame\s*\)\s*const'
    assert re.search(pattern, content),         "CheckSerialAccessPermission signature must have requesting_frame parameter"
    old_pattern = r'CheckSerialAccessPermission\(\s*const\s+url::Origin&'
    assert not re.search(old_pattern, content),         "CheckSerialAccessPermission should not take url::Origin parameter"


def test_serial_delegate_passes_frame():
    """F2P: ElectronSerialDelegate must pass frame to CheckSerialAccessPermission."""
    content = read_file("shell/browser/serial/electron_serial_delegate.cc")
    assert "CheckSerialAccessPermission(frame)" in content,         "ElectronSerialDelegate must pass frame (not origin) to CheckSerialAccessPermission"


def test_check_serial_access_uses_requesting_frame():
    """F2P: CheckSerialAccessPermission must use requesting_frame for security origin."""
    content = read_file("shell/browser/web_contents_permission_helper.cc")
    func_start = content.find("bool WebContentsPermissionHelper::CheckSerialAccessPermission(")
    assert func_start != -1, "CheckSerialAccessPermission function not found"
    next_func = content.find("\nbool WebContentsPermissionHelper::", func_start + 1)
    if next_func == -1:
        next_marker = content.find("WEB_CONTENTS_USER_DATA_KEY_IMPL", func_start)
        func_end = next_marker if next_marker != -1 else len(content)
    else:
        func_end = next_func
    func_body = content[func_start:func_end]
    assert "requesting_frame->GetLastCommittedOrigin().GetURL().spec()" in func_body,         "CheckSerialAccessPermission must use requesting_frame to get security origin"
    assert "CheckPermission(requesting_frame" in func_body,         "CheckSerialAccessPermission must pass requesting_frame to CheckPermission"


def test_header_guards_follow_convention():
    """P2P: Header guards must follow Electron's naming convention."""
    content = read_file("shell/browser/web_contents_permission_helper.h")
    guard_pattern = r'#ifndef\s+ELECTRON_SHELL_BROWSER_[A-Z_]+_H_'
    assert re.search(guard_pattern, content),         "Header guard must follow ELECTRON_SHELL_BROWSER_*_H_ convention"


def test_no_web_contents_primary_main_frame_in_check_permission():
    """F2P: CheckPermission must not use GetPrimaryMainFrame."""
    content = read_file("shell/browser/web_contents_permission_helper.cc")
    func_start = content.find("bool WebContentsPermissionHelper::CheckPermission(")
    assert func_start != -1, "CheckPermission function not found"
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
    assert "GetPrimaryMainFrame" not in func_body,         "CheckPermission must not use GetPrimaryMainFrame, should use requesting_frame parameter"


def test_clang_format():
    """P2P: Modified C++ files must follow clang-format rules."""
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
    assert r.returncode == 0,         f"clang-format check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_modified_headers_have_guards():
    """P2P: Modified header files must have header guards."""
    modified_headers = [
        "shell/browser/web_contents_permission_helper.h",
    ]
    for header in modified_headers:
        content = read_file(header)
        guard_pattern = r'#ifndef\s+ELECTRON_[A-Z_]+_H_'
        endif_pattern = r'#endif\s+//\s+ELECTRON_[A-Z_]+_H_'
        assert re.search(guard_pattern, content),             f"{header}: Missing or invalid header guard"
        assert re.search(endif_pattern, content),             f"{header}: Missing or invalid #endif comment"


def test_cpplint():
    """P2P: Modified C++ files must pass cpplint checks."""
    subprocess.run(
        ["pip", "install", "cpplint", "-q"],
        capture_output=True,
        timeout=60,
        cwd=REPO,
    )
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
        ["/usr/local/bin/cpplint",
         "--filter=" + cpplint_filters] + modified_files,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0,         f"cpplint check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


def test_modified_files_exist():
    """P2P: All modified files must exist in the repository."""
    modified_files = [
        "shell/browser/web_contents_permission_helper.h",
        "shell/browser/web_contents_permission_helper.cc",
        "shell/browser/api/electron_api_web_contents.cc",
        "shell/browser/serial/electron_serial_delegate.cc",
    ]
    for filepath in modified_files:
        full_path = REPO / filepath
        assert full_path.exists(), f"Modified file does not exist: {filepath}"
        assert full_path.is_file(), f"Modified path is not a file: {filepath}"
        content = full_path.read_text()
        assert len(content) > 0, f"Modified file is empty: {filepath}"


def test_serial_delegate_has_can_request_port_permission():
    """P2P: ElectronSerialDelegate must have CanRequestPortPermission method."""
    content = read_file("shell/browser/serial/electron_serial_delegate.cc")
    assert "ElectronSerialDelegate::CanRequestPortPermission" in content,         "ElectronSerialDelegate must have CanRequestPortPermission method"


def test_web_contents_permission_helper_structure():
    """P2P: WebContentsPermissionHelper must have expected class structure."""
    h_content = read_file("shell/browser/web_contents_permission_helper.h")
    cc_content = read_file("shell/browser/web_contents_permission_helper.cc")
    assert "class WebContentsPermissionHelper" in h_content,         "WebContentsPermissionHelper class must be defined in header"
    assert "CheckMediaAccessPermission" in h_content,         "CheckMediaAccessPermission must be declared in header"
    assert "CheckSerialAccessPermission" in h_content,         "CheckSerialAccessPermission must be declared in header"
    assert "CheckPermission" in h_content,         "CheckPermission must be declared in header"
    assert "WebContentsPermissionHelper::CheckMediaAccessPermission" in cc_content,         "CheckMediaAccessPermission must be implemented"
    assert "WebContentsPermissionHelper::CheckSerialAccessPermission" in cc_content,         "CheckSerialAccessPermission must be implemented"
    assert "WebContentsPermissionHelper::CheckPermission" in cc_content,         "CheckPermission must be implemented"


def test_shell_directory_clang_format():
    """P2P: All C++ files in shell/browser must pass clang-format."""
    r = subprocess.run(
        ['python3', 'script/run-clang-format.py', '-r', '-c', 'shell/browser/'],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0,         f"clang-format check failed for shell/browser/:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_git_repository_valid():
    """P2P: Git repository must be in a valid state."""
    r = subprocess.run(
        ['git', 'status', '--short'],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, "Git status failed"
    r = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, "Git rev-parse failed"
    commit = r.stdout.strip()
    expected_commit = '821b738db0a64c863e8371e7141564cef70d56b8'
    assert commit == expected_commit,         f"Expected commit {expected_commit}, got {commit}"


def test_no_merge_conflict_markers():
    """P2P: Modified files must not contain merge conflict markers."""
    modified_files = [
        'shell/browser/web_contents_permission_helper.h',
        'shell/browser/web_contents_permission_helper.cc',
        'shell/browser/api/electron_api_web_contents.cc',
        'shell/browser/serial/electron_serial_delegate.cc',
    ]
    for filepath in modified_files:
        content = read_file(filepath)
        assert '<<<<<<<' not in content, f"{filepath}: Contains merge conflict markers (<<<<<<<)"
        assert '=======' not in content, f"{filepath}: Contains merge conflict markers (=======)"
        assert '>>>>>>>' not in content, f"{filepath}: Contains merge conflict markers (>>>>>>>)"


def test_file_utf8_encoding():
    """P2P: All modified files must be valid UTF-8 encoded."""
    modified_files = [
        'shell/browser/web_contents_permission_helper.h',
        'shell/browser/web_contents_permission_helper.cc',
        'shell/browser/api/electron_api_web_contents.cc',
        'shell/browser/serial/electron_serial_delegate.cc',
    ]
    for filepath in modified_files:
        full_path = REPO / filepath
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError as e:
            assert False, f"{filepath}: Not valid UTF-8 encoded: {e}"


def test_no_trailing_whitespace_in_modified():
    """P2P: Modified files must not have trailing whitespace."""
    modified_files = [
        'shell/browser/web_contents_permission_helper.h',
        'shell/browser/web_contents_permission_helper.cc',
        'shell/browser/api/electron_api_web_contents.cc',
        'shell/browser/serial/electron_serial_delegate.cc',
    ]
    for filepath in modified_files:
        content = read_file(filepath)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                assert False, f"{filepath}:{i} has trailing whitespace"


def test_patches_config_valid():
    """P2P: Patches config must be valid JSON with required structure."""
    import json
    config_path = REPO / "patches" / "config.json"
    assert config_path.exists(), "patches/config.json must exist"
    content = config_path.read_text()
    try:
        config = json.loads(content)
    except json.JSONDecodeError as e:
        assert False, f"patches/config.json is not valid JSON: {e}"
    for entry in config:
        assert "patch_dir" in entry, "Each config entry must have 'patch_dir'"
        assert "repo" in entry, "Each config entry must have 'repo'"


def test_patches_directory_structure():
    """P2P: Chromium patches directory must have valid .patches file."""
    chromium_patches_dir = REPO / "patches" / "chromium"
    dot_patches = chromium_patches_dir / ".patches"
    assert dot_patches.exists(), "patches/chromium/.patches file must exist"
    content = dot_patches.read_text().strip()
    assert content, ".patches file should not be empty"
    patch_files = content.split('\n')
    for patch_file in patch_files:
        if patch_file.strip():
            patch_path = chromium_patches_dir / patch_file.strip()
            assert patch_path.exists(), f"Patch file listed in .patches not found: {patch_file}"


def test_clang_format_shell_browser():
    """P2P: All C++ files in shell/browser must pass clang-format."""
    r = subprocess.run(
        ["python3", "script/run-clang-format.py", "-r", "-c", "-j", "4", "shell/browser/"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0,         f"clang-format check failed for shell/browser/:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_cpplint_modified_files():
    """P2P: Modified C++ files must pass cpplint with Electron's filters."""
    subprocess.run(
        ["pip", "install", "cpplint", "-q"],
        capture_output=True,
        timeout=60,
    )
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
        ["/usr/local/bin/cpplint", "--filter=" + cpplint_filters] + modified_files,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0,         f"cpplint check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_shell_common_clang_format():
    """P2P: shell/common C++ files must pass clang-format."""
    r = subprocess.run(
        ["python3", "script/run-clang-format.py", "-r", "-c", "-j", "4", "shell/common/"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0,         f"clang-format check failed for shell/common/:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_git_no_uncommitted_changes():
    """P2P: Git repository must have no uncommitted changes at base commit."""
    r = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, "git diff command failed"
    assert r.stdout.strip() == "",         f"Repository has uncommitted changes:\n{r.stdout}"
