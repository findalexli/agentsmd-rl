#!/usr/bin/env bash
# Gold patch for apache/superset PR #38648:
# add security_manager.raise_for_access(...) to QueryEstimationCommand.validate().
set -euo pipefail

cd /workspace/superset

# Idempotency: if the distinctive line is already present, the patch has been applied.
if grep -q "security_manager.raise_for_access(database=self._database)" \
        superset/commands/sql_lab/estimate.py; then
    echo "Gold patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset/commands/sql_lab/estimate.py b/superset/commands/sql_lab/estimate.py
index 03aec8ade21d..2baca1eeb2b2 100644
--- a/superset/commands/sql_lab/estimate.py
+++ b/superset/commands/sql_lab/estimate.py
@@ -22,7 +22,7 @@
 from flask import current_app as app
 from flask_babel import gettext as __

-from superset import db
+from superset import db, security_manager
 from superset.commands.base import BaseCommand
 from superset.errors import ErrorLevel, SupersetError, SupersetErrorType
 from superset.exceptions import SupersetErrorException, SupersetTimeoutException
@@ -67,6 +67,7 @@ def validate(self) -> None:
                 ),
                 status=404,
             )
+        security_manager.raise_for_access(database=self._database)

     def run(
         self,
PATCH

echo "Gold patch applied successfully."
