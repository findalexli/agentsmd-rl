#!/usr/bin/env bash
set -euo pipefail

cd /workspace/finance-skills

# Idempotency guard
if grep -qF "- Was the later round during or after the April 2026 Software Meltdown? (public " "skills/saas-valuation-compression/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/saas-valuation-compression/SKILL.md b/skills/saas-valuation-compression/SKILL.md
@@ -84,19 +84,22 @@ Use this checklist. For each cause, rate it: Primary / Contributing / Not applic
 **Macro / Rate Environment**
 - Was the earlier round during 2020–2021 ZIRP bubble? (adds ~2–5x artificial premium)
 - Was the later round during 2022–2023 rate hikes? (removes bubble premium)
+- Was the later round during or after the April 2026 Software Meltdown? (public SaaS down 40–86% from 52w highs; tariff/trade-war driven selloff crushed multiples sector-wide — even high-growth names like Figma -87%, monday.com -80%, HubSpot -70%, ServiceNow -58%)
 - Reference: SaaS private market median multiples by period:
 
-| Period | Approx Median ARR Multiple (private) |
-|---|---|
-| 2019 | ~8–12x |
-| 2020 | ~12–18x |
-| 2021 Q1–Q3 peak | ~35–45x |
-| 2022 H2 | ~15–20x |
-| 2023 trough | ~8–12x |
-| 2024 | ~12–18x |
-| 2025–2026 | ~16–22x |
+| Period | Approx Median ARR Multiple (private) | Context |
+|---|---|---|
+| 2019 | ~8–12x | Pre-pandemic baseline |
+| 2020 | ~12–18x | ZIRP begins, multiple expansion |
+| 2021 Q1–Q3 peak | ~35–45x | Peak bubble |
+| 2022 H2 | ~15–20x | Rate hikes begin, first compression wave |
+| 2023 trough | ~8–12x | Rate plateau, valuation reset |
+| 2024 | ~12–18x | AI narrative recovery, selective re-rating |
+| 2025 H1 | ~16–22x | Continued AI-driven recovery |
+| 2025 H2–2026 Q1 | ~10–16x | Tariff shock / trade-war selloff begins |
+| **2026 Q2 (Apr meltdown)** | **~6–10x** | **Software Meltdown — broad sector crash, public SaaS down 40–86% from 52w highs** |
 
-*(These are rough private market estimates. Public SaaS multiples are ~30–50% lower.)*
+*(These are rough private market estimates. Public SaaS multiples are ~30–50% lower. The April 2026 figures reflect the acute selloff; private marks typically lag public by 1–2 quarters.)*
 
 **Growth Deceleration**
 - Did YoY ARR growth rate slow materially between rounds? (most common cause)
@@ -110,6 +113,7 @@ Use this checklist. For each cause, rate it: Primary / Contributing / Not applic
 - Does the company serve AI-native companies (OpenAI, Anthropic, etc.) as customers? → premium
 - Did the company pivot to AI narrative credibly? → premium
 - Did the company fail to articulate AI story? → discount vs peers
+- Note: In the Apr 2026 meltdown, even strong AI narratives did not protect multiples — Snowflake (-53%), Datadog (-46%), MongoDB (-48%) all cratered despite AI tailwinds. AI premium may be necessary but not sufficient in a macro-driven selloff.
 
 **Competitive / Market**
 - Market saturation signal (e.g., Okta pressure on WorkOS, Auth0 competition)
@@ -164,6 +168,35 @@ Use these as context when search results are thin or for the comparison chart.
 | Stripe | — | — | — | — | Private; est. flat/compressed 2021→2023 down round |
 | HashiCorp | Acquired by IBM 2024 | — | — | — | Acq at ~8x ARR vs ~40x peak |
 
+### April 2026 Software Meltdown — Public SaaS Drawdowns
+
+As of April 9, 2026, a broad tariff/trade-war driven selloff crushed public software valuations. Use these as reference for how private multiples will lag-compress over the following 1–2 quarters.
+
+| Ticker | Company | Δ from 52w High | Sector relevance |
+|---|---|---|---|
+| FIG | Figma | -86.7% | Design/dev tools — worst hit |
+| MNDY | monday.com | -80.2% | Work management SaaS |
+| TEAM | Atlassian | -75.7% | Dev tools / collaboration |
+| HUBS | HubSpot | -69.9% | Marketing/CRM SaaS |
+| WIX | WIX | -65.1% | Website builder |
+| GTLB | GitLab | -63.6% | DevOps |
+| CVLT | Commvault | -61.7% | Data protection |
+| WDAY | Workday | -59.1% | HR/Finance SaaS |
+| NOW | ServiceNow | -57.8% | Enterprise IT workflows |
+| INTU | Intuit | -56.0% | FinTech/SMB SaaS |
+| SNOW | Snowflake | -52.8% | Data cloud |
+| KVYO | Klaviyo | -52.9% | Marketing automation |
+| DOCU | DocuSign | -52.3% | eSignature |
+| MDB | MongoDB | -47.9% | Database |
+| SAP | SAP | -47.6% | Enterprise ERP |
+| DDOG | Datadog | -45.7% | Observability |
+| APP | AppLovin | -47.6% | AdTech/mobile |
+| CRM | Salesforce | -42.5% | CRM market leader |
+| ADBE | Adobe | -34.6% | Creative/doc SaaS |
+| ZM | Zoom | -13.9% | Video/collab (already de-rated) |
+
+*Source: @speculator_io, April 9, 2026. Average drawdown across tracked software names: ~50–55%.*
+
 ---
 
 ## Edge Cases
PATCH

echo "Gold patch applied."
