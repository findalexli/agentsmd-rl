#!/usr/bin/env bash
set -euo pipefail

cd /workspace/kscrash

# Idempotency guard
if grep -qF "description: Review code changes for async-signal-safety violations in KSCrash c" ".claude/skills/async-signal-safety-review/SKILL.md" && grep -qF "> Verify whether `strerror_r` is async-signal-safe on Apple. It's in apple-oss-d" ".claude/skills/async-signal-safety-review/apple-oss-reference.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/async-signal-safety-review/SKILL.md b/.claude/skills/async-signal-safety-review/SKILL.md
@@ -0,0 +1,107 @@
+---
+name: async-signal-safety-review
+description: Review code changes for async-signal-safety violations in KSCrash crash handlers, signal handlers, and monitor code. Verifies suspect system calls by reading the actual implementation in Apple's open-source repos on github.com/apple-oss-distributions rather than guessing. Use when the user asks to review a diff/branch/PR/file for signal safety, or before landing changes that touch signal handlers, Mach exception handlers, or anything reachable from `Sources/KSCrashRecording`, `Sources/KSCrashRecordingCore`, `Sources/KSCrashBootTimeMonitor`, or `Sources/KSCrashDiscSpaceMonitor`.
+argument-hint: "[PR-number, branch, or file path]"
+allowed-tools: Bash(git diff:*), Bash(git show:*), Bash(git log:*), Bash(git status:*), Bash(git merge-base:*), Bash(gh api repos/apple-oss-distributions:*), Bash(gh search code --owner apple-oss-distributions:*), Bash(gh pr view:*), Bash(gh pr diff:*), Read, Grep, Glob, WebFetch, WebSearch
+---
+
+# Async-Signal-Safety Review (with Libc ground-truthing)
+
+**Scope is strict: async-signal-safety and crash-time correctness only.** This is NOT a general PR review. You are not evaluating whether the PR should land, whether the design is good, whether doc comments read well, whether names are clear, whether tests exist, or whether refactors are worthwhile. You are answering exactly one question per changed line: *does this break async-signal-safety on the signal-handler path?*
+
+**Do NOT include in the report:**
+- Style, naming, readability, or refactor opinions.
+- Doc / comment wording suggestions, unless the comment makes a false claim about signal safety (e.g. says something is unsafe when it is, or vice versa).
+- DX concerns, API-shape feedback, "the author should clarify intent", "worth a second look" items that aren't concrete signal-safety issues.
+- Test coverage commentary.
+- Summaries of what the diff does beyond the one-line Scope.
+- Praise, "looks good", "nice refactor", or any editorial voice.
+
+If a concern is not "X calls a lock/alloc/ObjC from a signal-reachable path" or "a comment misstates signal safety", it does not belong in the output. When in doubt, cut it.
+
+## Ground rules
+
+The authoritative rules live in `.claude/rules/async-signal-safety.md`. **Read that file before every review** — do not summarize or duplicate the rules here; they may have been updated since this skill was last edited. Apply all rules from that file as-is.
+
+## Verify suspect calls against Apple's open source (do not guess)
+
+Whenever you're unsure whether a system function is async-signal-safe, **do not guess** — read the actual implementation. Full instructions for how to look up symbols, which Apple OSS repo owns which function, how to fetch source via `gh`, how to delegate lookups to parallel subagents, and a list of common findings are in [apple-oss-reference.md](apple-oss-reference.md). **Read that file** when you encounter a suspect system call.
+
+## What to review
+
+Determine the review mode from the user's input:
+
+- **PR number** (e.g. `#809`, `PR 809`): fetch the PR diff with `gh pr diff <number>` and review only those changes.
+- **Branch name**: diff that branch against `master` and review only those changes.
+- **File or module name** (e.g. `signal monitor`, `KSCrashMonitor_Signal.c`, `KSObjC`): **ambiguous** — the user might mean the whole file or just changes to it. Ask: "Do you want me to review the entire file or only the changes on the current branch?" Do not guess.
+- **No argument**: default to current branch vs `master` — `git merge-base HEAD master`, then `git diff <base>...HEAD`.
+
+Only review files where async-signal-safety applies (the `paths:` list in `.claude/rules/async-signal-safety.md`). Ignore Swift modules, Filters, Sinks, Installations, sample app, and docs — mention that you skipped them once, then move on.
+
+## How to review
+
+### 1. Identify signal-reachable functions
+
+Not every function in a file needs signal-safety. First, determine which functions are on the **critical path** — reachable (directly or transitively) from a signal/crash handler. Entry points to trace from: `ksmach_*` exception handlers, `kssignal_*` signal handlers, `KSCrashMonitorAPI.handleException` / `notifyPostSystemEnable`, `kscm_*_getAPI`, `kscrashsentry_*`, anything registered via `sigaction` or `thread_set_exception_ports`. Functions only called from `+load`, init, setup, or background threads don't need signal-safety — skip them.
+
+### 2. Trace transitive calls (across files)
+
+For each signal-reachable function, follow **every call it makes** — including into other files, other modules, and system libraries. A function that looks clean itself but calls a helper in `KSString.c` or `KSLogger.c` that uses `snprintf` is still unsafe. Grep for the callee, read its implementation, and recurse until you reach either a leaf (safe primitive, raw syscall, atomic op) or a violation (lock, alloc, ObjC). This is where subagents are most valuable — delegate cross-file lookups in parallel per [apple-oss-reference.md](apple-oss-reference.md).
+
+### 3. Check dual-context correctness
+
+If a signal-reachable function also runs in a non-crash context (normal thread, background queue), thread-safety and signal-safety must BOTH hold. A lock-free path that races with a concurrent writer is still a bug.
+
+### 4. Scan for violations
+
+Then check for concrete violations. For any system call you're not 100% certain about, **fetch the source from apple-oss-distributions and verify** before flagging or clearing it. Cite `file.c:LINE` for the KSCrash change and `<repo>/<path>:LINE` for the evidence.
+
+Be especially suspicious of:
+
+- New `static` mutable state without `_Atomic`, without documented single-thread ownership.
+- New format strings or `KSLOG_*` calls — check the configured log level constant; verbose logging uses `snprintf` under the hood and is compiled out only at low levels.
+- New includes of `<Foundation/...>`, `<dispatch/...>`, `<os/lock.h>`, `<stdio.h>`.
+- Ring buffers / caches: verify producer/consumer contract holds under signal interruption (pattern: `KSThreadCache.c`, `KSBinaryImageCache.c`).
+- Changes under `kscrash_install` / `kscrs_initialize` that add I/O or parsing.
+- Stale comments: "not async-signal-safe" on something that now is, or vice versa.
+
+## Output format
+
+The output uses **only** the sections shown in the template below. No other sections, headers, labels, or free-text are allowed. Do not add "Analysis details", "Notes", "Context", "Summary", explanations of why something is safe, or any prose outside these sections.
+
+```
+Scope: <one line>
+Signal-handler reachable files: <list>
+Skipped (not on signal path): <list>
+
+Violations:
+
+Root cause: <unsafe primitive, e.g. "vsnprintf (locale lock + FLOCKFILE)">
+Evidence: apple-oss-distributions/<repo> <path>:LINE — <lock/alloc seen>
+Fix: <one fix that addresses all instances of this root cause>
+Instances:
+- Sources/.../file.c:LINE in func_name — call chain: handler → ... → func_name → unsafe_call
+- Sources/.../other.c:LINE in other_func — call chain: handler → ... → other_func → unsafe_call
+- ...
+
+Root cause: <next distinct unsafe primitive>
+...
+
+Suspected (unverified) violations:
+- <symbol, call chain showing how it's reachable, and what needs verifying>
+
+Stale signal-safety claims in comments:
+- <comment that falsely claims signal safety or unsafety>
+
+Verdict: signal-safe | NOT signal-safe (see violations above)
+```
+
+Strict rules — violating any of these makes the report wrong:
+- **Group violations by root cause.** If 15 call sites all hit `vsnprintf`, that's one root cause with 15 instances — not 15 separate violations. The Evidence and Fix appear once per root cause; instances are a flat list with call chains.
+- **Every instance must include its call chain** from the signal handler entry point to the unsafe call. Example: `handleSignal → kscrashreport_writeStandardReport → ksjson_addFloatingPointElement → formatDouble → snprintf`. Without the chain, the reader can't verify reachability.
+- **Only the sections above exist.** If you catch yourself writing any heading or label not in the template, delete it.
+- If a section has no entries, **omit it entirely**. For a clean report with no violations, output is exactly three lines: Scope, Signal-handler reachable files, Verdict.
+- The verdict is binary. Never write "safe to land", "needs clarification", "looks good".
+- **Nothing comes after the Verdict line.** No caveats, no "in practice", no analysis, no mitigating context. The Verdict line is the end.
+- **Every Evidence line must cite a concrete file:line from apple-oss-distributions.** If you spawned a subagent, wait for it and use its citation. Do not write "well-known to use fprintf" — cite the source or mark as unverified.
+- Do not explain why things are safe. Do not restate what the code does. The reader already knows.
diff --git a/.claude/skills/async-signal-safety-review/apple-oss-reference.md b/.claude/skills/async-signal-safety-review/apple-oss-reference.md
@@ -0,0 +1,67 @@
+# Apple OSS Signal-Safety Verification Reference
+
+How to verify whether a system function is async-signal-safe by reading Apple's actual source at **https://github.com/apple-oss-distributions**.
+
+## Which repo owns which symbol
+
+Match the function to a repo before fetching:
+
+- **`Libc`** — `printf`/`snprintf`/`vfprintf`, `fopen`/`fwrite`/`FILE*` stdio, `str*`, `mem*`, `getenv`, `strtol`, `strerror`, locale machinery (`xlocale`, `__current_locale`), `syslog`.
+- **`libplatform`** — `os_unfair_lock_*`, `_os_semaphore_*`, low-level atomics and memory barriers, `setjmp`/`longjmp`, `bzero`.
+- **`libpthread`** — `pthread_*` (mutex, rwlock, cond, key, create, self, kill), `pthread_once`.
+- **`libdispatch`** — all `dispatch_*`, `dispatch_source_*`, `os_workgroup_*`.
+- **`libmalloc`** — `malloc`/`calloc`/`realloc`/`free`/`malloc_zone_*`/`malloc_size`. (All unsafe — they take the zone lock.)
+- **`dyld`** — `dlopen`/`dlsym`/`dladdr`, `_dyld_*`, `getsectiondata`, image list iteration. Signal safety of `dladdr` specifically matters for symbolication.
+- **`xnu`** — Mach traps, `mach_*`, `task_*`, `thread_*`, `sigaction`/signal delivery internals, `sysctl`, kernel side of syscalls. Usually you want the userspace wrapper first (Libc/libsyscall), then xnu only if needed.
+- **`objc4`** — ObjC runtime (`objc_msgSend`, `objc_retain`, class lookup). All unsafe in signal context; the runtime takes its own locks.
+- **`CF` (`CoreFoundation` is mirrored as `CF`)** — `CF*` APIs. Almost always unsafe.
+
+If you can't tell which repo a symbol lives in, `gh search code --owner apple-oss-distributions '<symbol>'` first.
+
+## How to fetch and read the source
+
+Prefer `gh` over raw WebFetch — it authenticates, handles rate limits, and returns clean text:
+
+```
+gh api repos/apple-oss-distributions/Libc/contents/stdio/FreeBSD/vfprintf.c -H "Accept: application/vnd.github.raw"
+gh search code --owner apple-oss-distributions --filename vfprintf.c
+gh api repos/apple-oss-distributions/Libc/git/trees/main?recursive=1   # only if you really need the layout
+```
+
+If `gh` isn't available or the path is already known, use WebFetch against the `raw.githubusercontent.com` URL for the repo's default branch (usually `main`). Example: `https://raw.githubusercontent.com/apple-oss-distributions/Libc/main/stdio/FreeBSD/vfprintf.c`. Do not guess tags/versions — stick to `main` unless the user asks for a specific OS version.
+
+## What to look for in the source
+
+1. **Lock primitives.** Grep the file (and any helpers it calls) for:
+   `FLOCKFILE`, `FUNLOCKFILE`, `pthread_mutex_lock`, `pthread_rwlock_`, `os_unfair_lock`, `OSSpinLock`, `LOCK(`, `_MUTEX_LOCK`, `xlocale`, `__current_locale`, `lock_`, `_lock`.
+2. **Heap.** `malloc`, `calloc`, `realloc`, `asprintf`, zone allocation, VLA growth, `__sbuf` grow paths. Any of these disqualifies the call for signal context.
+3. **Follow helpers.** `snprintf` looks innocent but calls `__vfprintf` → locale helpers → `__current_locale()` which takes a lock. Trace until you hit either a lock/alloc (unsafe) or a leaf that's obviously lock-free (safe).
+4. **Cite the evidence.** In your report, give the repo + path + line + the exact lock/alloc call you saw (e.g., `apple-oss-distributions/Libc stdio/FreeBSD/vfprintf.c:123 — FLOCKFILE(fp)`). A verdict with no citation is a guess; don't ship guesses.
+
+If the symbol isn't published on apple-oss-distributions at all (some `libsystem_*` shims, some kernel-only paths), say so explicitly rather than guessing.
+
+## Delegate verifications to subagents (in parallel)
+
+Each "is function X actually async-signal-safe on Apple?" lookup is **independent** and **context-heavy** (you may have to read several files to trace helpers). Do not do them inline in the main conversation — spawn a subagent per suspect symbol and run them in parallel. This keeps the main context clean and is much faster.
+
+- Use the `Agent` tool with `subagent_type: "general-purpose"` (it has `gh`, `WebFetch`, `Read`, `Grep`). `Explore` also works but is read-only; `general-purpose` is safer since you may need `gh api`.
+- Launch **all independent lookups in a single message** with multiple `Agent` tool calls. Don't serialize them.
+- Give each subagent a tight, self-contained prompt: the symbol, which repo you think it lives in (or say "find it"), the specific question ("does this take a lock or allocate on the signal-handler path?"), and require it to cite `<repo>/<path>:LINE` for every lock/alloc it finds. Ask for ≤150 words.
+- Do **not** delegate the review itself — only the factual lookups. You still decide the verdict, map findings back to the KSCrash diff, and write the report.
+
+Example subagent prompt:
+
+> Verify whether `strerror_r` is async-signal-safe on Apple. It's in apple-oss-distributions/Libc. Fetch the implementation (try `gen/FreeBSD/strerror.c` first via `gh api repos/apple-oss-distributions/Libc/contents/...`), trace any helpers it calls, and report: (1) does it take any lock (FLOCKFILE, pthread_mutex, os_unfair_lock, xlocale, __current_locale)? (2) does it allocate? (3) cite file+line for every lock/alloc you find, or state "no locks, no allocs found on this path". ≤150 words.
+
+Only skip delegation if the answer is already in the "Common findings" list below AND the diff doesn't touch a variant/edge case.
+
+## Common findings — use as priors but still verify
+
+- `snprintf` / `vsnprintf` / `printf` family → **unsafe** (locale lock via `__current_locale`, plus stdio FLOCKFILE).
+- `asprintf` → **unsafe** (calls `malloc`).
+- `strerror` → **unsafe** (locale-dependent); `strerror_r` with a caller buffer is safer but still locale-touching on Apple — verify.
+- `fopen` / `fwrite` / `fclose` / any `FILE*` API → **unsafe** (FLOCKFILE).
+- `open` / `read` / `write` / `close` / `lseek` / `fstat` → **safe** (raw syscalls).
+- `memcpy` / `memset` / `memmove` / `memcmp` / `strlen` / `strncmp` / `strcmp` → **safe**.
+- `getsectiondata` → **safe** on Apple (confirmed via dyld source; its only non-trivial call is `strncmp`).
+- `mach_*` task/thread APIs called by KSCrash → mostly safe; verify per-call if the diff touches new ones.
PATCH

echo "Gold patch applied."
