#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotfiles

# Idempotency guard
if grep -qF "crabfit-cli respond EVENT_ID --name \"Bob\" --slots 1000-19012026 1100-19012026" "pkgs/crabfit-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/pkgs/crabfit-cli/SKILL.md b/pkgs/crabfit-cli/SKILL.md
@@ -7,22 +7,22 @@ description: Create and manage Crab.fit scheduling events. Use for coordinating
 
 ```bash
 # Create an event for the next 3 days, 9am-5pm
-python3 crabfit_cli.py create --dates +0:+2 --start 9 --end 17
+crabfit-cli create --dates +0:+2 --start 9 --end 17
 
 # Create a named event for specific dates
-python3 crabfit_cli.py create --name "Team Meeting" --dates 2026-01-20,2026-01-22
+crabfit-cli create --name "Team Meeting" --dates 2026-01-20,2026-01-22
 
 # Create with specific timezone
-python3 crabfit_cli.py create --dates +0:+6 --timezone America/New_York
+crabfit-cli create --dates +0:+6 --timezone America/New_York
 
 # Add your availability (all slots)
-python3 crabfit_cli.py respond EVENT_ID --name "Alice" --all
+crabfit-cli respond EVENT_ID --name "Alice" --all
 
 # Add specific availability
-python3 crabfit_cli.py respond EVENT_ID --name "Bob" --slots 1000-19012026 1100-19012026
+crabfit-cli respond EVENT_ID --name "Bob" --slots 1000-19012026 1100-19012026
 
 # Show event with availability overlap
-python3 crabfit_cli.py show EVENT_ID
+crabfit-cli show EVENT_ID
 ```
 
 # Date Formats
@@ -45,12 +45,12 @@ Jan 19, 2026).
 
 ```bash
 # 1. Create event
-python3 crabfit_cli.py create --name "Project Sync" --dates +1:+5 --start 10 --end 16
+crabfit-cli create --name "Project Sync" --dates +1:+5 --start 10 --end 16
 
 # 2. Share URL with participants, they respond via web or CLI
 
 # 3. Check availability overlap
-python3 crabfit_cli.py show project-sync-123456
+crabfit-cli show project-sync-123456
 ```
 
 Output shows best meeting times:
PATCH

echo "Gold patch applied."
