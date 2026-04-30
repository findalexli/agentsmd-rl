import json
from pathlib import Path

status_file = Path("/workspace/task/status.json")
if status_file.exists():
    status = json.loads(status_file.read_text())
    
    if "nodes" not in status:
        status["nodes"] = {}
        
    status["nodes"]["p2p_enrichment"] = {
        "status": "completed",
        "notes": "Added 4 real pass_to_pass checks using 'node --check --experimental-strip-types' as the CI command, validating the syntax of the modified file and its corresponding test files without requiring external dependencies or network access. Replaced the 9 erroneous static file-read checks previously labeled as repo_tests."
    }
    
    status_file.write_text(json.dumps(status, indent=2))
    print("Status updated.")
