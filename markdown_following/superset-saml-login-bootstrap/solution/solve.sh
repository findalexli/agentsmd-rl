#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superset

# Idempotency guard - if the SAML branch is already in place, skip
if grep -q "elif auth_type == AUTH_SAML:" superset/views/base.py 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch directly via patch HEREDOC.
# We split the patch into individual hunks per file to avoid issues with
# patch trying to apply context that may have shifted.

# 1) superset/views/base.py — import AUTH_SAML and add the SAML branch + recaptcha guard
python3 - <<'PYEOF'
from pathlib import Path
p = Path("superset/views/base.py")
s = p.read_text()

s = s.replace(
    "from flask_appbuilder.const import AUTH_OAUTH",
    "from flask_appbuilder.const import AUTH_OAUTH, AUTH_SAML",
)

s = s.replace(
    "should_show_recaptcha = auth_user_registration and (auth_type != AUTH_OAUTH)",
    "should_show_recaptcha = auth_user_registration and (\n        auth_type not in (AUTH_OAUTH, AUTH_SAML)\n    )",
)

s = s.replace(
    '            )\n        frontend_config["AUTH_PROVIDERS"] = oauth_providers\n\n    bootstrap_data = {',
    '            )\n        frontend_config["AUTH_PROVIDERS"] = oauth_providers\n    elif auth_type == AUTH_SAML:\n        saml_providers = []\n        for provider in appbuilder.sm.saml_providers:\n            saml_providers.append(\n                {\n                    "name": provider["name"],\n                    "icon": provider.get("icon", "fa-sign-in"),\n                }\n            )\n        frontend_config["AUTH_PROVIDERS"] = saml_providers\n\n    bootstrap_data = {',
)

p.write_text(s)
PYEOF

# 2) superset/config.py — add SAML ACS to CSRF exempt list
python3 - <<'PYEOF'
from pathlib import Path
p = Path("superset/config.py")
s = p.read_text()
old = '    "superset.views.datasource.views.samples",\n]'
new = '    "superset.views.datasource.views.samples",\n    "flask_appbuilder.security.views.acs",\n]'
if "flask_appbuilder.security.views.acs" not in s:
    s = s.replace(old, new)
p.write_text(s)
PYEOF

# 3) superset-frontend/src/pages/Login/index.tsx — add AuthSAML enum value and render SAML
python3 - <<'PYEOF'
from pathlib import Path
p = Path("superset-frontend/src/pages/Login/index.tsx")
s = p.read_text()

s = s.replace(
    "  AuthOauth = 4,\n}",
    "  AuthOauth = 4,\n  AuthSAML = 5,\n}",
)
s = s.replace(
    "{authType === AuthType.AuthOauth && (",
    "{(authType === AuthType.AuthOauth ||\n          authType === AuthType.AuthSAML) && (",
)
p.write_text(s)
PYEOF

echo "Patch applied successfully"
