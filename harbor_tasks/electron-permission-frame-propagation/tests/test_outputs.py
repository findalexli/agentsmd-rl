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


def test_permission_frame_propagation_behavioral():
    """F2P: Verify permission frame propagation is correctly implemented via subprocess."""
    analysis_script = '''
import re, sys, json

def extract_function_body(content, func_sig):
    start = content.find(func_sig)
    if start == -1:
        return None
    brace = content.find("{", start)
    if brace == -1:
        return None
    depth, pos = 1, brace + 1
    while depth > 0 and pos < len(content):
        if content[pos] == "{": depth += 1
        elif content[pos] == "}": depth -= 1
        pos += 1
    return content[start:pos]

results = {}

with open("shell/browser/web_contents_permission_helper.h") as f:
    header = f.read()
with open("shell/browser/web_contents_permission_helper.cc") as f:
    impl = f.read()
with open("shell/browser/api/electron_api_web_contents.cc") as f:
    wc = f.read()
with open("shell/browser/serial/electron_serial_delegate.cc") as f:
    sd = f.read()

# 1. CheckPermission signature has RenderFrameHost* as first param
results["cp_sig"] = bool(re.search(
    r"bool\\s+CheckPermission\\(\\s*content::RenderFrameHost\\*", header))

# 2. CheckPermission body uses frame origin, not main frame
body = extract_function_body(impl, "bool WebContentsPermissionHelper::CheckPermission(")
if body:
    results["cp_frame_origin"] = "GetLastCommittedOrigin().GetURL()" in body
    results["cp_no_main_frame"] = "GetPrimaryMainFrame" not in body
else:
    results["cp_frame_origin"] = False
    results["cp_no_main_frame"] = False

# 3. CheckMediaAccessPermission passes frame to CheckPermission
media_body = extract_function_body(impl,
    "bool WebContentsPermissionHelper::CheckMediaAccessPermission(")
if media_body:
    results["media_passes_frame"] = bool(re.search(
        r"CheckPermission\\s*\\(\\s*\\w+\\s*,\\s*blink", media_body))
else:
    results["media_passes_frame"] = False

# 4. WebContents passes render_frame_host
results["wc_passes_rfh"] = bool(re.search(
    r"CheckMediaAccessPermission\\s*\\(\\s*render_frame_host", wc))

# 5. Serial delegate passes frame, not origin
results["sd_passes_frame"] = bool(re.search(
    r"CheckSerialAccessPermission\\s*\\(\\s*frame\\s*\\)", sd))

print(json.dumps(results))
sys.exit(0 if all(results.values()) else 1)
'''
    r = subprocess.run(
        ["python3", "-c", analysis_script],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Frame propagation check failed:\n{r.stdout}\n{r.stderr}"
    import json as _json
    data = _json.loads(r.stdout.strip())
    assert data["cp_sig"], "CheckPermission must accept RenderFrameHost*"
    assert data["cp_frame_origin"], "CheckPermission must use frame's GetLastCommittedOrigin()"
    assert data["cp_no_main_frame"], "CheckPermission must not use GetPrimaryMainFrame"
    assert data["media_passes_frame"], "CheckMediaAccessPermission must pass frame to CheckPermission"
    assert data["wc_passes_rfh"], "WebContents must pass render_frame_host"
    assert data["sd_passes_frame"], "SerialDelegate must pass frame"


def test_check_permission_signature_updated():
    """F2P: CheckPermission must accept RenderFrameHost as first parameter."""
    content = read_file("shell/browser/web_contents_permission_helper.h")
    # Check that CheckPermission takes a RenderFrameHost* (flexible on parameter name)
    pattern = r'bool\s+CheckPermission\(\s*content::RenderFrameHost\*\s+\w+'
    assert re.search(pattern, content), \
        "CheckPermission signature must accept content::RenderFrameHost* as first parameter"


def test_check_permission_uses_render_frame_host_for_origin():
    """F2P: CheckPermission must use the frame parameter to get origin."""
    content = read_file("shell/browser/web_contents_permission_helper.cc")
    func_start = content.find("bool WebContentsPermissionHelper::CheckPermission(")
    assert func_start != -1, "CheckPermission function not found"
    # Extract function body
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
    # Must call GetLastCommittedOrigin().GetURL() on the frame parameter
    assert re.search(r'GetLastCommittedOrigin\(\)\.GetURL\(\)', func_body), \
        "CheckPermission must call GetLastCommittedOrigin().GetURL() on the frame parameter"
    # Must NOT use GetPrimaryMainFrame
    assert "GetPrimaryMainFrame" not in func_body, \
        "CheckPermission must not use GetPrimaryMainFrame"


def test_check_media_access_signature_updated():
    """F2P: CheckMediaAccessPermission must accept RenderFrameHost parameter."""
    content = read_file("shell/browser/web_contents_permission_helper.h")
    # Check signature accepts RenderFrameHost* (flexible on parameter name)
    pattern = r'bool\s+CheckMediaAccessPermission\(\s*content::RenderFrameHost\*\s+\w+'
    assert re.search(pattern, content), \
        "CheckMediaAccessPermission must accept content::RenderFrameHost* parameter"


def test_check_media_access_passes_frame():
    """F2P: CheckMediaAccessPermission must pass frame to CheckPermission."""
    content = read_file("shell/browser/web_contents_permission_helper.cc")
    func_start = content.find("bool WebContentsPermissionHelper::CheckMediaAccessPermission(")
    assert func_start != -1, "CheckMediaAccessPermission function not found"
    # Extract function body
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
    # Check that CheckPermission is called with the frame parameter (first argument)
    # The frame parameter is passed as first argument to CheckPermission
    assert re.search(r'CheckPermission\s*\(\s*\w+\s*,\s*blink_type', func_body), \
        "CheckMediaAccessPermission must pass frame as first arg to CheckPermission"


def test_web_contents_passes_render_frame_host():
    """F2P: WebContents::CheckMediaAccessPermission must pass render_frame_host."""
    content = read_file("shell/browser/api/electron_api_web_contents.cc")
    # Check that WebContents calls CheckMediaAccessPermission with render_frame_host
    pattern = r'CheckMediaAccessPermission\s*\(\s*render_frame_host'
    assert re.search(pattern, content), \
        "WebContents must pass render_frame_host to CheckMediaAccessPermission"


def test_check_serial_access_signature_updated():
    """F2P: CheckSerialAccessPermission must accept RenderFrameHost instead of url::Origin."""
    content = read_file("shell/browser/web_contents_permission_helper.h")
    # Must have RenderFrameHost* parameter (flexible on name)
    pattern = r'bool\s+CheckSerialAccessPermission\s*\(\s*content::RenderFrameHost\*\s+\w+'
    assert re.search(pattern, content), \
        "CheckSerialAccessPermission must accept content::RenderFrameHost* parameter"
    # Must NOT have old url::Origin parameter
    old_pattern = r'CheckSerialAccessPermission\s*\(\s*const\s+url::Origin&'
    assert not re.search(old_pattern, content), \
        "CheckSerialAccessPermission should not take url::Origin parameter"


def test_serial_delegate_passes_frame_not_origin():
    """F2P: ElectronSerialDelegate must pass frame (not origin) to CheckSerialAccessPermission."""
    content = read_file("shell/browser/serial/electron_serial_delegate.cc")
    # Check that CheckSerialAccessPermission is called with the frame variable
    assert re.search(r'CheckSerialAccessPermission\s*\(\s*frame\s*\)', content), \
        "ElectronSerialDelegate must pass frame to CheckSerialAccessPermission"
    # Must not pass origin directly (old bad pattern)
    assert not re.search(r'CheckSerialAccessPermission\s*\(\s*frame->GetLastCommittedOrigin\s*\(\s*\)\s*\)', content), \
        "ElectronSerialDelegate should pass frame, not origin"


def test_check_serial_access_uses_frame_for_origin():
    """F2P: CheckSerialAccessPermission must use frame to derive security origin."""
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
    # Must derive origin from the frame (call GetLastCommittedOrigin on the frame param)
    assert re.search(r'\w+->GetLastCommittedOrigin\(\)\.GetURL\(\)', func_body), \
        "CheckSerialAccessPermission must derive origin from the frame parameter"
    # Must pass frame to CheckPermission
    assert re.search(r'CheckPermission\s*\(\s*\w+', func_body), \
        "CheckSerialAccessPermission must pass the frame to CheckPermission"


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
    assert "GetPrimaryMainFrame" not in func_body, \
        "CheckPermission must not use GetPrimaryMainFrame"


def test_header_guards_follow_convention():
    """P2P: Header guards must follow Electron naming convention."""
    content = read_file("shell/browser/web_contents_permission_helper.h")
    guard_pattern = r'#ifndef\s+ELECTRON_SHELL_BROWSER_[A-Z_]+_H_'
    assert re.search(guard_pattern, content), \
        "Header guard must follow ELECTRON_SHELL_BROWSER_*_H_ convention"


def test_clang_format():
    """P2P: Modified C++ files must follow clang-format rules."""
    r = subprocess.run(
        ["python3", "script/run-clang-format.py", "-r",
         "--clang-format-executable", "/usr/bin/clang-format",
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
    """P2P: Modified header files must have header guards."""
    modified_headers = [
        "shell/browser/web_contents_permission_helper.h",
    ]
    for header in modified_headers:
        content = read_file(header)
        guard_pattern = r'#ifndef\s+ELECTRON_[A-Z_]+_H_'
        endif_pattern = r'#endif\s+//\s+ELECTRON_[A-Z_]+_H_'
        assert re.search(guard_pattern, content), \
            f"{header}: Missing or invalid header guard"
        assert re.search(endif_pattern, content), \
            f"{header}: Missing or invalid #endif comment"


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
    assert r.returncode == 0, \
        f"cpplint check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


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
    assert "ElectronSerialDelegate::CanRequestPortPermission" in content, \
        "ElectronSerialDelegate must have CanRequestPortPermission method"


def test_web_contents_permission_helper_structure():
    """P2P: WebContentsPermissionHelper must have expected class structure."""
    h_content = read_file("shell/browser/web_contents_permission_helper.h")
    cc_content = read_file("shell/browser/web_contents_permission_helper.cc")
    assert "class WebContentsPermissionHelper" in h_content, \
        "WebContentsPermissionHelper class must be defined in header"
    assert "CheckMediaAccessPermission" in h_content, \
        "CheckMediaAccessPermission must be declared in header"
    assert "CheckSerialAccessPermission" in h_content, \
        "CheckSerialAccessPermission must be declared in header"
    assert "CheckPermission" in h_content, \
        "CheckPermission must be declared in header"
    assert "WebContentsPermissionHelper::CheckMediaAccessPermission" in cc_content, \
        "CheckMediaAccessPermission must be implemented"
    assert "WebContentsPermissionHelper::CheckSerialAccessPermission" in cc_content, \
        "CheckSerialAccessPermission must be implemented"
    assert "WebContentsPermissionHelper::CheckPermission" in cc_content, \
        "CheckPermission must be implemented"


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
    assert commit == expected_commit, \
        f"Expected commit {expected_commit}, got {commit}"


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
