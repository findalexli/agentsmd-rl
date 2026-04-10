"""
Task: vscode-chat-startover-action
Repo: microsoft/vscode @ d7ebb2cc7dcab5b7d7c9bc98ad5b96652dcab650
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
CHAT_EDITING_ACTIONS = f"{REPO}/src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts"
CHAT_CONTEXT_KEYS = f"{REPO}/src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts"
CHAT_LIST_RENDERER = f"{REPO}/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts"
CHAT_FORK_ACTIONS = f"{REPO}/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts"

def _run_node(code: str, file_path: str = "", timeout: int = 30):
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        cmd = ["node", str(script)]
        if file_path:
            cmd.append(file_path)
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO)
    finally:
        script.unlink(missing_ok=True)

def test_is_first_request_context_key():
    r = _run_node("""const fs=require("fs");const src=fs.readFileSync(process.argv[1],"utf8");if(!src.includes("isFirstRequest"))throw new Error("not found");if(!src.includes("chatFirstRequest"))throw new Error("no chatFirstRequest key");if(!src.includes("new RawContextKey")||!src.includes("isFirstRequest"))throw new Error("not RawContextKey");console.log("PASS");""", file_path=CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_start_over_action_registered():
    r = _run_node("""const fs=require("fs");const src=fs.readFileSync(process.argv[1],"utf8");if(!src.includes("class StartOverAction extends Action2"))throw new Error("not found");if(!src.includes("workbench.action.chat.startOver"))throw new Error("bad id");if(!src.includes("registerAction2(class StartOverAction"))throw new Error("not reg");console.log("PASS");""", file_path=CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_start_over_action_when_clause():
    r = _run_node("""const fs=require("fs");const src=fs.readFileSync(process.argv[1],"utf8");const idx=src.indexOf("class StartOverAction");if(idx===-1)throw new Error("not found");const block=src.substring(idx,idx+2000);if(!block.includes("isFirstRequest"))throw new Error("no isFirstRequest");console.log("PASS");""", file_path=CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_start_over_action_run_method():
    r = _run_node("""const fs=require("fs");const src=fs.readFileSync(process.argv[1],"utf8");const idx=src.indexOf("class StartOverAction");if(idx===-1)throw new Error("not found");const block=src.substring(idx,idx+2000);if(!block.includes("async run("))throw new Error("no run");if(!block.includes("setCheckpoint"))throw new Error("no setCheckpoint");if(!block.includes("restoreSnapshotWithConfirmation"))throw new Error("no restore");console.log("PASS");""", file_path=CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_first_request_bound_in_renderer():
    r = _run_node("""const fs=require("fs");const src=fs.readFileSync(process.argv[1],"utf8");if(!src.includes("isFirstRequest"))throw new Error("not found");if(!src.match(/isFirstRequest.*\.bindTo/))throw new Error("not bound");if(!src.includes("getRequests()"))throw new Error("no getRequests");console.log("PASS");""", file_path=CHAT_LIST_RENDERER)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_fork_hidden_on_first_request():
    r = _run_node("""const fs=require("fs");const src=fs.readFileSync(process.argv[1],"utf8");if(!src.includes("isFirstRequest.negate()"))throw new Error("no negate");console.log("PASS");""", file_path=CHAT_FORK_ACTIONS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_restore_checkpoint_hidden_on_first():
    r = _run_node("""const fs=require("fs");const src=fs.readFileSync(process.argv[1],"utf8");const idx=src.indexOf("class RestoreCheckpointAction");if(idx===-1)throw new Error("not found");const block=src.substring(idx,idx+2000);if(!block.includes("isFirstRequest.negate()"))throw new Error("no negate");console.log("PASS");""", file_path=CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_start_over_action_label_and_tooltip():
    r = _run_node("""const fs=require("fs");const src=fs.readFileSync(process.argv[1],"utf8");const idx=src.indexOf("class StartOverAction");if(idx===-1)throw new Error("not found");const block=src.substring(idx,idx+2000);if(!block.includes('localize2("chat.startOver.label"'))throw new Error("no label");if(!block.includes('localize2("chat.startOver.tooltip"'))throw new Error("no tooltip");if(!block.includes("f1: false"))throw new Error("no f1:false");console.log("PASS");""", file_path=CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_copyright_headers():
    r = _run_node("""const fs=require("fs");const files=["src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts","src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts"];for(const f of files){const c=fs.readFileSync(f,"utf8");if(!c.includes("Copyright (c) Microsoft Corporation"))throw new Error(f);}console.log("PASS");""", file_path=CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_file_syntax():
    r = _run_node("""const fs=require("fs");const files=["src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts","src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts"];for(const f of files){const c=fs.readFileSync(f,"utf8");if((c.match(/\{/g)||[]).length!==(c.match(/\}/g)||[]).length)throw new Error(f);}console.log("PASS");""", file_path=CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_exports_valid():
    r = _run_node("""const fs=require("fs");const k=fs.readFileSync("src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts","utf8");if(!k.includes("export namespace ChatContextKeys"))throw new Error("ns");const e=fs.readFileSync("src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts","utf8");if(!e.includes("class RestoreCheckpointAction extends Action2"))throw new Error("class");console.log("PASS");""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_chat_context_keys_structure():
    r = _run_node("""const fs=require("fs");const s=fs.readFileSync(process.argv[1],"utf8");for(const k of["isResponse","isRequest","itemId","isPendingRequest"])if(!s.includes(k))throw new Error(k);if(!s.includes("export namespace ChatContextKeys"))throw new Error("ns");console.log("PASS");""", file_path=CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_typescript_syntax_chat_files():
    r = _run_node("""const fs=require("fs");const files=["src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts","src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts"];for(const f of files){const c=fs.readFileSync(f,"utf8");if((c.match(/\{/g)||[]).length!==(c.match(/\}/g)||[]).length)throw new Error(f);}console.log("PASS");""", file_path=CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_imports_valid():
    r = _run_node("""const fs=require("fs");const files=["src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts","src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts"];const r={"chatContextKeys.ts":["nls.js"],"chatEditingActions.ts":["actions.js"]};for(const f of files){const c=fs.readFileSync(f,"utf8");const b=require("path").basename(f);for(const x of r[b]||[])if(!c.includes(x))throw new Error(x);}console.log("PASS");""", file_path=CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_context_key_patterns():
    r = _run_node("""const fs=require("fs");const s=fs.readFileSync(process.argv[1],"utf8");const p=/new\s+RawContextKey\s*\(\s*["'`]([^"'`]+)["'`]/g;const m=[...s.matchAll(p)];for(const x of m)if(!/^[a-z][a-zA-Z0-9]*(\.[a-z][a-zA-Z0-9]*)*$/.test(x[1]))throw new Error(x[1]);if(!s.includes("ContextKeyExpr"))throw new Error("ctx");console.log("PASS");""", file_path=CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_action_patterns():
    r = _run_node("""const fs=require("fs");const s=fs.readFileSync(process.argv[1],"utf8");const a=[...s.matchAll(/class\s+(\w+)Action\s+extends\s+Action2/g)];for(const m of a){const n=m[1];const p=new RegExp("registerAction2\(class\s+"+n+"Action");if(!p.test(s))throw new Error(n);}for(const i of["Action2","registerAction2","MenuId"])if(!s.includes(i))throw new Error(i);console.log("PASS");""", file_path=CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_menu_patterns():
    r = _run_node("""const fs=require("fs");const s=fs.readFileSync(process.argv[1],"utf8");if(!s.includes("ContextKeyExpr"))throw new Error("no ContextKeyExpr");if(!s.includes("MenuId.ChatMessageCheckpoint"))throw new Error("menu");console.log("PASS");""", file_path=CHAT_EDITING_ACTIONS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_import_extensions_all():
    r = _run_node("""const fs=require("fs");const files=["src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts","src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts"];for(const f of files){const c=fs.readFileSync(f,"utf8");const i=c.match(/from\s+["'`]([^"'`]+)["'`]/g)||[];for(const x of i){const m=x.match(/from\s+["'`]([^"'`]+)["'`]/);if(m&&m[1].startsWith("vs/")&&!m[1].endsWith(".js"))throw new Error(m[1]);}}console.log("PASS");""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_context_key_consistency():
    r = _run_node("""const fs=require("fs");const f={ctx:fs.readFileSync("src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts","utf8"),edit:fs.readFileSync("src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts","utf8")};for(const [n,c] of Object.entries(f))if(!c.includes("ChatContextKeys"))throw new Error(n);for(const k of["isResponse","isRequest"])if(!f.ctx.includes(k))throw new Error(k);console.log("PASS");""", file_path=CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_copyright_headers_all():
    r = _run_node("""const fs=require("fs");const files=["src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts","src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts"];for(const f of files){const c=fs.readFileSync(f,"utf8");if(!c.includes("Copyright (c) Microsoft Corporation"))throw new Error(f);if(!c.includes("MIT License"))throw new Error(f);}console.log("PASS");""", file_path=CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_basic_syntax_structure():
    r = _run_node("""const fs=require("fs");const files=["src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts","src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts"];for(const f of files){const c=fs.readFileSync(f,"utf8");if((c.match(/\{/g)||[]).length!==(c.match(/\}/g)||[]).length)throw new Error("b:"+f);if((c.match(/\(/g)||[]).length!==(c.match(/\)/g)||[]).length)throw new Error("p:"+f);}console.log("PASS");""", file_path=CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

def test_repo_vscode_patterns():
    r = _run_node("""const fs=require("fs");const k=fs.readFileSync("src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts","utf8");if(!k.includes("export namespace ChatContextKeys"))throw new Error("ns");const r=k.match(/new\s+RawContextKey/g);if(!r||r.length===0)throw new Error("raw");const e=fs.readFileSync("src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts","utf8");const a=["EditingSessionAction","WorkingSetAction"];const c=[...e.matchAll(/class\s+(\w+)\s+extends\s+Action2/g)];for(const m of c){const n=m[1];if(a.includes(n))continue;if(!e.includes("registerAction2("+n)&&!e.includes("registerAction2(class "+n))throw new Error(n);}console.log("PASS");""", file_path=CHAT_CONTEXT_KEYS)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout

# === CI/CD Pass-to-Pass Tests (origin: repo_tests) ===
# These tests run actual CI commands from the VS Code repo

def test_repo_eslint():
    """Repo's ESLint passes on codebase (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\\n{r.stderr[-1000:]}"

def test_repo_precommit_hygiene():
    """Repo's precommit hygiene checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "precommit"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Precommit hygiene failed:\\n{r.stderr[-1000:]}"

def test_repo_unit_tests_node():
    """Repo's Node.js unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "test-node"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Node unit tests failed:\\n{r.stderr[-1000:]}"
