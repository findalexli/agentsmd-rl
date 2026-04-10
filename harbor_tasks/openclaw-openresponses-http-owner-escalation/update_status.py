import json
from pathlib import Path

status_path = Path("/workspace/task/status.json")
with open(status_path, "r") as f:
    data = json.load(f)

data["nodes"]["p2p_enrichment"]["status"] = "pass"
data["nodes"]["p2p_enrichment"]["notes"] = "Added test_repo_lint (pnpm lint), test_repo_format (npx oxfmt), and test_repo_parity_tests (npx vitest run src/gateway/openresponses-parity.test.ts) as pass_to_pass tests which successfully run real CI commands using subprocess.run(). Verified they pass on base commit and fail_to_pass tests fail on base but pass after solve.sh."

with open(status_path, "w") as f:
    json.dump(data, f, indent=4)
