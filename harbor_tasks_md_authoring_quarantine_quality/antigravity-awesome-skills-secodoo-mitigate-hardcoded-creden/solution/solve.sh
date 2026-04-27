#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "odoo_url = os.getenv(\"ODOO_URL\", \"https://myodoo.example.com\")" "skills/odoo-woocommerce-bridge/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/odoo-woocommerce-bridge/SKILL.md b/skills/odoo-woocommerce-bridge/SKILL.md
@@ -43,20 +43,24 @@ This skill guides you through building a reliable sync bridge between Odoo (the
 ```python
 from woocommerce import API
 import xmlrpc.client
+import os
 
 # WooCommerce client
 wcapi = API(
-    url="https://mystore.com",
-    consumer_key="ck_xxxxxxxxxxxxx",
-    consumer_secret="cs_xxxxxxxxxxxxx",
+    url=os.getenv("WC_URL", "https://mystore.com"),
+    consumer_key=os.getenv("WC_KEY"),
+    consumer_secret=os.getenv("WC_SECRET"),
     version="wc/v3"
 )
 
 # Odoo client
-odoo_url = "https://myodoo.example.com"
-db, uid, pwd = "my_db", 2, "api_key"
+odoo_url = os.getenv("ODOO_URL", "https://myodoo.example.com")
+db = os.getenv("ODOO_DB", "my_db")
+uid = int(os.getenv("ODOO_UID", "2"))
+pwd = os.getenv("ODOO_PASSWORD")
 models = xmlrpc.client.ServerProxy(f"{odoo_url}/xmlrpc/2/object")
 
+
 def sync_orders():
     # Get unprocessed WooCommerce orders
     orders = wcapi.get("orders", params={"status": "processing", "per_page": 50}).json()
PATCH

echo "Gold patch applied."
