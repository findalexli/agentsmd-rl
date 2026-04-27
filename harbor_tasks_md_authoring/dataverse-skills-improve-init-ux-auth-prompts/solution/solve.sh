#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dataverse-skills

# Idempotency guard
if grep -qF "- `TENANT_ID`: Auto-discover from the `DATAVERSE_URL` using the curl method (see" ".github/plugins/dataverse/skills/init/SKILL.md" && grep -qF "Separately from tenant-level consent, each Dataverse environment must explicitly" ".github/plugins/dataverse/skills/mcp-configure/SKILL.md" && grep -qF "- If EITHER is missing: **Automatically run the init flow** (see the init skill)" ".github/plugins/dataverse/skills/overview/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/plugins/dataverse/skills/init/SKILL.md b/.github/plugins/dataverse/skills/init/SKILL.md
@@ -161,11 +161,20 @@ CLIENT_SECRET=<app-registration-secret>
 ```
 
 How to prompt the user:
-- `DATAVERSE_URL`: "What is your Dataverse environment URL?"
-- `TENANT_ID`: Auto-discover from the URL above before asking. Only ask if discovery fails.
-- `SOLUTION_NAME`: "What is the unique name of your solution?"
+- `DATAVERSE_URL`: "What is your Dataverse environment URL?" (e.g., `https://myorg.crm10.dynamics.com`). If the Environment Discovery flow already determined this, use it directly — do not re-ask.
+- `TENANT_ID`: Auto-discover from the `DATAVERSE_URL` using the curl method (see Scenario A step 2). This is preferred over `pac org who` because it derives the tenant directly from the URL — no PAC CLI setup needed, and no risk of returning the wrong tenant when multiple auth profiles exist. Only ask the user if the curl method fails.
+- `SOLUTION_NAME`: "What is the unique name of your solution?" (allow skipping for now)
 - `PUBLISHER_PREFIX`: Do **not** ask yet — this is discovered in the solution creation step (step 7 in Scenario B). Leave it blank in `.env` for now; the `create_solution.py` script will query existing publishers and ask the user. Once confirmed, update `.env` with the chosen prefix.
-- `CLIENT_ID` / `CLIENT_SECRET`: Only needed for service principal auth. If the user authenticates via browser (interactive login), skip these. When omitted, auth.py uses interactive device code flow with AuthenticationRecord persistence (no browser re-prompt on subsequent runs).
+
+**Present authentication options — always ask this explicitly with clear descriptions:**
+
+> How would you like to authenticate with Dataverse?
+>
+> 1. **Interactive login (recommended for personal use)** — Sign in via your browser. No app registration needed. You'll authenticate once and the token stays cached across sessions.
+> 2. **Service principal (for CI/CD or shared environments)** — Uses a CLIENT_ID and CLIENT_SECRET from an Azure app registration. Required for unattended/automated scenarios.
+
+- If **Interactive**: skip `CLIENT_ID` and `CLIENT_SECRET`. `auth.py` uses device code flow with persistent OS-level token caching — no re-prompt on subsequent runs.
+- If **Service principal**: ask for `CLIENT_ID` and `CLIENT_SECRET`.
 
 Write the file directly — do not instruct the user to create it:
 
diff --git a/.github/plugins/dataverse/skills/mcp-configure/SKILL.md b/.github/plugins/dataverse/skills/mcp-configure/SKILL.md
@@ -311,23 +311,54 @@ Store this command as `CLAUDE_COMMAND` for use in step 9.
 
 Proceed to step 7.
 
-### 7. Confirm admin consent is granted
+### 7. Ensure tenant-level admin consent (one-time per tenant)
+
+The MCP client app registration must be granted admin consent on the Azure AD tenant. This is a **one-time** action per tenant — once done, it applies to all Dataverse environments in that tenant. It **requires an Azure AD Global Admin or Privileged Role Admin**.
 
 List out the parameters chosen in previous steps:
-- Tool type (Copilot or claude) from step 0
-- Scope (list possible options based on tool) from step 1
+- Tool type (Copilot or Claude) from step 0
+- Scope from step 1
 - Environment URL from step 4
 - Endpoint (GA or Preview) from step 5
+- MCP Client ID from step 0
 
-Ask the user if their Azure tenant administrator has granted admin consent for the MCP client ID to access the environment (which is a one-time action). If not, provide instructions to grant consent and share the following URL with them, replacing `{TENANT_ID}` with their tenant ID from `.env` and `{MCP_CLIENT_ID}` with the client ID determined in step 0:
+Ask the user if admin consent has already been granted for this tenant. If not, provide the consent URL:
 
-```
-https://login.microsoftonline.com/{TENANT_ID}/adminconsent?client_id={MCP_CLIENT_ID}
-```
+> **Tenant-level admin consent** is required for the MCP client app. This is a one-time action per Azure AD tenant — once granted, it covers all environments in the tenant.
+>
+> An Azure AD Global Admin or Privileged Role Admin must open this URL and click **Accept**:
+> ```
+> https://login.microsoftonline.com/{TENANT_ID}/adminconsent?client_id={MCP_CLIENT_ID}
+> ```
+>
+> If you don't have admin permissions, send this URL to your Azure AD administrator.
 
-### 8. Add the client ID to the allowed clients list
+Wait for the user to confirm this is done (or was already done previously) before proceeding.
+
+### 8. Add the MCP client to the environment's allowed list (one-time per environment)
+
+Separately from tenant-level consent, each Dataverse environment must explicitly allow the MCP client. This is a **one-time** action per environment and does **NOT** require Azure AD admin permissions — any user with Environment Admin or System Administrator role in the environment can do it.
+
+Present the two methods (PPAC portal is recommended for non-developers):
+
+> **Method A: Power Platform Admin Center (recommended — no Azure AD admin needed)**
+>
+> 1. Go to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com/)
+> 2. Select **Environments** in the left navigation
+> 3. Click on your environment (e.g., the one matching `{USER_URL}`)
+> 4. Click **Settings** in the top toolbar
+> 5. Expand **Product** and click **Features**
+> 6. Scroll down to the **MCP Server** section
+> 7. Toggle **Enable MCP Server** to **On** (if not already)
+> 8. Under **Allowed clients**, click **Add client**
+> 9. Paste the MCP Client ID: `{MCP_CLIENT_ID}`
+> 10. Click **Save**
+>
+> **Method B: Programmatic (via script)**
+>
+> Run `scripts/enable-mcp-client.py` to add the client ID to the allowed list via the Dataverse API.
 
-Run the `scripts/enable-mcp-client.py` script to add the MCP client ID (from step 0) to the Allowed Clients list for the environment (which will require a new app registration when using the VSCode extension for Claude Code but will work with standard client IDs for Copilot and Claude CLI). Do not ask for user confirmation.
+If the user completed Method A, attempt to run `scripts/enable-mcp-client.py` anyway to verify. If it reports the client is already enabled, continue. Do not ask for user confirmation.
 
 ### 9. Confirm success and provide next steps
 
@@ -394,8 +425,12 @@ If something goes wrong, help the user check:
 - The URL format is correct (`https://<org>.<region>.dynamics.com`)
 - They have access to the Dataverse environment
 - The environment URL matches what's shown in the Power Platform Admin Center
-- Their Environment Admin has enabled "Dataverse CLI MCP" in the Allowed Clients list
-- Their Environment has Dataverse MCP enabled, and if they're trying to use the preview endpoint that is enabled
+- **Tenant-level admin consent** has been granted for the MCP client app. This is a one-time per-tenant action requiring an Azure AD admin. Without it, authentication succeeds but the app is denied access. Use the admin consent URL from step 7.
+- **Org-level allowed clients** — the MCP client ID has been added to the environment's allowed list. To check or fix this:
+  1. Go to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com/) > Environments > your environment > Settings > Product > Features
+  2. Verify **MCP Server** is toggled **On**
+  3. Verify the MCP Client ID appears under **Allowed clients**
+- If using the Preview endpoint, verify that the Preview MCP endpoint is also enabled in the same Features page
 - **If TOOL_TYPE is `copilot`:**
   - For project-scoped configuration, ensure the `.mcp/copilot/mcp.json` file was created successfully
   - For global configuration, check permissions on the `~/.copilot/` directory
diff --git a/.github/plugins/dataverse/skills/overview/SKILL.md b/.github/plugins/dataverse/skills/overview/SKILL.md
@@ -29,7 +29,7 @@ ls .env scripts/auth.py 2>/dev/null
 ```
 
 - If BOTH exist: workspace is initialized. Proceed to the relevant task.
-- If EITHER is missing: **STOP. Run the init flow first** (see the init skill). Do not create your own `.env`, `requirements.txt`, `.env.example`, or auth scripts. The init skill handles all of this.
+- If EITHER is missing: **Automatically run the init flow** (see the init skill). Do NOT ask the user whether to initialize — just do it. Do not create your own `.env`, `requirements.txt`, `.env.example`, or auth scripts. The init skill handles all of this.
 
 Do NOT create `requirements.txt`, `.env.example`, or scaffold files manually. The init flow produces the correct file structure. Skipping init is the #1 cause of broken setups.
 
PATCH

echo "Gold patch applied."
