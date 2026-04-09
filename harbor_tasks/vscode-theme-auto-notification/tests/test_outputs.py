"""
Task: vscode-theme-auto-notification
Repo: microsoft/vscode @ af50a47c13e23e0b3c46719dbd92fe00144362a5

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Uses Node.js subprocess to parse TypeScript source — extracting method
bodies via brace counting so assertions are scoped to the right function,
not the whole file.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/vscode"
TARGET = "src/vs/workbench/services/themes/browser/workbenchThemeService.ts"


# -- Helpers ----------------------------------------------------------------

def _node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# Template: extract a method body from the TS file via brace counting.
# Placeholders TARGET_PATH and METHOD_NAME are replaced before execution.
_EXTRACT_TMPL = """\
const fs = require("fs");
const src = fs.readFileSync("TARGET_PATH", "utf8");
let idx = src.indexOf("private METHOD_NAME(");
if (idx === -1) { idx = src.indexOf("async METHOD_NAME("); }
if (idx === -1) { process.stdout.write("null"); process.exit(0); }
const brace = src.indexOf("{", idx);
if (brace === -1) { process.stdout.write("null"); process.exit(0); }
let depth = 1, i = brace + 1;
while (depth > 0 && i < src.length) {
    if (src[i] === "{") depth++;
    else if (src[i] === "}") depth--;
    i++;
}
process.stdout.write(JSON.stringify(src.substring(brace + 1, i - 1)));
"""


def _method_body(method_name: str) -> str | None:
    """Extract a method body from the TS file using Node.js brace counting."""
    js = _EXTRACT_TMPL.replace("TARGET_PATH", TARGET).replace("METHOD_NAME", method_name)
    r = _node(js)
    if r.returncode != 0:
        return None
    out = r.stdout.strip()
    return json.loads(out) if out != "null" else None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_method_exists():
    """showThemeAutoUpdatedNotification private method is defined in WorkbenchThemeService"""
    body = _method_body("showThemeAutoUpdatedNotification")
    assert body is not None, "showThemeAutoUpdatedNotification method not defined"


# [pr_diff] fail_to_pass
def test_method_called_in_init():
    """showThemeAutoUpdatedNotification is called during theme initialization"""
    init_body = _method_body("initialize")
    assert init_body is not None, "initialize method not found"
    assert "this.showThemeAutoUpdatedNotification()" in init_body, (
        "showThemeAutoUpdatedNotification is not called during initialization"
    )


# [pr_diff] fail_to_pass
def test_storage_key_for_one_time_notification():
    """A storage key constant exists and is read via getBoolean to prevent repeat display"""
    body = _method_body("showThemeAutoUpdatedNotification")
    assert body is not None, "Method not found"
    assert "THEME_AUTO_UPDATED_NOTIFICATION_KEY" in body, "Storage key constant missing"
    assert "getBoolean" in body, "Storage key not used in getBoolean guard"


# [pr_diff] fail_to_pass
def test_skips_new_users():
    """storageService.isNew check suppresses notification for brand-new users"""
    body = _method_body("showThemeAutoUpdatedNotification")
    assert body is not None, "Method not found"
    assert "isNew" in body, (
        "No isNew check — new users would incorrectly see the notification"
    )


# [pr_diff] fail_to_pass
def test_skips_explicit_theme_choice():
    """isDefaultColorTheme() guard prevents notification for users who explicitly chose their theme"""
    body = _method_body("showThemeAutoUpdatedNotification")
    assert body is not None, "Method not found"
    assert "isDefaultColorTheme" in body, (
        "No isDefaultColorTheme() guard — users who explicitly chose a theme would see the notification"
    )


# [pr_diff] fail_to_pass
def test_has_browse_themes_action():
    """Notification offers a Browse Themes action (workbench.action.selectTheme or browseThemes label)"""
    body = _method_body("showThemeAutoUpdatedNotification")
    assert body is not None, "Method not found"
    has_cmd = "workbench.action.selectTheme" in body
    has_label = "browseThemes" in body
    assert has_cmd or has_label, "No Browse Themes action found in the notification"


# [pr_diff] fail_to_pass
def test_has_revert_action():
    """Notification offers a Revert action that calls setColorTheme to restore the previous default"""
    body = _method_body("showThemeAutoUpdatedNotification")
    assert body is not None, "Method not found"
    assert "setColorTheme" in body, "No setColorTheme call in revert action"


# [pr_diff] fail_to_pass
def test_stores_shown_flag_on_close():
    """THEME_AUTO_UPDATED_NOTIFICATION_KEY is persisted to storage when notification is dismissed"""
    body = _method_body("showThemeAutoUpdatedNotification")
    assert body is not None, "Method not found"
    assert "THEME_AUTO_UPDATED_NOTIFICATION_KEY" in body, "Notification key not referenced"
    assert "storageService.store" in body, (
        "Notification flag not stored on close — user would see notification again"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — config-derived coding rules
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:132 @ af50a47c13e23e0b3c46719dbd92fe00144362a5
def test_nls_localize_used_for_notification():
    """Notification message strings use nls.localize for externalization/localization"""
    body = _method_body("showThemeAutoUpdatedNotification")
    assert body is not None, "Method not found"
    assert "nls.localize" in body, (
        "Notification strings must use nls.localize for localization "
        "(copilot-instructions.md:132)"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:144 @ af50a47c13e23e0b3c46719dbd92fe00144362a5
def test_disposable_registered_with_register():
    """Event listener on notification handle is registered via this._register for proper disposal"""
    body = _method_body("showThemeAutoUpdatedNotification")
    assert body is not None, "Method not found"
    assert "this._register" in body, (
        "Disposable event listener not registered via this._register "
        "(copilot-instructions.md:144)"
    )
