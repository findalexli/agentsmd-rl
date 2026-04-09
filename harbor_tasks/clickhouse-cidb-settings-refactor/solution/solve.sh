#!/bin/bash
set -e

cd /workspace/ClickHouse

# Idempotency check: if already applied, exit early
if grep -q "info.get_secret(Settings.SECRET_CI_DB_URL)" ci/jobs/collect_statistics.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

FILE="ci/jobs/collect_statistics.py"

# Remove 'from ci.praktika import Secret' line
sed -i '/^from ci.praktika import Secret$/d' "$FILE"

# Add 'from ci.praktika.info import Info' after 'from ci.praktika.cidb import CIDB'
sed -i '/^from ci.praktika.cidb import CIDB$/a from ci.praktika.info import Info' "$FILE"

# Replace the CIDB initialization block (lines 113-129 in the original file)
sed -i '113,129c\    info = Info()\n    url_secret = info.get_secret(Settings.SECRET_CI_DB_URL)\n    user_secret = info.get_secret(Settings.SECRET_CI_DB_USER)\n    passwd_secret = info.get_secret(Settings.SECRET_CI_DB_PASSWORD)\n    url, user, pwd = (\n        url_secret.join_with(user_secret).join_with(passwd_secret).get_value()\n    )\n    cidb = CIDB(url=url, user=user, passwd=pwd)' "$FILE"

echo "Patch applied successfully!"
