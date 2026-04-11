import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
CHAT_CONTEXT_KEYS = f"{REPO}/src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts"

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

# Debug script that shows what's happening
r = _run_node("""
const fs=require("fs");
console.error("Reading file:", process.argv[1]);
const src=fs.readFileSync(process.argv[1],"utf8");
console.error("File length:", src.length);
console.error("Has isFirstRequest:", src.includes("isFirstRequest"));
if(!src.includes("isFirstRequest")) {
    console.error("ERROR: isFirstRequest not found - throwing");
    throw new Error("not found");
}
console.log("PASS");
""", file_path=CHAT_CONTEXT_KEYS)
print(f"returncode: {r.returncode}")
print(f"stdout: {r.stdout}")
print(f"stderr: {r.stderr}")
