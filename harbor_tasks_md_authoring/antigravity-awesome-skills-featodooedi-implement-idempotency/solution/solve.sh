#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "partner_name = transaction.get_segment('N1')[2] if transaction.get_segment('N1')" "skills/odoo-edi-connector/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/odoo-edi-connector/SKILL.md b/skills/odoo-edi-connector/SKILL.md
@@ -41,28 +41,49 @@ Electronic Data Interchange (EDI) is the standard for automated B2B document exc
 
 ```python
 from pyx12 import x12file  # pip install pyx12
+from datetime import datetime
 
 import xmlrpc.client
+import os
+
+odoo_url = os.getenv("ODOO_URL")
+db = os.getenv("ODOO_DB")
+pwd = os.getenv("ODOO_API_KEY") 
+uid = int(os.getenv("ODOO_UID", "2"))
 
-odoo_url = "https://myodoo.example.com"
-db, uid, pwd = "my_db", 2, "api_key"
 models = xmlrpc.client.ServerProxy(f"{odoo_url}/xmlrpc/2/object")
 
 def process_850(edi_file_path):
     """Parse X12 850 Purchase Order and create Odoo Sale Order"""
     with x12file.X12File(edi_file_path) as f:
         for transaction in f.get_transaction_sets():
-            # Extract header info (BEG segment)
-            po_number = transaction['BEG'][3]    # Purchase Order Number
-            po_date   = transaction['BEG'][5]    # Purchase Order Date
+            # Extract header info (BEG segment)                     
+            po_number = transaction['BEG'][3]    # Purchase Order Number                                                    
+            po_date   = transaction['BEG'][5]    # Purchase Order Date 
+
+            # IDEMPOTENCY CHECK: Verify PO doesn't already exist in Odoo
+            existing = models.execute_kw(db, uid, pwd, 'sale.order', 'search', [
+                [['client_order_ref', '=', po_number]]
+            ])
+            if existing:
+                print(f"Skipping: PO {po_number} already exists.")
+                continue 
 
             # Extract partner (N1 segment — Buyer)
-            partner_name = transaction['N1'][2]
 
-            # Find partner in Odoo
-            partner = models.execute_kw(db, uid, pwd, 'res.partner', 'search',
-                [[['name', 'ilike', partner_name]]])
-            partner_id = partner[0] if partner else False
+
+                        # Extract partner (N1 segment — Buyer)                  
+            partner_name = transaction.get_segment('N1')[2] if transaction.get_segment('N1') else "Unknown"                                                                             
+            
+            # Find partner in Odoo                                  
+            partner = models.execute_kw(db, uid, pwd, 'res.partner', 'search',                                                  
+                                [[['name', 'ilike', partner_name]]])                
+            
+            if not partner:
+                print(f"Error: Partner '{partner_name}' not found. Skipping transaction.")
+                continue
+                
+            partner_id = partner[0]
 
             # Extract line items (PO1 segments)
             order_lines = []
@@ -94,6 +115,7 @@ def process_850(edi_file_path):
 ```python
 def generate_997(isa_control, gs_control, transaction_control):
     """Generate a functional acknowledgment for received EDI"""
+    today = datetime.now().strftime('%y%m%d')
     return f"""ISA*00*          *00*          *ZZ*YOURISAID      *ZZ*PARTNERISAID   *{today}*1200*^*00501*{isa_control}*0*P*>~
 GS*FA*YOURGID*PARTNERGID*{today}*1200*{gs_control}*X*005010X231A1~
 ST*997*0001~
PATCH

echo "Gold patch applied."
