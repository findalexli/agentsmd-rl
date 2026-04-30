#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cognithor

# Idempotency guard
if grep -qF "description: \"Automated hourly backup skill that creates timestamped archives of" "skills/backup/SKILL.md" && grep -qF "description: \"API integration skill that fetches Gmail messages, syncs inbox lab" "skills/gmail_sync/SKILL.md" && grep -qF "description: \"Diagnostic smoke-test skill that validates Cognithor's skill loadi" "skills/test/SKILL.md" && grep -qF "description: \"Extended diagnostic skill that validates the full Cognithor skill " "skills/test_skill/SKILL.md" && grep -qF "description: \"Weather query skill that retrieves current temperature, humidity, " "skills/wetter_abfrage/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/backup/SKILL.md b/skills/backup/SKILL.md
@@ -1,3 +1,46 @@
+---
+name: backup
+description: "Automated hourly backup skill that creates timestamped archives of Cognithor config files, skill definitions, and data directories on a cron schedule. Use when setting up automated backups, restoring from snapshots, scheduling data protection, or configuring backup retention policies."
+---
+
 # Backup
 
-Automation: Jarvis Skill: Backup
+Automated backup skill that creates timestamped archives of Cognithor configuration, skills, and data on a cron schedule (`0 * * * *` — hourly by default).
+
+## Steps
+
+1. **Check prerequisites** — verify backup target exists and has write access:
+   ```bash
+   BACKUP_DIR="${COGNITHOR_HOME:-$HOME/.cognithor}/backups"
+   mkdir -p "$BACKUP_DIR" && test -w "$BACKUP_DIR"
+   ```
+2. **Create timestamped archive** of config, skills, and data:
+   ```bash
+   STAMP=$(date +%Y%m%d_%H%M%S)
+   tar czf "$BACKUP_DIR/cognithor_$STAMP.tar.gz" \
+     -C "${COGNITHOR_HOME:-$HOME/.cognithor}" \
+     config/ skills/ data/
+   ```
+3. **Validate integrity** — verify the archive is readable:
+   ```bash
+   tar tzf "$BACKUP_DIR/cognithor_$STAMP.tar.gz" > /dev/null
+   ```
+4. **Prune old backups** — keep the last 24 hourly snapshots:
+   ```bash
+   ls -1t "$BACKUP_DIR"/cognithor_*.tar.gz | tail -n +25 | xargs rm -f
+   ```
+5. **Return status** — the skill returns `{"status": "ok", "automated": true}` on success
+
+## Example
+
+```
+User > Starte ein Backup meiner Cognithor-Daten
+Cognithor > Backup erstellt: cognithor_20260420_140000.tar.gz (12 MB)
+         Nächstes automatisches Backup: 15:00 Uhr
+```
+
+## Error Handling
+
+- **Disk full**: Log warning, skip archive creation, alert user to free space
+- **Permission denied**: Verify `$BACKUP_DIR` ownership and retry with correct permissions
+- **Corrupt archive**: Re-run backup immediately; if persistent, check filesystem health
diff --git a/skills/gmail_sync/SKILL.md b/skills/gmail_sync/SKILL.md
@@ -1,3 +1,43 @@
+---
+name: gmail-sync
+description: "API integration skill that fetches Gmail messages, syncs inbox labels, and processes attachments via the Gmail REST API. Use when fetching new emails, syncing inbox state, triaging unread messages, exporting mail data, or integrating Gmail into automated workflows."
+---
+
 # Gmail Sync
 
-API-Integration für Jarvis Skill: Gmail Sync
+Fetches Gmail messages, syncs labels, and processes attachments via the Gmail REST API using `httpx`. Requires network access.
+
+## Steps
+
+1. **Authenticate** — obtain or refresh the OAuth2 token:
+   ```python
+   headers = {"Authorization": f"Bearer {access_token}"}
+   ```
+2. **Fetch new messages** since the last sync timestamp:
+   ```python
+   async with httpx.AsyncClient() as client:
+       resp = await client.get(
+           f"{API_BASE}/messages",
+           headers=headers,
+           params={"q": "after:{last_sync_epoch}"}
+       )
+       messages = resp.json().get("messages", [])
+   ```
+3. **Parse each message** — extract sender, subject, body, labels, and attachment metadata
+4. **Store locally** — persist parsed data under `$COGNITHOR_HOME/data/gmail/` as JSON
+5. **Return summary** — the skill returns `{"data": <parsed_response>}` with message counts
+
+## Example
+
+```
+User > Synchronisiere meine Gmail-Inbox
+Cognithor > 14 neue Nachrichten synchronisiert (3 ungelesen, 2 mit Anhängen)
+         Letzte Synchronisation: 2026-04-20 14:00 UTC
+```
+
+## Error Handling
+
+- **401 Unauthorized**: Token expired — trigger OAuth refresh flow before retrying
+- **429 Rate Limited**: Back off exponentially (1s, 2s, 4s) up to 3 retries
+- **Network timeout**: Log the failure, preserve last-known state, report to user
+- **Empty response**: Confirm query parameters are correct; check `last_sync_epoch` is valid
diff --git a/skills/test/SKILL.md b/skills/test/SKILL.md
@@ -1,9 +1,43 @@
+---
+name: test
+description: "Diagnostic smoke-test skill that validates Cognithor's skill loading, SkillRegistry registration, and Planner-Gatekeeper-Executor pipeline. Use when running a framework health check, verifying skill setup works end-to-end, debugging skill registration, or smoke-testing after configuration changes."
+---
+
 # Test
 
-## Beschreibung
-Jarvis Skill: Test
+Diagnostic smoke-test that sends a probe through the full Planner → Gatekeeper → Executor pipeline and returns a status response.
+
+## Steps
+
+1. **Invoke the skill** with any input:
+   ```
+   cognithor test <eingabe>
+   ```
+2. **Planner** receives the input and identifies this skill via SkillRegistry matching
+3. **Gatekeeper** validates the request against the skill's empty permission set (always passes)
+4. **Executor** runs `TestSkill.execute(params)` and returns:
+   ```json
+   {"status": "ok", "result": "TODO"}
+   ```
+5. **Verify success** — confirm the response contains `"status": "ok"`
+
+## Example
 
-## Verwendung
 ```
-jarvis test <eingabe>
+User > cognithor test Hallo Welt
+Cognithor > {"status": "ok", "result": "TODO"}
+
+# Healthy pipeline — skill loaded, registered, and executed successfully
 ```
+
+## Troubleshooting
+
+| Symptom | Cause | Fix |
+|---------|-------|-----|
+| Skill not found | Not registered in SkillRegistry | Restart Cognithor to re-scan `skills/` |
+| Import error | `cognithor.skills.base` missing | Verify installation: `pip install -e ".[all]"` |
+| No response | Executor timeout | Check logs at `$COGNITHOR_HOME/logs/` for stack traces |
+
+## Notes
+
+This is a diagnostic-only skill — the `"result": "TODO"` placeholder confirms the pipeline works without performing real work.
diff --git a/skills/test_skill/SKILL.md b/skills/test_skill/SKILL.md
@@ -1,9 +1,47 @@
+---
+name: test-skill
+description: "Extended diagnostic skill that validates the full Cognithor skill lifecycle — SkillRegistry scanning, keyword matching (exact + fuzzy at 70% threshold), and async execution. Use when testing skill discovery, debugging keyword matching accuracy, validating the SkillRegistry scan cycle, or verifying async execute() behavior."
+---
+
 # Test Skill
 
-## Beschreibung
-Jarvis Skill: Test Skill
+Extended diagnostic that validates the full skill lifecycle: directory scan → SkillRegistry registration → keyword matching → async `execute()`.
+
+## Steps
+
+1. **Trigger the skill** — Cognithor must match via keyword similarity:
+   ```
+   cognithor test_skill <eingabe>
+   ```
+2. **Verify registration** — confirm the skill appears in the registry:
+   ```
+   User > Zeige alle registrierten Skills
+   # Expected: test_skill listed with NAME="test_skill", VERSION="0.1.0"
+   ```
+3. **Check keyword matching** — the SkillRegistry uses exact match (case-insensitive) then fuzzy match (70% threshold). Verify the input routes to this skill, not the sibling `test` skill
+4. **Inspect the response** — `execute()` returns:
+   ```json
+   {"status": "ok", "result": "TODO"}
+   ```
+5. **Confirm async execution** — the skill runs via `async def execute(self, params)`, so verify no blocking calls appear in logs
+
+## Example
 
-## Verwendung
 ```
-jarvis test_skill <eingabe>
+User > cognithor test_skill Prüfe den Lifecycle
+Cognithor > {"status": "ok", "result": "TODO"}
+
+# Success: skill was discovered, matched, and executed asynchronously
 ```
+
+## Troubleshooting
+
+| Symptom | Cause | Fix |
+|---------|-------|-----|
+| Routes to `test` instead | Fuzzy match overlap | Use the full slug `test_skill` to force exact match |
+| `ModuleNotFoundError` | `__init__.py` missing | Verify `skills/test_skill/__init__.py` exists |
+| Timeout on execute | Event loop blocked | Check for synchronous calls in `skill.py` |
+
+## Notes
+
+Diagnostic-only skill — `"result": "TODO"` is intentional. Differs from `test` by validating keyword disambiguation and the full scan-to-execute lifecycle.
diff --git a/skills/wetter_abfrage/SKILL.md b/skills/wetter_abfrage/SKILL.md
@@ -1,9 +1,52 @@
+---
+name: wetter-abfrage
+description: "Weather query skill that retrieves current temperature, humidity, wind speed, and multi-day forecasts for a given city or coordinate. Use when checking the weather, getting a forecast, looking up temperature or wind conditions, or planning outdoor activities based on weather data."
+---
+
 # Wetter Abfrage
 
-## Beschreibung
-Jarvis Skill: Wetter Abfrage
+Retrieves current weather conditions (temperature, humidity, wind speed, conditions) and multi-day forecasts for a user-specified location.
+
+## Steps
+
+1. **Parse location** — extract city name or coordinates from user input:
+   ```
+   cognithor wetter_abfrage München
+   ```
+2. **Query weather API** — fetch current conditions and forecast data:
+   ```python
+   async with httpx.AsyncClient() as client:
+       resp = await client.get(
+           f"{API_BASE}/weather",
+           params={"q": location, "units": "metric"}
+       )
+       data = resp.json()
+   ```
+3. **Format response** — present key metrics in a readable summary:
+   ```
+   München — 18°C, leicht bewölkt
+   Luftfeuchtigkeit: 62% | Wind: 12 km/h NW
+   Vorhersage: Mo 20°C ☀️ | Di 17°C 🌧️ | Mi 19°C ⛅
+   ```
+4. **Handle ambiguity** — if multiple locations match, present options:
+   ```
+   Meinten Sie: (1) München, DE  (2) München, AT?
+   ```
+5. **Return structured data** — `{"status": "ok", "result": <weather_data>}`
+
+## Example
 
-## Verwendung
 ```
-jarvis wetter_abfrage <eingabe>
+User > Wie wird das Wetter morgen in Berlin?
+Cognithor > Berlin — morgen: 22°C, sonnig
+         Luftfeuchtigkeit: 45% | Wind: 8 km/h SO
+         UV-Index: 6 (hoch) — Sonnenschutz empfohlen
 ```
+
+## Error Handling
+
+| Error | Cause | Recovery |
+|-------|-------|----------|
+| Location not found | Typo or unknown city | Ask user to re-enter or provide coordinates |
+| API timeout | Network issue or rate limit | Retry once after 2s; report failure if persistent |
+| Missing data fields | Partial API response | Return available fields, note missing ones |
PATCH

echo "Gold patch applied."
