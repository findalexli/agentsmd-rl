"""
Pytest configuration to mock heavy superset imports.
This allows testing the MCP schemas without the full superset environment.
"""
import sys
import types
import json as stdlib_json
from pathlib import Path
from unittest.mock import MagicMock

REPO = Path("/workspace/superset")
sys.path.insert(0, str(REPO))

# Create a fake superset module that acts as a real package
fake_superset = types.ModuleType('superset')
fake_superset.__path__ = [str(REPO / 'superset')]
fake_superset.__file__ = str(REPO / 'superset' / '__init__.py')

# Create fake app module
fake_app = types.ModuleType('superset.app')
fake_app.create_app = MagicMock()
fake_app.SupersetApp = MagicMock()

# Create fake extensions module with mocked db
fake_extensions = types.ModuleType('superset.extensions')
fake_extensions.db = MagicMock()
fake_extensions.celery_app = MagicMock()
fake_extensions.cache_manager = MagicMock()
fake_extensions.machine_auth_provider_factory = MagicMock()
fake_extensions.appbuilder = MagicMock()
fake_extensions.feature_flag_manager = MagicMock()
fake_extensions.security_manager = MagicMock()
fake_extensions.async_query_manager = MagicMock()
fake_extensions.results_backend_manager = MagicMock()
fake_extensions.talisman = MagicMock()
fake_extensions.encrypted_field_factory = MagicMock()
fake_extensions.event_logger = MagicMock()
fake_extensions.profiling = MagicMock()

# Create fake utils module
fake_utils = types.ModuleType('superset.utils')
fake_utils.__path__ = [str(REPO / 'superset' / 'utils')]
fake_utils.__file__ = str(REPO / 'superset' / 'utils' / '__init__.py')

# Create fake utils.json with standard json functionality
fake_utils_json = types.ModuleType('superset.utils.json')
fake_utils_json.loads = stdlib_json.loads
fake_utils_json.dumps = stdlib_json.dumps
fake_utils_json.load = stdlib_json.load
fake_utils_json.dump = stdlib_json.dump
fake_utils_json.JSONDecodeError = stdlib_json.JSONDecodeError
fake_utils_json.validate_json = MagicMock()
fake_utils_json.json_iso_dttm_ser = MagicMock(side_effect=lambda x, pessimistic=None: str(x))

# Register the fake modules BEFORE anything else imports them
sys.modules['superset'] = fake_superset
sys.modules['superset.app'] = fake_app
sys.modules['superset.extensions'] = fake_extensions
sys.modules['superset.utils'] = fake_utils
sys.modules['superset.utils.json'] = fake_utils_json
fake_superset.app = fake_app
fake_superset.extensions = fake_extensions
fake_superset.utils = fake_utils
fake_utils.json = fake_utils_json
