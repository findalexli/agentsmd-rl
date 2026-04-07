#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotent: skip if already applied
if [ -f .claude/skills/copilot/approve.sh ]; then
    echo "Patch already applied."
    exit 0
fi

# Create approve.sh
cat > .claude/skills/copilot/approve.sh <<'SCRIPT'
#!/usr/bin/env bash
# Rerun action_required workflow runs for Copilot PRs.
# The /approve API fails with 'not a fork pull request'. Use /rerun instead.
set -euo pipefail

repo="$1"
pr_number="$2"

head_sha=$(gh pr view "$pr_number" --repo "$repo" --json headRefOid --jq '.headRefOid')

run_ids=$(
  gh api --paginate "repos/${repo}/actions/runs?head_sha=${head_sha}" \
    --jq '
      .workflow_runs[]
      | select(.conclusion == "action_required" and .actor.login == "Copilot")
      | .id
    '
)

if [[ -z "$run_ids" ]]; then
  echo "No action_required workflow runs found"
  exit 0
fi

echo "Rerunning action_required workflows..."
while IFS= read -r run_id; do
  gh api --method POST "repos/${repo}/actions/runs/${run_id}/rerun" 2>&1 && \
    echo "  Rerun triggered for run $run_id" || \
    echo "  Failed to rerun run $run_id"
done <<< "$run_ids"
SCRIPT

chmod +x .claude/skills/copilot/approve.sh

# Update SKILL.md: add approve.sh to allowed-tools
sed -i '/Bash(bash .claude\/skills\/copilot\/poll.sh \*)/a\  - Bash(bash .claude/skills/copilot/approve.sh *)' .claude/skills/copilot/SKILL.md

# Append approving workflows section to SKILL.md
cat >> .claude/skills/copilot/SKILL.md <<'EOF'

## Approving workflows

Approve workflows to run once the PR is finalized:

```bash
bash .claude/skills/copilot/approve.sh "<owner>/<repo>" <pr_number>
```
EOF

echo "Patch applied successfully."
