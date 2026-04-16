#!/bin/bash
set -e

cd /workspace/dagster

echo "Applying telemetry user_id patch..."

# 1. Update dagster_shared telemetry module - add USER_ID_STR constant
sed -i 's/INSTANCE_ID_STR = "instance_id"/INSTANCE_ID_STR = "instance_id"\nUSER_ID_STR = "user_id"/' python_modules/libraries/dagster-shared/dagster_shared/telemetry/__init__.py

# 2. Add get_or_create_user_telemetry_dir function after get_or_create_dir_from_dagster_home
cat > /tmp/add_user_telemetry_dir.py << 'PYEOF'
import re

file_path = "python_modules/libraries/dagster-shared/dagster_shared/telemetry/__init__.py"
with open(file_path, "r") as f:
    content = f.read()

# Find the end of get_or_create_dir_from_dagster_home function and add new function after it
new_function = '''

def get_or_create_user_telemetry_dir() -> str:
    """Always return ~/.dagster/.telemetry/, ignoring $DAGSTER_HOME.

    This is used for user-level telemetry data (like user_id) that should be
    consistent across all Dagster instances for a given user.
    """
    path = os.path.join(os.path.expanduser(DAGSTER_HOME_FALLBACK), TELEMETRY_STR)
    os.makedirs(path, exist_ok=True)
    return path

'''

# Find the pattern: return dagster_home_logs_path (end of get_or_create_dir_from_dagster_home)
# There are multiple ways this could appear, let's try a simpler approach
pattern = r'(    return dagster_home_logs_path)'
replacement = r'    return dagster_home_logs_path\n' + new_function
content = re.sub(pattern, replacement, content, count=1)

with open(file_path, "w") as f:
    f.write(content)

print("Added get_or_create_user_telemetry_dir function")
PYEOF

python3 /tmp/add_user_telemetry_dir.py

# 3. Update TelemetryEntry NamedTuple - add user_id field
cat > /tmp/update_telemetry_entry.py << 'PYEOF'
import re

file_path = "python_modules/libraries/dagster-shared/dagster_shared/telemetry/__init__.py"
with open(file_path, "r") as f:
    content = f.read()

# Add user_id to the _fields tuple in TelemetryEntry class
# Find the pattern: ("instance_id", str), followed by ("metadata", ...)
content = content.replace(
    '("instance_id", str),\n            ("metadata", Mapping[str, str]),',
    '("instance_id", str),\n            ("user_id", str),\n            ("metadata", Mapping[str, str]),'
)

# Update docstring to include user_id description
content = content.replace(
    'instance_id - Unique id for dagster instance\n    python_version - Python version',
    'instance_id - Unique id for dagster instance (varies by $DAGSTER_HOME)\n    user_id - Unique id for the user (consistent across all instances, stored in ~/.dagster)\n    python_version - Python version'
)

with open(file_path, "w") as f:
    f.write(content)

print("Updated TelemetryEntry with user_id field")
PYEOF

python3 /tmp/update_telemetry_entry.py

# 4. Update TelemetryEntry.__new__ to accept user_id parameter
cat > /tmp/update_new_method.py << 'PYEOF'
import re

file_path = "python_modules/libraries/dagster-shared/dagster_shared/telemetry/__init__.py"
with open(file_path, "r") as f:
    content = f.read()

# Add user_id parameter to __new__ method signature
content = content.replace(
    '''def __new__(
        cls,
        action: str,
        client_time: str,
        event_id: str,
        instance_id: str,
        metadata: Optional[Mapping[str, str]] = None,''',
    '''def __new__(
        cls,
        action: str,
        client_time: str,
        event_id: str,
        instance_id: str,
        user_id: str,
        metadata: Optional[Mapping[str, str]] = None,'''
)

# Add user_id to the super().__new__() call
content = content.replace(
    '''            event_id=event_id,
            instance_id=instance_id,
            python_version=get_python_version(),''',
    '''            event_id=event_id,
            instance_id=instance_id,
            user_id=user_id,
            python_version=get_python_version(),'''
)

with open(file_path, "w") as f:
    f.write(content)

print("Updated TelemetryEntry.__new__ with user_id parameter")
PYEOF

python3 /tmp/update_new_method.py

# 5. Update log_telemetry_action to include user_id in the payload
cat > /tmp/update_log_action.py << 'PYEOF'
import re

file_path = "python_modules/libraries/dagster-shared/dagster_shared/telemetry/__init__.py"
with open(file_path, "r") as f:
    content = f.read()

# Add user_id to the telemetry entry creation in log_telemetry_action
content = content.replace(
    '''                event_id=str(uuid.uuid4()),
                instance_id=instance_id,
                metadata=metadata,''',
    '''                event_id=str(uuid.uuid4()),
                instance_id=instance_id,
                user_id=get_or_set_user_id(),
                metadata=metadata,'''
)

with open(file_path, "w") as f:
    f.write(content)

print("Updated log_telemetry_action with user_id")
PYEOF

python3 /tmp/update_log_action.py

# 6. Add the get_or_set_user_id functions at the end of the file (after get_or_set_instance_id)
cat >> /tmp/add_user_functions.py << 'PYEOF'
import re

file_path = "python_modules/libraries/dagster-shared/dagster_shared/telemetry/__init__.py"
with open(file_path, "r") as f:
    content = f.read()

user_functions = '''

def get_or_set_user_id() -> str:
    """Get or create a user-level telemetry ID.

    Unlike instance_id which varies by $DAGSTER_HOME, user_id is always stored
    in ~/.dagster/.telemetry/user_id.yaml to ensure consistency across all
    Dagster instances for a given user.
    """
    user_id = _get_telemetry_user_id()
    if user_id is None:
        user_id = _set_telemetry_user_id() or "<<unable_to_set_user_id>>"
    return user_id


def _get_telemetry_user_id() -> Optional[str]:
    """Gets the user_id from ~/.dagster/.telemetry/user_id.yaml."""
    import yaml

    user_id_path = os.path.join(get_or_create_user_telemetry_dir(), "user_id.yaml")
    if not os.path.exists(user_id_path):
        return None

    try:
        with open(user_id_path, encoding="utf8") as user_id_file:
            user_id_yaml = yaml.safe_load(user_id_file)
            if (
                user_id_yaml
                and USER_ID_STR in user_id_yaml
                and isinstance(user_id_yaml[USER_ID_STR], str)
            ):
                return user_id_yaml[USER_ID_STR]
    except Exception:
        pass
    return None


def _set_telemetry_user_id() -> Optional[str]:
    """Sets the user_id at ~/.dagster/.telemetry/user_id.yaml."""
    import yaml

    user_id_path = os.path.join(get_or_create_user_telemetry_dir(), "user_id.yaml")
    user_id = str(uuid.uuid4())

    try:
        with open(user_id_path, "w", encoding="utf8") as user_id_file:
            yaml.dump({USER_ID_STR: user_id}, user_id_file, default_flow_style=False)
        return user_id
    except Exception:
        return None

'''

# Append after the last function (before the comment about _get_telemetry_instance_id if it's at the end)
# Just append to end of file
with open(file_path, "a") as f:
    f.write(user_functions)

print("Added get_or_set_user_id and helper functions")
PYEOF

python3 /tmp/add_user_functions.py

# 7. Update dagster core telemetry.py to import and use get_or_set_user_id
sed -i 's/from dagster_shared.telemetry import (/from dagster_shared.telemetry import (\n    get_or_set_user_id,/' python_modules/dagster/dagster/_core/telemetry.py

# 8. Add user_id to the telemetry calls in dagster core
# Add to log_remote_repo_stats - find the pattern and add user_id
sed -i '/event_id=str(uuid.uuid4()),/{N;s/instance_id=instance_id,/instance_id=instance_id,\n                user_id=get_or_set_user_id(),/}' python_modules/dagster/dagster/_core/telemetry.py

# 9. Update webserver test to expect user_id in logs
sed -i 's/"instance_id",/"instance_id",\n                        "user_id",/' python_modules/dagster-webserver/dagster_webserver_tests/test_app.py

echo "Patch applied successfully"

# Idempotency check - verify get_or_set_user_id was added to telemetry module
if ! grep -q "def get_or_set_user_id" python_modules/libraries/dagster-shared/dagster_shared/telemetry/__init__.py; then
    echo "ERROR: get_or_set_user_id function not found after patch"
    exit 1
fi

if ! grep -q "user_id=get_or_set_user_id()" python_modules/libraries/dagster-shared/dagster_shared/telemetry/__init__.py; then
    echo "ERROR: user_id not added to log_telemetry_action"
    exit 1
fi

echo "Idempotency check passed - get_or_set_user_id function exists"
