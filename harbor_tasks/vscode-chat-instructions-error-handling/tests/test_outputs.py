"""
Task: vscode-chat-instructions-error-handling
Repo: microsoft/vscode @ ba1bdcd30b83d8090ee0f28549299a52874d71ac

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fail-to-pass tests use Node.js subprocess to parse TypeScript with brace-counting,
verifying proper nesting (not just grep/regex string matching).
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/vscode"
TARGET_FILE = (
    f"{REPO}/src/vs/workbench/contrib/chat/browser/widget/chatWidget.ts"
)


def _node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Node.js script."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using Node.js code execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_try_block_around_collect():
    """_autoAttachInstructions wraps await computer.collect() in a try block."""
    # Node.js: extract method body via brace counting, verify collect is inside try
    r = _node(
        "const fs=require('fs');"
        f"const c=fs.readFileSync('{TARGET_FILE}','utf8');"
        "const s=c.indexOf('async _autoAttachInstructions');"
        "if(s===-1){process.stderr.write('method not found');process.exit(1);}"
        # Find the method body's opening { (after the signature's closing ))
        "let sigEnd=c.indexOf(')',s);"
        "if(sigEnd===-1){process.stderr.write('signature end not found');process.exit(1);}"
        "let ob=c.indexOf('{',sigEnd),d=0,e=ob;"
        "for(let i=ob;i<c.length;i++){if(c[i]==='{')d++;else if(c[i]==='}')d--;if(d===0){e=i+1;break;}}"
        "const body=c.substring(s,e);"
        "const ti=body.indexOf('try {');"
        "if(ti===-1){process.stderr.write('no try block');process.exit(1);}"
        "let td=0,tbs=-1,tbe=-1;"
        "for(let i=ti+4;i<body.length;i++){"
        "if(body[i]==='{'){if(td===0)tbs=i+1;td++;}"
        "else if(body[i]==='}'){td--;if(td===0){tbe=i;break;}}"
        "}"
        "if(tbs===-1||tbe===-1){process.stderr.write('bad try block');process.exit(1);}"
        "const tb=body.substring(tbs,tbe);"
        "if(!tb.includes('await computer.collect')){"
        "process.stderr.write('computer.collect NOT inside try block');process.exit(1);"
        "}"
        "console.log('PASS');"
    )
    assert r.returncode == 0, f"Node analysis failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_catch_block_logs_error():
    """Catch block catches the exception and logs it via logService.error with the expected message."""
    # Node.js: extract catch block via brace counting, verify logService.error + message
    r = _node(
        "const fs=require('fs');"
        f"const c=fs.readFileSync('{TARGET_FILE}','utf8');"
        "const s=c.indexOf('async _autoAttachInstructions');"
        "if(s===-1){process.stderr.write('method not found');process.exit(1);}"
        # Find the method body's opening { (after the signature's closing ))
        "let sigEnd=c.indexOf(')',s);"
        "if(sigEnd===-1){process.stderr.write('signature end not found');process.exit(1);}"
        "let ob=c.indexOf('{',sigEnd),d=0,e=ob;"
        "for(let i=ob;i<c.length;i++){if(c[i]==='{')d++;else if(c[i]==='}')d--;if(d===0){e=i+1;break;}}"
        "const body=c.substring(s,e);"
        "const ci=body.indexOf('catch (err)');"
        "if(ci===-1){process.stderr.write('no catch block');process.exit(1);}"
        "let cd=0,cbs=-1,cbe=-1;"
        "for(let i=ci;i<body.length;i++){"
        "if(body[i]==='{'){if(cd===0)cbs=i+1;cd++;}"
        "else if(body[i]==='}'){cd--;if(cd===0){cbe=i;break;}}"
        "}"
        "if(cbs===-1||cbe===-1){process.stderr.write('bad catch block');process.exit(1);}"
        "const cb=body.substring(cbs,cbe);"
        "if(!cb.includes('logService.error')){"
        "process.stderr.write('logService.error not in catch block');process.exit(1);"
        "}"
        "if(!cb.includes('failed to compute automatic instructions')){"
        "process.stderr.write('expected error message not in catch block');process.exit(1);"
        "}"
        "console.log('PASS');"
    )
    assert r.returncode == 0, f"Node analysis failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_original_logic_preserved():
    """Core instruction-computation logic is still present inside the try block."""
    content = Path(TARGET_FILE).read_text()
    s = content.find("async _autoAttachInstructions")
    assert s != -1, "Method _autoAttachInstructions not found"
    body = content[s : s + 2000]
    assert "ComputeAutomaticInstructions" in body, (
        "ComputeAutomaticInstructions class instantiation was removed"
    )
    assert "enabledTools" in body, "enabledTools assignment was removed"
    assert "enabledSubAgents" in body, "enabledSubAgents assignment was removed"
    assert "CancellationToken.None" in body, "CancellationToken.None was removed"


# [static] pass_to_pass
def test_catch_is_not_empty():
    """Catch block has real error handling -- not an empty {} or just a comment."""
    content = Path(TARGET_FILE).read_text()
    s = content.find("async _autoAttachInstructions")
    assert s != -1, "Method _autoAttachInstructions not found"
    body = content[s : s + 2000]
    catch_match = re.search(r"catch\s*\(err\)\s*\{([^}]*)\}", body, re.DOTALL)
    assert catch_match is not None, "Could not locate catch block body"
    catch_body = catch_match.group(1).strip()
    non_comment = re.sub(r"//.*", "", catch_body).strip()
    assert len(non_comment) > 0, "Catch block is empty -- exception is silently swallowed"
    assert "logService" in catch_body, (
        "Catch block must call logService to record the error"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- .github/copilot-instructions.md:147 @ ba1bdcd30b83d8090ee0f28549299a52874d71ac
def test_no_promise_then_in_method():
    """Fix uses async/await, not .then() chains (copilot-instructions.md:147)."""
    content = Path(TARGET_FILE).read_text()
    s = content.find("async _autoAttachInstructions")
    assert s != -1, "Method _autoAttachInstructions not found"
    body = content[s : s + 2000]
    assert ".then(" not in body, (
        "Fix must use 'await' syntax, not Promise.then() chains"
        " (see .github/copilot-instructions.md:147)"
    )
