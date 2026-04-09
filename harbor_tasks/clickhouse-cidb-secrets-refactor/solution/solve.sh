#!/bin/bash
set -e

cd /workspace/ClickHouse

# Use Python for reliable text manipulation
python3 << "PYEOF"
import re

with open("ci/jobs/collect_statistics.py", "r") as f:
    content = f.read()

# Replace the cidb initialization block - match exact content
old_block = """    cidb = CIDB(
        url=Secret.Config(
            name=\"clickhouse-test-stat-url\",
            type=Secret.Type.AWS_SSM_PARAMETER,
        ).get_value(),
        user=Secret.Config(
            name=\"clickhouse-test-stat-login\",
            type=Secret.Type.AWS_SSM_PARAMETER,
        ).get_value(),
        passwd=Secret.Config(
            name=\"clickhouse-test-stat-password\",
            type=Secret.Type.AWS_SSM_PARAMETER,
        ).get_value(),
    )"""

new_block = """    info = Info()
    url_secret = info.get_secret(Settings.SECRET_CI_DB_URL)
    user_secret = info.get_secret(Settings.SECRET_CI_DB_USER)
    passwd_secret = info.get_secret(Settings.SECRET_CI_DB_PASSWORD)
    url, user, pwd = (
        url_secret.join_with(user_secret).join_with(passwd_secret).get_value()
    )
    cidb = CIDB(url=url, user=user, passwd=pwd)"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Replaced CIDB block")
else:
    print("WARNING: Could not find old CIDB block to replace")

# Remove Secret import if present
if "from ci.praktika import Secret\n" in content:
    content = content.replace("from ci.praktika import Secret\n", "")
    print("Removed Secret import")

# Add Info import after CIDB import if not present
if "from ci.praktika.info import Info" not in content:
    content = content.replace(
        "from ci.praktika.cidb import CIDB\n",
        "from ci.praktika.cidb import CIDB\nfrom ci.praktika.info import Info\n"
    )
    print("Added Info import")

# Add Settings import after S3 import if not present  
if "from ci.praktika.settings import Settings" not in content:
    content = content.replace(
        "from ci.praktika.s3 import S3\n",
        "from ci.praktika.s3 import S3\nfrom ci.praktika.settings import Settings\n"
    )
    print("Added Settings import")

with open("ci/jobs/collect_statistics.py", "w") as f:
    f.write(content)

print("Patch applied successfully")
PYEOF
