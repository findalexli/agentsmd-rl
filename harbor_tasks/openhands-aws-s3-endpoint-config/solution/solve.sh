#!/bin/bash
set -e

cd /workspace/openhands

TARGET_FILE="openhands/app_server/event/aws_event_service.py"

# Use Python to properly modify the file
python3 << 'PYTHON'
import re

with open('openhands/app_server/event/aws_event_service.py', 'r') as f:
    content = f.read()

# 1. Add pydantic import after the fastapi import
content = content.replace(
    'from fastapi import Request',
    'from fastapi import Request\nfrom pydantic import Field'
)

# 2. Add the new function before the AwsEventServiceInjector class
new_function = '''\ndef _get_default_aws_endpoint_url() -> str | None:
    """Legacy fallback for aws endpoint url based on V0"""
    endpoint_url = os.getenv('AWS_S3_ENDPOINT')
    if not endpoint_url:
        return None
    secure = os.getenv('AWS_S3_SECURE', 'true').lower() == 'true'
    if secure:
        if not endpoint_url.startswith('https://'):
            endpoint_url = 'https://' + endpoint_url.removeprefix('http://')
    else:
        if not endpoint_url.startswith('http://'):
            endpoint_url = 'http://' + endpoint_url.removeprefix('https://')
    return endpoint_url
'''

# Find the class definition and insert before it
class_pattern = r'\n(class AwsEventServiceInjector\(EventServiceInjector\):)'
match = re.search(class_pattern, content)
if match:
    insert_pos = match.start()
    content = content[:insert_pos] + new_function + content[insert_pos:]

# 3. Add endpoint_url field to AwsEventServiceInjector class
prefix_pattern = r'(prefix: Path = Path\(\'users\'\)\n)'
replacement = r'\1    endpoint_url: str | None = Field(default_factory=_get_default_aws_endpoint_url)\n'
content = re.sub(prefix_pattern, replacement, content)

# 4. Replace os.getenv with self.endpoint_url in boto3.client call
old_endpoint = "endpoint_url=os.getenv('AWS_S3_ENDPOINT'),"
new_endpoint = "endpoint_url=self.endpoint_url,"
content = content.replace(old_endpoint, new_endpoint)

with open('openhands/app_server/event/aws_event_service.py', 'w') as f:
    f.write(content)

print('Fix applied successfully')
PYTHON

# Run ruff format to ensure proper formatting
pip install ruff -q
ruff format "$TARGET_FILE" --config dev_config/python/ruff.toml

# Verify the fix was applied
grep -q "_get_default_aws_endpoint_url" "$TARGET_FILE"
grep -q "endpoint_url: str | None = Field" "$TARGET_FILE"
grep -q "endpoint_url=self.endpoint_url" "$TARGET_FILE"
grep -q "from pydantic import Field" "$TARGET_FILE"

echo 'All verifications passed!'
